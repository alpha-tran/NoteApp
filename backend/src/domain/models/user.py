from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId

class User(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

    def update_last_login(self):
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self):
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def make_superuser(self):
        self.is_superuser = True
        self.updated_at = datetime.utcnow()

    def revoke_superuser(self):
        self.is_superuser = False
        self.updated_at = datetime.utcnow() 