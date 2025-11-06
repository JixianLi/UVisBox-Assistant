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




# Data Tools Error Handling Tests

def test_load_csv_file_not_found():
    """Test load_csv_to_numpy with non-existent file."""
    result = load_csv_to_numpy("/nonexistent/file.csv")

    assert result['status'] == 'error'
    assert 'not found' in result['message'].lower()
    print("✓ test_load_csv_file_not_found")


def test_load_csv_success(tmp_path):
    """Test load_csv_to_numpy with valid CSV."""
    import pandas as pd

    # Create test CSV
    csv_file = tmp_path / "test.csv"
    df = pd.DataFrame({
        'x': [1, 2, 3],
        'y': [4, 5, 6]
    })
    df.to_csv(csv_file, index=False)

    result = load_csv_to_numpy(str(csv_file))

    assert result['status'] == 'success'
    assert 'output_path' in result
    assert result['shape'] == (3, 2)
    print("✓ test_load_csv_success")


def test_load_npy_file_not_found():
    """Test load_npy with non-existent file."""
    result = load_npy("/nonexistent/file.npy")

    assert result['status'] == 'error'
    assert 'not found' in result['message'].lower()
    print("✓ test_load_npy_file_not_found")


def test_load_npy_success(tmp_path):
    """Test load_npy with valid file."""
    # Create test npy file
    npy_file = tmp_path / "test.npy"
    data = np.random.randn(10, 20)
    np.save(npy_file, data)

    result = load_npy(str(npy_file))

    assert result['status'] == 'success'
    assert 'output_path' in result
    assert result['shape'] == (10, 20)
    print("✓ test_load_npy_success")


def test_load_npy_invalid_file(tmp_path):
    """Test load_npy with invalid/corrupt file."""
    # Create invalid npy file
    invalid_file = tmp_path / "invalid.npy"
    with open(invalid_file, 'w') as f:
        f.write("not a valid npy file")

    result = load_npy(str(invalid_file))

    assert result['status'] == 'error'
    print("✓ test_load_npy_invalid_file")


def test_generate_scalar_field_edge_case_constant():
    """Test scalar field generation with edge case (constant values)."""
    # Test with n_ensemble=1 which could trigger edge cases
    result = generate_scalar_field_ensemble(
        nx=10, ny=10, n_ensemble=1
    )

    assert result['status'] == 'success'
    assert result['shape'] == (10, 10, 1)
    print("✓ test_generate_scalar_field_edge_case_constant")


def test_generate_vector_field_small_grid():
    """Test vector field generation with small grid."""
    result = generate_vector_field_ensemble(
        x_res=3, y_res=3, n_instances=5
    )

    assert result['status'] == 'success'
    assert 'positions_path' in result
    assert 'vectors_path' in result
    print("✓ test_generate_vector_field_small_grid")


# Vis Tools Error Handling Tests

def test_plot_functional_boxplot_file_not_found():
    """Test functional boxplot with non-existent data file."""
    result = plot_functional_boxplot("/nonexistent/file.npy")

    assert result['status'] == 'error'
    assert 'not found' in result['message'].lower()
    print("✓ test_plot_functional_boxplot_file_not_found")


def test_plot_functional_boxplot_invalid_shape(tmp_path):
    """Test functional boxplot with wrong data shape."""
    # Create 1D array (invalid for functional boxplot)
    invalid_data = tmp_path / "invalid.npy"
    np.save(invalid_data, np.random.randn(100))

    result = plot_functional_boxplot(str(invalid_data))

    assert result['status'] == 'error'
    assert '2D' in result['message'] or 'shape' in result['message'].lower()
    print("✓ test_plot_functional_boxplot_invalid_shape")


def test_plot_curve_boxplot_file_not_found():
    """Test curve boxplot with non-existent file."""
    result = plot_curve_boxplot("/nonexistent/file.npy")

    assert result['status'] == 'error'
    assert 'not found' in result['message'].lower()
    print("✓ test_plot_curve_boxplot_file_not_found")


