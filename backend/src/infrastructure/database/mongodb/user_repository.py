from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from ....domain.models.user import User
from ....domain.repositories.user_repository import UserRepository

class MongoDBUserRepository(UserRepository):
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.users

    async def create(self, user: User) -> User:
        user_dict = user.model_dump(by_alias=True)
        result = await self.collection.insert_one(user_dict)
        user.id = str(result.inserted_id)
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        user_dict = await self.collection.find_one({"_id": ObjectId(user_id)})
        return User(**user_dict) if user_dict else None

    async def get_by_email(self, email: str) -> Optional[User]:
        user_dict = await self.collection.find_one({"email": email})
        return User(**user_dict) if user_dict else None

    async def get_by_username(self, username: str) -> Optional[User]:
        user_dict = await self.collection.find_one({"username": username})
        return User(**user_dict) if user_dict else None

    async def update(self, user: User) -> User:
        user_dict = user.model_dump(by_alias=True)
        await self.collection.update_one(
            {"_id": ObjectId(user.id)},
            {"$set": user_dict}
        )
        return user

    async def delete(self, user_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        cursor = self.collection.find().skip(skip).limit(limit)
        users = []
        async for user_dict in cursor:
            users.append(User(**user_dict))
        return users

    async def count(self) -> int:
        return await self.collection.count_documents({}) 