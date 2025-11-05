"""Unified data loading utilities for multiple file formats."""

import numpy as np
from pathlib import Path
from typing import Tuple, Optional


def load_array(filepath: str) -> Tuple[bool, Optional[np.ndarray], str]:
    """
    Load numpy array from various file formats.

    Supports:
    - .npy: Binary numpy format
    - .csv: Comma-separated values
    - .txt: Space/tab delimited text

    Args:
        filepath: Path to data file

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
    path = Path(filepath)
    suffix = path.suffix.lower()

    try:
        if suffix == '.npy':
            array = np.load(filepath)
        elif suffix == '.csv':
            # CSV files use comma delimiter
            array = np.loadtxt(filepath, delimiter=',')
        elif suffix == '.txt':
            # TXT files use whitespace delimiter (space or tab)
            # delimiter=None tells numpy to auto-detect whitespace
            array = np.loadtxt(filepath, delimiter=None)
        else:
            return False, None, f"Unsupported file format: {suffix}. Supported: .npy, .csv, .txt"

        return True, array, ""

    except Exception as e:
        return False, None, f"Error loading {suffix} file: {str(e)}"
