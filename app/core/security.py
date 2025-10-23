from pwdlib import PasswordHash

# Create a reusable password hasher using recommended settings (Argon2id)
password_hasher = PasswordHash.recommended()

def get_password_hash(password: str) -> str:
    """Return a securely hashed version of the given password."""
    return password_hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a user's password by comparing it to the stored hash."""
    return password_hasher.verify(plain_password, hashed_password)
