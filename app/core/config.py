from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL:str
    SECRET_KEY:str #change in production
    ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 60

    # tokenUrl used by OAuth2 docs UI; match the router you will use
    TOKEN_URL: str = "/api/internal/auth/login"

    class Config:
        env_file = ".env"

settings = Settings()