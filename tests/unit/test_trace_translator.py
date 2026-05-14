# ABOUTME: Unit tests for trace_translator (astream_events -> wire envelopes).
# ABOUTME: Uses captured astream_events fixtures plus synthetic events; no LLM calls.
"""Tests for ``uvisbox_assistant.web.trace_translator``.

Fixtures in ``tests/unit/fixtures/astream_events_sample.json`` were captured
from a real graph run on 2026-05-14 driving the prompt
"Generate 30 curves and plot functional boxplot" with ``FileRenderer`` active
and the matplotlib ``Agg`` backend. Event format follows the LangGraph v2
``astream_events`` schema.

Note: the running graph emits ``on_chain_end`` events for tool nodes rather
than ``on_tool_end``. The translator supports both shapes; synthetic-event
tests below exercise the ``on_tool_end`` path explicitly as required by the
phase plan, while ``test_full_sequence_from_fixture`` exercises the real
``on_chain_end`` path end-to-end.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from uvisbox_assistant.web.trace_translator import (
    TranslatorContext,
    figure_url,
    translate_event,
    truncate_payload,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "astream_events_sample.json"


# ---------------------------------------------------------------------------
# Synthetic-event tests
# ---------------------------------------------------------------------------


def _chat_model_end_with_tool_call(tool_name: str, args: dict) -> dict:
    """Build a synthetic on_chat_model_end event with one tool call."""
    return {
        "event": "on_chat_model_end",
        "name": "ChatOllama",
        "data": {
            "output": {
                "content": "",
                "tool_calls": [
                    {"name": tool_name, "args": args, "id": "call_1", "type": "tool_call"}
                ],
            }
        },
    }


def _chat_model_end_text(text: str) -> dict:
    """Build a synthetic on_chat_model_end event with text content only."""
    return {
        "event": "on_chat_model_end",
        "name": "ChatOllama",
        "data": {"output": {"content": text, "tool_calls": []}},
    }


def _tool_end(output: dict, tool_name: str = "") -> dict:
    """Build a synthetic on_tool_end event."""
    return {
        "event": "on_tool_end",
        "name": tool_name,
        "data": {"output": output},
    }


def test_chat_model_end_with_tool_call_emits_trace():
    event = _chat_model_end_with_tool_call(
        "plot_functional_boxplot",
        {"data_path": "/tmp/foo.npy", "percentiles": [25, 50, 90, 100]},
    )
    ctx = TranslatorContext()

    envelopes = translate_event(event, ctx)

    assert len(envelopes) == 1
    env = envelopes[0]
    assert env["type"] == "trace"
    msg = env["message"]
    assert msg["from"] == "model"
    assert msg["to"] == "vis_tool"
    assert msg["kind"] == "tool_call"
    assert msg["payload"]["tool"] == "plot_functional_boxplot"
    assert msg["payload"]["args"]["data_path"] == "/tmp/foo.npy"
    assert msg["payload"]["args"]["percentiles"] == [25, 50, 90, 100]
    assert isinstance(msg["id"], str) and len(msg["id"]) == 32


def test_chat_model_end_with_data_tool_call_emits_trace():
    event = _chat_model_end_with_tool_call(
        "generate_ensemble_curves",
        {"n_curves": 30, "n_points": 100},
    )
    ctx = TranslatorContext()

    envelopes = translate_event(event, ctx)

    assert len(envelopes) == 1
    msg = envelopes[0]["message"]
    assert msg["from"] == "model"
    assert msg["to"] == "data_tool"
    assert msg["kind"] == "tool_call"
    assert msg["payload"]["tool"] == "generate_ensemble_curves"


def test_chat_model_end_text_only_emits_prompt_and_chat():
    event = _chat_model_end_text("Here is your plot. Let me know if anything looks off.")
    ctx = TranslatorContext()

    envelopes = translate_event(event, ctx)

    assert len(envelopes) == 2
    trace_env, chat_env = envelopes
    assert trace_env["type"] == "trace"
    assert trace_env["message"]["from"] == "model"
    assert trace_env["message"]["to"] == "user"
    assert trace_env["message"]["kind"] == "prompt"
    assert trace_env["message"]["payload"] == \
        "Here is your plot. Let me know if anything looks off."

    assert chat_env["type"] == "chat"
    cm = chat_env["message"]
    assert cm["role"] == "assistant"
    assert cm["authorName"] == "Model"
    assert cm["content"] == "Here is your plot. Let me know if anything looks off."


def test_tool_end_success_with_figure_path_emits_trace_and_image_chat():
    result = {
        "status": "success",
        "message": "plotted",
        "_vis_params": {"_tool_name": "plot_functional_boxplot"},
        "_figure_path": (
            "/Users/foo/projects/uvisbox-assistant/tmp_dev/web_figures/"
            "abcdef0123456789abcdef0123456789.png"
        ),
    }
    event = _tool_end(result, tool_name="plot_functional_boxplot")
    ctx = TranslatorContext(last_seen_node="vis_tool")

    envelopes = translate_event(event, ctx)

    assert len(envelopes) == 2
    trace_env, chat_env = envelopes

    assert trace_env["type"] == "trace"
    tm = trace_env["message"]
    assert tm["from"] == "vis_tool"
    assert tm["to"] == "model"
    assert tm["kind"] == "tool_result"
    assert tm["payload"] == {"status": "success", "message": "plotted"}

    assert chat_env["type"] == "chat"
    cm = chat_env["message"]
    assert cm["role"] == "assistant"
    assert cm["authorName"] == "Vis Tool"
    assert isinstance(cm["content"], list)
    assert len(cm["content"]) == 2
    text_part, image_part = cm["content"]
    assert text_part == {"type": "text", "text": "plotted"}
    assert image_part["type"] == "image"
    assert image_part["url"] == \
        "/figures/abcdef0123456789abcdef0123456789.png"
    assert image_part["alt"] == "plot_functional_boxplot"


def test_tool_end_success_no_figure_path_emits_trace_only():
    result = {
        "status": "success",
        "output_path": "/tmp/foo.npy",
        "message": "Generated 30 curves",
    }
    event = _tool_end(result, tool_name="generate_ensemble_curves")
    ctx = TranslatorContext(last_seen_node="data_tool")

    envelopes = translate_event(event, ctx)

    assert len(envelopes) == 1
    env = envelopes[0]
    assert env["type"] == "trace"
    assert env["message"]["kind"] == "tool_result"
    assert env["message"]["from"] == "data_tool"
    assert env["message"]["payload"] == {
        "status": "success",
        "message": "Generated 30 curves",
    }


def test_tool_end_error_emits_error_trace():
    result = {"status": "error", "message": "file not found"}
    event = _tool_end(result, tool_name="load_npy")
    ctx = TranslatorContext(last_seen_node="data_tool")

    envelopes = translate_event(event, ctx)

    assert len(envelopes) == 1
    env = envelopes[0]
    assert env["type"] == "trace"
    tm = env["message"]
    assert tm["from"] == "data_tool"
    assert tm["to"] == "model"
    assert tm["kind"] == "error"
    assert tm["payload"] == "file not found"


def test_chain_start_updates_last_seen_node():
    ctx = TranslatorContext()
    events = [
        {"event": "on_chain_start", "name": "model", "data": {}},
        {"event": "on_chain_start", "name": "vis_tool", "data": {}},
        {"event": "on_chain_start", "name": "data_tool", "data": {}},
    ]

    out: list = []
    for ev in events:
        out.extend(translate_event(ev, ctx))

    assert out == []
    assert ctx.last_seen_node == "data_tool"


def test_chain_end_captures_final_state():
    final_state = {
        "messages": [],
        "current_data_path": "/tmp/foo.npy",
        "last_vis_params": None,
        "session_files": [],
        "error_count": 0,
    }
    event = {
        "event": "on_chain_end",
        "name": "LangGraph",
        "data": {"output": final_state},
    }
    ctx = TranslatorContext()

    envelopes = translate_event(event, ctx)

    assert envelopes == []
    assert ctx.final_state == final_state


def test_truncate_payload_drops_figure_path():
    result = {
        "status": "success",
        "message": "ok",
        "_figure_path": "/abs/tmp_dev/web_figures/deadbeef.png",
        "_vis_params": {"_tool_name": "plot_functional_boxplot"},
    }
    out = truncate_payload(result)

    assert out == {"status": "success", "message": "ok"}
    assert "_figure_path" in result  # input unchanged
    assert "_vis_params" in result


def test_truncate_payload_truncates_long_strings():
    long_msg = "x" * 500
    result = {"status": "success", "message": long_msg}

    out = truncate_payload(result)

    assert len(out["message"]) < 500
    assert out["message"].startswith("x")
    assert out["message"].endswith("[truncated]")
    assert out["status"] == "success"


def test_figure_url_translates_path():
    p = "/Users/foo/projects/uvisbox-assistant/tmp_dev/web_figures/abcdef.png"
    assert figure_url(p) == "/figures/abcdef.png"

    # Deeper ancestry
    deep = "/a/b/c/d/e/tmp_dev/web_figures/cafebabe.png"
    assert figure_url(deep) == "/figures/cafebabe.png"

    # Fallback: no web_figures segment
    other = "/some/where/file.png"
    assert figure_url(other) == "/figures/file.png"


# ---------------------------------------------------------------------------
# Fixture-driven end-to-end test
# ---------------------------------------------------------------------------


@pytest.fixture
def captured_events():
    """Load real astream_events captured from a graph run."""
    if not FIXTURE_PATH.exists():
        pytest.skip(f"fixture not present: {FIXTURE_PATH}")
    return json.loads(FIXTURE_PATH.read_text())


def test_full_sequence_from_fixture(captured_events):
    """Replay captured events through the translator and sanity-check outputs."""
    ctx = TranslatorContext()
    envelopes: list = []
    for ev in captured_events:
        envelopes.extend(translate_event(ev, ctx))

    trace_msgs = [e["message"] for e in envelopes if e["type"] == "trace"]
    chat_msgs = [e["message"] for e in envelopes if e["type"] == "chat"]
    kinds = [m["kind"] for m in trace_msgs]

    # The prompt generated curves and a plot, so we expect both tool calls
    # and tool results.
    assert "tool_call" in kinds
    assert "tool_result" in kinds

    # The graph eventually produces a final assistant text response.
    assert "prompt" in kinds
    assert any(m["role"] == "assistant" and isinstance(m["content"], str)
               for m in chat_msgs)

    # Final state captured from the root on_chain_end.
    assert ctx.final_state is not None
    assert "current_data_path" in ctx.final_state

    # Every envelope carries a unique id.
    all_ids = [e["message"]["id"] for e in envelopes]
    assert len(set(all_ids)) == len(all_ids)
