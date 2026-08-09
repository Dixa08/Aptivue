import type { ChatMessage } from "../../types";

export function ChatBubble({ message }: { message: ChatMessage }) {
  const isInterviewer = message.role === "interviewer";

  return (
    <div
      className={`flex animate-rise ${
        isInterviewer ? "justify-start" : "justify-end"
      }`}
    >
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isInterviewer
            ? "glass rounded-tl-sm text-slate-200"
            : "rounded-tr-sm bg-gradient-to-br from-signal-blue/90 to-signal-violet/80 text-white"
        }`}
      >
        {isInterviewer && (
          <div className="mb-2 font-mono text-[10px] tracking-wider text-blue-400">
            INTERVIEWER
          </div>
        )}

        <div className="text-slate-200">
          {message.text}
        </div>
      </div>
    </div>
  );
}