from pydantic import BaseModel,EmailStr


# Schemas for new user create
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str

# Schemas for user login
class UserLogin(BaseModel):
    username: str
    password: str   




