import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  experimental: {
    serverComponentsExternalPackages: ["@firebase/auth", "undici"],
  },
};

export default nextConfig;
