from sqlmodel import SQLModel
from pydantic import EmailStr
from typing import Optional
from datetime import datetime, date
from app.schemas.models import AdoptionStatus, RequestStatus

class UserBase(SQLModel):
    email: EmailStr
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str #plain password from the client

class UserRead(UserBase):
    id:int
    created_at: datetime

class UserUpdate(UserBase):
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = None


#-----------------------
#AdoptionRequest Schema
#-----------------------
#Don’t require login for the adopter.
#Store adopter info (name/email/phone) inside AdoptionRequest.
#Generate a unique request tracking ID (UUID) so adopters can check their status later using a public endpoint like /adoption/status/{tracking_code}.

class AdoptionRequestBase(SQLModel):
    animal_id: int
    #adopter_user_id: int
    shelter_id: int
    full_name: str
    email: str
    phone: Optional[str] = None

class AdoptionRequestCreate(AdoptionRequestBase):
    pass

class AdoptionRequestRead(AdoptionRequestBase):
    id: int
    tracking_code: str
    status: RequestStatus
    request_date: datetime
    staff_notes: Optional[str] = None

class AdoptionRequestUpdate(AdoptionRequestBase):
    #adopter_user_id: Optional[int] = None
    status: Optional[RequestStatus] = None
    staff_notes: Optional[str] = None

