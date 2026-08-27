# app/main.py
from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Live case-law search and automated brief-generation API",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}