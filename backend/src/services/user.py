from typing import Optional
from database import get_mongo_db
from models.user import UserInDB
from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

async def get_user_by_email(email: str) -> Optional[UserInDB]:
    db = get_mongo_db()
    user_dict = await db["users"].find_one({"email": email})
    if user_dict:
        return UserInDB(**user_dict)
    return None

async def get_user_by_username(username: str) -> Optional[UserInDB]:
    db = get_mongo_db()
    user_dict = await db["users"].find_one({"username": username})
    if user_dict:
        return UserInDB(**user_dict)
    return None

async def create_user(user: UserInDB) -> UserInDB:
    db = get_mongo_db()
    # Create unique indexes if they don't exist
    await db["users"].create_index("email", unique=True)
    await db["users"].create_index("username", unique=True)
    
    user_dict = user.dict()
    try:
        result = await db["users"].insert_one(user_dict)
        user_dict["id"] = str(result.inserted_id)
        return UserInDB(**user_dict)
    except DuplicateKeyError as e:
        if "email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        elif "username" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        raise e 