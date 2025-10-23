from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import init_db, engine
from app.api.api_router import api_router

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
