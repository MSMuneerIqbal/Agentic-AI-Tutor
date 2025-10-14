"""Authentication endpoints."""

import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.mongodb import get_database
from app.core.logging import get_logger
from app.core.metrics import get_metrics_collector
from app.models.user_mongo import User

logger = get_logger(__name__)
metrics = get_metrics_collector()

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    """User registration request."""
    
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    """User login request."""
    
    email: str
    password: str


class AuthResponse(BaseModel):
    """Authentication response."""
    
    success: bool
    user: Dict[str, Any]
    message: str


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user."""
    try:
        # Check if user already exists
        existing_user = await User.find_one(User.email == request.email)
        
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create new user
        user = User(
            email=request.email,
            display_name=request.name,
            learning_style="Visual",
            progress=0,
            level="beginner"
        )
        
        await user.insert()
        metrics.increment_counter("user_registrations")
        
        return AuthResponse(
            success=True,
            user=user.to_dict(),
            message="User registered successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user."""
    try:
        user = await User.find_one(User.email == request.email)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # For now, we'll accept any password (in production, use proper password hashing)
        metrics.increment_counter("user_logins")
        
        return AuthResponse(
            success=True,
            user=user.to_dict(),
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/logout", response_model=Dict[str, Any])
async def logout():
    """Logout user."""
    metrics.increment_counter("user_logouts")
    
    return {
        "success": True,
        "message": "Logged out successfully"
    }
