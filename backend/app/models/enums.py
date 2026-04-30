"""Shared enumerations — no external dependencies."""

from enum import Enum


class SessionState(str, Enum):
    GREETING = "greeting"
    ASSESSING = "assessing"
    PLANNING = "planning"
    TUTORING = "tutoring"
    QUIZZING = "quizzing"
    DONE = "done"
