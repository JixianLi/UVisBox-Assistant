# Phase 02 — Web Server Skeleton (Transport Only)

## Scope

Add a FastAPI server that handles WebSocket `hello`/`reset` and serves
PNGs from `tmp_dev/web_figures/`. No agent integration yet — this phase
proves the transport and the `FileRenderer` wiring in isolation. After
this phase, `python -m uvisbox_assistant.web` launches a server that
accepts a WebSocket connection, replies to `hello` with `session_ready`,
and serves PNG files written manually to the figures directory.

## Implementation

### Task 1 — Add runtime dependencies

Edit `pyproject.toml`. Add to the **main** dependencies (not dev):

```toml
fastapi = "^0.115"
uvicorn = { extras = ["standard"], version = "^0.32" }
websockets = "^13"
```

Run `poetry lock` and `poetry install` after editing. Verify with
`python -c "import fastapi, uvicorn, websockets"`.

### Task 2 — Create `src/uvisbox_assistant/web/figures.py`

New file. Two pieces:

- `FIGURES_DIR: Path` constant pointing to `tmp_dev/web_figures/`
  (resolve from project root via the existing `config.TEMP_DIR` or
  similar — match what `config.py` already exposes).
- `clear_figures_dir()` — delete every file under `FIGURES_DIR`, then
  `mkdir(parents=True, exist_ok=True)`. Tolerate missing directory.
- `validate_figure_filename(name: str) -> bool` — accept only
  `^[0-9a-f]{32}\.png$` (UUID hex + `.png`). Rejects any name with
  separators, leading dots, traversal sequences, or other extensions.

### Task 3 — Create `src/uvisbox_assistant/web/server.py`

New file. Defines the FastAPI app and its endpoints. Skeleton:

```python
# ABOUTME: ...

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from .figures import FIGURES_DIR, validate_figure_filename, clear_figures_dir

app = FastAPI()

ACTORS = [
    {"id": "user", "label": "User", "kind": "user"},
    {"id": "model", "label": "Model", "kind": "model"},
    {"id": "data_tool", "label": "Data Tool", "kind": "tool"},
    {"id": "vis_tool", "label": "Vis Tool", "kind": "tool"},
]

@app.get("/figures/{name}")
async def get_figure(name: str):
    if not validate_figure_filename(name):
        raise HTTPException(status_code=400, detail="invalid figure name")
    path = FIGURES_DIR / name
    if not path.exists():
        raise HTTPException(status_code=404)
    return FileResponse(path, media_type="image/png")

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    clear_figures_dir()
    try:
        while True:
            msg = await ws.receive_json()
            t = msg.get("type")
            if t == "hello":
                await ws.send_json({"type": "session_ready", "actors": ACTORS})
            elif t == "reset":
                clear_figures_dir()
                await ws.send_json({"type": "session_ready", "actors": ACTORS})
            elif t == "prompt":
                # Phase 03 wires real prompt handling. For now, NACK.
                await ws.send_json({
                    "type": "error",
                    "message": "prompt handling not yet implemented",
                })
            else:
                await ws.send_json({
                    "type": "error",
                    "message": f"unknown message type: {t}",
                })
    except WebSocketDisconnect:
        return
```

Notes:
- The server intentionally does NOT yet hold a `ConversationSession`.
  That comes in Phase 03.
- `clear_figures_dir()` runs on every connection accept and on `reset`
  to ensure a clean state.

### Task 4 — Create `src/uvisbox_assistant/web/__main__.py`

New file. Sets the renderer contextvar to `FileRenderer` **before**
importing anything that might construct tools/graph, then runs uvicorn.

```python
# ABOUTME: ...

from pathlib import Path
from uvisbox_assistant.utils.renderer import current_renderer, FileRenderer
from .figures import FIGURES_DIR

def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    current_renderer.set(FileRenderer(FIGURES_DIR))

    import uvicorn
    from .server import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    main()
```

Bind 127.0.0.1 explicitly — never 0.0.0.0. No auth, localhost-only.

### Task 5 — Create `src/uvisbox_assistant/web/__init__.py`

Empty file (package marker). Add the standard `ABOUTME:` two-line
header.

### Task 6 — Unit tests: `tests/unit/test_figures.py`

New file. Cover:

- `validate_figure_filename("abc123def456...".ljust(32, "0") + ".png")`
  returns True for a 32-hex string plus `.png`.
- `validate_figure_filename("../etc/passwd")` returns False.
- `validate_figure_filename("foo.png")` returns False (not hex/wrong
  length).
