import type { MetadataRoute } from "next";

/**
 * NORA — Web App Manifest (PWA installable).
 * Native Next.js 14: di-serve di /manifest.webmanifest, link di-inject otomatis.
 */
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "NORA — Network Oracle for Reliable Answers",
    short_name: "NORA",
    description:
      "AI Research Engine untuk standar telekomunikasi — jawaban tergrounded pada spesifikasi resmi, terverifikasi, dengan confidence dan sumber.",
    start_url: "/",
    scope: "/",
    display: "standalone",
    orientation: "portrait",
    background_color: "#0F3460",
    theme_color: "#0F3460",
    lang: "id",
    categories: ["productivity", "utilities"],
    icons: [
      { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
      { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any" },
      { src: "/icons/maskable-192.png", sizes: "192x192", type: "image/png", purpose: "maskable" },
      { src: "/icons/maskable-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
    ],
  };
}
