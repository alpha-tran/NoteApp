from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect_to_database(cls):
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            print("Connected to MongoDB!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise e

    @classmethod
    async def close_database_connection(cls):
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed.")

def get_database() -> Database:
    return Database

def get_user_repository():
    from domain.repositories.user_repository import UserRepository
    return UserRepository(Database.db)

__all__ = ["Database", "get_database", "get_user_repository"] 