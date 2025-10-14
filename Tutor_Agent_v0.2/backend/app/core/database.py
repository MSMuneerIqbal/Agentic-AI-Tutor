"""Legacy database module - now using MongoDB."""

# This module is kept for compatibility but functionality has moved to MongoDB
# All database operations now use app.core.mongodb

class Base:
    """Legacy Base class for compatibility."""
    pass

def get_database():
    """Legacy function - returns None since we use MongoDB now."""
    return None

async def get_db():
    """Legacy function - MongoDB handles sessions automatically."""
    return None