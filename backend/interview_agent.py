"""
interview_agent.py
-------------------
Aptivue's evidence-driven adaptive interview engine.

Core idea: the next question is never picked from a fixed list. It's
chosen turn-by-turn from a small state machine driven by:

  - the candidate's job role, experience, and curriculum history
    (which missions they passed / failed / skipped, and how many
    attempts it took) — loaded from the request payload and cross
    referenced against data/curriculum.json's day -> topic mapping
  - a live classification of the candidate's most recent answer
    (weak / partial / strong / excellent)
  - which topics have already been covered in this session

Everything the model needs to reason about across turns (per-topic
scores, evidence snippets, what's been asked) lives in the *session
dict* that session_manager.py already keeps in memory — this file adds
new keys to that same dict rather than introducing new storage.

LLM usage is optional and isolated to three call sites (`_classify_llm`,
`_generate_question_llm`, `_generate_feedback_llm`), gated by the
ANTHROPIC_API_KEY environment variable. Without a key, deterministic
fallbacks (heuristic classifier + curated per-topic/difficulty question
bank + rule-based feedback) keep the interview fully functional offline.
No new pip dependency is introduced — the optional LLM call uses the
standard library's urllib.

Public interface consumed by main.py:
    interview_agent.start_interview(session: dict) -> str
    interview_agent.handle_turn(session: dict, message: str, turn_count: int)
        -> tuple[str, bool, Feedback | None]
"""

from __future__ import annotations
import random
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from models import Candidate, Feedback

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
LLM_MODEL = os.environ.get("INTERVIEW_LLM_MODEL", "claude-sonnet-4-6")
LLM_ENABLED = bool(ANTHROPIC_API_KEY)
ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
LLM_TIMEOUT_SECONDS = 20

MIN_QUESTIONS = 8      # spec minimum: at least 8 questions
MIN_TOPICS = 4         # spec minimum: at least 4 different curriculum days/topics
MAX_QUESTIONS = 12     # hard cap so the interview can't run forever

DIFFICULTY_ORDER = ["foundational", "applied", "advanced", "system_design"]
LEVEL_TO_SCORE = {"weak": 1, "partial": 2, "strong": 3, "excellent": 4}


# ---------------------------------------------------------------------------
# Curriculum loading — topic <-> curriculum day mapping
# ---------------------------------------------------------------------------

# Hand-mapped once from data/curriculum.json's module structure. The day
# *titles* are still pulled live from the file (see _load_curriculum_days)
# so prompts/reasoning always reflect the real curriculum content.
TOPIC_CURRICULUM_DAYS: Dict[str, List[int]] = {
    "embeddings": [7],
    "vector_databases": [8, 9],
    "retrieval": [10],
    "rag": [11],
    "prompt_engineering": [12, 13],
    "agents": [21, 22],
    "mcp": [23],
    "deployment": [28, 29, 30],
}

TOPIC_DISPLAY_NAMES: Dict[str, str] = {
    "embeddings": "Embeddings",
    "vector_databases": "Vector Databases",
    "retrieval": "Retrieval & Matching",
    "rag": "RAG (Retrieval-Augmented Generation)",
    "prompt_engineering": "Prompt Engineering",
    "agents": "Agentic AI / Multi-Agent Orchestration",
    "mcp": "Model Context Protocol (MCP)",
    "deployment": "Deployment & Production Readiness",
}

# Key terms used only by the offline heuristic classifier / fallback
# question bank — not exposed to the candidate.
TOPIC_KEY_TERMS: Dict[str, List[str]] = {
    "embeddings": ["vector", "embedding", "semantic", "cosine", "dimension", "similarity"],
    "vector_databases": ["index", "ann", "chroma", "pinecone", "hnsw", "vector database", "metadata filter"],
    "retrieval": ["retrieval", "query", "rank", "hybrid", "recall", "precision", "router"],
    "rag": ["rag", "grounding", "context window", "hallucinat", "prompt", "generation"],
    "prompt_engineering": ["prompt", "few-shot", "zero-shot", "chain-of-thought", "system prompt"],
    "agents": ["agent", "tool", "react", "orchestrat", "planner", "delegate"],
    "mcp": ["mcp", "model context protocol", "server", "client", "tool schema"],
    "deployment": ["docker", "kubernetes", "container", "scaling", "deploy", "monitoring", "latency"],
}

