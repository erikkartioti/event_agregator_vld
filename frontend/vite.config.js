import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// В dev: /api -> Spring Boot (8080), /tiles -> Martin (3000)
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8080",
      "/tiles": {
        target: "http://localhost:3000",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/tiles/, ""),
      },
    },
  },
  build: { outDir: "dist" },
});
