# Phase 04 — React Host App + UVisBoxAssistant Scenario

## Scope

Stand up a Vite/React app at the repo top-level `web/` directory that
imports `webuvisbox` as a local dependency, registers a single
`UVisBoxAssistant` scenario, and renders the chat + trace panels. The
scenario's `GlobalContext` is a WebSocket client that mirrors
`ChatUIGlobalContext` — same MobX shape, same trace/chat data — but
sources its events from the Python backend instead of `runFakeAgent`.

After this phase, `npm run dev` (in `web/`) plus
`python -m uvisbox_assistant.web` (in the project root) lets a user
type prompts in a browser and see live trace + chat updates with
embedded plot images. webuvisbox submodule is read-only — we depend on
it as a library.

## Implementation

### Task 1 — Top-level `web/` scaffold

Create the directory tree:

```
web/
├── package.json
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── vite.config.ts
├── index.html
├── public/
│   └── ScenarioConfigs/
│       └── UVisBoxAssistant.json
└── src/
    ├── main.tsx
    └── UVisBoxAssistant/
        ├── index.ts
        ├── UVisBoxAssistantGlobalContext.ts
        ├── uvisboxAssistantPanelMappingFunction.tsx
        └── Views/
            ├── ChatPanel.tsx
            └── TracePanel.tsx
```

**`package.json`:** name `uvisbox-assistant-web`, private, scripts
`dev`/`build`/`lint`/`preview` matching webuvisbox's. Dependencies:

```json
{
  "dependencies": {
    "webuvisbox": "file:../webuvisbox",
    "@mui/material": "^6",
    "@mui/icons-material": "^6",
    "@emotion/react": "^11",
    "@emotion/styled": "^11",
    "mobx": "^6",
    "mobx-react-lite": "^4",
    "react": "^18",
    "react-dom": "^18"
  },
  "devDependencies": {
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "@vitejs/plugin-react": "^4",
    "typescript": "^5",
    "vite": "^5",
    "vitest": "^2",
    "@testing-library/react": "^16"
  }
}
```

> Use the exact major versions webuvisbox already pins. Run
> `npm install` in `web/` after writing `package.json`; the `file:`
> dependency resolves to the submodule on disk.

**`vite.config.ts`:** standard React plugin + path alias `@webuvisbox`
→ `../webuvisbox/src`; proxy `/ws` and `/figures` to
`http://127.0.0.1:8000`:

```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@webuvisbox": path.resolve(__dirname, "../webuvisbox/src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/ws":      { target: "ws://127.0.0.1:8000", ws: true },
      "/figures": { target: "http://127.0.0.1:8000", changeOrigin: false },
    },
  },
});
```

**`tsconfig.app.json`:** mirror webuvisbox's structure; map paths for
`@webuvisbox/*` → `../webuvisbox/src/*`.

**`index.html`:** standard Vite template, loads `/src/main.tsx`.

### Task 2 — `src/main.tsx`

```tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "@webuvisbox/App";
import "./UVisBoxAssistant";  // self-registers the scenario

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App initialConfig="ScenarioConfigs/UVisBoxAssistant.json" />
  </StrictMode>
);
```

(Use whichever named export webuvisbox's `src/App.tsx` provides — if
default-exported, adjust the import.)

### Task 3 — `src/UVisBoxAssistant/index.ts`

```ts
// ABOUTME: ...

import { scenarioRegistry } from "@webuvisbox/Scenarios/ScenarioRegistry";
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
```

### Task 4 — `UVisBoxAssistantGlobalContext.ts`

Mirrors `ChatUIGlobalContext` but drives a WebSocket client.

State (all MobX observable):
- `actors: Actor[]` (populated from `session_ready`)
- `traceMessages: TraceMessage[]`
- `chatMessages: ChatMessage[]`
- `selectedTraceId: string | null`
- `busy: boolean`
- `connectionState: "connecting" | "connected" | "disconnected"`

Lifecycle in `asyncInitialize()`:

```ts
async asyncInitialize(): Promise<void> {
  this.connect();
}

private connect() {
  this.connectionState = "connecting";
  const proto = window.location.protocol === "https:" ? "wss" : "ws";
  this.ws = new WebSocket(`${proto}://${window.location.host}/ws`);

  this.ws.onopen = () => {
    runInAction(() => { this.connectionState = "connected"; });
    this.ws.send(JSON.stringify({ type: "hello" }));
  };
  this.ws.onmessage = (ev) => this.handleServerMessage(JSON.parse(ev.data));
  this.ws.onclose = () => {
    runInAction(() => {
      this.connectionState = "disconnected";
      this.appendChat({
        role: "system",
        content: "Disconnected from server. Reload the page to reconnect.",
      });
    });
  };
}
```

`handleServerMessage` dispatches:

| Server `type` | Action |
|---|---|
| `session_ready` | replace `actors`, clear `traceMessages` + `chatMessages` |
| `trace` | append `message` to `traceMessages` |
| `chat` | append `message` to `chatMessages` |
| `busy` | set `busy = msg.busy` |
| `error` | append to `chatMessages` as `{role: "system", content: msg.message}` |

User actions:

```ts
submitUserPrompt(text: string) {
  if (this.busy || this.connectionState !== "connected") return;
  this.ws.send(JSON.stringify({ type: "prompt", text }));
}

reset() {
  if (this.connectionState !== "connected") return;
  this.ws.send(JSON.stringify({ type: "reset" }));
}

