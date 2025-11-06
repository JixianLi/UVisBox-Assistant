"""Integration tests for analyzer tool with LLM (uses API calls)."""

import pytest
import time
from uvisbox_assistant.tools.analyzer_tools import generate_uncertainty_report

pytestmark = pytest.mark.llm_subset_analyzer


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
            "overall_msd": 0.35,
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
            valid_processed_statistics
        )

        assert result["status"] == "success"
        assert "reports" in result
        assert isinstance(result["reports"], dict)
        assert "inline" in result["reports"]

        # Verify report is short (1 sentence ~15-30 words)
        word_count = len(result["reports"]["inline"].split())
        assert 10 <= word_count <= 40, f"Inline report should be ~15-30 words, got {word_count}"

        # Verify descriptive content
        report_lower = result["reports"]["inline"].lower()
        # Should mention uncertainty level
        assert any(word in report_lower for word in ["uncertainty", "variation", "ensemble"])


class TestQuickReportGeneration:
    """Test quick report generation."""

    def test_quick_report_success(self, valid_processed_statistics):
        """Test successful quick report generation."""
        time.sleep(2)  # Rate limit delay

        result = generate_uncertainty_report(
            valid_processed_statistics
        )

        assert result["status"] == "success"
        assert "reports" in result
        assert isinstance(result["reports"], dict)
        assert "quick" in result["reports"]

        # Verify report is brief (3-5 sentences, ~50-100 words)
        word_count = len(result["reports"]["quick"].split())
        assert 30 <= word_count <= 150, f"Quick report should be ~50-100 words, got {word_count}"

        # Verify mentions key components
        report_lower = result["reports"]["quick"].lower()
        assert "median" in report_lower or "trend" in report_lower
        assert "band" in report_lower or "percentile" in report_lower


class TestDetailedReportGeneration:
    """Test detailed report generation."""

    def test_detailed_report_success(self, valid_processed_statistics):
        """Test successful detailed report generation."""
        time.sleep(2)  # Rate limit delay

        result = generate_uncertainty_report(
            valid_processed_statistics
        )

        assert result["status"] == "success"
        assert "reports" in result
        assert isinstance(result["reports"], dict)
        assert "detailed" in result["reports"]

        # Verify report is comprehensive (multiple sections)
        report = result["reports"]["detailed"]
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
            valid_processed_statistics
        )

        assert result["status"] == "success"
        assert "reports" in result
        assert isinstance(result["reports"], dict)

        # Check for prescriptive language in detailed report (should NOT be present)
        report_lower = result["reports"]["detailed"].lower()
        # Check for prescriptive phrases (not just individual words like "suggest" which can be descriptive)
        prescriptive_phrases = [
            "should", "must", "recommend that", "i suggest",
            "need to", "you should", "consider", "improve"
        ]

        for phrase in prescriptive_phrases:
            assert phrase not in report_lower, \
                f"Report should be descriptive only, found prescriptive phrase: {phrase}"


class TestMultiReportGeneration:
    """Test that analyzer generates all three report types at once (v0.3.2)"""

    def test_all_three_reports_generated(self):
        """Verify analyzer returns inline, quick, and detailed reports in single call"""
        # Arrange
        processed_stats = {
            "data_shape": {"n_curves": 100, "n_points": 50},
            "median": {
                "trend": "increasing",
                "overall_slope": 0.5,
                "fluctuation_level": "low",
                "smoothness_score": 0.95,
                "value_range": {"min": 0.0, "max": 10.0}
            },
            "bands": {
                "band_widths": [0.5, 1.0, 1.5],
                "overall_msd": 0.3
            },
            "outliers": {
                "count": 2,
                "similarity_to_median": 0.7
            },
            "method": "modified_band_depth"
        }

        # Act
        from uvisbox_assistant.tools.analyzer_tools import generate_uncertainty_report
        result = generate_uncertainty_report(processed_stats)

        # Assert
        assert result["status"] == "success", f"Expected success, got: {result.get('message')}"
        assert "reports" in result, "Result should contain 'reports' key"
        assert isinstance(result["reports"], dict), "Reports should be a dictionary"

        # Verify all three types present
        assert "inline" in result["reports"], "Missing inline report"
        assert "quick" in result["reports"], "Missing quick report"
        assert "detailed" in result["reports"], "Missing detailed report"

        # Verify each is non-empty string
        for report_type in ["inline", "quick", "detailed"]:
            report = result["reports"][report_type]
            assert isinstance(report, str), f"{report_type} report should be string"
            assert len(report) > 0, f"{report_type} report should not be empty"
            assert len(report.split()) > 5, f"{report_type} report should have multiple words"

    def test_multi_report_word_counts(self):
        """Verify different report types have appropriate lengths"""
        # Arrange
        processed_stats = {
            "data_shape": {"n_curves": 100, "n_points": 50},
            "median": {
                "trend": "increasing",
                "overall_slope": 0.5,
                "fluctuation_level": "low",
                "smoothness_score": 0.95,
                "value_range": {"min": 0.0, "max": 10.0}
            },
            "bands": {
                "band_widths": [0.5, 1.0, 1.5],
                "overall_msd": 0.3
            },
            "outliers": {
                "count": 2,
                "similarity_to_median": 0.7
            },
            "method": "modified_band_depth"
        }

        # Act
        from uvisbox_assistant.tools.analyzer_tools import generate_uncertainty_report
        result = generate_uncertainty_report(processed_stats)

        # Assert - verify appropriate lengths
        reports = result["reports"]
        inline_words = len(reports["inline"].split())
        quick_words = len(reports["quick"].split())
        detailed_words = len(reports["detailed"].split())

        # Inline should be shortest (1 sentence, ~15-30 words)
        assert 10 <= inline_words <= 40, f"Inline should be 10-40 words, got {inline_words}"

        # Quick should be medium (3-5 sentences, ~50-100 words)
        assert 40 <= quick_words <= 150, f"Quick should be 40-150 words, got {quick_words}"

        # Detailed should be longest (>100 words)
        assert detailed_words >= 80, f"Detailed should be >=80 words, got {detailed_words}"

        # Verify ordering: inline < quick < detailed
        assert inline_words < quick_words, "Inline should be shorter than quick"
        assert quick_words < detailed_words, "Quick should be shorter than detailed"
