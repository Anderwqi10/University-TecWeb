"""Lógica de negocio CRUD de estudiantes por usuario autenticado."""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.student_model import Student
from models.db_model import Student as StudentDB


class StudentController:

    @staticmethod
    def get_all(user_id: int, db: Session):
        # Lista solo los estudiantes del usuario actual.
        return db.query(StudentDB).filter(StudentDB.user_id == user_id).all()

    @staticmethod
    def get_by_id(student_id: int, user_id: int, db: Session):
        # Busca un estudiante por id, restringido por propietario.
        student = (
            db.query(StudentDB)
            .filter(StudentDB.id == student_id, StudentDB.user_id == user_id)
            .first()
        )
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return student

    @staticmethod
    def create(student: Student, user_id: int, db: Session):
        # Crea estudiante y lo asocia al usuario autenticado.
        new_student = StudentDB(**student.model_dump(), user_id=user_id)
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return new_student

    @staticmethod
    def update(student_id: int, student: Student, user_id: int, db: Session):
        # Reutiliza get_by_id para validar pertenencia antes de editar.
        existing = StudentController.get_by_id(student_id, user_id, db)
        for key, value in student.model_dump().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing

    @staticmethod
    def delete(student_id: int, user_id: int, db: Session):
        # Elimina solo si el registro pertenece al usuario.
        existing = StudentController.get_by_id(student_id, user_id, db)
        db.delete(existing)
        db.commit()
        return {"deleted": True, "id": student_id}
