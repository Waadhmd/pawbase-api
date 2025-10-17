from fastapi import FastAPI

app = FastAPI(title="PawBase API",
              version="1.0.0",
              description="API for the PawBase animal shelter")


@app.get("/")
def read_root():
    return {"message":"Hello to PawBase API!"}
