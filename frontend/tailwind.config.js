/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#080a10",
          900: "#0b0e16",
          850: "#0f1320",
          800: "#131829",
          700: "#1a2036",
          600: "#242c47",
          500: "#323c5e",
        },
        mist: {
          400: "#5b6482",
          300: "#7d86a3",
          200: "#a7aec4",
          100: "#ced2e2",
          50: "#e9ebf3",
        },
        signal: {
          blue: "#5b7fff",
          violet: "#9b7bf0",
          cyan: "#4fd7d0",
          amber: "#f0b45b",
          green: "#4ade9a",
          red: "#f0705b",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      boxShadow: {
        glass: "0 1px 0 0 rgba(255,255,255,0.04) inset, 0 8px 24px -12px rgba(0,0,0,0.6)",
        glow: "0 0 0 1px rgba(91,127,255,0.25), 0 0 24px -4px rgba(91,127,255,0.35)",
      },
      keyframes: {
        pulseDot: {
          "0%, 100%": { opacity: 1, transform: "scale(1)" },
          "50%": { opacity: 0.5, transform: "scale(0.85)" },
        },
        rise: {
          "0%": { opacity: 0, transform: "translateY(8px)" },
          "100%": { opacity: 1, transform: "translateY(0)" },
        },
        traceDraw: {
          "0%": { strokeDashoffset: 240 },
          "100%": { strokeDashoffset: 0 },
        },
      },
      animation: {
        pulseDot: "pulseDot 1.8s ease-in-out infinite",
        rise: "rise 0.5s cubic-bezier(0.16,1,0.3,1) both",
        traceDraw: "traceDraw 1.2s ease-out both",
      },
    },
  },
  plugins: [],
}
