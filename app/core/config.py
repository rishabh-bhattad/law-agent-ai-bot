# app/core/config.py
from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    PROJECT_NAME: str = "Live Case-Law Briefing Bot"
    DEBUG: bool = False

    # LLM Provider & Tiers
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL_FAST: str | None = None
    LLM_MODEL_REASONING: str | None = None
    
    # API Keys
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = "" # No integration yet
    OPENAI_API_KEY: str = ""
    COURTLISTENER_API_KEY: str = ""
    REVENIUM_API_KEY: str = ""
    REVENIUM_KEY: str = ""
    
    # External API Base URLs
    COURTLISTENER_BASE_URL: str = "https://www.courtlistener.com/api/rest/v4"
    REVENIUM_BASE_URL: str = "https://api.revenium.ai/meter/v2/ai/completions"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def set_dynamic_models(self) -> "Settings":
        provider = (self.LLM_PROVIDER or "").lower()

        if provider == "openai":
            self.LLM_MODEL_FAST = "gpt-6-luna"
            self.LLM_MODEL_REASONING = "gpt-6.1-sol"
        elif provider == "gemini":
            self.LLM_MODEL_FAST = "gemini-3.5-flash-lite"
            self.LLM_MODEL_REASONING = "gemini-3.5-flash"

        return self

# Create a global settings instance to import across the app
@lru_cache
def get_settings() -> Settings:
    """Creates and caches the settings object."""
    return Settings()