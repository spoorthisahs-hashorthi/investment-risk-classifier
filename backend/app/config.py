"""Application configuration and settings."""

import os
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    PROJECT_NAME: str = "Risk Classification of Online Investment Schemes"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "t")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000",
        ).split(",")
        if origin.strip()
    ]
    
    # Limits
    MAX_TEXT_LENGTH: int = int(os.getenv("MAX_TEXT_LENGTH", "20000"))
    MAX_URL_LENGTH: int = int(os.getenv("MAX_URL_LENGTH", "2048"))
    
    # Network Inspection / SSRF Limits
    NETWORK_INSPECTION_ENABLED: bool = os.getenv("NETWORK_INSPECTION_ENABLED", "true").lower() in ("true", "1", "t")
    NETWORK_TIMEOUT_SECONDS: float = float(os.getenv("NETWORK_TIMEOUT_SECONDS", "4.0"))
    MAX_REDIRECTS: int = int(os.getenv("MAX_REDIRECTS", "3"))
    MAX_RESPONSE_BYTES: int = int(os.getenv("MAX_RESPONSE_BYTES", str(256 * 1024)))  # 256 KB
    
    # Supabase / DB (Optional persistence)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")


settings = Settings()
