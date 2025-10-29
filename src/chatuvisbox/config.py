"""Configuration for ChatUVisBox"""
import os
from pathlib import Path

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment. Please set it in your system environment.")

# Model Configuration
MODEL_NAME = "gemini-2.0-flash-lite"  # Lite version: 30 RPM (vs standard: 15 RPM)

# Paths
# config.py is in src/chatuvisbox/, need to go up 3 levels to project root
PACKAGE_ROOT = Path(__file__).parent.parent.parent
PROJECT_ROOT = PACKAGE_ROOT
TEMP_DIR = PROJECT_ROOT / "temp"
TEST_DATA_DIR = PROJECT_ROOT / "test_data"
LOG_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
TEMP_DIR.mkdir(exist_ok=True)
TEST_DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# File naming
TEMP_FILE_PREFIX = "_temp_"
TEMP_FILE_EXTENSION = ".npy"

# Visualization defaults (Tier-2 parameters)
# These parameters are used across different visualization tools
DEFAULT_VIS_PARAMS = {
    # General figure settings
    "figsize": (10, 8),
    "dpi": 100,

    # BoxplotStyleConfig defaults (for functional_boxplot, curve_boxplot, contour_boxplot)
    "percentiles": [25, 50, 90, 100],       # List of percentiles for band visualization
    "percentile_colormap": "viridis",       # Colormap for percentile bands
    "show_median": True,                    # Whether to show median curve/contour
    "median_color": "red",                  # Color of median curve/contour
    "median_width": 3.0,                    # Width of median curve/contour
    "median_alpha": 1.0,                    # Alpha of median curve/contour
    "show_outliers": False,                 # Whether to show outlier curves/contours
    "outliers_color": "gray",               # Color of outlier curves/contours
    "outliers_width": 1.0,                  # Width of outlier curves/contours
    "outliers_alpha": 0.5,                  # Alpha of outlier curves/contours

    # Contour boxplot specific
    "contour_percentiles": [25, 50, 75, 90],  # Percentiles for contour bands

    # Parallel computation
    "workers": 12,                          # Number of parallel workers for band depth

    # Probabilistic marching squares
    "isovalue": 0.5,                        # Threshold for contour extraction
    "colormap": "viridis",                  # Colormap for scalar field visualization

    # Uncertainty lobes
    "percentile1": 90,                      # First percentile for depth filtering
    "percentile2": 50,                      # Second percentile for depth filtering
    "scale": 0.2,                           # Scale factor for glyphs
}