- `validate_figure_filename("abc.png.exe")` returns False.
- `validate_figure_filename("ABC...PNG")` — accept lowercase only or
  both. Pick lowercase-only; document in the function's docstring.
- `clear_figures_dir()` deletes existing PNGs but leaves the directory.

### Task 7 — Unit tests: `tests/unit/test_web_server.py`

New file. Uses `fastapi.testclient.TestClient`.

- **Handshake test:** `with TestClient(app).websocket_connect("/ws") as ws:`
  Send `{"type": "hello"}`. Receive must be `{"type": "session_ready", "actors": [...]}` with the four expected actor IDs.
- **Reset test:** Inside the same connection, send `{"type": "reset"}`.
  Receive `session_ready` again.
- **Unknown type test:** Send `{"type": "nonsense"}`. Receive an `error`
  message naming the type.
- **Prompt NACK test:** Send `{"type": "prompt", "text": "hi"}`.
  Receive an `error` message (Phase 03 replaces this).
- **Figures 404:** `client.get("/figures/0123456789abcdef0123456789abcdef.png")`
  → 404 (file doesn't exist).
- **Figures 400 (invalid name):** `client.get("/figures/../etc/passwd")`
  → 400.
- **Figures 200:** Write a tiny valid PNG to
  `FIGURES_DIR / "<uuid>.png"`, then `client.get(...)` → 200 with
  `content-type: image/png` and the file bytes.

## Verification

- **Tasks 1–2:** `python -c "from uvisbox_assistant.web.figures import FIGURES_DIR, validate_figure_filename, clear_figures_dir"` runs cleanly.
- **Task 3:** `python -c "from uvisbox_assistant.web.server import app"` imports without error.
- **Task 4:** `python -m uvisbox_assistant.web` starts uvicorn on
  `127.0.0.1:8000`. Verify by visiting
  `http://127.0.0.1:8000/figures/nonexistent.png` and getting a 400 (the
  name fails validation). Stop the server with Ctrl-C.
- **Task 4 (renderer activation):** Inside `__main__.py` (or via a small
  REPL script), after `current_renderer.set(FileRenderer(...))`, calling
  a plot tool from `vis_tools.py` writes a PNG to `tmp_dev/web_figures/`
  with `_figure_path` populated in the result. This re-validates Phase
  01's wiring in the web-mode context.
- **Tasks 6–7:** `pytest tests/unit/test_figures.py tests/unit/test_web_server.py -v` passes.

## Validation

- Manual WebSocket smoke with `websocat` (or any WS client):
  ```bash
  websocat ws://127.0.0.1:8000/ws
  > {"type":"hello"}
  < {"type":"session_ready","actors":[...]}
  > {"type":"reset"}
  < {"type":"session_ready","actors":[...]}
  > {"type":"prompt","text":"hello"}
  < {"type":"error","message":"prompt handling not yet implemented"}
  ```
- REPL still works unchanged.
- `python tests/test.py --pre-planning` passes.

## Acceptance Criteria

- [ ] `pyproject.toml` lists `fastapi`, `uvicorn[standard]`,
      `websockets` as main dependencies; `poetry install` succeeds.
- [ ] `src/uvisbox_assistant/web/{__init__,__main__,server,figures}.py`
      all exist with `ABOUTME:` headers.
- [ ] `python -m uvisbox_assistant.web` starts uvicorn on
      `127.0.0.1:8000`.
- [ ] WebSocket handshake (`hello`/`reset`) returns `session_ready`
      with four actors.
- [ ] Prompt messages return an explicit `error` (Phase 03 replaces
      this).
- [ ] `/figures/<id>.png` enforces filename validation (400 on bad
      names, 404 on missing, 200 on a valid existing file).
- [ ] `tests/unit/test_figures.py` and
      `tests/unit/test_web_server.py` pass.
- [ ] REPL unchanged: `python tests/test.py --pre-planning` passes.

## Git Commit

```
feat(web): add FastAPI server skeleton with WS handshake + figures

Introduces src/uvisbox_assistant/web/ with a FastAPI app exposing /ws
(handles hello/reset, NACKs prompts pending Phase 03) and a /figures
endpoint with strict filename validation. __main__.py activates
FileRenderer before launching uvicorn so plot tools save PNGs to disk
in web mode.
```

Include: `pyproject.toml`, `poetry.lock`,
`src/uvisbox_assistant/web/__init__.py`,
`src/uvisbox_assistant/web/__main__.py`,
`src/uvisbox_assistant/web/server.py`,
`src/uvisbox_assistant/web/figures.py`,
`tests/unit/test_figures.py`,
`tests/unit/test_web_server.py`.
