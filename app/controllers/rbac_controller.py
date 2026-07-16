import logging

from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User

logger = logging.getLogger(__name__)


class RbacController:
    """Semillas y utilidades de perfiles (roles) + permisos."""

    @staticmethod
    def seed(db: Session) -> None:
        """
        Crea permisos base y perfiles:
        - administrador: todo (incluye administración de usuarios)
        - ingeniero: ver + crear + editar muestreo
        - auxiliar: ver + crear muestreo (sin editar)
        - consulta: verificación limitada (sin cumplimiento ni T1/T2, solo lectura)
        """
        definitions = [
            ("sampling:view", "Ver muestreos, listados y detalles"),
            ("sampling:view-limited", "Ver verificaciones sin resultado de cumplimiento ni errores T1/T2"),
            ("sampling:view-all", "Ver todos los muestreos (dashboard y verificaciones)"),
            ("sampling:view-own", "Ver solo los muestreos realizados por el usuario"),
            ("sampling:create", "Crear muestreo"),
            ("sampling:edit", "Editar muestreo / contenido neto"),
            ("sampling:edit-package", "Editar pesos de empaque (bolsas vacías)"),
            ("sampling:delete", "Eliminar muestreos"),
            ("users:manage", "Administrar usuarios, perfiles y permisos"),
            ("catalog:manage", "Administrar productos, marcas y gramajes"),
        ]
        for code, desc in definitions:
            p = db.query(Permission).filter(Permission.code == code).first()
            if not p:
                db.add(Permission(code=code, description=desc))
        db.commit()

        profiles = {
            "administrador": [
                "sampling:view",
                "sampling:view-all",
                "sampling:create",
                "sampling:edit",
                "sampling:edit-package",
                "sampling:delete",
                "users:manage",
                "catalog:manage",
            ],
            "ingeniero": [
                "sampling:view",
                "sampling:view-all",
                "sampling:create",
                "sampling:edit",
                "sampling:edit-package",
                "sampling:delete",
                "catalog:manage",
            ],
            "auxiliar": ["sampling:view", "sampling:view-own", "sampling:create"],
            "consulta": ["sampling:view-limited", "sampling:view-own"],
        }

        for role_name, codes in profiles.items():
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name)
                db.add(role)
                db.commit()
                db.refresh(role)

            perm_objs = (
                db.query(Permission).filter(Permission.code.in_(codes)).all()
            )
            wanted_ids = {p.id for p in perm_objs}

            existing = (
                db.query(RolePermission)
                .filter(RolePermission.role_id == role.id)
                .all()
            )

            existing_ids = {rp.permission_id for rp in existing}

            for pid in wanted_ids - existing_ids:
                db.add(RolePermission(role_id=role.id, permission_id=pid))
            for rp in list(existing):
                if rp.permission_id not in wanted_ids:
                    db.delete(rp)

        db.commit()
        logger.info("RBAC: permisos y perfiles (administrador/ingeniero/auxiliar/consulta) verificados.")

        # Migración suave desde roles viejos (si existían)
        legacy_map = {"admin": "administrador", "editor": "ingeniero", "viewer": "auxiliar"}
        for old_name, new_name in legacy_map.items():
            old = db.query(Role).filter(Role.name == old_name).first()
            new = db.query(Role).filter(Role.name == new_name).first()
            if old and new:
                db.query(User).filter(User.role_id == old.id).update(
                    {"role_id": new.id}, synchronize_session=False
                )
        db.commit()
