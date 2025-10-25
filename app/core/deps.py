from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from sqlmodel import Session, select
from app.core.config import settings
from app.core.jwt import decode_access_token
from app.db.database import get_session
from app.schemas.models import User
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

