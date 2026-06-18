"use client";

import { useState } from "react";

export default function AuthCard({
  mode,
  onSubmit,
  altHref,
  altLabel,
}: {
  mode: "login" | "register";
  onSubmit: (email: string, password: string) => Promise<void>;
  altHref: string;
  altLabel: string;
}) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const title = mode === "login" ? "Masuk" : "Daftar";
  const cta = mode === "login" ? "Masuk" : "Daftar";

  async function handle(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await onSubmit(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Terjadi kesalahan");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-offwhite px-4">
      <div className="w-full max-w-sm border border-slate-200 bg-white p-8">
        <div className="mb-1 text-center text-3xl font-bold uppercase tracking-widest text-navy">
          NORA
        </div>
        <div className="mb-6 text-center font-mono text-[10px] uppercase tracking-wide text-teal">
          {title}
        </div>

        <form onSubmit={handle} className="space-y-4">
          <div>
            <label className="mb-1 block font-mono text-xs uppercase tracking-wide text-slate-500">
              Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-slate-200 bg-white px-3 py-2 text-sm text-ink outline-none focus:border-navy"
            />
          </div>
          <div>
            <label className="mb-1 block font-mono text-xs uppercase tracking-wide text-slate-500">
              Kata Sandi
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-slate-200 bg-white px-3 py-2 text-sm text-ink outline-none focus:border-navy"
            />
          </div>

          {error && (
            <div className="border border-conf-low/40 bg-conf-low/10 px-3 py-2 font-mono text-xs text-conf-low">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-teal py-3 font-mono text-xs font-bold uppercase tracking-wide text-white transition-opacity hover:opacity-90 disabled:opacity-40"
          >
            {loading ? "…" : cta}
          </button>
        </form>

        <div className="mt-6 text-center font-mono text-xs text-slate-500">
          <a href={altHref} className="hover:text-teal">
            {altLabel}
          </a>
        </div>
      </div>
    </div>
  );
}
