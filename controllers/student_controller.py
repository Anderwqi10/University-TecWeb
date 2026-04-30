from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from models.student_model import Student
from models.db_model import Student as StudentDB
from database import get_db

class StudentController:
    @staticmethod
    def get_all(db: Session=Depends(get_db)) -> list[dict]:
        return db.query(StudentDB).all()
    
    @staticmethod
    def get_by_id(student_id: int, db: Session=Depends(get_db))-> dict:
        student = db.query(StudentDB).filter(student_id == StudentDB.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        return student
    
    @staticmethod
    def create(student: Student, db: Session=Depends(get_db)):
        new_student = StudentDB(**student.model_dump())
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return new_student
    
    @staticmethod
    def update(student_id: int, student: Student, db: Session=Depends(get_db)):
        existing_student = db.query(StudentDB).filter(student_id == StudentDB.id).first()
        if not existing_student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        for key, value in student.model_dump().items():
            setattr(existing_student, key, value)
        db.commit()
        db.refresh(existing_student)
        return existing_student
    
    @staticmethod
    def delete(student_id: int, db: Session=Depends(get_db)):
        student = db.query(StudentDB).filter(student_id == StudentDB.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        db.delete(student)
        db.commit()
        return {"detail": "Estudiante eliminado"}