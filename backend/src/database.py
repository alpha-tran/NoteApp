"""
Database configuration for MongoDB using Motor.
"""
import logging
import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
from contextlib import asynccontextmanager
from config import settings

logger = logging.getLogger(__name__)

class DataBase:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect_to_mongo(cls) -> None:
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
            # Ping the server to confirm connection
            await cls.client.admin.command('ping')
            cls.db = cls.client[settings.MONGODB_DATABASE]
            logger.info("Successfully connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            raise

    @classmethod
    async def close_mongo_connection(cls) -> None:
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None
            logger.info("MongoDB connection closed")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """
        Returns the MongoDB database instance.
        Requires connect_to_mongo() to be called first.
        
        Returns:
            AsyncIOMotorDatabase: The MongoDB database instance
            
        Raises:
            RuntimeError: If the database is not initialized
        """
        if cls.db is None:
            logger.error("Database not initialized. Call connect_to_mongo first.")
            raise RuntimeError("Database not initialized. Ensure connect_to_mongo() is called during application startup.")
        return cls.db

def get_mongo_db() -> AsyncIOMotorDatabase:
    """
    Dependency function to get MongoDB database instance.
    To be used with FastAPI Depends().
    
    Returns:
        AsyncIOMotorDatabase: The MongoDB database instance
    """
    return DataBase.get_db()

# Example Usage in routes (dependency):
# from database import get_mongo_db
# from motor.motor_asyncio import AsyncIOMotorDatabase
# 
# @router.get("/")
# async def read_items(db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
#     items = await db["your_collection"].find().to_list(100)
#     return items