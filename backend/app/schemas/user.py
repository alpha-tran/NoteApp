from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import PydanticObjectId # Import ObjectId handler

class UserCreate(BaseModel):
    # username: str # Removed as it's not in the current User model
    email: EmailStr
    password: str

class UserOut(BaseModel):
    # Use the PydanticObjectId Field from the model
    # It handles the alias and serialization automatically
    id: PydanticObjectId = Field(alias="_id")
    # username: str # Removed as it's not in the current User model
    email: EmailStr

    class Config:
        from_attributes = True # Pydantic v2+ equivalent of orm_mode
        populate_by_name = True # Allow using alias _id
        json_encoders = {PydanticObjectId: str} # Ensure _id is str in JSON output

# LoginCredentials can likely be removed as we use OAuth2PasswordRequestForm
# class LoginCredentials(BaseModel):
#     username: str # Keep in mind this is email for login
#     password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str