"""Unit tests for data_tools and vis_tools."""

import sys
from pathlib import Path
import numpy as np
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from uvisbox_assistant.tools.data_tools import (
    generate_ensemble_curves,
    generate_scalar_field_ensemble,
    generate_vector_field_ensemble,
    clear_session,
    load_csv_to_numpy,
    load_npy
)
from uvisbox_assistant.tools.vis_tools import (
    plot_functional_boxplot,
    plot_curve_boxplot,
    plot_contour_boxplot,
    plot_probabilistic_marching_squares,
    plot_uncertainty_lobes,
    plot_squid_glyph_2D
)
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# ============================================================================
# Unit Tests for data_tools and vis_tools (0 UVisBox calls)
#
# These tests mock all external dependencies (UVisBox, file I/O) to test
# wrapper logic in isolation:
# - Default parameter application
# - Validation logic
# - Error handling and propagation
# - Return structure correctness
#
# Real UVisBox integration is tested in tests/uvisbox_interface/
# ============================================================================


# ============================================================================
# Visualization Tools - Mocked Unit Tests
# ============================================================================

class TestPlotFunctionalBoxplot:
    """Unit tests for plot_functional_boxplot (0 UVisBox calls)."""

    @patch('uvisbox_assistant.tools.vis_tools.BoxplotStyleConfig', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.functional_boxplot', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_default_percentiles_applied(self, mock_load_array, mock_path, mock_uvisbox, mock_config):
        """Test percentiles=None applies default [25, 50, 90, 100]."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(10, 50), None)

        # Act
        result = plot_functional_boxplot(data_path="curves.npy")

        # Assert
        assert result['status'] == 'success'
        assert result['_vis_params']['percentiles'] == [25, 50, 90, 100]
        mock_uvisbox.assert_called_once()

    @patch('uvisbox_assistant.tools.vis_tools.BoxplotStyleConfig', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.functional_boxplot', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_custom_percentiles_preserved(self, mock_load_array, mock_path, mock_uvisbox, mock_config):
        """Test custom percentiles are not overridden."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(10, 50), None)

        # Act
        result = plot_functional_boxplot(
            data_path="curves.npy",
            percentiles=[10, 50, 90]
        )

        # Assert
        assert result['status'] == 'success'
        assert result['_vis_params']['percentiles'] == [10, 50, 90]
        mock_uvisbox.assert_called_once()

    @patch('uvisbox_assistant.tools.vis_tools.BoxplotStyleConfig', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.functional_boxplot', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_data_loading_error_propagated(self, mock_load_array, mock_path, mock_uvisbox, mock_config):
        """Test load_array error returns error dict."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (False, None, "File not found: curves.npy")

        # Act
        result = plot_functional_boxplot(data_path="curves.npy")

        # Assert
        assert result['status'] == 'error'
        assert "File not found" in result['message']
        mock_uvisbox.assert_not_called()

    @patch('uvisbox_assistant.tools.vis_tools.BoxplotStyleConfig', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.functional_boxplot', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_wrong_shape_validation(self, mock_load_array, mock_path, mock_uvisbox, mock_config):
        """Test 3D array rejected with error message."""
        # Arrange - return 3D array instead of required 2D
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(10, 50, 3), None)

        # Act
        result = plot_functional_boxplot(data_path="curves.npy")

        # Assert
        assert result['status'] == 'error'
        assert '2D' in result['message'] or 'shape' in result['message'].lower()
        mock_uvisbox.assert_not_called()

    @patch('uvisbox_assistant.tools.vis_tools.BoxplotStyleConfig', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.functional_boxplot', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_uvisbox_exception_handled(self, mock_load_array, mock_path, mock_uvisbox, mock_config):
        """Test UVisBox exception caught and returned as error dict."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(10, 50), None)
        mock_uvisbox.side_effect = RuntimeError("UVisBox internal error")

        # Act
        result = plot_functional_boxplot(data_path="curves.npy")

        # Assert
        assert result['status'] == 'error'
        assert 'error' in result['message'].lower()
        assert '_error_details' in result
        mock_uvisbox.assert_called_once()


class TestPlotCurveBoxplot:
    """Unit tests for plot_curve_boxplot (0 UVisBox calls)."""

    @patch('uvisbox_assistant.tools.vis_tools.BoxplotStyleConfig', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.curve_boxplot', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_data_loading_error_propagated(self, mock_load_array, mock_path, mock_uvisbox, mock_config):
        """Test load_array error returns error dict."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (False, None, "File not found: curves.npy")

        # Act
        result = plot_curve_boxplot(data_path="curves.npy")

        # Assert
        assert result['status'] == 'error'
        assert "File not found" in result['message']
        mock_uvisbox.assert_not_called()

    @patch('uvisbox_assistant.tools.vis_tools.BoxplotStyleConfig', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.curve_boxplot', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_2d_curves_accepted(self, mock_load_array, mock_path, mock_uvisbox, mock_config):
        """Test 2D curves (n_curves, n_points) are accepted."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(10, 50), None)

        # Act
        result = plot_curve_boxplot(data_path="curves.npy")

        # Assert
        assert result['status'] == 'success'
        assert result['_vis_params']['_tool_name'] == 'plot_curve_boxplot'
        mock_uvisbox.assert_called_once()

    @patch('uvisbox_assistant.tools.vis_tools.BoxplotStyleConfig', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.curve_boxplot', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_3d_curves_accepted(self, mock_load_array, mock_path, mock_uvisbox, mock_config):
        """Test 3D curves (n_curves, n_points, 3) are accepted."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(10, 50, 3), None)

        # Act
        result = plot_curve_boxplot(data_path="curves.npy")

        # Assert
        assert result['status'] == 'success'
        assert result['_vis_params']['_tool_name'] == 'plot_curve_boxplot'
        mock_uvisbox.assert_called_once()

    @patch('uvisbox_assistant.tools.vis_tools.BoxplotStyleConfig', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.curve_boxplot', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_wrong_shape_validation(self, mock_load_array, mock_path, mock_uvisbox, mock_config):
        """Test 1D array rejected with error message."""
        # Arrange - return 1D array
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(50), None)

        # Act
        result = plot_curve_boxplot(data_path="curves.npy")

        # Assert
        assert result['status'] == 'error'
        assert 'shape' in result['message'].lower()
        mock_uvisbox.assert_not_called()

    @patch('uvisbox_assistant.tools.vis_tools.BoxplotStyleConfig', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.curve_boxplot', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_uvisbox_exception_handled(self, mock_load_array, mock_path, mock_uvisbox, mock_config):
        """Test UVisBox exception caught and returned as error dict."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(10, 50), None)
        mock_uvisbox.side_effect = ValueError("Invalid curve data")

        # Act
        result = plot_curve_boxplot(data_path="curves.npy")

        # Assert
        assert result['status'] == 'error'
        assert '_error_details' in result
        mock_uvisbox.assert_called_once()


class TestPlotContourBoxplot:
    """Unit tests for plot_contour_boxplot (0 UVisBox calls)."""

    @patch('uvisbox_assistant.tools.vis_tools.BoxplotStyleConfig', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.contour_boxplot', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_explicit_isovalue_used(self, mock_load_array, mock_path, mock_uvisbox, mock_config):
        """Test explicit isovalue parameter is used."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(20, 20, 10), None)

        # Act
        result = plot_contour_boxplot(data_path="field.npy", isovalue=0.3)

        # Assert
        assert result['status'] == 'success'
        assert result['_vis_params']['isovalue'] == 0.3
        mock_uvisbox.assert_called_once()

    @patch('uvisbox_assistant.tools.vis_tools.BoxplotStyleConfig', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.contour_boxplot', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_data_loading_error_propagated(self, mock_load_array, mock_path, mock_uvisbox, mock_config):
        """Test load_array error returns error dict."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (False, None, "File not found: field.npy")

        # Act
        result = plot_contour_boxplot(data_path="field.npy", isovalue=0.5)

        # Assert
        assert result['status'] == 'error'
        assert "File not found" in result['message']
        mock_uvisbox.assert_not_called()

    @patch('uvisbox_assistant.tools.vis_tools.BoxplotStyleConfig', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.contour_boxplot', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_wrong_shape_validation(self, mock_load_array, mock_path, mock_uvisbox, mock_config):
        """Test 2D array rejected with error message."""
        # Arrange - return 2D array instead of required 3D
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(20, 20), None)

        # Act
        result = plot_contour_boxplot(data_path="field.npy", isovalue=0.5)

        # Assert
        assert result['status'] == 'error'
        assert '3D' in result['message'] or 'shape' in result['message'].lower()
        mock_uvisbox.assert_not_called()

    @patch('uvisbox_assistant.tools.vis_tools.BoxplotStyleConfig', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.contour_boxplot', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_uvisbox_exception_handled(self, mock_load_array, mock_path, mock_uvisbox, mock_config):
        """Test UVisBox exception caught and returned as error dict."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(20, 20, 10), None)
        mock_uvisbox.side_effect = RuntimeError("Contour extraction failed")

        # Act
        result = plot_contour_boxplot(data_path="field.npy", isovalue=0.5)

        # Assert
        assert result['status'] == 'error'
        assert '_error_details' in result
        mock_uvisbox.assert_called_once()


class TestPlotProbabilisticMarchingSquares:
    """Unit tests for plot_probabilistic_marching_squares (0 UVisBox calls)."""

    @patch('uvisbox_assistant.tools.vis_tools.probabilistic_marching_squares', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_default_isovalue_applied(self, mock_load_array, mock_path, mock_uvisbox):
        """Test isovalue=None applies default 0.5."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(20, 20, 10), None)

        # Act
        result = plot_probabilistic_marching_squares(data_path="field.npy")

        # Assert
        assert result['status'] == 'success'
        assert result['_vis_params']['isovalue'] == 0.5
        mock_uvisbox.assert_called_once()

    @patch('uvisbox_assistant.tools.vis_tools.probabilistic_marching_squares', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_data_loading_error_propagated(self, mock_load_array, mock_path, mock_uvisbox):
        """Test load_array error returns error dict."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (False, None, "File not found: field.npy")

        # Act
        result = plot_probabilistic_marching_squares(data_path="field.npy")

        # Assert
        assert result['status'] == 'error'
        assert "File not found" in result['message']
        mock_uvisbox.assert_not_called()

    @patch('uvisbox_assistant.tools.vis_tools.probabilistic_marching_squares', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_wrong_shape_validation(self, mock_load_array, mock_path, mock_uvisbox):
        """Test 2D array rejected with error message."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(20, 20), None)

        # Act
        result = plot_probabilistic_marching_squares(data_path="field.npy")

        # Assert
        assert result['status'] == 'error'
        assert '3D' in result['message'] or 'shape' in result['message'].lower()
        mock_uvisbox.assert_not_called()

    @patch('uvisbox_assistant.tools.vis_tools.probabilistic_marching_squares', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_uvisbox_exception_handled(self, mock_load_array, mock_path, mock_uvisbox):
        """Test UVisBox exception caught and returned as error dict."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(20, 20, 10), None)
        mock_uvisbox.side_effect = ValueError("Marching squares failed")

        # Act
        result = plot_probabilistic_marching_squares(data_path="field.npy")

        # Assert
        assert result['status'] == 'error'
        assert '_error_details' in result
        mock_uvisbox.assert_called_once()


class TestPlotUncertaintyLobes:
    """Unit tests for plot_uncertainty_lobes (0 UVisBox calls)."""

    @patch('uvisbox_assistant.tools.vis_tools.uncertainty_lobes', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_default_percentiles_applied(self, mock_load_array, mock_path, mock_uvisbox):
        """Test percentile1/percentile2 defaults to 90/50."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        positions = np.random.rand(25, 2)
        vectors = np.random.rand(25, 10, 2)
        mock_load_array.side_effect = [
            (True, vectors, None),
            (True, positions, None)
        ]

        # Act
        result = plot_uncertainty_lobes(
            vectors_path="vectors.npy",
            positions_path="positions.npy"
        )

        # Assert
        assert result['status'] == 'success'
        assert result['_vis_params']['percentile1'] == 90
        assert result['_vis_params']['percentile2'] == 50
        mock_uvisbox.assert_called_once()

    @patch('uvisbox_assistant.tools.vis_tools.uncertainty_lobes', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_vectors_loading_error_propagated(self, mock_load_array, mock_path, mock_uvisbox):
        """Test vectors load error returns error dict."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (False, None, "File not found: vectors.npy")

        # Act
        result = plot_uncertainty_lobes(
            vectors_path="vectors.npy",
            positions_path="positions.npy"
        )

        # Assert
        assert result['status'] == 'error'
        assert "File not found" in result['message']
        mock_uvisbox.assert_not_called()

    @patch('uvisbox_assistant.tools.vis_tools.uncertainty_lobes', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_uvisbox_shape_mismatch_exception(self, mock_load_array, mock_path, mock_uvisbox):
        """Test UVisBox exception when shapes mismatch."""
        # Arrange - mismatched shapes will cause UVisBox to throw exception
        mock_path.return_value.exists.return_value = True
        positions = np.random.rand(25, 2)  # 25 positions
        vectors = np.random.rand(30, 10, 2)  # 30 vectors (mismatch!)
        mock_load_array.side_effect = [
            (True, vectors, None),
            (True, positions, None)
        ]
        mock_uvisbox.side_effect = ValueError("Shape mismatch")

        # Act
        result = plot_uncertainty_lobes(
            vectors_path="vectors.npy",
            positions_path="positions.npy"
        )

        # Assert
        assert result['status'] == 'error'
        assert '_error_details' in result
        mock_uvisbox.assert_called_once()

    @patch('uvisbox_assistant.tools.vis_tools.uncertainty_lobes', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_uvisbox_exception_handled(self, mock_load_array, mock_path, mock_uvisbox):
        """Test UVisBox exception caught and returned as error dict."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        positions = np.random.rand(25, 2)
        vectors = np.random.rand(25, 10, 2)
        mock_load_array.side_effect = [
            (True, vectors, None),
            (True, positions, None)
        ]
        mock_uvisbox.side_effect = RuntimeError("UVisBox error")

        # Act
        result = plot_uncertainty_lobes(
            vectors_path="vectors.npy",
            positions_path="positions.npy"
        )

        # Assert
        assert result['status'] == 'error'
        assert '_error_details' in result
        mock_uvisbox.assert_called_once()


class TestPlotSquidGlyph2D:
    """Unit tests for plot_squid_glyph_2D (0 UVisBox calls)."""

    @patch('uvisbox_assistant.tools.vis_tools.squid_glyph_2D', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_default_percentile_applied(self, mock_load_array, mock_path, mock_uvisbox):
        """Test percentile defaults to 95."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        positions = np.random.rand(25, 2)
        vectors = np.random.rand(25, 10, 2)
        mock_load_array.side_effect = [
            (True, vectors, None),
            (True, positions, None)
        ]

        # Act
        result = plot_squid_glyph_2D(
            vectors_path="vectors.npy",
            positions_path="positions.npy"
        )

        # Assert
        assert result['status'] == 'success'
        assert result['_vis_params']['percentile'] == 95
        mock_uvisbox.assert_called_once()

    @patch('uvisbox_assistant.tools.vis_tools.squid_glyph_2D', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_vectors_loading_error_propagated(self, mock_load_array, mock_path, mock_uvisbox):
        """Test vectors load error returns error dict."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        mock_load_array.return_value = (False, None, "File not found: vectors.npy")

        # Act
        result = plot_squid_glyph_2D(
            vectors_path="vectors.npy",
            positions_path="positions.npy"
        )

        # Assert
        assert result['status'] == 'error'
        assert "File not found" in result['message']
        mock_uvisbox.assert_not_called()

    @patch('uvisbox_assistant.tools.vis_tools.squid_glyph_2D', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_uvisbox_shape_mismatch_exception(self, mock_load_array, mock_path, mock_uvisbox):
        """Test UVisBox exception when shapes mismatch."""
        # Arrange - mismatched shapes will cause UVisBox to throw exception
        mock_path.return_value.exists.return_value = True
        positions = np.random.rand(25, 2)
        vectors = np.random.rand(30, 10, 2)  # Mismatch
        mock_load_array.side_effect = [
            (True, vectors, None),
            (True, positions, None)
        ]
        mock_uvisbox.side_effect = ValueError("Shape mismatch")

        # Act
        result = plot_squid_glyph_2D(
            vectors_path="vectors.npy",
            positions_path="positions.npy"
        )

        # Assert
        assert result['status'] == 'error'
        assert '_error_details' in result
        mock_uvisbox.assert_called_once()

    @patch('uvisbox_assistant.tools.vis_tools.squid_glyph_2D', create=True)
    @patch('uvisbox_assistant.tools.vis_tools.Path')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_uvisbox_exception_handled(self, mock_load_array, mock_path, mock_uvisbox):
        """Test UVisBox exception caught and returned as error dict."""
        # Arrange
        mock_path.return_value.exists.return_value = True
        positions = np.random.rand(25, 2)
        vectors = np.random.rand(25, 10, 2)
        mock_load_array.side_effect = [
            (True, vectors, None),
            (True, positions, None)
        ]
        mock_uvisbox.side_effect = RuntimeError("Glyph generation failed")

        # Act
        result = plot_squid_glyph_2D(
            vectors_path="vectors.npy",
            positions_path="positions.npy"
        )

        # Assert
        assert result['status'] == 'error'
        assert '_error_details' in result
        mock_uvisbox.assert_called_once()


# Mocked exception tests to trigger error handlers

@patch('uvisbox_assistant.tools.vis_tools.functional_boxplot', create=True)
def test_plot_functional_boxplot_uvisbox_exception(mock_uvisbox, tmp_path):
    """Test functional boxplot with UVisBox exception to trigger error handler."""
    # Create valid data
    data = tmp_path / "data.npy"
    np.save(data, np.random.randn(10, 50))

    # Mock UVisBox to raise exception
    mock_uvisbox.side_effect = RuntimeError("UVisBox internal error")

    result = plot_functional_boxplot(str(data))

    assert result['status'] == 'error'
    assert 'error' in result['message'].lower()
    assert '_error_details' in result
    print("✓ test_plot_functional_boxplot_uvisbox_exception")


@patch('uvisbox_assistant.tools.vis_tools.curve_boxplot', create=True)
def test_plot_curve_boxplot_uvisbox_exception(mock_uvisbox, tmp_path):
    """Test curve boxplot with UVisBox exception."""
    data = tmp_path / "data.npy"
    np.save(data, np.random.randn(10, 50))

    mock_uvisbox.side_effect = ValueError("Invalid curve data")

    result = plot_curve_boxplot(str(data))

    assert result['status'] == 'error'
    assert '_error_details' in result
    print("✓ test_plot_curve_boxplot_uvisbox_exception")


@patch('uvisbox_assistant.tools.vis_tools.contour_boxplot', create=True)
def test_plot_contour_boxplot_uvisbox_exception(mock_uvisbox, tmp_path):
    """Test contour boxplot with UVisBox exception."""
    data = tmp_path / "data.npy"
    np.save(data, np.random.randn(5, 10, 10))

    mock_uvisbox.side_effect = RuntimeError("Contour extraction failed")

    result = plot_contour_boxplot(str(data), isovalue=0.5)

    assert result['status'] == 'error'
    assert '_error_details' in result
    print("✓ test_plot_contour_boxplot_uvisbox_exception")


@patch('uvisbox_assistant.tools.vis_tools.probabilistic_marching_squares', create=True)
def test_plot_probabilistic_marching_squares_uvisbox_exception(mock_uvisbox, tmp_path):
    """Test probabilistic marching squares with UVisBox exception."""
    data = tmp_path / "data.npy"
    np.save(data, np.random.randn(10, 10, 5))

    mock_uvisbox.side_effect = ValueError("Marching squares failed")

    result = plot_probabilistic_marching_squares(str(data), isovalue=0.5)

    assert result['status'] == 'error'
    assert '_error_details' in result
    print("✓ test_plot_probabilistic_marching_squares_uvisbox_exception")


# Data tools exception tests

@patch('pandas.read_csv')
def test_load_csv_pandas_exception(mock_read_csv, tmp_path):
    """Test load_csv with pandas exception to trigger error handler."""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("col1,col2\n1,2\n")

    # Mock pandas to raise exception
    mock_read_csv.side_effect = ValueError("Pandas parsing error")

    result = load_csv_to_numpy(str(csv_file))

    assert result['status'] == 'error'
    assert '_error_details' in result
    print("✓ test_load_csv_pandas_exception")


@patch('numpy.save')
def test_generate_ensemble_curves_save_exception(mock_save):
    """Test generate_ensemble_curves with save exception."""
    mock_save.side_effect = OSError("Disk full")

    result = generate_ensemble_curves(n_curves=5, n_points=20)

    assert result['status'] == 'error'
    assert '_error_details' in result
    print("✓ test_generate_ensemble_curves_save_exception")


@patch('numpy.save')
def test_generate_scalar_field_save_exception(mock_save):
    """Test generate_scalar_field_ensemble with save exception."""
    mock_save.side_effect = OSError("Permission denied")

    result = generate_scalar_field_ensemble(nx=10, ny=10, n_ensemble=3)

    assert result['status'] == 'error'
    assert '_error_details' in result
    print("✓ test_generate_scalar_field_save_exception")


@patch('uvisbox_assistant.utils.data_loading.load_array')
def test_load_npy_corrupt_data(mock_load_array, tmp_path):
    """Test load_npy with corrupt file to trigger exception."""
    npy_file = tmp_path / "corrupt.npy"
    npy_file.write_text("not valid npy data")

    # Mock load_array to return error
    mock_load_array.return_value = (False, None, "Error loading .npy file: Failed to load npy")

    result = load_npy(str(npy_file))

    assert result['status'] == 'error'
    assert 'Failed to load npy' in result['message']
    print("✓ test_load_npy_corrupt_data")


@patch('numpy.save')
def test_generate_vector_field_save_exception(mock_save):
    """Test generate_vector_field_ensemble with save exception."""
    # Mock to raise exception on save
    mock_save.side_effect = IOError("Cannot write to disk")

    result = generate_vector_field_ensemble(x_res=5, y_res=5, n_instances=5)

    assert result['status'] == 'error'
    assert '_error_details' in result
    print("✓ test_generate_vector_field_save_exception")


if __name__ == "__main__":
    print("Run tests with: poetry run pytest tests/unit/test_tools.py -v")
