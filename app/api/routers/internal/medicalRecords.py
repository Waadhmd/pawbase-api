from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.database import get_session
from app.core.deps import get_current_user, get_tenant_organization
from app.core.security import require_roles
from app.schemas.models import User, MedicalRecord, Animal, Shelter, Staff, Organization
from app.core.deps import get_accessible_shelter_ids, ensure_animal_access
from app.schemas.schema_medicalRecord import MedicalRecordCreate, MedicalRecordRead, MedicalRecordUpdate

router = APIRouter()


# CREATE

@router.post("/", response_model=MedicalRecordRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_roles("org_admin", "staff"))],
)
def create_medical_record(
        record_in: MedicalRecordCreate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization),
):
    """Create a new medical record (staff/admin only)."""
    ensure_animal_access(session, current_user, tenant_org, record_in.animal_id)
    record = MedicalRecord(
        **record_in.model_dump(),
        staff_user_id = current_user.id
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


# READ ALL

@router.get("/", response_model=List[MedicalRecordRead],dependencies=[Depends(require_roles("org_admin", "staff"))],
)
def read_medical_records(session: Session = Depends(get_session), current_user: User = Depends(get_current_user),tenant_org: Organization = Depends(get_tenant_organization),
):
    """List all medical records accessible to the user."""
    accessible_shelters = get_accessible_shelter_ids(session, current_user, tenant_org)

    query = select(MedicalRecord).join(Animal).where(Animal.shelter_id.in_(accessible_shelters))
    return session.exec(query).all()

# READ ONE
@router.get(
"/{record_id}",
response_model=MedicalRecordRead,
dependencies=[Depends(require_roles("org_admin", "staff"))],
)
def read_medical_record(
        record_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization),
):
    """Get a single medical record."""
    record = session.get(MedicalRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    ensure_animal_access(session, current_user, tenant_org, record.animal_id)
    return record

# UPDATE
@router.patch(
"/{record_id}",
response_model=MedicalRecordRead,
dependencies=[Depends(require_roles("org_admin", "staff"))],
)
def update_medical_record(
        record_id: int,
        record_in: MedicalRecordUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization),
):
    """Update a medical record (staff/admin only)."""
    record_db = session.get(MedicalRecord, record_id)

    if not record_db:
        raise HTTPException(status_code=404, detail="Medical record not found")

    ensure_animal_access(session, current_user, tenant_org, record_db.animal_id)
    update_data = record_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record_db, key, value)
    session.add(record_db)
    session.commit()
    session.refresh(record_db)

    return record_db

# DELETE

@router.delete(
"/{record_id}",
dependencies=[Depends(require_roles("org_admin", "staff"))],
)
def delete_medical_record(
        record_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization),
):
    """Delete a medical record."""
    record = session.get(MedicalRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    ensure_animal_access(session, current_user, tenant_org, record.animal_id)
    session.delete(record)
    session.commit()
    return {"ok": True}
