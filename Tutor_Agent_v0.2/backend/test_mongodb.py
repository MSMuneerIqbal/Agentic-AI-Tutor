#!/usr/bin/env python3
"""Test MongoDB connection."""

import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection string - direct connection to bypass DNS issues
MONGODB_URL = "mongodb://mustafaadeel989_db_user:xhuqP857lVk2kOlP@cluster0-shard-00-00.4nszshk.mongodb.net:27017,cluster0-shard-00-01.4nszshk.mongodb.net:27017,cluster0-shard-00-02.4nszshk.mongodb.net:27017/tutor_gpt?ssl=true&replicaSet=atlas-14c8dq-shard-0&authSource=admin&retryWrites=true&w=majority"

async def test_mongodb_connection():
    """Test MongoDB connection."""
    try:
        print("🔄 Testing MongoDB connection...")
        print(f"📡 URL: {MONGODB_URL[:50]}...")
        
        # Create client
        client = AsyncIOMotorClient(MONGODB_URL)
        
        # Test connection with timeout
        print("⏱️  Waiting for connection (max 10 seconds)...")
        await asyncio.wait_for(
            client.admin.command('ping'),
            timeout=10.0
        )
        
        print("✅ MongoDB connection successful!")
        
        # Test database access
        db = client.tutor_gpt
        collections = await db.list_collection_names()
        print(f"📊 Collections in tutor_gpt: {collections}")
        
        # Check storage usage
        stats = await db.command("dbStats")
        print(f"💾 Database size: {stats.get('dataSize', 0)} bytes")
        print(f"📁 Storage size: {stats.get('storageSize', 0)} bytes")
        
        client.close()
        return True
        
    except asyncio.TimeoutError:
        print("❌ Connection timeout - MongoDB Atlas cluster might be paused")
        print("💡 Go to MongoDB Atlas dashboard and resume your cluster")
        return False
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("💡 Check your internet connection and MongoDB Atlas cluster status")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_mongodb_connection())
    sys.exit(0 if result else 1)
