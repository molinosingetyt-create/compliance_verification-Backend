from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import joinedload

from app.lib.config.database import SessionLocal
from app.lib.security.auth import hash_password
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User


class AdminController:
    @staticmethod
    def _role_payload(db, role: Role) -> dict:
        links = (
            db.query(RolePermission)
            .options(joinedload(RolePermission.permission))
            .filter(RolePermission.role_id == role.id)
            .all()
        )
        perm_ids = [x.permission_id for x in links]
        return {
            **role.toDict(),
            "permission_ids": perm_ids,
            "permissions": [x.permission.code for x in links if x.permission],
        }

    # ——— Permisos ———
    @staticmethod
    def list_permissions():
        with SessionLocal() as db:
            rows = db.query(Permission).order_by(Permission.id.asc()).all()
            return [p.toDict() for p in rows]

    @staticmethod
    def get_permission(permission_id: int):
        with SessionLocal() as db:
            p = db.query(Permission).filter(Permission.id == permission_id).first()
            if not p:
                raise HTTPException(status_code=404, detail="Permiso no encontrado")
            return p.toDict()

    @staticmethod
    def create_permission(code: str, description: Optional[str] = None):
        code = (code or "").strip()
        if not code:
            raise HTTPException(status_code=400, detail="El código es obligatorio")
        with SessionLocal() as db:
            if db.query(Permission).filter(Permission.code == code).first():
                raise HTTPException(status_code=400, detail="Ya existe un permiso con ese código")
            p = Permission(code=code, description=(description or "").strip() or None)
            db.add(p)
            db.commit()
            db.refresh(p)
            return p.toDict()

    @staticmethod
    def update_permission(permission_id: int, code: Optional[str] = None, description: Optional[str] = None):
        with SessionLocal() as db:
            p = db.query(Permission).filter(Permission.id == permission_id).first()
            if not p:
                raise HTTPException(status_code=404, detail="Permiso no encontrado")
            if code is not None:
                code = code.strip()
                if not code:
                    raise HTTPException(status_code=400, detail="El código no puede estar vacío")
                other = db.query(Permission).filter(Permission.code == code, Permission.id != p.id).first()
                if other:
                    raise HTTPException(status_code=400, detail="Ya existe un permiso con ese código")
                p.code = code
            if description is not None:
                p.description = description.strip() or None
            db.commit()
            db.refresh(p)
            return p.toDict()

    @staticmethod
    def delete_permission(permission_id: int):
        with SessionLocal() as db:
            p = db.query(Permission).filter(Permission.id == permission_id).first()
            if not p:
                raise HTTPException(status_code=404, detail="Permiso no encontrado")
            db.query(RolePermission).filter(RolePermission.permission_id == p.id).delete()
            db.delete(p)
            db.commit()
            return {"detail": "Permiso eliminado"}

    # ——— Perfiles (roles) ———
    @staticmethod
    def list_roles():
        with SessionLocal() as db:
            roles = db.query(Role).order_by(Role.id.asc()).all()
            return [AdminController._role_payload(db, r) for r in roles]

    @staticmethod
    def get_role(role_id: int):
        with SessionLocal() as db:
            role = db.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise HTTPException(status_code=404, detail="Perfil no encontrado")
            return AdminController._role_payload(db, role)

    @staticmethod
    def create_role(name: str, permission_ids: Optional[list[int]] = None):
        name = (name or "").strip()
        if not name:
            raise HTTPException(status_code=400, detail="El nombre del perfil es obligatorio")
        with SessionLocal() as db:
            if db.query(Role).filter(Role.name == name).first():
                raise HTTPException(status_code=400, detail="Ya existe un perfil con ese nombre")
            role = Role(name=name)
            db.add(role)
            db.flush()
            if permission_ids is not None:
                AdminController._apply_role_permissions(db, role.id, permission_ids)
            db.commit()
            db.refresh(role)
            return AdminController._role_payload(db, role)

    @staticmethod
    def update_role(
        role_id: int,
        name: Optional[str] = None,
        permission_ids: Optional[list[int]] = None,
    ):
        with SessionLocal() as db:
            role = db.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise HTTPException(status_code=404, detail="Perfil no encontrado")
            if name is not None:
                name = name.strip()
                if not name:
                    raise HTTPException(status_code=400, detail="El nombre no puede estar vacío")
                other = db.query(Role).filter(Role.name == name, Role.id != role.id).first()
                if other:
                    raise HTTPException(status_code=400, detail="Ya existe un perfil con ese nombre")
                role.name = name
            if permission_ids is not None:
                AdminController._apply_role_permissions(db, role.id, permission_ids)
            db.commit()
            db.refresh(role)
            return AdminController._role_payload(db, role)

    @staticmethod
    def delete_role(role_id: int):
        with SessionLocal() as db:
            role = db.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise HTTPException(status_code=404, detail="Perfil no encontrado")
            users_count = db.query(User).filter(User.role_id == role.id).count()
            if users_count > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"No se puede eliminar: {users_count} usuario(s) tienen este perfil",
                )
            db.query(RolePermission).filter(RolePermission.role_id == role.id).delete()
            db.delete(role)
            db.commit()
            return {"detail": "Perfil eliminado"}

    @staticmethod
    def set_role_permissions(role_id: int, permission_ids: list[int]):
        with SessionLocal() as db:
            role = db.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise HTTPException(status_code=404, detail="Perfil no encontrado")
            AdminController._apply_role_permissions(db, role.id, permission_ids)
            db.commit()
            return AdminController._role_payload(db, role)

    @staticmethod
    def _apply_role_permissions(db, role_id: int, permission_ids: list[int]):
        valid_ids = {p.id for p in db.query(Permission).all()}
        for pid in permission_ids:
            if pid not in valid_ids:
                raise HTTPException(status_code=400, detail=f"Permiso inválido: {pid}")
        existing = db.query(RolePermission).filter(RolePermission.role_id == role_id).all()
        existing_ids = {rp.permission_id for rp in existing}
        wanted = set(permission_ids)
        for pid in wanted - existing_ids:
            db.add(RolePermission(role_id=role_id, permission_id=pid))
        for rp in existing:
            if rp.permission_id not in wanted:
                db.delete(rp)

    # ——— Usuarios ———
    @staticmethod
    def list_users():
        with SessionLocal() as db:
            users = (
                db.query(User)
                .options(joinedload(User.role), joinedload(User.packaging_area))
                .order_by(User.id.asc())
                .all()
            )
            return [u.toDict() for u in users]

    @staticmethod
    def get_user(user_id: int):
        with SessionLocal() as db:
            u = (
                db.query(User)
                .options(joinedload(User.role), joinedload(User.packaging_area))
                .filter(User.id == user_id)
                .first()
            )
            if not u:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            return u.toDict()

    @staticmethod
    def create_user(
        username: str,
        password: str,
        role_id: int,
        is_active: bool = True,
        full_name: Optional[str] = None,
        packaging_area_id: Optional[int] = None,
    ):
        username = (username or "").strip()
        if not username or not password:
            raise HTTPException(status_code=400, detail="Usuario y contraseña son obligatorios")
        with SessionLocal() as db:
            role = db.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise HTTPException(status_code=404, detail="Perfil no encontrado")
            if packaging_area_id is None:
                raise HTTPException(status_code=400, detail="El área de empaque es obligatoria")
            exists = db.query(User).filter(User.username == username).first()
            if exists:
                raise HTTPException(status_code=400, detail="El usuario ya existe")
            area_id = AdminController._resolve_packaging_area_id(db, packaging_area_id)
            fn = (full_name or "").strip() or None
            u = User(
                username=username,
                full_name=fn,
                password_hash=hash_password(password),
                role_id=role.id,
                is_active=is_active,
                packaging_area_id=area_id,
            )
            db.add(u)
            db.commit()
            db.refresh(u)
            u = (
                db.query(User)
                .options(joinedload(User.role), joinedload(User.packaging_area))
                .filter(User.id == u.id)
                .first()
            )
            return u.toDict()

    @staticmethod
    def update_user(
        user_id: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        role_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        full_name: Optional[str] = None,
        packaging_area_id: Optional[int] = None,
    ):
        with SessionLocal() as db:
            u = (
                db.query(User)
                .options(joinedload(User.role), joinedload(User.packaging_area))
                .filter(User.id == user_id)
                .first()
            )
            if not u:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            if username is not None:
                username = username.strip()
                if not username:
                    raise HTTPException(status_code=400, detail="El usuario no puede estar vacío")
                other = db.query(User).filter(User.username == username, User.id != u.id).first()
                if other:
                    raise HTTPException(status_code=400, detail="El usuario ya existe")
                u.username = username
            if password:
                u.password_hash = hash_password(password)
            if role_id is not None:
                role = db.query(Role).filter(Role.id == role_id).first()
                if not role:
                    raise HTTPException(status_code=404, detail="Perfil no encontrado")
                u.role_id = role.id
            if is_active is not None:
                u.is_active = is_active
            if full_name is not None:
                u.full_name = full_name.strip() or None
            if packaging_area_id is not None:
                u.packaging_area_id = AdminController._resolve_packaging_area_id(
                    db, packaging_area_id
                )
            db.commit()
            db.refresh(u)
            u = (
                db.query(User)
                .options(joinedload(User.role), joinedload(User.packaging_area))
                .filter(User.id == u.id)
                .first()
            )
            return u.toDict()

    @staticmethod
    def _resolve_packaging_area_id(db, packaging_area_id: Optional[int]) -> Optional[int]:
        if packaging_area_id is None:
            return None
        from app.models.parameters.packaging_area import PackagingArea

        area = (
            db.query(PackagingArea)
            .filter(PackagingArea.id == packaging_area_id, PackagingArea.status == 1)
            .first()
        )
        if not area:
            raise HTTPException(status_code=404, detail="Área de empaque no encontrada")
        return area.id

    @staticmethod
    def delete_user(user_id: int):
        with SessionLocal() as db:
            u = db.query(User).filter(User.id == user_id).first()
            if not u:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            db.delete(u)
            db.commit()
            return {"detail": "Usuario eliminado"}
