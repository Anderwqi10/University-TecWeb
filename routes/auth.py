"""Endpoints HTTP de autenticación.

Rutas:
- POST /auth/register
- POST /auth/login
- POST /auth/verify  (código enviado por correo)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from controllers.auth_controller import AuthController
from core.database import get_db
from models.user_model import (
    LoginRequest,
    RegisterResponse,
    TokenResponse,
    UserCreate,
    UserResponse,
    VerifyEmailRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        created = AuthController.register(user, db)
        return RegisterResponse(email=created.email, verification_required=True)
    except ValueError as e:
        if str(e) == "EMAIL_ALREADY_VERIFIED":
            raise HTTPException(status_code=409, detail="El correo ya está registrado y verificado")
        raise
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        token = AuthController.login(payload, db)
        return TokenResponse(access_token=token)
    except ValueError as e:
        if str(e) == "INVALID_CREDENTIALS":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña inválidos",
            )
        if str(e) == "EMAIL_NOT_VERIFIED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Revisa tu correo e ingresa el código OTP antes de iniciar sesión",
            )
        raise


@router.post("/verify", response_model=UserResponse)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    try:
        return AuthController.verify_email(payload, db)
    except ValueError as e:
        if str(e) == "CODE_EXPIRED":
            raise HTTPException(
                status_code=400,
                detail="El código expiró. Vuelve a registrarte con el mismo correo para recibir uno nuevo.",
            )
        if str(e) == "INVALID_CODE":
            raise HTTPException(status_code=400, detail="Código inválido")
        raise
