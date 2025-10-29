from sqlmodel import SQLModel
from pydantic import EmailStr
from typing import Optional
from datetime import datetime

# Base Schema
# ----------------------------
class OrganizationBase(SQLModel):
    name: str
    contact_email: Optional[EmailStr] = None
    admin_id: int

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationRead(OrganizationBase):
    id:int
    created_at: datetime

class OrganizationUpdate(OrganizationBase):
    name: Optional[str] = None
    contact_email: Optional[str] = None
    admin_id: Optional[int] = None

