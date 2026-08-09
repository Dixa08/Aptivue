"""
main.py
-------
FastAPI application entrypoint for Aptivue's backend foundation.

This step only wires up:
  - GET  /health          simple liveness check
  - POST /api/interview   the single endpoint defined in
                           data/technical-spec.md

No database, no auth, no vector store, no agent framework — just
in-memory session state (session_manager.py) and the evidence-driven
adaptive interview engine (interview_agent.py).

Run with:
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from interview_agent import interview_agent
from models import HealthResponse, InterviewRequest, InterviewResponse
from session_manager import session_manager

app = FastAPI(
    title="Aptivue Backend",
    description="Evidence-Driven Adaptive Technical Interview Agent — backend foundation",
    version="0.1.0",
)

# CORS: wide open for local hackathon development so the (not-yet-built)
# frontend can call this API from any dev server port. Tighten
# allow_origins before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Basic liveness check."""
    return HealthResponse(status="ok")


@app.post("/api/interview", response_model=InterviewResponse)
def interview(request: InterviewRequest) -> InterviewResponse:
    """
    Single endpoint driving the whole interview, per technical-spec.md.

    Branch logic:
      - If this sessionId has never been seen AND a "candidate" object was
        sent -> treat as the START of a new interview.
      - If this sessionId already exists AND a "message" was sent ->
        treat as a CONVERSATION TURN.
      - Anything else is a malformed request for the current session state.
    """
    session_exists = session_manager.exists(request.sessionId)

    # --- Start of a new interview -----------------------------------
    if not session_exists:
        if request.candidate is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "New sessionId requires a 'candidate' object to start "
                    "the interview."
                ),
            )

        session = session_manager.create_session(request.sessionId, request.candidate)
        reply = interview_agent.start_interview(session)
        session_manager.append_message(request.sessionId, "agent", reply)

        return InterviewResponse(reply=reply, done=False)

    # --- Conversation turn on an existing session ---------------------
    session = session_manager.get_session(request.sessionId)
    if session is not None and session["done"]:
        raise HTTPException(
            status_code=400,
            detail="This interview session has already been completed.",
        )

    if request.message is None:
        raise HTTPException(
            status_code=400,
            detail="Existing sessionId requires a 'message' field for each turn.",
        )

    session_manager.append_message(request.sessionId, "candidate", request.message)
    turn_count = session_manager.increment_turn(request.sessionId)

    reply, done, feedback = interview_agent.handle_turn(session, request.message, turn_count)
    session_manager.append_message(request.sessionId, "agent", reply)

    if done:
        session_manager.mark_done(request.sessionId)

    return InterviewResponse(reply=reply, done=done, feedback=feedback)
