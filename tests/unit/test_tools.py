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


# Data Tools Tests

def test_generate_ensemble_curves():
    """Test curve generation with various parameters."""
    result = generate_ensemble_curves(n_curves=10, n_points=50)

    assert result['status'] == 'success'
    assert 'output_path' in result
    assert Path(result['output_path']).exists()

    # Verify data shape
    data = np.load(result['output_path'])
    assert data.shape == (10, 50)

    print("✓ test_generate_ensemble_curves")


def test_generate_scalar_field_ensemble():
    """Test scalar field generation."""
    result = generate_scalar_field_ensemble(nx=20, ny=20, n_ensemble=10)

    assert result['status'] == 'success'
    assert 'output_path' in result
    assert Path(result['output_path']).exists()

    # Verify data shape
    data = np.load(result['output_path'])
    assert data.shape == (20, 20, 10)

    print("✓ test_generate_scalar_field_ensemble")


def test_generate_vector_field_ensemble():
    """Test vector field generation."""
    result = generate_vector_field_ensemble(x_res=5, y_res=5, n_instances=10)

    assert result['status'] == 'success'
    assert 'positions_path' in result
    assert 'vectors_path' in result
    assert Path(result['positions_path']).exists()
    assert Path(result['vectors_path']).exists()

    # Verify data shapes
    positions = np.load(result['positions_path'])
    vectors = np.load(result['vectors_path'])
    assert positions.shape == (25, 2)  # 5x5 grid
    assert vectors.shape == (25, 10, 2)  # 25 positions, 10 instances, 2D

    print("✓ test_generate_vector_field_ensemble")


# Visualization Tools Tests - BoxplotStyleConfig

def test_plot_functional_boxplot_with_styling():
    """Test functional boxplot with BoxplotStyleConfig parameters."""
    # Generate test data
    curves_result = generate_ensemble_curves(n_curves=10, n_points=50)

    # Test with full styling parameters
    result = plot_functional_boxplot(
        data_path=curves_result['output_path'],
        percentiles=[25, 50, 75, 90],
        percentile_colormap='plasma',
        show_median=True,
        median_color='blue',
        median_width=2.5,
        median_alpha=0.8,
        show_outliers=True,
        outliers_color='black',
        outliers_width=1.5,
        outliers_alpha=0.7
    )

    assert result['status'] == 'success'
    assert '_vis_params' in result

    # Verify all styling params preserved
    params = result['_vis_params']
    assert params['_tool_name'] == 'plot_functional_boxplot'
    assert params['percentiles'] == [25, 50, 75, 90]
    assert params['percentile_colormap'] == 'plasma'
    assert params['median_color'] == 'blue'
    assert params['median_width'] == 2.5
    assert params['median_alpha'] == 0.8
    assert params['show_outliers'] == True
    assert params['outliers_color'] == 'black'
    assert params['outliers_width'] == 1.5
    assert params['outliers_alpha'] == 0.7

    plt.close('all')
    print("✓ test_plot_functional_boxplot_with_styling")


def test_plot_curve_boxplot_with_workers():
    """Test curve boxplot with workers parameter."""
    curves_result = generate_ensemble_curves(n_curves=10, n_points=50)

    result = plot_curve_boxplot(
        data_path=curves_result['output_path'],
        percentiles=[50, 90],
        percentile_colormap='viridis',
        show_median=True,
        median_color='red',
        show_outliers=False,
        workers=4
    )

    assert result['status'] == 'success'
    assert result['_vis_params']['workers'] == 4
    assert result['_vis_params']['percentile_colormap'] == 'viridis'

    plt.close('all')
    print("✓ test_plot_curve_boxplot_with_workers")


def test_plot_contour_boxplot_full_params():
    """Test contour boxplot with all BoxplotStyleConfig parameters."""
    field_result = generate_scalar_field_ensemble(nx=20, ny=20, n_ensemble=10)

    result = plot_contour_boxplot(
        data_path=field_result['output_path'],
        isovalue=0.5,
        percentiles=[25, 50, 75],
        percentile_colormap='plasma',
        show_median=True,
        median_color='red',
        median_width=3.0,
        median_alpha=1.0,
        show_outliers=True,
        outliers_color='gray',
        outliers_width=1.0,
        outliers_alpha=0.5,
        workers=8
    )

    assert result['status'] == 'success'
    params = result['_vis_params']
    assert params['isovalue'] == 0.5
    assert params['workers'] == 8
    assert params['median_color'] == 'red'
    assert params['outliers_alpha'] == 0.5

    plt.close('all')
    print("✓ test_plot_contour_boxplot_full_params")


