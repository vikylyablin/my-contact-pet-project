import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, Text


# Загружаем переменные из .env
load_dotenv()

# Берем URL из окружения, если его нет — используем sqlite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./contacts.db")

# database.py
engine = create_engine(
    DATABASE_URL, 
    #Это убирает ошибку "database is locked" в SQLite
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String, nullable=True)
    category = Column(String, nullable=True)
    address = Column(String, nullable=True) 
    note = Column(Text, nullable=True)
    avatar = Column(Text, nullable=True)
    is_pinned = Column(Boolean, default=False)

def init_db():
    Base.metadata.create_all(bind=engine)
