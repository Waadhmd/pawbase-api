from fastapi import APIRouter
from app.api.routers.internal import users as internal_users
#from app.api.v1.routers.public import animals as public_animals

api_v1_router = APIRouter()
api_v1_router.include_router(internal_users.router, prefix="/internal/users", tags=["Internal - Users"])
#api_v1_router.include_router(public_animals.router, prefix="/public/animals", tags=["Public - Animals"])