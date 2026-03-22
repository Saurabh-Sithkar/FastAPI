from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "Sithkar"}

@app.get("/greet")
def greet():
    return {"message": "Welcome to FastAPI!"}

@app.get("/greet/")
def read_item(name: str,age: Optional[int] = None):
    return {"Message": f"Hello, {name}! and age is {age}"}


class Student(BaseModel):
    name: str
    age: int
    roll : int

@app.post("/create_student")
def create_student(student: Student):
    return {
        "name": student.name,
        "age": student.age, 
        "roll": student.roll
    }



