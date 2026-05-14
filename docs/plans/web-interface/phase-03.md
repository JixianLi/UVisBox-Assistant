# Phase 03 — Agent Integration Over WebSocket

## Scope

Replace the Phase 02 prompt NACK with full agent integration: a per-WS
`ConversationSession`, a worker thread running the LangGraph workflow via
`astream_events`, an `asyncio.Queue` carrying translated events back to
the WebSocket, and the hybrid auto-rerender flow. After this phase, a
Python WebSocket client can send a prompt and receive a complete stream
of `trace` / `chat` / `busy` events ending in `busy: false`. No browser
yet.

## Implementation

### Task 1 — `trace_translator.py`

New file `src/uvisbox_assistant/web/trace_translator.py`. Pure function
module — no state, no async, no I/O. Each translator function takes a
`dict` (an `astream_events` event) and returns a list of zero or more
`{"type": "trace"|"chat", "message": {...}}` envelopes.

API:

```python
def translate_event(event: dict, ctx: TranslatorContext) -> list[dict]:
    ...
```

`TranslatorContext` is a small dataclass: `last_seen_node: Optional[str]`
(updated as `on_chain_start` events come through; used to disambiguate
which tool node ran). It is mutable; the caller owns it across the
lifetime of one `astream_events` iteration.

Mapping (per the design doc, Section 3):

| Incoming event | Output envelopes |
|---|---|
| `on_chain_start` where `event["name"] in ("data_tool", "vis_tool")` | update `ctx.last_seen_node` |
| `on_chat_model_end` with `event["data"]["output"].tool_calls` | one trace per call: `{from: "model", to: tool_node_for(call.name), kind: "tool_call", payload: {tool, args}}` |
| `on_chat_model_end` without tool_calls | one trace: `{from: "model", to: "user", kind: "prompt", payload: text}`; one chat: `{role: "assistant", authorName: "Model", content: text}` |
| `on_tool_end` with success | one trace: `{from: ctx.last_seen_node, to: "model", kind: "tool_result", payload: truncated_result}`; if `_figure_path` present, one chat: image content (see below) |
| `on_tool_end` with error / exception in `event["data"]["output"]["status"]` | one trace: `{from: ctx.last_seen_node, to: "model", kind: "error", payload: error_message}` |

Helpers:
- `tool_node_for(tool_name: str) -> str` — checks
  `tool_name in TOOL_REGISTRY` (vis tool) else `"data_tool"`.
- `truncate_payload(result: dict) -> dict` — drops large fields (numpy
  blobs, base64 strings). For Phase 03 keep it simple: include only
  `status`, `message`, and a short `keys_preview` listing other top-level
  keys.
- `figure_url(path: str) -> str` — converts an absolute path like
  `/abs/tmp_dev/web_figures/<uuid>.png` to the relative URL
  `/figures/<uuid>.png`.

Image chat envelope:

```python
{
    "type": "chat",
    "message": {
        "role": "assistant",
        "authorName": tool_label,  # e.g., "Vis Tool"
        "content": [
            {"type": "text", "text": result.get("message", "")},
            {"type": "image", "url": figure_url(result["_figure_path"]),
             "alt": tool_name},
        ],
    },
}
```

### Task 2 — `session_runner.py`

New file `src/uvisbox_assistant/web/session_runner.py`. Holds the
plumbing that turns a WebSocket plus one `ConversationSession` into a
streaming event source.

Class `SessionRunner`:

```python
class SessionRunner:
    def __init__(self, ws: WebSocket):
        self.ws = ws
        self.session = ConversationSession()
        self.busy = False

    async def handle_prompt(self, text: str) -> None:
        if self.busy:
            await self.ws.send_json({"type": "error",
                                     "message": "already processing a prompt"})
            return
        self.busy = True
        await self.ws.send_json({"type": "busy", "busy": True})

        # Emit synthetic user→model prompt trace
        await self._send_trace(from_="user", to="model", kind="prompt",
                               payload=text)
        await self._send_chat({"role": "user", "content": text})

        # Try hybrid first; fall back to streaming graph
        if self.session.state and is_hybrid_eligible(text):
            await self._handle_hybrid(text)
        else:
            await self._handle_graph(text)

        self.busy = False
        await self.ws.send_json({"type": "busy", "busy": False})

    async def reset(self) -> None:
        self.session.reset()
        # caller (server.py) clears figures and replies session_ready
```

`_handle_graph` runs the agent in a worker thread, draining translated
events to the WebSocket:

