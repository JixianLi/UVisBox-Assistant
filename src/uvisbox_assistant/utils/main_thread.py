# ABOUTME: Dispatches a synchronous callable to the asyncio event loop's main thread.
# ABOUTME: Used to keep PyVista calls on the main thread on macOS, where VTK's Cocoa render window cannot init off-thread.

"""Main-thread dispatch helper for blocking work that must not run on a worker thread.

Background
----------
On macOS, VTK's render window (used by PyVista) initialises an ``NSWindow``
even when ``off_screen=True``. AppKit requires that to happen on the
process's main thread. Our web server runs the agent in a worker thread,
so PyVista calls dispatched from there crash with
"NSWindow should only be initiated from the main thread."

Usage
-----
At application startup, on the asyncio event loop's main thread::

    register_main_loop(asyncio.get_running_loop())

Then anywhere::

    result = run_on_main_thread(lambda: pyvista_render_sync())

If no loop is registered (CLI REPL) or the caller is already on the main
thread, ``run_on_main_thread`` runs the callable directly without dispatch.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import threading
from typing import Callable, Optional, TypeVar

T = TypeVar("T")

_main_loop: Optional[asyncio.AbstractEventLoop] = None


def register_main_loop(loop: asyncio.AbstractEventLoop) -> None:
    """Record the asyncio loop running on the process's main thread."""
    global _main_loop
    _main_loop = loop


def run_on_main_thread(fn: Callable[[], T]) -> T:
    """Run ``fn`` synchronously on the main thread; block the caller until done.

    Behavior:
    - If the caller is already on the main thread, ``fn`` runs in-place.
    - If no main loop has been registered (CLI mode), ``fn`` runs in-place.
    - Otherwise the call is marshaled via ``loop.call_soon_threadsafe`` and
      the caller blocks on a :class:`concurrent.futures.Future` until ``fn``
      returns (or raises) on the main thread.
    """
    if _main_loop is None or threading.current_thread() is threading.main_thread():
        return fn()

    future: concurrent.futures.Future = concurrent.futures.Future()

    def runner() -> None:
        try:
            future.set_result(fn())
        except BaseException as exc:  # noqa: BLE001
            future.set_exception(exc)

    _main_loop.call_soon_threadsafe(runner)
    return future.result()
