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

    @patch('pathlib.Path.exists')
    @patch('matplotlib.pyplot.pause')
    @patch('matplotlib.pyplot.show')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_default_percentiles_applied(self, mock_load_array, mock_show, mock_pause, mock_exists):
        """Test percentiles=None applies default [25, 50, 90, 100]."""
        # Arrange
        mock_exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(10, 50), None)

        # Mock functional_boxplot by injecting it into the module
        with patch.dict('sys.modules', {'uvisbox': MagicMock(), 'uvisbox.Modules': MagicMock(), 'uvisbox.Core.CommonInterface': MagicMock()}):
            import uvisbox_assistant.tools.vis_tools as vis_tools_module
            mock_uvisbox = MagicMock()
            vis_tools_module.functional_boxplot = mock_uvisbox
            vis_tools_module.BoxplotStyleConfig = MagicMock()

            # Act
            result = plot_functional_boxplot(data_path="curves.npy")

            # Assert
            assert result['status'] == 'success'
            assert result['_vis_params']['percentiles'] == [25, 50, 90, 100]

    @patch('pathlib.Path.exists')
    @patch('matplotlib.pyplot.pause')
    @patch('matplotlib.pyplot.show')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_custom_percentiles_preserved(self, mock_load_array, mock_show, mock_pause, mock_exists):
        """Test custom percentiles are not overridden."""
        # Arrange
        mock_exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(10, 50), None)

        with patch.dict('sys.modules', {'uvisbox': MagicMock(), 'uvisbox.Modules': MagicMock(), 'uvisbox.Core.CommonInterface': MagicMock()}):
            import uvisbox_assistant.tools.vis_tools as vis_tools_module
            mock_uvisbox = MagicMock()
            vis_tools_module.functional_boxplot = mock_uvisbox
            vis_tools_module.BoxplotStyleConfig = MagicMock()

            # Act
            result = plot_functional_boxplot(
                data_path="curves.npy",
                percentiles=[10, 50, 90]
            )

            # Assert
            assert result['status'] == 'success'
            assert result['_vis_params']['percentiles'] == [10, 50, 90]

    @patch('pathlib.Path.exists')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_data_loading_error_propagated(self, mock_load_array, mock_exists):
        """Test load_array error returns error dict."""
        # Arrange
        mock_exists.return_value = True
        mock_load_array.return_value = (False, None, "File not found: curves.npy")

        # Act
        result = plot_functional_boxplot(data_path="curves.npy")

        # Assert
        assert result['status'] == 'error'
        assert "File not found" in result['message']

    @patch('pathlib.Path.exists')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_wrong_shape_validation(self, mock_load_array, mock_exists):
        """Test 3D array rejected with error message."""
        # Arrange - return 3D array instead of required 2D
        mock_exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(10, 50, 3), None)

        # Act
        result = plot_functional_boxplot(data_path="curves.npy")

        # Assert
        assert result['status'] == 'error'
        assert '2D' in result['message'] or 'shape' in result['message'].lower()

    @patch('pathlib.Path.exists')
    @patch('matplotlib.pyplot.pause')
    @patch('matplotlib.pyplot.show')
    @patch('uvisbox_assistant.utils.data_loading.load_array')
    def test_uvisbox_exception_handled(self, mock_load_array, mock_show, mock_pause, mock_exists):
        """Test UVisBox exception caught and returned as error dict."""
        # Arrange
        mock_exists.return_value = True
        mock_load_array.return_value = (True, np.random.rand(10, 50), None)

        with patch.dict('sys.modules', {'uvisbox': MagicMock(), 'uvisbox.Modules': MagicMock(), 'uvisbox.Core.CommonInterface': MagicMock()}):
            import uvisbox_assistant.tools.vis_tools as vis_tools_module
            mock_uvisbox = MagicMock(side_effect=RuntimeError("UVisBox internal error"))
            vis_tools_module.functional_boxplot = mock_uvisbox
            vis_tools_module.BoxplotStyleConfig = MagicMock()

            # Act
            result = plot_functional_boxplot(data_path="curves.npy")

            # Assert
            assert result['status'] == 'error'
            assert 'error' in result['message'].lower()
            assert '_error_details' in result


# Mocked exception tests to trigger error handlers

@patch('uvisbox_assistant.tools.vis_tools.functional_boxplot')
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


@patch('uvisbox_assistant.tools.vis_tools.curve_boxplot')
def test_plot_curve_boxplot_uvisbox_exception(mock_uvisbox, tmp_path):
    """Test curve boxplot with UVisBox exception."""
    data = tmp_path / "data.npy"
    np.save(data, np.random.randn(10, 50))

    mock_uvisbox.side_effect = ValueError("Invalid curve data")

    result = plot_curve_boxplot(str(data))

    assert result['status'] == 'error'
    assert '_error_details' in result
    print("✓ test_plot_curve_boxplot_uvisbox_exception")


@patch('uvisbox_assistant.tools.vis_tools.contour_boxplot')
def test_plot_contour_boxplot_uvisbox_exception(mock_uvisbox, tmp_path):
    """Test contour boxplot with UVisBox exception."""
    data = tmp_path / "data.npy"
    np.save(data, np.random.randn(5, 10, 10))

    mock_uvisbox.side_effect = RuntimeError("Contour extraction failed")

    result = plot_contour_boxplot(str(data), isovalue=0.5)

    assert result['status'] == 'error'
    assert '_error_details' in result
    print("✓ test_plot_contour_boxplot_uvisbox_exception")


@patch('uvisbox_assistant.tools.vis_tools.probabilistic_marching_squares')
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
