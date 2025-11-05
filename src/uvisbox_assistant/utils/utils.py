"""Utility functions for the UVisBox-Assistant pipeline"""
from typing import Dict, Optional
from pathlib import Path
from uvisbox_assistant import config


def is_data_tool(tool_name: str) -> bool:
    """Check if a tool name corresponds to a data tool."""
    from uvisbox_assistant.tools.data_tools import DATA_TOOLS
    return tool_name in DATA_TOOLS


def is_vis_tool(tool_name: str) -> bool:
    """Check if a tool name corresponds to a vis tool."""
    from uvisbox_assistant.tools.vis_tools import VIS_TOOLS
    return tool_name in VIS_TOOLS


def get_tool_type(tool_name: str) -> str:
    """
    Determine the type of tool based on its name.

    Args:
        tool_name: Name of the tool

    Returns:
        Tool type: "data", "vis", "statistics", "analyzer", or "unknown"
    """
    # Import tool registries
    from uvisbox_assistant.tools.data_tools import DATA_TOOLS
    from uvisbox_assistant.tools.vis_tools import VIS_TOOLS
    from uvisbox_assistant.tools.statistics_tools import STATISTICS_TOOLS
    from uvisbox_assistant.tools.analyzer_tools import ANALYZER_TOOLS

    if tool_name in DATA_TOOLS:
        return "data"
    elif tool_name in VIS_TOOLS:
        return "vis"
    elif tool_name in STATISTICS_TOOLS:
        return "statistics"
    elif tool_name in ANALYZER_TOOLS:
        return "analyzer"
    else:
        return "unknown"


def cleanup_temp_files():
    """Remove all temporary .npy files from the temp directory."""
    if not config.TEMP_DIR.exists():
        return

    count = 0
    for file in config.TEMP_DIR.glob(f"{config.TEMP_FILE_PREFIX}*{config.TEMP_FILE_EXTENSION}"):
        file.unlink()
        count += 1

    print(f"Cleaned up {count} temporary files")


def get_available_files() -> list:
    """Get list of available files in test_data directory."""
    if not config.TEST_DATA_DIR.exists():
        return []

    return [f.name for f in config.TEST_DATA_DIR.iterdir() if f.is_file()]


def format_file_list(files: list) -> str:
    """Format a file list for display."""
    if not files:
        return "No files available"

    return "\n".join([f"  - {f}" for f in files])
