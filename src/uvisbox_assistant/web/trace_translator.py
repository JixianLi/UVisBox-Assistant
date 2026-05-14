# ABOUTME: Translates LangGraph astream_events into wire-format trace + chat envelopes.
# ABOUTME: Pure functional; the caller threads a TranslatorContext through one stream iteration.
"""Convert LangGraph ``astream_events`` events into WebSocket trace/chat envelopes.

The translator is pure: each call takes one event dict plus a mutable
``TranslatorContext`` and returns zero or more envelope dicts of the form
``{"type": "trace"|"chat", "message": {...}}``. The session runner is responsible
for sending those envelopes over the WebSocket; this module performs no I/O.

Mapping rules are documented in ``docs/plans/web-interface/phase-03.md``.
"""
from __future__ import annotations

import ast
import uuid
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Dict, List, Optional

from uvisbox_assistant.tools.vis_tools import TOOL_REGISTRY

# Node names emitted by ``src/uvisbox_assistant/core/graph.py``.
_TOOL_NODES = ("data_tool", "vis_tool")
_TRACKED_NODES = ("data_tool", "vis_tool", "model")

# Mapping from actor id to the human label used for ChatMessage.authorName.
_ACTOR_LABELS: Dict[str, str] = {
    "user": "User",
    "model": "Model",
    "data_tool": "Data Tool",
    "vis_tool": "Vis Tool",
}

# Trim long strings in trace payloads to keep WebSocket frames small.
_MAX_TRACE_STRING_LEN = 200
_TRUNCATION_SUFFIX = "... [truncated]"


@dataclass
class TranslatorContext:
    """State carried across one ``astream_events`` iteration.

    ``last_seen_node`` is updated as ``on_chain_start`` events for tool nodes
    flow past so a subsequent ``on_tool_end`` (or chain-node end) can be
    attributed to the correct actor.

    ``final_state`` is populated when the root LangGraph chain emits its
    ``on_chain_end`` so the session runner can read the final ``GraphState``
    without re-invoking the graph.
    """

    last_seen_node: Optional[str] = None
    final_state: Optional[dict] = None


def actor_label(actor_id: str) -> str:
    """Map an actor id to the human label used in chat ``authorName``."""
    return _ACTOR_LABELS.get(actor_id, actor_id)


def tool_node_for(tool_name: str) -> str:
    """Return ``"vis_tool"`` if ``tool_name`` is in :data:`TOOL_REGISTRY`,
    else ``"data_tool"``.
    """
    return "vis_tool" if tool_name in TOOL_REGISTRY else "data_tool"


def figure_url(abs_path: str) -> str:
    """Convert an absolute path under ``tmp_dev/web_figures/`` to its URL form.

    Example::

        /Users/jixianli/projects/uvisbox-assistant/tmp_dev/web_figures/abcd.png
            -> /figures/abcd.png

    Falls back to ``/figures/<basename>`` if the path does not contain a
    ``web_figures`` segment.
    """
    parts = PurePosixPath(abs_path).parts
    if "web_figures" in parts:
        idx = parts.index("web_figures")
        tail = "/".join(parts[idx + 1:])
        return f"/figures/{tail}"
    return f"/figures/{PurePosixPath(abs_path).name}"


