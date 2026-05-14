# ABOUTME: Single-LLM-call llm_integration test for the web WebSocket session lifecycle.
# ABOUTME: Drives /ws end-to-end via TestClient: hello -> prompt -> drain envelopes until busy:false.
"""Web WebSocket session smoke test (one LLM call).

Drives the FastAPI ``/ws`` endpoint synchronously through
:class:`fastapi.testclient.TestClient` and verifies the broad shape of the
envelope stream produced by one short prompt: a leading ``busy:true``, at
least one ``tool_call`` and ``tool_result`` trace, at least one ``chat``
envelope, and a trailing ``busy:false``. The test does not pin LLM output
text -- only the structural invariants of the wire protocol.
"""

from __future__ import annotations

import time

import matplotlib
import matplotlib.pyplot as plt
import pytest
from fastapi.testclient import TestClient

from uvisbox_assistant.utils.renderer import (
    FileRenderer,
    current_renderer,
    set_renderer,
)
from uvisbox_assistant.web.server import app


VALID_ACTORS = {"user", "model", "data_tool", "vis_tool"}


@pytest.fixture
def figures_dir(tmp_path):
    """Activate :class:`FileRenderer` against ``tmp_path`` so the test does not
    write into the real ``tmp_dev/web_figures/`` directory.
    """
    out_dir = tmp_path / "figures"
    token = set_renderer(FileRenderer(out_dir))
    try:
        yield out_dir
    finally:
        current_renderer.reset(token)


@pytest.fixture
def agg_backend():
    """Switch matplotlib to ``Agg`` for the duration of the test.

    Plot tools run on a worker thread driven by ``astream_events``; the macOS
    GUI backend cannot create figure managers off the main thread.
    """
    previous = matplotlib.get_backend()
    plt.switch_backend("Agg")
    try:
        yield
    finally:
        plt.switch_backend(previous)


@pytest.mark.smoke
def test_prompt_streams_full_event_sequence(figures_dir, agg_backend):
    """One short prompt produces a structurally well-formed envelope stream.

    Sends a single prompt over ``/ws`` and drains until ``busy:false``. Asserts
    only broad-shape invariants (envelope ordering, presence of tool_call and
    tool_result traces, valid actor names) rather than any LLM-generated text.
    """
    with TestClient(app).websocket_connect("/ws") as ws:
        # Handshake.
        ws.send_json({"type": "hello"})
        ready = ws.receive_json()
        assert ready["type"] == "session_ready", ready

        # One short prompt. We DO NOT pin specific text from the LLM response;
        # only the shape of the resulting stream.
        ws.send_json({
            "type": "prompt",
            "text": "Generate 30 curves and plot functional boxplot",
        })

        envelopes: list[dict] = []
        deadline = time.monotonic() + 120
        while True:
            if time.monotonic() > deadline:
                pytest.fail(
                    f"timeout draining envelopes after 120s; "
                    f"last 10: {envelopes[-10:]}"
                )
            env = ws.receive_json()
            envelopes.append(env)
            if env.get("type") == "busy" and env.get("busy") is False:
                break
            if len(envelopes) > 200:
                pytest.fail(
                    f"received more than 200 envelopes; "
                    f"last 10: {envelopes[-10:]}"
                )

    # First envelope after the prompt is busy:true.
    assert envelopes[0] == {"type": "busy", "busy": True}, envelopes[:3]
    # Last envelope is busy:false (loop terminator).
    assert envelopes[-1] == {"type": "busy", "busy": False}, envelopes[-3:]

    traces = [e for e in envelopes if e.get("type") == "trace"]
    chats = [e for e in envelopes if e.get("type") == "chat"]

    # The LLM must have produced at least one tool call and one tool result.
    tool_calls = [t for t in traces if t["message"].get("kind") == "tool_call"]
    tool_results = [t for t in traces if t["message"].get("kind") == "tool_result"]
    assert tool_calls, (
        "expected at least one tool_call trace (LLM didn't request a tool); "
        f"saw kinds: {[t['message'].get('kind') for t in traces]}"
    )
    assert tool_results, (
        "expected at least one tool_result trace (no tool ran successfully); "
        f"saw kinds: {[t['message'].get('kind') for t in traces]}"
    )

    # At least one chat envelope (the user echo, plus assistant messages).
    assert chats, f"expected at least one chat envelope; envelopes: {envelopes}"

    # Every trace's from/to fields are valid actor ids.
    for t in traces:
        msg = t["message"]
        assert msg["from"] in VALID_ACTORS, msg
        assert msg["to"] in VALID_ACTORS, msg

    # Every tool_call trace payload carries tool + args.
    for tc in tool_calls:
        payload = tc["message"]["payload"]
        assert isinstance(payload, dict), tc
        assert "tool" in payload, tc
        assert "args" in payload, tc

    # Ordering: at least one tool_call precedes at least one tool_result.
    first_tool_call_idx = envelopes.index(tool_calls[0])
    first_tool_result_idx = envelopes.index(tool_results[0])
    assert first_tool_call_idx < first_tool_result_idx, (
        f"tool_call must precede tool_result; "
        f"got tool_call idx={first_tool_call_idx}, "
        f"tool_result idx={first_tool_result_idx}"
    )

    # Soft-assert: an image chat (content as a list including an image part)
    # is desirable but small LLMs can be flaky -- only warn, don't fail.
    image_chats = [
        c for c in chats
        if isinstance(c["message"].get("content"), list)
        and any(
            isinstance(p, dict) and p.get("type") == "image"
            for p in c["message"]["content"]
        )
    ]
    if not image_chats:
        print(
            "WARNING: no image chat envelope appeared in the stream; "
            "LLM may not have driven the workflow all the way to a plot."
        )

    # Diagnostic print to help future investigators read the stream shape.
    print(
        f"DIAG: envelopes={len(envelopes)} traces={len(traces)} "
        f"chats={len(chats)} tool_calls={len(tool_calls)} "
        f"tool_results={len(tool_results)} image_chats={len(image_chats)}"
    )
    print(
        f"DIAG: first 5 trace kinds = "
        f"{[t['message'].get('kind') for t in traces[:5]]}"
    )
