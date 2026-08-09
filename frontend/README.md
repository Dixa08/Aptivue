# Aptivue — Frontend

React + Vite + TypeScript + Tailwind frontend for the Aptivue adaptive
technical interview agent. This talks to the existing backend at
`POST /api/interview` — nothing here changes that contract.

## Setup

```bash
cd frontend
npm install
cp .env.example .env    # defaults to http://127.0.0.1:8000
npm run dev
```

Open the printed local URL (typically `http://localhost:5173`). Make sure
the backend is running first (`http://127.0.0.1:8000/docs` should load).

## Environment variable

`VITE_API_URL` — base URL of the backend. Defaults to
`http://127.0.0.1:8000` if unset.

## How it talks to the backend

- `src/lib/api.ts` wraps `POST {VITE_API_URL}/api/interview`.
  - `startInterview(sessionId, candidate)` → sends `{ sessionId, candidate }`
    on "Start Interview".
  - `continueInterview(sessionId, message)` → sends
    `{ sessionId, message }` on every submitted answer.
  - The same `sessionId` (a `crypto.randomUUID()`) is reused for the whole
    session, generated once per interview in `App.tsx`.
- Responses are read as `{ reply, done, feedback? }`. When `done === true`,
  the app switches to the feedback screen and renders whatever
  `feedback.summary/strengths/gaps/next` the backend returned — nothing is
  invented if a field is missing or empty.
- An optional, unrequired `reason` field is read and shown in the "Interview
  Intelligence" panel only if the backend actually sends it.

## Project structure

```
src/
  types.ts                     API + domain types
  lib/api.ts                   fetch wrapper for /api/interview
  data/candidates.json         copied verbatim from data/candidates.json
  data/candidates.ts           typed re-export
  data/topics.ts                maps real mission titles to the 12 topic
                                categories (Embeddings, RAG, MCP, etc.)
  components/
    common/                    Logo, EvidenceTrail (signature mark)
    landing/                   Screen 1 — candidate selection
    interview/                 Screen 2 — sidebar, chat, learning journey
    feedback/                  Screen 3 — final results dashboard
  App.tsx                      screen routing + session lifecycle
```

## Re-syncing candidate data

If `data/candidates.json` changes upstream, copy it over
`frontend/src/data/candidates.json` (same shape, no fields renamed).

## Notes / known limitations

- "Discussed in Interview" badges in the Learning Journey sidebar are
  derived by matching the *interviewer's own question text* against topic
  keywords (e.g. the word "embedding") — a transparent, local heuristic.
  It does not talk to the backend and is not a claim about backend
  internals; it just reflects which topics have visibly come up so far in
  the live conversation.
- No interview score/metric is shown anywhere unless the backend's
  `feedback` object provides one — the UI never computes or fakes one.
- Tested manually end-to-end (start → multi-turn conversation → completion)
  against a local stub server matching the documented contract.
