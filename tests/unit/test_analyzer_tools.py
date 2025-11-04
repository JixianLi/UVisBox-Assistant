"""Unit tests for analyzer_tools module (0 API calls)."""

import pytest
from uvisbox_assistant.analyzer_tools import (
    ANALYZER_TOOLS,
    ANALYZER_TOOL_SCHEMAS,
    generate_uncertainty_report
)


class TestAnalyzerToolRegistry:
    """Test tool registry structure."""

    def test_analyzer_tools_registry_exists(self):
        """Verify ANALYZER_TOOLS dict exists."""
        assert isinstance(ANALYZER_TOOLS, dict)
        assert len(ANALYZER_TOOLS) > 0

    def test_generate_report_in_registry(self):
        """Verify generate_uncertainty_report is registered."""
        assert "generate_uncertainty_report" in ANALYZER_TOOLS
        assert callable(ANALYZER_TOOLS["generate_uncertainty_report"])


class TestAnalyzerToolSchemas:
    """Test tool schemas for LLM binding."""

    def test_schemas_list_exists(self):
        """Verify ANALYZER_TOOL_SCHEMAS is a list."""
        assert isinstance(ANALYZER_TOOL_SCHEMAS, list)
        assert len(ANALYZER_TOOL_SCHEMAS) > 0

    def test_generate_report_schema(self):
        """Verify generate_uncertainty_report schema."""
        schema = ANALYZER_TOOL_SCHEMAS[0]
        assert schema["name"] == "generate_uncertainty_report"
        assert "description" in schema
        assert "parameters" in schema

        params = schema["parameters"]["properties"]
        assert "statistics_summary" in params
        assert "analysis_type" in params

        # Verify enum values
        assert "inline" in params["analysis_type"]["enum"]
        assert "quick" in params["analysis_type"]["enum"]
        assert "detailed" in params["analysis_type"]["enum"]


class TestGenerateReportPlaceholder:
    """Test placeholder implementation (Phase 1)."""

    def test_returns_not_implemented_error(self):
        """Verify placeholder returns error message."""
        dummy_summary = {
            "median": {"trend": "increasing"},
            "bands": {},
            "outliers": {"count": 0}
        }

        result = generate_uncertainty_report(dummy_summary, "quick")

        assert result["status"] == "error"
        assert "not yet implemented" in result["message"].lower()
