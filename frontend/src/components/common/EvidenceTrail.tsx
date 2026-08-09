interface EvidenceTrailProps {
  className?: string;
  variant?: "hero" | "inline";
}

/**
 * The Aptivue signature mark: a stepped trace line, like an oscilloscope
 * reading, that stands in for "the line adjusts to what it measures."
 * Purely decorative — it does not encode any real candidate data.
 */
export function EvidenceTrail({ className = "", variant = "hero" }: EvidenceTrailProps) {
  const path =
    variant === "hero"
      ? "M0 70 L40 70 L40 40 L90 40 L90 84 L150 84 L150 20 L210 20 L210 58 L270 58 L270 12 L330 12 L330 66 L400 66"
      : "M0 20 L14 20 L14 8 L30 8 L30 26 L48 26 L48 4 L66 4 L66 18 L84 18";

  const viewBox = variant === "hero" ? "0 0 400 96" : "0 0 84 30";

  return (
    <svg
      viewBox={viewBox}
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d={path}
        stroke="url(#trailGradient)"
        strokeWidth={variant === "hero" ? 2 : 1.5}
        strokeLinejoin="round"
        strokeLinecap="round"
        strokeDasharray={variant === "hero" ? 900 : 200}
        strokeDashoffset={0}
        className="animate-traceDraw"
      />
      {variant === "hero" &&
        [40, 90, 150, 210, 270, 330].map((x, i) => (
          <circle
            key={x}
            cx={x}
            cy={[70, 40, 84, 20, 58, 12][i]}
            r={3.5}
            fill="#0b0e16"
            stroke={i % 2 === 0 ? "#5b7fff" : "#9b7bf0"}
            strokeWidth={1.5}
          />
        ))}
      <defs>
        <linearGradient id="trailGradient" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#5b7fff" />
          <stop offset="50%" stopColor="#9b7bf0" />
          <stop offset="100%" stopColor="#4fd7d0" />
        </linearGradient>
      </defs>
    </svg>
  );
}
