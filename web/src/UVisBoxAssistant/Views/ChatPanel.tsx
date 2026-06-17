// ABOUTME: Wires the Chat library renderer to the UVisBoxAssistant global context.
// ABOUTME: Adds a refresh button above the transcript that resets the server-side session.

import { useState } from "react";
import { observer } from "mobx-react-lite";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import Slider from "@mui/material/Slider";
import Typography from "@mui/material/Typography";
import MenuIcon from "@mui/icons-material/Menu";
import RefreshIcon from "@mui/icons-material/Refresh";
import Panel from "@/Panels/Panel";
import { Chat } from "@/Renderers/Chat";
import { useScenario } from "@/ScenarioManager/ScenarioManager";
import type UVisBoxAssistantGlobalContext from "../UVisBoxAssistantGlobalContext";

const ChatPanel = observer(() => {
    const ctx = useScenario().globalContext as UVisBoxAssistantGlobalContext;
    const [anchor, setAnchor] = useState<null | HTMLElement>(null);

    const appbarContent = (
        <>
            <IconButton
                size="small"
                edge="start"
                color="inherit"
                aria-label="settings"
                sx={{ mr: 1 }}
                onClick={(e) => setAnchor(e.currentTarget)}
            >
                <MenuIcon fontSize="small" />
            </IconButton>
            <Menu anchorEl={anchor} open={Boolean(anchor)} onClose={() => setAnchor(null)}>
                <Box sx={{ px: 2, py: 1, width: 200 }} onKeyDown={(e) => e.stopPropagation()}>
                    <Typography variant="caption" color="text.secondary">
                        Font size: {ctx.chatFontSize}px
                    </Typography>
                    <Slider
                        size="small"
                        min={10}
                        max={24}
                        step={1}
                        value={ctx.chatFontSize}
                        onChange={(_, v) => ctx.setChatFontSize(v as number)}
                    />
                </Box>
            </Menu>
        </>
    );

    return (
        <Panel panelName="Chat" appbarContent={appbarContent}>
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
                        fontSize={ctx.chatFontSize}
                    />
                </Box>
            </Box>
        </Panel>
    );
});

export default ChatPanel;
