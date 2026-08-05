import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone output keeps the Docker runtime image to node_modules actually used.
  output: "standalone",
};

export default nextConfig;
