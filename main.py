from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import init_db, engine
from app.api.api_router import api_router
from fastapi import  Depends, status
from sqlmodel import Session
from app.db.database import get_session
from sqlalchemy import text

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Starting PawBase API...")
    init_db()
    yield
    print("Shutting down PawBase API...")
    engine.dispose()


app = FastAPI(title="PawBase API",
              version="1.0.0",
              description="API for the PawBase animal shelter",
              lifespan=lifespan)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message":"Hello to PawBase API!"}


# 2. New, Dedicated Health Check Route (Use this for your demo screenshot!)
@app.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
def get_health_status(session: Session = Depends(get_session)):
    """
    Checks the status of the API and its primary dependencies (like the database).
    """
    try:
        # Attempt a simple query to verify database connection
        session.exec(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        # If the database query fails, the application is running but not ready
        db_status = "disconnected"

    return {
        "status": "active",
        "database": db_status,
        "version": app.version
    }