```python
async def _handle_graph(self, text: str) -> None:
    queue: asyncio.Queue = asyncio.Queue()
    ctx = TranslatorContext()

    # Update session state in main thread (no graph invocation yet)
    if self.session.state is None:
        self.session.state = create_initial_state(text)
    else:
        self.session.state["messages"].append(HumanMessage(content=text))

    loop = asyncio.get_running_loop()

    def worker():
        try:
            async def run():
                async for event in graph_app.astream_events(
                    self.session.state, version="v2"
                ):
                    for envelope in translate_event(event, ctx):
                        await queue.put(envelope)
                # On success, capture final state
                final = await graph_app.ainvoke(self.session.state)
                await queue.put({"_done": True, "_state": final})
            asyncio.run(run())
        except Exception as e:
            loop.call_soon_threadsafe(
                queue.put_nowait,
                {"_done": True, "_error": str(e)},
            )

    threading.Thread(target=worker, daemon=True).start()

    while True:
        env = await queue.get()
        if env.get("_done"):
            if env.get("_error"):
                await self._send_trace(from_="model", to="user",
                                       kind="error", payload=env["_error"])
                await self._send_chat({
                    "role": "assistant", "authorName": "Model",
                    "content": f"Error: {env['_error']}",
                })
            else:
                self.session.state = env["_state"]
            return
        await self.ws.send_json(env)
```

> **Implementation note:** `graph_app.astream_events` and `ainvoke`
> together would double-execute the graph. Resolve this by running
> `astream_events` only, accumulating the final state from the stream's
> own state-update events (LangGraph emits a final `on_chain_end` for
> the root with the output state in `event["data"]["output"]`). Update
> `self.session.state` from that event in `translate_event` (returning
> no envelopes, just mutating ctx) or via a second pass. The Task
> Engineer will pick whichever path proves cleanest after reading the
> actual event shapes from `astream_events`.

`_handle_hybrid` follows the hybrid-control flow:

```python
async def _handle_hybrid(self, text: str) -> None:
    success, result, message = execute_simple_command(text, self.session.state)
    if not success:
        # Fall through to graph
        await self._handle_graph(text)
        return

    # Update session state per ConversationSession.send() logic
    self.session.state["last_vis_params"] = result if isinstance(result, dict) else self.session.state["last_vis_params"]
    self.session.state["messages"].append(HumanMessage(content=text))
    self.session.state["messages"].append(AIMessage(content=message))

    await self._send_trace(from_="model", to="user", kind="prompt", payload=message)
    await self._send_chat({"role": "assistant", "authorName": "Model",
                           "content": message})

    # Auto-rerender if we have vis params + a known tool
    params = self.session.state.get("last_vis_params") or {}
    tool_name = params.get("_tool_name")
    if not tool_name or tool_name not in TOOL_REGISTRY:
        return  # nothing to rerender

    tool_fn = TOOL_REGISTRY[tool_name]
    call_args = {k: v for k, v in params.items() if not k.startswith("_")}

    await self._send_trace(from_="model", to="vis_tool",
                           kind="tool_call",
                           payload={"tool": tool_name, "args": call_args})
    rerun = await asyncio.to_thread(tool_fn, **call_args)
    if rerun.get("status") != "success":
        await self._send_trace(from_="vis_tool", to="model", kind="error",
                               payload=rerun.get("message", "error"))
        await self._send_chat({
            "role": "assistant", "authorName": "Vis Tool",
            "content": f"Re-render failed: {rerun.get('message', '')}"
        })
        return

    await self._send_trace(from_="vis_tool", to="model", kind="tool_result",
                           payload=truncate_payload(rerun))
    if rerun.get("_figure_path"):
        await self._send_chat({
            "role": "assistant", "authorName": "Vis Tool",
            "content": [
                {"type": "text", "text": rerun.get("message", "")},
                {"type": "image",
                 "url": figure_url(rerun["_figure_path"]),
                 "alt": tool_name},
            ],
        })
```

Helpers `_send_trace` and `_send_chat` build the envelope (adding a
`crypto.randomUUID`-style id via `uuid.uuid4().hex`) and call
`ws.send_json`.

### Task 3 — Wire into `server.py`

Modify `src/uvisbox_assistant/web/server.py`. In `ws_endpoint`,
instantiate a `SessionRunner` per connection and dispatch:

```python
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    clear_figures_dir()
    runner = SessionRunner(ws)
    try:
        while True:
            msg = await ws.receive_json()
            t = msg.get("type")
            if t == "hello":
                await ws.send_json({"type": "session_ready", "actors": ACTORS})
            elif t == "reset":
                await runner.reset()
                clear_figures_dir()
                await ws.send_json({"type": "session_ready", "actors": ACTORS})
            elif t == "prompt":
                await runner.handle_prompt(msg.get("text", ""))
            else:
                await ws.send_json({"type": "error",
                                    "message": f"unknown message type: {t}"})
    except WebSocketDisconnect:
        return
```

### Task 4 — Unit tests: `tests/unit/test_trace_translator.py`

0 LLM calls. Construct synthetic `astream_events` dicts and assert the
output envelope list matches expectations.

Cover:
- `on_chat_model_end` with a single tool call to `plot_functional_boxplot`
  produces one `tool_call` trace, `from: "model"`, `to: "vis_tool"`,
  payload contains the tool name and args.
- `on_chat_model_end` with a single tool call to a data tool (e.g.,
  `generate_curves`) produces one trace with `to: "data_tool"`.
- `on_chat_model_end` without tool calls produces one `prompt` trace and
  one chat message.
