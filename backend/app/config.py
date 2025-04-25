from typing import List, Optional
from pydantic_settings import BaseSettings
import os
from functools import lru_cache

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "FastAPI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_CONNECT_TIMEOUT: int = 10
    
    # SSL Certificate paths for database
    DB_SSL_CERT_PATH: Optional[str] = os.getenv("DB_SSL_CERT_PATH")
    DB_SSL_KEY_PATH: Optional[str] = os.getenv("DB_SSL_KEY_PATH")
    DB_SSL_ROOT_CERT_PATH: Optional[str] = os.getenv("DB_SSL_ROOT_CERT_PATH")
    
    # Environment settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    def is_development(self) -> bool:
        """Check if the environment is development"""
        return self.ENVIRONMENT.lower() == "development"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()

settings = get_settings() 