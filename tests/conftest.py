"""Pytest fixtures and configuration for UVisBox-Assistant tests."""

import pytest
from pathlib import Path
import matplotlib.pyplot as plt


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Return the test data directory."""
    return project_root / "test_data"


@pytest.fixture(autouse=True)
def cleanup_matplotlib():
    """Clean up matplotlib figures after each test."""
    yield
    plt.close("all")


@pytest.fixture
def temp_dir(project_root):
    """Return the temp directory."""
    return project_root / "temp"
