"""Unit tests for error interpretation."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from uvisbox_assistant.errors.error_interpretation import (
    interpret_uvisbox_error,
    format_error_with_hint,
    _extract_colormap_name,
    _extract_method_name,
    _extract_valid_methods
)


def test_colormap_error_no_debug():
    """Test colormap error without debug mode."""
    error = ValueError("Invalid colormap name 'Reds'")
    traceback = "...matplotlib..."

    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=False)

    assert "Colormap error" in user_msg
    assert hint is None


def test_colormap_error_with_debug():
    """Test colormap error with debug mode."""
    error = ValueError("Invalid colormap name 'Reds'")
    traceback = "...matplotlib...mpl_colors..."

    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=True)

    assert "Colormap error" in user_msg
    assert hint is not None
    assert "UVisBox" in hint


def test_method_error():
    """Test method validation error."""
    error = ValueError("Unknown method 'fbd'. Choose 'fdb' or 'mfbd'.")
    traceback = "..."

    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=True)

    assert "Method validation error" in user_msg
    assert hint is not None
    assert "'fbd'" in hint


def test_shape_error():
    """Test shape mismatch error."""
    error = ValueError("Expected 2D array, got shape (100, 50, 3)")
    traceback = "..."

    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=True)

    assert "shape" in user_msg.lower()
    assert hint is not None


def test_file_not_found_error():
    """Test file not found error."""
    error = FileNotFoundError("/tmp/missing.npy")
    traceback = "..."

    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=True)

    assert "File not found" in user_msg
    assert hint is not None
    assert "/context" in hint


def test_import_error():
    """Test import error for UVisBox."""
    error = ImportError("No module named 'uvisbox'")
    traceback = "..."

    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=True)

    assert "UVisBox" in user_msg
    assert hint is not None
    assert "conda" in hint or "pip" in hint


def test_format_error_with_hint():
    """Test error formatting with hint."""
    formatted = format_error_with_hint("Error", "Hint here")

    assert "Error" in formatted
    assert "💡 Debug hint:" in formatted
    assert "Hint here" in formatted


def test_format_error_without_hint():
    """Test error formatting without hint."""
    formatted = format_error_with_hint("Error", None)

    assert formatted == "Error"
    assert "💡" not in formatted


def test_extract_colormap_name():
    """Test colormap name extraction."""
    assert _extract_colormap_name("Invalid colormap 'Reds'") == "Reds"
    assert _extract_colormap_name("colormap Plasma not found") == "Plasma"


def test_extract_method_name():
    """Test method name extraction."""
    assert _extract_method_name("Unknown method 'fbd'") == "fbd"
    assert _extract_method_name("Invalid method: 'mfbd'") == "mfbd"


def test_extract_valid_methods():
    """Test valid methods extraction."""
    methods = _extract_valid_methods("Choose 'fdb' or 'mfbd'")
    assert "fdb" in methods
    assert "mfbd" in methods
