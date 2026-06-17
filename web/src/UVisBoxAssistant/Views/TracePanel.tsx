// ABOUTME: Wires the Trace library renderer to the UVisBoxAssistant global context.
// ABOUTME: Reads actors / trace / selection from the store and forwards onSelect.

import { useState } from "react";
import { observer } from "mobx-react-lite";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import Slider from "@mui/material/Slider";
import Typography from "@mui/material/Typography";
import MenuIcon from "@mui/icons-material/Menu";
import Panel from "@/Panels/Panel";
import { Trace } from "@/Renderers/Trace";
import { useScenario } from "@/ScenarioManager/ScenarioManager";
import type UVisBoxAssistantGlobalContext from "../UVisBoxAssistantGlobalContext";

const TracePanel = observer(() => {
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
                        Font size: {ctx.traceFontSize}px
                    </Typography>
                    <Slider
                        size="small"
                        min={10}
                        max={24}
                        step={1}
                        value={ctx.traceFontSize}
                        onChange={(_, v) => ctx.setTraceFontSize(v as number)}
                    />
                </Box>
            </Menu>
        </>
    );

    return (
        <Panel panelName="Trace" appbarContent={appbarContent}>
            <Trace
                actors={ctx.actors.slice()}
                messages={ctx.traceMessages.slice()}
                selectedId={ctx.selectedTraceId}
                onSelect={(id) => ctx.selectTrace(id)}
                fontSize={ctx.traceFontSize}
            />
        </Panel>
    );
});

export default TracePanel;
