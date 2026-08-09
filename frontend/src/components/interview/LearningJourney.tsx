import { Check, Circle, MessageSquare, X } from "lucide-react";
import type { Candidate } from "../../types";
import { cohortStatusFor, TOPICS } from "../../data/topics";

interface LearningJourneyProps {
  candidate: Candidate;
  discussedTopicIds: Set<string>;
}

export function LearningJourney({ candidate, discussedTopicIds }: LearningJourneyProps) {
  return (
    <div>
      <h3 className="mb-3 font-display text-xs font-semibold uppercase tracking-wide text-mist-300">
        Learning Journey
      </h3>
      <ul className="space-y-1.5">
        {TOPICS.map((topic) => {
          const cohortStatus = cohortStatusFor(candidate, topic);
          const discussed = discussedTopicIds.has(topic.id);
          return (
            <li
              key={topic.id}
              className="flex items-center justify-between rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-white/[0.03]"
            >
              <div className="flex min-w-0 items-center gap-2">
                <CohortIcon status={cohortStatus} />
                <span
                  className={
                    cohortStatus === "none"
                      ? "truncate text-mist-400"
                      : "truncate text-mist-100"
                  }
                >
                  {topic.label}
                </span>
              </div>
              {discussed && (
                <span
                  title="Discussed in Interview"
                  className="flex shrink-0 items-center gap-1 rounded-full bg-signal-violet/10 px-1.5 py-0.5 text-[10px] font-medium text-signal-violet ring-1 ring-signal-violet/25"
                >
                  <MessageSquare className="h-2.5 w-2.5" />
                  Live
                </span>
              )}
            </li>
          );
        })}
      </ul>
      <div className="mt-4 space-y-1.5 border-t border-white/[0.06] pt-3 text-[11px] text-mist-400">
        <Legend icon={<Check className="h-3 w-3 text-signal-green" />} label="Completed in Cohort" />
        <Legend icon={<X className="h-3 w-3 text-signal-red" />} label="Skipped in Cohort" />
        <Legend
          icon={<MessageSquare className="h-2.5 w-2.5 text-signal-violet" />}
          label="Discussed in Interview"
        />
      </div>
    </div>
  );
}

function CohortIcon({ status }: { status: ReturnType<typeof cohortStatusFor> }) {
  if (status === "passed")
    return (
      <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-signal-green/15">
        <Check className="h-2.5 w-2.5 text-signal-green" />
      </span>
    );
  if (status === "skipped")
    return (
      <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-signal-red/15">
        <X className="h-2.5 w-2.5 text-signal-red" />
      </span>
    );
  if (status === "attempted")
    return (
      <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-signal-amber/15">
        <Circle className="h-2 w-2 fill-signal-amber text-signal-amber" />
      </span>
    );
  return (
    <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-white/[0.04]">
      <Circle className="h-2 w-2 text-mist-400" />
    </span>
  );
}

function Legend({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      {icon}
      <span>{label}</span>
    </div>
  );
}
