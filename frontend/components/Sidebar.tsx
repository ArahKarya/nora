"use client";

import type { Topic, User } from "@/lib/api";

export default function Sidebar({
  topics,
  activeId,
  onSelect,
  user,
  onLogout,
}: {
  topics: Topic[];
  activeId: string | null;
  onSelect: (id: string) => void;
  user: User | null;
  onLogout: () => void;
}) {
  return (
    <aside className="flex h-full w-64 flex-col bg-navy text-white">
      <div className="border-b border-white/10 px-5 py-5">
        <div className="text-2xl font-bold uppercase tracking-widest">
          NORA
        </div>
        <div className="mt-1 font-mono text-[10px] uppercase tracking-wide text-teal">
          NETWORK ORACLE
        </div>
      </div>

      <div className="px-5 pb-2 pt-4">
        <div className="font-mono text-xs uppercase tracking-wide text-white/50">
          TOPIK
        </div>
      </div>

      <nav className="scroll-thin scroll-thin-dark flex-1 overflow-y-auto px-3 pb-4">
        {topics.length === 0 && (
          <div className="px-2 py-3 font-mono text-xs text-white/40">
            Tidak ada topik
          </div>
        )}
        {topics.map((t) => {
          const active = t.id === activeId;
          return (
            <button
              key={t.id}
              onClick={() => onSelect(t.id)}
              className={`mb-1 flex w-full flex-col items-start border-l-2 px-3 py-2 text-left transition-colors ${
                active
                  ? "border-teal bg-white/10"
                  : "border-transparent hover:bg-white/5"
              }`}
            >
              <span className="text-sm font-semibold">{t.name}</span>
              <span className="font-mono text-[10px] uppercase tracking-wide text-white/40">
                {t.slug} · {t.count} doc
              </span>
            </button>
          );
        })}
      </nav>

      <div className="border-t border-white/10 px-5 py-4">
        <div className="truncate font-mono text-xs text-white/70">
          {user?.email ?? "—"}
        </div>
        <button
          onClick={onLogout}
          className="mt-2 w-full border border-white/20 px-3 py-2 font-mono text-xs uppercase tracking-wide text-white/80 hover:border-teal hover:text-teal"
        >
          Keluar
        </button>
      </div>
    </aside>
  );
}
