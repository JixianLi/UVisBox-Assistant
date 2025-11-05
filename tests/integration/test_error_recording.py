"""Integration tests for error recording in tool nodes."""

import pytest
import numpy as np
from pathlib import Path
from langchain_core.messages import AIMessage
from uvisbox_assistant.session.conversation import ConversationSession
from uvisbox_assistant.core.nodes import call_vis_tool, call_data_tool, call_statistics_tool, call_analyzer_tool
from uvisbox_assistant.core.state import create_initial_state


@pytest.fixture
def corrupted_npy_file(tmp_path):
    """Create a corrupted .npy file that will cause a loading exception."""
    # Create a file that exists but isn't a valid .npy file
    bad_file = tmp_path / "corrupted.npy"
    bad_file.write_text("This is not a valid .npy file!")
    return bad_file


def test_vis_tool_errors_recorded(corrupted_npy_file):
    """Test that VIS TOOL errors are recorded in error history."""
    session = ConversationSession()

    # Create a state with a tool call that will fail with exception (corrupted file)
    state = create_initial_state("test")
    ai_message = AIMessage(
        content="",
        tool_calls=[{
            "name": "plot_functional_boxplot",
            "args": {"data_path": str(corrupted_npy_file)},
            "id": "test_call_1"
        }]
    )
    state["messages"] = [ai_message]

    # Call the vis tool node directly
    result = call_vis_tool(state)

    # Check error was recorded
    assert len(session.error_history) > 0, f"No errors recorded. Result: {result.get('messages', [{}])[0].content if result.get('messages') else 'No messages'}"

    # Verify error details
    error = session.error_history[-1]
    assert "plot_functional_boxplot" in error.tool_name


def test_data_tool_errors_recorded():
    """Test that DATA TOOL errors are recorded in error history."""
    session = ConversationSession()

    # Create a state with a tool call that will fail (invalid parameters)
    state = create_initial_state("test")
    ai_message = AIMessage(
        content="",
        tool_calls=[{
            "name": "generate_ar2_curves",
            "args": {"n_curves": 0},  # Invalid: must be > 0
            "id": "test_call_2"
        }]
    )
    state["messages"] = [ai_message]

    # Call the data tool node directly
    result = call_data_tool(state)

    # Check error was recorded
    assert len(session.error_history) > 0, f"No errors recorded. Result: {result.get('messages', [{}])[0].content if result.get('messages') else 'No messages'}"

    # Verify error details
    error = session.error_history[-1]
    assert "generate_ar2_curves" in error.tool_name or "DATA TOOL" in error.tool_name.upper()


def test_statistics_tool_errors_recorded(corrupted_npy_file):
    """Test that STATISTICS TOOL errors are recorded in error history."""
    session = ConversationSession()

    # Create a state with a tool call that will fail with nonexistent file
    state = create_initial_state("test")
    ai_message = AIMessage(
        content="",
        tool_calls=[{
            "name": "compute_functional_boxplot_statistics",
            "args": {"data_path": str(corrupted_npy_file)},
            "id": "test_call_1"
        }]
    )
    state["messages"] = [ai_message]

    # Call the statistics tool node directly
    result = call_statistics_tool(state)

    # Check error was recorded
    assert len(session.error_history) > 0, "No errors recorded"

    # Verify error details
    error = session.error_history[-1]
    assert "compute_functional_boxplot_statistics" in error.tool_name


def test_analyzer_tool_errors_recorded():
    """Test that ANALYZER TOOL errors are recorded in error history."""
    session = ConversationSession()

    # Trigger ANALYZER TOOL error by calling without statistics
    state = create_initial_state("test")
    ai_message = AIMessage(
        content="",
        tool_calls=[{
            "name": "generate_uncertainty_report",
            "args": {},
            "id": "test_call_1"
        }]
    )
    state["messages"] = [ai_message]

    # Call the analyzer tool node directly (without statistics in state)
    result = call_analyzer_tool(state)

    # Check error was recorded
    assert len(session.error_history) > 0, "No errors recorded"

    # Verify error details
    error = session.error_history[-1]
    assert "generate_uncertainty_report" in error.tool_name
    assert "statistics" in error.error_message.lower()
