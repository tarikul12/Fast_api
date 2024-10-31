from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4
import os
from starlette.middleware.sessions import SessionMiddleware
from database import get_db
from models import User
from database import engine
from models import Base
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi import Request

# Initialize FastAPI app
app = FastAPI()

secret_key = os.getenv("SECRET_KEY", "fallback_dev_key_for_local")
app.add_middleware(SessionMiddleware, secret_key="secret_key")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
Base.metadata.create_all(bind=engine)

# Templates and Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/home")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/register")
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(
    request: Request, 
    username: str = Form(...), 
    email: str = Form(...), 
    password: str = Form(...),
    cgpa: str = Form(...),
    program: str = Form(...),
    address: str = Form(...),
    sex: str = Form(...),
    blood: str = Form(...),
    birth_date: str = Form(...),  # Still accepting as string
    phone: str = Form(...), 
    db: Session = Depends(get_db)
):
    # Check if username already exists
    if get_user(db, username):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already registered"})
    
    # Hash the password
    hashed_password = get_password_hash(password)
    
    # Convert birth_date string to a date object
    try:
        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
    except ValueError:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Invalid birth date format. Use YYYY-MM-DD."})

    # Create the new user
    new_user = User(
        username=username, 
        email=email, 
        hashed_password=hashed_password, 
        cgpa=cgpa, 
        program=program, 
        address=address, 
        sex=sex, 
        blood=blood, 
        birth_date=birth_date, 
        phone=phone
    )
    db.add(new_user)
    db.commit()
    
    # Redirect to login
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@app.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")
    
    
    user = db.query(User).filter(User.username == username).first()
    if user and user.verify_password(password):  
        request.session["username"] = user.username 
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return {"error": "Invalid credentials"}

@app.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    session_id = request.session.get("session_id")
    if "username" not in request.session:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    users = db.query(User).all()
    total_count = db.query(User).count()
    cgpa_count = db.query(User.cgpa).distinct().count()
    email_count = db.query(User.email).distinct().count()
    program_count = db.query(User.program).distinct().count()
    sex_count = db.query(User.sex).distinct().count()
    blood_count = db.query(User.blood).distinct().count()
    
    #sex graph show
    male_count = db.query(User).filter(User.sex == 'male').count()
    female_count = db.query(User).filter(User.sex == 'female').count()
    
    #blood graph show
    blood_counts = {
        "A+": db.query(User).filter(User.blood == 'A+').count(),
        "A-": db.query(User).filter(User.blood == 'A-').count(),
        "B+": db.query(User).filter(User.blood == 'B+').count(),
        "B-": db.query(User).filter(User.blood == 'B-').count(),
        "O+": db.query(User).filter(User.blood == 'O+').count(),
        "O-": db.query(User).filter(User.blood == 'O-').count(),
        "AB+": db.query(User).filter(User.blood == 'AB+').count(),
        "AB-": db.query(User).filter(User.blood == 'AB-').count(),
    }


    return templates.TemplateResponse("dashboard.html", {"request": request, "users": users, "total_count": total_count,"cgpa_count":cgpa_count,"sex_count":sex_count,"blood_count":blood_count,"email_count":email_count,
                                                          "male_count": male_count,
        "female_count": female_count,"program_count":program_count,"blood_counts": blood_counts})

@app.get('/all_user')
async def all_user(request: Request, db: Session = Depends(get_db)):
      users = db.query(User).all()
      return templates.TemplateResponse("all_user.html", {"request": request, "users": users})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()  # Clear all session data
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


def get_current_user(request: Request, db: Session):
    
    username = request.session.get("username") 
    
    if not username:
        return None
    
    user = db.query(User).filter(User.username == username).first()
    return user


@app.get("/profile")
async def profile(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("profile.html", {"request": request, "current_user": current_user})
 


@app.get("/profile/edit")
async def edit_profile(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("edit_profile.html", {"request": request, "current_user": current_user})

@app.post("/profile/update/{user_id}")
async def update_user(user_id: int, username: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    retries = 3
    for attempt in range(retries):
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Update user details
            user.username = username
            user.email = email
            db.commit()  # Save the changes
            return {"message": "User updated successfully"}
        except OperationalError:
            if attempt < retries - 1:
                time.sleep(1)  # Wait a second before retrying
            else:
                raise HTTPException(status_code=500, detail="Database is currently busy. Please try again later.")

