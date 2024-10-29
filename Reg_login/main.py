# from fastapi import FastAPI, Form, Depends, Request, HTTPException
# from fastapi.templating import Jinja2Templates
# from sqlalchemy import Column, Integer, String, create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from passlib.context import CryptContext
# from starlette.middleware.sessions import SessionMiddleware
# from starlette.responses import RedirectResponse
# # from database import get_db,SessionLocal
# # from models import User
# app = FastAPI()

# # Set up session
# app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

# # Set up Jinja2Templates
# templates = Jinja2Templates(directory="templates")


# # Utility to get a user by username
# def get_user_by_username(db, username: str):
#     return db.query(User).filter(User.username == username).first()

# # Utility to verify password
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# # Utility to hash password
# def hash_password(password: str):
#     return pwd_context.hash(password)

# @app.get("/navbar")
# def index(request: Request):
#     return templates.TemplateResponse("navbar.html", {"request": request})

# # Registration route
# @app.get("/register")
# def show_register_form(request: Request):
#     return templates.TemplateResponse("register.html", {"request": request})

# # @app.post("/register")
# # def register_user(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), db: SessionLocal = Depends(get_db)):
# #     user = get_user_by_username(db, username)
# #     if user:
# #         raise HTTPException(status_code=400, detail="Username already taken")
    
# #     hashed_password = hash_password(password)
# #     new_user = User(username=username, email=email, password=hashed_password)
# #     db.add(new_user)
# #     db.commit()
# #     db.refresh(new_user)
    
# #     return RedirectResponse("/login", status_code=303)

# # Login route
# @app.get("/login")
# def show_login_form(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

# # @app.post("/login")
# # def login_user(request: Request, username: str = Form(...), password: str = Form(...), db: SessionLocal = Depends(get_db)):
# #     user = get_user_by_username(db, username)
# #     if not user or not verify_password(password, user.password):
# #         raise HTTPException(status_code=400, detail="Invalid credentials")
    
# #     request.session['username'] = user.username
# #     return RedirectResponse("/dashboard", status_code=303)

# # Dashboard route
# @app.get("/dashboard")
# def dashboard(request: Request):
#     username = request.session.get('username')
#     if not username:
#         return RedirectResponse("/login")
#     return templates.TemplateResponse("dashboard.html", {"request": request, "username": username})

# # Logout route
# @app.get("/logout")
# def logout(request: Request):
#     request.session.clear()
#     return RedirectResponse("/login")

# main.py
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from uuid import uuid4

app = FastAPI()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Templates and Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory database and sessions
fake_users_db = {}
sessions = {}

# User model
class User(BaseModel):
    username: str
    email: str
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    return db.get(username)

def authenticate_user(username: str, password: str):
    user = get_user(fake_users_db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

@app.get("/base")
async def base(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/register")
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    if username in fake_users_db:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already registered"})
    
    hashed_password = get_password_hash(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    fake_users_db[username] = new_user
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@app.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect username or password"})
    
    session_id = str(uuid4())
    sessions[session_id] = user.username
    response = RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="session_id", value=session_id)
    return response

def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    username = sessions.get(session_id)
    if not username:
        return None
    return get_user(fake_users_db, username)

@app.get("/profile")
async def profile(request: Request):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("profile.html", {"request": request, "user": current_user})

@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="session_id")
    return response
