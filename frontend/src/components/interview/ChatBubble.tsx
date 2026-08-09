import type { ChatMessage } from "../../types";

export function ChatBubble({ message }: { message: ChatMessage }) {
  const isInterviewer = message.role === "interviewer";
  return (
    <div className={`flex animate-rise ${isInterviewer ? "justify-start" : "justify-end"}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isInterviewer
            ? "glass rounded-tl-sm text-slate-800"
            : "rounded-tr-sm bg-gradient-to-br from-signal-blue/90 to-signal-violet/80 text-white"
        }`}
      >
        {!isInterviewer ? null : (
          <span className="mb-1 block font-mono text-[10px] uppercase tracking-wider text-signal-blue">
            Interviewer
          </span>
        )}
        <p className="whitespace-pre-wrap">{message.text}</p>
      </div>
    </div>
  );
}
