import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: "#0F3460",
        teal: "#16C79A",
        offwhite: "#F7F9FC",
        ink: "#1A1A2E",
        conf: {
          high: "#16C79A",
          medium: "#F0A500",
          low: "#E94560",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      borderRadius: {
        sharp: "0px",
      },
    },
  },
  plugins: [],
};

export default config;