def truncate_payload(result: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a tool-result dict to fields safe for a trace payload.

    Keeps only ``status`` and ``message`` (the two fields the trace panel
    actually displays). Drops ``_figure_path``, ``_vis_params``,
    ``_error_details``, numpy arrays, and any other large or binary payloads.
    Long strings are truncated to :data:`_MAX_TRACE_STRING_LEN` characters
    with a suffix marker.

    Returns a new dict; the input is not mutated.
    """
    out: Dict[str, Any] = {}
    if "status" in result:
        out["status"] = result["status"]
    if "message" in result:
        out["message"] = _shorten_string(result["message"])
    return out


def translate_event(event: Dict[str, Any], ctx: TranslatorContext) -> List[Dict[str, Any]]:
    """Translate one ``astream_events`` event into zero or more envelopes.

    May mutate ``ctx``. Returns a list of envelopes ready to ``send_json``
    over the WebSocket.
    """
    kind = event.get("event")
    name = event.get("name")
    data = event.get("data") or {}

    if kind == "on_chain_start":
        if name in _TRACKED_NODES:
            ctx.last_seen_node = name
        return []

    if kind == "on_chain_end":
        # The root LangGraph chain end carries the final GraphState as output.
        # In practice it is emitted with name="LangGraph"; we also accept the
        # case where event["name"] equals the compiled graph's class name.
        if name == "LangGraph":
            output = data.get("output")
            if isinstance(output, dict):
                ctx.final_state = output
            return []
        # Tool-node chain ends double as our "tool_end" signal in real runs.
        if name in _TOOL_NODES:
            return _translate_tool_node_end(name, data, ctx)
        return []

    if kind == "on_chat_model_end":
        return _translate_chat_model_end(data)

    if kind == "on_tool_end":
        return _translate_tool_end(event, ctx)

    return []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _envelope(env_type: str, message: Dict[str, Any]) -> Dict[str, Any]:
    """Wrap a message dict in a ``{"type", "message"}`` envelope with id."""
    message = dict(message)
    message.setdefault("id", uuid.uuid4().hex)
    return {"type": env_type, "message": message}


def _shorten_string(value: Any) -> Any:
    """Truncate ``value`` to :data:`_MAX_TRACE_STRING_LEN` if it is a long string.

    Non-strings pass through unchanged.
    """
    if isinstance(value, str) and len(value) > _MAX_TRACE_STRING_LEN:
        return value[:_MAX_TRACE_STRING_LEN] + _TRUNCATION_SUFFIX
    return value


def _translate_chat_model_end(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Map an ``on_chat_model_end`` event to envelopes."""
    output = data.get("output")
    if output is None:
        return []

    tool_calls = _get_tool_calls(output)
    if tool_calls:
        envelopes: List[Dict[str, Any]] = []
        for call in tool_calls:
            tool_name = call.get("name", "")
            envelopes.append(_envelope("trace", {
                "from": "model",
                "to": tool_node_for(tool_name),
                "kind": "tool_call",
                "payload": {
                    "tool": tool_name,
                    "args": call.get("args", {}),
                },
            }))
        return envelopes

    text = _get_text_content(output)
    if not text:
        return []

    return [
        _envelope("trace", {
            "from": "model",
            "to": "user",
            "kind": "prompt",
            "payload": text,
        }),
        _envelope("chat", {
            "role": "assistant",
            "authorName": actor_label("model"),
            "content": text,
        }),
    ]


def _translate_tool_end(event: Dict[str, Any], ctx: TranslatorContext) -> List[Dict[str, Any]]:
    """Map an ``on_tool_end`` event to envelopes.

    ``event["data"]["output"]`` is expected to be the raw result dict the tool
    returned (status, message, optional ``_figure_path``).
    """
    data = event.get("data") or {}
    output = data.get("output")
    if not isinstance(output, dict):
        return []
    tool_name = _get_tool_name(event)
    return _envelopes_for_tool_result(output, ctx.last_seen_node, tool_name)


def _translate_tool_node_end(
    node_name: str,
    data: Dict[str, Any],
    ctx: TranslatorContext,
) -> List[Dict[str, Any]]:
    """Map a tool-node ``on_chain_end`` event to envelopes.

    The node's output is a state-update dict whose ``messages[-1]`` is the
    ``ToolMessage`` carrying the tool result. We recover the original result
    dict from that message's ``content`` (a stringified Python dict).
    """
    output = data.get("output")
    if not isinstance(output, dict):
        return []
    messages = output.get("messages") or []
    if not messages:
        return []
    last = messages[-1]
    content = _get_attr_or_key(last, "content")
    result = _parse_tool_message_content(content)
    if not isinstance(result, dict):
        return []
    # Use the recorded last_seen_node when available; fall back to node_name.
    actor = ctx.last_seen_node if ctx.last_seen_node in _TOOL_NODES else node_name
    # Try to recover the tool name from the execution sequence if present.
    tool_name = _tool_name_from_execution_sequence(output)
    return _envelopes_for_tool_result(result, actor, tool_name)


def _envelopes_for_tool_result(
    result: Dict[str, Any],
    actor: Optional[str],
    tool_name: str,
) -> List[Dict[str, Any]]:
    """Build trace (+ optional chat) envelopes for one tool result dict."""
    status = result.get("status")
    src = actor or "data_tool"

    if status != "success":
        return [_envelope("trace", {
            "from": src,
            "to": "model",
            "kind": "error",
            "payload": result.get("message", "tool error"),
        })]

    envelopes: List[Dict[str, Any]] = [_envelope("trace", {
        "from": src,
        "to": "model",
        "kind": "tool_result",
        "payload": truncate_payload(result),
    })]

    fig_path = result.get("_figure_path")
    if fig_path:
        envelopes.append(_envelope("chat", {
            "role": "assistant",
            "authorName": actor_label(src),
            "content": [
                {"type": "text", "text": result.get("message", "")},
                {"type": "image", "url": figure_url(fig_path), "alt": tool_name},
            ],
        }))
    return envelopes


def _get_tool_calls(output: Any) -> List[Dict[str, Any]]:
    """Extract a list of tool_call dicts from a model output (AIMessage)."""
    calls = _get_attr_or_key(output, "tool_calls")
    if not calls:
        return []
    # Normalise to a list of plain dicts with at least name + args.
    normalised: List[Dict[str, Any]] = []
    for call in calls:
        if isinstance(call, dict):
            normalised.append(call)
        else:  # langchain ToolCall objects expose .name / .args / .id
            normalised.append({
                "name": getattr(call, "name", ""),
                "args": getattr(call, "args", {}),
                "id": getattr(call, "id", None),
            })
    return normalised


def _get_text_content(output: Any) -> str:
    """Return the text content of an AIMessage, or empty string."""
    content = _get_attr_or_key(output, "content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # langchain content can be a list of {type, text} parts.
        parts: List[str] = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(part.get("text", ""))
            elif isinstance(part, str):
                parts.append(part)
        return "".join(parts)
    return ""


def _get_attr_or_key(obj: Any, key: str) -> Any:
    """Read ``obj.key`` if available, else ``obj[key]`` if ``obj`` is a dict."""
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def _get_tool_name(event: Dict[str, Any]) -> str:
    """Best-effort extraction of the tool name from an on_tool_end event."""
    # Common shapes: event["name"] is the tool name itself, or
    # event["data"]["input"] carries it.
    name = event.get("name")
    if isinstance(name, str) and name:
        return name
    data = event.get("data") or {}
    input_ = data.get("input") or {}
    if isinstance(input_, dict):
        n = input_.get("name") or input_.get("tool")
        if isinstance(n, str):
            return n
    return ""


def _parse_tool_message_content(content: Any) -> Any:
    """Recover a Python dict from a stringified ToolMessage content payload.

    ``call_data_tool`` / ``call_vis_tool`` build the ``ToolMessage`` content
    via ``str(result_dict)``. ``ast.literal_eval`` parses that safely for
    dict / list / scalar literals. Returns ``content`` unchanged on failure.
    """
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        try:
            return ast.literal_eval(content)
        except (ValueError, SyntaxError):
            return content
    return content


def _tool_name_from_execution_sequence(output: Dict[str, Any]) -> str:
    """Pull the tool name from the most recent ``tool_execution_sequence`` entry."""
    seq = output.get("tool_execution_sequence") or []
    if seq and isinstance(seq[-1], dict):
        name = seq[-1].get("tool_name")
        if isinstance(name, str):
            return name
    return ""
