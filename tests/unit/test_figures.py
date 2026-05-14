# ABOUTME: Unit tests for src/uvisbox_assistant/web/figures.py
# ABOUTME: Covers filename validation rules and clear_figures_dir behavior (0 LLM calls).

import uuid

import pytest

from uvisbox_assistant.web import figures
from uvisbox_assistant.web.figures import (
    FIGURES_DIR,
    clear_figures_dir,
    validate_figure_filename,
)


def test_valid_uuid_png_filename():
    assert validate_figure_filename("0123456789abcdef0123456789abcdef.png") is True
    assert validate_figure_filename(uuid.uuid4().hex + ".png") is True


def test_rejects_uppercase_hex():
    assert validate_figure_filename("ABCDEF0123456789ABCDEF0123456789.png") is False


@pytest.mark.parametrize(
    "name",
    [
        "../etc/passwd",
        "..",
        "./foo.png",
        "/etc/passwd",
        "subdir/abc.png",
    ],
)
def test_rejects_path_traversal(name):
    assert validate_figure_filename(name) is False


@pytest.mark.parametrize(
    "name",
    [
        "0123456789abcdef0123456789abcdef.jpg",
        "0123456789abcdef0123456789abcdef.png.exe",
        "0123456789ABCDEF0123456789ABCDEF.PNG",
        "0123456789abcdef0123456789abcdef",
    ],
)
def test_rejects_wrong_extension(name):
    assert validate_figure_filename(name) is False


@pytest.mark.parametrize(
    "name",
    [
        "0123456789abcdef0123456789abcde.png",   # 31 hex chars
        "0123456789abcdef0123456789abcdef0.png", # 33 hex chars
        ".png",                                  # empty hex
    ],
)
def test_rejects_wrong_length(name):
    assert validate_figure_filename(name) is False


def test_rejects_non_hex_chars():
    # g-z are not hex digits
    assert validate_figure_filename("ghijklmnopqrstuvwxyz0123456789ab.png") is False


def test_clear_figures_dir_creates_when_missing(tmp_path, monkeypatch):
    fresh = tmp_path / "fresh_dir"
    assert not fresh.exists()
    monkeypatch.setattr(figures, "FIGURES_DIR", fresh)

    clear_figures_dir()

    assert fresh.exists()
    assert fresh.is_dir()
    assert list(fresh.iterdir()) == []


def test_clear_figures_dir_removes_files(tmp_path, monkeypatch):
    monkeypatch.setattr(figures, "FIGURES_DIR", tmp_path)
    for name in ("a.png", "b.png", "c.png"):
        (tmp_path / name).write_bytes(b"x")
    assert {p.name for p in tmp_path.iterdir()} == {"a.png", "b.png", "c.png"}

    clear_figures_dir()

    assert tmp_path.exists()
    assert list(tmp_path.iterdir()) == []
