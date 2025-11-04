# Phase 2: Statistics Tool Implementation

## Overview

Implement the core statistical analysis logic in `compute_functional_boxplot_statistics()` function. This phase transforms raw UVisBox output (numpy arrays) into LLM-friendly structured summaries using scipy, numpy, and scikit-learn. Focus on three analysis categories: median behavior, percentile band characteristics, and outlier analysis.

## Goals

- Implement complete statistical analysis pipeline
- Process functional_boxplot_summary_statistics() output
- Generate LLM-friendly summaries (no numpy arrays)
- Create comprehensive unit tests (0 API calls)
- Achieve robust error handling

## Prerequisites

- Phase 1 completed (GraphState extended, statistics_tools.py structure created)
- UVisBox library with functional_boxplot_summary_statistics() available
- scipy, numpy, scikit-learn installed

## Implementation Plan

### Step 1: Implement Helper Functions for Statistical Analysis

**File**: `src/uvisbox_assistant/statistics_tools.py`

Add helper functions before the main tool function:

```python
def _analyze_median_curve(median: np.ndarray, x_values: Optional[np.ndarray] = None) -> Dict:
    """
    Analyze median curve characteristics.

    Computes:
    - Trend: overall direction (increasing/decreasing/stationary)
    - Fluctuation: amount of variation along curve
    - Smoothness: gradient consistency
    - Range: min/max values

    Args:
        median: 1D array of median curve values (shape: D)
        x_values: Optional 1D array of x-coordinates (shape: D)

    Returns:
        Dict with numeric summaries:
        - trend: str ("increasing" | "decreasing" | "stationary")
        - overall_slope: float (positive/negative/~0)
        - fluctuation_level: float (std of curve)
        - smoothness_score: float (0-1, higher = smoother)
        - value_range: tuple (min, max)
        - mean_value: float
    """
    if x_values is None:
        x_values = np.arange(len(median))

    # Compute overall trend using linear regression
    slope, intercept = np.polyfit(x_values, median, 1)

    # Determine trend category
    slope_threshold = 0.01 * (median.max() - median.min())  # 1% of range
    if slope > slope_threshold:
        trend = "increasing"
    elif slope < -slope_threshold:
        trend = "decreasing"
    else:
        trend = "stationary"

    # Fluctuation: standard deviation normalized by range
    value_range = median.max() - median.min()
    fluctuation = np.std(median)
    fluctuation_level = fluctuation / value_range if value_range > 0 else 0.0

    # Smoothness: inverse of gradient variability
    # Higher smoothness = more consistent gradients
    gradients = np.gradient(median)
    gradient_std = np.std(gradients)
    gradient_range = np.ptp(gradients)  # peak-to-peak
    smoothness_score = 1.0 / (1.0 + gradient_std) if gradient_std > 0 else 1.0

    return {
        "trend": trend,
        "overall_slope": float(slope),
        "fluctuation_level": float(fluctuation_level),
        "smoothness_score": float(smoothness_score),
        "value_range": (float(median.min()), float(median.max())),
        "mean_value": float(np.mean(median)),
        "std_value": float(np.std(median))
    }


def _analyze_percentile_bands(
    percentile_bands: Dict[str, Tuple[np.ndarray, np.ndarray]],
    percentiles: List[float]
) -> Dict:
    """
    Analyze percentile band characteristics.

    Computes:
    - Band widths (mean, max, min for each band)
    - Widest regions (where uncertainty is highest)
    - Inter-band gaps (proximity between different percentile levels)

    Args:
        percentile_bands: Dict mapping band names to (bottom, top) curve tuples
                         e.g., {"25_percentile_band": (bottom_array, top_array)}
        percentiles: List of percentile values (e.g., [25, 50, 90, 100])

    Returns:
        Dict with:
        - band_widths: Dict[str, Dict] with mean/max/min widths per band
        - widest_region_indices: List of (start, end) tuples for high-variation regions
        - overall_uncertainty_score: float (0-1, higher = more uncertain)
    """
    band_widths = {}
    all_widths = []

    for band_name, (bottom, top) in percentile_bands.items():
        width = top - bottom
        band_widths[band_name] = {
            "mean_width": float(np.mean(width)),
            "max_width": float(np.max(width)),
            "min_width": float(np.min(width)),
            "std_width": float(np.std(width)),
            "max_width_index": int(np.argmax(width))
        }
        all_widths.append(width)

    # Find widest regions (top 10% of widths)
    if all_widths:
        combined_widths = np.mean(all_widths, axis=0)  # Average across bands
        width_threshold = np.percentile(combined_widths, 90)  # Top 10%
        wide_indices = np.where(combined_widths >= width_threshold)[0]

        # Group consecutive indices into regions
        widest_regions = _group_consecutive_indices(wide_indices)
    else:
        widest_regions = []

    # Overall uncertainty score: mean normalized band width
    if all_widths:
        mean_combined_width = np.mean(combined_widths)
        # Normalize by data range (estimate from outermost band)
        outermost_band = list(percentile_bands.values())[-1]
        data_range = np.ptp(outermost_band[1])  # peak-to-peak of top curve
        uncertainty_score = mean_combined_width / data_range if data_range > 0 else 0.0
    else:
        uncertainty_score = 0.0

    return {
        "band_widths": band_widths,
        "widest_regions": widest_regions,
        "overall_uncertainty_score": float(uncertainty_score),
        "num_bands": len(percentile_bands)
    }


def _group_consecutive_indices(indices: np.ndarray) -> List[Tuple[int, int]]:
    """
    Group consecutive indices into (start, end) tuples.

    Args:
        indices: Array of sorted indices

    Returns:
        List of (start, end) tuples
    """
    if len(indices) == 0:
        return []

    groups = []
    start = indices[0]
    prev = indices[0]

    for idx in indices[1:]:
        if idx != prev + 1:
            # Gap detected, save current group
            groups.append((int(start), int(prev)))
            start = idx
        prev = idx

    # Save last group
    groups.append((int(start), int(prev)))

    return groups


def _analyze_outliers(
    outliers: np.ndarray,
    median: np.ndarray,
    sorted_curves: np.ndarray
) -> Dict:
    """
    Analyze outlier curve characteristics.

    Computes:
    - Outlier count
    - Similarity to median (using correlation)
    - Outlier clustering (are outliers similar to each other?)

    Args:
        outliers: Array of outlier curves (shape: n_outliers x D)
        median: Median curve (shape: D)
        sorted_curves: All curves sorted by depth (shape: N x D)

    Returns:
        Dict with:
        - count: int (number of outliers)
        - median_similarity_mean: float (mean correlation with median)
        - median_similarity_std: float (std of correlations)
        - intra_outlier_similarity: float (mean pairwise correlation among outliers)
        - outlier_percentage: float (outliers / total curves)
    """
    n_outliers = outliers.shape[0] if outliers.ndim == 2 else 0
    n_total = sorted_curves.shape[0]

    if n_outliers == 0:
        return {
            "count": 0,
            "median_similarity_mean": None,
            "median_similarity_std": None,
            "intra_outlier_similarity": None,
            "outlier_percentage": 0.0
        }

    # Similarity to median: Pearson correlation
    from scipy.stats import pearsonr
    median_correlations = []
    for outlier in outliers:
        corr, _ = pearsonr(outlier, median)
        median_correlations.append(corr)

    median_sim_mean = np.mean(median_correlations)
    median_sim_std = np.std(median_correlations)

    # Intra-outlier similarity: mean pairwise correlation
    if n_outliers > 1:
        # Use pairwise distances with correlation metric
        # sklearn uses 1 - correlation, so we convert back
        distances = pairwise_distances(outliers, metric='correlation')
        correlations = 1 - distances
        # Get upper triangle (exclude diagonal)
        upper_triangle = correlations[np.triu_indices_from(correlations, k=1)]
        intra_similarity = np.mean(upper_triangle)
    else:
        intra_similarity = None

    outlier_percentage = (n_outliers / n_total) * 100.0

    return {
        "count": int(n_outliers),
        "median_similarity_mean": float(median_sim_mean),
        "median_similarity_std": float(median_sim_std),
        "intra_outlier_similarity": float(intra_similarity) if intra_similarity is not None else None,
        "outlier_percentage": float(outlier_percentage)
    }
```

