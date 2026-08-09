import { Briefcase, Clock } from "lucide-react";
import type { Candidate } from "../../types";
import { Logo } from "../common/Logo";
import { LearningJourney } from "./LearningJourney";
import { InterviewIntelligence } from "./InterviewIntelligence";

interface SidebarProps {
  candidate: Candidate;
  questionCount: number;
  discussedTopicIds: Set<string>;
  latestReason?: string | null;
}

export function Sidebar({ candidate, questionCount, discussedTopicIds, latestReason }: SidebarProps) {
  const { member, signals } = candidate;

  return (
    <aside className="flex h-full w-full flex-col overflow-y-auto border-r border-white/[0.06] bg-ink-950/60 px-5 py-6">
      <Logo />

      <div className="mt-6 rounded-xl bg-white/[0.03] p-4 ring-1 ring-white/[0.06]">
        <h2 className="truncate font-display text-base font-semibold text-mist-50">
          {member.name}
        </h2>
        <p className="mt-1 flex items-center gap-1.5 text-sm text-mist-300">
          <Briefcase className="h-3.5 w-3.5 shrink-0" />
          {member.jobRole}
        </p>
        <p className="mt-1 flex items-center gap-1.5 text-xs text-mist-400">
          <Clock className="h-3 w-3 shrink-0" />
          {member.yearsExperience} years experience
        </p>

        <div className="mt-4 grid grid-cols-3 gap-2 border-t border-white/[0.06] pt-3 text-center">
          <MiniStat value={signals.missionsCompleted} label="Missions" />
          <MiniStat value={signals.missionsFirstTry} label="1st try" />
          <MiniStat value={signals.commitDays} label="Days" />
        </div>
      </div>

      <div className="mt-5 rounded-xl bg-white/[0.03] px-3 py-3 ring-1 ring-white/[0.06]">
        <div className="flex items-center justify-between text-xs">
          <span className="text-mist-400">Interview progress</span>
          <span className="font-mono text-mist-200">
            {questionCount > 0 ? `Q${questionCount}` : "—"}
          </span>
        </div>
        <div className="mt-2 flex gap-1">
          {Array.from({ length: Math.max(questionCount, 1) }).map((_, i) => (
            <span
              key={i}
              className={`h-1.5 flex-1 rounded-full ${
                i < questionCount ? "bg-gradient-to-r from-signal-blue to-signal-violet" : "bg-white/[0.06]"
              }`}
            />
          ))}
        </div>
      </div>

      <div className="mt-6 flex-1">
        <LearningJourney candidate={candidate} discussedTopicIds={discussedTopicIds} />
      </div>

      <div className="mt-5">
        <InterviewIntelligence reason={latestReason} />
      </div>
    </aside>
  );
}

function MiniStat({ value, label }: { value: number; label: string }) {
  return (
    <div>
      <div className="font-mono text-sm font-medium text-mist-100">{value}</div>
      <div className="text-[10px] uppercase tracking-wide text-mist-400">{label}</div>
    </div>
  );
}
