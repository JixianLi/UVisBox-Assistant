"""Unit tests for hybrid control command parser."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from chatuvisbox.command_parser import parse_simple_command, apply_command_to_params


def test_parse_colormap():
    """Test parsing colormap command."""
    cmd = parse_simple_command("colormap plasma")
    assert cmd is not None
    assert cmd.param_name == "colormap"
    assert cmd.value == "plasma"


def test_parse_percentile():
    """Test parsing percentile command."""
    cmd = parse_simple_command("percentile 75")
    assert cmd is not None
    assert cmd.param_name == "percentiles"
    assert cmd.value == [75.0]


def test_parse_isovalue():
    """Test parsing isovalue command."""
    cmd = parse_simple_command("isovalue 0.8")
    assert cmd is not None
    assert cmd.param_name == "isovalue"
    assert cmd.value == 0.8


def test_parse_show_median():
    """Test parsing show median command."""
    cmd = parse_simple_command("show median")
    assert cmd is not None
    assert cmd.param_name == "show_median"
    assert cmd.value == True


def test_parse_hide_outliers():
    """Test parsing hide outliers command."""
    cmd = parse_simple_command("hide outliers")
    assert cmd is not None
    assert cmd.param_name == "show_outliers"
    assert cmd.value == False


# BoxplotStyleConfig median styling tests
def test_parse_median_color():
    """Test parsing median color command."""
    cmd = parse_simple_command("median color blue")
    assert cmd is not None
    assert cmd.param_name == "median_color"
    assert cmd.value == "blue"


def test_parse_median_width():
    """Test parsing median width command."""
    cmd = parse_simple_command("median width 2.5")
    assert cmd is not None
    assert cmd.param_name == "median_width"
    assert cmd.value == 2.5


def test_parse_median_alpha():
    """Test parsing median alpha command."""
    cmd = parse_simple_command("median alpha 0.8")
    assert cmd is not None
    assert cmd.param_name == "median_alpha"
    assert cmd.value == 0.8


# BoxplotStyleConfig outliers styling tests
def test_parse_outliers_color():
    """Test parsing outliers color command."""
    cmd = parse_simple_command("outliers color black")
    assert cmd is not None
    assert cmd.param_name == "outliers_color"
    assert cmd.value == "black"


def test_parse_outliers_width():
    """Test parsing outliers width command."""
    cmd = parse_simple_command("outliers width 1.5")
    assert cmd is not None
    assert cmd.param_name == "outliers_width"
    assert cmd.value == 1.5


def test_parse_outliers_alpha():
    """Test parsing outliers alpha command."""
    cmd = parse_simple_command("outliers alpha 1.0")
    assert cmd is not None
    assert cmd.param_name == "outliers_alpha"
    assert cmd.value == 1.0


def test_parse_scale():
    """Test parsing scale command."""
    cmd = parse_simple_command("scale 0.5")
    assert cmd is not None
    assert cmd.param_name == "scale"
    assert cmd.value == 0.5


def test_parse_alpha():
    """Test parsing alpha command."""
    cmd = parse_simple_command("alpha 0.7")
    assert cmd is not None
    assert cmd.param_name == "alpha"
    assert cmd.value == 0.7


def test_parse_invalid_command():
    """Test that invalid commands return None."""
    cmd = parse_simple_command("generate some curves")
    assert cmd is None


# Test apply_command_to_params
def test_apply_styling_params():
    """Test applying BoxplotStyleConfig params to current params."""
    current = {
        "_tool_name": "plot_functional_boxplot",
        "data_path": "/path/to/data.npy",
        "median_color": "red",
        "outliers_alpha": 0.5
    }

    # Update outliers color
    cmd = parse_simple_command("outliers color black")
    updated = apply_command_to_params(cmd, current)

    assert updated["outliers_color"] == "black"
    assert updated["median_color"] == "red"  # Unchanged
    assert updated["outliers_alpha"] == 0.5  # Unchanged


def test_apply_median_styling():
    """Test applying median styling parameters."""
    current = {
        "_tool_name": "plot_functional_boxplot",
        "data_path": "/path/to/data.npy",
        "median_color": "red",
        "median_width": 3.0,
        "median_alpha": 1.0
    }

    # Update median color
    cmd = parse_simple_command("median color blue")
    updated = apply_command_to_params(cmd, current)
    assert updated["median_color"] == "blue"

    # Update median width
    cmd = parse_simple_command("median width 2.5")
    updated = apply_command_to_params(cmd, updated)
    assert updated["median_width"] == 2.5

    # Update median alpha
    cmd = parse_simple_command("median alpha 0.8")
    updated = apply_command_to_params(cmd, updated)
    assert updated["median_alpha"] == 0.8


def test_colormap_mapping():
    """Test that colormap maps to both colormap and percentile_colormap."""
    current = {
        "_tool_name": "plot_functional_boxplot",
        "data_path": "/path/to/data.npy"
    }

    cmd = parse_simple_command("colormap plasma")
    updated = apply_command_to_params(cmd, current)

    # Should set both (hybrid_control.py will filter based on function signature)
    assert updated["colormap"] == "plasma"
    assert updated["percentile_colormap"] == "plasma"


if __name__ == "__main__":
    # Run all tests
    import inspect

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
        print("✅ All command parser tests passed!")
