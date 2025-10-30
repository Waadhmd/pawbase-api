from sqlmodel import SQLModel
from pydantic import EmailStr, validator, field_validator
from typing import Optional
from datetime import datetime
from app.schemas.enums import UserRole

class UserBase(SQLModel):
    email: EmailStr
    avatar_url: Optional[str] = None
    role: UserRole


    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v):
        """Ensure role is lowercase to match DB enum values."""
        if isinstance(v, str):
            return v.lower()
        if isinstance(v, UserRole):
            return v.value.lower()
        return v

class UserCreate(UserBase):
    password: str #plain password from the client

class UserRead(UserBase):
    id:int
    created_at: datetime

class UserUpdate(UserBase):
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = None
    role : Optional[UserRole] = None
