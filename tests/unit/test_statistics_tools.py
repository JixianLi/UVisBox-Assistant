"""Unit tests for statistics_tools module (0 API calls)."""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
from uvisbox_assistant.tools.statistics_tools import (
    compute_functional_boxplot_statistics,
    _analyze_median_curve,
    _analyze_percentile_bands,
    _analyze_outliers,
    _group_consecutive_indices,
    STATISTICS_TOOLS,
    STATISTICS_TOOL_SCHEMAS
)


class TestStatisticsToolRegistry:
    """Test tool registry structure."""

    def test_statistics_tools_registry_exists(self):
        """Verify STATISTICS_TOOLS dict exists."""
        assert isinstance(STATISTICS_TOOLS, dict)
        assert len(STATISTICS_TOOLS) > 0

    def test_compute_statistics_in_registry(self):
        """Verify compute_functional_boxplot_statistics is registered."""
        assert "compute_functional_boxplot_statistics" in STATISTICS_TOOLS
        assert callable(STATISTICS_TOOLS["compute_functional_boxplot_statistics"])


class TestStatisticsToolSchemas:
    """Test tool schemas for LLM binding."""

    def test_schemas_list_exists(self):
        """Verify STATISTICS_TOOL_SCHEMAS is a list."""
        assert isinstance(STATISTICS_TOOL_SCHEMAS, list)
        assert len(STATISTICS_TOOL_SCHEMAS) > 0

    def test_compute_statistics_schema(self):
        """Verify compute_functional_boxplot_statistics schema."""
        schema = STATISTICS_TOOL_SCHEMAS[0]
        assert schema["name"] == "compute_functional_boxplot_statistics"
        assert "description" in schema
        assert "parameters" in schema

        params = schema["parameters"]["properties"]
        assert "data_path" in params
        assert "method" in params

        # Verify required fields
        assert "data_path" in schema["parameters"]["required"]


class TestAnalyzeMedianCurve:
    """Test median curve analysis helper."""

    def test_increasing_trend(self):
        """Test detection of increasing trend."""
        median = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = _analyze_median_curve(median)

        assert result["trend"] == "increasing"
        assert result["overall_slope"] > 0
        assert "value_range" in result
        assert result["value_range"] == (1.0, 5.0)

    def test_decreasing_trend(self):
        """Test detection of decreasing trend."""
        median = np.array([5.0, 4.0, 3.0, 2.0, 1.0])
        result = _analyze_median_curve(median)

        assert result["trend"] == "decreasing"
        assert result["overall_slope"] < 0

    def test_stationary_trend(self):
        """Test detection of stationary trend."""
        median = np.array([2.0, 2.1, 1.9, 2.0, 2.05])
        result = _analyze_median_curve(median)

        assert result["trend"] == "stationary"
        assert abs(result["overall_slope"]) < 0.1

    def test_smoothness_high(self):
        """Test high smoothness detection (linear curve)."""
        median = np.linspace(0, 10, 100)
        result = _analyze_median_curve(median)

        # Linear curve should have high smoothness (consistent gradients)
        assert result["smoothness_score"] > 0.9

    def test_smoothness_low(self):
        """Test low smoothness detection (noisy curve)."""
        np.random.seed(42)
        median = np.random.randn(100).cumsum()  # Random walk (noisy)
        result = _analyze_median_curve(median)

        # Noisy curve should have lower smoothness
        assert result["smoothness_score"] < 0.9

    def test_fluctuation_level(self):
        """Test fluctuation level computation."""
        median = np.array([1.0, 5.0, 1.0, 5.0, 1.0])
        result = _analyze_median_curve(median)

        # High fluctuation relative to range
        assert result["fluctuation_level"] > 0.3


class TestGroupConsecutiveIndices:
    """Test consecutive index grouping helper."""

    def test_single_group(self):
        """Test single consecutive group."""
        indices = np.array([5, 6, 7, 8])
        result = _group_consecutive_indices(indices)

        assert result == [(5, 8)]

    def test_multiple_groups(self):
        """Test multiple consecutive groups."""
        indices = np.array([1, 2, 3, 10, 11, 20])
        result = _group_consecutive_indices(indices)

        assert result == [(1, 3), (10, 11), (20, 20)]

    def test_empty_indices(self):
        """Test empty input."""
        indices = np.array([])
        result = _group_consecutive_indices(indices)

        assert result == []


class TestAnalyzePercentileBands:
    """Test percentile band analysis helper."""

    def test_band_width_computation(self):
        """Test band width statistics."""
        bottom = np.array([1.0, 2.0, 3.0])
        top = np.array([2.0, 4.0, 5.0])
        bands = {"50_percentile_band": (bottom, top)}
        percentiles = [50]

        result = _analyze_percentile_bands(bands, percentiles)

        assert "band_widths" in result
        assert "50_percentile_band" in result["band_widths"]

        band_stats = result["band_widths"]["50_percentile_band"]
        # Widths are (2-1, 4-2, 5-3) = (1, 2, 2), mean = 5/3 ≈ 1.667
        assert abs(band_stats["mean_width"] - 5/3) < 0.001
        assert band_stats["max_width"] == 2.0
        assert band_stats["min_width"] == 1.0

    def test_msd_score(self):
        """Test overall MSD (Mean Squared Difference to median)."""
        bottom = np.array([0.0, 0.0, 0.0])
        top = np.array([1.0, 1.0, 1.0])
        bands = {"90_percentile_band": (bottom, top)}
        percentiles = [90]

        # Create test median and curves
        median = np.array([0.5, 0.5, 0.5])
        curves = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 1.0, 1.0],
            [0.5, 0.5, 0.5]
        ])

        result = _analyze_percentile_bands(bands, percentiles, median=median, curves=curves)

        # MSD should be non-negative
        assert result["overall_msd"] >= 0.0

    def test_widest_regions(self):
        """Test widest region detection."""
        # Create band with one wide region
        bottom = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        top = np.array([1.0, 1.0, 5.0, 5.0, 1.0])  # Wide in middle
        bands = {"75_percentile_band": (bottom, top)}
        percentiles = [75]

        result = _analyze_percentile_bands(bands, percentiles)

        # Should detect wide region
        assert len(result["widest_regions"]) > 0


