from pathlib import Path

from dotenv import load_dotenv


# ---------------------------------------------------------
# Load environment variables BEFORE importing application
# modules that use them.
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    PROJECT_ROOT / ".env"
)


from fastapi import FastAPI

from app.routers.git import router as git_router


app = FastAPI(
    title="Agentic Deployment Hub"
)

app.include_router(
    git_router
)


@app.get("/")
def root():
    return {
        "message": "Agentic Deployment Hub is running"
    }