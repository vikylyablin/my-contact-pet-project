from sqlalchemy import create_engine, Column, Integer, String, Boolean, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./contacts.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    phone = Column(String, index=True, nullable=False)
    category = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    note = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    is_pinned = Column(Boolean, default=False)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Поддержка миграции: добавляем отсутствующие колонки
    inspector = inspect(engine)
    if inspector.has_table('contacts'):
        columns = [col['name'] for col in inspector.get_columns('contacts')]
        
        with engine.begin() as conn:
            if 'avatar' not in columns:
                conn.execute(text("ALTER TABLE contacts ADD COLUMN avatar TEXT"))
            if 'address' not in columns:
                conn.execute(text("ALTER TABLE contacts ADD COLUMN address TEXT"))
            if 'note' not in columns:
                conn.execute(text("ALTER TABLE contacts ADD COLUMN note TEXT"))