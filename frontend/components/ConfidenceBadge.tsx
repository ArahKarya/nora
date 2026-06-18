import type { Flag } from "@/lib/api";

const MAP: Record<Flag, { bg: string; label: string }> = {
  HIGH: { bg: "bg-conf-high", label: "TINGGI" },
  MEDIUM: { bg: "bg-conf-medium", label: "SEDANG" },
  LOW: { bg: "bg-conf-low", label: "RENDAH" },
};

export default function ConfidenceBadge({
  flag,
  confidence,
}: {
  flag: Flag;
  confidence: number;
}) {
  const cfg = MAP[flag] ?? MAP.LOW;
  const pct = Math.round((confidence ?? 0) * 100);
  return (
    <span
      className={`inline-flex items-center gap-2 px-2 py-1 font-mono text-xs uppercase tracking-wide text-white ${cfg.bg}`}
    >
      <span className="font-bold">{cfg.label}</span>
      <span className="opacity-90">{pct}%</span>
    </span>
  );
}
