import logging
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List

from database import get_mongo_db
from models.user import User, UserInDB
from schemas.user import UserOut
from security import get_current_user, get_password_hash

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[UserOut])
async def get_users(
    skip: int = 0,
    limit: int = 10,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Get list of users with pagination.
    Only accessible by authenticated users.
    """
    users = await db["users"].find().skip(skip).limit(limit).to_list(length=limit)
    return [UserOut(**user) for user in users]

@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Get a specific user by ID.
    Only accessible by authenticated users.
    """
    from bson import ObjectId
    try:
        user = await db["users"].find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserOut(**user)
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid user ID format")

@router.put("/me", response_model=UserOut)
async def update_user_me(
    user_update: UserOut,
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Update current user's information.
    Only allows updating email.
    """
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "email" in update_data:
        # Check if email is already taken
        existing_user = await db["users"].find_one({"email": update_data["email"]})
        if existing_user and str(existing_user["_id"]) != str(current_user.id):
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
    
    # Update user in database
    result = await db["users"].update_one(
        {"_id": current_user.id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await db["users"].find_one({"_id": current_user.id})
    return UserOut(**updated_user)

@router.delete("/me")
async def delete_user_me(
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """
    Delete current user's account.
    This will also delete all user's notes.
    """
    # Delete user's notes first
    await db["notes"].delete_many({"owner_id": current_user.id})
    
    # Delete user
    result = await db["users"].delete_one({"_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"} 