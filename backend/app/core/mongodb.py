"""MongoDB connection and Beanie initialisation."""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models.user_mongo import User
from app.core.session_store import Session
from app.core.config import get_settings

settings = get_settings()


class MongoDB:
    client: AsyncIOMotorClient = None
    database = None


mongodb = MongoDB()


async def connect_to_mongo() -> bool:
    """Connect to MongoDB using DATABASE_URL from environment."""
    url = settings.database_url
    if not url:
        print("❌ DATABASE_URL is not set. Add it to your .env file.")
        return False

    try:
        print("🔄 Connecting to MongoDB...")
        mongodb.client = AsyncIOMotorClient(
            url,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000,
        )

        # Extract database name from URL, default to tutor_lms
        db_name = url.rstrip("/").split("/")[-1].split("?")[0] or "tutor_lms"
        mongodb.database = mongodb.client[db_name]

        await mongodb.client.admin.command("ping")
        print("✅ MongoDB ping successful!")

        await init_beanie(database=mongodb.database, document_models=[User, Session])
        print("✅ Connected to MongoDB and initialised Beanie models.")
        return True

    except Exception as exc:
        print(f"❌ MongoDB connection failed: {exc}")
        if mongodb.client:
            mongodb.client.close()
            mongodb.client = None
        return False


async def close_mongo_connection() -> None:
    """Close the database connection."""
    if mongodb.client:
        mongodb.client.close()
        print("✅ MongoDB connection closed.")


def get_database():
    return mongodb.database
