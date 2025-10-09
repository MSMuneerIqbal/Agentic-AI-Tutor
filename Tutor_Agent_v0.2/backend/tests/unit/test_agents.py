"""Unit tests for agents."""

import pytest

from app.agents import AssessmentAgent, OrchestratorAgent, TutorAgent
from app.models import SessionState


@pytest.mark.asyncio
async def test_orchestrator_greeting():
    """Test orchestrator initial greeting."""
    orchestrator = OrchestratorAgent()

    context = {"state": SessionState.GREETING}
    response = await orchestrator.run("hello", context)

    assert response["agent"] == "Orchestrator"
    assert "Hello" in response["message"] or "welcome" in response["message"].lower()
    assert response["next_state"] == SessionState.ASSESSING


@pytest.mark.asyncio
async def test_orchestrator_routing():
    """Test orchestrator routing based on state."""
    orchestrator = OrchestratorAgent()

    # Test routing to assessment
    context = {"state": SessionState.ASSESSING}
    response = await orchestrator.run("ready", context)
    assert response["action"] == "handoff_to_assessment"

    # Test routing to tutor
    context = {"state": SessionState.TUTORING}
    response = await orchestrator.run("ready", context)
    assert response["action"] == "handoff_to_tutor"


@pytest.mark.asyncio
async def test_assessment_agent_first_question():
    """Test assessment agent asks first question."""
    assessment = AssessmentAgent()

    context = {"answers": []}
    response = await assessment.run("start", context)

    assert response["agent"] == "Assessment"
    assert "Question 1" in response["message"]
    assert response["action"] == "collect_answer"


@pytest.mark.asyncio
async def test_assessment_agent_completion():
    """Test assessment agent completes after minimum questions."""
    assessment = AssessmentAgent()

    # Simulate 5 answers
    answers = [
        {"question": 1, "answer": "a"},
        {"question": 2, "answer": "a"},
        {"question": 3, "answer": "a"},
        {"question": 4, "answer": "a"},
    ]
    context = {"answers": answers}

    response = await assessment.run("a", context)

    assert response["action"] == "assessment_complete"
    assert "learning_style" in response
    assert response["learning_style"] in ["V", "A", "R", "K"]


@pytest.mark.asyncio
async def test_tutor_agent_lesson_delivery():
    """Test tutor agent delivers lesson."""
    tutor = TutorAgent()

    context = {
        "topic": "Docker",
        "learning_style": "V",
        "progress": 0,
    }
    response = await tutor.run("teach me", context)

    assert response["agent"] == "Tutor"
    assert "Docker" in response["message"]
    assert response["action"] == "deliver_lesson"
    assert response["progress"] == 1


@pytest.mark.asyncio
async def test_tutor_agent_learning_style_adaptation():
    """Test tutor agent adapts to different learning styles."""
    tutor = TutorAgent()

    # Visual learner
    context_v = {"topic": "Kubernetes", "learning_style": "V", "progress": 0}
    response_v = await tutor.run("start", context_v)
    assert "🎨" in response_v["message"] or "Imagine" in response_v["message"]

    # Kinesthetic learner
    context_k = {"topic": "Kubernetes", "learning_style": "K", "progress": 0}
    response_k = await tutor.run("start", context_k)
    assert "🛠️" in response_k["message"] or "practice" in response_k["message"].lower()


@pytest.mark.asyncio
async def test_agent_input_validation():
    """Test agent input validation with guardrails."""
    orchestrator = OrchestratorAgent()

    # Test empty input rejection
    with pytest.raises(ValueError, match="Input validation failed"):
        await orchestrator.run("", {})

    # Test too long input rejection
    long_input = "x" * 6000
    with pytest.raises(ValueError, match="Input validation failed"):
        await orchestrator.run(long_input, {})


@pytest.mark.asyncio
async def test_orchestrator_handoffs():
    """Test orchestrator provides correct handoff targets."""
    orchestrator = OrchestratorAgent()

    handoffs = orchestrator.get_handoffs()

    assert len(handoffs) == 5
    handoff_targets = [h.target for h in handoffs]
    assert "Assessment" in handoff_targets
    assert "Planning" in handoff_targets
    assert "Tutor" in handoff_targets
    assert "Quiz" in handoff_targets
    assert "Feedback" in handoff_targets

