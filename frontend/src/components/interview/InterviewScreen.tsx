import { useEffect, useRef, useState } from "react";
import { AlertTriangle, Send } from "lucide-react";
import type { Candidate, ChatMessage, InterviewFeedback } from "../../types";
import { continueInterview, InterviewApiError } from "../../lib/api";
import { topicsMentionedIn } from "../../data/topics";
import { Sidebar } from "./Sidebar";
import { ChatBubble } from "./ChatBubble";
import { AnalyzingIndicator } from "./AnalyzingIndicator";

interface InterviewScreenProps {
  candidate: Candidate;
  sessionId: string;
  initialMessages: ChatMessage[];
  onComplete: (feedback: InterviewFeedback | null | undefined, finalReply: string) => void;
}

function newId() {
  return Math.random().toString(36).slice(2, 10);
}

export function InterviewScreen({
  candidate,
  sessionId,
  initialMessages,
  onComplete,
}: InterviewScreenProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [latestReason, setLatestReason] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, pending]);

  const questionCount = messages.filter((m) => m.role === "interviewer").length;

  const discussedTopicIds = new Set<string>();
  messages
    .filter((m) => m.role === "interviewer")
    .forEach((m) => topicsMentionedIn(m.text).forEach((id) => discussedTopicIds.add(id)));

  async function handleSend() {
    const text = draft.trim();
    if (!text || pending) return;

    const candidateMsg: ChatMessage = {
      id: newId(),
      role: "candidate",
      text,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, candidateMsg]);
    setDraft("");
    setPending(true);
    setError(null);

    try {
      const res = await continueInterview(sessionId, text);
      setLatestReason(res.reason ?? null);

      if (res.done) {
        setMessages((prev) => [
          ...prev,
          { id: newId(), role: "interviewer", text: res.reply, timestamp: Date.now() },
        ]);
        onComplete(res.feedback, res.reply);
        return;
      }

      setMessages((prev) => [
        ...prev,
        { id: newId(), role: "interviewer", text: res.reply, timestamp: Date.now() },
      ]);
    } catch (err) {
      const msg =
        err instanceof InterviewApiError
          ? err.message
          : "Something went wrong reaching the interview backend.";
      setError(msg);
      // Put the candidate's answer back in the draft so nothing is lost.
      setDraft(text);
      setMessages((prev) => prev.filter((m) => m.id !== candidateMsg.id));
    } finally {
      setPending(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="grid h-screen grid-cols-1 md:grid-cols-[280px_1fr]">
      <div className="hidden md:block">
        <Sidebar
          candidate={candidate}
          questionCount={questionCount}
          discussedTopicIds={discussedTopicIds}
          latestReason={latestReason}
        />
      </div>

      <div className="flex h-screen flex-col">
        <header className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div>
            <h1 className="font-display text-sm font-semibold text-mist-800">
              Technical Interview
            </h1>
            <p className="text-xs text-mist-400">
              {questionCount > 0 ? `Question ${questionCount} of 8+` : "Starting…"}
            </p>
          </div>
          <span className="font-mono text-[10px] text-mist-500">
            session · {sessionId.slice(0, 8)}
          </span>
        </header>

        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto px-6 py-6">
          {messages.map((m) => (
            <ChatBubble key={m.id} message={m} />
          ))}
          {pending && <AnalyzingIndicator />}
        </div>

        {error && (
          <div className="mx-6 mb-3 flex items-start gap-2 rounded-lg border border-signal-red/30 bg-signal-red/10 px-3 py-2.5 text-sm text-signal-red">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <div>
              <p>{error}</p>
              <p className="mt-0.5 text-xs text-signal-red/80">
                Your answer wasn't lost — it's back in the box. Try sending again.
              </p>
            </div>
          </div>
        )}

        <div className="border-t border-slate-200 px-6 py-4">
          <div className="glass flex items-end gap-3 rounded-xl p-2 pl-4">
            <textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your answer…"
              rows={1}
              disabled={pending}
              className="max-h-40 min-h-[40px] flex-1 resize-none bg-transparent py-2 text-sm text-mist-100 placeholder:text-mist-400 focus:outline-none disabled:opacity-60"
            />
            <button
              onClick={handleSend}
              disabled={pending || !draft.trim()}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-signal-blue to-signal-violet text-white shadow-glow transition-transform hover:scale-105 active:scale-95 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:scale-100"
              aria-label="Send answer"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
          <p className="mt-2 text-[11px] text-mist-400">Enter to send · Shift+Enter for a new line</p>
        </div>
      </div>
    </div>
  );
}
