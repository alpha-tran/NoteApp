from typing import List, Optional, Dict, Literal, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, validator
import os
from functools import lru_cache
import secrets
import json
from typing import TypeVar, Type, cast

T = TypeVar('T')

def parse_json_env(key: str, default: T) -> T:
    """Parse JSON from environment variable with fallback to default value"""
    value = os.getenv(key)
    if not value:
        return default
    try:
        parsed = json.loads(value)
        if isinstance(parsed, type(default)):
            return cast(T, parsed)
        return default
    except json.JSONDecodeError:
        return default

class Settings(BaseSettings):
    # Project settings
    PROJECT_NAME: str = "NoteApp API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["development", "production", "testing"] = "development"
    
    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    WORKERS: int = 1
    USE_HTTPS: bool = False
    
    # Security settings
    SECRET_KEY: SecretStr = Field(default_factory=lambda: SecretStr(secrets.token_urlsafe(32)))
    JWT_SECRET_KEY: str = Field(...)  # Required field
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=5, le=60)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1, le=30)
    
    # Password settings
    PASSWORD_MIN_LENGTH: int = Field(default=12, ge=8)
    PASSWORD_MAX_LENGTH: int = Field(default=128, ge=64)
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: Dict[str, int] = Field(
        default_factory=lambda: parse_json_env(
            "RATE_LIMIT_PER_MINUTE",
            {"default": 100, "auth": 20, "user": 200}
        )
    )
    
    @property
    def RATE_LIMIT(self) -> int:
        """Alias for default rate limit used by middleware"""
        return self.RATE_LIMIT_PER_MINUTE.get("default", 100)
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: parse_json_env(
            "CORS_ORIGINS",
            ["http://localhost:3000"]
        )
    )
    
    # Security headers
    SECURITY_HEADERS: bool = True
    HSTS_SECONDS: int = 31536000  # 1 year
    FRAME_DENY: bool = True
    XSS_PROTECTION: bool = True
    CONTENT_TYPE_NOSNIFF: bool = True
    CSP_POLICY: str = "default-src 'self'; img-src 'self' data:; script-src 'self'"
    
    # MongoDB settings
    MONGODB_URI: str = Field(...)  # Required field
    MONGODB_DB_NAME: str = "noteapp"
    MONGODB_MAX_CONNECTIONS: int = Field(default=10, ge=1, le=100)
    MONGODB_MIN_CONNECTIONS: int = Field(default=1, ge=1, le=10)
    MONGODB_MAX_POOL_SIZE: int = 100
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_IDLE_TIME_MS: int = 10000
    MONGODB_CONNECT_TIMEOUT_MS: int = 2000
    
    # Session settings
    SESSION_SECRET_KEY: SecretStr = Field(default_factory=lambda: SecretStr(secrets.token_urlsafe(32)))
    SESSION_EXPIRE_MINUTES: int = Field(default=60, ge=15, le=240)
    SESSION_LIFETIME: int = Field(default=3600, ge=300, le=86400)  # 1 hour default, min 5 minutes, max 24 hours
    
    # Environment settings
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # SSL/TLS settings
    SSL_KEYFILE: Optional[str] = None
    SSL_CERTFILE: Optional[str] = None
    FORCE_SSL: bool = False
    
    @validator("MONGODB_URI")
    def validate_mongodb_uri(cls, v: str) -> str:
        if not v:
            raise ValueError("MONGODB_URI must be set")
        return v
    
    @validator("JWT_SECRET_KEY")
    def validate_jwt_secret(cls, v: str) -> str:
        if not v:
            raise ValueError("JWT_SECRET_KEY must be set")
        return v
    
    @validator("DEBUG", "SECURITY_HEADERS", "FORCE_SSL")
    def validate_production_settings(cls, v: bool, values: Dict) -> bool:
        if values.get("ENVIRONMENT") == "production":
            if values.get("DEBUG", False):
                raise ValueError("DEBUG must be False in production")
            if not values.get("SECURITY_HEADERS", True):
                raise ValueError("SECURITY_HEADERS must be True in production")
            if not values.get("FORCE_SSL", True):
                raise ValueError("FORCE_SSL must be True in production")
        return v
    
    @validator("RATE_LIMIT_PER_MINUTE")
    def validate_rate_limits(cls, v: Dict[str, int]) -> Dict[str, int]:
        required_keys = {"default", "auth", "user"}
        if not all(key in v for key in required_keys):
            raise ValueError(f"RATE_LIMIT_PER_MINUTE must contain all keys: {required_keys}")
        if not all(isinstance(value, int) and value > 0 for value in v.values()):
            raise ValueError("All rate limits must be positive integers")
        return v
    
    def is_development(self) -> bool:
        """Check if the environment is development"""
        return self.ENVIRONMENT.lower() == "development"
    
    def is_production(self) -> bool:
        """Check if the environment is production"""
        return self.ENVIRONMENT.lower() == "production"
    
    def is_testing(self) -> bool:
        """Check if the environment is testing"""
        return self.ENVIRONMENT.lower() == "testing"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        secrets_dir="/run/secrets" if os.path.exists("/run/secrets") else None
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

settings = get_settings() 