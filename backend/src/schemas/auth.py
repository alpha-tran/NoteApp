from pydantic import BaseModel, EmailStr, Field

from services.user_service import UserService

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class RegisterData(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str | None = None 