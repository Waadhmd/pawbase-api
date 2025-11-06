from typing import Optional
from datetime import date
from sqlmodel import SQLModel


class MedicalRecordBase(SQLModel):
    animal_id: int
    vet_notes: Optional[str] = None
    exam_date: date
    condition: Optional[str] = None


class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordRead(MedicalRecordBase):
    id: int
    staff_user_id: int


class MedicalRecordUpdate(MedicalRecordBase):
    animal_id: Optional[int] = None
    vet_notes: Optional[str] = None
    exam_date: Optional[date] = None
    condition: Optional[str] = None