"""Unit tests for AssessmentAgent pure-logic helpers."""

import pytest
from app.agents.assessment import AssessmentAgent


@pytest.fixture
def agent():
    return AssessmentAgent()


# ── _normalize ────────────────────────────────────────────────────────────────

def test_normalize_direct_letters(agent):
    assert agent._normalize("a") == "a"
    assert agent._normalize("b") == "b"
    assert agent._normalize("c") == "c"
    assert agent._normalize("d") == "d"


def test_normalize_uppercase(agent):
    assert agent._normalize("A") == "a"
    assert agent._normalize("D") == "d"


def test_normalize_visual_keywords(agent):
    assert agent._normalize("I prefer diagrams") == "a"
    assert agent._normalize("charts help me") == "a"


def test_normalize_auditory_keywords(agent):
    assert agent._normalize("I like to listen") == "b"
    assert agent._normalize("verbal explanations") == "b"


def test_normalize_reading_keywords(agent):
    assert agent._normalize("reading notes") == "c"
    assert agent._normalize("written instructions") == "c"


def test_normalize_kinesthetic_keywords(agent):
    assert agent._normalize("hands-on practice") == "d"
    assert agent._normalize("I learn by doing") == "d"


def test_normalize_unknown_returns_none(agent):
    assert agent._normalize("xyzzy") is None
    assert agent._normalize("") is None


# ── _confidence / _analyze ────────────────────────────────────────────────────

def _make_answers(choices: list[str]) -> list[dict]:
    return [{"normalized_answer": c} for c in choices]


def test_confidence_unanimous(agent):
    answers = _make_answers(["a", "a", "a", "a", "a"])
    assert agent._confidence(answers) == 1.0


def test_confidence_majority(agent):
    answers = _make_answers(["a", "a", "a", "b", "c"])
    conf = agent._confidence(answers)
    assert conf == pytest.approx(0.6)


def test_confidence_even_split(agent):
    answers = _make_answers(["a", "b", "c", "d"])
    conf = agent._confidence(answers)
    assert conf == pytest.approx(0.25)


def test_analyze_returns_correct_style(agent):
    answers = _make_answers(["b", "b", "b", "a"])
    style, _ = agent._analyze(answers)
    assert style == "A"


def test_analyze_maps_choices_to_styles(agent):
    mapping = {"a": "V", "b": "A", "c": "R", "d": "K"}
    for choice, expected_style in mapping.items():
        style, _ = agent._analyze(_make_answers([choice] * 5))
        assert style == expected_style
