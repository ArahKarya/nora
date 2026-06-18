import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NORA",
  description: "Network Oracle — RAG chat untuk spesifikasi",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
