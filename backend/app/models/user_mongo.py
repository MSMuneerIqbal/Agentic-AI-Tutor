"""User model for MongoDB using Beanie."""

from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field, EmailStr

class User(Document):
    """User document model."""
    
    email: EmailStr = Field(..., unique=True, index=True)
    display_name: str = Field(..., min_length=2, max_length=100)
    password_hash: Optional[str] = None
    learning_style: str = Field(default="Visual")
    progress: int = Field(default=0, ge=0, le=100)
    level: str = Field(default="beginner")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "created_at",
            "is_active"
        ]
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for API responses."""
        # Convert learning style to single character
        style_map = {
            "Visual": "V",
            "Auditory": "A", 
            "Reading": "R",
            "Kinesthetic": "K"
        }
        
        return {
            "id": str(self.id),
            "name": self.display_name,
            "email": self.email,
            "learningStyle": style_map.get(self.learning_style, "V"),
            "progress": self.progress,
            "level": self.level
        }
