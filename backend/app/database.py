"""
Database configuration for MongoDB using Motor.
"""
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

logger = logging.getLogger(__name__)

class DataBase:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

db = DataBase()

async def connect_to_mongo():
    """
    Connects to the MongoDB database.
    """
    logger.info("Connecting to MongoDB...")
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URI)
        db.db = db.client[settings.MONGODB_DB_NAME]
        # Ping the server to verify connection
        await db.client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB database: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """
    Closes the MongoDB database connection.
    """
    if db.client:
        logger.info("Closing MongoDB connection...")
        db.client.close()
        logger.info("MongoDB connection closed.")

def get_mongo_db() -> AsyncIOMotorDatabase:
    """
    Returns the MongoDB database instance.
    Requires connect_to_mongo() to be called first.
    """
    if db.db is None:
        # This scenario should ideally not happen if connect_to_mongo is called at startup
        logger.error("Database not initialized. Call connect_to_mongo first.")
        raise RuntimeError("Database not initialized")
    return db.db

# Example Usage in routes (dependency):
# from app.database import get_mongo_db
# from motor.motor_asyncio import AsyncIOMotorDatabase
# 
# @router.get("/")
# async def read_items(db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
#     items = await db["your_collection"].find().to_list(100)
#     return items