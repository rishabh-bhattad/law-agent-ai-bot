# app/main.py
from fastapi import FastAPI
from app.core.config import get_settings
from app.api.generate import router as generate_router

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Live case-law search and automated brief-generation API",
    version="0.1.0",
)

app.include_router(generate_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}