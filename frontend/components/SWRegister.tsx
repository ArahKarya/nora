"use client";

import { useEffect } from "react";

/**
 * Daftarkan service worker (production saja).
 * Gagal diam-diam jika SW tak didukung / di-block — tidak mengganggu app.
 */
export default function SWRegister() {
  useEffect(() => {
    if (
      typeof window !== "undefined" &&
      "serviceWorker" in navigator &&
      process.env.NODE_ENV === "production"
    ) {
      navigator.serviceWorker.register("/sw.js").catch(() => {
        /* abaikan: SW opsional, app tetap jalan tanpa offline support */
      });
    }
  }, []);

  return null;
}
