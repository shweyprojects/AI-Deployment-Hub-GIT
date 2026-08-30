from fastapi import FastAPI
from app.routers.git import router as git_router

app = FastAPI(title="Agentic Deployment Hub")

app.include_router(git_router)


@app.get("/")
def root():
    return {"message": "Agentic Deployment Hub is running"}