"""Configuration for UVisBox-Assistant"""
import os
from pathlib import Path

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment. Please set it in your system environment.")

# Model Configuration
MODEL_NAME = "gemini-2.0-flash-lite"  # Lite version: 30 RPM (vs standard: 15 RPM)

# Paths
# config.py is in src/uvisbox_assistant/, need to go up 3 levels to project root
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

# Figure defaults
# These are the ONLY parameters actually used from config.DEFAULT_VIS_PARAMS
# All visualization-specific defaults are hardcoded in function signatures (vis_tools.py)
# This prevents duplication and mismatch between config and function APIs
DEFAULT_VIS_PARAMS = {
    "figsize": (10, 8),
    "dpi": 100,
}
