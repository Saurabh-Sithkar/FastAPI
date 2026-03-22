from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models,schemas,utils
from auth_database import get_db    
from jose import jwt
from datetime import datetime, timedelta    
import fastapi.security as OAth2PasswordRequestForm


SECRET_KEY = "X8EOsMzLhL8AbklmFPgbsxfj5oobjZluLS_kSIxwQNw"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Helper function to create user data
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


app = FastAPI()

@app.post("/signup")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check the user exits or not
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    
    existing_email = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    
    # Hash the password and create a new user
    hashed_pass = utils.hash_password(user.password)
    # create a new user instance and save to the database
    new_user = models.User(username=user.username, email=user.email, hased_password=hashed_pass, role=user.role)

    # Save the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Return the created user details (excluding password)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email, "role": new_user.role}



@app.post("/login")
def login(form_data: OAth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    if not utils.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}