class TestAnalyzeOutliers:
    """Test outlier analysis helper."""

    def test_no_outliers(self):
        """Test with no outliers."""
        median = np.array([1.0, 2.0, 3.0])
        sorted_curves = np.array([[1.0, 2.0, 3.0]] * 10)
        outliers = np.array([])

        result = _analyze_outliers(outliers, median, sorted_curves)

        assert result["count"] == 0
        assert result["outlier_percentage"] == 0.0
        assert result["median_similarity_mean"] is None

    def test_with_outliers(self):
        """Test with outliers."""
        median = np.array([1.0, 2.0, 3.0, 4.0])
        sorted_curves = np.array([[1.0, 2.0, 3.0, 4.0]] * 20)
        outliers = np.array([
            [5.0, 6.0, 7.0, 8.0],  # Positive offset
            [1.5, 2.5, 3.5, 4.5]   # Slight offset
        ])

        result = _analyze_outliers(outliers, median, sorted_curves)

        assert result["count"] == 2
        assert result["outlier_percentage"] == 10.0  # 2/20 * 100
        assert result["median_similarity_mean"] is not None
        assert -1.0 <= result["median_similarity_mean"] <= 1.0

    def test_outlier_similarity_to_median(self):
        """Test outlier-median similarity computation."""
        # Highly correlated outlier
        median = np.array([1.0, 2.0, 3.0, 4.0])
        outliers = np.array([[2.0, 4.0, 6.0, 8.0]])  # 2x median (perfect correlation)
        sorted_curves = np.array([[1.0, 2.0, 3.0, 4.0]] * 10)

        result = _analyze_outliers(outliers, median, sorted_curves)

        # Correlation should be very high (close to 1.0)
        assert result["median_similarity_mean"] > 0.99


class TestComputeFunctionalBoxplotStatistics:
    """Test main statistics computation function."""

    def test_file_not_found(self):
        """Test error handling for missing file."""
        result = compute_functional_boxplot_statistics("/nonexistent/path.npy")

        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    def test_invalid_shape(self, tmp_path):
        """Test error handling for wrong data shape."""
        # Create 1D array (invalid)
        data = np.random.randn(100)
        data_path = tmp_path / "invalid.npy"
        np.save(data_path, data)

        result = compute_functional_boxplot_statistics(str(data_path))

        assert result["status"] == "error"
        assert "2D array" in result["message"]

    @patch('uvisbox_assistant.tools.statistics_tools.functional_boxplot_summary_statistics')
    def test_successful_computation(self, mock_uvisbox, tmp_path):
        """Test successful statistics computation with mocked UVisBox."""
        # Create test data
        n_curves, n_points = 30, 100
        curves = np.random.randn(n_curves, n_points)
        data_path = tmp_path / "test_curves.npy"
        np.save(data_path, curves)

        # Mock UVisBox output
        mock_uvisbox.return_value = {
            "depths": np.random.rand(n_curves),
            "median": np.random.randn(n_points),
            "percentile_bands": {
                "50_percentile_band": (
                    np.random.randn(n_points),
                    np.random.randn(n_points) + 1.0
                ),
                "90_percentile_band": (
                    np.random.randn(n_points),
                    np.random.randn(n_points) + 2.0
                )
            },
            "outliers": np.random.randn(2, n_points),
            "sorted_curves": curves,
            "sorted_indices": np.arange(n_curves)
        }

        result = compute_functional_boxplot_statistics(str(data_path), method="fbd")

        # Verify success
        assert result["status"] == "success"
        assert "processed_statistics" in result

        # Verify structure
        summary = result["processed_statistics"]
        assert "data_shape" in summary
        assert summary["data_shape"]["n_curves"] == n_curves
        assert summary["data_shape"]["n_points"] == n_points

        assert "median" in summary
        assert "trend" in summary["median"]
        assert "overall_slope" in summary["median"]

        assert "bands" in summary
        assert "band_widths" in summary["bands"]

        assert "outliers" in summary
        assert "count" in summary["outliers"]

    @patch('uvisbox_assistant.tools.statistics_tools.functional_boxplot_summary_statistics')
    def test_no_numpy_arrays_in_output(self, mock_uvisbox, tmp_path):
        """Verify no numpy arrays in processed_statistics."""
        # Create test data
        curves = np.random.randn(30, 100)
        data_path = tmp_path / "test.npy"
        np.save(data_path, curves)

        # Mock UVisBox
        mock_uvisbox.return_value = {
            "depths": np.random.rand(30),
            "median": np.random.randn(100),
            "percentile_bands": {
                "50_percentile_band": (np.random.randn(100), np.random.randn(100) + 1.0)
            },
            "outliers": np.array([]),
            "sorted_curves": curves,
            "sorted_indices": np.arange(30)
        }

        result = compute_functional_boxplot_statistics(str(data_path))

        # Recursively check for numpy arrays in processed_statistics
        def has_numpy_array(obj):
            if isinstance(obj, np.ndarray):
                return True
            elif isinstance(obj, dict):
                return any(has_numpy_array(v) for v in obj.values())
            elif isinstance(obj, (list, tuple)):
                return any(has_numpy_array(item) for item in obj)
            return False

        assert not has_numpy_array(result["processed_statistics"]), \
            "processed_statistics should not contain numpy arrays"
