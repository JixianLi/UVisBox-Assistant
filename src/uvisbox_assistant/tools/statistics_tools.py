"""Statistical analysis tools for uncertainty quantification."""

import numpy as np
import traceback
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from scipy import stats
from sklearn.metrics import pairwise_distances

# UVisBox import
try:
    from uvisbox.Modules import functional_boxplot_summary_statistics
except ImportError as e:
    print(f"Warning: UVisBox statistics function import failed: {e}")
    print("Make sure UVisBox is installed with statistics support")


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


def _analyze_percentile_bands(
    percentile_bands: Dict[str, Tuple[np.ndarray, np.ndarray]],
    percentiles: List[float],
    median: Optional[np.ndarray] = None,
    curves: Optional[np.ndarray] = None
) -> Dict:
    """
    Analyze percentile band characteristics.

    Computes:
    - Band widths (mean, max, min for each band)
    - Widest regions (where uncertainty is highest)
    - Overall MSD (Mean Squared Difference to median)

    Args:
        percentile_bands: Dict mapping band names to (bottom, top) curve tuples
                         e.g., {"25_percentile_band": (bottom_array, top_array)}
        percentiles: List of percentile values (e.g., [25, 50, 90, 100])
        median: Optional median curve for MSD calculation
        curves: Optional array of all curves (shape: N x D) for MSD calculation

    Returns:
        Dict with:
        - band_widths: Dict[str, Dict] with mean/max/min widths per band
        - widest_region_indices: List of (start, end) tuples for high-variation regions
        - overall_msd: float (Mean Squared Difference to median)
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

    # Compute overall MSD (Mean Squared Difference to median)
    if median is not None and curves is not None:
        # MSD at each x-coordinate
        msd_values = np.mean((curves - median) ** 2, axis=0)  # MSD at each x
        overall_msd = float(np.mean(msd_values))  # Mean of MSD values
    else:
        # Fallback to 0.0 if median/curves not provided
        overall_msd = 0.0

    return {
        "band_widths": band_widths,
        "widest_regions": widest_regions,
        "overall_msd": float(overall_msd),
        "num_bands": len(percentile_bands)
    }


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
        from uvisbox_assistant.utils.data_loading import load_array

        success, curves, error_msg = load_array(data_path)
        if not success:
            return {"status": "error", "message": error_msg}

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
        depths = raw_stats["depths"]              # Shape: (n_curves,) - Note: plural "depths"
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

        band_analysis = _analyze_percentile_bands(percentile_bands, percentiles, median=median, curves=curves)

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
            "depths": depths.tolist(),
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


# Tool registry (similar to DATA_TOOLS and VIS_TOOLS)
STATISTICS_TOOLS = {
    "compute_functional_boxplot_statistics": compute_functional_boxplot_statistics,
}


# Tool schemas for LLM binding
STATISTICS_TOOL_SCHEMAS = [
    {
        "name": "compute_functional_boxplot_statistics",
        "description": (
            "Compute summary statistics for functional boxplot data including "
            "median behavior, percentile band characteristics, and outlier analysis. "
            "REQUIRED FIRST STEP before generating text reports with generate_uncertainty_report. "
            "Use this when user requests uncertainty analysis or data summary."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_path": {
                    "type": "string",
                    "description": "Path to .npy file containing curve ensemble data"
                },
                "method": {
                    "type": "string",
                    "description": "Band depth method: 'fbd' (functional band depth) or 'mfbd' (modified functional band depth)",
                    "enum": ["fbd", "mfbd"],
                    "default": "fbd"
                }
            },
            "required": ["data_path"]
        }
    }
]
