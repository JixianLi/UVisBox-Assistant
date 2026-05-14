# ABOUTME: Renderer abstraction selecting between on-screen windows and file output via a contextvar.
# ABOUTME: WindowRenderer is the default for the CLI REPL; FileRenderer writes PNGs for web mode.
"""Renderer abstraction for matplotlib and PyVista output."""
from __future__ import annotations

import matplotlib.pyplot as plt
from contextvars import ContextVar, Token
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Optional, Protocol, runtime_checkable
from uuid import uuid4

from uvisbox_assistant.utils.main_thread import run_on_main_thread

if TYPE_CHECKING:
    import pyvista


@runtime_checkable
class Renderer(Protocol):
    """Renders matplotlib figures and PyVista scenes to a window or to a file."""

    def show_matplotlib(self, fig) -> Optional[str]:
        """Display or save a matplotlib Figure. Returns the PNG path if file-based, else None."""
        ...

    def show_pyvista(
        self,
        plotter_factory: Callable[..., "pyvista.Plotter"],
        build_scene: Callable[["pyvista.Plotter"], None],
    ) -> Optional[str]:
        """Display or save a PyVista scene. Returns the PNG path if file-based, else None."""
        ...


class WindowRenderer:
    """Renders to an interactive on-screen window. Used by the CLI REPL."""

    def show_matplotlib(self, fig) -> Optional[str]:
        plt.show(block=False)
        plt.pause(0.1)
        return None

    def show_pyvista(
        self,
        plotter_factory: Callable[..., "pyvista.Plotter"],
        build_scene: Callable[["pyvista.Plotter"], None],
    ) -> Optional[str]:
        plotter = plotter_factory()
        build_scene(plotter)
        return None


class FileRenderer:
    """Renders by saving a PNG to disk. Used by the web interface."""

    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def show_matplotlib(self, fig) -> Optional[str]:
        path = self.out_dir / f"{uuid4().hex}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return str(path)

    def show_pyvista(
        self,
        plotter_factory: Callable[..., "pyvista.Plotter"],
        build_scene: Callable[["pyvista.Plotter"], None],
    ) -> Optional[str]:
        # VTK/Cocoa on macOS requires NSWindow init on the main thread, even
        # for off_screen plotters. The agent runs in a worker thread in web
        # mode, so we marshal the render to the main thread. In CLI mode
        # (no loop registered) this is a no-op.
        return run_on_main_thread(lambda: self._render_pyvista(plotter_factory, build_scene))

    def _render_pyvista(
        self,
        plotter_factory: Callable[..., "pyvista.Plotter"],
        build_scene: Callable[["pyvista.Plotter"], None],
    ) -> str:
        path = self.out_dir / f"{uuid4().hex}.png"
        plotter = plotter_factory(off_screen=True)
        build_scene(plotter)
        plotter.screenshot(str(path))
        plotter.close()
        return str(path)


current_renderer: ContextVar[Renderer] = ContextVar("renderer", default=WindowRenderer())


def set_renderer(renderer: Renderer) -> Token:
    """Set the active renderer for the current context. Returns a token for resetting."""
    return current_renderer.set(renderer)
