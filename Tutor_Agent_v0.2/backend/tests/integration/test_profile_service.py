"""Integration tests for Profile Service."""

import pytest
import uuid
from datetime import datetime

from app.models.assessment import AssessmentResult, LearningStyle
from app.models.user import User
from app.services.profile_service import profile_service


@pytest.mark.asyncio
async def test_get_user_profile(test_db):
    """Test getting user profile."""
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
    await test_db.refresh(assessment)
    
    # Get profile
    profile = await profile_service.get_user_profile(str(user.id), test_db)
    
    assert profile["user_id"] == str(user.id)
    assert profile["email"] == "test@example.com"
    assert profile["display_name"] == "Test User"
    assert profile["learning_style"] == "V"
    assert profile["last_assessment"] is not None


@pytest.mark.asyncio
async def test_get_user_profile_no_assessment(test_db):
    """Test getting user profile without assessment."""
    # Create test user
    user = User(
        email="test2@example.com",
        display_name="Test User 2",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Get profile
    profile = await profile_service.get_user_profile(str(user.id), test_db)
    
    assert profile["user_id"] == str(user.id)
    assert profile["email"] == "test2@example.com"
    assert profile["learning_style"] is None
    assert profile["last_assessment"] is None


@pytest.mark.asyncio
async def test_get_latest_assessment(test_db):
    """Test getting latest assessment."""
    # Create test user
    user = User(
        email="test3@example.com",
        display_name="Test User 3",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Create multiple assessments
    assessment1 = AssessmentResult(
        user_id=user.id,
        style=LearningStyle.VISUAL,
        answers=[{"question": 1, "answer": "a"}],
    )
    test_db.add(assessment1)
    await test_db.commit()
    
    assessment2 = AssessmentResult(
        user_id=user.id,
        style=LearningStyle.AUDITORY,
        answers=[{"question": 1, "answer": "b"}],
    )
    test_db.add(assessment2)
    await test_db.commit()
    
    # Get latest assessment
    latest = await profile_service.get_latest_assessment(str(user.id), test_db)
    
    assert latest is not None
    assert latest["style"] == "A"  # Should be the latest (auditory)
    assert latest["id"] == str(assessment2.id)


@pytest.mark.asyncio
async def test_get_assessment_history(test_db):
    """Test getting assessment history."""
    # Create test user
    user = User(
        email="test4@example.com",
        display_name="Test User 4",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Create multiple assessments
    for i, style in enumerate([LearningStyle.VISUAL, LearningStyle.AUDITORY, LearningStyle.READING]):
        assessment = AssessmentResult(
            user_id=user.id,
            style=style,
            answers=[{"question": 1, "answer": "a"}],
        )
        test_db.add(assessment)
        await test_db.commit()
    
    # Get assessment history
    history = await profile_service.get_assessment_history(str(user.id), limit=5, db=test_db)
    
    assert len(history) == 3
    # Should be ordered by created_at desc
    assert history[0]["style"] == "R"  # Latest
    assert history[1]["style"] == "A"
    assert history[2]["style"] == "V"  # Oldest


@pytest.mark.asyncio
async def test_get_learning_style_stats(test_db):
    """Test getting learning style statistics."""
    # Create test users
    users = []
    for i in range(5):
        user = User(
            email=f"test{i}@example.com",
            display_name=f"Test User {i}",
        )
        test_db.add(user)
        users.append(user)
    await test_db.commit()
    
    # Create assessments with different styles
    styles = [LearningStyle.VISUAL, LearningStyle.VISUAL, LearningStyle.AUDITORY, 
              LearningStyle.READING, LearningStyle.KINESTHETIC]
    
    for user, style in zip(users, styles):
        assessment = AssessmentResult(
            user_id=user.id,
            style=style,
            answers=[{"question": 1, "answer": "a"}],
        )
        test_db.add(assessment)
    await test_db.commit()
    
    # Get stats
    stats = await profile_service.get_learning_style_stats(test_db)
    
    assert stats["total_assessments"] == 5
    assert stats["style_counts"]["V"] == 2
    assert stats["style_counts"]["A"] == 1
    assert stats["style_counts"]["R"] == 1
    assert stats["style_counts"]["K"] == 1
    assert stats["style_percentages"]["V"] == 40.0
    assert stats["most_common_style"] == "V"


@pytest.mark.asyncio
async def test_update_user_preferences(test_db):
    """Test updating user preferences."""
    # Create test user
    user = User(
        email="test5@example.com",
        display_name="Test User 5",
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
    await test_db.refresh(assessment)
    
    # Update preferences
    preferences = {
        "preferred_pace": "slow",
        "difficulty_level": "beginner",
        "study_time": "morning",
    }
    
    success = await profile_service.update_user_preferences(
        str(user.id), preferences, test_db
    )
    
    assert success == True
    
    # Verify preferences were saved
    latest = await profile_service.get_latest_assessment(str(user.id), test_db)
    assert "preferences" in latest["answers"]
    assert latest["answers"]["preferences"] == preferences
