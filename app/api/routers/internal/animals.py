from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.database import get_session
from app.core.deps import get_current_user
from app.schemas.models import User, Animal
from app.schemas.schema_animal import AnimalCreate, AnimalRead, AnimalUpdate

router = APIRouter()


@router.post("/", response_model=AnimalRead, status_code=status.HTTP_201_CREATED)
def create_animal(
    animal_in: AnimalCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new animal entry (staff/admin only)."""

    #could later check if current_user belongs to shelter/organization
    animal = Animal(**animal_in.model_dump())
    session.add(animal)
    session.commit()
    session.refresh(animal)
    return animal


@router.get("/", response_model=List[AnimalRead])
def read_animals(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Return all animals (visible to authorized users)."""
    animals = session.exec(select(Animal)).all()
    return animals


@router.get("/{animal_id}", response_model=AnimalRead)
def read_animal(
    animal_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single animal by ID."""
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found.")
    return animal


@router.patch("/{animal_id}", response_model=AnimalRead)
def update_animal(
    animal_id: int,
    animal_in: AnimalUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Update an animal's information (staff/admin only)."""
    animal_db = session.get(Animal, animal_id)
    if not animal_db:
        raise HTTPException(status_code=404, detail="Animal not found.")

    update_data = animal_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(animal_db, key, value)

    session.add(animal_db)
    session.commit()
    session.refresh(animal_db)
    return animal_db


@router.delete("/{animal_id}")
def delete_animal(
    animal_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete an animal record (admin only)."""
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found.")

    session.delete(animal)
    session.commit()
    return {"ok": True}
