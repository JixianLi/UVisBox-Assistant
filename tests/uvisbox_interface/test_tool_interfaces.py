# ABOUTME: UVisBox-interface integration tests that call vis tool wrappers against the real UVisBox library.
# ABOUTME: Catches structure changes in UVisBox APIs; 0 LLM calls.
"""Integration tests for tool interfaces with UVisBox.

These tests directly call tool functions to verify the interface between
the assistant and UVisBox library. They catch breaking changes in UVisBox
API and ensure tools return expected structures.

Layer 1: Tool Interface Tests
- No LLM calls
- No graph execution
- Direct function calls with real UVisBox
"""

import pytest
import numpy as np
import sys
from pathlib import Path
import matplotlib.pyplot as plt

from uvisbox_assistant.tools.vis_tools import (
    plot_functional_boxplot,
    plot_curve_boxplot,
    plot_probabilistic_marching_squares,
    plot_uncertainty_lobes,
    plot_squid_glyph_2D,
    plot_contour_boxplot,
)
from uvisbox_assistant import config


@pytest.fixture(scope="module")
def test_data_dir():
    """Create temporary directory for test data."""
    test_dir = config.TEMP_DIR / "test_interfaces"
    test_dir.mkdir(parents=True, exist_ok=True)
    yield test_dir
    # Cleanup after all tests
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture
def curves_2d(test_data_dir):
    """Generate 2D curve data (n_curves, n_points)."""
    curves = np.random.randn(30, 100).cumsum(axis=1)
    path = test_data_dir / "curves_2d.npy"
    np.save(path, curves)
    return str(path)


@pytest.fixture
def curves_3d(test_data_dir):
    """Generate 3D curve data (n_curves, n_points, 2)."""
    n_curves, n_points = 25, 50
    t = np.linspace(0, 2*np.pi, n_points)
    curves = np.zeros((n_curves, n_points, 2))
    for i in range(n_curves):
        radius = 1.0 + np.random.randn() * 0.2
        curves[i, :, 0] = radius * np.cos(t) + np.random.randn(n_points) * 0.1
        curves[i, :, 1] = radius * np.sin(t) + np.random.randn(n_points) * 0.1
    path = test_data_dir / "curves_3d.npy"
    np.save(path, curves)
    return str(path)


@pytest.fixture
def scalar_field_3d(test_data_dir):
    """Generate 3D scalar field (nx, ny, n_ensemble)."""
    field = np.random.randn(30, 30, 10)
    path = test_data_dir / "scalar_field.npy"
    np.save(path, field)
    return str(path)


@pytest.fixture
def vectors_and_positions(test_data_dir):
    """Generate vector ensemble and positions for glyphs."""
    n_positions = 5
    n_ensemble = 20

    # Positions
    positions = np.random.rand(n_positions, 2) * 10
    positions_path = test_data_dir / "positions.npy"
    np.save(positions_path, positions)

    # Vectors
    vectors = np.random.randn(n_positions, n_ensemble, 2)
    vectors_path = test_data_dir / "vectors.npy"
    np.save(vectors_path, vectors)

    return str(vectors_path), str(positions_path)


# ============================================================================
# Visualization Tool Interface Tests
# ============================================================================

class TestFunctionalBoxplotInterface:
    """Test plot_functional_boxplot interface with UVisBox."""

    def test_returns_success_with_valid_data(self, curves_2d):
        """Verify successful plot creation with valid 2D curve data."""
        result = plot_functional_boxplot(
            data_path=curves_2d,
            percentiles=[25, 50, 90, 100]
        )

        # Verify structure
        assert result["status"] == "success", f"Expected success, got: {result}"
        assert isinstance(result["message"], str)
        assert len(result["message"]) > 0

        # Verify _vis_params contains all parameters
        assert "_vis_params" in result
        params = result["_vis_params"]
        assert params["_tool_name"] == "plot_functional_boxplot"
        assert params["data_path"] == curves_2d
        assert params["percentiles"] == [25, 50, 90, 100]
        assert "median_color" in params
        assert "method" in params

        plt.close('all')

    def test_returns_error_with_invalid_shape(self, scalar_field_3d):
        """Verify error when data has wrong shape."""
        result = plot_functional_boxplot(data_path=scalar_field_3d)

        assert result["status"] == "error"
        assert "shape" in result["message"].lower() or "2d" in result["message"].lower()

    def test_returns_error_with_missing_file(self):
        """Verify error when file doesn't exist."""
        result = plot_functional_boxplot(data_path="nonexistent.npy")

        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    def test_supports_different_methods(self, curves_2d):
        """Verify both fbd and mfbd methods work."""
        for method in ["fbd", "mfbd"]:
            result = plot_functional_boxplot(
                data_path=curves_2d,
                method=method
            )
            assert result["status"] == "success"
            assert result["_vis_params"]["method"] == method
            plt.close('all')