# Fallback question bank, used only when no LLM key is configured. One
# question per topic per difficulty tier — the *selection* of topic and
# difficulty is still fully adaptive; this is just the offline text source.
FALLBACK_QUESTIONS: Dict[str, Dict[str, List[str]]] = {
    "embeddings": {
        "foundational": [
            "In your own words, what does it mean to turn a piece of text into a vector embedding?",
            "What is a text embedding, and why is it useful for comparing pieces of text?",
            "Can you explain embeddings using a simple real-world example?",
        ],
        "applied": [
            "Suppose two documents use very different terminology but refer to the same concept. Why might embeddings help retrieve both?",
            "Imagine you are building semantic search for a college knowledge base. How would embeddings help?",
            "How would you use embeddings to find documents that are similar in meaning even when they don't share the same keywords?",
        ],
        "advanced": [
            "How would you choose an embedding model and similarity metric for a large, domain-specific corpus?",
            "What trade-offs exist when choosing embedding dimensionality for a production retrieval system?",
            "How would you evaluate whether one embedding model is better than another for your retrieval task?",
        ],
        "system_design": [
            "Design an embedding pipeline that re-embeds millions of documents when the model is upgraded. How would you avoid downtime?",
            "Design a scalable service that continuously creates embeddings for newly uploaded documents.",
            "How would you design an embedding pipeline that supports model versioning and re-indexing?",
        ],
    },

    "vector_databases": {
        "foundational": [
            "What role does a vector database play in a retrieval system, and how is it different from a normal database?",
            "Why would you use a vector database instead of a traditional relational database for semantic search?",
            "What is stored inside a vector database and how is it used during similarity search?",
        ],
        "applied": [
            "If you needed to filter search results by metadata such as date or category in addition to semantic similarity, how would you approach that?",
            "Suppose your vector search returns relevant documents from the wrong department. How could metadata filtering help?",
            "How would you combine vector similarity search with metadata filters in a real application?",
        ],
        "advanced": [
            "How would you decide between a local vector store and a managed vector database for production?",
            "What factors would you consider when choosing an indexing strategy for a large vector database?",
            "How would you balance search accuracy, latency, storage cost, and scalability in a vector database?",
        ],
        "system_design": [
            "Design a vector database strategy for a system with hundreds of millions of vectors and low-latency queries.",
            "How would you architect a highly available vector search system for millions of users?",
            "Design a scalable vector retrieval architecture that supports indexing, updates, filtering, and fast search.",
        ],
    },

    "retrieval": {
        "foundational": [
            "Walk me through what happens when a user query comes in and your system needs to retrieve relevant documents.",
            "What is the difference between retrieval and generation in an AI system?",
            "Can you explain how a semantic search system finds relevant documents for a user query?",
        ],
        "applied": [
            "When would you choose hybrid retrieval using keyword and semantic search over pure semantic search?",
            "Suppose semantic search misses exact product names. How would you improve the retrieval system?",
            "How would you improve retrieval when the system returns many irrelevant documents?",
        ],
        "advanced": [
            "How would you evaluate whether your retrieval system is actually returning the right documents at scale?",
            "What metrics would you use to evaluate a retrieval system and why?",
            "How would you diagnose a retrieval system with high recall but poor precision?",
        ],
        "system_design": [
            "Design a query router that decides between SQL lookup, vector search, and hybrid retrieval.",
            "Design a retrieval pipeline for a large enterprise document collection.",
            "How would you design a retrieval system that supports multiple document types and ranking strategies?",
        ],
    },

    "rag": {
        "foundational": [
            "What problem does RAG solve that a plain LLM call doesn't?",
            "Can you explain the basic flow of a Retrieval-Augmented Generation system?",
            "Why might an application use RAG instead of relying only on an LLM's trained knowledge?",
        ],
        "applied": [
            "If your RAG system starts hallucinating facts not present in the retrieved context, where would you start debugging?",
            "How would you improve a RAG system that retrieves relevant documents but still gives poor answers?",
            "What would you do if the retrieved documents contain conflicting information?",
        ],
        "advanced": [
            "How would you handle a case where the retrieved context is too large to fit in the model's context window?",
            "How would you evaluate the retrieval and generation components of a RAG system separately?",
            "What techniques could reduce hallucination in a production RAG system?",
        ],
        "system_design": [
            "Design an end-to-end RAG pipeline for a domain where answers must never contradict retrieved source documents.",
            "Design a production RAG system that supports millions of documents and frequent document updates.",
            "How would you design observability for a RAG system so you can diagnose retrieval failures and generation failures?",
        ],
    },

    "prompt_engineering": {
        "foundational": [
            "What's the difference between zero-shot and few-shot prompting, and when would you use each?",
            "What is prompt engineering and why does it matter when working with LLMs?",
            "What makes a prompt clear and effective for an LLM?",
        ],
        "applied": [
            "How would you systematically compare two candidate system prompts to decide which performs better?",
            "Suppose an LLM gives inconsistent answers to the same task. How could prompt engineering help?",
            "How would you improve a prompt that produces vague or incomplete answers?",
        ],
        "advanced": [
            "What failure modes can occur when prompts work well in testing but degrade in production?",
            "How would you evaluate prompt quality beyond simply looking at a few example outputs?",
            "How would you design an evaluation process for comparing different prompts?",
        ],
        "system_design": [
            "Design a process for versioning, testing, and safely rolling out system prompt changes in a live product.",
            "How would you build a prompt management system for a production AI application?",
            "Design a safe workflow for testing new prompts before deploying them to users.",
        ],
    },

    "agents": {
        "foundational": [
            "What's the difference between a simple function-calling LLM and an autonomous agent?",
            "What is an AI agent, and how is it different from a normal chatbot?",
            "What role do tools play in an AI agent?",
        ],
        "applied": [
            "How would you decide whether a task needs a single agent versus a multi-agent architecture?",
            "How would you design an agent that needs to choose between several tools?",
            "What would you do if an agent repeatedly chooses the wrong tool?",
        ],
        "advanced": [
            "What can go wrong when an agent selects the wrong tool, and how would you design the system to recover?",
            "How would you evaluate whether an agent is making reliable decisions?",
            "What techniques can prevent an agent from entering an endless reasoning or tool-use loop?",
        ],
        "system_design": [
            "Design a multi-agent system where a router agent delegates to domain specialists. How do you prevent runaway loops?",
            "Design a production AI agent that can safely call external tools.",
            "How would you design monitoring and guardrails for a multi-agent system?",
        ],
    },

    "mcp": {
        "foundational": [
            "In your own words, what problem does the Model Context Protocol solve?",
            "What is MCP and why might an AI application use it?",
            "How does MCP help an AI model interact with external tools or data?",
        ],
        "applied": [
            "How would you decide which capabilities of your system to expose as MCP tools?",
            "What types of functionality would you avoid exposing through an MCP server?",
            "How would you handle errors when an MCP tool fails?",
        ],
        "advanced": [
            "What security or reliability concerns arise when exposing internal tools through an MCP server?",
            "How would you authenticate and authorize MCP tool requests?",
            "How would you prevent an AI agent from misusing an MCP tool?",
        ],
        "system_design": [
            "Design an MCP server that exposes several tools with different risk levels.",
            "How would you structure authorization and error handling for a production MCP server?",
            "Design a secure MCP architecture for an enterprise AI application.",
        ],
    },

    "deployment": {
        "foundational": [
            "What are the basic steps to containerize a backend service for deployment?",
            "What is the purpose of a health-check endpoint in a deployed application?",
            "What is the difference between deploying an application and scaling an application?",
        ],
        "applied": [
            "How would you configure health checks so a load balancer can determine whether your service is actually healthy?",
            "How would you investigate a backend that works locally but fails after deployment?",
            "How would you handle an application that becomes slow when traffic increases?",
        ],
        "advanced": [
            "How would you roll out a breaking API change to a production service with zero downtime?",
            "How would you design monitoring for an API handling unpredictable traffic?",
            "What metrics would you monitor for a production AI service?",
        ],
        "system_design": [
            "Design the deployment and observability strategy for a service with unpredictable, spiky LLM-driven traffic.",
            "Design a highly available backend architecture for an AI application.",
            "How would you design CI/CD, monitoring, health checks, and rollback for a production AI service?",
        ],
    },
}

