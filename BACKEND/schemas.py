from typing import Optional
from pydantic import BaseModel

class ContactBase(BaseModel):
    name: str
    phone: str
    category: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None
    avatar: Optional[str] = None
    is_pinned: bool = False

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    category: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None
    avatar: Optional[str] = None
    is_pinned: Optional[bool] = None

class Contact(ContactBase):
    id: int | None = None

    class Config:
        from_attributes = True
