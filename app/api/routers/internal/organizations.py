from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from app.schemas.schema_organization import OrganizationCreate, OrganizationRead, OrganizationUpdate
from app.db.database import get_session
from app.core.deps import get_current_user
from app.schemas.models import User, Organization

router = APIRouter()
# TODO: Restrict this endpoint to admin users only

@router.post("/", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_organization(
        org_in: OrganizationCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    existing_org = session.exec(select(Organization).where(Organization.name == org_in.name)).first()
    if existing_org:
        raise HTTPException(
            status_code=400,
            detail="Organization already exist"
        )
    org = Organization(
        name = org_in.name,
        contact_email = org_in.contact_email,
        admin_id = org_in.admin_id
    )
    session.add(org)
    session.commit()
    session.refresh(org)
    return org

@router.get("/", response_model=List[OrganizationRead])
def read_organizations(
        session: Session = Depends(get_session),
         current_user: User = Depends(get_current_user)
):
    orgs = session.exec(select(Organization)).all()
    return orgs

@router.get("/{organization_id}", response_model=OrganizationRead)
def read_organization(
        organization_id:int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    org_db = session.get(Organization, organization_id)
    if not org_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org_db

@router.patch("/{organization_id}", response_model=OrganizationRead)
def update_organization(
        organization_id:int,
        org: OrganizationUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    org_db = session.get(Organization, organization_id)
    if not org_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    org_data = org.model_dump(exclude_unset=True)
    #for key, value in org_data.items():
    #setattr(org_db, key, value)
    org_db.sqlmodel_update(org_data)
    session.add(org_db)
    session.commit()
    session.refresh(org_db)
    return org_db

@router.delete("/{organization_id}")
def delete_organization(
        organization_id:int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    org_db = session.get(Organization, organization_id)
    if not org_db:
        raise HTTPException(status_code=404, detail="Organization not found")
    session.delete(org_db)
    session.commit()
    return {"ok": True}


