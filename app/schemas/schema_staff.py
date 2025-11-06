from typing import Optional
from sqlmodel import SQLModel, Field

class StaffBase(SQLModel):
    user_id: int
    shelter_id: int

class StaffCreate(StaffBase):
    pass

class StaffRead(StaffBase):
    id: int

class StaffUpdate(SQLModel):
    shelter_id: Optional[int] = None