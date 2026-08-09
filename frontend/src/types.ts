export interface Mission {
  day: number;
  title: string;
  passed?: boolean;
  skipped?: boolean;
  attempts?: number;
}

export interface CandidateSignals {
  commitDays: number;
  missionsCompleted: number;
  missionsFirstTry: number;
}

export interface CandidateMember {
  id: string;
  name: string;
  jobRole: string;
  yearsExperience: number;
  education: string;
  status: string;
}

export interface Candidate {
  member: CandidateMember;
  missions: Mission[];
  signals: CandidateSignals;
}

export interface CandidatesFile {
  candidates: Candidate[];
}

// ---- Interview API contract (do not modify — matches backend exactly) ----

export interface InterviewStartRequest {
  sessionId: string;
  candidate: Candidate;
}

export interface InterviewTurnRequest {
  sessionId: string;
  message: string;
}

export interface InterviewFeedback {
  summary: string;
  strengths: string[];
  gaps: string[];
  next: string[];
}

export interface InterviewResponse {
  reply: string;
  done: boolean;
  feedback?: InterviewFeedback | null;
  /** Optional, safe, non-sensitive explanation of why the question adapted.
   *  Only rendered if the backend actually sends it — never fabricated. */
  reason?: string;
}

// ---- Frontend-only conversation state ----

export type ChatRole = "interviewer" | "candidate";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  text: string;
  timestamp: number;
}
