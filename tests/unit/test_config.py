"""Unit tests for configuration."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from chatuvisbox import config


def test_config_paths_exist():
    """Test that all configured paths exist."""
    assert config.TEMP_DIR.exists()
    assert config.TEST_DATA_DIR.exists()
    assert config.LOG_DIR.exists()


def test_boxplot_style_config_defaults():
    """Test BoxplotStyleConfig default parameters."""
    params = config.DEFAULT_VIS_PARAMS

    # Percentiles and colormap
    assert params["percentiles"] == [25, 50, 90, 100]
    assert params["percentile_colormap"] == "viridis"

    # Median styling
    assert params["show_median"] == True
    assert params["median_color"] == "red"
    assert params["median_width"] == 3.0
    assert params["median_alpha"] == 1.0

    # Outliers styling
    assert params["show_outliers"] == False
    assert params["outliers_color"] == "gray"
    assert params["outliers_width"] == 1.0
    assert params["outliers_alpha"] == 0.5

    # Parallel computation
    assert params["workers"] == 12


def test_no_plot_all_curves_param():
    """Verify plot_all_curves parameter is removed."""
    params = config.DEFAULT_VIS_PARAMS
    assert "plot_all_curves" not in params


def test_probabilistic_marching_squares_defaults():
    """Test probabilistic marching squares defaults."""
    params = config.DEFAULT_VIS_PARAMS
    assert params["isovalue"] == 0.5
    assert params["colormap"] == "viridis"


def test_uncertainty_lobes_defaults():
    """Test uncertainty lobes defaults."""
    params = config.DEFAULT_VIS_PARAMS
    assert params["percentile1"] == 90
    assert params["percentile2"] == 50
    assert params["scale"] == 0.2


def test_figure_defaults():
    """Test general figure defaults."""
    params = config.DEFAULT_VIS_PARAMS
    assert params["figsize"] == (10, 8)
    assert params["dpi"] == 100


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
