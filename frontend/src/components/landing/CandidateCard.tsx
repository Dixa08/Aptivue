import { Briefcase, GraduationCap, Target, Zap } from "lucide-react";
import type { Candidate } from "../../types";

interface CandidateCardProps {
  candidate: Candidate;
  onStart: (candidate: Candidate) => void;
  disabled?: boolean;
}

export function CandidateCard({ candidate, onStart, disabled }: CandidateCardProps) {
  const { member, signals } = candidate;
  const initials = member.name
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("");

  return (
    <div className="glass group relative flex flex-col rounded-2xl p-5 shadow-glass transition-all duration-300 hover:border-signal-blue/40 hover:bg-white/[0.04]">
      <div className="flex items-start gap-3">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-ink-700 to-ink-800 font-display text-sm font-semibold text-mist-100 ring-1 ring-white/10">
          {initials}
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="truncate font-display text-base font-semibold text-mist-50">
            {member.name}
          </h3>
          <p className="flex items-center gap-1.5 truncate text-sm text-mist-300">
            <Briefcase className="h-3.5 w-3.5 shrink-0" />
            {member.jobRole}
          </p>
        </div>
      </div>

      <div className="mt-4 flex items-center gap-1.5 text-xs text-mist-400">
        <GraduationCap className="h-3.5 w-3.5 shrink-0" />
        <span className="truncate">{member.education}</span>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2 border-t border-white/[0.06] pt-4">
        <Stat label="Experience" value={`${member.yearsExperience}y`} />
        <Stat label="Missions" value={`${signals.missionsCompleted}`} icon={<Target className="h-3 w-3" />} />
        <Stat label="First-try" value={`${signals.missionsFirstTry}`} icon={<Zap className="h-3 w-3" />} />
      </div>

      <button
        onClick={() => onStart(candidate)}
        disabled={disabled}
        className="mt-5 w-full rounded-lg bg-gradient-to-r from-signal-blue to-signal-violet px-4 py-2.5 font-display text-sm font-medium text-white shadow-glow transition-transform duration-200 hover:scale-[1.02] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:scale-100"
      >
        {disabled ? "Starting…" : "Start Interview"}
      </button>
    </div>
  );
}

function Stat({ label, value, icon }: { label: string; value: string; icon?: React.ReactNode }) {
  return (
    <div className="flex flex-col items-start gap-0.5">
      <span className="flex items-center gap-1 font-mono text-sm font-medium text-mist-100">
        {icon}
        {value}
      </span>
      <span className="text-[10px] uppercase tracking-wide text-mist-400">{label}</span>
    </div>
  );
}
