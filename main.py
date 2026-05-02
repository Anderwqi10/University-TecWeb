"""Punto de entrada de la aplicación FastAPI.

Responsabilidades:
- Cargar variables de entorno.
- Inicializar base de datos y asegurar esquema mínimo.
- Servir páginas frontend (login, registro, verificación por correo y app principal).
- Registrar routers API.
"""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from core.database import Base, engine, ensure_schema
from models import db_model  # noqa: F401
from models import db_user_model  # noqa: F401
from routes import students
from routes import auth

# Carga desde la carpeta del proyecto (no depende del directorio desde el que arranques uvicorn).
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
# Completa claves que falten si solo tienes .env.example o un .env incompleto.
load_dotenv(BASE_DIR / ".env.example", override=False)

# Creamos tablas y aplicamos ajustes básicos de esquema al iniciar.
Base.metadata.create_all(bind=engine)
ensure_schema()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory=BASE_DIR / "frontend"), name="frontend")


@app.get("/")
def serve_index():
    # Vista principal (dashboard de estudiantes).
    return FileResponse(BASE_DIR / "frontend" / "index.html")


@app.get("/login")
def serve_login():
    # Vista de inicio de sesión.
    return FileResponse(BASE_DIR / "frontend" / "login.html")


@app.get("/register")
def serve_register():
    # Vista de registro de cuenta.
    return FileResponse(BASE_DIR / "frontend" / "register.html")


@app.get("/verify")
def serve_verify():
    # Vista de verificación con código enviado al correo.
    return FileResponse(BASE_DIR / "frontend" / "verify.html")


app.include_router(students.router)
app.include_router(auth.router)
