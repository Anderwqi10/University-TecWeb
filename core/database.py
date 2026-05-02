"""Configuración de SQLAlchemy y helpers de base de datos."""

import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

# En Render u otros hosts: exporta DATABASE_URL (ej. sqlite:////var/data/students.db con disco persistente).
SQLALCHEMY_DB_URL = os.getenv("DATABASE_URL", "sqlite:///./students.db")

engine = create_engine(
    SQLALCHEMY_DB_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_schema():
    """Aplica cambios mínimos de esquema para bases SQLite existentes.

    Nota: esto no reemplaza un sistema formal de migraciones (ej. Alembic).
    """
    # SQLite no hace migrations automáticas con create_all.
    # Aseguramos la columna user_id en students para "datos por usuario".
    with engine.begin() as conn:
        cols = conn.execute(text("PRAGMA table_info(students)")).fetchall()
        if cols:
            names = {row[1] for row in cols}
            if "user_id" not in names:
                conn.execute(text("ALTER TABLE students ADD COLUMN user_id INTEGER"))

        user_cols = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        if user_cols:
            u_names = {row[1] for row in user_cols}
            if "is_verified" not in u_names:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0"))
            if "verification_code_hash" not in u_names:
                conn.execute(text("ALTER TABLE users ADD COLUMN verification_code_hash TEXT"))
            if "verification_code_expires_at" not in u_names:
                conn.execute(text("ALTER TABLE users ADD COLUMN verification_code_expires_at INTEGER"))


def get_db():
    """Dependencia de FastAPI para abrir/cerrar sesión de DB por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
