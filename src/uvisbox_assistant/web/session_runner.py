# ABOUTME: SessionRunner drives one ConversationSession from a single WebSocket connection.
# ABOUTME: Bridges LangGraph astream_events (in a worker thread) and hybrid auto-rerender into wire-format trace/chat envelopes.
"""Per-connection session runner for the web interface.

For each prompt arriving over a WebSocket, :class:`SessionRunner` either:

* delegates to the hybrid-control fast path (re-invoking the last vis tool
  directly via :data:`TOOL_REGISTRY`), or
* drives the full LangGraph workflow via ``graph_app.astream_events`` in a
  worker thread, draining translated envelopes through an
  :class:`asyncio.Queue` back to the WebSocket.

The runner owns one :class:`ConversationSession` whose ``state`` is updated
from :attr:`TranslatorContext.final_state` so the stream itself is the
single source of truth (avoiding a second ``ainvoke``).

SessionRunner processes one prompt at a time; a concurrent prompt receives
an error envelope and is dropped.
"""
from __future__ import annotations

import asyncio
import contextvars
import threading
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from fastapi import WebSocket
from langchain_core.messages import AIMessage, HumanMessage

from uvisbox_assistant.core.graph import graph_app
from uvisbox_assistant.core.state import create_initial_state
from uvisbox_assistant.session.conversation import ConversationSession
from uvisbox_assistant.session.hybrid_control import (
    execute_simple_command,
    is_hybrid_eligible,
)
from uvisbox_assistant.tools.vis_tools import TOOL_REGISTRY
from uvisbox_assistant.web.trace_translator import (
    TranslatorContext,
    figure_url,
    translate_event,
    truncate_payload,
)


@dataclass(frozen=True)
class _Sentinel:
    """Queue control marker distinguishing stream-end signals from envelopes.

    Using a dedicated type (rather than a string or special-key dict) keeps
    sentinels unambiguous against the dict envelopes that flow through the
    same queue.
    """

    kind: str  # "done" or "error"
    message: str = ""

    @classmethod
    def done(cls) -> "_Sentinel":
        return cls(kind="done")

    @classmethod
    def error(cls, message: str) -> "_Sentinel":
        return cls(kind="error", message=message)


