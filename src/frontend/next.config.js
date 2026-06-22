/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Forward API calls to the FastAPI backend in dev / prod
  async rewrites() {
    const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      { source: '/api/:path*', destination: `${api}/api/:path*` },
    ];
  },
};

module.exports = nextConfig;
