from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

#create the database engine
engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    from app.db import models
    SQLModel.metadata.create_all(engine)
