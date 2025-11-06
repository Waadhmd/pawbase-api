
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import Session, select
from app.schemas.schema_animal import AnimalRead
from app.schemas.models import Animal
from app.core.deps import get_session


router = APIRouter()

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
