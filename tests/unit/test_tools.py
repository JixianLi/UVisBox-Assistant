"""Unit tests for data_tools and vis_tools."""

import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from uvisbox_assistant.data_tools import (
    generate_ensemble_curves,
    generate_scalar_field_ensemble,
    generate_vector_field_ensemble,
    clear_session
)
from uvisbox_assistant.vis_tools import (
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
