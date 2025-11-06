from http.client import HTTPException

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from sqlmodel import Session, select

from app.core.security import require_roles
from app.db.database import get_session
from app.schemas.models import User, Organization,Vaccination, Animal
from app.core.deps import get_accessible_shelter_ids, get_current_user, get_tenant_organization
from app.schemas.schema_vaccination import VaccinationRead, VaccinationCreate, VaccinationUpdate

router = APIRouter()

def ensure_animal_access(
        session: Session,
        current_user: User,
        tenant_org: Organization,
        animal_id:int
)-> Animal:
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
    accessible_shelters = get_accessible_shelter_ids(session, current_user, tenant_org)
    if animal.shelter_id not in accessible_shelters:
        raise HTTPException(status_code=403, detail="Animal not in your shelter/org")
    return animal

@router.post('/', response_model=VaccinationRead,status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles('org_admin','staff'))] )
def create_vaccination(
        vaccination_in: VaccinationCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization)
):
    """Create a new vaccination record (staff/admin only)."""
    animal = ensure_animal_access(session, current_user, tenant_org, vaccination_in.animal_id)
    vaccination = Vaccination(
        **vaccination_in.model_dump(),
        staff_user_id = current_user.id
    )
    session.add(vaccination)
    session.commit()
    session.refresh(vaccination)
    return vaccination

@router.get('/', response_model=list[VaccinationRead], dependencies=[Depends(require_roles('org_admin','staff'))])
def list_vaccination(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization)
):
    """List vaccination records """
    accessible_shelters = get_accessible_shelter_ids(session, current_user, tenant_org)
    query = select(Vaccination).join(Animal).where(Animal.shelter_id.in_(accessible_shelters))
    return session.exec(query).all()

@router.get('/{vaccination_id}', response_model=VaccinationRead, dependencies=[Depends(require_roles('org_admin','staff'))])
def read_vaccination(
        vaccination_id: int,
        session: Session = Depends(get_session),
        current_suer: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization)
):
    """Read vaccination by ID"""
    vaccination = session.get(Vaccination, vaccination_id)
    if not vaccination:
        raise HTTPException(status_code=404, detail="vaccination not found")
    animal = ensure_animal_access(session, current_suer, tenant_org, vaccination.animal_id)
    return vaccination

@router.patch('/{vaccination_id}', response_model=VaccinationRead, dependencies=[Depends(require_roles('org_admin', 'staff'))],)
def update_vaccination(
        vaccination_id: int,
        vaccination_in: VaccinationUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization)
):
    """Update Vaccination by ID (org_Admin, staff)"""
    vaccination_db = session.get(Vaccination, vaccination_id)
    if not vaccination_db:
        raise HTTPException(status_code=404, detail="Vaccination not found")
    ensure_animal_access(session, current_user, tenant_org, vaccination_db.animal_id)
    vaccination_data = vaccination_in.model_dump(exclude_unset=True)
    for key, value in vaccination_data.items():
        setattr(vaccination_db,key, value)

    session.add(vaccination_db)
    session.commit()
    session.add(vaccination_db)
    return vaccination_db

@router.delete('/{vaccination_id', dependencies=[Depends(require_roles('org_admin','staff'))])
def delete_vaccination(
        vaccination_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization)
):
    """Delete Vaccination record by ID"""
    vaccination_db = session.get(Vaccination, vaccination_id)
    if not vaccination_db:
        raise HTTPException(status_code=404, detail="Vaccination not found")
    ensure_animal_access(session, current_user, tenant_org, vaccination_db.animal_id)

    session.delete(vaccination_db)
    session.commit()
    return {'ok': True}










