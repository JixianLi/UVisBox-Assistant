"""Unit tests for error recording in tool nodes."""

import pytest
import numpy as np
from pathlib import Path
from langchain_core.messages import AIMessage
from uvisbox_assistant.session.conversation import ConversationSession
from uvisbox_assistant.core.nodes import call_vis_tool, call_data_tool
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

    # Create a state with a tool call that will fail (invalid output path)
    state = create_initial_state("test")
    ai_message = AIMessage(
        content="",
        tool_calls=[{
            "name": "generate_ensemble_curves",
            "args": {"output_path": "/nonexistent/directory/output.npy"},  # Invalid path
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
    assert "generate_ensemble_curves" in error.tool_name or "DATA TOOL" in error.tool_name.upper()


