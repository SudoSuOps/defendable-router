import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// DefendableRouter — we cracked the router. OpenWrt for AI agents.
// Deployed to defendablerouter.com via Cloudflare Pages.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist",
    target: "es2020",
    sourcemap: false,
  },
  server: {
    port: 5176,
    host: true,
  },
});
