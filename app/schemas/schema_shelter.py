from sqlmodel import SQLModel,  Field, Relationship
from datetime import  datetime, timezone
from pydantic import EmailStr
from typing import Optional


# Base schema
# ---------------------
class ShelterBase(SQLModel):
    organization_id: int
    name: str
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None


# Schemas
# ---------------------
class ShelterCreate(ShelterBase):
    """Used when creating a new shelter."""
    pass

class ShelterRead(ShelterBase):
    """Returned when reading shelter data."""
    id: int
    created_at: datetime

class ShelterUpdate(ShelterBase):
    organization_id: Optional[int] = None
    name: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
