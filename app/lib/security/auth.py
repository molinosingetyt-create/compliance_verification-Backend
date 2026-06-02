import time
from typing import Optional, Dict, Any

import jwt
from passlib.context import CryptContext

from app.lib.config.config import settings

# Evitamos bcrypt para no depender del backend nativo (y su límite de 72 bytes).
# PBKDF2 es estable y suficiente para este caso.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(subject: str, extra: Optional[Dict[str, Any]] = None) -> str:
    expire_minutes = int((settings.ACCESS_TOKEN_EXPIRE_MINUTES or "3600").strip())
    now = int(time.time())
    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + (expire_minutes * 60),
    }
    if extra:
        payload.update(extra)
    secret = (settings.SECRET_KEY or "").strip()
    algo = (settings.ALGORITHM or "HS256").strip()
    if not secret:
        raise RuntimeError("SECRET_KEY no configurada.")
    return jwt.encode(payload, secret, algorithm=algo)


def decode_token(token: str) -> Dict[str, Any]:
    secret = (settings.SECRET_KEY or "").strip()
    algo = (settings.ALGORITHM or "HS256").strip()
    return jwt.decode(token, secret, algorithms=[algo])

