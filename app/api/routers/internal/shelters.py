from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.security import require_roles
from app.db.database import get_session
from app.core.deps import get_current_user, get_tenant_organization
from app.schemas.models import User, Shelter, Organization
from app.schemas.schema_shelter import ShelterCreate, ShelterRead, ShelterUpdate

router = APIRouter()

#Create new shelter (org_admin only)
@router.post("/", response_model=ShelterRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles('org_admin'))])
def create_shelter(
    shelter_in: ShelterCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    tenant_org: Organization = Depends(get_tenant_organization)
):
    #ensure organization exists or belongs to current user
    existing_shelter = session.exec(
        select(Shelter).where(Shelter.name == shelter_in.name)
    ).first()

    if existing_shelter:
        raise HTTPException(status_code=400, detail="Shelter with this name already exists.")

    shelter = Shelter(**shelter_in.model_dump())
    shelter.organization_id = tenant_org.id
    session.add(shelter)
    session.commit()
    session.refresh(shelter)
    return shelter

#get all shelters in org (org_admin, staff)
@router.get("/",
            response_model=List[ShelterRead],
            dependencies=[Depends(require_roles('org_admin','staff'))])
def read_shelters(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    tenant_org: Organization = Depends(get_tenant_organization)
):
    query = select(Shelter).where(Shelter.organization_id == tenant_org.id)
    #staff can only see their own shelter
    if current_user.role == 'staff':
        query = query.join(Shelter.staff_memberships).where(Shelter.staff_memberships.any(user_id= current_user.id))

    shelters = session.exec(query).all()
    return shelters


@router.get("/{shelter_id}", response_model=ShelterRead, dependencies=[Depends(require_roles('org_admin','staff'))])
def read_shelter(
    shelter_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    tenant_org: Organization = Depends(get_tenant_organization)
):
    shelter = session.get(Shelter, shelter_id)
    if not shelter or shelter.organization_id != tenant_org.id:
        raise HTTPException(status_code=404, detail="Shelter not found.")
    # If user is staff, ensure they belong to this shelter
    if current_user.role == 'staff':
        is_staff_member = any(member.user_id == current_user.id for member in shelter.staff_memberships)
        if not is_staff_member:
            raise HTTPException(status_code=403, detail="Access forbidden")

    return shelter


@router.patch("/{shelter_id}", response_model=ShelterRead, dependencies=[Depends(require_roles('org_admin'))])
def update_shelter(
    shelter_id: int,
    shelter_in: ShelterUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    tenant_org: Organization = Depends(get_tenant_organization)
):
    shelter_db = session.get(Shelter, shelter_id)
    if not shelter_db or shelter_db.organization_id != tenant_org.id:
        raise HTTPException(status_code=404, detail="Shelter not found.")

    update_data = shelter_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(shelter_db, key, value)

    session.add(shelter_db)
    session.commit()
    session.refresh(shelter_db)
    return shelter_db


@router.delete("/{shelter_id}", dependencies=[Depends(require_roles('org_admin'))])
def delete_shelter(
    shelter_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    tenant_org: Organization = Depends(get_tenant_organization)
):
    shelter = session.get(Shelter, shelter_id)
    if not shelter or shelter.organization_id != tenant_org.id:
        raise HTTPException(status_code=404, detail="Shelter not found.")

    session.delete(shelter)
    session.commit()
    return {"ok": True}
