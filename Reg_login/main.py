from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
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


# Initialize FastAPI app
app = FastAPI()

secret_key = os.getenv("SECRET_KEY", "fallback_dev_key_for_local")
app.add_middleware(SessionMiddleware, secret_key="secret_key")


# Templates and Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_password_hash(password):
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
async def register_user(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if get_user(db, username):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already registered"})
    
    hashed_password = get_password_hash(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
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
    if not session_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    users = db.query(User).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "users": users})

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
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("edit_profile.html", {"request": request, "current_user": current_user})


@app.post("/profile/edit")
async def update_profile(request: Request, username: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    current_user = get_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Update user details
    current_user.username = username
    current_user.email = email
    db.commit()  # Save the changes

    # Redirect to the profile page after update
    return RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)
