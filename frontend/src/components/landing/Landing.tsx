import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import { candidates } from "../../data/candidates";
import type { Candidate } from "../../types";
import { CandidateCard } from "./CandidateCard";
import { EvidenceTrail } from "../common/EvidenceTrail";
import { Logo } from "../common/Logo";

interface LandingProps {
  onStart: (candidate: Candidate) => void;
  startingId: string | null;
}

export function Landing({ onStart, startingId }: LandingProps) {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return candidates;
    return candidates.filter(
      (c) =>
        c.member.name.toLowerCase().includes(q) ||
        c.member.jobRole.toLowerCase().includes(q)
    );
  }, [query]);

  return (
    <div className="min-h-full">
      <header className="flex items-center justify-between px-6 py-6 sm:px-10">
        <Logo />
        <span className="hidden font-mono text-xs text-mist-400 sm:block">
          v1 · session-scoped
        </span>
      </header>

      <section className="mx-auto max-w-5xl px-6 pb-14 pt-6 sm:px-10 sm:pt-10">
        <p className="mb-4 font-mono text-xs uppercase tracking-[0.2em] text-signal-blue">
          Evidence-Driven Adaptive Technical Interview Agent
        </p>
        <h1 className="animate-rise font-display text-4xl font-semibold leading-[1.08] tracking-tight text-mist-50 sm:text-5xl">
          An interview that adapts
          <br />
          to <span className="text-gradient">what you know.</span>
        </h1>
        <p className="mt-5 max-w-xl animate-rise text-base leading-relaxed text-mist-300 [animation-delay:80ms]">
          Aptivue transforms a candidate's learning journey into a personalized
          technical interview that adapts after every answer — probing weak
          spots, and raising the bar the moment it's earned.
        </p>

        <EvidenceTrail
          variant="hero"
          className="mt-10 h-16 w-full max-w-xl animate-rise opacity-80 [animation-delay:160ms]"
        />
      </section>

      <section className="mx-auto max-w-5xl px-6 pb-24 sm:px-10">
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="font-display text-lg font-semibold text-mist-50">
              Select a candidate
            </h2>
            <p className="text-sm text-mist-400">
              {candidates.length} candidates from the completed cohort
            </p>
          </div>
          <div className="relative w-full sm:w-64">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-mist-400" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search name or role…"
              className="glass w-full rounded-lg py-2 pl-9 pr-3 text-sm text-mist-100 placeholder:text-mist-400 focus:outline-none focus:ring-2 focus:ring-signal-blue/50"
            />
          </div>
        </div>

        {filtered.length === 0 ? (
          <p className="rounded-xl border border-dashed border-white/10 py-16 text-center text-sm text-mist-400">
            No candidates match "{query}".
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((c) => (
              <CandidateCard
                key={c.member.id}
                candidate={c}
                onStart={onStart}
                disabled={startingId === c.member.id}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
