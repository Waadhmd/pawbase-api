from fastapi import APIRouter
from app.api.routers.internal import users, organizations, shelters, animals, adoptionRequests, staff, vaccinations, medicalRecords,  auth as internal_auth
from app.api.routers.public import animals as public_animals

api_router = APIRouter()
api_router.include_router(users.router, prefix="/internal/users", tags=["Internal - Users"])
api_router.include_router(organizations.router, prefix="/internal/organizations", tags=["Internal - organization"])
api_router.include_router(shelters.router, prefix="/internal/shelters", tags=["internal-shelters"])
api_router.include_router(animals.router, prefix="/internals/animals", tags=["internal-animals"])
api_router.include_router(adoptionRequests.router, prefix="/internal/adoptionRequests", tags=["internal-adoptionRequest"])
api_router.include_router(staff.router, prefix="/internal/staff", tags=["internal-staff"])
api_router.include_router(vaccinations.router, prefix="/internal/vaccinations", tags=["internal-vaccination"])
api_router.include_router(medicalRecords.router, prefix="/internal/medicalRecords", tags=["internal-medicalRecord"])
api_router.include_router(internal_auth.router, prefix="/internal/auth", tags=["Internal - Auth"])

api_router.include_router(public_animals.router, prefix="/public/animals", tags=["Public - Animals"])