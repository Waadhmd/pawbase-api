from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime, date
from app.schemas.enums import  RequestStatus

#-----------------------
#AdoptionRequest Schema
#-----------------------

class AdoptionRequestBase(SQLModel):
    animal_id: int
    adopter_user_id: int
    status: RequestStatus = RequestStatus.submitted
    staff_notes: Optional[str] = None

class AdoptionRequestCreate(AdoptionRequestBase):
    pass

class AdoptionRequestRead(AdoptionRequestBase):
    id: int
    request_date: datetime

class AdoptionRequestUpdate(AdoptionRequestBase):
    animal_id: Optional[int] = None
    adopter_user_id: Optional[int] = None
    status: Optional[RequestStatus] = None
    staff_notes: Optional[str] = None