# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.generate import router as generate_router
from app.core.telemetry import setup_telemetry

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Live case-law search and automated brief-generation API",
    version="0.1.0",
)

setup_telemetry(app=app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
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