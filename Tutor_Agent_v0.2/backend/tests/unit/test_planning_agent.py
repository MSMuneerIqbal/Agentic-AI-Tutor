"""Unit tests for Planning Agent."""

import pytest

from app.agents.planning import PlanningAgent


def test_planning_agent_initialization():
    """Test Planning Agent initialization."""
    agent = PlanningAgent()
    
    assert agent.name == "Planning"
    assert agent.agent is not None


def test_get_style_adaptation():
    """Test learning style adaptation messages."""
    agent = PlanningAgent()
    
    # Visual style
    adaptation = agent._get_style_adaptation("V")
    assert "visual" in adaptation.lower()
    assert "diagrams" in adaptation.lower()
    
    # Auditory style
    adaptation = agent._get_style_adaptation("A")
    assert "discussions" in adaptation.lower()
    assert "audio" in adaptation.lower()
    
    # Reading style
    adaptation = agent._get_style_adaptation("R")
    assert "reading" in adaptation.lower()
    assert "written" in adaptation.lower()
    
    # Kinesthetic style
    adaptation = agent._get_style_adaptation("K")
    assert "hands-on" in adaptation.lower()
    assert "practical" in adaptation.lower()
    
    # Default case
    adaptation = agent._get_style_adaptation("X")
    assert "visual" in adaptation.lower()


def test_get_style_name():
    """Test learning style name retrieval."""
    agent = PlanningAgent()
    
    assert agent._get_style_name("V") == "Visual"
    assert agent._get_style_name("A") == "Auditory"
    assert agent._get_style_name("R") == "Reading/Writing"
    assert agent._get_style_name("K") == "Kinesthetic"
    assert agent._get_style_name("X") == "Visual"  # Default


def test_get_style_activities():
    """Test learning activities based on style and topic type."""
    agent = PlanningAgent()
    
    # Visual activities
    activities = agent._get_style_activities("V", "fundamentals")
    assert "concept maps" in activities[0].lower()
    assert "diagrams" in activities[2].lower()
    
    # Auditory activities
    activities = agent._get_style_activities("A", "applications")
    assert "discussions" in activities[1].lower()
    assert "verbal" in activities[2].lower()
    
    # Reading activities
    activities = agent._get_style_activities("R", "advanced")
    assert "research" in activities[0].lower()
    assert "written" in activities[2].lower()
    
    # Kinesthetic activities
    activities = agent._get_style_activities("K", "fundamentals")
    assert "hands-on" in activities[0].lower()
    assert "interactive" in activities[2].lower()


def test_create_plan_structure():
    """Test study plan structure creation."""
    agent = PlanningAgent()
    
    goals = "Learn Python programming"
    interests = "Web development and data analysis"
    time_commitment = "5 hours per week"
    
    plan_structure = agent._create_plan_structure("V", goals, interests, time_commitment)
    
    assert "summary" in plan_structure
    assert "topics" in plan_structure
    assert "learning_style" in plan_structure
    assert "total_hours" in plan_structure
    
    assert plan_structure["learning_style"] == "V"
    assert len(plan_structure["topics"]) == 3
    assert plan_structure["total_hours"] == 18  # 4 + 6 + 8
    
    # Check topic structure
    topic = plan_structure["topics"][0]
    assert "id" in topic
    assert "title" in topic
    assert "description" in topic
    assert "estimated_hours" in topic
    assert "activities" in topic
    assert "milestones" in topic


def test_format_plan_overview():
    """Test plan overview formatting."""
    agent = PlanningAgent()
    
    topics = [
        {
            "title": "Introduction",
            "estimated_hours": 4,
            "description": "Basic concepts"
        },
        {
            "title": "Advanced Topics",
            "estimated_hours": 6,
            "description": "Complex scenarios"
        }
    ]
    
    overview = agent._format_plan_overview(topics)
    
    assert "1. **Introduction** (4 hours)" in overview
    assert "2. **Advanced Topics** (6 hours)" in overview
    assert "Basic concepts" in overview
    assert "Complex scenarios" in overview


@pytest.mark.asyncio
async def test_planning_flow_goals():
    """Test planning flow - goals stage."""
    agent = PlanningAgent()
    
    context = {
        "user_id": "test-user",
        "session_id": "test-session",
        "planning_stage": "goals"
    }
    
    result = await agent._execute("", context)
    
    assert result["agent"] == "Planning"
    assert "learning goals" in result["message"].lower()
    assert result["action"] == "collect_goals"
    assert result["planning_stage"] == "interests"


@pytest.mark.asyncio
async def test_planning_flow_interests():
    """Test planning flow - interests stage."""
    agent = PlanningAgent()
    
    context = {
        "user_id": "test-user",
        "session_id": "test-session",
        "planning_stage": "interests",
        "goals": "Learn Python programming"
    }
    
    result = await agent._execute("", context)
    
    assert result["agent"] == "Planning"
    assert "interests" in result["message"].lower()
    assert result["action"] == "collect_interests"
    assert result["planning_stage"] == "time_commitment"
    assert result["goals"] == "Learn Python programming"


@pytest.mark.asyncio
async def test_planning_flow_time_commitment():
    """Test planning flow - time commitment stage."""
    agent = PlanningAgent()
    
    context = {
        "user_id": "test-user",
        "session_id": "test-session",
        "planning_stage": "time_commitment",
        "goals": "Learn Python programming",
        "interests": "Web development"
    }
    
    result = await agent._execute("", context)
    
    assert result["agent"] == "Planning"
    assert "time commitment" in result["message"].lower()
    assert result["action"] == "collect_time_commitment"
    assert result["planning_stage"] == "generate_plan"
    assert result["goals"] == "Learn Python programming"
    assert result["interests"] == "Web development"


@pytest.mark.asyncio
async def test_planning_flow_generate_plan():
    """Test planning flow - generate plan stage."""
    agent = PlanningAgent()
    
    context = {
        "user_id": "test-user",
        "session_id": "test-session",
        "planning_stage": "generate_plan",
        "goals": "Learn Python programming",
        "interests": "Web development"
    }
    
    result = await agent._execute("5 hours per week", context)
    
    assert result["agent"] == "Planning"
    assert "study plan is ready" in result["message"].lower()
    assert result["action"] == "plan_complete"
    assert result["next_state"] == "tutoring"
    assert "topics" in result
    assert "learning_style" in result


@pytest.mark.asyncio
async def test_planning_flow_default():
    """Test planning flow - default stage."""
    agent = PlanningAgent()
    
    context = {
        "user_id": "test-user",
        "session_id": "test-session",
        "planning_stage": "unknown"
    }
    
    result = await agent._execute("", context)
    
    assert result["agent"] == "Planning"
    assert "personalized study plan" in result["message"].lower()
    assert result["action"] == "start_planning"
    assert result["planning_stage"] == "goals"
