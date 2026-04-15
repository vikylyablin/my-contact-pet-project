from fastapi import FastAPI, Depends, Body
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import api, schemas
from database import SessionLocal, init_db

app = FastAPI()
init_db()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/contacts/", response_model=list[schemas.Contact])
def read_contacts(db: Session = Depends(get_db)):
    return api.get_contacts(db=db)

@app.post("/contacts/", response_model=schemas.Contact)
def create_new_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    create_data = contact.model_dump(exclude_unset=True)
    return api.create_contact(db=db, **create_data)

@app.delete("/contacts/{name}", response_model=schemas.Contact)
def delete_contact_route(name: str, db: Session = Depends(get_db)):
    return api.delete_contact(db=db, name=name)

@app.patch("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact_route(contact_id: int, contact_data: schemas.ContactUpdate, db: Session = Depends(get_db)):
    update_data = contact_data.model_dump(exclude_unset=True)
    if not update_data:
        return api.update_contact(db=db, contact_id=contact_id)
    return api.update_contact(db=db, contact_id=contact_id, **update_data)

@app.delete("/contacts/", response_model=list[schemas.Contact])
def delete_multiple_contacts_route(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    return api.delete_contacts(db=db, ids=ids)