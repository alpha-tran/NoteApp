from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Any, Dict
from bson import ObjectId # Import ObjectId

# PydanticObjectId class to handle MongoDB ObjectId serialization/validation
class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if not isinstance(v, ObjectId):
            if ObjectId.is_valid(v):
                return ObjectId(v)
            raise ValueError("Invalid ObjectId")
        return v

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: Dict[str, Any], field_name: str) -> None:
        field_schema.update(type="string")
        
    # Thêm phương thức này để hỗ trợ OpenAPI schema
    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type="string")


class UserBase(BaseModel):
    # username: str = Field(..., index=True) # Assuming username is required
    email: EmailStr = Field(..., index=True) # Email is unique

class UserCreate(UserBase):
    password: str

class UserInDBBase(UserBase):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id") # Map MongoDB's _id
    hashed_password: str

    class Config:
        from_attributes = True # Replace orm_mode
        json_encoders = {ObjectId: str} # Serialize ObjectId to str
        populate_by_name = True # Allow using alias _id

class User(UserInDBBase):
    # Include fields to return to the client (exclude hashed_password)
    pass

class UserInDB(UserInDBBase):
    # Represents the full user object in the database
    pass

# Note: Relationships like 'notes' are handled differently in NoSQL.
# You might store note_ids in the user document or query notes separately.