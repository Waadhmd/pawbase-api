from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

#create the database engine
engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
#SessionDep = Annotated[Session, Depends(get_session)]
def init_db():
    from app.schemas import models
    SQLModel.metadata.create_all(engine)
