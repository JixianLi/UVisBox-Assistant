"""Unit tests for data loading utilities."""

import numpy as np
import pytest
from pathlib import Path
from uvisbox_assistant.utils.data_loading import load_array


def test_load_npy_file(tmp_path):
    """Test loading .npy binary file."""
    # Create test .npy file
    test_data = np.array([[1, 2, 3], [4, 5, 6]])
    npy_file = tmp_path / "test.npy"
    np.save(npy_file, test_data)

    # Load it
    success, array, error = load_array(str(npy_file))

    # Verify
    assert success is True
    assert error == ""
    assert np.array_equal(array, test_data)


def test_load_csv_file(tmp_path):
    """Test loading .csv file with comma delimiter."""
    # Create test .csv file
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("1,2,3\n4,5,6\n")

    # Load it
    success, array, error = load_array(str(csv_file))

    # Verify
    assert success is True
    assert error == ""
    expected = np.array([[1, 2, 3], [4, 5, 6]])
    assert np.array_equal(array, expected)


def test_load_txt_file_space_delimited(tmp_path):
    """Test loading .txt file with space delimiter."""
    # Create test .txt file
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("1 2 3\n4 5 6\n")

    # Load it
    success, array, error = load_array(str(txt_file))

    # Verify
    assert success is True
    assert error == ""
    expected = np.array([[1, 2, 3], [4, 5, 6]])
    assert np.array_equal(array, expected)


def test_unsupported_format(tmp_path):
    """Test error for unsupported file format."""
    # Create .json file
    json_file = tmp_path / "test.json"
    json_file.write_text('{"data": [1, 2, 3]}')

    # Try to load it
    success, array, error = load_array(str(json_file))

    # Verify error
    assert success is False
    assert array is None
    assert "Unsupported file format" in error
    assert ".json" in error


def test_malformed_csv(tmp_path):
    """Test error for malformed CSV file."""
    # Create malformed .csv file
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text("1,2,3\ninvalid,data\n")

    # Try to load it
    success, array, error = load_array(str(csv_file))

    # Verify error
    assert success is False
    assert array is None
    assert "Error loading" in error
