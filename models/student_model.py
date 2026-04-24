from pydantic import BaseModel, Field

class Student(BaseModel):
    name: str= Field(...,min_length=2)
    age: int = Field(..., gt=0)
    grade: float=Field(...,ge=0,le=5)

class StudentReponse(Student):
    id:int