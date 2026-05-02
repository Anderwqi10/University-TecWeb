"""Utilidades de autenticación y tokens JWT.

Este módulo centraliza:
- Hash y verificación de contraseñas.
- Creación y validación de access tokens.
"""

import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

# Usamos pbkdf2_sha256 para evitar problemas de compatibilidad de bcrypt en algunos entornos.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Producción (Render, etc.): define JWT_SECRET en variables de entorno.
_secret = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY")
if os.getenv("RENDER") == "true" and not _secret:
    raise RuntimeError(
        "Defina JWT_SECRET en el panel de Render (Environment) antes de desplegar."
    )
SECRET_KEY = _secret or "CHANGE_ME_IN_PROD"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    # El subject normalmente es el correo del usuario autenticado.
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_minutes)
    to_encode = {"sub": subject, "iat": int(now.timestamp()), "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    # Retorna payload si el token es válido; None si está expirado o mal firmado.
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
