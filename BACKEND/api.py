#Этот файл содержит функции для работы с базой данных, связанные с контактами.
#CRUD - Create, Read, Update, Delete
#Выполнение операций с базой данных через SQLAlchemy.
#Этот файл не знает ничего про интернет или HTTP-запросы,
#он умеет только манипулировать данными в таблицах.

from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import Session
from database import Contact
from fastapi import HTTPException
from database import Contact

def get_contacts(db: Session, skip=0, limit=20):
    return db.query(Contact).offset(skip).limit(limit).all()

#принимает любое количество па    раметров 
#(email, category, address, note, avatar)
def create_contact(db: Session, **kwargs):
    # kwargs теперь содержит name, phone, email, address и т.д.
    db_contact = Contact(**kwargs)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def delete_contact(db, contact_id: int):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return contact

def delete_contacts(db, ids: list[int]):
    contacts = db.query(Contact).filter(Contact.id.in_(ids)).all()
    if not contacts:
        raise HTTPException(status_code=404, detail="Contacts not found")
    for contact in contacts:
        db.delete(contact)
    db.commit()
    return contacts


def update_contact(db, contact_id: int, **kwargs):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    for key, value in kwargs.items():
        if hasattr(contact, key):
            setattr(contact, key, value)
    db.commit()
    db.refresh(contact)
    return contact
    