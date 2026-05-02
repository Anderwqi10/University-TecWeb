from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from core.auth import decode_token
from core.database import get_db
from models.db_user_model import User as UserDB


def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
) -> UserDB:
    """Obtiene el usuario autenticado desde el header Authorization.

    El formato que se espera es mas o menos como: `Authorization: Bearer <token>`.
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

    email = str(payload["sub"])
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")

    return user