selectTrace(id: string | null) { this.selectedTraceId = id; }
```

`initialize()`, `toObject()` — same minimal shape as `ChatUIGlobalContext`.

### Task 5 — `uvisboxAssistantPanelMappingFunction.tsx`

Maps panel IDs to JSX:

```tsx
export const uvisboxAssistantPanelMappingFunction: PanelMappingFunction = (
  panelId,
  ctx: UVisBoxAssistantGlobalContext,
) => {
  switch (panelId) {
    case "chat":  return <ChatPanel  ctx={ctx} />;
    case "trace": return <TracePanel ctx={ctx} />;
    default:      return null;
  }
};
```

### Task 6 — `Views/ChatPanel.tsx`

Thin wrapper around webuvisbox's `Chat` plus a reset button.

```tsx
import { observer } from "mobx-react-lite";
import IconButton from "@mui/material/IconButton";
import RefreshIcon from "@mui/icons-material/Refresh";
import Box from "@mui/material/Box";
import { Chat } from "@webuvisbox/Renderers/Chat";

export const ChatPanel = observer(({ ctx }: { ctx: UVisBoxAssistantGlobalContext }) => (
  <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
    <Box sx={{ display: "flex", justifyContent: "flex-end", p: 0.5,
               borderBottom: 1, borderColor: "divider" }}>
      <IconButton size="small" onClick={() => ctx.reset()} title="Reset session">
        <RefreshIcon fontSize="small" />
      </IconButton>
    </Box>
    <Box sx={{ flex: 1, minHeight: 0 }}>
      <Chat
        messages={ctx.chatMessages}
        busy={ctx.busy}
        onSubmit={(text) => ctx.submitUserPrompt(text)}
      />
    </Box>
  </Box>
));
```

### Task 7 — `Views/TracePanel.tsx`

```tsx
import { observer } from "mobx-react-lite";
import { Trace } from "@webuvisbox/Renderers/Trace";

export const TracePanel = observer(({ ctx }: { ctx: UVisBoxAssistantGlobalContext }) => (
  <Trace
    actors={ctx.actors}
    messages={ctx.traceMessages}
    selectedId={ctx.selectedTraceId}
    onSelect={(id) => ctx.selectTrace(id)}
  />
));
```

### Task 8 — `public/ScenarioConfigs/UVisBoxAssistant.json`

Two-panel responsive layout (chat left, trace right). Match the shape
of the existing `webuvisbox/examples/public/ScenarioConfigs/ChatUI.json`
— same breakpoints, panel IDs `"chat"` and `"trace"`. Example xl
breakpoint:

```json
{
  "name": "UVisBoxAssistant",
  "panel_layouts": {
    "xl": [
      { "i": "chat",  "x": 0, "y": 0, "w": 6, "h": 12 },
      { "i": "trace", "x": 6, "y": 0, "w": 6, "h": 12 }
    ],
    "lg": [...],
    "sm": [...]
  },
  "global_data": {}
}
```

Use the ChatUI config as a literal template — copy its layout numbers.

### Task 9 — TS unit test for the GlobalContext

`web/src/UVisBoxAssistant/__tests__/UVisBoxAssistantGlobalContext.test.ts`.

Stub `WebSocket` with a tiny mock class (records `send` calls, exposes
methods to trigger `onopen`, `onmessage`, `onclose`). Use Vitest.

Cover:
- After construction + connect + mock `onopen`, the context sends
  `{type:"hello"}`.
- On `session_ready` message, `actors` is set and stores cleared.
- On `trace` message, `traceMessages` length grows by 1.
- On `chat` message with image content, `chatMessages` entry preserves
  the content parts array.
- On `busy: true`, `submitUserPrompt` is a no-op (send is not called).
- On `reset()`, sends `{type:"reset"}` and stores stay until the next
  `session_ready` clears them.

## Verification

- `cd web && npm install` succeeds (resolves `webuvisbox` from
  `../webuvisbox`).
- `cd web && npm run dev` starts Vite on port 5173.
- With the Python server running, navigate to `http://localhost:5173`:
  - Two panels render (chat left, trace right).
  - The chat input is enabled.
  - Typing "Generate 30 curves and plot functional boxplot" produces:
    - a `user → model` trace bar appearing immediately,
    - subsequent `tool_call` / `tool_result` bars,
    - a chat bubble containing the generated PNG (visible image),
    - input re-enables when `busy: false` arrives.
  - Clicking the refresh button clears both panels and re-enables input
    against a fresh server-side session.
- `cd web && npm run lint` passes.
- `cd web && npm test` (vitest) passes.

## Validation

- REPL untouched — `python tests/test.py --pre-planning` still green.
- Manual disconnect test: stop the Python server while the browser is
  open; a system chat message appears, input disables.

## Acceptance Criteria

- [ ] `web/` directory exists with the file tree above; `npm install`
      and `npm run dev` succeed.
- [ ] `UVisBoxAssistant` scenario registers via `scenarioRegistry`.
- [ ] WebSocket client sends `hello` on open, handles
      `session_ready` / `trace` / `chat` / `busy` / `error`.
- [ ] Reset button sends `{type:"reset"}` and stores re-clear on
      server's `session_ready`.
- [ ] Trace panel and chat panel render via webuvisbox's library
      renderers (no fork).
- [ ] Vitest unit test for the GlobalContext passes.
- [ ] Manual browser smoke: prompt → image-in-chat workflow works
      end-to-end against a running Python server.
- [ ] webuvisbox submodule unchanged.

## Git Commit

```
feat(web): add React host app for UVisBox-Assistant

Creates web/ as a Vite/React project that consumes webuvisbox as a
local file dependency and registers a UVisBoxAssistant scenario. The
scenario's GlobalContext is a WebSocket client driving webuvisbox's
Chat and Trace renderers. Reset button maps to the server's reset
message. Adds a Vitest unit test for the WS state machine.
```

Include all files under the new `web/` directory.