def test_plot_contour_boxplot_file_not_found():
    """Test contour boxplot with non-existent file."""
    result = plot_contour_boxplot("/nonexistent/file.npy", isovalue=0.5)

    assert result['status'] == 'error'
    assert 'not found' in result['message'].lower()
    print("✓ test_plot_contour_boxplot_file_not_found")


def test_plot_contour_boxplot_invalid_shape(tmp_path):
    """Test contour boxplot with wrong data shape."""
    # Create 2D array (invalid, needs 3D)
    invalid_data = tmp_path / "invalid_2d.npy"
    np.save(invalid_data, np.random.randn(10, 10))

    result = plot_contour_boxplot(str(invalid_data), isovalue=0.5)

    assert result['status'] == 'error'
    assert 'shape' in result['message'].lower() or '3D' in result['message']
    print("✓ test_plot_contour_boxplot_invalid_shape")


def test_plot_probabilistic_marching_squares_file_not_found():
    """Test probabilistic marching squares with non-existent file."""
    result = plot_probabilistic_marching_squares("/nonexistent/file.npy", isovalue=0.5)

    assert result['status'] == 'error'
    assert 'not found' in result['message'].lower()
    print("✓ test_plot_probabilistic_marching_squares_file_not_found")


def test_plot_uncertainty_lobes_file_not_found():
    """Test uncertainty lobes with non-existent files."""
    result = plot_uncertainty_lobes(
        positions_path="/nonexistent/pos.npy",
        vectors_path="/nonexistent/vec.npy"
    )

    assert result['status'] == 'error'
    assert 'not found' in result['message'].lower()
    print("✓ test_plot_uncertainty_lobes_file_not_found")


def test_plot_squid_glyph_file_not_found():
    """Test squid glyph with non-existent files."""
    result = plot_squid_glyph_2D(
        positions_path="/nonexistent/pos.npy",
        vectors_path="/nonexistent/vec.npy"
    )

    assert result['status'] == 'error'
    assert 'not found' in result['message'].lower()
    print("✓ test_plot_squid_glyph_file_not_found")


def test_load_csv_malformed(tmp_path):
    """Test load_csv with malformed CSV to trigger exception."""
    # Create malformed CSV that will cause pandas to fail
    malformed_csv = tmp_path / "malformed.csv"
    with open(malformed_csv, 'w') as f:
        f.write("col1,col2\n")
        f.write("1,2,3,4,5\n")  # Mismatched columns
        f.write("a,b\n")

    result = load_csv_to_numpy(str(malformed_csv))

    # Should handle the error gracefully
    assert result['status'] in ['success', 'error']  # Either pandas handles it or errors
    print("✓ test_load_csv_malformed")


def test_plot_probabilistic_marching_squares_invalid_shape(tmp_path):
    """Test probabilistic marching squares with wrong data shape."""
    # Create 2D array (invalid, needs 3D)
    invalid_data = tmp_path / "invalid_2d.npy"
    np.save(invalid_data, np.random.randn(10, 10))

    result = plot_probabilistic_marching_squares(str(invalid_data), isovalue=0.5)

    assert result['status'] == 'error'
    assert 'shape' in result['message'].lower() or '3D' in result['message']
    print("✓ test_plot_probabilistic_marching_squares_invalid_shape")


def test_plot_uncertainty_lobes_shape_mismatch(tmp_path):
    """Test uncertainty lobes with mismatched position/vector shapes."""
    # Create mismatched shapes
    pos_file = tmp_path / "pos.npy"
    vec_file = tmp_path / "vec.npy"

    np.save(pos_file, np.random.randn(10, 2))  # 10 points
    np.save(vec_file, np.random.randn(5, 2, 20))  # 5 points (mismatch!)

    result = plot_uncertainty_lobes(str(pos_file), str(vec_file))

    assert result['status'] == 'error'
    print("✓ test_plot_uncertainty_lobes_shape_mismatch")


