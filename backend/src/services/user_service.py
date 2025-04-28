from typing import Optional

from database import get_mongo_db
from schemas.user import UserCreate, UserResponse

class UserService:
    @staticmethod
    async def get_user_by_username(username: str) -> Optional[dict]:
        db = get_mongo_db()
        user = await db["users"].find_one({"username": username})
        return user

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[dict]:
        db = get_mongo_db()
        user = await db["users"].find_one({"email": email})
        return user

    @staticmethod
    async def create_user(user_data: dict) -> UserResponse:
        db = get_mongo_db()
        result = await db["users"].insert_one(user_data)
        created_user = await db["users"].find_one({"_id": result.inserted_id})
        return UserResponse(
            id=str(created_user["_id"]),
            username=created_user["username"],
            email=created_user["email"]
        ) 