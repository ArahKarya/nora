"use client";

import type { QueryResult } from "@/lib/api";
import ConfidenceBadge from "./ConfidenceBadge";

export default function SourcesPanel({
  result,
  open,
  onToggle,
}: {
  result: QueryResult | null;
  open: boolean;
  onToggle: () => void;
}) {
  if (!open) {
    return (
      <div className="flex h-full w-10 flex-col items-center border-l border-slate-200 bg-white pt-4">
        <button
          onClick={onToggle}
          className="font-mono text-xs uppercase tracking-wide text-navy [writing-mode:vertical-rl]"
        >
          SUMBER
        </button>
      </div>
    );
  }

  return (
    <aside className="flex h-full w-80 flex-col border-l border-slate-200 bg-white">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-4">
        <h2 className="font-bold uppercase tracking-wide text-navy">Sumber</h2>
        <button
          onClick={onToggle}
          className="font-mono text-xs uppercase tracking-wide text-slate-400 hover:text-navy"
        >
          Tutup
        </button>
      </div>

      {!result && (
        <div className="px-4 py-6 font-mono text-xs text-slate-400">
          Belum ada jawaban. Kirim pertanyaan untuk melihat sumber.
        </div>
      )}

      {result && (
        <div className="scroll-thin flex-1 overflow-y-auto px-4 py-4">
          <div className="mb-2 font-mono text-xs uppercase tracking-wide text-slate-400">
            Keyakinan
          </div>
          <div className="mb-1">
            <ConfidenceBadge flag={result.flag} confidence={result.confidence} />
          </div>
          {result.verifier_verdict && (
            <div className="mb-4 font-mono text-[10px] uppercase tracking-wide text-slate-400">
              Verifier: {result.verifier_verdict}
            </div>
          )}

          <div className="mb-2 mt-4 font-mono text-xs uppercase tracking-wide text-slate-400">
            Dokumen ({result.sources.length})
          </div>
          <div className="space-y-3">
            {result.sources.map((s, i) => (
              <div
                key={`${s.spec}-${s.section}-${i}`}
                className="border border-slate-200 bg-offwhite p-3"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="font-mono text-[10px] uppercase tracking-wide text-navy">
                    {s.spec} {s.version} § {s.section}
                  </div>
                  <div className="shrink-0 font-mono text-[10px] text-teal">
                    {Math.round((s.similarity ?? 0) * 100)}%
                  </div>
                </div>
                <div className="mt-1 text-xs font-semibold text-ink">
                  {s.title}
                </div>
                <p className="mt-2 line-clamp-5 text-xs leading-relaxed text-slate-600">
                  {s.chunk_text}
                </p>
              </div>
            ))}
            {result.sources.length === 0 && (
              <div className="font-mono text-xs text-slate-400">
                Tidak ada sumber.
              </div>
            )}
          </div>
        </div>
      )}
    </aside>
  );
}
