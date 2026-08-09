import { Sparkles } from "lucide-react";

interface InterviewIntelligenceProps {
  reason?: string | null;
}

export function InterviewIntelligence({ reason }: InterviewIntelligenceProps) {
  return (
    <div className="glass rounded-xl p-4">
      <div className="mb-2 flex items-center gap-2">
        <Sparkles className="h-3.5 w-3.5 text-signal-violet" />
        <h3 className="font-display text-xs font-semibold uppercase tracking-wide text-mist-300">
          Interview Intelligence
        </h3>
      </div>
      <p className="text-xs leading-relaxed text-mist-400">
        Questions adapt to your previous answers and learning journey — probing
        further where a response is thin, and moving faster where it's strong.
      </p>
      {reason && (
        <p className="mt-2 rounded-lg bg-signal-violet/10 px-2.5 py-2 font-mono text-[11px] leading-relaxed text-signal-violet ring-1 ring-signal-violet/20">
          {reason}
        </p>
      )}
    </div>
  );
}
