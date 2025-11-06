from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.security import require_roles
from app.db.database import get_session
from app.core.deps import get_current_user, get_tenant_organization, get_accessible_shelter_ids, ensure_animal_access
from app.schemas.models import User, AdoptionRequest, Animal, Organization
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
    """Any logged-in user can submit an adoption request"""
    animal = session.get(Animal, request_in.animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
   #prevent duplicate request for the same animal by the same user
    existing = session.exec(select(AdoptionRequest).where(AdoptionRequest.animal_id == animal.id,AdoptionRequest.adopter_user_id == current_user.id)).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already requested adoption for this animal")
    request = AdoptionRequest(
        animal_id=request_in.animal_id,
        adopter_user_id= current_user.id,
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
@router.get("/", response_model=List[AdoptionRequestRead], dependencies=[Depends(require_roles('org_admin','staff'))])
def read_adoption_requests(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization)
):
    """Retrieve all adoption requests."""
    accessible_shelters = get_accessible_shelter_ids(session, current_user, tenant_org)
    query = select(AdoptionRequest).join(Animal).where(Animal.shelter_id.in_(accessible_shelters))
    requests = session.exec(query).all()
    return requests


@router.get("/{request_id}", response_model=AdoptionRequestRead, dependencies=[Depends(require_roles('org_admin','staff'))])
def read_adoption_request(
        request_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization)
):
    """Retrieve a single adoption request by ID."""
    request = session.get(AdoptionRequest, request_id)
    ensure_animal_access(session, current_user, tenant_org, request.animal_id)
    if not request:
        raise HTTPException(status_code=404, detail="Adoption request not found.")
    return request


@router.patch("/{request_id}", response_model=AdoptionRequestRead, dependencies=[Depends(require_roles('org_admin', 'staff'))])
def update_adoption_request(
        request_id: int,
        request_in: AdoptionRequestUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization)
):
    """Update an adoption request (staff/admin only)."""
    request_db = session.get(AdoptionRequest, request_id)
    if not request_db:
        raise HTTPException(status_code=404, detail="Adoption request not found.")
    ensure_animal_access(session, current_user, tenant_org, request_db.animal_id )
    old_status = request_db.status

    update_data = request_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(request_db, key, value)

    if "status" in update_data and update_data["status"] != old_status:
        animal_db = session.get(Animal, AdoptionRequest.animal_id)
        if not animal_db:
            raise  HTTPException(status_code=404, detail="Animal not found")
        if update_data["status"] == 'Approved':
            animal_db.status = animal_db.status.adopted
        session.add(animal_db)

    session.add(request_db)
    session.commit()
    session.refresh(request_db)
    return request_db


@router.delete("/{request_id}", dependencies=[Depends(require_roles('org_admin','staff'))])
def delete_adoption_request(
        request_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization)
):
    """Delete an adoption request (admin/staff only)."""
    request = session.get(AdoptionRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Adoption request not found.")
    ensure_animal_access(session, current_user, tenant_org, request.animal_id)

    session.delete(request)
    session.commit()
    return {"ok": True}
