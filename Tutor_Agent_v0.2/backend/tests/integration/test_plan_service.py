"""Integration tests for Plan Service."""

import pytest
import uuid
from datetime import datetime

from app.models.plan import Plan
from app.models.user import User
from app.services.plan_service import plan_service


@pytest.mark.asyncio
async def test_get_user_plans(test_db):
    """Test getting user plans."""
    # Create test user
    user = User(
        email="test@example.com",
        display_name="Test User",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Create test plans
    plan1 = Plan(
        user_id=user.id,
        summary="Python Basics Plan",
        topics=[
            {"id": "topic_1", "title": "Variables", "estimated_hours": 2},
            {"id": "topic_2", "title": "Functions", "estimated_hours": 3},
        ],
    )
    test_db.add(plan1)
    await test_db.commit()
    
    plan2 = Plan(
        user_id=user.id,
        summary="Advanced Python Plan",
        topics=[
            {"id": "topic_3", "title": "Classes", "estimated_hours": 4},
            {"id": "topic_4", "title": "Modules", "estimated_hours": 3},
        ],
    )
    test_db.add(plan2)
    await test_db.commit()
    
    # Get plans
    plans = await plan_service.get_user_plans(str(user.id), limit=5, db=test_db)
    
    assert len(plans) == 2
    # Should be ordered by created_at desc
    assert plans[0]["summary"] == "Advanced Python Plan"
    assert plans[1]["summary"] == "Python Basics Plan"
    
    # Check plan structure
    plan = plans[0]
    assert "id" in plan
    assert "summary" in plan
    assert "topics" in plan
    assert "created_at" in plan
    assert "topic_count" in plan
    assert "total_hours" in plan
    assert plan["topic_count"] == 2
    assert plan["total_hours"] == 7


@pytest.mark.asyncio
async def test_get_latest_plan(test_db):
    """Test getting latest plan."""
    # Create test user
    user = User(
        email="test2@example.com",
        display_name="Test User 2",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Create multiple plans
    plan1 = Plan(
        user_id=user.id,
        summary="First Plan",
        topics=[{"id": "topic_1", "title": "Topic 1", "estimated_hours": 2}],
    )
    test_db.add(plan1)
    await test_db.commit()
    
    plan2 = Plan(
        user_id=user.id,
        summary="Second Plan",
        topics=[{"id": "topic_2", "title": "Topic 2", "estimated_hours": 3}],
    )
    test_db.add(plan2)
    await test_db.commit()
    
    # Get latest plan
    latest = await plan_service.get_latest_plan(str(user.id), test_db)
    
    assert latest is not None
    assert latest["summary"] == "Second Plan"  # Should be the latest
    assert latest["id"] == str(plan2.id)


@pytest.mark.asyncio
async def test_get_plan_by_id(test_db):
    """Test getting plan by ID."""
    # Create test user
    user = User(
        email="test3@example.com",
        display_name="Test User 3",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Create plan
    plan = Plan(
        user_id=user.id,
        summary="Test Plan",
        topics=[
            {"id": "topic_1", "title": "Topic 1", "estimated_hours": 2},
            {"id": "topic_2", "title": "Topic 2", "estimated_hours": 3},
        ],
    )
    test_db.add(plan)
    await test_db.commit()
    await test_db.refresh(plan)
    
    # Get plan by ID
    retrieved_plan = await plan_service.get_plan_by_id(str(plan.id), test_db)
    
    assert retrieved_plan is not None
    assert retrieved_plan["id"] == str(plan.id)
    assert retrieved_plan["summary"] == "Test Plan"
    assert retrieved_plan["user_id"] == str(user.id)
    assert retrieved_plan["topic_count"] == 2
    assert retrieved_plan["total_hours"] == 5


@pytest.mark.asyncio
async def test_update_plan_progress(test_db):
    """Test updating plan progress."""
    # Create test user
    user = User(
        email="test4@example.com",
        display_name="Test User 4",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Create plan
    plan = Plan(
        user_id=user.id,
        summary="Test Plan",
        topics=[
            {"id": "topic_1", "title": "Topic 1", "estimated_hours": 2},
            {"id": "topic_2", "title": "Topic 2", "estimated_hours": 3},
        ],
    )
    test_db.add(plan)
    await test_db.commit()
    await test_db.refresh(plan)
    
    # Update progress
    progress_data = {
        "completed": True,
        "completion_date": "2025-10-09",
        "notes": "Completed successfully"
    }
    
    success = await plan_service.update_plan_progress(
        str(plan.id), "topic_1", progress_data, test_db
    )
    
    assert success == True
    
    # Verify progress was updated
    updated_plan = await plan_service.get_plan_by_id(str(plan.id), test_db)
    topic = next(t for t in updated_plan["topics"] if t["id"] == "topic_1")
    assert topic["progress"] == progress_data


@pytest.mark.asyncio
async def test_get_plan_statistics(test_db):
    """Test getting plan statistics."""
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
    
    # Create plans with different structures
    plans_data = [
        {"topics": [{"estimated_hours": 2}, {"estimated_hours": 3}]},  # 5 hours, 2 topics
        {"topics": [{"estimated_hours": 4}]},  # 4 hours, 1 topic
        {"topics": [{"estimated_hours": 1}, {"estimated_hours": 2}, {"estimated_hours": 3}]},  # 6 hours, 3 topics
    ]
    
    for user, plan_data in zip(users, plans_data):
        plan = Plan(
            user_id=user.id,
            summary=f"Plan for {user.display_name}",
            topics=plan_data["topics"],
        )
        test_db.add(plan)
    await test_db.commit()
    
    # Get statistics
    stats = await plan_service.get_plan_statistics(test_db)
    
    assert stats["total_plans"] == 3
    assert stats["total_topics"] == 6  # 2 + 1 + 3
    assert stats["total_hours"] == 15  # 5 + 4 + 6
    assert stats["average_topics_per_plan"] == 2.0
    assert stats["average_hours_per_plan"] == 5.0


@pytest.mark.asyncio
async def test_delete_plan(test_db):
    """Test deleting a plan."""
    # Create test user
    user = User(
        email="test5@example.com",
        display_name="Test User 5",
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # Create plan
    plan = Plan(
        user_id=user.id,
        summary="Test Plan",
        topics=[{"id": "topic_1", "title": "Topic 1", "estimated_hours": 2}],
    )
    test_db.add(plan)
    await test_db.commit()
    await test_db.refresh(plan)
    
    # Delete plan
    success = await plan_service.delete_plan(str(plan.id), str(user.id), test_db)
    
    assert success == True
    
    # Verify plan was deleted
    deleted_plan = await plan_service.get_plan_by_id(str(plan.id), test_db)
    assert deleted_plan is None


@pytest.mark.asyncio
async def test_delete_plan_wrong_user(test_db):
    """Test deleting a plan with wrong user ID."""
    # Create test users
    user1 = User(
        email="test6@example.com",
        display_name="Test User 6",
    )
    user2 = User(
        email="test7@example.com",
        display_name="Test User 7",
    )
    test_db.add(user1)
    test_db.add(user2)
    await test_db.commit()
    await test_db.refresh(user1)
    await test_db.refresh(user2)
    
    # Create plan for user1
    plan = Plan(
        user_id=user1.id,
        summary="Test Plan",
        topics=[{"id": "topic_1", "title": "Topic 1", "estimated_hours": 2}],
    )
    test_db.add(plan)
    await test_db.commit()
    await test_db.refresh(plan)
    
    # Try to delete with user2's ID
    success = await plan_service.delete_plan(str(plan.id), str(user2.id), test_db)
    
    assert success == False  # Should fail due to authorization
