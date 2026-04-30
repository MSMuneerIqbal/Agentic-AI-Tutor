"""Unit tests for Assessment Agent."""

import pytest

from app.agents.assessment import AssessmentAgent


def test_assessment_agent_initialization():
    """Test Assessment Agent initialization."""
    agent = AssessmentAgent()
    
    assert agent.name == "Assessment"
    assert agent.questions_asked == 0
    assert agent.max_questions == 12
    assert agent.min_questions == 5
    assert len(agent.questions) == 8


def test_validate_answer():
    """Test answer validation."""
    agent = AssessmentAgent()
    
    # Valid single letter choices
    assert agent._validate_answer("a") == True
    assert agent._validate_answer("b") == True
    assert agent._validate_answer("c") == True
    assert agent._validate_answer("d") == True
    
    # Valid text responses
    assert agent._validate_answer("diagrams") == True
    assert agent._validate_answer("listening") == True
    assert agent._validate_answer("reading") == True
    assert agent._validate_answer("hands-on") == True
    
    # Invalid responses
    assert agent._validate_answer("invalid") == False
    assert agent._validate_answer("") == False
    assert agent._validate_answer("e") == False


def test_normalize_answer():
    """Test answer normalization."""
    agent = AssessmentAgent()
    
    # Direct letter choices
    assert agent._normalize_answer("a") == "a"
    assert agent._normalize_answer("b") == "b"
    assert agent._normalize_answer("c") == "c"
    assert agent._normalize_answer("d") == "d"
    
    # Visual keywords
    assert agent._normalize_answer("diagrams") == "a"
    assert agent._normalize_answer("visual aids") == "a"
    assert agent._normalize_answer("charts") == "a"
    
    # Auditory keywords
    assert agent._normalize_answer("listening") == "b"
    assert agent._normalize_answer("discussion") == "b"
    assert agent._normalize_answer("hearing") == "b"
    
    # Reading keywords
    assert agent._normalize_answer("reading") == "c"
    assert agent._normalize_answer("notes") == "c"
    assert agent._normalize_answer("written") == "c"
    
    # Kinesthetic keywords
    assert agent._normalize_answer("hands-on") == "d"
    assert agent._normalize_answer("practice") == "d"
    assert agent._normalize_answer("trying") == "d"
    
    # Default fallback
    assert agent._normalize_answer("unknown") == "a"


def test_analyze_answers():
    """Test answer analysis."""
    agent = AssessmentAgent()
    
    # Test with clear visual preference
    answers = [
        {"normalized_answer": "a"},
        {"normalized_answer": "a"},
        {"normalized_answer": "a"},
        {"normalized_answer": "b"},
        {"normalized_answer": "a"},
    ]
    
    style, confidence = agent._analyze_answers(answers)
    assert style == "V"
    assert confidence == 0.8  # 4 out of 5 answers
    
    # Test with mixed answers
    answers = [
        {"normalized_answer": "a"},
        {"normalized_answer": "b"},
        {"normalized_answer": "c"},
        {"normalized_answer": "d"},
    ]
    
    style, confidence = agent._analyze_answers(answers)
    assert style in ["V", "A", "R", "K"]
    assert confidence == 0.25  # 1 out of 4 answers
    
    # Test with empty answers
    style, confidence = agent._analyze_answers([])
    assert style == "V"
    assert confidence == 0.0


def test_calculate_confidence():
    """Test confidence calculation."""
    agent = AssessmentAgent()
    
    # High confidence
    answers = [
        {"normalized_answer": "a"},
        {"normalized_answer": "a"},
        {"normalized_answer": "a"},
    ]
    confidence = agent._calculate_confidence(answers)
    assert confidence == 1.0
    
    # Low confidence
    answers = [
        {"normalized_answer": "a"},
        {"normalized_answer": "b"},
        {"normalized_answer": "c"},
        {"normalized_answer": "d"},
    ]
    confidence = agent._calculate_confidence(answers)
    assert confidence == 0.25
    
    # Empty answers
    confidence = agent._calculate_confidence([])
    assert confidence == 0.0


def test_get_style_name():
    """Test style name retrieval."""
    agent = AssessmentAgent()
    
    assert agent._get_style_name("V") == "Visual"
    assert agent._get_style_name("A") == "Auditory"
    assert agent._get_style_name("R") == "Reading/Writing"
    assert agent._get_style_name("K") == "Kinesthetic"
    assert agent._get_style_name("X") == "Visual"  # Default


def test_get_style_description():
    """Test style description retrieval."""
    agent = AssessmentAgent()
    
    desc_v = agent._get_style_description("V")
    assert "Visual learner" in desc_v
    assert "diagrams" in desc_v
    
    desc_a = agent._get_style_description("A")
    assert "Auditory learner" in desc_a
    assert "listening" in desc_a
    
    desc_r = agent._get_style_description("R")
    assert "Reading/Writing learner" in desc_r
    assert "reading" in desc_r
    
    desc_k = agent._get_style_description("K")
    assert "Kinesthetic learner" in desc_k
    assert "hands-on" in desc_k


@pytest.mark.asyncio
async def test_assessment_flow():
    """Test complete assessment flow."""
    agent = AssessmentAgent()
    
    # First question
    result = await agent._execute("", {"answers": []})
    assert result["agent"] == "Assessment"
    assert "Question 1:" in result["message"]
    assert result["action"] == "collect_answer"
    assert result["question_number"] == 1
    
    # Answer first question
    result = await agent._execute("a", {"answers": []})
    assert result["agent"] == "Assessment"
    assert "Question 2:" in result["message"]
    assert result["action"] == "collect_answer"
    assert result["question_number"] == 2
    
    # Continue with more answers
    answers = [
        {"question_number": 1, "question": "test", "answer": "a", "normalized_answer": "a"},
        {"question_number": 2, "question": "test", "answer": "a", "normalized_answer": "a"},
        {"question_number": 3, "question": "test", "answer": "a", "normalized_answer": "a"},
        {"question_number": 4, "question": "test", "answer": "a", "normalized_answer": "a"},
    ]
    
    result = await agent._execute("a", {"answers": answers})
    assert result["agent"] == "Assessment"
    assert "Assessment complete!" in result["message"]
    assert result["action"] == "assessment_complete"
    assert result["learning_style"] == "V"
    assert "confidence" in result


@pytest.mark.asyncio
async def test_invalid_answer_handling():
    """Test handling of invalid answers."""
    agent = AssessmentAgent()
    
    # Start assessment
    result = await agent._execute("", {"answers": []})
    
    # Provide invalid answer
    result = await agent._execute("invalid answer", {"answers": []})
    assert result["agent"] == "Assessment"
    assert "Please choose one of the options" in result["message"]
    assert result["action"] == "collect_answer"
    assert "error" in result
