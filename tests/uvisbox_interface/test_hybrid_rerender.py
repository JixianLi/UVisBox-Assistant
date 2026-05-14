# ABOUTME: Integration tests for SessionRunner's hybrid auto-rerender path (0 LLM calls).
# ABOUTME: Exercises hybrid command -> TOOL_REGISTRY rerender -> WebSocket envelope emission with a fake WS.
"""Hybrid auto-rerender integration tests.

These tests drive ``SessionRunner._handle_hybrid`` (and ``handle_prompt`` where
no LLM is involved) directly with a capture-only stub WebSocket. They verify
that a hybrid command following a prior plot re-invokes the right tool via
:data:`TOOL_REGISTRY`, writes a PNG via the active :class:`FileRenderer`, and
emits the correct sequence of ``trace`` / ``chat`` / ``busy`` envelopes.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest

from uvisbox_assistant.core.state import create_initial_state
from uvisbox_assistant.tools.vis_tools import plot_functional_boxplot
from uvisbox_assistant.utils.renderer import (
    FileRenderer,
    current_renderer,
    set_renderer,
)
from uvisbox_assistant.web import session_runner as session_runner_module
from uvisbox_assistant.web.session_runner import SessionRunner


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


@pytest.fixture
def agg_backend():
    """Switch matplotlib to the non-interactive ``Agg`` backend for one test.

    Required because the hybrid auto-rerender path calls the plot tool from a
    worker thread (via ``asyncio.to_thread``), and the default macOS GUI
    backend cannot create figure managers off the main thread. Restored to
    the previous backend on teardown so other tests are unaffected.
    """
    previous = matplotlib.get_backend()
    plt.switch_backend("Agg")
    try:
        yield
    finally:
        plt.switch_backend(previous)


@pytest.fixture
def fake_ws():
    """A capture-only stub WebSocket. Records every ``send_json`` payload."""

    class FakeWS:
        def __init__(self):
            self.sent = []

        async def send_json(self, payload):
            self.sent.append(payload)

    return FakeWS()


@pytest.fixture
def figures_dir(tmp_path):
    """Activate :class:`FileRenderer` with ``tmp_path`` as the output dir."""
    out_dir = tmp_path / "figures"
    token = set_renderer(FileRenderer(out_dir))
    try:
        yield out_dir
    finally:
        current_renderer.reset(token)


def _curves_path(tmp_path: Path) -> str:
    """Seed a small synthetic 2D curve ensemble on disk and return its path."""
    rng = np.random.RandomState(42)
    curves = rng.randn(30, 100).cumsum(axis=1)
    path = tmp_path / "curves.npy"
    np.save(path, curves)
    return str(path)


def _seed_runner_with_plot(fake_ws, tmp_path) -> tuple:
    """Run one real ``plot_functional_boxplot`` to seed ``last_vis_params``.

    Returns ``(runner, seed_result)``.
    """
    curves_path = _curves_path(tmp_path)
    seed_result = plot_functional_boxplot(data_path=curves_path)
    assert seed_result["status"] == "success", seed_result
    runner = SessionRunner(fake_ws)
    runner.session.state = create_initial_state("seed")
    runner.session.state["last_vis_params"] = seed_result["_vis_params"]
    return runner, seed_result


def _filter(sent, type_):
    return [e for e in sent if e.get("type") == type_]


def _traces(sent):
    return _filter(sent, "trace")


def _chats(sent):
    return _filter(sent, "chat")


def test_hybrid_rerender_emits_expected_envelopes_and_writes_png(
    fake_ws, figures_dir, tmp_path, agg_backend,
):
    """Hybrid command after a prior plot must rerender and emit a full envelope sequence."""
    runner, _ = _seed_runner_with_plot(fake_ws, tmp_path)

    asyncio.run(runner.handle_prompt("median color blue"))

    sent = fake_ws.sent
    assert len(sent) >= 2, sent

    # busy:true first, busy:false last
    assert sent[0] == {"type": "busy", "busy": True}
    assert sent[-1] == {"type": "busy", "busy": False}

    traces = _traces(sent)
    chats = _chats(sent)

    # Identify the key envelopes by kind / role / payload.
    user_chat = next(
        c for c in chats if c["message"].get("role") == "user"
    )
    assert user_chat["message"]["content"] == "median color blue"

    user_prompt_trace = next(
        t for t in traces
        if t["message"]["from"] == "user" and t["message"]["to"] == "model"
        and t["message"]["kind"] == "prompt"
    )
    assert user_prompt_trace["message"]["payload"] == "median color blue"

    # Hybrid acknowledgement: model->user prompt trace + Model assistant chat.
    model_ack_trace = next(
        t for t in traces
        if t["message"]["from"] == "model" and t["message"]["to"] == "user"
        and t["message"]["kind"] == "prompt"
    )
    assert "median_color" in model_ack_trace["message"]["payload"]
    model_ack_chat = next(
        c for c in chats
        if c["message"].get("role") == "assistant"
        and c["message"].get("authorName") == "Model"
    )
    assert isinstance(model_ack_chat["message"]["content"], str)

    # model -> vis_tool tool_call trace.
    tool_call_trace = next(
        t for t in traces
        if t["message"]["from"] == "model"
        and t["message"]["to"] == "vis_tool"
        and t["message"]["kind"] == "tool_call"
    )
    payload = tool_call_trace["message"]["payload"]
    assert payload["tool"] == "plot_functional_boxplot"
    assert payload["args"]["median_color"] == "blue"

    # vis_tool -> model tool_result trace.
    tool_result_trace = next(
        t for t in traces
        if t["message"]["from"] == "vis_tool"
        and t["message"]["to"] == "model"
        and t["message"]["kind"] == "tool_result"
    )
    assert tool_result_trace["message"]["payload"]["status"] == "success"

    # Vis Tool assistant chat with image content.
    image_chat = next(
        c for c in chats
        if c["message"].get("role") == "assistant"
        and c["message"].get("authorName") == "Vis Tool"
    )
    content = image_chat["message"]["content"]
    assert isinstance(content, list)
    image_part = next(p for p in content if p.get("type") == "image")
    assert image_part["url"].startswith("/figures/")
    text_part = next(p for p in content if p.get("type") == "text")
    assert isinstance(text_part["text"], str)

    # Relative ordering invariants.
    idx_busy_true = sent.index({"type": "busy", "busy": True})
    idx_busy_false = sent.index({"type": "busy", "busy": False})
    idx_tool_call = sent.index(tool_call_trace)
    idx_tool_result = sent.index(tool_result_trace)
    idx_image_chat = sent.index(image_chat)
    assert idx_busy_true < idx_tool_call < idx_tool_result < idx_image_chat < idx_busy_false

    # PNG file actually written on disk under figures_dir.
    url = image_part["url"]
    filename = url.rsplit("/", 1)[-1]
    png_path = figures_dir / filename
    assert png_path.exists(), f"PNG file not on disk: {png_path}"
    with open(png_path, "rb") as f:
        head = f.read(len(PNG_MAGIC))
    assert head == PNG_MAGIC, f"File is not a PNG: {png_path}"

    # State updated.
    assert runner.session.state["last_vis_params"]["median_color"] == "blue"


def test_hybrid_without_prior_plot_skips_rerender(fake_ws, figures_dir):
    """With no ``last_vis_params``, ``_handle_hybrid`` must fall through (return False) without rerendering.

    ``execute_simple_command`` returns ``(False, ...)`` when ``last_vis_params``
    is missing, so ``_handle_hybrid`` returns False -- meaning the hybrid
    layer did not claim the prompt. The runner would then call the graph,
    which we avoid by invoking ``_handle_hybrid`` directly here (no LLM).
    """
    runner = SessionRunner(fake_ws)
    runner.session.state = create_initial_state("seed")
    # Note: create_initial_state already sets last_vis_params=None.

    claimed = asyncio.run(runner._handle_hybrid("median color blue"))

    assert claimed is False, "Hybrid layer should fall through when no prior plot exists"
    # No envelopes emitted: hybrid bailed before sending anything.
    assert fake_ws.sent == [], fake_ws.sent


def test_hybrid_rerender_failure_emits_error(
    fake_ws, figures_dir, tmp_path, monkeypatch, agg_backend,
):
    """Tool failure during auto-rerender surfaces as an ``error`` trace + chat, not ``tool_result``.

    Strategy: seed with a real successful plot so ``execute_simple_command``
    (which does its own tool pre-run) succeeds. Then monkeypatch
    ``session_runner.TOOL_REGISTRY`` so the runner's auto-rerender call hits
    a stub that returns ``{"status": "error", ...}`` -- exercising the failure
    branch of ``_handle_hybrid`` without LLM involvement.
    """
    runner, _ = _seed_runner_with_plot(fake_ws, tmp_path)

    def failing_tool(**kwargs):
        return {"status": "error", "message": "synthetic rerender failure"}

    patched_registry = dict(session_runner_module.TOOL_REGISTRY)
    patched_registry["plot_functional_boxplot"] = failing_tool
    monkeypatch.setattr(session_runner_module, "TOOL_REGISTRY", patched_registry)

    asyncio.run(runner.handle_prompt("median color blue"))

    sent = fake_ws.sent
    assert sent[0] == {"type": "busy", "busy": True}
    assert sent[-1] == {"type": "busy", "busy": False}

    traces = _traces(sent)
    chats = _chats(sent)

    # Model acknowledgement trace + chat (from the hybrid layer) still happen.
    model_ack_trace = next(
        t for t in traces
        if t["message"]["from"] == "model" and t["message"]["to"] == "user"
        and t["message"]["kind"] == "prompt"
    )
    assert "median_color" in model_ack_trace["message"]["payload"]
    model_ack_chat = next(
        c for c in chats
        if c["message"].get("role") == "assistant"
        and c["message"].get("authorName") == "Model"
    )
    assert isinstance(model_ack_chat["message"]["content"], str)

    # tool_call trace IS emitted (the runner attempts the rerender).
    tool_call_trace = next(
        t for t in traces
        if t["message"]["from"] == "model"
        and t["message"]["to"] == "vis_tool"
        and t["message"]["kind"] == "tool_call"
    )
    assert tool_call_trace["message"]["payload"]["tool"] == "plot_functional_boxplot"

    # vis_tool -> model error trace IS emitted; tool_result is NOT.
    error_trace = next(
        t for t in traces
        if t["message"]["from"] == "vis_tool"
        and t["message"]["to"] == "model"
        and t["message"]["kind"] == "error"
    )
    assert "synthetic rerender failure" in error_trace["message"]["payload"]
    assert not [t for t in traces
                if t["message"]["from"] == "vis_tool"
                and t["message"]["kind"] == "tool_result"]

    # Re-render failure chat from Vis Tool.
    failure_chat = next(
        c for c in chats
        if c["message"].get("role") == "assistant"
        and c["message"].get("authorName") == "Vis Tool"
    )
    assert "Re-render failed" in failure_chat["message"]["content"]

    # Ordering: tool_call before error trace; error trace before busy:false.
    idx_tool_call = sent.index(tool_call_trace)
    idx_error = sent.index(error_trace)
    idx_busy_false = sent.index({"type": "busy", "busy": False})
    assert idx_tool_call < idx_error < idx_busy_false

    # State was updated with the hybrid command's params before the rerender
    # was attempted. ``_handle_hybrid`` mutates ``last_vis_params`` first via
    # ``execute_simple_command``'s output then calls the tool again; even on
    # rerender failure the stored color is the new "blue".
    assert runner.session.state["last_vis_params"]["median_color"] == "blue"
