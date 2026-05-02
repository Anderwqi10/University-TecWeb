"""Endpoints HTTP CRUD de estudiantes protegidos por JWT"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.student_model import Student, StudentReponse
from controllers.student_controller import StudentController
from core.database import get_db
from core.deps import get_current_user
from models.db_user_model import User as UserDB

router = APIRouter(prefix="/students")

@router.get("", response_model=list[StudentReponse])
def get_students(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # Devuelve los estudiantes del usuario autenticado
    return StudentController.get_all(current_user.id, db)

@router.get("/{student_id}", response_model=StudentReponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # Devuelve un estudiante específico del usuario actual
    return StudentController.get_by_id(student_id, current_user.id, db)

@router.post("", response_model=StudentReponse)
def create_student(
    student: Student,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # Crea estudiante asociado al usuario actual
    return StudentController.create(student, current_user.id, db)

@router.put("/{student_id}", response_model=StudentReponse)
def update_student(
    student_id: int,
    student: Student,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # Actualiza un estudiante existente del usuario.
    return StudentController.update(student_id, student, current_user.id, db)


@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # Elimina un estudiante del usuario.
    return StudentController.delete(student_id, current_user.id, db)
