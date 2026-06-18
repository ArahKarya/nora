// Badge keyakinan — derive level dari confidence (0..1).
// >0.85 TINGGI, 0.7-0.85 SEDANG, <0.7 RENDAH.

function level(confidence: number): { bg: string; label: string } {
  const c = confidence ?? 0;
  if (c >= 0.85) return { bg: "bg-conf-high", label: "TINGGI" };
  if (c >= 0.7) return { bg: "bg-conf-medium", label: "SEDANG" };
  return { bg: "bg-conf-low", label: "RENDAH" };
}

export default function ConfidenceBadge({
  confidence,
}: {
  confidence: number;
  flag?: string | null;
}) {
  const cfg = level(confidence);
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
