from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models,schemas,utils
from auth_database import get_db    
from jose import jwt, JWTError
from datetime import datetime, timedelta    
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer


SECRET_KEY = "X8EOsMzLhL8AbklmFPgbsxfj5oobjZluLS_kSIxwQNw"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
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
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_pass, role=user.role)

    # Save the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Return the created user details (excluding password)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email, "role": new_user.role}



@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username")
    
    if not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    token_data = {"sub": user.username,'role':user.role}
    token = create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer"}



def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return {"username": username, "role": role}

@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, {current_user['username']}! You have accessed a protected route.", "role": current_user['role']}


def require_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user['role'] != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource")
        return current_user
    return role_checker

@app.get("/profile")
def read_profile(current_user: dict = Depends(require_role("user"))):
    return {"message": f"Hello, {current_user['username']}! This is your profile.", "role": current_user['role']}

@app.get("/user/dashboard")
def user_dashboard(current_user: dict = Depends(require_role("user"))):
    return {"message":"Welcome User"}

@app.get("/admin/dashboard")
def admin_dashboard(current_user: dict = Depends(require_role("admin"))):
    return {"message":"Welcome Admin"}


