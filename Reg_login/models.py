from sqlalchemy import Column, Integer, String, Date
from passlib.context import CryptContext
from database import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    cgpa = Column(String(10), index=True)
    program = Column(String(50), index=True)
    address = Column(String(100))
    sex = Column(String(10))
    blood = Column(String(5))
    birth_date = Column(Date)
    phone = Column(String(15), unique=True)
    

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)
