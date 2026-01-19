"""Configuration for UVisBox-Assistant"""
import os
from pathlib import Path

# API Configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")

# Model Configuration
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "qwen3-vl:8b")  # Local Ollama model name

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
