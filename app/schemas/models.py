from datetime import date, datetime, UTC
from enum import Enum as PyEnum
from typing import Optional

from markdown_it.rules_block import table
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM

#ENUM DEFINITIONS
class UserRole(str, PyEnum):
    shelter_staff = "shelter_staff"
    adopter = "adopter"

class AdoptionStatus(str, PyEnum):
    available = "Available"
    pending = "Pending"
    adopted = "Adopted"
    quarantine = "Quarantine"

class RequestStatus(str, PyEnum):
    submitted = "Submitted"
    approved = "Approved"
    rejected = "Rejected"

#helper for enum in PostgreSQl
def enum_column(enum_class):
    return Column(ENUM(enum_class, enum_class.__name__.lower()), nullable=False)

class Organization(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name:str = Field(index=True, unique=True)
    contact_email: Optional[EmailStr] = Field(default=None, unique=True)
    admin_id:int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class Shelter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organization.id")
    name: str
    city: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    contact_email: Optional[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
