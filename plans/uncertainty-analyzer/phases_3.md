# Phase 3: Analyzer Tool Implementation

## Overview

Implement the LLM-powered analyzer tool that generates natural language uncertainty reports from statistical summaries. This phase creates three specialized prompts for inline, quick, and detailed report formats, integrates with the Gemini model, and establishes comprehensive testing strategies that respect API rate limits.

## Goals

- Implement generate_uncertainty_report() with LLM integration
- Create three specialized system prompts for report formats
- Generate descriptive-only reports (no recommendations)
- Establish integration testing with API budget management
- Achieve robust error handling and validation

## Prerequisites

- Phase 2 completed (statistics_tools.py fully functional)
- Gemini API key configured in environment
- langchain-google-genai available

## Implementation Plan

### Step 1: Create Report Generation Prompts

**File**: `src/uvisbox_assistant/analyzer_tools.py`

Add prompt templates before the main function:

```python
# Report generation prompts for different formats

INLINE_REPORT_PROMPT = """You are an uncertainty analysis expert. Generate a single concise sentence describing the overall uncertainty level in this ensemble data.

Statistical Summary:
{statistics_json}

Guidelines:
- ONE sentence only
- Mention overall uncertainty level (low/moderate/high)
- No recommendations or prescriptions
- Be precise and quantitative when possible

Example outputs:
- "This ensemble shows low uncertainty with tightly clustered curves and no outliers."
- "The data exhibits moderate uncertainty with 15% band width variation and 3 outliers."
- "High uncertainty is evident with wide percentile bands (40% range) and 12% outlier rate."

Generate your inline summary:"""


QUICK_REPORT_PROMPT = """You are an uncertainty analysis expert. Generate a brief 3-5 sentence overview of uncertainty characteristics in this ensemble data.

Statistical Summary:
{statistics_json}

Guidelines:
- 3-5 sentences maximum
- Cover: overall uncertainty level, median behavior, band characteristics
- Include specific numbers from the summary
- No recommendations or prescriptions
- Descriptive only

Structure:
1. Overall uncertainty assessment (1 sentence)
2. Median curve characteristics (1 sentence)
3. Band/variation characteristics (1-2 sentences)
4. Outliers if present (1 sentence)

Generate your quick summary:"""


DETAILED_REPORT_PROMPT = """You are an uncertainty analysis expert. Generate a comprehensive uncertainty analysis report from these statistical summaries.

Statistical Summary:
{statistics_json}

Guidelines:
- Comprehensive but concise
- Three sections: Median Behavior, Band Characteristics, Outlier Analysis
- Include specific numbers and metrics from the summary
- Describe trends, patterns, and uncertainty levels
- NO recommendations or prescriptions (descriptive only)
- Use clear, professional language

Structure your report with these sections:

## Median Behavior
[Describe trend, fluctuation, smoothness, value range]

## Band Characteristics
[Describe band widths, widest regions, overall uncertainty score]

## Outlier Analysis
[Describe outlier count, similarity to median, clustering]

## Overall Assessment
[Synthesize findings into overall uncertainty characterization]

Generate your detailed report:"""


def _get_prompt_for_analysis_type(analysis_type: str) -> str:
    """
    Get the appropriate prompt template for the analysis type.

    Args:
        analysis_type: "inline" | "quick" | "detailed"

    Returns:
        Prompt template string

    Raises:
        ValueError: If analysis_type is invalid
    """
    prompts = {
        "inline": INLINE_REPORT_PROMPT,
        "quick": QUICK_REPORT_PROMPT,
        "detailed": DETAILED_REPORT_PROMPT
    }

    if analysis_type not in prompts:
        raise ValueError(
            f"Invalid analysis_type: {analysis_type}. "
            f"Must be one of {list(prompts.keys())}"
        )

    return prompts[analysis_type]
```

### Step 2: Implement Report Generation Function

**File**: `src/uvisbox_assistant/analyzer_tools.py`

Replace placeholder with full implementation:

