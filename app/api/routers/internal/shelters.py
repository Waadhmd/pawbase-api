from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.database import get_session
from app.core.deps import get_current_user
from app.schemas.models import User, Shelter
from app.schemas.schema_shelter import ShelterCreate, ShelterRead, ShelterUpdate

router = APIRouter()


@router.post("/", response_model=ShelterRead, status_code=status.HTTP_201_CREATED)
def create_shelter(
    shelter_in: ShelterCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    #ensure organization exists or belongs to current user
    existing_shelter = session.exec(
        select(Shelter).where(Shelter.name == shelter_in.name)
    ).first()

    if existing_shelter:
        raise HTTPException(status_code=400, detail="Shelter with this name already exists.")

    shelter = Shelter(**shelter_in.model_dump())
    session.add(shelter)
    session.commit()
    session.refresh(shelter)
    return shelter


@router.get("/", response_model=List[ShelterRead])
def read_shelters(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    shelters = session.exec(select(Shelter)).all()
    return shelters


@router.get("/{shelter_id}", response_model=ShelterRead)
def read_shelter(
    shelter_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    shelter = session.get(Shelter, shelter_id)
    if not shelter:
        raise HTTPException(status_code=404, detail="Shelter not found.")
    return shelter


@router.patch("/{shelter_id}", response_model=ShelterRead)
def update_shelter(
    shelter_id: int,
    shelter_in: ShelterUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    shelter_db = session.get(Shelter, shelter_id)
    if not shelter_db:
        raise HTTPException(status_code=404, detail="Shelter not found.")

    update_data = shelter_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(shelter_db, key, value)

    session.add(shelter_db)
    session.commit()
    session.refresh(shelter_db)
    return shelter_db


@router.delete("/{shelter_id}")
def delete_shelter(
    shelter_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    shelter = session.get(Shelter, shelter_id)
    if not shelter:
        raise HTTPException(status_code=404, detail="Shelter not found.")

    session.delete(shelter)
    session.commit()
    return {"ok": True}
