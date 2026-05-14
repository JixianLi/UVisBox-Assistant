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
        // webuvisbox/node_modules and web/node_modules both contain copies of
        // these packages; dedupe forces a single instance to be bundled so
        // emotion / MUI / React internals work correctly.
        dedupe: [
            "react",
            "react-dom",
            "@emotion/react",
            "@emotion/styled",
            "@mui/material",
            "@mui/icons-material",
            "@mui/system",
            "mobx",
            "mobx-react-lite",
        ],
    },
    server: {
        port: 5173,
        // Vite's default fs.allow is the project root (web/); webuvisbox is
        // a sibling, and pulling its source via the "@" alias means assets
        // (fonts, CSS) under ../webuvisbox/ also need to be readable.
        fs: {
            allow: [
                path.resolve(__dirname),
                path.resolve(__dirname, "../webuvisbox"),
            ],
        },
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
