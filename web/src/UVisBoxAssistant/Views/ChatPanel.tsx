// ABOUTME: Wires the Chat library renderer to the UVisBoxAssistant global context.
// ABOUTME: Adds a refresh button above the transcript that resets the server-side session.

import { observer } from "mobx-react-lite";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import RefreshIcon from "@mui/icons-material/Refresh";
import Panel from "@/Panels/Panel";
import { Chat } from "@/Renderers/Chat";
import { useScenario } from "@/ScenarioManager/ScenarioManager";
import type UVisBoxAssistantGlobalContext from "../UVisBoxAssistantGlobalContext";

const ChatPanel = observer(() => {
    const ctx = useScenario().globalContext as UVisBoxAssistantGlobalContext;
    return (
        <Panel panelName="Chat">
            <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
                <Box
                    sx={{
                        display: "flex",
                        justifyContent: "flex-end",
                        p: 0.5,
                        borderBottom: 1,
                        borderColor: "divider",
                        flex: "0 0 auto",
                    }}
                >
                    <IconButton
                        size="small"
                        onClick={() => ctx.reset()}
                        title="Reset session"
                        disabled={ctx.connectionState !== "connected"}
                    >
                        <RefreshIcon fontSize="small" />
                    </IconButton>
                </Box>
                <Box sx={{ flex: 1, minHeight: 0 }}>
                    <Chat
                        messages={ctx.chatMessages.slice()}
                        onSubmit={(text) => ctx.submitUserPrompt(text)}
                        busy={ctx.busy}
                    />
                </Box>
            </Box>
        </Panel>
    );
});

export default ChatPanel;
