import type { Candidate, Mission } from "../types";

export interface Topic {
  id: string;
  label: string;
  /** Case-insensitive substrings used to match this topic against real mission
   *  titles and against interviewer question text. Nothing is invented here —
   *  these are just the vocabulary a topic is known by. */
  keywords: string[];
}

// The canonical topic set called out in the product brief. Order is the
// rough order these subjects appear across the cohort curriculum.
export const TOPICS: Topic[] = [
  { id: "embeddings", label: "Embeddings", keywords: ["embedding"] },
  { id: "vector-db", label: "Vector Databases", keywords: ["vector database"] },
  { id: "retrieval", label: "Retrieval", keywords: ["retrieval"] },
  { id: "rag", label: "RAG", keywords: ["rag"] },
  { id: "prompt-eng", label: "Prompt Engineering", keywords: ["prompt engineering"] },
  { id: "function-calling", label: "Function Calling", keywords: ["function calling"] },
  { id: "agents", label: "Agents", keywords: ["langchain agents", "agent"] },
  { id: "multi-agent", label: "Multi-Agent", keywords: ["multi-agent"] },
  { id: "mcp", label: "MCP", keywords: ["model context protocol", "mcp"] },
  { id: "security", label: "Security", keywords: ["security", "guardrail"] },
  { id: "deployment", label: "Deployment", keywords: ["deployment", "docker", "kubernetes"] },
  { id: "observability", label: "Observability", keywords: ["observability", "monitoring", "logging"] },
];

export type CohortStatus = "passed" | "skipped" | "attempted" | "none";

function matchMission(missions: Mission[], topic: Topic): Mission | undefined {
  return missions.find((m) =>
    topic.keywords.some((kw) => m.title.toLowerCase().includes(kw))
  );
}

export function cohortStatusFor(candidate: Candidate, topic: Topic): CohortStatus {
  const mission = matchMission(candidate.missions, topic);
  if (!mission) return "none";
  if (mission.skipped) return "skipped";
  if (mission.passed) return "passed";
  return "attempted";
}

/** Very small, transparent keyword check used only to reflect back which
 *  topics the backend's own questions have touched on — never used to
 *  fabricate scores or completion state. */
export function topicsMentionedIn(text: string): string[] {
  const lower = text.toLowerCase();
  return TOPICS.filter((t) => t.keywords.some((kw) => lower.includes(kw))).map((t) => t.id);
}