- `on_tool_end` with a result containing `_figure_path` produces one
  `tool_result` trace and one chat message with an `image` content part
  whose URL is the `/figures/<uuid>.png` form (not the absolute path).
- `on_tool_end` with `status: error` produces an `error`-kind trace
  only, no chat message.
- `truncate_payload` does not include array-shaped values, base64
  strings, or `_figure_path` (kept out of trace payloads — image goes
  in the chat envelope only).

### Task 5 — uvisbox_interface test: `tests/uvisbox_interface/test_hybrid_rerender.py`

0 LLM calls. Verifies the auto-rerender path end-to-end without going
through LangGraph.

Setup: activate `FileRenderer(tmp_path)`; create a minimal
`GraphState` whose `last_vis_params` matches what
`plot_functional_boxplot` returns (run it once on test data first to
get a realistic dict).

Test:
1. Construct a `SessionRunner` with a fake `WebSocket` (record-only
   stub that captures every `send_json` payload into a list).
2. Pre-populate `runner.session.state` from the seeded plot result.
3. `await runner.handle_prompt("median color blue")`.
4. Assert the recorded envelopes contain, in order: `busy: true`,
   `prompt` trace, user chat, `prompt`-kind trace from model
   acknowledging the hybrid update, model chat, `tool_call` trace,
   `tool_result` trace, image chat envelope, `busy: false`.
5. Assert the new `_figure_path` PNG exists on disk and the URL in the
   image chat envelope points at `/figures/<that-uuid>.png`.

### Task 6 — llm_integration test: `tests/llm_integration/test_web_session.py`

Small LLM budget (one short prompt). Uses
`fastapi.testclient.TestClient.websocket_connect`.

```python
def test_prompt_streams_events():
    with TestClient(app).websocket_connect("/ws") as ws:
        ws.send_json({"type": "hello"})
        assert ws.receive_json()["type"] == "session_ready"
        ws.send_json({"type": "prompt",
                      "text": "Generate 30 curves and plot functional boxplot"})

        kinds = []
        while True:
            msg = ws.receive_json()
            if msg["type"] == "busy" and not msg["busy"]:
                break
            if msg["type"] == "trace":
                kinds.append(msg["message"]["kind"])
            # Skip chat/error for this assertion

    assert "tool_call" in kinds
    assert "tool_result" in kinds
```

Mark with `@pytest.mark.llm` so it's excluded from `--pre-planning`.

## Verification

- **Task 1:** `python -c "from uvisbox_assistant.web.trace_translator import translate_event, TranslatorContext"` works.
- **Task 2:** `python -c "from uvisbox_assistant.web.session_runner import SessionRunner"` works.
- **Task 3:** `python -m uvisbox_assistant.web` starts. Manual smoke
  with `websocat`: send `{"type":"hello"}`, then a prompt; observe a
  stream of `busy: true`, multiple `trace` + `chat` events, then
  `busy: false`.
- **Tasks 4–5:** `pytest tests/unit/test_trace_translator.py tests/uvisbox_interface/test_hybrid_rerender.py -v` passes.
- **Task 6:** `python tests/test.py --iterative --llm-subset=smoke` runs
  the new llm_integration test and it passes.

## Validation

- Full pre-planning suite (`python tests/test.py --pre-planning`) green.
- REPL still unchanged — run a quick CLI session and produce a plot
  window.
- Manual: with a running server, use a small Python script
  (`websockets` library or `websocat`) to drive one prompt-to-image
  workflow end-to-end and confirm the image is reachable at
  `http://127.0.0.1:8000/figures/<uuid>.png`.

## Acceptance Criteria

- [ ] `trace_translator.py` translates the five event categories listed
      above; unit tests cover each.
- [ ] `session_runner.py` runs the graph in a worker thread, streams
      translated envelopes, and ends with `busy: false`.
- [ ] Hybrid commands re-render and produce a new image in the chat
      stream; `last_vis_params` is updated.
- [ ] Tool errors and graph-level errors emit `error` traces without
      tearing down the connection.
- [ ] Image chat messages reference `/figures/<uuid>.png` (relative
      URL), and that URL serves the PNG.
- [ ] `pytest tests/unit/test_trace_translator.py tests/uvisbox_interface/test_hybrid_rerender.py` passes.
- [ ] `python tests/test.py --iterative --llm-subset=smoke` passes.
- [ ] REPL unaffected: `python tests/test.py --pre-planning` passes.

## Git Commit

```
feat(web): wire ConversationSession into WebSocket prompts

Adds trace_translator and session_runner. Prompts now run the LangGraph
workflow in a worker thread, streaming translated trace + chat events
back over the WebSocket. Hybrid commands take a fast path that re-
renders the last plot directly via TOOL_REGISTRY. Errors surface as
trace events without dropping the connection.
```

Include: `src/uvisbox_assistant/web/trace_translator.py`,
`src/uvisbox_assistant/web/session_runner.py`,
`src/uvisbox_assistant/web/server.py`,
`tests/unit/test_trace_translator.py`,
`tests/uvisbox_interface/test_hybrid_rerender.py`,
`tests/llm_integration/test_web_session.py`.
