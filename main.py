from fastapi import FastAPI
from routes import students
from database import engine, Base
Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(students.router)