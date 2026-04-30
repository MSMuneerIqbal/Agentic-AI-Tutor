"""Integration tests for Plan API endpoints."""

import pytest
import uuid
from datetime import datetime

from app.models.plan import Plan
from app.models.user import User


@pytest.mark.asyncio
async def test_get_user_plans_endpoint(test_client, test_db):
    """Test GET /api/v1/plans/{user_id} endpoint."""
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
        ],
    )
    test_db.add(plan2)
    await test_db.commit()
    
    # Test endpoint
    response = await test_client.get(f"/api/v1/plans/{user.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["plans"]) == 2
    # Should be ordered by created_at desc
    assert data["plans"][0]["summary"] == "Advanced Python Plan"
    assert data["plans"][1]["summary"] == "Python Basics Plan"
    
    # Check plan structure
    plan = data["plans"][0]
    assert "id" in plan
    assert "summary" in plan
    assert "topics" in plan
    assert "created_at" in plan
    assert "topic_count" in plan
    assert "total_hours" in plan


@pytest.mark.asyncio
async def test_get_latest_plan_endpoint(test_client, test_db):
    """Test GET /api/v1/plans/{user_id}/latest endpoint."""
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
    
    # Test endpoint
    response = await test_client.get(f"/api/v1/plans/{user.id}/latest")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["summary"] == "Second Plan"  # Should be the latest
    assert data["id"] == str(plan2.id)


@pytest.mark.asyncio
async def test_get_latest_plan_not_found(test_client):
    """Test GET /api/v1/plans/{user_id}/latest with no plans."""
    fake_user_id = str(uuid.uuid4())
    
    response = await test_client.get(f"/api/v1/plans/{fake_user_id}/latest")
    
    assert response.status_code == 404
    assert "No study plan found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_plan_by_id_endpoint(test_client, test_db):
    """Test GET /api/v1/plans/plan/{plan_id} endpoint."""
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
    
    # Test endpoint
    response = await test_client.get(f"/api/v1/plans/plan/{plan.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == str(plan.id)
    assert data["summary"] == "Test Plan"
    assert data["user_id"] == str(user.id)
    assert data["topic_count"] == 2
    assert data["total_hours"] == 5


@pytest.mark.asyncio
async def test_get_plan_by_id_not_found(test_client):
    """Test GET /api/v1/plans/plan/{plan_id} with non-existent plan."""
    fake_plan_id = str(uuid.uuid4())
    
    response = await test_client.get(f"/api/v1/plans/plan/{fake_plan_id}")
    
    assert response.status_code == 404
    assert "Plan not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_plan_progress_endpoint(test_client, test_db):
    """Test PUT /api/v1/plans/{plan_id}/progress endpoint."""
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
    
    # Test endpoint
    progress_data = {
        "topic_id": "topic_1",
        "progress_data": {
            "completed": True,
            "completion_date": "2025-10-09",
            "notes": "Completed successfully"
        }
    }
    
    response = await test_client.put(
        f"/api/v1/plans/{plan.id}/progress",
        json=progress_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Progress updated successfully"


@pytest.mark.asyncio
async def test_update_plan_progress_not_found(test_client):
    """Test PUT /api/v1/plans/{plan_id}/progress with non-existent plan."""
    fake_plan_id = str(uuid.uuid4())
    progress_data = {
        "topic_id": "topic_1",
        "progress_data": {"completed": True}
    }
    
    response = await test_client.put(
        f"/api/v1/plans/{fake_plan_id}/progress",
        json=progress_data
    )
    
    assert response.status_code == 404
    assert "Plan or topic not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_plan_statistics_endpoint(test_client, test_db):
    """Test GET /api/v1/plans/stats/overview endpoint."""
    # Create test users
    users = []
    for i in range(2):
        user = User(
            email=f"test{i}@example.com",
            display_name=f"Test User {i}",
        )
        test_db.add(user)
        users.append(user)
    await test_db.commit()
    
    # Create plans
    plan1 = Plan(
        user_id=users[0].id,
        summary="Plan 1",
        topics=[
            {"estimated_hours": 2},
            {"estimated_hours": 3}
        ],
    )
    test_db.add(plan1)
    
    plan2 = Plan(
        user_id=users[1].id,
        summary="Plan 2",
        topics=[
            {"estimated_hours": 4}
        ],
    )
    test_db.add(plan2)
    await test_db.commit()
    
    # Test endpoint
    response = await test_client.get("/api/v1/plans/stats/overview")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_plans"] == 2
    assert data["total_topics"] == 3
    assert data["total_hours"] == 9
    assert data["average_topics_per_plan"] == 1.5
    assert data["average_hours_per_plan"] == 4.5


@pytest.mark.asyncio
async def test_delete_plan_endpoint(test_client, test_db):
    """Test DELETE /api/v1/plans/{plan_id} endpoint."""
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
    
    # Test endpoint
    response = await test_client.delete(
        f"/api/v1/plans/{plan.id}",
        params={"user_id": str(user.id)}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Plan deleted successfully"


@pytest.mark.asyncio
async def test_delete_plan_not_found(test_client):
    """Test DELETE /api/v1/plans/{plan_id} with non-existent plan."""
    fake_plan_id = str(uuid.uuid4())
    fake_user_id = str(uuid.uuid4())
    
    response = await test_client.delete(
        f"/api/v1/plans/{fake_plan_id}",
        params={"user_id": fake_user_id}
    )
    
    assert response.status_code == 404
    assert "Plan not found or access denied" in response.json()["detail"]
