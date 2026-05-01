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
    def update(student_id: int, student: Student, db: Session):
        student_db = db.query(StudentDB).filter(StudentDB.id == student_id).first()

        if not student_db:
            raise HTTPException(status_code=404, detail="Student not found")

        student_db.name = student.name
        student_db.age = student.age
        student_db.grade = student.grade

        db.commit()
        db.refresh(student_db)

        return student_db

    @staticmethod
    def delete(student_id: int, db: Session):
        student_db = db.query(StudentDB).filter(StudentDB.id == student_id).first()

        if not student_db:
            raise HTTPException(status_code=404, detail="Student not found")

        db.delete(student_db)
        db.commit()

        return student_db




