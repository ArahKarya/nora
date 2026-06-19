import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Offline — NORA",
};

export default function OfflinePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-navy px-6 text-center text-white">
      <div className="text-3xl font-bold uppercase tracking-widest">NORA</div>
      <div className="mt-1.5 font-mono text-[10px] uppercase tracking-[0.2em] text-teal">
        NETWORK ORACLE FOR RELIABLE ANSWERS
      </div>

      <div className="mt-10 max-w-sm">
        <h1 className="text-xl font-bold uppercase tracking-wide">Tidak ada koneksi</h1>
        <p className="mt-3 text-sm leading-relaxed text-white/60">
          NORA butuh koneksi internet untuk mengambil jawaban dari spesifikasi.
          Periksa jaringan Anda lalu coba lagi.
        </p>
      </div>

      <a
        href="/"
        className="mt-8 border border-white/20 px-6 py-3 font-mono text-xs uppercase tracking-wide text-white/80 transition-colors hover:border-teal hover:text-teal"
      >
        Coba lagi
      </a>
    </div>
  );
}
