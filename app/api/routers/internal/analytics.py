
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from sqlalchemy import func, case
from app.core.deps import get_session, get_current_user, get_tenant_organization
from app.core.security import require_roles
from app.schemas.models import AdoptionRequest, Animal, Shelter, Organization, User

router = APIRouter()


@router.get("/", dependencies=[Depends(require_roles('org_admin'))])
def get_basic_analytics(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        tenant_org: Organization = Depends(get_tenant_organization)
):
    """Return basic adoption analytics per shelter"""
    if current_user.role != 'org_admin':
        raise HTTPException(status_code=403, detail="unauthorized operation for non 'org_admin' role")

    # Adoption success rate per shelter
    adoption_success_query = (
        select(
            Shelter.name,
            func.count(AdoptionRequest.id).label("total_requests"),
            func.sum(
                case(
                    (AdoptionRequest.status == "Approved", 1),
                    else_=0
                )
            ).label("approved_requests"),
        ).where(Shelter.organization_id == tenant_org.id)
        .join(Animal, Animal.shelter_id == Shelter.id)
        .join(AdoptionRequest, AdoptionRequest.animal_id == Animal.id)
        .group_by(Shelter.id)
    )

    success_results = session.exec(adoption_success_query).all()
    success_rate_per_shelter = [
        {
            "shelter_name": s[0],
            "total_requests": s[1],
            "approved_requests": s[2],
            "success_rate": round((s[2] / s[1]) * 100, 2) if s[1] else 0
        }
        for s in success_results
    ]

    # Top 3 adopted breeds
    top_breeds_query = (
        select(Animal.breed_name, func.count(AdoptionRequest.id))
        .join(AdoptionRequest, AdoptionRequest.animal_id == Animal.id)
        .join(Shelter, Shelter.id == Animal.shelter_id)
        .where( Shelter.organization_id == tenant_org.id )
        .where(AdoptionRequest.status == "Approved")
        .group_by(Animal.breed_name)
        .order_by(func.count(AdoptionRequest.id).desc())
        .limit(3)
    )

    top_breeds = [
        {"breed": breed, "adopted_count": count}
        for breed, count in session.exec(top_breeds_query).all()
    ]

    return {
        "adoption_success_per_shelter": success_rate_per_shelter,
        "top_adopted_breeds": top_breeds
    }