```python
def generate_uncertainty_report(
    statistics_summary: dict,
    analysis_type: str = "quick"
) -> Dict:
    """
    Generate natural language uncertainty analysis report.

    Uses LLM to interpret statistical summaries and generate reports in three formats:
    - inline: 1 sentence summary of uncertainty level
    - quick: 3-5 sentence overview
    - detailed: Full report with median, band, and outlier analysis

    Args:
        statistics_summary: Structured dict from compute_functional_boxplot_statistics
        analysis_type: "inline" | "quick" | "detailed" (default: "quick")

    Returns:
        Dict with:
        - status: "success" or "error"
        - message: User-friendly confirmation
        - report: Generated text report
        - analysis_type: Echo of requested type
    """
    try:
        # Validate analysis_type
        if analysis_type not in ["inline", "quick", "detailed"]:
            return {
                "status": "error",
                "message": f"Invalid analysis_type: {analysis_type}. Must be 'inline', 'quick', or 'detailed'."
            }

        # Validate input structure
        required_keys = ["data_shape", "median", "bands", "outliers"]
        for key in required_keys:
            if key not in statistics_summary:
                return {
                    "status": "error",
                    "message": f"Missing required key in statistics_summary: {key}"
                }

        # Convert statistics summary to JSON string for prompt
        import json
        statistics_json = json.dumps(statistics_summary, indent=2)

        # Get appropriate prompt template
        prompt_template = _get_prompt_for_analysis_type(analysis_type)
        prompt = prompt_template.format(statistics_json=statistics_json)

        # Create Gemini model (no tools needed for text generation)
        from langchain_google_genai import ChatGoogleGenerativeAI

        model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.3  # Slight creativity for natural language, but mostly deterministic
        )

        # Generate report
        response = model.invoke([HumanMessage(content=prompt)])

        # Extract report text
        report_text = response.content.strip()

        # Validate output length based on type
        word_count = len(report_text.split())
        if analysis_type == "inline" and word_count > 30:
            # Inline should be very short
            return {
                "status": "error",
                "message": f"Inline report too long ({word_count} words). Expected ~15-25 words."
            }
        elif analysis_type == "quick" and word_count > 150:
            # Quick should be brief
            return {
                "status": "error",
                "message": f"Quick report too long ({word_count} words). Expected 50-100 words."
            }

        return {
            "status": "success",
            "message": f"Generated {analysis_type} uncertainty report ({word_count} words)",
            "report": report_text,
            "analysis_type": analysis_type
        }

    except Exception as e:
        tb_str = traceback.format_exc()
        return {
            "status": "error",
            "message": f"Error generating report: {str(e)}",
            "_error_details": {
                "exception": e,
                "traceback": tb_str
            }
        }
```

### Step 3: Add Validation Helper

**File**: `src/uvisbox_assistant/analyzer_tools.py`

Add a helper function for statistics summary validation:

```python
def validate_statistics_summary(summary: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate statistics summary structure.

    Args:
        summary: Dictionary to validate

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    # Check top-level keys
    required_top_keys = ["data_shape", "median", "bands", "outliers", "method"]
    for key in required_top_keys:
        if key not in summary:
            return False, f"Missing required top-level key: {key}"

    # Check data_shape structure
    if "n_curves" not in summary["data_shape"] or "n_points" not in summary["data_shape"]:
        return False, "data_shape missing n_curves or n_points"

    # Check median structure
    median_keys = ["trend", "overall_slope", "fluctuation_level", "smoothness_score", "value_range"]
    for key in median_keys:
        if key not in summary["median"]:
            return False, f"median missing required key: {key}"

    # Check bands structure
    if "band_widths" not in summary["bands"]:
        return False, "bands missing band_widths"

    # Check outliers structure
    if "count" not in summary["outliers"]:
        return False, "outliers missing count"

    return True, None
```

Update generate_uncertainty_report() to use validation:

```python
def generate_uncertainty_report(
    statistics_summary: dict,
    analysis_type: str = "quick"
) -> Dict:
    """..."""
    try:
        # Validate analysis_type
        if analysis_type not in ["inline", "quick", "detailed"]:
            return {
                "status": "error",
                "message": f"Invalid analysis_type: {analysis_type}. Must be 'inline', 'quick', or 'detailed'."
            }

        # Validate input structure
        is_valid, error_msg = validate_statistics_summary(statistics_summary)
        if not is_valid:
            return {
                "status": "error",
                "message": f"Invalid statistics_summary: {error_msg}"
            }

        # ... rest of implementation
```

