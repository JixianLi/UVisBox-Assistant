# ABOUTME: Unit tests for GraphState fields and the state-update helpers in core/state.py.
# ABOUTME: 0 LLM calls; pure logic tests against create_initial_state and update_state_with_*.
"""Unit tests for GraphState helpers (0 API calls)."""

import pytest
from uvisbox_assistant.core.state import (
    GraphState,
    create_initial_state,
    update_state_with_data,
    update_state_with_vis,
    increment_error_count,
)


class TestGraphStateBasics:
    """Test core GraphState fields."""

    def test_initial_state_has_required_fields(self):
        """Verify existing fields still present."""
        state = create_initial_state("test message")

        assert "messages" in state
        assert "current_data_path" in state
        assert "last_vis_params" in state
        assert "session_files" in state
        assert "error_count" in state


class TestDataStateUpdate:
    """Test update_state_with_data helper."""

    def test_updates_data_fields(self):
        """Verify data state update."""
        state = create_initial_state("test")
        state["session_files"] = []

        data_path = "temp/_temp_test_curves.npy"
        updates = update_state_with_data(state, data_path)

        assert updates["current_data_path"] == data_path
        assert updates["session_files"] == [data_path]
        assert updates["error_count"] == 0

    def test_appends_to_session_files(self):
        """Verify session_files appends correctly."""
        state = create_initial_state("test")
        state["session_files"] = ["existing_file.npy"]

        data_path = "temp/_temp_new_file.npy"
        updates = update_state_with_data(state, data_path)

        assert updates["session_files"] == ["existing_file.npy", "temp/_temp_new_file.npy"]

    def test_resets_error_count(self):
        """Verify error count reset on success."""
        state = create_initial_state("test")
        state["error_count"] = 3
        state["session_files"] = []

        updates = update_state_with_data(state, "test.npy")
        assert updates["error_count"] == 0


class TestVisStateUpdate:
    """Test update_state_with_vis helper."""

    def test_updates_vis_fields(self):
        """Verify vis state update."""
        state = create_initial_state("test")

        vis_params = {
            "_tool_name": "plot_functional_boxplot",
            "data_path": "test.npy",
            "percentiles": [25, 50, 90],
            "show_median": True
        }
        updates = update_state_with_vis(state, vis_params)

        assert updates["last_vis_params"] == vis_params
        assert updates["error_count"] == 0

    def test_resets_error_count(self):
        """Verify error count reset on success."""
        state = create_initial_state("test")
        state["error_count"] = 2

        updates = update_state_with_vis(state, {"_tool_name": "plot_test"})
        assert updates["error_count"] == 0


class TestIncrementErrorCount:
    """Test increment_error_count helper."""

    def test_increments_from_zero(self):
        """Verify error count increments from 0."""
        state = create_initial_state("test")
        state["error_count"] = 0

        updates = increment_error_count(state)
        assert updates["error_count"] == 1

    def test_increments_from_existing(self):
        """Verify error count increments from existing value."""
        state = create_initial_state("test")
        state["error_count"] = 2

        updates = increment_error_count(state)
        assert updates["error_count"] == 3

    def test_handles_missing_error_count(self):
        """Verify handling when error_count key is missing."""
        state = create_initial_state("test")
        # Manually remove error_count to test .get() fallback
        if "error_count" in state:
            del state["error_count"]

        updates = increment_error_count(state)
        assert updates["error_count"] == 1
