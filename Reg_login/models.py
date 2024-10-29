# from sqlalchemy import Column,String,Integer,Boolean,Enum
# from database import  Base
 
# class User(Base):
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, nullable=False, unique=True, index=True)
#     password = Column(String, nullable=False)
#     is_active = Column(Boolean(), default=True)


# User model
# class User(BaseModel):
#     username: str
#     email: str
#     hashed_password: str

# class UserCreate(BaseModel):
#     username: str
#     email: str
#     password: str