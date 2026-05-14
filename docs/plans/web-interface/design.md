# Web Interface for UVisBox-Assistant — Design

## 1. Overview & Architecture

### Purpose

Add a browser-based interface for UVisBox-Assistant that shows the agent's
conversation as a chat (with embedded static plot images) and its execution
as a live swim-lane trace. The CLI REPL stays as a parallel entry point;
nothing about it changes.

### Top-level shape

Three pieces:

1. **Python WebSocket server** — new module `src/uvisbox_assistant/web/`.
   FastAPI app with one WebSocket endpoint (`/ws`) and one static-file
   endpoint (`/figures/<id>.png`). Wraps a single `ConversationSession` per
   socket connection. Runs the agent in a worker thread, streams trace +
   chat events to the client as the LangGraph workflow executes.

2. **Renderer abstraction** — new module
   `src/uvisbox_assistant/utils/renderer.py`. A `Renderer` interface with
   two implementations: `WindowRenderer` (current REPL behavior —
   `plt.show(block=False)` / `BackgroundPlotter`) and `FileRenderer(out_dir)`
   (matplotlib `savefig`, PyVista `Plotter(off_screen=True).screenshot`).
   Selected via `contextvars` at startup. Tools call
   `renderer.show_matplotlib(fig)` / `renderer.show_pyvista(plotter_factory)`;
   the file renderer returns the PNG path, which tools include in their
   result dict as `_figure_path`.

3. **React host app** — new top-level directory `web/` (peer of `src/`).
   Tiny Vite/React app that imports `webuvisbox`'s `<App>` and registers a
   single scenario `UVisBoxAssistant`. The scenario reuses webuvisbox's
   `Chat` and `Trace` renderers verbatim; its `GlobalContext` swaps the
   fake-agent driver for a WebSocket client. Dev server proxies `/ws` and
   `/figures` to FastAPI; production build is served as static assets by
   the same FastAPI process.

### Key invariants

- REPL code path unchanged.
- No graph or tool wrapping. Trace is sourced from LangGraph's
  `astream_events`.
- PNGs live on disk under `tmp_dev/web_figures/` and are served by URL,
  never inlined.

---

## 2. Backend — Server, Renderer, vis_tools changes

### Web module layout

```
src/uvisbox_assistant/web/
├── __init__.py
├── __main__.py          # python -m uvisbox_assistant.web → uvicorn launcher
├── server.py            # FastAPI app, lifespan, mounts WebSocket + static
├── session_runner.py    # Per-WS-connection agent driver
├── trace_translator.py  # LangGraph astream_events → TraceMessage + ChatMessage
└── figures.py           # Figure store: write PNG, return URL
```

`__main__.py` binds to `127.0.0.1:8000`, sets the contextvar to
`FileRenderer(tmp_dev/web_figures)` before importing the graph, and starts
uvicorn. Localhost-only — no auth.

### Renderer abstraction

```python
# src/uvisbox_assistant/utils/renderer.py
class Renderer(Protocol):
    def show_matplotlib(self, fig) -> Optional[str]: ...
    def show_pyvista(self, plotter_factory) -> Optional[str]: ...

class WindowRenderer:  # default; current behavior
    def show_matplotlib(self, fig):
        plt.show(block=False); plt.pause(0.1); return None
    def show_pyvista(self, plotter_factory):
        plotter = plotter_factory(off_screen=False); ...; return None

class FileRenderer:
    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
    def show_matplotlib(self, fig):
        path = self.out_dir / f"{uuid4().hex}.png"
        fig.savefig(path); plt.close(fig); return str(path)
    def show_pyvista(self, plotter_factory):
        plotter = plotter_factory(off_screen=True); ...
        path = self.out_dir / f"{uuid4().hex}.png"
        plotter.screenshot(path); plotter.close(); return str(path)

current_renderer: ContextVar[Renderer] = ContextVar(
    "renderer", default=WindowRenderer()
)
```

PyVista tools take a `plotter_factory` callable so the renderer chooses
`off_screen` — avoids hard-coding `BackgroundPlotter` inside tools.

### vis_tools.py changes

