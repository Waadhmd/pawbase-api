from fastapi import Depends, HTTPException, status
from app.schemas.models import User
from pwdlib import PasswordHash

from app.core.deps import get_current_user

# Create a reusable password hasher using recommended settings (Argon2id)
password_hasher = PasswordHash.recommended()

def get_password_hash(password: str) -> str:
    """Return a securely hashed version of the given password."""
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a user's password by comparing it to the stored hash."""
    return password_hasher.verify(plain_password, hashed_password)

#add helper to require roles
def require_roles(*roles):
    def wrapper(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User role {current_user.role} not authorized for this operation")
        return current_user
    return wrapper