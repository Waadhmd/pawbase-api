from sqlmodel import SQLModel
from datetime import  date
from typing import Optional

class VaccinationBase(SQLModel):
    animal_id: int
    vaccine_type: str
    vaccination_date: date
    valid_until: date
    notes: Optional[str] = None

class VaccinationCreate(VaccinationBase):
    pass

class VaccinationRead(VaccinationBase):
    id: int
    staff_user_id: int

class VaccinationUpdate(VaccinationBase):
    animal_id: Optional[int] = None
    staff_user_id :Optional[int] = None
    vaccination_date: Optional[date] = None
    vaccine_type : Optional[str] = None
    valid_until : Optional[date] = None
    notes : Optional[str] = None