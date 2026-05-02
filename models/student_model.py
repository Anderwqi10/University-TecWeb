"""Modelos Pydantic para validar entrada/salida de estudiantes."""

from pydantic import BaseModel, Field

class Student(BaseModel):
    # Payload de creación/edición.
    name: str= Field(...,min_length=2)
    age: int = Field(..., gt=0)
    grade: float=Field(...,ge=0,le=5)

class StudentReponse(Student):
    # Respuesta API incluye ID generado por DB.
    id:int