### Step 2: Implement Main Statistics Tool Function

**File**: `src/uvisbox_assistant/statistics_tools.py`

Replace the placeholder implementation:

```python
def compute_functional_boxplot_statistics(
    data_path: str,
    method: str = "fbd"
) -> Dict:
    """
    Compute functional boxplot summary statistics and process into LLM-friendly format.

    This tool:
    1. Calls UVisBox functional_boxplot_summary_statistics()
    2. Analyzes median curve behavior (trend, fluctuation, smoothness, range)
    3. Analyzes percentile band behavior (widths, variation regions, gaps)
    4. Analyzes outlier behavior (count, similarity to median)
    5. Returns structured dict suitable for LLM consumption (no numpy arrays)

    Args:
        data_path: Path to .npy file with shape (n_curves, n_points)
        method: Band depth method - 'fbd' or 'mfbd' (default: 'fbd')

    Returns:
        Dict with:
        - status: "success" or "error"
        - message: User-friendly message
        - processed_statistics: Structured dict with numeric summaries
        - _raw_statistics: Original UVisBox output (for debugging)
    """
    try:
        # Validate input
        if not Path(data_path).exists():
            return {
                "status": "error",
                "message": f"Data file not found: {data_path}"
            }

        # Load data
        curves = np.load(data_path)

        # Validate shape
        if curves.ndim != 2:
            return {
                "status": "error",
                "message": f"Expected 2D array (n_curves, n_points), got shape {curves.shape}"
            }

        n_curves, n_points = curves.shape

        # Call UVisBox function to get summary statistics
        raw_stats = functional_boxplot_summary_statistics(
            data=curves,
            method=method
        )

        # Extract components from raw statistics
        depth = raw_stats["depth"]              # Shape: (n_curves,)
        median = raw_stats["median"]            # Shape: (n_points,)
        percentile_bands = raw_stats.get("percentile_bands", {})  # Dict of (bottom, top) tuples
        outliers = raw_stats.get("outliers", np.array([]))        # Shape: (n_outliers, n_points)
        sorted_curves = raw_stats["sorted_curves"]  # Shape: (n_curves, n_points)
        sorted_indices = raw_stats["sorted_indices"]  # Shape: (n_curves,)

        # Analyze median curve
        median_analysis = _analyze_median_curve(median)

        # Analyze percentile bands
        # Extract percentile values from band names (e.g., "25_percentile_band" -> 25)
        percentiles = []
        for band_name in percentile_bands.keys():
            pct = int(band_name.split("_")[0])
            percentiles.append(pct)
        percentiles.sort()

        band_analysis = _analyze_percentile_bands(percentile_bands, percentiles)

        # Analyze outliers
        outlier_analysis = _analyze_outliers(outliers, median, sorted_curves)

        # Construct LLM-friendly summary (no numpy arrays!)
        processed_statistics = {
            "data_shape": {
                "n_curves": int(n_curves),
                "n_points": int(n_points)
            },
            "median": median_analysis,
            "bands": band_analysis,
            "outliers": outlier_analysis,
            "method": method
        }

        # Prepare raw statistics for debugging (convert numpy to lists)
        raw_stats_serializable = {
            "depth": depth.tolist(),
            "median": median.tolist(),
            "percentile_bands": {
                name: (bottom.tolist(), top.tolist())
                for name, (bottom, top) in percentile_bands.items()
            },
            "outliers": outliers.tolist() if outliers.size > 0 else [],
            "sorted_indices": sorted_indices.tolist()
        }

        return {
            "status": "success",
            "message": f"Computed statistics for {n_curves} curves ({outlier_analysis['count']} outliers)",
            "processed_statistics": processed_statistics,
            "_raw_statistics": raw_stats_serializable
        }

    except Exception as e:
        tb_str = traceback.format_exc()
        return {
            "status": "error",
            "message": f"Error computing statistics: {str(e)}",
            "_error_details": {
                "exception": e,
                "traceback": tb_str
            }
        }
```

