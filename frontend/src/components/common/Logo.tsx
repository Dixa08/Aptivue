export function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-2.5">
      <div className="relative flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-signal-blue to-signal-violet shadow-glow">
        <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none">
          <path
            d="M4 16 L8 16 L8 10 L12 10 L12 18 L16 18 L16 6 L20 6"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
      {!compact && (
        <span className="font-display text-lg font-semibold tracking-tight text-mist-50">
          APTIVUE
        </span>
      )}
    </div>
  );
}