class SessionRunner:
    """Drive one :class:`ConversationSession` from a single WebSocket.

    See module docstring for the prompt lifecycle.
    """

    def __init__(self, ws: WebSocket):
        self.ws = ws
        self.session = ConversationSession()
        self._busy = False

    async def handle_prompt(self, text: str) -> None:
        """Process one user prompt end-to-end, streaming envelopes back."""
        if self._busy:
            await self.ws.send_json({
                "type": "error",
                "message": "already processing a prompt",
            })
            return

        self._busy = True
        await self.ws.send_json({"type": "busy", "busy": True})
        try:
            await self._emit_chat(role="user", content=text)
            await self._emit_trace(
                from_="user", to="model", kind="prompt", payload=text,
            )

            try:
                handled = False
                if self.session.state is not None and is_hybrid_eligible(text):
                    handled = await self._handle_hybrid(text)
                if not handled:
                    await self._handle_graph(text)
            except Exception as exc:  # noqa: BLE001 - keep the WS alive
                message = str(exc) or exc.__class__.__name__
                await self._emit_trace(
                    from_="model", to="user", kind="error", payload=message,
                )
                await self._emit_chat(
                    role="assistant",
                    authorName="Model",
                    content=f"Error: {message}",
                )
        finally:
            self._busy = False
            await self.ws.send_json({"type": "busy", "busy": False})

    async def reset(self) -> None:
        """Reset the underlying conversation session.

        Figures on disk and the ``session_ready`` envelope are the server's
        responsibility, not this runner's.
        """
        self.session.reset()
        self._busy = False

    # ------------------------------------------------------------------
    # Graph path
    # ------------------------------------------------------------------

    async def _handle_graph(self, text: str) -> None:
        """Run the LangGraph workflow in a worker thread, draining envelopes."""
        if self.session.state is None:
            self.session.state = create_initial_state(text)
        else:
            self.session.state["messages"].append(HumanMessage(content=text))

        queue: asyncio.Queue = asyncio.Queue()
        ctx = TranslatorContext()
        loop = asyncio.get_running_loop()
        # Propagate ContextVars (notably current_renderer) into the worker
        # thread so plot tools dispatched by the graph use FileRenderer.
        context_snapshot = contextvars.copy_context()

        def worker() -> None:
            async def run() -> None:
                try:
                    async for event in graph_app.astream_events(
                        self.session.state, version="v2",
                    ):
                        for envelope in translate_event(event, ctx):
                            loop.call_soon_threadsafe(queue.put_nowait, envelope)
                    loop.call_soon_threadsafe(queue.put_nowait, _Sentinel.done())
                except Exception as exc:  # noqa: BLE001
                    loop.call_soon_threadsafe(
                        queue.put_nowait,
                        _Sentinel.error(str(exc) or exc.__class__.__name__),
                    )

            context_snapshot.run(asyncio.run, run())

        threading.Thread(target=worker, daemon=True).start()

        while True:
            item: Union[Dict[str, Any], _Sentinel] = await queue.get()
            if isinstance(item, _Sentinel):
                if item.kind == "done":
                    if ctx.final_state is not None:
                        self.session.state = ctx.final_state
                    return
                # error during streaming
                await self._emit_trace(
                    from_="model", to="user", kind="error", payload=item.message,
                )
                await self._emit_chat(
                    role="assistant",
                    authorName="Model",
                    content=f"Error: {item.message}",
                )
                return
            await self.ws.send_json(item)

    # ------------------------------------------------------------------
    # Hybrid path
    # ------------------------------------------------------------------

    async def _handle_hybrid(self, text: str) -> bool:
        """Run the hybrid fast path.

        Returns True if the hybrid layer claimed the prompt (whether or not
        a rerender succeeded). Returns False to fall through to the graph.
        """
        success, result, message = execute_simple_command(text, self.session.state)
        if not success:
            return False

        # Update session state per ConversationSession.send() logic.
        if isinstance(result, dict):
            self.session.state["last_vis_params"] = result
        self.session.state["messages"].append(HumanMessage(content=text))
        self.session.state["messages"].append(AIMessage(content=message))

        # Synthetic acknowledgement so the trace UI sees the hybrid response.
        await self._emit_trace(
            from_="model", to="user", kind="prompt", payload=message,
        )
        await self._emit_chat(
            role="assistant", authorName="Model", content=message,
        )

        # Auto-rerender path: only when we have a known vis tool to re-invoke.
        params = self.session.state.get("last_vis_params") or {}
        tool_name = params.get("_tool_name")
        if not tool_name or tool_name not in TOOL_REGISTRY:
            return True

        tool_fn = TOOL_REGISTRY[tool_name]
        call_args = {k: v for k, v in params.items() if not k.startswith("_")}

        await self._emit_trace(
            from_="model",
            to="vis_tool",
            kind="tool_call",
            payload={"tool": tool_name, "args": call_args},
        )

        # Tool is sync and does I/O (matplotlib savefig); offload to a thread.
        rerun = await asyncio.to_thread(tool_fn, **call_args)

        if rerun.get("status") != "success":
            await self._emit_trace(
                from_="vis_tool",
                to="model",
                kind="error",
                payload=rerun.get("message", "rerender failed"),
            )
            await self._emit_chat(
                role="assistant",
                authorName="Vis Tool",
                content=f"Re-render failed: {rerun.get('message', '')}",
            )
            return True

        await self._emit_trace(
            from_="vis_tool",
            to="model",
            kind="tool_result",
            payload=truncate_payload(rerun),
        )

        fig_path = rerun.get("_figure_path")
        if fig_path:
            await self._emit_chat(
                role="assistant",
                authorName="Vis Tool",
                content=[
                    {"type": "text", "text": rerun.get("message", "")},
                    {"type": "image", "url": figure_url(fig_path), "alt": tool_name},
                ],
            )

        return True

    # ------------------------------------------------------------------
    # Envelope helpers
    # ------------------------------------------------------------------

    async def _emit_trace(
        self,
        *,
        from_: str,
        to: str,
        kind: str,
        payload: Any,
    ) -> None:
        """Send a single ``trace`` envelope with a fresh id."""
        await self.ws.send_json({
            "type": "trace",
            "message": {
                "id": uuid.uuid4().hex,
                "from": from_,
                "to": to,
                "kind": kind,
                "payload": payload,
            },
        })

    async def _emit_chat(
        self,
        *,
        role: str,
        content: Union[str, List[Dict[str, Any]]],
        authorName: Optional[str] = None,
    ) -> None:
        """Send a single ``chat`` envelope with a fresh id."""
        message: Dict[str, Any] = {
            "id": uuid.uuid4().hex,
            "role": role,
            "content": content,
        }
        if authorName is not None:
            message["authorName"] = authorName
        await self.ws.send_json({"type": "chat", "message": message})
