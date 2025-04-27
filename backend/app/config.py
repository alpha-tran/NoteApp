from typing import List, Optional
from pydantic_settings import BaseSettings
import os
from functools import lru_cache
import secrets

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "FastAPI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")  # No default value
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Password settings
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    
    # CORS settings - Default to empty list, must be set in environment
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # Security headers
    SECURITY_HEADERS: bool = True
    HSTS_SECONDS: int = 31536000  # 1 year
    FRAME_DENY: bool = True
    XSS_PROTECTION: bool = True
    CONTENT_TYPE_NOSNIFF: bool = True
    
    # MongoDB settings with connection pool and timeout
    MONGODB_URI: str = os.getenv("MONGODB_URI")  # No default value
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME")  # No default value
    MONGODB_MAX_POOL_SIZE: int = int(os.getenv("MONGODB_MAX_POOL_SIZE", "100"))
    MONGODB_MIN_POOL_SIZE: int = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))
    MONGODB_MAX_IDLE_TIME_MS: int = int(os.getenv("MONGODB_MAX_IDLE_TIME_MS", "10000"))
    MONGODB_CONNECT_TIMEOUT_MS: int = int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", "2000"))
    
    # Session settings
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", secrets.token_urlsafe(32))
    SESSION_EXPIRE_MINUTES: int = int(os.getenv("SESSION_EXPIRE_MINUTES", "60"))
    
    # Environment settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # SSL/TLS settings
    SSL_KEYFILE: Optional[str] = os.getenv("SSL_KEYFILE")
    SSL_CERTFILE: Optional[str] = os.getenv("SSL_CERTFILE")
    FORCE_SSL: bool = os.getenv("FORCE_SSL", "False").lower() == "true"
    
    def is_development(self) -> bool:
        """Check if the environment is development"""
        return self.ENVIRONMENT.lower() == "development"
    
    def is_production(self) -> bool:
        """Check if the environment is production"""
        return self.ENVIRONMENT.lower() == "production"
    
    def validate_settings(self) -> None:
        """Validate all required settings"""
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY must be set")
            
        if not self.MONGODB_URI:
            raise ValueError("MONGODB_URI must be set")
            
        if not self.MONGODB_DB_NAME:
            raise ValueError("MONGODB_DB_NAME must be set")
            
        if self.is_production():
            if not self.BACKEND_CORS_ORIGINS:
                raise ValueError("BACKEND_CORS_ORIGINS must be set in production")
            if not self.SSL_KEYFILE or not self.SSL_CERTFILE:
                raise ValueError("SSL certificate and key must be set in production")
            if self.DEBUG:
                raise ValueError("DEBUG must be False in production")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance and validate
    """
    settings = Settings()
    settings.validate_settings()
    return settings

settings = get_settings() 