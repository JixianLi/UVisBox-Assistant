// ABOUTME: Entry point for the UVisBox-Assistant web host.
// ABOUTME: Imports the UVisBoxAssistant scenario for its registration side effect, then mounts the app.

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@/index.css";
import App from "@/App";
import "./UVisBoxAssistant";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <App initialConfig="ScenarioConfigs/UVisBoxAssistant.json" />
    </StrictMode>,
);