class TestCurveBoxplotInterface:
    """Test plot_curve_boxplot interface with UVisBox."""

    def test_returns_success_with_2d_curves(self, curves_2d):
        """Verify 2D curves are converted to 3D and plotted."""
        result = plot_curve_boxplot(data_path=curves_2d)

        assert result["status"] == "success"
        assert "_vis_params" in result
        assert result["_vis_params"]["_tool_name"] == "plot_curve_boxplot"

        plt.close('all')

    def test_returns_success_with_3d_curves(self, curves_3d):
        """Verify 3D curve data works directly."""
        result = plot_curve_boxplot(data_path=curves_3d)

        assert result["status"] == "success"
        assert isinstance(result["message"], str)

        plt.close('all')

    def test_returns_error_with_missing_file(self):
        """Verify error handling for missing file."""
        result = plot_curve_boxplot(data_path="missing.npy")

        assert result["status"] == "error"
        assert "not found" in result["message"].lower()


class TestProbabilisticMarchingSquaresInterface:
    """Test plot_probabilistic_marching_squares interface with UVisBox."""

    def test_returns_success_with_valid_field(self, scalar_field_3d):
        """Verify PMS visualization with valid scalar field."""
        result = plot_probabilistic_marching_squares(
            data_path=scalar_field_3d,
            isovalue=0.5
        )

        assert result["status"] == "success"
        assert "_vis_params" in result
        assert result["_vis_params"]["_tool_name"] == "plot_probabilistic_marching_squares"
        assert result["_vis_params"]["isovalue"] == 0.5

        plt.close('all')

    def test_returns_error_with_wrong_shape(self, curves_2d):
        """Verify error when data is not 3D."""
        result = plot_probabilistic_marching_squares(data_path=curves_2d)

        assert result["status"] == "error"
        assert "3d" in result["message"].lower() or "shape" in result["message"].lower()


class TestUncertaintyLobesInterface:
    """Test plot_uncertainty_lobes interface with UVisBox."""

    def test_returns_success_with_valid_data(self, vectors_and_positions):
        """Verify uncertainty lobes with valid vector ensemble."""
        vectors_path, positions_path = vectors_and_positions

        result = plot_uncertainty_lobes(
            vectors_path=vectors_path,
            positions_path=positions_path,
            percentile1=90,
            percentile2=50
        )

        assert result["status"] == "success"
        assert "_vis_params" in result
        assert result["_vis_params"]["_tool_name"] == "plot_uncertainty_lobes"
        assert result["_vis_params"]["percentile1"] == 90
        assert result["_vis_params"]["percentile2"] == 50

        plt.close('all')

    def test_returns_error_with_missing_vectors(self, vectors_and_positions):
        """Verify error when vectors file missing."""
        _, positions_path = vectors_and_positions

        result = plot_uncertainty_lobes(
            vectors_path="missing.npy",
            positions_path=positions_path
        )

        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    def test_returns_error_with_missing_positions(self, vectors_and_positions):
        """Verify error when positions file missing."""
        vectors_path, _ = vectors_and_positions

        result = plot_uncertainty_lobes(
            vectors_path=vectors_path,
            positions_path="missing.npy"
        )

        assert result["status"] == "error"
        assert "not found" in result["message"].lower()


class TestSquidGlyphInterface:
    """Test plot_squid_glyph_2D interface with UVisBox."""

    def test_returns_success_with_valid_data(self, vectors_and_positions):
        """Verify squid glyphs with valid vector ensemble."""
        vectors_path, positions_path = vectors_and_positions

        result = plot_squid_glyph_2D(
            vectors_path=vectors_path,
            positions_path=positions_path,
            percentile=95
        )

        assert result["status"] == "success"
        assert "_vis_params" in result
        assert result["_vis_params"]["_tool_name"] == "plot_squid_glyph_2D"
        assert result["_vis_params"]["percentile"] == 95

        plt.close('all')

    def test_returns_error_with_missing_file(self, vectors_and_positions):
        """Verify error handling for missing files."""
        _, positions_path = vectors_and_positions

        result = plot_squid_glyph_2D(
            vectors_path="missing.npy",
            positions_path=positions_path
        )

        assert result["status"] == "error"


class TestContourBoxplotInterface:
    """Test plot_contour_boxplot interface with UVisBox."""

    def test_returns_success_with_valid_field(self, scalar_field_3d):
        """Verify contour boxplot with valid scalar field."""
        result = plot_contour_boxplot(
            data_path=scalar_field_3d,
            isovalue=0.5,
            percentiles=[25, 50, 75, 90]
        )

        assert result["status"] == "success"
        assert "_vis_params" in result
        assert result["_vis_params"]["_tool_name"] == "plot_contour_boxplot"
        assert result["_vis_params"]["isovalue"] == 0.5
        assert result["_vis_params"]["percentiles"] == [25, 50, 75, 90]

        plt.close('all')

    def test_returns_error_with_invalid_shape(self, curves_2d):
        """Verify error when data is not 3D."""
        result = plot_contour_boxplot(
            data_path=curves_2d,
            isovalue=0.5
        )

        assert result["status"] == "error"
        assert "shape" in result["message"].lower() or "3d" in result["message"].lower()


# ============================================================================
# Test Runner
# ============================================================================

def run_all_interface_tests():
    """Run all interface tests."""
    print("\n" + "🔌"*35)
    print("TOOL INTERFACE TESTS (Layer 1)")
    print("🔌"*35)
    print("\nTesting direct tool-to-UVisBox interface...")
    print("These tests catch UVisBox API changes.\n")

    # Run pytest programmatically
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-k", "test_"
    ])

    plt.close('all')

    return exit_code


if __name__ == "__main__":
    exit_code = run_all_interface_tests()
    sys.exit(exit_code)
