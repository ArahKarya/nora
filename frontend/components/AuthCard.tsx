"use client";

import { useState } from "react";

/* ---- inline icons (no external dep; stroke = currentColor) ---- */
const I = {
  mail: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
      <rect x="3" y="5" width="18" height="14" />
      <path d="m3 7 9 6 9-6" />
    </svg>
  ),
  lock: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
      <rect x="4" y="10" width="16" height="11" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
    </svg>
  ),
  eye: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  ),
  eyeOff: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4">
      <path d="M10.7 6.2A9.8 9.8 0 0 1 12 5c6.5 0 10 7 10 7a17 17 0 0 1-3 3.7M6.6 6.6A17 17 0 0 0 2 12s3.5 7 10 7a9.7 9.7 0 0 0 5.4-1.6" />
      <path d="m2 2 20 20" />
    </svg>
  ),
};

const FEATURES = [
  "Tergrounded pada teks spesifikasi resmi — bukan halusinasi",
  "Diverifikasi model kedua sebelum jawaban dikirim",
  "Tiap jawaban auditable: confidence + sumber section",
];

const STATS = [
  { value: "257", label: "VERSI TS 24.008" },
  { value: "<10s", label: "LATENSI QUERY" },
  { value: "DUAL", label: "MODEL VERIFIER" },
];

/* input gaya ChatPanel/Sidebar — border tipis, focus navy, flat */
const INPUT_CLASS =
  "w-full border border-slate-200 bg-white py-2.5 pl-10 pr-10 text-sm text-ink outline-none transition-colors placeholder:text-slate-400 focus:border-navy";

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
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const isLogin = mode === "login";
  const tag = isLogin ? "MASUK" : "DAFTAR";
  const heading = isLogin ? "Selamat datang kembali" : "Buat akun baru";
  const sub = isLogin
    ? "Masuk untuk mulai riset spesifikasi telco di NORA."
    : "Daftar untuk mengakses engine riset spesifikasi telco NORA.";

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
    <div className="flex min-h-screen items-stretch bg-offwhite">
      {/* ============ BRAND PANEL (kiri, lg+) — navy solid flat, gaya Sidebar ============ */}
      <aside className="hidden flex-col justify-between bg-navy p-12 text-white lg:flex lg:w-[44%] xl:w-[40%]">
        {/* top: brand block (mirror Sidebar header) */}
        <div>
          <div className="text-3xl font-bold uppercase tracking-widest">NORA</div>
          <div className="mt-1.5 font-mono text-[10px] uppercase tracking-[0.2em] text-teal">
            NETWORK ORACLE FOR RELIABLE ANSWERS
          </div>
        </div>

        {/* middle: deskripsi + feature list (border-left teal, gaya item aktif Sidebar) */}
        <div className="max-w-sm">
          <div className="mb-4 font-mono text-[10px] uppercase tracking-[0.2em] text-white/40">
            AI RESEARCH ENGINE · STANDAR TELEKOMUNIKASI
          </div>
          <p className="text-[15px] leading-relaxed text-white/70">
            Engine riset RAG yang menjawab pertanyaan teknis standar telco
            langsung dari spesifikasi resmi — diverifikasi model kedua, dengan
            confidence dan sumber yang bisa ditelusuri.
          </p>

          <ul className="mt-8 space-y-0">
            {FEATURES.map((f) => (
              <li
                key={f}
                className="border-l-2 border-teal bg-white/5 px-4 py-2.5 text-[13px] text-white/80 [&:not(:last-child)]:mb-1"
              >
                {f}
              </li>
            ))}
          </ul>
        </div>

        {/* bottom: stat strip */}
        <div className="flex gap-8 border-t border-white/10 pt-6">
          {STATS.map((s) => (
            <div key={s.label}>
              <div className="text-xl font-bold tracking-tight text-teal">{s.value}</div>
              <div className="mt-0.5 font-mono text-[9px] uppercase tracking-[0.16em] text-white/40">
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* ============ FORM PANEL (kanan) ============ */}
      <main className="flex flex-1 items-center justify-center px-6 py-12">
        <div className="w-full max-w-[380px]">
          {/* mobile brand header (< lg) */}
          <div className="mb-10 lg:hidden">
            <div className="text-2xl font-bold uppercase tracking-widest text-navy">NORA</div>
            <div className="mt-1 font-mono text-[10px] uppercase tracking-[0.2em] text-teal">
              NETWORK ORACLE FOR RELIABLE ANSWERS
            </div>
          </div>

          {/* heading */}
          <div className="mb-8">
            <div className="mb-2 font-mono text-[11px] uppercase tracking-[0.2em] text-teal">
              {tag}
            </div>
            <h1 className="text-2xl font-bold uppercase tracking-wide text-navy">{heading}</h1>
            <p className="mt-2 text-sm text-slate-500">{sub}</p>
          </div>

          {/* error inline — gaya ChatPanel error */}
          {error && (
            <div
              role="alert"
              className="mb-5 border border-conf-low/30 bg-conf-low/10 px-3 py-2.5 font-mono text-xs text-conf-low"
            >
              {error}
            </div>
          )}

          <form onSubmit={handle} noValidate className="space-y-5">
            {/* email */}
            <div>
              <label className="mb-2 block font-mono text-[11px] uppercase tracking-wide text-slate-500">
                Email
              </label>
              <div className="relative">
                <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
                  {I.mail}
                </span>
                <input
                  type="email"
                  required
                  autoFocus
                  autoComplete="email"
                  placeholder="nama@arahkarya.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={INPUT_CLASS}
                />
              </div>
            </div>

            {/* password */}
            <div>
              <label className="mb-2 block font-mono text-[11px] uppercase tracking-wide text-slate-500">
                Kata Sandi
              </label>
              <div className="relative">
                <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
                  {I.lock}
                </span>
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  autoComplete={isLogin ? "current-password" : "new-password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={INPUT_CLASS}
                />
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? "Sembunyikan kata sandi" : "Tampilkan kata sandi"}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 text-slate-400 transition-colors hover:bg-slate-100 hover:text-navy"
                >
                  {showPassword ? I.eyeOff : I.eye}
                </button>
              </div>
            </div>

            {/* submit — flat teal, hover:opacity-90 (gaya tombol ChatPanel) */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-teal py-3 font-mono text-xs font-bold uppercase tracking-wide text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {loading ? "…" : tag}
            </button>
          </form>

          {/* footer */}
          <div className="mt-8 flex items-center justify-between border-t border-slate-200 pt-6 font-mono text-[11px] uppercase tracking-wide text-slate-400">
            <a href={altHref} className="transition-colors hover:text-teal">
              {altLabel}
            </a>
            <span>NOZ × ARAHKARYA</span>
          </div>
        </div>
      </main>
    </div>
  );
}
