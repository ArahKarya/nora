/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  async rewrites() {
    // Proxy /api/* ke backend (internal docker network).
    // Browser cuma lihat 1 origin (nora.arahkarya.com) → cookie same-origin, no CORS.
    const backend = process.env.BACKEND_INTERNAL_URL || "http://backend:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${backend}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
