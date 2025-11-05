"""Integration tests for CSV file loading."""

import pytest
import numpy as np
from pathlib import Path
from uvisbox_assistant.tools.vis_tools import plot_functional_boxplot


@pytest.fixture
def csv_file(tmp_path):
    """Create a test CSV file."""
    csv_path = tmp_path / "test_curves.csv"
    # Create 5 curves with 10 points each
    data = np.random.randn(5, 10)
    np.savetxt(csv_path, data, delimiter=',')
    return csv_path


def test_load_csv_and_plot_functional_boxplot(csv_file):
    """Test loading CSV file and plotting functional boxplot."""
    # Call the tool directly with CSV file
    result = plot_functional_boxplot(data_path=str(csv_file))

    # Should fail with pickle error before fix
    # After fix, should succeed
    assert result.get("status") == "success", f"Tool failed: {result.get('message')}"
    assert "_vis_params" in result, "Visualization parameters not returned"
