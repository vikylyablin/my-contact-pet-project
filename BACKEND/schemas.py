from typing import Optional
from pydantic import BaseModel, field_validator, EmailStr
import re

class ContactBase(BaseModel):
    name: str
    phone: str
    category: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    note: Optional[str] = None
    avatar: Optional[str] = None
    is_pinned: bool = False
    search: str | None = None

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
    
    @field_validator("phone")
    def validate_phone(cls, v):
        if not re.match(r"^\+?\d{10,15}$", v):
            raise ValueError("Invalid phone number")
        return v

class Contact(ContactBase):
    id: int | None = None

    class Config:
        from_attributes = True
