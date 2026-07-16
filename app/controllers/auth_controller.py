from fastapi import HTTPException
from sqlalchemy.orm import joinedload

from app.lib.config.database import SessionLocal
from app.lib.config.config import settings
from app.lib.security.auth import verify_password, create_access_token, hash_password
from app.models.user import User
from app.models.role import Role


class AuthController:
    @staticmethod
    def ensure_default_admin(db, username: str | None, password: str | None):
        username = (username or "").strip()
        password = password or ""
        if not username or not password:
            return
        admin_role = db.query(Role).filter(Role.name == "administrador").first()
        if not admin_role:
            return
        existing = db.query(User).filter(User.username == username).first()
        admin_full_name = (getattr(settings, "DEFAULT_ADMIN_FULL_NAME", None) or "").strip() or None
        if existing:
            # Si ya existe, sincroniza contraseña y rol desde .env (útil al cambiar DEFAULT_ADMIN_PASS).
            existing.password_hash = hash_password(password)
            existing.role_id = admin_role.id
            existing.is_active = True
            if admin_full_name and not (existing.full_name or "").strip():
                existing.full_name = admin_full_name
            db.commit()
            return
        db.add(
            User(
                username=username,
                full_name=admin_full_name,
                password_hash=hash_password(password),
                role_id=admin_role.id,
                is_active=True,
            )
        )
        db.commit()

    @staticmethod
    def login(username: str, password: str):
        username = (username or "").strip()
        with SessionLocal() as db:
            from app.lib.security.rbac import get_user_permission_codes

            user = (
                db.query(User)
                .options(joinedload(User.role), joinedload(User.packaging_area))
                .filter(User.username == username)
                .first()
            )
            if not user or not user.is_active:
                raise HTTPException(status_code=401, detail="Credenciales inválidas")
            if not verify_password(password, user.password_hash):
                raise HTTPException(status_code=401, detail="Credenciales inválidas")
            token = create_access_token(
                subject=str(user.id),
                extra={"role": user.role.name if user.role else None, "username": user.username},
            )
            user_dict = user.toDict()
            user_dict["permissions"] = sorted(get_user_permission_codes(db, user.id))
            return {"access_token": token, "token_type": "bearer", "user": user_dict}

