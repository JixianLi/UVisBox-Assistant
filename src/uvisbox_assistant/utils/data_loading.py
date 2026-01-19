"""Unified data loading utilities for multiple file formats."""

import numpy as np
from pathlib import Path
from typing import Tuple, Optional
from uvisbox_assistant import config


def resolve_data_path(filepath: str) -> Tuple[bool, Optional[Path], str]:
    """
    Resolve a data file path with flexible path handling.

    Resolution strategy:
    1. If absolute path exists → use as-is
    2. If relative path exists from working directory → use it
    3. If bare filename (no separators) and not found → try test_data/{filename}
    4. Otherwise → return error

    Args:
        filepath: User-provided path (absolute, relative, or bare filename)

    Returns:
        Tuple of (success, resolved_path, error_message)
        - success: True if file found
        - resolved_path: Path object to the file (None if not found)
        - error_message: Error description (empty if success)

    Examples:
        >>> success, path, _ = resolve_data_path("/absolute/path/data.npy")
        >>> success, path, _ = resolve_data_path("test_data/sine.npy")
        >>> success, path, _ = resolve_data_path("sine.npy")  # Tries test_data/sine.npy
    """
    path = Path(filepath)

    # Strategy 1: Absolute path
    if path.is_absolute():
        if path.exists():
            return True, path, ""
        else:
            return False, None, f"File not found: {filepath}"

    # Strategy 2: Relative path from working directory
    if path.exists():
        return True, path, ""

    # Strategy 3: Bare filename - try test_data/ directory
    # Only if the path has no directory separators (it's just a filename)
    if "/" not in filepath and "\\" not in filepath:
        test_data_path = config.TEST_DATA_DIR / filepath
        if test_data_path.exists():
            return True, test_data_path, ""

    # Strategy 4: File not found anywhere
    suggestions = []
    suggestions.append(f"  - As absolute path: {Path(filepath).absolute()}")
    suggestions.append(f"  - From working directory: {Path.cwd() / filepath}")
    if "/" not in filepath and "\\" not in filepath:
        suggestions.append(f"  - In test_data/: {config.TEST_DATA_DIR / filepath}")

    error_msg = f"File not found: {filepath}\n\nTried:\n" + "\n".join(suggestions)
    return False, None, error_msg


def load_array(filepath: str) -> Tuple[bool, Optional[np.ndarray], str]:
    """
    Load numpy array from various file formats.

    Supports:
    - .npy: Binary numpy format
    - .csv: Comma-separated values
    - .txt: Space/tab delimited text

    Args:
        filepath: Path to data file (absolute, relative, or bare filename)

    Returns:
        Tuple of (success, array, error_message)
        - success: True if loaded successfully
        - array: Loaded numpy array (None if failed)
        - error_message: Error description (empty string if success)

    Examples:
        >>> success, data, error = load_array("curves.npy")
        >>> if success:
        ...     print(f"Loaded shape: {data.shape}")

        >>> success, data, error = load_array("data.csv")
        >>> if not success:
        ...     print(f"Failed: {error}")
    """
    # Resolve path first
    success, resolved_path, error_msg = resolve_data_path(filepath)
    if not success:
        return False, None, error_msg

    suffix = resolved_path.suffix.lower()

    try:
        if suffix == '.npy':
            array = np.load(resolved_path)
        elif suffix == '.csv':
            # CSV files: try comma delimiter first, fall back to whitespace
            try:
                array = np.loadtxt(resolved_path, delimiter=',')
            except ValueError:
                # If comma delimiter fails, try whitespace (common for misnamed files)
                array = np.loadtxt(resolved_path, delimiter=None)
        elif suffix == '.txt':
            # TXT files use whitespace delimiter (space or tab)
            # delimiter=None tells numpy to auto-detect whitespace
            array = np.loadtxt(resolved_path, delimiter=None)
        else:
            return False, None, f"Unsupported file format: {suffix}. Supported: .npy, .csv, .txt"

        return True, array, ""

    except Exception as e:
        return False, None, f"Error loading {suffix} file: {str(e)}"
