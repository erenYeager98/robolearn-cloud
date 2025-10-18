# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Existing settings
    ALLOWED_ORIGINS: list[str] = ["*"]
    SERPER_API_KEY: str = "your_serper_api_key"
    
    # GCP settings
    GCP_PROJECT_ID: str
    GCP_REGION: str = "us-central1"
    GCS_BUCKET_NAME: str

    # New Google AI Gemini API Key
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()