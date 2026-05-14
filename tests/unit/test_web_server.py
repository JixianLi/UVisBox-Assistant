# ABOUTME: Unit tests for src/uvisbox_assistant/web/server.py
# ABOUTME: Exercises WebSocket /ws handshake and the /figures/<name> endpoint (0 LLM calls).

import pytest
from fastapi.testclient import TestClient

from uvisbox_assistant.web import figures as figures_module
from uvisbox_assistant.web import server as server_module
from uvisbox_assistant.web.server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_ws_hello_returns_session_ready(client):
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "hello"})
        msg = ws.receive_json()

    assert msg["type"] == "session_ready"
    assert len(msg["actors"]) == 4
    assert {a["id"] for a in msg["actors"]} == {"user", "model", "data_tool", "vis_tool"}


def test_ws_reset_replies_session_ready(client):
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "hello"})
        ws.receive_json()  # session_ready from hello
        ws.send_json({"type": "reset"})
        msg = ws.receive_json()

    assert msg["type"] == "session_ready"
    assert len(msg["actors"]) == 4
    assert {a["id"] for a in msg["actors"]} == {"user", "model", "data_tool", "vis_tool"}


def test_ws_unknown_type_returns_error(client):
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "nonsense"})
        msg = ws.receive_json()

    assert msg["type"] == "error"
    assert isinstance(msg["message"], str)
    assert "nonsense" in msg["message"]


def test_figures_endpoint_404_on_missing(client):
    # Vanishingly unlikely to collide with any real file.
    resp = client.get("/figures/00000000000000000000000000000000.png")
    assert resp.status_code == 404


@pytest.mark.parametrize(
    "name",
    [
        "foo.png",
        "ABC.png",
        "0123456789abcdef0123456789abcdef.jpg",
    ],
)
def test_figures_endpoint_400_on_bad_name(client, name):
    resp = client.get(f"/figures/{name}")
    assert resp.status_code == 400


def test_figures_endpoint_path_traversal_blocked(client):
    # Starlette/httpx normalizes "../" in the URL path before it reaches the
    # endpoint, so the request typically never hits validate_figure_filename
    # and comes back as 404 (route not matched) or 405. The contract we care
    # about is "no file is served". Accept 400/404/405 here.
    resp = client.get("/figures/../etc/passwd")
    assert resp.status_code in (400, 404, 405)


def test_figures_endpoint_200_on_valid_existing(client, tmp_path, monkeypatch):
    # server.py did `from .figures import FIGURES_DIR`, so both modules hold
    # the binding. The endpoint reads from server_module.FIGURES_DIR; patch
    # both to be safe.
    monkeypatch.setattr(figures_module, "FIGURES_DIR", tmp_path)
    monkeypatch.setattr(server_module, "FIGURES_DIR", tmp_path)

    name = "0123456789abcdef0123456789abcdef.png"
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
    (tmp_path / name).write_bytes(png_bytes)

    resp = client.get(f"/figures/{name}")

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    assert resp.content == png_bytes