## Testing Plan

### Unit Tests

**File**: `tests/unit/test_statistics_tools.py`

Replace placeholder tests with comprehensive test suite:

```python
"""Unit tests for statistics_tools module (0 API calls)."""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
from uvisbox_assistant.statistics_tools import (
    compute_functional_boxplot_statistics,
    _analyze_median_curve,
    _analyze_percentile_bands,
    _analyze_outliers,
    _group_consecutive_indices
)


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
        assert band_stats["mean_width"] == 1.5  # (1+2+2)/3
        assert band_stats["max_width"] == 2.0
        assert band_stats["min_width"] == 1.0

    def test_uncertainty_score(self):
        """Test overall uncertainty score."""
        bottom = np.array([0.0, 0.0, 0.0])
        top = np.array([1.0, 1.0, 1.0])
        bands = {"90_percentile_band": (bottom, top)}
        percentiles = [90]

        result = _analyze_percentile_bands(bands, percentiles)

        # Uncertainty score should be normalized
        assert 0.0 <= result["overall_uncertainty_score"] <= 1.0

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

    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_successful_computation(self, mock_uvisbox, tmp_path):
        """Test successful statistics computation with mocked UVisBox."""
        # Create test data
        n_curves, n_points = 30, 100
        curves = np.random.randn(n_curves, n_points)
        data_path = tmp_path / "test_curves.npy"
        np.save(data_path, curves)

        # Mock UVisBox output
        mock_uvisbox.return_value = {
            "depth": np.random.rand(n_curves),
            "median": np.random.randn(n_points),
            "percentile_bands": {
                "50_percentile_band": (
                    np.random.randn(n_points),
                    np.random.randn(n_points)
                ),
                "90_percentile_band": (
                    np.random.randn(n_points),
                    np.random.randn(n_points)
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

    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_no_numpy_arrays_in_output(self, mock_uvisbox, tmp_path):
        """Verify no numpy arrays in statistics_summary."""
        # Create test data
        curves = np.random.randn(30, 100)
        data_path = tmp_path / "test.npy"
        np.save(data_path, curves)

        # Mock UVisBox
        mock_uvisbox.return_value = {
            "depth": np.random.rand(30),
            "median": np.random.randn(100),
            "percentile_bands": {
                "50_percentile_band": (np.random.randn(100), np.random.randn(100))
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
```