Replace each `plt.show(block=False)` and direct `BackgroundPlotter()` call
with:

```python
renderer = current_renderer.get()
path = renderer.show_matplotlib(fig)        # or .show_pyvista(factory)
result = {"status": "success", "message": ...}
if path is not None:
    result["_figure_path"] = path
```

CLI mode: `path` is `None`, result dict unchanged, REPL behavior
identical. ~10–15 LOC change per tool, mechanical.

### Figure cleanup

`tmp_dev/web_figures/` cleared on server startup and on `/reset`. No
per-figure GC during a session.

---

## 3. Backend — Trace event mapping & auto-rerender

### LangGraph → trace events

`session_runner.py` runs the agent via
`graph_app.astream_events(state, version="v2")` in a worker thread,
pushing translated events onto an `asyncio.Queue` that the WebSocket
task drains.

`trace_translator.py` filters and maps:

| `astream_events` event | Trace emitted | Chat emitted |
|---|---|---|
| `on_chain_start`, `name="model"` | — | — |
| `on_chat_model_end` with `tool_calls` | one `tool_call` per call: `model → {data_tool\|vis_tool}`, payload = `{tool, args}` | — |
| `on_chat_model_end` without `tool_calls` | `model → user` `prompt` (final response) | assistant text message |
| `on_tool_end`, status=success | `{tool_node} → model` `tool_result`, payload = truncated result | if `_figure_path` present: assistant image message |
| `on_tool_end`, status=error | `{tool_node} → model` `error`, payload = error message | — |
| Circuit-breaker stop (state-derived) | `model → user` `error` | assistant error text |

Routing between `data_tool` vs `vis_tool` actors is inferred from the
LangGraph node name in the event metadata. The `user → model` `prompt`
event is emitted by `session_runner.py` directly when the WS receives a
user message (not from the graph).

Hybrid commands bypass the graph; `session_runner.py` emits a synthetic
trace pair (`user → model` prompt, `model → user` system note) for them so
the user sees something in the trace panel.

### Auto-rerender flow

After a hybrid command returns successfully, `session_runner.py`:

1. Reads `state["last_vis_params"]` — it already contains `_tool_name`
   and the merged params.
2. Looks up the tool function by name from a new `TOOL_REGISTRY: dict[str, Callable]`
   added to `vis_tools.py`.
3. Calls it directly (not through the graph) with the merged params. The
   `FileRenderer` writes a PNG; result dict carries `_figure_path`.
4. Emits a synthetic `vis_tool → model` `tool_result` trace and an
   assistant chat message with the new image.

If no `last_vis_params` exists yet (hybrid command before any plot was
made), the system note explains that and skips re-render.

---

## 4. Frontend — Host app & scenario

### Directory layout (peer of `src/`)

```
web/
├── package.json          # depends on webuvisbox (file:../webuvisbox) + react + mui + mobx
├── tsconfig.json
├── vite.config.ts        # proxy /ws + /figures → http://127.0.0.1:8000
├── index.html
└── src/
    ├── main.tsx          # imports ./UVisBoxAssistant + mounts <App initialConfig=...>
    ├── UVisBoxAssistant/
    │   ├── index.ts                                # scenarioRegistry.register({...})
    │   ├── UVisBoxAssistantGlobalContext.ts        # MobX, WS client, implements GlobalContext
    │   ├── uvisboxAssistantPanelMappingFunction.tsx
    │   └── Views/
    │       ├── ChatPanel.tsx                       # wraps webuvisbox Chat renderer
    │       └── TracePanel.tsx                      # wraps webuvisbox Trace renderer
    └── public/
        └── ScenarioConfigs/
            └── UVisBoxAssistant.json               # 2-panel layout (chat left, trace right)
```

Depends on `webuvisbox` as a local file dependency
(`"webuvisbox": "file:../webuvisbox"`) so the submodule stays
consumed-as-a-library. Path alias `@webuvisbox` resolves to
`../webuvisbox/src` for direct imports of `Chat`, `Trace`,
`scenarioRegistry`, and types.

### UVisBoxAssistantGlobalContext

