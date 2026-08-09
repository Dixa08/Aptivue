export function AnalyzingIndicator() {
  return (
    <div className="flex animate-rise justify-start">
      <div className="glass flex items-center gap-2 rounded-2xl rounded-tl-sm px-4 py-3 text-sm text-mist-300">
        <span className="flex gap-1">
          <span className="h-1.5 w-1.5 animate-pulseDot rounded-full bg-signal-violet [animation-delay:0ms]" />
          <span className="h-1.5 w-1.5 animate-pulseDot rounded-full bg-signal-violet [animation-delay:200ms]" />
          <span className="h-1.5 w-1.5 animate-pulseDot rounded-full bg-signal-violet [animation-delay:400ms]" />
        </span>
        Analyzing your response…
      </div>
    </div>
  );
}
