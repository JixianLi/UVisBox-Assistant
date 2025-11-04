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
        - statistics_summary: Structured dict with numeric summaries
        - _raw_statistics: Original UVisBox output (for debugging)
    """
    try:
        # Implementation will be in Phase 2
        # Placeholder for Phase 1
        return {
            "status": "error",
            "message": "Statistics tool not yet implemented (Phase 2)"
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
