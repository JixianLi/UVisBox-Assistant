"""Interpret and enhance error messages with context-aware hints."""

import re
from typing import Tuple, Optional


def interpret_uvisbox_error(
    error: Exception,
    traceback_str: str,
    debug_mode: bool = False
) -> Tuple[str, Optional[str]]:
    """
    Interpret UVisBox errors and provide helpful context.

    Args:
        error: The exception object
        traceback_str: Full traceback string
        debug_mode: Whether debug mode is enabled

    Returns:
        Tuple of (user_message, debug_hint)
        debug_hint is None if debug mode is OFF or no hint available
    """
    error_msg = str(error)
    error_type = type(error).__name__

    # Pattern 1: Colormap errors
    if "colormap" in error_msg.lower():
        colormap_name = _extract_colormap_name(error_msg)
        user_msg = f"Colormap error: {error_msg}"

        if debug_mode:
            if "matplotlib" in traceback_str or "mpl_colors" in traceback_str:
                hint = (
                    f"The colormap '{colormap_name}' may be valid in matplotlib "
                    f"but UVisBox might not be passing it correctly. "
                    f"This could be a UVisBox bug. Try 'viridis', 'plasma', or 'inferno' "
                    f"which are known to work."
                )
            else:
                hint = "Check if the colormap name is supported by UVisBox."
        else:
            hint = None

        return user_msg, hint

    # Pattern 2: Method validation errors
    if "unknown method" in error_msg.lower() or "invalid method" in error_msg.lower():
        method_name = _extract_method_name(error_msg)
        valid_methods = _extract_valid_methods(error_msg)

        user_msg = f"Method validation error: {error_msg}"

        if debug_mode:
            hint = (
                f"UVisBox doesn't recognize method '{method_name}'. "
                f"Valid options: {', '.join(valid_methods)}. "
                f"Note: Check UVisBox documentation - there may be a typo in the validation code."
            )
        else:
            hint = None

        return user_msg, hint

    # Pattern 3: Shape mismatch errors
    if "shape" in error_msg.lower() and ("expected" in error_msg.lower() or "got" in error_msg.lower()):
        shape_info = _extract_shape_info(error_msg)
        user_msg = f"Data shape mismatch: {error_msg}"

        if debug_mode:
            hint = (
                f"Data shape is {shape_info['actual']} but expected {shape_info['expected']}. "
                f"Check if you're using the right data for this visualization type."
            )
        else:
            hint = None

        return user_msg, hint

    # Pattern 4: File not found
    if error_type == "FileNotFoundError":
        user_msg = f"File not found: {error_msg}"

        if debug_mode:
            hint = (
                "The data file may have been deleted or not yet created. "
                "Use '/context' to see available session files."
            )
        else:
            hint = None

        return user_msg, hint

    # Pattern 5: Import errors (UVisBox not installed)
    if error_type == "ImportError" or error_type == "ModuleNotFoundError":
        if "uvisbox" in error_msg.lower():
            user_msg = "UVisBox is not installed or not accessible"

            if debug_mode:
                hint = (
                    "Make sure UVisBox is installed in the 'agent' conda environment. "
                    "Run: conda activate agent && pip install uvisbox"
                )
            else:
                hint = None

            return user_msg, hint

    # Default: return original message
    return error_msg, None


def _extract_colormap_name(error_msg: str) -> str:
    """Extract colormap name from error message."""
    # Try patterns like "colormap 'Reds'" or "Invalid colormap name 'Reds'"
    match = re.search(r"colormap\s+['\"]?(\w+)['\"]?", error_msg, re.IGNORECASE)
    if match:
        return match.group(1)

    match = re.search(r"['\"](\w+)['\"]", error_msg)
    if match:
        return match.group(1)

    return "unknown"


def _extract_method_name(error_msg: str) -> str:
    """Extract method name from error message."""
    # Try patterns like "Unknown method 'fbd'" or "method 'fbd'"
    match = re.search(r"method\s+['\"]?(\w+)['\"]?", error_msg, re.IGNORECASE)
    if match:
        return match.group(1)

    match = re.search(r"['\"](\w+)['\"]", error_msg)
    if match:
        return match.group(1)

    return "unknown"


def _extract_valid_methods(error_msg: str) -> list:
    """Extract list of valid methods from error message."""
    # Try pattern like "Choose 'fdb' or 'mfbd'"
    match = re.search(r"Choose\s+([^.]+)", error_msg, re.IGNORECASE)
    if match:
        methods_str = match.group(1)
        # Extract quoted strings
        methods = re.findall(r"['\"](\w+)['\"]", methods_str)
        return methods

    return ["see documentation"]


def _extract_shape_info(error_msg: str) -> dict:
    """Extract shape information from error message."""
    shape_info = {"actual": "unknown", "expected": "unknown"}

    # Try to extract actual shape
    match = re.search(r"got\s+shape\s+\(([^)]+)\)", error_msg, re.IGNORECASE)
    if match:
        shape_info["actual"] = f"({match.group(1)})"

    # Try to extract expected shape
    match = re.search(r"expected\s+([^,]+)", error_msg, re.IGNORECASE)
    if match:
        shape_info["expected"] = match.group(1).strip()

    return shape_info


def format_error_with_hint(user_message: str, hint: Optional[str]) -> str:
    """
    Format error message with optional debug hint.

    Args:
        user_message: Main error message
        hint: Optional debug hint (shown when debug mode is ON)

    Returns:
        Formatted error message
    """
    if hint:
        return f"{user_message}\n💡 Debug hint: {hint}"
    return user_message
