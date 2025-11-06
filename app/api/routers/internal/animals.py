from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.database import get_session
from app.core.deps import get_current_user, get_tenant_organization
from app.schemas.models import User, Animal, Organization, Staff, Shelter
from app.core.security import require_roles
from app.core.deps import get_accessible_shelter_ids
from app.schemas.schema_animal import AnimalCreate, AnimalRead, AnimalUpdate

router = APIRouter()

"""def get_accessible_shelter_ids(
session: Session,
current_user: User,
tenant_org: Organization,
) -> List[int]:
    if current_user.role == "org_admin":
        result = session.exec(
            select(Shelter.id).where(Shelter.organization_id == tenant_org.id)
        ).all()
        return result

    elif current_user.role == "staff":
        staff = session.exec(select(Staff).where(Staff.user_id == current_user.id)).first()
        if not staff:
            raise HTTPException(status_code=403, detail="Staff not linked to any shelter")
        return [staff.shelter_id]

    raise HTTPException(status_code=403, detail="User not authorized")"""



@router.post("/", response_model=AnimalRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles('org_admin','staff'))])
def create_animal(
    animal_in: AnimalCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    tenant_org: Organization = Depends(get_tenant_organization)
):
    """Create a new animal entry (staff/admin only)."""
    accessible_shelters = get_accessible_shelter_ids(session, current_user, tenant_org)
    if animal_in.shelter_id not in accessible_shelters:
        raise HTTPException(status_code=403,detail="Cannot add animal to this shelter")

    animal = Animal(**animal_in.model_dump())
    session.add(animal)
    session.commit()
    session.refresh(animal)
    return animal


@router.get("/", response_model=List[AnimalRead], dependencies=[Depends(require_roles('org_admin','staff'))])
def read_animals(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    tenant_org: Organization = Depends(get_tenant_organization)
):
    """Return all animals (visible to authorized users)."""
    accessible_shelters = get_accessible_shelter_ids(session, current_user, tenant_org)
    query = select(Animal).where(Animal.shelter_id.in_(accessible_shelters))
    animals = session.exec(query).all()
    return animals



@router.get("/{animal_id}", response_model=AnimalRead, dependencies=[Depends(require_roles('org_admin','staff'))])
def read_animal(
    animal_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    tenant_org: Organization = Depends(get_tenant_organization)
):
    """Retrieve a single animal by ID."""
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found.")

    accessible_shelters = get_accessible_shelter_ids(session, current_user, tenant_org)
    if animal.shelter_id not in accessible_shelters:
        raise HTTPException(status_code=403, detail="Not authorized to view this animal")
    return animal


@router.patch("/{animal_id}", response_model=AnimalRead, dependencies=[Depends(require_roles('org_admin','staff'))])
def update_animal(
    animal_id: int,
    animal_in: AnimalUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    tenant_org: Organization = Depends(get_tenant_organization)
):
    """Update an animal's information (staff/admin only)."""
    animal_db = session.get(Animal, animal_id)
    if not animal_db:
        raise HTTPException(status_code=404, detail="Animal not found.")

    accessible_shelters = get_accessible_shelter_ids(session, current_user, tenant_org)
    if animal_db.shelter_id not in accessible_shelters:
        raise HTTPException(status_code=403, detail="Not authorized to edit this animal")

    update_data = animal_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(animal_db, key, value)

    session.add(animal_db)
    session.commit()
    session.refresh(animal_db)
    return animal_db


@router.delete("/{animal_id}", dependencies=[Depends(require_roles('org_admin','staff'))])
def delete_animal(
    animal_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    tenant_org: Organization = Depends(get_tenant_organization)
):
    """Delete an animal record (admin only)."""
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found.")
    accessible_shelters = get_accessible_shelter_ids(session, current_user, tenant_org)
    if animal.shelter_id not in accessible_shelters:
        raise HTTPException(status_code=403,  detail="Cannot delete outside your shelter/org")

    session.delete(animal)
    session.commit()
    return {"ok": True}