## Testing Plan

### Unit Tests (0 API Calls)

**File**: `tests/unit/test_analyzer_tools.py`

Add tests for validation and error handling (no LLM calls):

```python
"""Unit tests for analyzer_tools module (0 API calls)."""

import pytest
from uvisbox_assistant.analyzer_tools import (
    ANALYZER_TOOLS,
    ANALYZER_TOOL_SCHEMAS,
    generate_uncertainty_report,
    validate_statistics_summary,
    _get_prompt_for_analysis_type,
    INLINE_REPORT_PROMPT,
    QUICK_REPORT_PROMPT,
    DETAILED_REPORT_PROMPT
)


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


class TestValidateStatisticsSummary:
    """Test statistics summary validation."""

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

        is_valid, error_msg = validate_statistics_summary(summary)
        assert is_valid is True
        assert error_msg is None

    def test_missing_top_level_key(self):
        """Test validation fails with missing top-level key."""
        summary = {
            "data_shape": {"n_curves": 30, "n_points": 100},
            # Missing "median", "bands", "outliers", "method"
        }

        is_valid, error_msg = validate_statistics_summary(summary)
        assert is_valid is False
        assert "Missing required top-level key" in error_msg

    def test_missing_data_shape_field(self):
        """Test validation fails with incomplete data_shape."""
        summary = {
            "data_shape": {"n_curves": 30},  # Missing n_points
            "median": {},
            "bands": {},
            "outliers": {},
            "method": "fbd"
        }

        is_valid, error_msg = validate_statistics_summary(summary)
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

        is_valid, error_msg = validate_statistics_summary(summary)
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
        assert "Invalid statistics_summary" in result["message"]
```

### Integration Tests (Uses API Calls)

**File**: `tests/integration/test_analyzer_tool.py`

```python
"""Integration tests for analyzer tool with LLM (uses API calls)."""

import pytest
import time
from uvisbox_assistant.analyzer_tools import generate_uncertainty_report


@pytest.fixture
def valid_statistics_summary():
    """Fixture providing valid statistics summary."""
    return {
        "data_shape": {"n_curves": 30, "n_points": 100},
        "median": {
            "trend": "increasing",
            "overall_slope": 0.05,
            "fluctuation_level": 0.15,
            "smoothness_score": 0.85,
            "value_range": (0.5, 5.5),
            "mean_value": 3.0,
            "std_value": 1.2
        },
        "bands": {
            "band_widths": {
                "50_percentile_band": {
                    "mean_width": 0.8,
                    "max_width": 1.5,
                    "min_width": 0.3,
                    "std_width": 0.2
                },
                "90_percentile_band": {
                    "mean_width": 2.0,
                    "max_width": 3.5,
                    "min_width": 1.0,
                    "std_width": 0.5
                }
            },
            "widest_regions": [(45, 55), (80, 90)],
            "overall_uncertainty_score": 0.35,
            "num_bands": 2
        },
        "outliers": {
            "count": 2,
            "median_similarity_mean": 0.65,
            "median_similarity_std": 0.1,
            "intra_outlier_similarity": 0.8,
            "outlier_percentage": 6.7
        },
        "method": "fbd"
    }


class TestInlineReportGeneration:
    """Test inline report generation."""

    def test_inline_report_success(self, valid_statistics_summary):
        """Test successful inline report generation."""
        time.sleep(2)  # Rate limit delay

        result = generate_uncertainty_report(
            valid_statistics_summary,
            analysis_type="inline"
        )

        assert result["status"] == "success"
        assert "report" in result
        assert result["analysis_type"] == "inline"

        # Verify report is short (1 sentence ~15-30 words)
        word_count = len(result["report"].split())
        assert 10 <= word_count <= 40, f"Inline report should be ~15-30 words, got {word_count}"

        # Verify descriptive content
        report_lower = result["report"].lower()
        # Should mention uncertainty level
        assert any(word in report_lower for word in ["uncertainty", "variation", "ensemble"])


class TestQuickReportGeneration:
    """Test quick report generation."""

    def test_quick_report_success(self, valid_statistics_summary):
        """Test successful quick report generation."""
        time.sleep(2)  # Rate limit delay

        result = generate_uncertainty_report(
            valid_statistics_summary,
            analysis_type="quick"
        )

        assert result["status"] == "success"
        assert "report" in result
        assert result["analysis_type"] == "quick"

        # Verify report is brief (3-5 sentences, ~50-100 words)
        word_count = len(result["report"].split())
        assert 30 <= word_count <= 150, f"Quick report should be ~50-100 words, got {word_count}"

        # Verify mentions key components
        report_lower = result["report"].lower()
        assert "median" in report_lower or "trend" in report_lower
        assert "band" in report_lower or "percentile" in report_lower


class TestDetailedReportGeneration:
    """Test detailed report generation."""

    def test_detailed_report_success(self, valid_statistics_summary):
        """Test successful detailed report generation."""
        time.sleep(2)  # Rate limit delay

        result = generate_uncertainty_report(
            valid_statistics_summary,
            analysis_type="detailed"
        )

        assert result["status"] == "success"
        assert "report" in result
        assert result["analysis_type"] == "detailed"

        # Verify report is comprehensive (multiple sections)
        report = result["report"]
        word_count = len(report.split())
        assert word_count >= 100, f"Detailed report should be substantial, got {word_count} words"

        # Verify section structure (should have headers or clear organization)
        report_lower = report.lower()
        assert "median" in report_lower
        assert "band" in report_lower or "percentile" in report_lower
        assert "outlier" in report_lower or "outliers" in report_lower


class TestReportNoRecommendations:
    """Verify reports are descriptive only (no recommendations)."""

    def test_no_prescriptive_language(self, valid_statistics_summary):
        """Verify reports don't include recommendations."""
        time.sleep(2)  # Rate limit delay

        result = generate_uncertainty_report(
            valid_statistics_summary,
            analysis_type="detailed"
        )

        assert result["status"] == "success"

        # Check for prescriptive language (should NOT be present)
        report_lower = result["report"].lower()
        prescriptive_words = [
            "should", "must", "recommend", "suggest",
            "need to", "you should", "consider", "improve"
        ]

        for word in prescriptive_words:
            assert word not in report_lower, \
                f"Report should be descriptive only, found prescriptive word: {word}"
```

