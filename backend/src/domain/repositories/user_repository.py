from abc import ABC, abstractmethod
from typing import Optional, List
from ..models.user import User
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import UserInDB, UserCreate
from security import get_password_hash

class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user"""
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete user"""
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all users with pagination"""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Get total number of users"""
        pass

class UserRepositoryImpl:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        user_dict = await self.collection.find_one({"email": email})
        if user_dict:
            return UserInDB(**user_dict)
        return None

    async def create_user(self, user: UserCreate) -> UserInDB:
        hashed_password = get_password_hash(user.password)
        user_dict = user.model_dump()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        
        result = await self.collection.insert_one(user_dict)
        user_dict["id"] = str(result.inserted_id)
        return UserInDB(**user_dict)

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        from bson import ObjectId
        user_dict = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_dict:
            user_dict["id"] = str(user_dict["_id"])
            return UserInDB(**user_dict)
        return None 