import logging
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from datetime import datetime
from bson import ObjectId

from app.database import get_mongo_db
from app.models.note import Note, NoteCreate, NoteUpdate, NoteInDB
from app.models.user import UserInDB
from app.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[Note])
async def get_notes(
    skip: int = 0,
    limit: int = 10,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Get list of notes for the current user with pagination.
    """
    notes = await db["notes"].find(
        {"owner_id": current_user.id}
    ).skip(skip).limit(limit).to_list(length=limit)
    return [Note(**note) for note in notes]

@router.post("/", response_model=Note, status_code=status.HTTP_201_CREATED)
async def create_note(
    note: NoteCreate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Create a new note for the current user.
    """
    note_in_db = NoteInDB(
        **note.model_dump(),
        owner_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    result = await db["notes"].insert_one(note_in_db.model_dump(by_alias=True))
    created_note = await db["notes"].find_one({"_id": result.inserted_id})
    
    if created_note is None:
        raise HTTPException(status_code=500, detail="Failed to create note")
    
    return Note(**created_note)

@router.get("/{note_id}", response_model=Note)
async def get_note(
    note_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Get a specific note by ID.
    Only accessible by the note owner.
    """
    try:
        note = await db["notes"].find_one({
            "_id": ObjectId(note_id),
            "owner_id": current_user.id
        })
        if note is None:
            raise HTTPException(status_code=404, detail="Note not found")
        return Note(**note)
    except Exception as e:
        logger.error(f"Error retrieving note {note_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid note ID format")

@router.put("/{note_id}", response_model=Note)
async def update_note(
    note_id: str,
    note_update: NoteUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Update a note.
    Only accessible by the note owner.
    """
    try:
        # Check if note exists and belongs to user
        existing_note = await db["notes"].find_one({
            "_id": ObjectId(note_id),
            "owner_id": current_user.id
        })
        if existing_note is None:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Update note
        update_data = note_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db["notes"].update_one(
            {"_id": ObjectId(note_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update note")
        
        updated_note = await db["notes"].find_one({"_id": ObjectId(note_id)})
        return Note(**updated_note)
    except Exception as e:
        logger.error(f"Error updating note {note_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid note ID format")

@router.delete("/{note_id}")
async def delete_note(
    note_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Delete a note.
    Only accessible by the note owner.
    """
    try:
        result = await db["notes"].delete_one({
            "_id": ObjectId(note_id),
            "owner_id": current_user.id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        
        return {"message": "Note deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting note {note_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid note ID format") 