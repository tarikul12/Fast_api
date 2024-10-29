# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from typing import Optional
# from passlib.context import CryptContext

# # Set up SQLite database
# DATABASE_URL = "sqlite:///test.sqlite3"

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
# Base.metadata.create_all(bind=engine)

# # Password hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Base.metadata.create_all(bind=engine)


# # Dependency to get the DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