Same shape as `ChatUIGlobalContext` (`actors`, `traceMessages`,
`chatMessages`, `selectedTraceId`, `busy`), but `submitUserPrompt(text)`
sends a JSON message over the WebSocket instead of calling
`runFakeAgent`. On WS open, it issues `{type: "hello"}` and waits for
`session_ready` before accepting prompts. Incoming messages mutate the
MobX store via `appendTrace` / `appendChat`. Connection failure surfaces
as a system-role chat message and a disabled input.

### Reset button

A small `IconButton` (refresh icon) added to `ChatPanel.tsx`'s header,
above the transcript. Click → sends `{type: "reset"}` to the server,
which calls `session.reset()` and clears `tmp_dev/web_figures/`. Server
replies with a fresh `session_ready`; client clears its local stores.

### No other UI

No file panel, no slash-command surface, no cancel, no settings dialog.
Two panels and a reset button.

---

## 5. Wire protocol (WebSocket messages)

All messages are JSON. Single envelope shape with a `type`
discriminator. Messages with `id` use UUIDv4 generated by the server.

### Client → Server

```ts
{ type: "hello" }                                 // sent on WS open
{ type: "prompt", text: string }                  // user submits a message
{ type: "reset" }                                 // clears session + figures
```

### Server → Client

```ts
{ type: "session_ready", actors: Actor[] }        // sent after hello/reset
{ type: "trace", message: TraceMessage }          // append to trace panel
{ type: "chat", message: ChatMessage }            // append to chat panel
{ type: "busy", busy: boolean }                   // toggles input disabled state
{ type: "error", message: string }                // surfaced as system-role chat
```

`Actor`, `TraceMessage`, `ChatMessage` use the existing TypeScript shapes
from `webuvisbox/src/Renderers/Trace` and `Chat` verbatim — same field
names, same `kind` values. This is what lets the existing renderers
consume the stream with no changes.

### ChatMessage.content with images

Server emits an image message as:

```json
{
  "role": "assistant",
  "authorName": "vis_tool",
  "content": [
    { "type": "text", "text": "Functional boxplot for 30 curves." },
    { "type": "image", "url": "/figures/<id>.png", "alt": "functional_boxplot" }
  ]
}
```

The URL is a relative path so it works through the Vite proxy in dev and
same-origin in prod.

### Lifecycle

1. Client opens WS → sends `hello`.
2. Server creates a fresh `ConversationSession`, clears
   `tmp_dev/web_figures/`, replies `session_ready` with the 4 actors
   (`user`, `model`, `data_tool`, `vis_tool`).
3. Client sends `prompt` → server emits `busy:true`, runs agent, streams
   `trace` + `chat` events, emits `busy:false`.
4. `reset` resets server-side state and replies with a fresh
   `session_ready`. Client clears its stores.

---

## 6. Error handling & lifecycle edge cases

### Per-message try/except in session_runner.py

The worker thread wraps `graph_app.astream_events` in a try/except. On
any exception:

1. Emit one `error`-kind trace event (`model → user`, payload = exception
   message).
2. Emit one assistant chat message with the error text.
3. Emit `busy:false`.
4. The session stays alive — the user can send another prompt. We do
   *not* tear down the WebSocket on a graph-level error.

This mirrors the REPL's behavior in `main.py:282-289`.

### Tool-level errors

Already returned as `{"status": "error", ...}` by tools, flow through
`on_tool_end` and become `error`-kind trace messages — no special
handling.

### WebSocket disconnect mid-run

If the client disconnects while the worker thread is executing the
graph, the worker keeps running to completion (we have no cancel). The
producer task on the server detects the closed socket on its next
`send_json` and aborts cleanly; any pending queue items are dropped. The
`ConversationSession` is then GC'd along with the connection state.

### Renderer crashes

If `FileRenderer.show_matplotlib` or `show_pyvista` fails (e.g.,
off-screen OpenGL not available), the exception propagates out of the
tool. The tool's existing `except Exception as e` block in
`vis_tools.py:72` catches it and returns `{"status": "error", ...}` —
the trace surfaces this as a normal tool error. No `_figure_path` in the
result, so no image is appended.

