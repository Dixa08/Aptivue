import type {
  Candidate,
  InterviewResponse,
  InterviewStartRequest,
  InterviewTurnRequest,
} from "../types";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export class InterviewApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = "InterviewApiError";
    this.status = status;
  }
}

async function postInterview(
  body: InterviewStartRequest | InterviewTurnRequest
): Promise<InterviewResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}/api/interview`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new InterviewApiError(
      "Can't reach the interview backend. Confirm it's running and reachable at " + API_URL + "."
    );
  }

  if (res.status === 422) {
    let detail = "The request was rejected as invalid (422).";
    try {
      const data = await res.json();
      if (data?.detail) detail = typeof data.detail === "string" ? data.detail : detail;
    } catch {
      /* ignore parse failure, use default message */
    }
    throw new InterviewApiError(detail, 422);
  }

  if (!res.ok) {
    throw new InterviewApiError(
      `The interview backend returned an error (${res.status}). Please try again.`,
      res.status
    );
  }

  try {
    return (await res.json()) as InterviewResponse;
  } catch {
    throw new InterviewApiError("The backend returned an unreadable response.");
  }
}

export function startInterview(sessionId: string, candidate: Candidate) {
  return postInterview({ sessionId, candidate });
}

export function continueInterview(sessionId: string, message: string) {
  return postInterview({ sessionId, message });
}

export function generateSessionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `sess-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}
