from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.student_model import Student, StudentReponse
from controllers.student_controller import StudentController
from database import get_db

router = APIRouter(prefix="/students")

@router.get('/', response_model=list[StudentReponse])
def get_students(db: Session=Depends(get_db)):
    return StudentController.get_all(db)

@router.get("/{student_id}", response_model=StudentReponse)
def get_student(student_id: int, db: Session=Depends(get_db)):
    return StudentController.get_by_id(student_id, db)

@router.post("/", response_model=StudentReponse)
def create_student(student: Student, db: Session=Depends(get_db)):
    return StudentController.create(student, db)

@router.put("/{student_id}", response_model=StudentReponse)
def update_student(student_id: int, student: Student, db: Session = Depends(get_db)):
    return StudentController.update(student_id, student, db)

@router.delete("/{studend_id}")
def delete_student(studend_id: int):
    ...