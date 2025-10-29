from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.database import get_session
from app.core.deps import get_current_user
from app.schemas.models import User, AdoptionRequest
from app.schemas.schema_AdoptionRequest import (
    AdoptionRequestCreate,
    AdoptionRequestRead,
    AdoptionRequestUpdate,
)

router = APIRouter()


@router.post("/", response_model=AdoptionRequestRead, status_code=status.HTTP_201_CREATED)
def create_adoption_request(
        request_in: AdoptionRequestCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    """Create a new adoption request (staff/admin only for now)."""

    # Optionally: check that the animal and shelter exist
    # animal = session.get(Animal, request_in.animal_id)
    # if not animal:
    #     raise HTTPException(status_code=404, detail="Animal not found")

    request = AdoptionRequest(
        animal_id=request_in.animal_id,
        adopter_user_id=request_in.adopter_user_id,
        shelter_id=request_in.shelter_id,
        status=request_in.status,
        staff_notes=request_in.staff_notes,
    )
    session.add(request)
    session.commit()
    session.refresh(request)
    return request


# ------------------------
# READ ALL
# ------------------------
@router.get("/", response_model=List[AdoptionRequestRead])
def read_adoption_requests(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    """Retrieve all adoption requests."""
    requests = session.exec(select(AdoptionRequest)).all()
    return requests


@router.get("/{request_id}", response_model=AdoptionRequestRead)
def read_adoption_request(
        request_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    """Retrieve a single adoption request by ID."""
    request = session.get(AdoptionRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Adoption request not found.")
    return request



@router.patch("/{request_id}", response_model=AdoptionRequestRead)
def update_adoption_request(
        request_id: int,
        request_in: AdoptionRequestUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    """Update an adoption request (staff/admin only)."""
    request_db = session.get(AdoptionRequest, request_id)
    if not request_db:
        raise HTTPException(status_code=404, detail="Adoption request not found.")

    update_data = request_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(request_db, key, value)

    session.add(request_db)
    session.commit()
    session.refresh(request_db)
    return request_db


@router.delete("/{request_id}")
def delete_adoption_request(
        request_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
):
    """Delete an adoption request (admin/staff only)."""
    request = session.get(AdoptionRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Adoption request not found.")

    session.delete(request)
    session.commit()
    return {"ok": True}
