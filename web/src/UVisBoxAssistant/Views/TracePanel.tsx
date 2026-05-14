// ABOUTME: Wires the Trace library renderer to the UVisBoxAssistant global context.
// ABOUTME: Reads actors / trace / selection from the store and forwards onSelect.

import { observer } from "mobx-react-lite";
import Panel from "@/Panels/Panel";
import { Trace } from "@/Renderers/Trace";
import { useScenario } from "@/ScenarioManager/ScenarioManager";
import type UVisBoxAssistantGlobalContext from "../UVisBoxAssistantGlobalContext";

const TracePanel = observer(() => {
    const ctx = useScenario().globalContext as UVisBoxAssistantGlobalContext;
    return (
        <Panel panelName="Trace">
            <Trace
                actors={ctx.actors.slice()}
                messages={ctx.traceMessages.slice()}
                selectedId={ctx.selectedTraceId}
                onSelect={(id) => ctx.selectTrace(id)}
            />
        </Panel>
    );
});

export default TracePanel;