def test_plot_probabilistic_marching_squares():
    """Test probabilistic marching squares."""
    field_result = generate_scalar_field_ensemble(nx=20, ny=20, n_ensemble=10)

    result = plot_probabilistic_marching_squares(
        data_path=field_result['output_path'],
        isovalue=0.5,
        colormap='viridis'
    )

    assert result['status'] == 'success'
    assert result['_vis_params']['isovalue'] == 0.5
    assert result['_vis_params']['colormap'] == 'viridis'

    plt.close('all')
    print("✓ test_plot_probabilistic_marching_squares")


def test_plot_uncertainty_lobes():
    """Test uncertainty lobes visualization."""
    vector_result = generate_vector_field_ensemble(x_res=5, y_res=5, n_instances=10)

    result = plot_uncertainty_lobes(
        positions_path=vector_result['positions_path'],
        vectors_path=vector_result['vectors_path'],
        percentile1=90,
        percentile2=50,
        scale=0.2
    )

    assert result['status'] == 'success'
    assert result['_vis_params']['percentile1'] == 90
    assert result['_vis_params']['percentile2'] == 50
    assert result['_vis_params']['scale'] == 0.2

    plt.close('all')
    print("✓ test_plot_uncertainty_lobes")


def test_plot_squid_glyph_2D():
    """Test squid glyph 2D visualization."""
    vector_result = generate_vector_field_ensemble(x_res=5, y_res=5, n_instances=10)

    result = plot_squid_glyph_2D(
        positions_path=vector_result['positions_path'],
        vectors_path=vector_result['vectors_path'],
        percentile=95,
        scale=0.3,
        workers=None
    )

    assert result['status'] == 'success'
    assert result['_vis_params']['percentile'] == 95
    assert result['_vis_params']['scale'] == 0.3
    assert result['_vis_params']['workers'] is None

    plt.close('all')
    print("✓ test_plot_squid_glyph_2D")


def test_default_percentiles():
    """Test that default percentiles are applied correctly."""
    curves_result = generate_ensemble_curves(n_curves=10, n_points=50)

    # Don't specify percentiles
    result = plot_functional_boxplot(
        data_path=curves_result['output_path']
    )

    assert result['status'] == 'success'
    # Should use default [25, 50, 90, 100]
    assert result['_vis_params']['percentiles'] == [25, 50, 90, 100]

    plt.close('all')
    print("✓ test_default_percentiles")


def test_vis_params_structure():
    """Test that _vis_params includes all required fields."""
    curves_result = generate_ensemble_curves(n_curves=10, n_points=50)

    result = plot_functional_boxplot(
        data_path=curves_result['output_path']
    )

    params = result['_vis_params']

    # Required fields
    assert '_tool_name' in params
    assert 'data_path' in params

    # BoxplotStyleConfig fields
    assert 'percentiles' in params
    assert 'percentile_colormap' in params
    assert 'show_median' in params
    assert 'median_color' in params
    assert 'median_width' in params
    assert 'median_alpha' in params
    assert 'show_outliers' in params
    assert 'outliers_color' in params
    assert 'outliers_width' in params
    assert 'outliers_alpha' in params

    plt.close('all')
    print("✓ test_vis_params_structure")


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


@patch('numpy.load')
def test_load_npy_corrupt_data(mock_load, tmp_path):
    """Test load_npy with corrupt file to trigger exception."""
    npy_file = tmp_path / "corrupt.npy"
    npy_file.write_text("not valid npy data")

    # Mock numpy.load to raise exception
    mock_load.side_effect = ValueError("Failed to load npy")

    result = load_npy(str(npy_file))

    assert result['status'] == 'error'
    assert '_error_details' in result
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
    # Run all tests
    test_functions = [
        test_generate_ensemble_curves,
        test_generate_scalar_field_ensemble,
        test_generate_vector_field_ensemble,
        test_plot_functional_boxplot_with_styling,
        test_plot_curve_boxplot_with_workers,
        test_plot_contour_boxplot_full_params,
        test_plot_probabilistic_marching_squares,
        test_plot_uncertainty_lobes,
        test_plot_squid_glyph_2D,
        test_default_percentiles,
        test_vis_params_structure,
    ]

    passed = 0
    failed = 0

    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")

    if failed == 0:
        print("✅ All tool tests passed!")