### Figure-path serving

`GET /figures/<id>.png` is a `FileResponse` against
`tmp_dev/web_figures/`. Path validation: reject anything that isn't a
bare UUID-shaped filename ending in `.png`. 404 on miss.

### Hybrid auto-rerender failures

If the re-rendered plot tool returns `status: "error"`, emit an `error`
trace and an assistant chat message; do *not* update `last_vis_params`.
The previously-shown image stays visible to the user.

### Server shutdown

SIGINT (Ctrl-C) → uvicorn gracefully closes WebSocket connections,
server exits. PNGs in `tmp_dev/web_figures/` are left on disk; cleared
on next startup.

---

## 7. File layout summary & testing

### Full file inventory

**New backend files:**

```
src/uvisbox_assistant/
├── utils/renderer.py                    # Renderer protocol + Window/File impls + contextvar
└── web/
    ├── __init__.py
    ├── __main__.py                      # uvicorn launcher, sets FileRenderer contextvar
    ├── server.py                        # FastAPI app, WS endpoint, /figures static
    ├── session_runner.py                # Per-WS agent driver + worker thread
    ├── trace_translator.py              # astream_events → TraceMessage/ChatMessage
    └── figures.py                       # Figure store helpers
```

**Modified backend files:**

- `src/uvisbox_assistant/tools/vis_tools.py` — replace `plt.show()` /
  `BackgroundPlotter()` callsites with
  `current_renderer.get().show_matplotlib(fig)` / `.show_pyvista(factory)`;
  add `_figure_path` to result dicts. Add `TOOL_REGISTRY` dict at module
  bottom for hybrid auto-rerender lookup.
- `pyproject.toml` — add `fastapi`, `uvicorn[standard]`, `websockets` to
  main deps.

**New frontend files:**

```
web/
├── package.json, tsconfig.json, vite.config.ts, index.html
└── src/
    ├── main.tsx
    └── UVisBoxAssistant/
        ├── index.ts
        ├── UVisBoxAssistantGlobalContext.ts
        ├── uvisboxAssistantPanelMappingFunction.tsx
        └── Views/{ChatPanel,TracePanel}.tsx
└── public/ScenarioConfigs/UVisBoxAssistant.json
```

### Testing strategy

Aligned with `CLAUDE.md` API-budget rule (unit + uvisbox_interface =
0 LLM calls; llm_integration = small budget; E2E = acceptance stage
only).

**Unit (0 LLM calls):**

- `tests/unit/test_renderer.py` — `FileRenderer` writes PNGs to a temp
  dir, returns path; `WindowRenderer` paths return `None`. Use a no-op
  stub for PyVista factory.
- `tests/unit/test_trace_translator.py` — feed synthetic
  `astream_events` dicts, assert produced `TraceMessage` / `ChatMessage`
  sequences.
- `tests/unit/test_figures.py` — path validation rejects traversal
  attempts and non-PNG names.

**Integration — uvisbox_interface (0 LLM calls):**

- `tests/uvisbox_interface/test_file_renderer.py` — call each `plot_*`
  tool with `FileRenderer` active, assert a valid PNG appears on disk
  and `_figure_path` is in the result.
- `tests/uvisbox_interface/test_hybrid_rerender.py` — run a plot, run a
  hybrid command, assert the registry lookup re-invokes the right tool
  with merged params.

**Integration — llm_integration (small LLM budget):**

- `tests/llm_integration/test_web_session.py` — spin up the FastAPI app
  with `TestClient.websocket_connect`, send a `prompt`, drain events,
  assert at least one `tool_call` + one `tool_result` + one assistant
  `chat` arrived in order.

**E2E:** none. Chat + trace surface is already exercised by the
integration tests; full E2E would just retest the same plumbing through
the LLM.

### Out of scope (parked for follow-up features)

- Drag-and-drop file upload
- Cancel / stop button
- Session persistence across reloads
- Slash commands beyond `/reset`
- Multi-user / multi-tab shared sessions
- Trace payload truncation policy
- Session-files panel
- Settings / preferences UI
