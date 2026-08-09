"""
session_manager.py
-------------------
Minimal in-memory session store, keyed by sessionId.

For this foundation step we deliberately use a plain Python dict instead
of a database or Redis (per the hackathon step's constraints). This is
NOT persistent and will reset whenever the server restarts — that's fine
for a hackathon demo and easy to swap out later behind the same interface.

Each session tracks:
  - the candidate object supplied at interview start
  - a running transcript of the conversation (for future adaptive logic)
  - a turn counter (used by the placeholder agent to decide when to stop)
  - whether the interview has been marked "done"

If you later add a real database, only this file should need to change —
main.py and interview_agent.py talk to it through the methods below, not
through the dict directly.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

from models import Candidate


class SessionManager:
    """Thread-safe in-memory store for active interview sessions."""

    def __init__(self) -> None:
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def exists(self, session_id: str) -> bool:
        with self._lock:
            return session_id in self._sessions

    def create_session(self, session_id: str, candidate: Candidate) -> Dict[str, Any]:
        """Initialize a brand-new session for a first-time sessionId."""
        with self._lock:
            session = {
                "sessionId": session_id,
                "candidate": candidate,
                "turnCount": 0,
                "done": False,
                "transcript": [],  # list of {"role": "agent"|"candidate", "text": str}
            }
            self._sessions[session_id] = session
            return session

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._sessions.get(session_id)

    def append_message(self, session_id: str, role: str, text: str) -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is not None:
                session["transcript"].append({"role": role, "text": text})

    def increment_turn(self, session_id: str) -> int:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return 0
            session["turnCount"] += 1
            return session["turnCount"]

    def mark_done(self, session_id: str) -> None:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is not None:
                session["done"] = True

    def get_transcript(self, session_id: str) -> List[Dict[str, str]]:
        with self._lock:
            session = self._sessions.get(session_id)
            return list(session["transcript"]) if session else []


# Module-level singleton used by main.py. A single FastAPI process shares
# one in-memory store; this is sufficient for a hackathon demo.
session_manager = SessionManager()
