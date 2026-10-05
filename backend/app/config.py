import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings:
    APP_NAME = os.getenv("APP_NAME", "Retail Fulfillment Failure Reason Classification")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "development-secret")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if origin.strip()]
    API_PREFIX = "/api/v1"


settings = Settings()
