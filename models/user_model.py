"""Modelos Pydantic para endpoints de autenticación."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    # Datos requeridos para registro.
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_verified: bool = False


class LoginRequest(BaseModel):
    # Datos para iniciar sesión.
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=10)


class RegisterResponse(BaseModel):
    email: EmailStr
    verification_required: bool = True

