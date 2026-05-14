# ABOUTME: FastAPI app exposing a WebSocket /ws endpoint and a /figures/<id>.png static endpoint.
# ABOUTME: Dispatches each connection to a per-WS SessionRunner that drives the agent over the wire.

"""FastAPI server for the web interface (transport + per-connection SessionRunner dispatch)."""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from .figures import FIGURES_DIR, clear_figures_dir, validate_figure_filename
from .session_runner import SessionRunner

app = FastAPI()

ACTORS = [
    {"id": "user",      "label": "User",      "kind": "user"},
    {"id": "model",     "label": "Model",     "kind": "model"},
    {"id": "data_tool", "label": "Data Tool", "kind": "tool"},
    {"id": "vis_tool",  "label": "Vis Tool",  "kind": "tool"},
]


@app.get("/figures/{name}")
async def get_figure(name: str):
    """Serve a PNG from FIGURES_DIR after strict filename validation."""
    if not validate_figure_filename(name):
        raise HTTPException(status_code=400, detail="invalid figure name")
    path = FIGURES_DIR / name
    if not path.exists():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(path, media_type="image/png")


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    """Handle hello/reset/prompt over a single WebSocket via a per-connection SessionRunner."""
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
                await ws.send_json({
                    "type": "error",
                    "message": f"unknown message type: {t!r}",
                })
    except WebSocketDisconnect:
        return
