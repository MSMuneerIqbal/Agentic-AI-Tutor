"""MongoDB connection and configuration."""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user_mongo import User
from app.core.session_store import Session
from app.core.config import get_settings

settings = get_settings()

# MongoDB connection string - direct connection to bypass DNS issues
MONGODB_URL = "mongodb://mustafaadeel989_db_user:xhuqP857lVk2kOlP@cluster0-shard-00-00.4nszshk.mongodb.net:27017,cluster0-shard-00-01.4nszshk.mongodb.net:27017,cluster0-shard-00-02.4nszshk.mongodb.net:27017/tutor_gpt?ssl=true&replicaSet=atlas-14c8dq-shard-0&authSource=admin&retryWrites=true&w=majority"

class MongoDB:
    """MongoDB connection manager."""
    
    client: AsyncIOMotorClient = None
    database = None

mongodb = MongoDB()

async def connect_to_mongo():
    """Create database connection with fallback methods."""
    
    # Try different connection methods
    connection_methods = [
        {
            "name": "Direct Connection",
            "url": "mongodb://mustafaadeel989_db_user:xhuqP857lVk2kOlP@cluster0-shard-00-00.4nszshk.mongodb.net:27017,cluster0-shard-00-01.4nszshk.mongodb.net:27017,cluster0-shard-00-02.4nszshk.mongodb.net:27017/tutor_gpt?ssl=true&replicaSet=atlas-14c8dq-shard-0&authSource=admin&retryWrites=true&w=majority"
        },
        {
            "name": "Simple SRV",
            "url": "mongodb+srv://mustafaadeel989_db_user:xhuqP857lVk2kOlP@cluster0.4nszshk.mongodb.net/tutor_gpt?retryWrites=true&w=majority"
        },
        {
            "name": "Alternative DNS",
            "url": "mongodb+srv://mustafaadeel989_db_user:xhuqP857lVk2kOlP@cluster0.4nszshk.mongodb.net/tutor_gpt?retryWrites=true&w=majority&serverSelectionTimeoutMS=30000"
        }
    ]
    
    for method in connection_methods:
        try:
            print(f"🔄 Trying {method['name']}...")
            print(f"📡 Using connection: {method['url'][:50]}...")
            
            # Create client with connection timeout
            mongodb.client = AsyncIOMotorClient(
                method['url'],
                serverSelectionTimeoutMS=15000,  # 15 seconds
                connectTimeoutMS=15000,          # 15 seconds
                socketTimeoutMS=15000,           # 15 seconds
            )
            mongodb.database = mongodb.client.tutor_gpt
            
            # Test connection with retry
            print("⏱️  Testing connection...")
            await mongodb.client.admin.command('ping')
            print("✅ MongoDB ping successful!")
            
            # Initialize Beanie with document models
            print("🔧 Initializing database models...")
            await init_beanie(
                database=mongodb.database,
                document_models=[User, Session]
            )
            
            print(f"✅ Connected to MongoDB successfully using {method['name']}!")
            return True
            
        except Exception as e:
            print(f"❌ {method['name']} failed: {str(e)[:100]}...")
            if mongodb.client:
                mongodb.client.close()
                mongodb.client = None
            continue
    
    print("💡 All connection methods failed. Troubleshooting:")
    print("   1. Check your internet connection")
    print("   2. Verify MongoDB Atlas cluster is running")
    print("   3. Try restarting your router")
    print("   4. Contact your network administrator about DNS issues")
    return False

async def close_mongo_connection():
    """Close database connection."""
    if mongodb.client:
        mongodb.client.close()
        print("✅ MongoDB connection closed.")

def get_database():
    """Get database instance."""
    return mongodb.database
