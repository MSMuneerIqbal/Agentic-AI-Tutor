"""Integration tests for Profile API endpoints."""

import pytest
import uuid
from datetime import datetime

from app.models.assessment import AssessmentResult, LearningStyle
from app.models.user import User


@pytest.mark.asyncio
async def test_get_user_profile_endpoint(test_client, test_db):
    """Test GET /api/v1/profiles/{user_id} endpoint."""
    # Create test user
    user = User(
        email="test@example.com",
        display_name="Test User",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Create assessment result
    assessment = AssessmentResult(
        user_id=user.id,
        style=LearningStyle.VISUAL,
        answers=[
            {"question": 1, "answer": "a", "normalized_answer": "a"},
            {"question": 2, "answer": "a", "normalized_answer": "a"},
        ],
    )
    test_db.add(assessment)
    await test_db.commit()
    
    # Test endpoint
    response = await test_client.get(f"/api/v1/profiles/{user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["user_id"] == str(user.id)
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "Test User"
    assert data["learning_style"] == "V"
    assert data["last_assessment"] is not None


@pytest.mark.asyncio
async def test_get_user_profile_not_found(test_client):
    """Test GET /api/v1/profiles/{user_id} with non-existent user."""
    fake_user_id = str(uuid.uuid4())
    
    response = await test_client.get(f"/api/v1/profiles/{fake_user_id}")
    
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_assessment_history_endpoint(test_client, test_db):
    """Test GET /api/v1/profiles/{user_id}/assessments endpoint."""
    # Create test user
    user = User(
        email="test2@example.com",
        display_name="Test User 2",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Create multiple assessments
    for i, style in enumerate([LearningStyle.VISUAL, LearningStyle.AUDITORY]):
        assessment = AssessmentResult(
            user_id=user.id,
            style=style,
            answers=[{"question": 1, "answer": "a"}],
        )
        test_db.add(assessment)
        await test_db.commit()
    
    # Test endpoint
    response = await test_client.get(f"/api/v1/profiles/{user.id}/assessments")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["assessments"]) == 2
    # Should be ordered by created_at desc
    assert data["assessments"][0]["style"] == "A"  # Latest
    assert data["assessments"][1]["style"] == "V"  # Oldest


@pytest.mark.asyncio
async def test_get_learning_style_stats_endpoint(test_client, test_db):
    """Test GET /api/v1/profiles/stats/learning-styles endpoint."""
    # Create test users
    users = []
    for i in range(3):
        user = User(
            email=f"test{i}@example.com",
            display_name=f"Test User {i}",
        )
        test_db.add(user)
        users.append(user)
    await test_db.commit()
    
    # Create assessments with different styles
    styles = [LearningStyle.VISUAL, LearningStyle.VISUAL, LearningStyle.AUDITORY]
    
    for user, style in zip(users, styles):
        assessment = AssessmentResult(
            user_id=user.id,
            style=style,
            answers=[{"question": 1, "answer": "a"}],
        )
        test_db.add(assessment)
    await test_db.commit()
    
    # Test endpoint
    response = await test_client.get("/api/v1/profiles/stats/learning-styles")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_assessments"] == 3
    assert data["style_counts"]["V"] == 2
    assert data["style_counts"]["A"] == 1
    assert data["style_counts"]["R"] == 0
    assert data["style_counts"]["K"] == 0
    assert data["style_percentages"]["V"] == 66.7
    assert data["most_common_style"] == "V"


@pytest.mark.asyncio
async def test_update_user_preferences_endpoint(test_client, test_db):
    """Test PUT /api/v1/profiles/{user_id}/preferences endpoint."""
    # Create test user
    user = User(
        email="test3@example.com",
        display_name="Test User 3",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Create assessment
    assessment = AssessmentResult(
        user_id=user.id,
        style=LearningStyle.VISUAL,
        answers=[{"question": 1, "answer": "a"}],
    )
    test_db.add(assessment)
    await test_db.commit()
    
    # Test endpoint
    preferences = {
        "preferred_pace": "slow",
        "difficulty_level": "beginner",
        "study_time": "morning",
    }
    
    response = await test_client.put(
        f"/api/v1/profiles/{user.id}/preferences",
        json=preferences
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Preferences updated successfully"


@pytest.mark.asyncio
async def test_update_user_preferences_not_found(test_client):
    """Test PUT /api/v1/profiles/{user_id}/preferences with non-existent user."""
    fake_user_id = str(uuid.uuid4())
    preferences = {"preferred_pace": "slow"}
    
    response = await test_client.put(
        f"/api/v1/profiles/{fake_user_id}/preferences",
        json=preferences
    )
    
    assert response.status_code == 404
    assert "User or assessment not found" in response.json()["detail"]
