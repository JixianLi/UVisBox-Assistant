// ABOUTME: Vite config for the UVisBox-Assistant web host.
// ABOUTME: Aliases @ to the webuvisbox source and proxies /ws + /figures to the Python server.

/// <reference types="vitest" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "../webuvisbox/src"),
        },
    },
    server: {
        port: 5173,
        proxy: {
            "/ws":      { target: "ws://127.0.0.1:8000",   ws: true },
            "/figures": { target: "http://127.0.0.1:8000", changeOrigin: false },
        },
    },
    test: {
        environment: "jsdom",
        globals: true,
    },
});
