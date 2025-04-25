import os
from typing import Optional

class Settings:
    PROJECT_NAME: str = "NoteApp"
    PROJECT_VERSION: str = "1.0.0"
    
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Security Settings
    CORS_ORIGINS: list = ["http://localhost:3000"]
    
    @property
    def jwt_secret_key(self) -> str:
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY environment variable is not set")
        return self.JWT_SECRET_KEY

    def __post_init__(self):
        # Ensure critical environment variables are set
        if not self.POSTGRES_PASSWORD:
            raise ValueError("POSTGRES_PASSWORD environment variable must be set")
        if not self.POSTGRES_DB:
            raise ValueError("POSTGRES_DB environment variable must be set")

settings = Settings()