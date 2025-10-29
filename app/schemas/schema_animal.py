from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime, date
from app.schemas.enums import AdoptionStatus


class AnimalBase(SQLModel):
    breed_name: str
    species_name: str
    shelter_id: int
    name: str
    status: AdoptionStatus = AdoptionStatus.available
    date_of_birth: Optional[date] = None
    weight: Optional[float] = None
    is_neutered: bool
    public_description: Optional[str] = None

class AnimalCreate(AnimalBase):
    pass

class AnimalRead(AnimalBase):
    id: int
    created_at: datetime

class AnimalUpdate(AnimalBase):
    breed_name: Optional[str] = None
    species_name: Optional[str] = None
    shelter_id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[AdoptionStatus] = None
    date_of_birth: Optional[date] = None
    weight: Optional[float] = None
    is_neutered: Optional[bool] = None
    public_description: Optional[str] = None