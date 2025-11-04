"""Unit tests for analyzer_tools module (0 API calls)."""

import pytest
from uvisbox_assistant.analyzer_tools import (
    ANALYZER_TOOLS,
    ANALYZER_TOOL_SCHEMAS,
    generate_uncertainty_report,
    validate_processed_statistics,
    _get_prompt_for_analysis_type,
    INLINE_REPORT_PROMPT,
    QUICK_REPORT_PROMPT,
    DETAILED_REPORT_PROMPT
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

        # Verify description mentions sequential workflow
        assert "compute_functional_boxplot_statistics FIRST" in schema["description"]

        params = schema["parameters"]["properties"]
        # statistics are injected from state, not passed as parameter
        assert "analysis_type" in params

        # Verify enum values
        assert "inline" in params["analysis_type"]["enum"]
        assert "quick" in params["analysis_type"]["enum"]
        assert "detailed" in params["analysis_type"]["enum"]

        # Verify no required parameters (analysis_type has default)
        assert len(schema["parameters"]["required"]) == 0


class TestPromptTemplates:
    """Test prompt template structure."""

    def test_inline_prompt_exists(self):
        """Verify inline prompt template defined."""
        assert INLINE_REPORT_PROMPT is not None
        assert len(INLINE_REPORT_PROMPT) > 0
        assert "{statistics_json}" in INLINE_REPORT_PROMPT

    def test_quick_prompt_exists(self):
        """Verify quick prompt template defined."""
        assert QUICK_REPORT_PROMPT is not None
        assert "{statistics_json}" in QUICK_REPORT_PROMPT

    def test_detailed_prompt_exists(self):
        """Verify detailed prompt template defined."""
        assert DETAILED_REPORT_PROMPT is not None
        assert "{statistics_json}" in DETAILED_REPORT_PROMPT

    def test_get_prompt_for_inline(self):
        """Test getting inline prompt."""
        prompt = _get_prompt_for_analysis_type("inline")
        assert prompt == INLINE_REPORT_PROMPT

    def test_get_prompt_for_quick(self):
        """Test getting quick prompt."""
        prompt = _get_prompt_for_analysis_type("quick")
        assert prompt == QUICK_REPORT_PROMPT

    def test_get_prompt_for_detailed(self):
        """Test getting detailed prompt."""
        prompt = _get_prompt_for_analysis_type("detailed")
        assert prompt == DETAILED_REPORT_PROMPT

    def test_get_prompt_invalid_type(self):
        """Test error for invalid analysis type."""
        with pytest.raises(ValueError, match="Invalid analysis_type"):
            _get_prompt_for_analysis_type("invalid")


class TestValidateProcessedStatistics:
    """Test processed statistics validation."""

    def test_valid_summary(self):
        """Test validation with valid summary."""
        summary = {
            "data_shape": {"n_curves": 30, "n_points": 100},
            "median": {
                "trend": "increasing",
                "overall_slope": 0.5,
                "fluctuation_level": 0.2,
                "smoothness_score": 0.8,
                "value_range": (0.0, 10.0),
                "mean_value": 5.0,
                "std_value": 2.0
            },
            "bands": {
                "band_widths": {},
                "widest_regions": [],
                "overall_uncertainty_score": 0.3,
                "num_bands": 2
            },
            "outliers": {
                "count": 2,
                "median_similarity_mean": 0.7,
                "outlier_percentage": 6.7
            },
            "method": "fbd"
        }

        is_valid, error_msg = validate_processed_statistics(summary)
        assert is_valid is True
        assert error_msg is None

    def test_missing_top_level_key(self):
        """Test validation fails with missing top-level key."""
        summary = {
            "data_shape": {"n_curves": 30, "n_points": 100},
            # Missing "median", "bands", "outliers", "method"
        }

        is_valid, error_msg = validate_processed_statistics(summary)
        assert is_valid is False
        assert "Missing required top-level key" in error_msg

    def test_missing_data_shape_field(self):
        """Test validation fails with incomplete data_shape."""
        summary = {
            "data_shape": {"n_curves": 30},  # Missing n_points
            "median": {
                "trend": "increasing",
                "overall_slope": 0.5,
                "fluctuation_level": 0.2,
                "smoothness_score": 0.8,
                "value_range": (0.0, 10.0)
            },
            "bands": {"band_widths": {}},
            "outliers": {"count": 0},
            "method": "fbd"
        }

        is_valid, error_msg = validate_processed_statistics(summary)
        assert is_valid is False
        assert "data_shape" in error_msg.lower()

    def test_missing_median_field(self):
        """Test validation fails with incomplete median."""
        summary = {
            "data_shape": {"n_curves": 30, "n_points": 100},
            "median": {"trend": "increasing"},  # Missing other required fields
            "bands": {"band_widths": {}},
            "outliers": {"count": 0},
            "method": "fbd"
        }

        is_valid, error_msg = validate_processed_statistics(summary)
        assert is_valid is False
        assert "median" in error_msg.lower()


class TestGenerateReportErrorHandling:
    """Test error handling without LLM calls."""

    def test_invalid_analysis_type(self):
        """Test error with invalid analysis type."""
        summary = {
            "data_shape": {"n_curves": 30, "n_points": 100},
            "median": {
                "trend": "increasing",
                "overall_slope": 0.5,
                "fluctuation_level": 0.2,
                "smoothness_score": 0.8,
                "value_range": (0.0, 10.0)
            },
            "bands": {"band_widths": {}},
            "outliers": {"count": 0},
            "method": "fbd"
        }

        result = generate_uncertainty_report(summary, "invalid_type")

        assert result["status"] == "error"
        assert "Invalid analysis_type" in result["message"]

    def test_invalid_summary_structure(self):
        """Test error with invalid summary structure."""
        invalid_summary = {"incomplete": "data"}

        result = generate_uncertainty_report(invalid_summary, "quick")

        assert result["status"] == "error"
        assert "Invalid processed_statistics" in result["message"]
