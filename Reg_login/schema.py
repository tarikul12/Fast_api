# from datetime import date
# from pydantic import BaseModel, EmailStr ,Field
# from enum import Enum
# from fastapi import Form
 
 
# class UserSchema(BaseModel):
#     email: EmailStr
#     username: str
#     password: str  = Field(..., min_length=4)

# class ShowUser(BaseModel):
#     id: int
#     email: EmailStr
#     is_active: bool

#     class Config:
#         orm_mode = True