"""Authentication endpoints."""

import bcrypt
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.logging import get_logger
from app.core.metrics import get_metrics_collector
from app.models.user_mongo import User

logger = get_logger(__name__)
metrics = get_metrics_collector()

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    success: bool
    user: Dict[str, Any]
    message: str


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    try:
        existing = await User.find_one(User.email == request.email)
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")

        password_hash = bcrypt.hashpw(
            request.password.encode(), bcrypt.gensalt()
        ).decode()

        user = User(
            email=request.email,
            display_name=request.name,
            password_hash=password_hash,
            learning_style="Visual",
            progress=0,
            level="beginner",
        )
        await user.insert()
        metrics.increment_counter("user_registrations")

        return AuthResponse(
            success=True,
            user=user.to_dict(),
            message="User registered successfully",
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Registration error: {exc}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    try:
        user = await User.find_one(User.email == request.email)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user.password_hash:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not bcrypt.checkpw(request.password.encode(), user.password_hash.encode()):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        metrics.increment_counter("user_logins")

        return AuthResponse(
            success=True,
            user=user.to_dict(),
            message="Login successful",
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Login error: {exc}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/logout", response_model=Dict[str, Any])
async def logout():
    metrics.increment_counter("user_logouts")
    return {"success": True, "message": "Logged out successfully"}
