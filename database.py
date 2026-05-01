from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Use SQLite by default for easy development, unless MYSQL_URL is provided
# e.g., MYSQL_URL = "mysql+pymysql://user:password@localhost/dyslexiread"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dyslexiread.db")

# For SQLite, we need connect_args={"check_same_thread": False}
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL, connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
