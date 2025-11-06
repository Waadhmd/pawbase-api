from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Depends
from sqlmodel import Session, select
from app.schemas.models import Staff, User, Shelter, Organization
from app.schemas.schema_staff import StaffRead, StaffCreate, StaffUpdate
from app.core.security import require_roles
from app.core.deps import get_tenant_organization, get_current_user
from app.db.database import get_session

router = APIRouter()

@router.post(
"/",
response_model=StaffRead,
status_code=status.HTTP_201_CREATED,
dependencies=[Depends(require_roles("org_admin"))],
)
def create_staff(
staff_in: StaffCreate,
session: Session = Depends(get_session),
current_user: User = Depends(get_current_user),
tenant_org: Organization = Depends(get_tenant_organization),
):
    # Validate shelter belongs to the current org
    shelter = session.get(Shelter, staff_in.shelter_id)
    if not shelter or shelter.organization_id != tenant_org.id:
        raise HTTPException(status_code=400, detail="Invalid shelter for this organization")

    # Validate user exists and is a staff user
    user = session.get(User, staff_in.user_id)
    if not user or user.role != "staff":
        raise HTTPException(status_code=400, detail="User must exist and have role='staff'")

    # Prevent duplicate staff assignment
    existing = session.exec(
        select(Staff).where(Staff.user_id == user.id, Staff.shelter_id == shelter.id)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User is already assigned to this shelter")

    staff = Staff(user_id=user.id, shelter_id=shelter.id)
    session.add(staff)
    session.commit()
    session.refresh(staff)
    return staff

@router.get('/', response_model=list[StaffRead], dependencies =[ Depends(require_roles("org_admin","staff"))] )
def list_staff(session: Session = Depends(get_session),
               current_user: User = Depends(get_current_user),
               tenant_org: Organization = Depends(get_tenant_organization),
               ):
    #org_admin -> all staff in org
    query = select(Staff).join(Shelter).where(Shelter.organization_id == tenant_org.id)
    #staff -> the staff record(s) of the logged-in user, not all staff in that user’s shelter.
    if current_user.role == "staff":
        query = query.join(User).where(User.id == current_user.id)

    return session.exec(query).all()

@router.get('/{staff_id}', response_model=StaffRead, dependencies=[Depends(require_roles('org_admin','staff'))])
def read_staff(staff_id: int,
               session: Session = Depends(get_session),
               tenant_org: Organization = Depends(get_tenant_organization),
               current_user: User = Depends(get_current_user)
               ):
    staff = session.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    # check org ownership
    if staff.shelter.organization_id != tenant_org.id:
        raise HTTPException(status_code=403, detail="Access forbidden to this staff")
    #staff can only view themselves:
    if current_user.role == 'staff' and current_user.id != staff.user_id:
        raise HTTPException(status_code=403, detail="Access forbidden to this staff record")
    return staff

@router.post('/{staff_id}', response_model=StaffUpdate, dependencies=[Depends(require_roles('org_admin'))])
def update_staff(
        staff_id: int,
        staff_in: StaffUpdate,
        session: Session = Depends(get_session),
        tenant_org: Organization = Depends(get_tenant_organization),
        current_user: User = Depends(get_current_user)):
    staff_db = session.get(Staff, staff_id)
    if not staff_db:
        raise HTTPException(status_code=404, detail="Staff not found")
    if staff_in.shelter_id:
        new_shelter = session.get(Shelter, staff_in.shelter_id)
        if not new_shelter or new_shelter.organization_id != tenant_org.id:
            raise HTTPException(status_code=400, detail="Invalid shelter for this organization")
    staff_data = staff_in.model_dump(exclude_unset=True)
    staff_db.sqlmodel_update(staff_data)
    session.add(staff_db)
    session.commit()
    session.refresh(staff_db)
    return staff_db

@router.delete('/{staff_id}', dependencies=[Depends(require_roles('org_admin'))])
def delete_staff(
        staff_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization)
):
    staff_db = session.get(Staff, staff_id)
    if not staff_db:
        raise HTTPException(status_code=404, detail="Staff not found")
    if staff_db.shelter.organization_id != tenant_org.id:
        raise HTTPException(status_code=403, detail="Access forbidden to this staff record")

    session.delete(staff_db)
    session.commit()
    return {"ok":True}







