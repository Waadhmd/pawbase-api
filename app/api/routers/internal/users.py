from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.schemas.models import User
from app.db.database import  get_session
from app.core.deps import get_current_user
from app.schemas.schema_user import UserCreate, UserRead, UserUpdate
from app.core.security import get_password_hash

router = APIRouter()
#create user signup
@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        password=get_password_hash(user_in.password),
        avatar_url=user_in.avatar_url
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

#read all users
@router.get("/",response_model=list[UserRead])
def get_users(
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """List all users (admin/staff only)."""
    # later: enforce admin-only
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admins only")
    users = session.exec(select(User)).all()
    return users

@router.get("/{user_id}", response_model=UserRead)
def get_user(
        user_id:int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """Get a user by ID"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

#update user
@router.patch("/{user_id}", response_model=UserRead)
def update_user(
        user_id:int,
        user: UserUpdate,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="user not found")

    user_data = user.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["password"] = get_password_hash(user_data.pop("password"))

    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db

#delete user
@router.delete("/{user_id}")
def delete_user(
        user_id:int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="user not found")

    session.delete(user_db)
    session.commit()
    return {"ok": True}





