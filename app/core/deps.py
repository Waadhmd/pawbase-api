from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from typing import List
from sqlmodel import Session, select
from app.core.config import settings
from app.core.jwt import decode_access_token
from app.db.database import get_session
from app.schemas.models import User, Organization, Staff, Shelter, Animal
from app.schemas.schema_auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)

def get_current_user(token:str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    """
    Dependency that returns the current authenticated User SQLModel object .
    raises 401 if token invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW_Authenticate": "Bearer"}
    )
    try:
        payload = decode_access_token(token)
        sub = payload.get('sub')
        if sub is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(sub))
    except (JWTError, ValueError):
        raise credentials_exception

    user : User | None = session.get(User, token_data.user_id)
    if not user:
        raise credentials_exception
    return user

#filter tenant
def get_tenant_organization(current_user: User = Depends(get_current_user) ,
                            session: Session = Depends(get_session)) -> Organization:
    # Organization admin -> directly linked to org
    org = session.exec(select(Organization).where(Organization.admin_id == current_user.id)).first()
    if org:
        return org
    #staff user -> find org via shelter membership
    staff = session.exec(select(Staff).where(Staff.user_id == current_user.id)).first()
    if staff:
        shelter = session.exec(select(Shelter).where(Shelter.id == staff.shelter_id)).first()
        if shelter:
            return session.exec(select(Organization).where(Organization.id == shelter.organization_id)).first()

    raise HTTPException(status_code=403, detail="User not linked to any organization")

def get_accessible_shelter_ids(
session: Session,
current_user: User,
tenant_org: Organization,
) -> List[int]:
    """Return a list of shelter IDs accessible to the user."""
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

    raise HTTPException(status_code=403, detail="User not authorized")

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
