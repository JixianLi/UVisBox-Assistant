"""Integration tests for analyzer tool with LLM (uses API calls)."""

import pytest
import time
from uvisbox_assistant.analyzer_tools import generate_uncertainty_report


@pytest.fixture
def valid_processed_statistics():
    """Fixture providing valid processed statistics."""
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

    def test_inline_report_success(self, valid_processed_statistics):
        """Test successful inline report generation."""
        time.sleep(2)  # Rate limit delay

        result = generate_uncertainty_report(
            valid_processed_statistics,
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

    def test_quick_report_success(self, valid_processed_statistics):
        """Test successful quick report generation."""
        time.sleep(2)  # Rate limit delay

        result = generate_uncertainty_report(
            valid_processed_statistics,
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

    def test_detailed_report_success(self, valid_processed_statistics):
        """Test successful detailed report generation."""
        time.sleep(2)  # Rate limit delay

        result = generate_uncertainty_report(
            valid_processed_statistics,
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

    def test_no_prescriptive_language(self, valid_processed_statistics):
        """Verify reports don't include recommendations."""
        time.sleep(2)  # Rate limit delay

        result = generate_uncertainty_report(
            valid_processed_statistics,
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
