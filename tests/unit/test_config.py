"""Unit tests for configuration."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from uvisbox_assistant import config


def test_config_paths_exist():
    """Test that all configured paths exist."""
    assert config.TEMP_DIR.exists()
    assert config.TEST_DATA_DIR.exists()
    assert config.LOG_DIR.exists()


def test_figure_defaults():
    """Test that DEFAULT_VIS_PARAMS only contains figure settings."""
    params = config.DEFAULT_VIS_PARAMS

    # Should only have figsize and dpi
    assert len(params) == 2
    assert params["figsize"] == (10, 8)
    assert params["dpi"] == 100


def test_no_visualization_specific_params():
    """Verify visualization-specific params are NOT in config (they're in function signatures)."""
    params = config.DEFAULT_VIS_PARAMS

    # These should NOT be in config - they're hardcoded in vis_tools.py function signatures
    assert "percentiles" not in params
    assert "percentile_colormap" not in params
    assert "show_median" not in params
    assert "median_color" not in params
    assert "workers" not in params
    assert "isovalue" not in params
    assert "colormap" not in params
    assert "percentile1" not in params
    assert "percentile2" not in params
    assert "scale" not in params
    assert "squid_percentile" not in params
    assert "method" not in params


def test_api_key_configured():
    """Test that API key is configured."""
    assert config.GEMINI_API_KEY is not None
    assert len(config.GEMINI_API_KEY) > 0


def test_model_name():
    """Test model name configuration."""
    assert config.MODEL_NAME == "gemini-2.0-flash-lite"


if __name__ == "__main__":
    # Run all tests
    test_functions = [
        obj for name, obj in globals().items()
        if name.startswith('test_') and callable(obj)
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")

    if failed == 0:
        print("✅ All config tests passed!")
