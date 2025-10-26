from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.schemas.models import User
from app.db.database import  get_session
from app.schemas.schemas import UserCreate, UserRead, UserUpdate
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
        password_hash=get_password_hash(user_in.password),
        avatar_url=user_in.avatar_url
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

#read all users
@router.get("/",response_model=list[UserRead])
def get_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

#read single user by ID
@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id:int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    #if not verify_password(password, user.password_hash):
       # raise HTTPException(status_code=400, detail="Incorrect password")
    return user

#update user
@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id:int, user: UserUpdate, session: Session = Depends(get_session) ):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="user not found")

    user_data = user.model_dump(exclude_unset=True)
    if "password" in user_data:
        user_data["password_hash"] = get_password_hash(user_data.pop("password"))

    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user

#delete user
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id:int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    session.delete(user)
    session.commit()
    return {"ok": True}





