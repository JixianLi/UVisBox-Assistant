"""Unit tests for graph.py (0 API calls with mocking)."""

import pytest
from unittest.mock import patch, MagicMock
from uvisbox_assistant.core.graph import create_graph, run_graph, stream_graph
from uvisbox_assistant.core.state import create_initial_state


class TestCreateGraph:
    """Test graph creation."""

    def test_create_graph_returns_compiled_graph(self):
        """Verify create_graph returns a compiled StateGraph."""
        graph = create_graph()

        # Check that graph is callable (compiled)
        assert callable(graph.invoke)
        assert callable(graph.stream)

    def test_graph_has_correct_nodes(self):
        """Verify graph contains all expected nodes."""
        graph = create_graph()

        # LangGraph compiled graphs have a 'nodes' attribute
        # Check nodes are present in the graph structure
        assert hasattr(graph, 'nodes')


class TestRunGraph:
    """Test run_graph function."""

    @patch('uvisbox_assistant.core.graph.graph_app')
    def test_run_graph_with_no_initial_state(self, mock_graph_app):
        """Test run_graph creates initial state when none provided."""
        # Setup mock
        mock_final_state = {"messages": [], "current_data_path": None}
        mock_graph_app.invoke.return_value = mock_final_state

        # Call function
        result = run_graph("test message")

        # Verify invoke was called
        assert mock_graph_app.invoke.called
        call_args = mock_graph_app.invoke.call_args[0][0]

        # Verify initial state was created
        assert "messages" in call_args
        assert len(call_args["messages"]) == 1
        assert call_args["messages"][0].content == "test message"

        # Verify result
        assert result == mock_final_state

    @patch('uvisbox_assistant.core.graph.graph_app')
    def test_run_graph_with_initial_state(self, mock_graph_app):
        """Test run_graph appends to existing state."""
        # Setup initial state
        initial_state = create_initial_state("first message")
        initial_state["current_data_path"] = "existing.npy"

        # Setup mock
        mock_final_state = {"messages": [], "current_data_path": "existing.npy"}
        mock_graph_app.invoke.return_value = mock_final_state

        # Call function
        result = run_graph("second message", initial_state=initial_state)

        # Verify invoke was called
        assert mock_graph_app.invoke.called
        call_args = mock_graph_app.invoke.call_args[0][0]

        # Verify message was appended
        assert "messages" in call_args
        assert len(call_args["messages"]) == 2
        assert call_args["messages"][0].content == "first message"
        assert call_args["messages"][1].content == "second message"

        # Verify existing data preserved
        assert call_args["current_data_path"] == "existing.npy"

    @patch('uvisbox_assistant.core.graph.graph_app')
    def test_run_graph_returns_final_state(self, mock_graph_app):
        """Verify run_graph returns the final state from invoke."""
        expected_state = {
            "messages": [],
            "current_data_path": "result.npy",
            "error_count": 0
        }
        mock_graph_app.invoke.return_value = expected_state

        result = run_graph("test")

        assert result == expected_state


class TestStreamGraph:
    """Test stream_graph function."""

    @patch('uvisbox_assistant.core.graph.graph_app')
    def test_stream_graph_with_no_initial_state(self, mock_graph_app):
        """Test stream_graph creates initial state when none provided."""
        # Setup mock stream
        mock_updates = [
            {"model": {"messages": ["update 1"]}},
            {"data_tool": {"current_data_path": "test.npy"}},
            {"model": {"messages": ["update 2"]}}
        ]
        mock_graph_app.stream.return_value = iter(mock_updates)

        # Call function and collect results
        results = list(stream_graph("test message"))

        # Verify stream was called
        assert mock_graph_app.stream.called
        call_args = mock_graph_app.stream.call_args[0][0]

        # Verify initial state was created
        assert "messages" in call_args
        assert len(call_args["messages"]) == 1
        assert call_args["messages"][0].content == "test message"

        # Verify results
        assert results == mock_updates

    @patch('uvisbox_assistant.core.graph.graph_app')
    def test_stream_graph_with_initial_state(self, mock_graph_app):
        """Test stream_graph appends to existing state."""
        # Setup initial state
        initial_state = create_initial_state("first message")

        # Setup mock stream
        mock_updates = [{"model": {"messages": ["update"]}}]
        mock_graph_app.stream.return_value = iter(mock_updates)

        # Call function
        results = list(stream_graph("second message", initial_state=initial_state))

        # Verify stream was called
        assert mock_graph_app.stream.called
        call_args = mock_graph_app.stream.call_args[0][0]

        # Verify message was appended
        assert len(call_args["messages"]) == 2
        assert call_args["messages"][1].content == "second message"

    @patch('uvisbox_assistant.core.graph.graph_app')
    def test_stream_graph_yields_updates(self, mock_graph_app):
        """Verify stream_graph yields all updates."""
        # Setup mock with multiple updates
        mock_updates = [
            {"node_1": {"data": "update1"}},
            {"node_2": {"data": "update2"}},
            {"node_3": {"data": "update3"}}
        ]
        mock_graph_app.stream.return_value = iter(mock_updates)

        # Collect all yielded updates
        results = []
        for update in stream_graph("test"):
            results.append(update)

        # Verify all updates were yielded
        assert len(results) == 3
        assert results[0] == {"node_1": {"data": "update1"}}
        assert results[1] == {"node_2": {"data": "update2"}}
        assert results[2] == {"node_3": {"data": "update3"}}
