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
            "@": path.resolve(__dirname, "../external/webuvisbox/src"),
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
    // webuvisbox source is consumed via the "@" alias, so Vite's dep scanner
    // does not crawl into it to discover these CJS deps. Pre-bundle them
    // explicitly so they get ESM-interop wrappers (a `default` export); without
    // this, @mui's responsivePropType.mjs imports raw CJS prop-types and the
    // browser throws "does not provide an export named 'default'".
    optimizeDeps: {
        include: ["prop-types", "react-is"],
    },
    server: {
        port: 5173,
        // Vite's default fs.allow is the project root (web/); webuvisbox lives
        // under ../external/, and pulling its source via the "@" alias means
        // assets (fonts, CSS) under ../external/webuvisbox/ also need to be readable.
        fs: {
            allow: [
                path.resolve(__dirname),
                path.resolve(__dirname, "../external/webuvisbox"),
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
