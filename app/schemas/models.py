from datetime import date, datetime, timezone
from typing import Optional
from app.schemas.enums import AdoptionStatus, RequestStatus
from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM
from app.schemas.schema_shelter import ShelterBase
from app.schemas.schema_user import UserBase
from app.schemas.schema_animal import AnimalBase
from app.schemas.schema_AdoptionRequest import AdoptionRequestBase


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


class Shelter(ShelterBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    organization_id: int = Field(foreign_key="organization.id")
    name: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    organization: Organization = Relationship(back_populates="shelters")
    animals : list["Animal"] = Relationship(back_populates="shelter")
    staff_memberships: list["Staff"] = Relationship(back_populates="shelter")
    adoption_requests: list["AdoptionRequest"] = Relationship(back_populates="shelter")

class User(UserBase, table=True):
    id:Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    password_hash: str
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

class Animal(AnimalBase, table=True):
    id:Optional[int] = Field(default=None, primary_key=True)
    shelter_id:int = Field(foreign_key="shelter.id")
    status: AdoptionStatus = Field(sa_column=enum_column(AdoptionStatus))
    created_at: datetime = Field(default_factory=lambda :datetime.now(timezone.utc))

    shelter: Shelter = Relationship(back_populates="animals")
    medical_records: list["MedicalRecord"] = Relationship(back_populates="animal")
    vaccinations: list["Vaccination"] = Relationship(back_populates="animal")
    adoption_requests: list["AdoptionRequest"] = Relationship(back_populates="animal")

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

class AdoptionRequest(AdoptionRequestBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    animal_id: int = Field(foreign_key="animal.id")
    adopter_user_id: int = Field(foreign_key="user.id")
    shelter_id: int = Field(foreign_key="shelter.id")
    status: RequestStatus = Field(sa_column=enum_column(RequestStatus))
    request_date: datetime = Field(default_factory=lambda : datetime.now(timezone.utc))

    animal: Animal = Relationship(back_populates="adoption_requests")
    shelter : "Shelter" = Relationship(back_populates="adoption_requests")
