### Integration Test (Optional for Phase 2)

If UVisBox is available, add a real integration test:

```python
@pytest.mark.integration
def test_real_uvisbox_integration(tmp_path):
    """Test with real UVisBox function (requires UVisBox installed)."""
    try:
        from uvisbox.Modules import functional_boxplot_summary_statistics
    except ImportError:
        pytest.skip("UVisBox not available")

    # Generate test data
    n_curves, n_points = 30, 100
    x = np.linspace(0, 2*np.pi, n_points)
    curves = []
    for i in range(n_curves):
        amplitude = np.random.uniform(0.8, 1.2)
        phase = np.random.uniform(0, np.pi)
        noise = np.random.normal(0, 0.1, n_points)
        curve = amplitude * np.sin(x + phase) + noise
        curves.append(curve)
    data = np.array(curves)

    data_path = tmp_path / "real_test.npy"
    np.save(data_path, data)

    # Run statistics computation
    result = compute_functional_boxplot_statistics(str(data_path))

    # Verify success
    assert result["status"] == "success"
    assert "processed_statistics" in result
```

## Success Conditions

- [ ] _analyze_median_curve() implemented and tested (6+ tests)
- [ ] _analyze_percentile_bands() implemented and tested (3+ tests)
- [ ] _analyze_outliers() implemented and tested (3+ tests)
- [ ] _group_consecutive_indices() implemented and tested (3+ tests)
- [ ] compute_functional_boxplot_statistics() fully implemented
- [ ] Main function handles file not found errors
- [ ] Main function handles invalid data shape errors
- [ ] Main function returns no numpy arrays in processed_statistics
- [ ] 20+ unit tests pass (0 API calls)
- [ ] All tests use mocked UVisBox function for predictability
- [ ] Optional integration test with real UVisBox works

## Integration Notes

### Output Structure

The `processed_statistics` dict structure:

```python
{
    "data_shape": {
        "n_curves": int,
        "n_points": int
    },
    "median": {
        "trend": str,                    # "increasing" | "decreasing" | "stationary"
        "overall_slope": float,
        "fluctuation_level": float,      # 0-1
        "smoothness_score": float,       # 0-1
        "value_range": (float, float),
        "mean_value": float,
        "std_value": float
    },
    "bands": {
        "band_widths": {
            "XX_percentile_band": {
                "mean_width": float,
                "max_width": float,
                "min_width": float,
                "std_width": float,
                "max_width_index": int
            },
            ...
        },
        "widest_regions": [(start, end), ...],
        "overall_uncertainty_score": float,  # 0-1
        "num_bands": int
    },
    "outliers": {
        "count": int,
        "median_similarity_mean": float | None,
        "median_similarity_std": float | None,
        "intra_outlier_similarity": float | None,
        "outlier_percentage": float
    },
    "method": str  # "fbd" | "mfbd"
}
```

### Performance Considerations

- Statistical computations are fast (< 1 second for typical data)
- No API calls required (pure computation)
- Memory efficient (no retention of large arrays)

### Error Recovery

Follows existing error pattern:
- File validation before processing
- Shape validation before UVisBox call
- Exception handling with full traceback capture
- Return dict with `_error_details` for debugging

## Estimated Effort

**Development**: 2.5 hours
- Helper functions: 1.5 hours
- Main function: 1 hour

**Testing**: 1.5 hours
- Unit test writing: 1 hour
- Mock setup and validation: 30 minutes

**Total**: 4-5 hours (including debugging and refinement)
