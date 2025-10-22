from datetime import date, datetime, timezone
from enum import Enum as PyEnum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM

#ENUM DEFINITIONS
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
    return Column(ENUM(enum_class, name=enum_class.__name__.lower()), nullable=False)

class Organization(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    contact_email: Optional[EmailStr] = Field(default=None, unique=True)
    admin_id:int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    #Python side Relationship
    admin_user: "User" = Relationship(back_populates="managed_organization")
    shelters: list["Shelter"] = Relationship(back_populates="organization")


class Shelter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organization.id")
    name: str = Field(index=True)
    city: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    contact_email: Optional[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    organization: Organization = Relationship(back_populates="shelters")
    animals : list["Animal"] = Relationship(back_populates="shelter")
    staff_memberships: list["Staff"] = Relationship(back_populates="shelter")
    adoption_requests: list["AdoptionRequest"] = Relationship(back_populates="shelter")

class User(SQLModel, table=True):
    id:Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    password_hash: str
    avatar_url: Optional[str] = None
    created_at:datetime = Field(default_factory=lambda : datetime.now(timezone.utc))

    managed_organization: Optional[Organization] = Relationship(back_populates="admin_user")
    staff_users: list["Staff"] = Relationship(back_populates="user")
    medical_records: list["MedicalRecord"] = Relationship(back_populates="staff_user")
    vaccinations: list["Vaccination"] = Relationship(back_populates="staff_user")

class Staff(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    shelter_id: int = Field(foreign_key="shelter.id")

    user: User = Relationship(back_populates="staff_users")
    shelter : Shelter = Relationship(back_populates="staff_memberships")

class Animal(SQLModel, table=True):
    id:Optional[int] = Field(default=None, primary_key=True)
    breed_name: str
    species_name: str
    shelter_id:int = Field(foreign_key="shelter.id")
    name: str
    status: AdoptionStatus = Field(sa_column=enum_column(AdoptionStatus))
    date_of_birth: Optional[date] = None
    weight: Optional[float] = None
    is_neutered: bool
    public_description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda :datetime.now(timezone.utc))

    shelter: Shelter = Relationship(back_populates="animals")
    medical_records: list["MedicalRecord"] = Relationship(back_populates="animal")
    vaccinations: list["Vaccination"] = Relationship(back_populates="animal")
    adoption_requests: list["AdoptionRequest"] = Relationship(back_populates="animals")

class MedicalRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    animal_id: int = Field(foreign_key="animal.id")
    staff_user_id: int = Field(foreign_key="user.id")
    vet_notes: Optional[str] = None
    exam_date: date
    condition: Optional[str] = None

    animal: Animal = Relationship(back_populates="medical_records")
    staff_user: User = Relationship(back_populates="medical_records")

class Vaccination(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    animal_id: int = Field(foreign_key="animal.id")
    staff_user_id: int = Field(foreign_key="user.id")
    vaccine_type: str
    vaccination_date: date
    valid_until: date
    notes: Optional[str] = None

    animal: Animal = Relationship(back_populates="vaccinations")
    staff_user: User = Relationship(back_populates="vaccinations")

class AdoptionRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    animal_id: int = Field(foreign_key="animal.id")
    adopter_user_id: int = Field(foreign_key="user.id")
    shelter_id: int = Field(foreign_key="shelter.id")
    status: RequestStatus = Field(sa_column=enum_column(RequestStatus))
    request_date: datetime = Field(default_factory=lambda : datetime.now(timezone.utc))
    staff_notes: Optional[str] = None

    animal: Animal = Relationship(back_populates="adoption_requests")
    shelter : "Shelter" = Relationship(back_populates="adoption_requests")
















