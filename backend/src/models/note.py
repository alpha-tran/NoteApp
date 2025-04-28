from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .user import PydanticObjectId # Reuse ObjectId handler

class NoteBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: str

class NoteCreate(NoteBase):
    pass # Add any other fields needed on creation

class NoteInDBBase(NoteBase):
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    owner_id: PydanticObjectId # Store the owner's ObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda dt: dt.isoformat(), PydanticObjectId: str}
        populate_by_name = True

class Note(NoteInDBBase):
    # Fields to return to the client
    pass

class NoteInDB(NoteInDBBase):
    # Full object in DB
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    # updated_at will be set automatically in the update logic 