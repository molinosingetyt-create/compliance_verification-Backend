from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import joinedload

from app.lib.config.database import get_db
from app.lib.security.auth import decode_token
from app.lib.security.rbac import get_user_permission_codes
from app.models.user import User

security = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db),
):
    if not creds or not creds.credentials:
        raise HTTPException(status_code=401, detail="No autenticado")
    token = creds.credentials
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == int(user_id))
        .first()
    )
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuario inválido")
    return user


def require_permission(code: str):
    """Exige un permiso puntual (código en tabla permissions)."""

    def _dep(user=Depends(get_current_user), db=Depends(get_db)):
        codes = get_user_permission_codes(db, user.id)
        if code not in codes:
            raise HTTPException(status_code=403, detail="Sin permiso")
        return user

    return _dep

