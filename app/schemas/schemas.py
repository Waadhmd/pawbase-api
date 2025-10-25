from sqlmodel import SQLModel
from pydantic import EmailStr
from typing import Optional
from datetime import datetime

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