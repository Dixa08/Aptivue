import { useState } from "react";
import { AlertTriangle, X } from "lucide-react";
import type { Candidate, ChatMessage, InterviewFeedback } from "./types";
import { generateSessionId, InterviewApiError, startInterview } from "./lib/api";
import { Landing } from "./components/landing/Landing";
import { InterviewScreen } from "./components/interview/InterviewScreen";
import { FeedbackScreen } from "./components/feedback/FeedbackScreen";

type Screen =
  | { name: "landing" }
  | { name: "interview"; candidate: Candidate; sessionId: string; initialMessages: ChatMessage[] }
  | { name: "feedback"; candidate: Candidate; feedback: InterviewFeedback | null | undefined; finalReply: string };

function newId() {
  return Math.random().toString(36).slice(2, 10);
}

export default function App() {
  const [screen, setScreen] = useState<Screen>({ name: "landing" });
  const [startingId, setStartingId] = useState<string | null>(null);
  const [startError, setStartError] = useState<string | null>(null);

  async function handleStart(candidate: Candidate) {
    setStartingId(candidate.member.id);
    setStartError(null);
    const sessionId = generateSessionId();

    try {
      const res = await startInterview(sessionId, candidate);
      const initialMessages: ChatMessage[] = [
        { id: newId(), role: "interviewer", text: res.reply, timestamp: Date.now() },
      ];

      if (res.done) {
        setScreen({ name: "feedback", candidate, feedback: res.feedback, finalReply: res.reply });
      } else {
        setScreen({ name: "interview", candidate, sessionId, initialMessages });
      }
    } catch (err) {
      setStartError(
        err instanceof InterviewApiError
          ? err.message
          : "Couldn't start the interview. Please try again."
      );
    } finally {
      setStartingId(null);
    }
  }

  function handleComplete(feedback: InterviewFeedback | null | undefined, finalReply: string) {
    if (screen.name !== "interview") return;
    setScreen({ name: "feedback", candidate: screen.candidate, feedback, finalReply });
  }

  function handleRestart() {
    setScreen({ name: "landing" });
  }

  return (
    <div className="min-h-screen">
      {startError && (
        <div className="fixed inset-x-0 top-0 z-50 flex justify-center px-4 pt-4">
          <div className="glass flex max-w-md items-start gap-2.5 rounded-xl border border-signal-red/30 bg-signal-red/10 px-4 py-3 text-sm text-signal-red shadow-glass">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <p className="flex-1">{startError}</p>
            <button onClick={() => setStartError(null)} aria-label="Dismiss">
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {screen.name === "landing" && <Landing onStart={handleStart} startingId={startingId} />}

      {screen.name === "interview" && (
        <InterviewScreen
          candidate={screen.candidate}
          sessionId={screen.sessionId}
          initialMessages={screen.initialMessages}
          onComplete={handleComplete}
        />
      )}

      {screen.name === "feedback" && (
        <FeedbackScreen
          candidate={screen.candidate}
          feedback={screen.feedback}
          finalReply={screen.finalReply}
          onRestart={handleRestart}
        />
      )}
    </div>
  );
}
