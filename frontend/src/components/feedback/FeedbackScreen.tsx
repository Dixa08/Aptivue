import { ArrowLeft, CheckCircle2, Compass, TrendingUp } from "lucide-react";
import type { Candidate, InterviewFeedback } from "../../types";
import { Logo } from "../common/Logo";

interface FeedbackScreenProps {
  candidate: Candidate;
  feedback: InterviewFeedback | null | undefined;
  finalReply: string;
  onRestart: () => void;
}

export function FeedbackScreen({ candidate, feedback, finalReply, onRestart }: FeedbackScreenProps) {
  return (
    <div className="mx-auto min-h-full max-w-4xl px-6 py-10 sm:px-10">
      <div className="mb-8 flex items-center justify-between">
        <Logo />
        <button
          onClick={onRestart}
          className="flex items-center gap-1.5 text-sm text-mist-300 transition-colors hover:text-mist-100"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to candidates
        </button>
      </div>

      <div className="animate-rise text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-signal-green/10 ring-1 ring-signal-green/30">
          <CheckCircle2 className="h-7 w-7 text-signal-green" />
        </div>
        <h1 className="font-display text-3xl font-semibold text-mist-50">Interview Complete</h1>
        <p className="mt-2 text-sm text-mist-400">
          {candidate.member.name} · {candidate.member.jobRole}
        </p>
      </div>

      {!feedback ? (
        <div className="glass mt-10 rounded-2xl p-6 text-center">
          <p className="text-sm text-mist-300">{finalReply}</p>
          <p className="mt-3 text-xs text-mist-400">
            No structured feedback was returned for this session.
          </p>
        </div>
      ) : (
        <div className="mt-10 space-y-6">
          {feedback.summary && (
            <section className="glass animate-rise rounded-2xl p-6 [animation-delay:80ms]">
              <h2 className="mb-2 font-display text-sm font-semibold uppercase tracking-wide text-mist-300">
                Overall Summary
              </h2>
              <p className="text-sm leading-relaxed text-mist-100">{feedback.summary}</p>
            </section>
          )}

          <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
            <FeedbackColumn
              title="Strengths"
              icon={<TrendingUp className="h-4 w-4 text-signal-green" />}
              accent="green"
              items={feedback.strengths}
              delay={140}
            />
            <FeedbackColumn
              title="Knowledge Gaps"
              icon={<Compass className="h-4 w-4 text-signal-amber" />}
              accent="amber"
              items={feedback.gaps}
              delay={200}
            />
            <FeedbackColumn
              title="Next Steps"
              icon={<ArrowLeft className="h-4 w-4 rotate-180 text-signal-blue" />}
              accent="blue"
              items={feedback.next}
              delay={260}
            />
          </div>
        </div>
      )}
    </div>
  );
}

const accentRing: Record<string, string> = {
  green: "ring-signal-green/20",
  amber: "ring-signal-amber/20",
  blue: "ring-signal-blue/20",
};

function FeedbackColumn({
  title,
  icon,
  accent,
  items,
  delay,
}: {
  title: string;
  icon: React.ReactNode;
  accent: string;
  items: string[] | undefined;
  delay: number;
}) {
  return (
    <section
      className={`glass animate-rise rounded-2xl p-5 ring-1 ${accentRing[accent]}`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="mb-3 flex items-center gap-2">
        {icon}
        <h3 className="font-display text-sm font-semibold text-mist-50">{title}</h3>
      </div>
      {!items || items.length === 0 ? (
        <p className="text-xs text-mist-400">Nothing reported here.</p>
      ) : (
        <ul className="space-y-2">
          {items.map((item, i) => (
            <li key={i} className="flex gap-2 text-sm leading-relaxed text-mist-200">
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-mist-400" />
              {item}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
