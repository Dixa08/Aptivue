import raw from "./candidates.json";
import type { CandidatesFile } from "../types";

// Candidate data copied verbatim from the project's /data/candidates.json.
// Nothing here is invented or altered — see README for how to re-sync.
const candidatesFile = raw as CandidatesFile;

export const candidates = candidatesFile.candidates;
