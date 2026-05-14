// ABOUTME: UVisBoxAssistant scenario entry point — registers with the webuvisbox scenario registry.
// ABOUTME: Self-registers on import so main.tsx only needs a side-effect import.

import { scenarioRegistry } from "@/Scenarios/ScenarioRegistry";
import { UVisBoxAssistantGlobalContext } from "./UVisBoxAssistantGlobalContext";
import { uvisboxAssistantPanelMappingFunction } from "./uvisboxAssistantPanelMappingFunction";

scenarioRegistry.register({
    name: "UVisBoxAssistant",
    description: "UVisBox-Assistant — chat-driven uncertainty visualization",
    createGlobalContext: () => new UVisBoxAssistantGlobalContext(),
    panelMapping: uvisboxAssistantPanelMappingFunction,
    defaultConfigPath: "ScenarioConfigs/UVisBoxAssistant.json",
});

export { UVisBoxAssistantGlobalContext };
