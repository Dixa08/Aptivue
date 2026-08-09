"""
models.py
---------
Pydantic models for Aptivue's backend.

Two families of models live here:

1. Candidate data models — mirror the shape of `data/candidates.json`
   (a single entry's "member" / "missions" / "signals" object). These
   describe the payload the frontend sends when it starts an interview.

2. API contract models — match `data/technical-spec.md` exactly.
   The spec defines a single endpoint, POST /api/interview, that accepts
   either a "start" payload (sessionId + candidate) or a "turn" payload
   (sessionId + message), and always returns {reply, done} with an
   optional "feedback" block once done=true.

Nothing here talks to storage or generates questions — that's
session_manager.py and interview_agent.py.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Candidate data models (mirrors data/candidates.json)
# ---------------------------------------------------------------------------

class CandidateMission(BaseModel):
    """One row from a candidate's mission history."""

    day: int
    title: str
    passed: Optional[bool] = None
    skipped: Optional[bool] = None
    attempts: Optional[int] = None


class CandidateSignals(BaseModel):
    """Aggregate behavioral signals used to steer question difficulty later."""

    commitDays: Optional[int] = None
    missionsCompleted: Optional[int] = None
    missionsFirstTry: Optional[int] = None


class CandidateMember(BaseModel):
    """Core identity/profile fields for a candidate."""

    id: str
    name: str
    jobRole: str
    yearsExperience: Optional[int] = None
    education: Optional[str] = None
    status: Optional[str] = None


class Candidate(BaseModel):
    """Full candidate object, matching one entry of candidates.json."""

    member: CandidateMember
    missions: List[CandidateMission] = Field(default_factory=list)
    signals: Optional[CandidateSignals] = None


# ---------------------------------------------------------------------------
# API contract models (mirrors data/technical-spec.md)
# ---------------------------------------------------------------------------

class InterviewRequest(BaseModel):
    """
    Single request model for POST /api/interview.

    The spec defines two shapes for this endpoint depending on whether the
    session already exists:

      - Start turn:      {"sessionId": "...", "candidate": {...}}
      - Conversation turn: {"sessionId": "...", "message": "..."}

    Both "candidate" and "message" are optional here so one model can
    accept either shape; main.py decides which branch to run based on
    whether the session already exists in memory and which field was sent.
    """

    sessionId: str
    candidate: Optional[Candidate] = None
    message: Optional[str] = None


class Feedback(BaseModel):
    """Final feedback block, required once done=true."""

    summary: str
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    next: List[str] = Field(default_factory=list)


class InterviewResponse(BaseModel):
    """Response model for POST /api/interview."""

    reply: str
    done: bool = False
    feedback: Optional[Feedback] = None


class HealthResponse(BaseModel):
    status: str = "ok"