def _find_data_dir() -> Optional[Path]:
    """Best-effort discovery of the project's data/ directory."""
    candidates = []
    env_dir = os.environ.get("APTIVUE_DATA_DIR")
    if env_dir:
        candidates.append(Path(env_dir))
    here = Path(__file__).resolve().parent
    candidates.append(here.parent / "data")   # Aptivue/data (sibling of backend/)
    candidates.append(here / "data")          # backend/data
    candidates.append(Path.cwd() / "data")    # ./data relative to cwd
    for c in candidates:
        if (c / "curriculum.json").is_file():
            return c
    return None


def _load_curriculum_days() -> Dict[int, Dict[str, Any]]:
    """Load {day_number: {title, type, objectives}} from curriculum.json."""
    data_dir = _find_data_dir()
    if data_dir is None:
        return {}
    try:
        with open(data_dir / "curriculum.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
        return {d["day"]: d for d in raw.get("days", [])}
    except (OSError, json.JSONDecodeError, KeyError):
        return {}


CURRICULUM_DAYS = _load_curriculum_days()


def _day_title(day: int) -> str:
    entry = CURRICULUM_DAYS.get(day)
    return entry["title"] if entry else f"Day {day}"


def _topic_curriculum_label(topic: str) -> str:
    days = TOPIC_CURRICULUM_DAYS.get(topic, [])
    titles = [_day_title(d) for d in days]
    return "; ".join(titles) if titles else TOPIC_DISPLAY_NAMES.get(topic, topic)


# ---------------------------------------------------------------------------
# Candidate skill-state construction
# ---------------------------------------------------------------------------

def _mission_status_for_topic(candidate: Candidate, days: List[int]) -> str:
    """
    Classify the candidate's curriculum history for one topic into a status
    used for prioritization. Skipped topics are deliberately NOT treated as
    evidence of weakness — they're just lower-priority (no evidence either way).
    """
    relevant = [m for m in candidate.missions if m.day in days]
    if not relevant:
        return "not_covered"

    passed = [m for m in relevant if m.passed is True]
    failed = [m for m in relevant if m.passed is False]
    skipped = [m for m in relevant if m.skipped]

    if passed:
        max_attempts = max((m.attempts or 1) for m in passed)
        if max_attempts <= 1:
            return "completed_first_try"
        if max_attempts >= 4:
            return "completed_struggled"
        return "completed"
    if failed:
        return "failed"
    if skipped:
        return "skipped"
    return "not_covered"


CURRICULUM_STATUS_WEIGHT = {
    "completed_first_try": 3.0,
    "completed_struggled": 2.7,   # worth probing — passed, but it took effort
    "completed": 2.5,
    "failed": 2.2,                # attempted and evidence exists, worth exploring
    "skipped": 1.4,               # no evidence either way, deprioritized (not penalized)
    "not_covered": 1.0,
}


def _role_weight(job_role: str, topic: str) -> float:
    """Light-touch relevance boost based on the candidate's job role."""
    role = (job_role or "").lower()
    weight = 1.0
    if any(k in role for k in ("ai", "ml", "machine learning", "data scientist")):
        if topic in ("embeddings", "rag", "agents", "retrieval", "vector_databases"):
            weight += 0.6
    if any(k in role for k in ("devops", "platform", "infra", "site reliability", "sre")):
        if topic in ("deployment", "mcp"):
            weight += 0.7
    if any(k in role for k in ("data engineer", "data")):
        if topic in ("retrieval", "vector_databases", "rag"):
            weight += 0.5
    if any(k in role for k in ("backend", "software engineer", "architect")):
        if topic in ("retrieval", "agents", "deployment", "mcp"):
            weight += 0.4
    if any(k in role for k in ("analyst", "manager", "product")):
        # Non-engineering roles: keep it balanced, slight preference for
        # conceptual topics over deep systems topics.
        if topic in ("prompt_engineering", "rag", "embeddings"):
            weight += 0.3
    return weight


def _build_skill_state(candidate: Candidate) -> Dict[str, Dict[str, Any]]:
    skill_state: Dict[str, Dict[str, Any]] = {}
    for topic, days in TOPIC_CURRICULUM_DAYS.items():
        status = _mission_status_for_topic(candidate, days)
        skill_state[topic] = {
            "score": None,
            "evidence": [],
            "difficulty_reached": None,
            "curriculum_status": status,
            "curriculum_days": days,
            "times_asked": 0,
        }
    return skill_state


def _build_priority_order(candidate: Candidate, skill_state: Dict[str, Dict[str, Any]]) -> List[str]:
    def priority(topic: str) -> float:
        status = skill_state[topic]["curriculum_status"]
        return CURRICULUM_STATUS_WEIGHT[status] * _role_weight(candidate.member.jobRole, topic)

    topics = list(TOPIC_CURRICULUM_DAYS.keys())
    topics.sort(key=priority, reverse=True)
    return topics


# ---------------------------------------------------------------------------
# LLM plumbing (optional)
# ---------------------------------------------------------------------------

def _call_llm(system_prompt: str, user_prompt: str, max_tokens: int = 500) -> Optional[str]:
    """Call the Anthropic Messages API. Returns raw text, or None on any failure."""
    if not LLM_ENABLED:
        return None

    body = json.dumps({
        "model": LLM_MODEL,
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        ANTHROPIC_MESSAGES_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": ANTHROPIC_VERSION,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=LLM_TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        parts = [block.get("text", "") for block in payload.get("content", []) if block.get("type") == "text"]
        return "".join(parts).strip() or None
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, KeyError):
        return None


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Pull the first {...} JSON object out of an LLM response, tolerating stray text."""
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# Answer classification
# ---------------------------------------------------------------------------

def _heuristic_classify(answer: str, topic: str) -> Dict[str, Any]:
    text = (answer or "").strip().lower()
    word_count = len(text.split())

    give_up_phrases = ["i don't know", "not sure", "no idea", "dont know", "i'm not sure", "no clue"]
    if word_count < 4 or any(p in text for p in give_up_phrases):
        return {
            "level": "weak",
            "missing_concepts": TOPIC_KEY_TERMS.get(topic, [])[:2],
            "evidence_note": "Answer was very brief or indicated uncertainty about the core concept.",
        }

    key_terms = TOPIC_KEY_TERMS.get(topic, [])
    term_hits = sum(1 for t in key_terms if t in text)
    depth_markers = ["trade-off", "tradeoff", "because", "however", "for example",
                      "in practice", "latency", "scal", "fails when", "edge case", "alternative"]
    depth_hits = sum(1 for m in depth_markers if m in text)

    if term_hits == 0:
        level = "weak"
    elif term_hits >= 3 and depth_hits >= 2 and word_count > 40:
        level = "excellent"
    elif term_hits >= 2 and depth_hits >= 1:
        level = "strong"
    else:
        level = "partial"

    missing = [t for t in key_terms if t not in text][:2]
    return {
        "level": level,
        "missing_concepts": missing,
        "evidence_note": f"Answer referenced {term_hits} core term(s) and {depth_hits} reasoning/trade-off marker(s) for {TOPIC_DISPLAY_NAMES.get(topic, topic)}.",
    }


def _classify_llm(answer: str, topic: str, question: str, candidate: Candidate) -> Optional[Dict[str, Any]]:
    system = (
        "You are an expert technical interviewer evaluating one candidate answer during a live "
        "technical interview. Classify strictly and honestly. Respond ONLY with compact JSON, "
        "no prose, no markdown fences: "
        '{"level": "weak|partial|strong|excellent", "missing_concepts": ["..."], "evidence_note": "one short factual sentence"}. '
        "The evidence_note must be safe to show the candidate directly (no meta-commentary about grading)."
    )
    user = (
        f"Topic: {TOPIC_DISPLAY_NAMES.get(topic, topic)}\n"
        f"Candidate role: {candidate.member.jobRole} ({candidate.member.yearsExperience} yrs experience)\n"
        f"Question asked: {question}\n"
        f"Candidate answer: {answer}\n"
    )
    raw = _call_llm(system, user, max_tokens=300)
    parsed = _extract_json(raw) if raw else None
    if parsed and parsed.get("level") in LEVEL_TO_SCORE:
        return parsed
    return None


def classify_answer(answer: str, topic: str, question: str, candidate: Candidate) -> Dict[str, Any]:
    return _classify_llm(answer, topic, question, candidate) or _heuristic_classify(answer, topic)


# ---------------------------------------------------------------------------
# Next-topic / next-difficulty selection
# ---------------------------------------------------------------------------

def _next_difficulty(current_difficulty: Optional[str], level: str, topic_changed: bool) -> str:
    if topic_changed:
        # Fresh topic: start easy unless the candidate has been performing
        # very well overall, in which case start a notch higher.
        return "applied" if level in ("strong", "excellent") else "foundational"

    idx = DIFFICULTY_ORDER.index(current_difficulty) if current_difficulty in DIFFICULTY_ORDER else 0
    if level == "weak":
        return DIFFICULTY_ORDER[max(0, idx - 1)]
    if level == "partial":
        return current_difficulty or "foundational"
    if level == "strong":
        return DIFFICULTY_ORDER[min(len(DIFFICULTY_ORDER) - 1, idx + 1)]
    # excellent
    return "system_design"


def select_next_topic(session: Dict[str, Any], last_topic: str, last_level: str) -> Tuple[str, str, str]:
    """
    Decide the next (topic, difficulty, reason) given the classification of
    the answer just received. Returns a short, UI-safe reason string.
    """
    skill_state = session["skill_state"]
    priority_order: List[str] = session["topic_priority_order"]

    stay_on_topic = last_level in ("weak", "partial") and skill_state[last_topic]["times_asked"] < 2

    if stay_on_topic:
        next_topic = last_topic
        difficulty = _next_difficulty(session.get("current_difficulty"), last_level, topic_changed=False)
        verb = "probing the fundamentals again" if last_level == "weak" else "asking for clarification/depth"
        reason = (
            f"Candidate's answer on {TOPIC_DISPLAY_NAMES[last_topic]} was classified as {last_level}; "
            f"{verb} before moving on."
        )
        return next_topic, difficulty, reason

    # Move to a new topic: prefer the highest-priority topic that hasn't
    # been asked yet; if all have been touched, prefer the least-asked one.
    unexplored = [t for t in priority_order if skill_state[t]["times_asked"] == 0 and t != last_topic]
    if unexplored:
        next_topic = unexplored[0]
    else:
        remaining = [t for t in priority_order if t != last_topic]
        remaining.sort(key=lambda t: skill_state[t]["times_asked"])
        next_topic = remaining[0] if remaining else last_topic

    difficulty = _next_difficulty(session.get("current_difficulty"), last_level, topic_changed=True)
    status = skill_state[next_topic]["curriculum_status"]
    status_phrase = {
        "completed_first_try": "completed this on the first attempt",
        "completed": "completed this mission",
        "completed_struggled": "completed this after several attempts",
        "failed": "attempted but did not pass this mission",
        "skipped": "skipped this mission (no prior evidence)",
        "not_covered": "has no recorded history on this topic",
    }[status]
    perf_phrase = (
        f"the previous answer was {last_level}, so difficulty moved to {difficulty}"
        if last_level in ("strong", "excellent")
        else "moving to a new topic to broaden coverage"
    )
    reason = f"Selected {TOPIC_DISPLAY_NAMES[next_topic]} — candidate {status_phrase}; {perf_phrase}."
    return next_topic, difficulty, reason


# ---------------------------------------------------------------------------
# Question generation
# ---------------------------------------------------------------------------

def _recent_transcript_snippet(session: Dict[str, Any], max_turns: int = 4) -> str:
    transcript = session.get("transcript", [])
    recent = transcript[-max_turns:]
    lines = []
    for turn in recent:
        speaker = "Interviewer" if turn["role"] == "agent" else "Candidate"
        lines.append(f"{speaker}: {turn['text']}")
    return "\n".join(lines)


def _asked_questions(session: Dict[str, Any]) -> List[str]:
    """Return every interviewer question already used in this session."""
    asked = []

    # Explicit session-level tracking survives even if transcript formatting changes.
    for question in session.get("asked_questions", []):
        if question:
            asked.append(str(question).strip())

    # Also inspect transcript so older sessions remain compatible.
    for turn in session.get("transcript", []):
        if turn.get("role") != "agent":
            continue

        text = str(turn.get("text", "")).strip()
        if not text:
            continue

        # The opening message contains a welcome preamble followed by the question.
        if "\n\n" in text:
            text = text.split("\n\n", 1)[1].strip()

        if text and text not in asked:
            asked.append(text)

    return asked


def _normalise_question(text: str) -> str:
    """Normalise a question for duplicate detection."""
    return " ".join((text or "").strip().lower().split())


def _generate_question_llm(
    candidate: Candidate, topic: str, difficulty: str, session: Dict[str, Any]
) -> Optional[Dict[str, str]]:
    asked = _asked_questions(session)
    asked_block = "\n".join(f"- {q}" for q in asked[-12:]) or "(none yet)"

    system = (
        "You are Aptivue, an adaptive technical interviewer conducting a live, spoken-style "
        "technical interview. Ask exactly ONE question. The interview must feel adaptive and "
        "natural. Do not repeat any question already asked. Do not merely rephrase an already "
        "asked question. If the candidate performed weakly, probe a different aspect of the "
        "same topic; if they performed well, increase the depth or move to a related topic. "
        "Use the requested topic and difficulty as guidance. Never reveal scoring, grading, "
        "or internal reasoning. Respond ONLY with compact JSON, no markdown fences: "
        '{"question": "...", "reason": "one short sentence explaining why this question was chosen"}'
    )

    user = (
        f"Candidate: {candidate.member.name}, role: {candidate.member.jobRole}, "
        f"{candidate.member.yearsExperience} years experience.\n"
        f"Topic to ask about now: {TOPIC_DISPLAY_NAMES.get(topic, topic)} "
        f"(curriculum reference: {_topic_curriculum_label(topic)}).\n"
        f"Target difficulty: {difficulty}.\n"
        f"Candidate's curriculum status for this topic: "
        f"{session['skill_state'][topic]['curriculum_status']}.\n\n"
        f"Questions already asked — NEVER repeat or closely rephrase these:\n"
        f"{asked_block}\n\n"
        f"Recent conversation:\n{_recent_transcript_snippet(session, max_turns=6)}\n"
    )

    raw = _call_llm(system, user, max_tokens=400)
    parsed = _extract_json(raw) if raw else None

    if parsed and parsed.get("question"):
        question = str(parsed["question"]).strip()
        normalised = _normalise_question(question)

        # Reject an exact duplicate returned by Claude.
        if normalised and all(
            normalised != _normalise_question(previous)
            for previous in asked
        ):
            return {
                "question": question,
                "reason": str(parsed.get("reason", "")).strip(),
            }

    return None


def _generate_question_fallback(
    topic: str, difficulty: str, session: Dict[str, Any]
) -> Dict[str, str]:
    bank = FALLBACK_QUESTIONS.get(topic, {})

    questions = bank.get(difficulty) or bank.get("foundational") or [
        f"Tell me about your experience with "
        f"{TOPIC_DISPLAY_NAMES.get(topic, topic)}."
    ]

    asked = _asked_questions(session)
    asked_normalised = {_normalise_question(q) for q in asked}

    # First choose an unused question from the requested difficulty.
    unused = [
        q for q in questions
        if _normalise_question(q) not in asked_normalised
    ]

    if unused:
        question = random.choice(unused)
    else:
        # If that tier is exhausted, use any unused question for the topic.
        all_topic_questions = []
        for tier_questions in bank.values():
            all_topic_questions.extend(tier_questions)

        unused_topic = [
            q for q in all_topic_questions
            if _normalise_question(q) not in asked_normalised
        ]

        if unused_topic:
            question = random.choice(unused_topic)
        else:
            # Only reached if the complete bank for this topic is exhausted.
            # Still return a valid question rather than using a canned
            # "concrete example" question every time.
            question = random.choice(questions)

    return {"question": question, "reason": ""}


def generate_question(
    candidate: Candidate, topic: str, difficulty: str, session: Dict[str, Any]
) -> Dict[str, str]:
    """
    Generate one question while guaranteeing that exact questions are not
    repeated within the same interview session.
    """
    session.setdefault("asked_questions", [])

    result = _generate_question_llm(candidate, topic, difficulty, session)

    if result is None:
        result = _generate_question_fallback(topic, difficulty, session)

    # Final duplicate guard. If an LLM/fallback ever returns a duplicate,
    # choose an unused fallback question.
    asked_normalised = {
        _normalise_question(q) for q in session["asked_questions"]
    }

    if _normalise_question(result["question"]) in asked_normalised:
        result = _generate_question_fallback(topic, difficulty, session)

    session["asked_questions"].append(result["question"])

    return result


# ---------------------------------------------------------------------------
# Final feedback generation
# ---------------------------------------------------------------------------

def _skill_state_summary(skill_state: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    return {
        TOPIC_DISPLAY_NAMES[t]: {
            "score": s["score"],
            "evidence": s["evidence"],
            "curriculum_status": s["curriculum_status"],
            "times_asked": s["times_asked"],
        }
        for t, s in skill_state.items()
        if s["times_asked"] > 0
    }


def _generate_feedback_llm(session: Dict[str, Any]) -> Optional[Feedback]:
    candidate: Candidate = session["candidate"]
    system = (
        "You are generating final structured technical interview feedback based ONLY on the transcript "
        "and per-topic evidence provided. Be specific and evidence-based; do not invent facts not "
        "supported by the transcript. Respond ONLY with compact JSON, no markdown fences: "
        '{"summary": "...", "strengths": ["..."], "gaps": ["..."], "next": ["..."]}. '
        "strengths, gaps, and next should each be concise, actionable bullet points."
    )
    user = (
        f"Candidate: {candidate.member.name}, role: {candidate.member.jobRole}, "
        f"{candidate.member.yearsExperience} years experience.\n"
        f"Per-topic evidence:\n{json.dumps(_skill_state_summary(session['skill_state']), indent=2)}\n"
        f"Full transcript:\n{_recent_transcript_snippet(session, max_turns=100)}\n"
    )
    raw = _call_llm(system, user, max_tokens=700)
    parsed = _extract_json(raw) if raw else None
    if not parsed:
        return None
    try:
        return Feedback(
            summary=parsed.get("summary", ""),
            strengths=list(parsed.get("strengths", [])),
            gaps=list(parsed.get("gaps", [])),
            next=list(parsed.get("next", [])),
        )
    except (TypeError, ValueError):
        return None


def _generate_feedback_fallback(session: Dict[str, Any]) -> Feedback:
    candidate: Candidate = session["candidate"]
    skill_state = session["skill_state"]
    assessed = {t: s for t, s in skill_state.items() if s["times_asked"] > 0}

    strengths, gaps, next_steps = [], [], []
    for topic, s in assessed.items():
        name = TOPIC_DISPLAY_NAMES[topic]
        evidence = s["evidence"][-1] if s["evidence"] else ""
        if s["score"] is not None and s["score"] >= 3:
            strengths.append(f"Strong grasp of {name}. {evidence}".strip())
        elif s["score"] is not None:
            gaps.append(f"Needs reinforcement in {name}. {evidence}".strip())
            next_steps.append(f"Revisit {name} fundamentals and practice applying them to concrete scenarios.")

    if not strengths:
        strengths.append("Completed the interview and engaged with each question asked.")
    if not gaps:
        gaps.append("No significant gaps identified in the topics covered during this session.")
    if not next_steps:
        next_steps.append("Continue building depth in advanced/system-design scenarios for covered topics.")

    topics_covered = ", ".join(TOPIC_DISPLAY_NAMES[t] for t in assessed)
    scored = [s["score"] for s in assessed.values() if s["score"] is not None]
    avg_score = sum(scored) / max(1, len(scored))
    tier = "strong overall" if avg_score >= 3 else "mixed" if avg_score >= 2 else "developing"
    summary = (
        f"{candidate.member.name} answered {sum(s['times_asked'] for s in assessed.values())} "
        f"questions across {len(assessed)} topics ({topics_covered}). Overall performance was {tier} "
        f"relative to the {candidate.member.jobRole} role."
    )

    return Feedback(summary=summary, strengths=strengths, gaps=gaps, next=next_steps)


def generate_feedback(session: Dict[str, Any]) -> Feedback:
    return _generate_feedback_llm(session) or _generate_feedback_fallback(session)


# ---------------------------------------------------------------------------
# InterviewAgent
# ---------------------------------------------------------------------------

class InterviewAgent:
    """Evidence-driven adaptive interview orchestrator."""

    def start_interview(self, session: Dict[str, Any]) -> str:
        candidate: Candidate = session["candidate"]

        skill_state = _build_skill_state(candidate)
        priority_order = _build_priority_order(candidate, skill_state)
        session["skill_state"] = skill_state
        session["topic_priority_order"] = priority_order
        session["reasoning_log"] = []
        session["asked_questions"] = []

        first_topic = priority_order[0]
        opening_difficulty = "applied" if (candidate.member.yearsExperience or 0) >= 8 else "foundational"

        result = generate_question(candidate, first_topic, opening_difficulty, session)
        question_text = result["question"]

        session["current_topic"] = first_topic
        session["current_difficulty"] = opening_difficulty
        skill_state[first_topic]["times_asked"] += 1
        skill_state[first_topic]["difficulty_reached"] = opening_difficulty

        status = skill_state[first_topic]["curriculum_status"]
        session["reasoning_log"].append({
            "topic": first_topic,
            "curriculum_day": TOPIC_CURRICULUM_DAYS[first_topic][0],
            "reason": result.get("reason") or (
                f"Opening topic — highest priority based on candidate's curriculum status "
                f"({status}) and role ({candidate.member.jobRole})."
            ),
            "difficulty": opening_difficulty,
        })

        return (
            f"Welcome, {candidate.member.name}. Let's begin your technical interview for the "
            f"{candidate.member.jobRole} role.\n\n{question_text}"
        )

    def handle_turn(
        self, session: Dict[str, Any], message: str, turn_count: int
    ) -> Tuple[str, bool, Optional[Feedback]]:
        candidate: Candidate = session["candidate"]
        skill_state = session["skill_state"]

        last_topic = session.get("current_topic")
        last_question = self._last_agent_question(session)

        classification = classify_answer(message, last_topic, last_question, candidate)
        level = classification["level"]

        topic_state = skill_state[last_topic]
        topic_state["score"] = LEVEL_TO_SCORE.get(level, topic_state["score"])
        note = classification.get("evidence_note", "").strip()
        if note:
            topic_state["evidence"].append(note)

        topics_covered = sum(1 for s in skill_state.values() if s["times_asked"] > 0)
        should_stop = turn_count >= MAX_QUESTIONS or (
            turn_count >= MIN_QUESTIONS and topics_covered >= MIN_TOPICS
        )

        if should_stop:
            feedback = generate_feedback(session)
            return "Interview completed.", True, feedback

        next_topic, next_difficulty, reason = select_next_topic(session, last_topic, level)
        result = generate_question(candidate, next_topic, next_difficulty, session)
        question_text = result["question"]

        session["current_topic"] = next_topic
        session["current_difficulty"] = next_difficulty
        skill_state[next_topic]["times_asked"] += 1
        skill_state[next_topic]["difficulty_reached"] = next_difficulty

        session["reasoning_log"].append({
            "topic": next_topic,
            "curriculum_day": TOPIC_CURRICULUM_DAYS[next_topic][0],
            "reason": result.get("reason") or reason,
            "difficulty": next_difficulty,
        })

        return question_text, False, None

    @staticmethod
    def _last_agent_question(session: Dict[str, Any]) -> str:
        for turn in reversed(session.get("transcript", [])):
            if turn["role"] == "agent":
                # Strip the "Welcome, X..." preamble if present so only the
                # question portion is used as classification/prompt context.
                text = turn["text"]
                if "\n\n" in text:
                    return text.split("\n\n", 1)[1]
                return text
        return ""


# Module-level singleton used by main.py.
interview_agent = InterviewAgent()
