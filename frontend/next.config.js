/** @type {import('next').NextConfig} */
const nextConfig = {
  // App directory is enabled by default in Next.js 13+
  experimental: {
    // Optimize compilation speed
    optimizeCss: true,
  },
  // Optimize bundle size
  swcMinify: true,
  // Reduce compilation time
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
}

module.exports = nextConfig
