import type { Metadata, Viewport } from "next";
import "./globals.css";
import SWRegister from "@/components/SWRegister";

export const metadata: Metadata = {
  title: "NORA",
  description: "Network Oracle for Reliable Answers — AI Research Engine standar telekomunikasi",
  applicationName: "NORA",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "NORA",
  },
  formatDetection: { telephone: false },
};

export const viewport: Viewport = {
  themeColor: "#0F3460",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body className="font-sans antialiased">
        {children}
        <SWRegister />
      </body>
    </html>
  );
}
