from sqlalchemy.orm import Session
from database import Contact
from fastapi import HTTPException

def get_contacts(db: Session, skip=0, limit=20):
    return db.query(Contact).offset(skip).limit(limit).all()

#принимает любое количество параметров 
#(email, category, address, note, avatar)
def create_contact(db: Session, **kwargs):
    try:
        contact = Contact(**kwargs)
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact
    except Exception:
        db.rollback()
        raise

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
    