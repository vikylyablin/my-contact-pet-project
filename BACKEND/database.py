import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String

# Загружаем переменные из .env
load_dotenv()

# Берем URL из окружения, если его нет — используем sqlite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./contacts.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    phone = Column(String, index=True, nullable=False)
    email = Column(String, nullable=True)
    category = Column(String, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)
