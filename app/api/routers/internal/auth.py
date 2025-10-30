from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core.config import settings
from app.db.database import get_session
from app.schemas.models import User
from app.schemas.schema_user import UserRead
from app.schemas.schema_auth import Token
from app.core.security import verify_password
from app.core.jwt import create_access_token
from app.core.deps import get_current_user


router = APIRouter()

@router.post('/login', response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           session: Session = Depends(get_session)):
    """
    Login using form data (username=email, password). Returns JWT token.
     The docs will provide a login form because 0auth2PasswordBearer expects that
    """
    stmt = select(User).where(User.email == form_data.username)
    user = session.exec(stmt).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user.id, expires_delta=access_token_expires)
    return {"access_token":access_token, "token_type":"bearer"}

@router.get('/me', response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Return the current authenticated user
    """
    return current_user
