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

    # Functional boxplot / curve boxplot
    "percentiles": [25, 50, 90, 100],  # List of percentiles for band visualization
    "colors": None,                     # Color scheme (None = use defaults)
    "plot_all_curves": False,           # Whether to show all individual curves

    # Contour boxplot
    "contour_percentiles": [25, 50, 75, 90],  # Percentiles for contour bands

    # Probabilistic marching squares / contour boxplot
    "isovalue": 0.5,                    # Threshold for contour extraction
    "colormap": "viridis",              # Colormap for scalar field visualization

    # Uncertainty lobes
    "percentile1": 90,                  # First percentile for depth filtering
    "percentile2": 50,                  # Second percentile for depth filtering
    "scale": 0.2,                       # Scale factor for glyphs

    # Display options
    "show_median": True,                # Show median contour/curve
    "show_outliers": True,              # Show outlier contours/curves
    "alpha": 0.5,                       # Transparency for overlays
}
