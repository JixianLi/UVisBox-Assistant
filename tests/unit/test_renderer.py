# ABOUTME: Unit tests for utils/renderer.py
# ABOUTME: Tests Renderer abstraction with stubs (0 LLM calls, no GUI)

import matplotlib.pyplot as plt
import pytest
from unittest.mock import MagicMock

from uvisbox_assistant.utils.renderer import (
    FileRenderer,
    WindowRenderer,
    current_renderer,
    set_renderer,
)


def test_window_renderer_matplotlib_returns_none(monkeypatch):
    show_mock = MagicMock()
    pause_mock = MagicMock()
    monkeypatch.setattr(plt, "show", show_mock)
    monkeypatch.setattr(plt, "pause", pause_mock)

    fig = plt.figure()
    try:
        result = WindowRenderer().show_matplotlib(fig)
    finally:
        plt.close(fig)

    assert result is None
    show_mock.assert_called_with(block=False)
    pause_mock.assert_called()


def test_file_renderer_matplotlib_writes_png(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])

    path = FileRenderer(tmp_path).show_matplotlib(fig)

    assert isinstance(path, str)
    from pathlib import Path

    file_path = Path(path)
    assert file_path.exists()
    assert file_path.stat().st_size > 0
    with open(file_path, "rb") as f:
        header = f.read(8)
    assert header == b"\x89PNG\r\n\x1a\n"


def test_file_renderer_creates_out_dir(tmp_path):
    out_dir = tmp_path / "nested" / "dir"
    assert not out_dir.exists()

    renderer = FileRenderer(out_dir)

    assert out_dir.exists()
    assert out_dir.is_dir()
    assert renderer.out_dir == out_dir


def test_file_renderer_pyvista_screenshots_and_closes(tmp_path):
    plotter_mock = MagicMock()
    factory_mock = MagicMock(return_value=plotter_mock)
    build_scene_mock = MagicMock()

    result = FileRenderer(tmp_path).show_pyvista(factory_mock, build_scene_mock)

    factory_mock.assert_called_once_with(off_screen=True)
    build_scene_mock.assert_called_once_with(plotter_mock)
    plotter_mock.screenshot.assert_called_once_with(result)
    plotter_mock.close.assert_called_once()
    assert isinstance(result, str)


def test_window_renderer_pyvista_no_off_screen():
    plotter_mock = MagicMock()
    factory_mock = MagicMock(return_value=plotter_mock)
    build_scene_mock = MagicMock()

    result = WindowRenderer().show_pyvista(factory_mock, build_scene_mock)

    factory_mock.assert_called_once_with()
    build_scene_mock.assert_called_once_with(plotter_mock)
    assert result is None
    plotter_mock.close.assert_not_called()


def test_current_renderer_default_is_window():
    renderer = current_renderer.get()
    assert isinstance(renderer, WindowRenderer)


def test_set_renderer_scopes_via_token(tmp_path):
    original = current_renderer.get()
    file_renderer = FileRenderer(tmp_path)

    token = set_renderer(file_renderer)
    try:
        assert current_renderer.get() is file_renderer
    finally:
        current_renderer.reset(token)

    assert current_renderer.get() is original
