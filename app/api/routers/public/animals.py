from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import date
from sqlmodel import Session, select
from app.schemas.schema_animal import AnimalRead
from app.schemas.models import Animal, Vaccination, MedicalRecord
from app.core.deps import get_session
from app.schemas.schema_animal import AnimalPublicProfile


router = APIRouter()

def calculate_age(dob: Optional[date])-> Optional[dict]:
    if not dob:
        return None
    today = date.today()
    years = today.year - dob.year
    if years  == 0:
        months = today.month - dob.month
        return {"value": months, "unit": "months"}
    else:
        years =  years - ((today.month, today.day) < (dob.month, dob.day))
        return {"value":years, "unit": "years"}



@router.get('/', response_model=list[AnimalRead])
def list_public_animals(
        session: Session = Depends(get_session),
        breed: str | None = Query(None),
        name: str | None = Query(None),
        sterilized: bool | None = Query(None),
        skip: int = 0,
        limit: int = 10,
):
    """publicly accessible list of animals with search & pagination """
    query  = select(Animal).where(Animal.status == 'Available')
    if name:
        query = query.where(Animal.name.ilike(f"%{name}%"))
    elif breed:
        query = query.where(Animal.breed_name.ilike(f"%{breed}%"))
    elif sterilized:
        query = query.where(Animal.is_neutered == sterilized )
    query = query.offset(skip).limit(limit)
    return session.exec(query).all()

@router.get('/{animal_id}', response_model=AnimalPublicProfile)
def read_animal_profile(
        animal_id: int,
        session: Session = Depends(get_session)
):
    animal = session.get(Animal, animal_id)
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")
        # Load related data
    session.refresh(animal, attribute_names=["shelter", "medical_records", "vaccinations"])

    vaccinations_db = session.exec(select(Vaccination).where(Vaccination.animal_id == animal_id).order_by(Vaccination.vaccination_date.desc()).limit(5)).all()
    medicalrecords_db = session.exec(select(MedicalRecord).where(MedicalRecord.animal_id == animal_id).order_by(MedicalRecord.exam_date.desc()).limit(2)).all()
    age_info = calculate_age(animal.date_of_birth)

    return AnimalPublicProfile(
        id=animal.id,
        name=animal.name,
        breed_name=animal.breed_name,
        species_name= animal.species_name,
        shelter_id=animal.shelter_id,
        status= animal.status,
        date_of_birth= animal.date_of_birth,
        age= age_info,
        weight= animal.weight,
        is_neutered=animal.is_neutered,
        public_description=animal.public_description,
        created_at=animal.created_at,

        vaccinations= [
            {"vaccine_type": vaccination.vaccine_type,
             "vaccination_date": vaccination.vaccination_date,
             "valid_until": vaccination.valid_until
            }
            for vaccination in vaccinations_db
        ],
        medicalRecords = [
            {
                "exam_date": record.exam_date,
                "condition": record.condition,
                "vet_notes": record.vet_notes,

            }
            for record in medicalrecords_db
        ],
        shelter = {
            "name" : animal.shelter.name,
            "contact_email":animal.shelter.contact_email
        }


    )
