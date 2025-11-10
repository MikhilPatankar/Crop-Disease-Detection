from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import settings
from pymongo.errors import ConnectionFailure

db_client: AsyncIOMotorClient | None = None

async def get_db() -> AsyncIOMotorDatabase:
    """FastAPI dependency to get a MongoDB database instance."""
    if db_client is None:
        raise Exception("Database client not initialized.")
    return db_client[settings.MONGO_DB_NAME]


async def connect_to_mongo():
    """Connect to MongoDB and verify the connection."""
    global db_client
    print("Connecting to MongoDB...")
    try:
        db_client = AsyncIOMotorClient(settings.MONGO_URL, serverSelectionTimeoutMS=5000)
        await db_client.admin.command('ping')
        print("Connected to MongoDB successfully.")
    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        db_client = None
        raise 

async def close_mongo_connection():
    """Close MongoDB connection."""
    global db_client
    if db_client:
        print("Closing MongoDB connection...")
        db_client.close()
        print("MongoDB connection closed.")
