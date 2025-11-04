"""Unit tests for statistics_tools module (0 API calls)."""

import pytest
import numpy as np
from pathlib import Path
from uvisbox_assistant.statistics_tools import (
    STATISTICS_TOOLS,
    STATISTICS_TOOL_SCHEMAS,
    compute_functional_boxplot_statistics
)


class TestStatisticsToolRegistry:
    """Test tool registry structure."""

    def test_statistics_tools_registry_exists(self):
        """Verify STATISTICS_TOOLS dict exists."""
        assert isinstance(STATISTICS_TOOLS, dict)
        assert len(STATISTICS_TOOLS) > 0

    def test_compute_statistics_in_registry(self):
        """Verify compute_functional_boxplot_statistics is registered."""
        assert "compute_functional_boxplot_statistics" in STATISTICS_TOOLS
        assert callable(STATISTICS_TOOLS["compute_functional_boxplot_statistics"])


class TestStatisticsToolSchemas:
    """Test tool schemas for LLM binding."""

    def test_schemas_list_exists(self):
        """Verify STATISTICS_TOOL_SCHEMAS is a list."""
        assert isinstance(STATISTICS_TOOL_SCHEMAS, list)
        assert len(STATISTICS_TOOL_SCHEMAS) > 0

    def test_compute_statistics_schema(self):
        """Verify compute_functional_boxplot_statistics schema."""
        schema = STATISTICS_TOOL_SCHEMAS[0]
        assert schema["name"] == "compute_functional_boxplot_statistics"
        assert "description" in schema
        assert "parameters" in schema

        params = schema["parameters"]["properties"]
        assert "data_path" in params
        assert "method" in params

        # Verify required fields
        assert "data_path" in schema["parameters"]["required"]


class TestComputeStatisticsPlaceholder:
    """Test placeholder implementation (Phase 1)."""

    def test_returns_not_implemented_error(self, tmp_path):
        """Verify placeholder returns error message."""
        # Create dummy data file
        data = np.random.randn(30, 100)
        data_path = tmp_path / "test_curves.npy"
        np.save(data_path, data)

        result = compute_functional_boxplot_statistics(str(data_path))

        assert result["status"] == "error"
        assert "not yet implemented" in result["message"].lower()
