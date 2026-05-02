"""Modelo ORM (tabla users)."""

from sqlalchemy import Boolean, Column, Integer, String

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_code_hash = Column(String, nullable=True)
    verification_code_expires_at = Column(Integer, nullable=True)
