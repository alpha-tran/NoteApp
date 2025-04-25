import os
from typing import List

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "NoteApp")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "1.0.0")

    # Database URL: use environment variable or fallback to SQLite for tests and development
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # JWT settings: fallback to default secret for development/testing
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "secret-test-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # CORS settings: comma-separated list
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

settings = Settings() 