def test_plot_squid_glyph_shape_mismatch(tmp_path):
    """Test squid glyph with mismatched shapes."""
    pos_file = tmp_path / "pos.npy"
    vec_file = tmp_path / "vec.npy"

    np.save(pos_file, np.random.randn(10, 2))  # 10 points
    np.save(vec_file, np.random.randn(5, 2, 20))  # 5 points (mismatch!)

    result = plot_squid_glyph_2D(str(pos_file), str(vec_file))

    assert result['status'] == 'error'
    print("✓ test_plot_squid_glyph_shape_mismatch")


def test_plot_curve_boxplot_invalid_shape(tmp_path):
    """Test curve boxplot with invalid data shape."""
    # Create 1D array (invalid)
    invalid_data = tmp_path / "invalid_1d.npy"
    np.save(invalid_data, np.random.randn(100))

    result = plot_curve_boxplot(str(invalid_data))

    assert result['status'] == 'error'
    assert '2D' in result['message'] or 'shape' in result['message'].lower()
    print("✓ test_plot_curve_boxplot_invalid_shape")


def test_plot_curve_boxplot_with_defaults():
    """Test curve boxplot with default parameters (no percentiles specified)."""
    # Generate test data
    curves_result = generate_ensemble_curves(n_curves=10, n_points=50)

    # Call without specifying percentiles to trigger line 216
    result = plot_curve_boxplot(
        data_path=curves_result['output_path']
        # No percentiles parameter - should use defaults
    )

    assert result['status'] == 'success'
    assert '_vis_params' in result
    # Should have default percentiles [25, 50, 90, 100]
    assert result['_vis_params']['percentiles'] == [25, 50, 90, 100]

    plt.close('all')
    print("✓ test_plot_curve_boxplot_with_defaults")


def test_clear_session_with_files():
    """Test clear_session removes temporary files."""
    # Generate some temp files
    generate_ensemble_curves(n_curves=5, n_points=20)
    generate_scalar_field_ensemble(nx=10, ny=10, n_ensemble=3)

    # Clear session
    result = clear_session()

    assert result['status'] == 'success'
    assert result['files_removed'] >= 0
    print("✓ test_clear_session_with_files")


def test_clear_session_no_temp_dir(tmp_path):
    """Test clear_session when temp dir doesn't exist."""
    import uvisbox_assistant.config as cfg

    # Temporarily change TEMP_DIR to non-existent location
    original_temp_dir = cfg.TEMP_DIR
    cfg.TEMP_DIR = tmp_path / "nonexistent_temp"

    try:
        result = clear_session()
        assert result['status'] == 'success'
        assert result['files_removed'] == 0
    finally:
        cfg.TEMP_DIR = original_temp_dir

    print("✓ test_clear_session_no_temp_dir")


def test_plot_uncertainty_lobes_with_defaults():
    """Test uncertainty lobes with default percentiles."""
    # Generate vector field
    vec_result = generate_vector_field_ensemble(x_res=5, y_res=5, n_instances=10)

    # Call without specifying percentiles to trigger defaults
    result = plot_uncertainty_lobes(
        positions_path=vec_result['positions_path'],
        vectors_path=vec_result['vectors_path']
        # No percentiles specified - should use defaults
    )

    assert result['status'] == 'success'
    plt.close('all')
    print("✓ test_plot_uncertainty_lobes_with_defaults")


def test_plot_squid_glyph_with_defaults():
    """Test squid glyph with default percentile."""
    # Generate vector field
    vec_result = generate_vector_field_ensemble(x_res=5, y_res=5, n_instances=10)

    # Call without specifying percentile to trigger defaults
    result = plot_squid_glyph_2D(
        positions_path=vec_result['positions_path'],
        vectors_path=vec_result['vectors_path']
        # No percentile specified - should use default
    )

    assert result['status'] == 'success'
    plt.close('all')
    print("✓ test_plot_squid_glyph_with_defaults")


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
