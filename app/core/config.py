# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Live Case-Law Briefing Bot"
    DEBUG: bool = False

    # LLM Provider
    LLM_PROVIDER: str
    
    # API Keys
    GEMINI_API_KEY: str
    ANTHROPIC_API_KEY: str
    OPENAI_API_KEY: str
    COURTLISTENER_API_KEY: str
    
    # CourtListener API Base URL
    COURTLISTENER_BASE_URL: str = "https://www.courtlistener.com/api/rest/v3"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Create a global settings instance to import across the app
settings = Settings()