**Important**: Add rate limit management to test runner:

```python
# In tests/utils/run_all_tests.py, add delay between analyzer tests
# Each test should include time.sleep(2) at start to respect 30 RPM limit
```

## Success Conditions

- [ ] Three prompt templates created (inline, quick, detailed)
- [ ] _get_prompt_for_analysis_type() implemented and tested
- [ ] validate_statistics_summary() implemented and tested (6+ tests)
- [ ] generate_uncertainty_report() fully implemented
- [ ] Error handling for invalid analysis_type
- [ ] Error handling for invalid summary structure
- [ ] 12+ unit tests pass (0 API calls)
- [ ] 4+ integration tests pass (with rate limit delays)
- [ ] Generated reports are descriptive only (no recommendations)
- [ ] Inline reports are 1 sentence (~15-30 words)
- [ ] Quick reports are 3-5 sentences (~50-100 words)
- [ ] Detailed reports have clear structure and sections

## Integration Notes

### LLM Configuration

- **Model**: gemini-2.0-flash-lite (30 RPM limit)
- **Temperature**: 0.3 (mostly deterministic, slight creativity for natural language)
- **No tools binding**: Text generation only, no function calls

### Prompt Engineering Notes

- All prompts include example outputs for inline format
- Prompts emphasize "no recommendations" requirement
- JSON formatting of statistics makes it easy for LLM to parse
- Structured guidance helps maintain consistent quality

### API Budget Management

Integration tests must:
- Include 2-second delays between calls (30 RPM = 1 call per 2 seconds)
- Run sequentially (not in parallel)
- Be marked with @pytest.mark.integration for selective running

### Output Validation

Report quality checks:
- Word count appropriate for format type
- Contains expected terminology (uncertainty, median, bands, outliers)
- No prescriptive language (should, must, recommend)
- Clear and professional tone

## Estimated Effort

**Development**: 2 hours
- Prompt templates: 45 minutes
- Main function: 45 minutes
- Validation helper: 30 minutes

**Testing**: 1.5 hours
- Unit tests: 45 minutes
- Integration tests: 45 minutes (including API delays)

**Total**: 3-4 hours (including prompt refinement and testing)
