"""Unit tests for GraphState extensions (0 API calls)."""

import pytest
from uvisbox_assistant.core.state import (
    GraphState,
    create_initial_state,
    update_state_with_statistics,
    update_state_with_analysis
)


class TestGraphStateExtensions:
    """Test new GraphState fields."""

    def test_initial_state_has_analysis_fields(self):
        """Verify initial state includes analysis fields."""
        state = create_initial_state("test message")

        # Check new fields exist and are None
        assert "raw_statistics" in state
        assert state["raw_statistics"] is None

        assert "processed_statistics" in state
        assert state["processed_statistics"] is None

        assert "analysis_report" in state
        assert state["analysis_report"] is None

        assert "analysis_type" in state
        assert state["analysis_type"] is None

    def test_initial_state_preserves_existing_fields(self):
        """Verify existing fields still present."""
        state = create_initial_state("test message")

        # Existing fields
        assert "messages" in state
        assert "current_data_path" in state
        assert "last_vis_params" in state
        assert "session_files" in state
        assert "error_count" in state


class TestStatisticsStateUpdate:
    """Test update_state_with_statistics helper."""

    def test_updates_statistics_fields(self):
        """Verify statistics state update."""
        state = create_initial_state("test")

        raw_stats = {"depths": [0.1, 0.2], "median": [1.0, 2.0]}
        processed_stats = {"median_trend": "increasing"}

        updates = update_state_with_statistics(state, raw_stats, processed_stats)

        assert updates["raw_statistics"] == raw_stats
        assert updates["processed_statistics"] == processed_stats
        assert updates["error_count"] == 0

    def test_resets_error_count(self):
        """Verify error count reset."""
        state = create_initial_state("test")
        state["error_count"] = 3

        updates = update_state_with_statistics(state, {}, {})
        assert updates["error_count"] == 0


class TestAnalysisStateUpdate:
    """Test update_state_with_analysis helper."""

    def test_updates_analysis_fields(self):
        """Verify analysis state update."""
        state = create_initial_state("test")

        report = "This ensemble shows moderate uncertainty."
        analysis_type = "quick"

        updates = update_state_with_analysis(state, report, analysis_type)

        assert updates["analysis_report"] == report
        assert updates["analysis_type"] == analysis_type
        assert updates["error_count"] == 0

    def test_resets_error_count(self):
        """Verify error count reset."""
        state = create_initial_state("test")
        state["error_count"] = 2

        updates = update_state_with_analysis(state, "report", "inline")
        assert updates["error_count"] == 0
