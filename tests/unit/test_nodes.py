"""Unit tests for nodes.py using mocks (0 API calls)."""

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage, HumanMessage
from uvisbox_assistant.core.nodes import (
    call_model, call_data_tool, call_vis_tool,
    call_statistics_tool, call_analyzer_tool
)
from uvisbox_assistant.core.state import create_initial_state


class TestCallModel:
    """Test call_model node with mocked LLM."""

    @patch('uvisbox_assistant.core.nodes.MODEL')
    @patch('uvisbox_assistant.core.nodes.config.TEST_DATA_DIR')
    def test_call_model_invokes_llm(self, mock_test_data_dir, mock_model):
        """Test that call_model invokes the model."""
        # Setup mocks
        mock_test_data_dir.exists.return_value = False
        mock_response = AIMessage(content="Test response")
        mock_model.invoke.return_value = mock_response

        # Create state
        state = create_initial_state("test message")

        # Call node
        result = call_model(state)

        # Verify model was invoked
        assert mock_model.invoke.called
        assert "messages" in result
        assert result["messages"][0] == mock_response

    @patch('uvisbox_assistant.core.nodes.MODEL')
    @patch('uvisbox_assistant.core.nodes.config.TEST_DATA_DIR')
    def test_call_model_includes_file_list_context(self, mock_test_data_dir, mock_model):
        """Test that file list is included in context when available."""
        # Setup mocks - simulate files exist
        mock_file1 = MagicMock()
        mock_file1.name = "file1.npy"
        mock_file1.is_file.return_value = True

        mock_file2 = MagicMock()
        mock_file2.name = "file2.csv"
        mock_file2.is_file.return_value = True

        mock_test_data_dir.exists.return_value = True
        mock_test_data_dir.iterdir.return_value = [mock_file1, mock_file2]

        mock_response = AIMessage(content="Response with context")
        mock_model.invoke.return_value = mock_response

        # Create state
        state = create_initial_state("test")

        # Call node
        result = call_model(state)

        # Verify model was called
        assert mock_model.invoke.called


class TestCallDataTool:
    """Test call_data_tool node."""

    def test_call_data_tool_no_tool_calls(self):
        """Test error when no tool_calls in message."""
        state = create_initial_state("test")
        # Add message without tool_calls
        state["messages"].append(AIMessage(content="No tools"))

        with pytest.raises(ValueError, match="no tool_calls"):
            call_data_tool(state)

    @patch('uvisbox_assistant.core.nodes.DATA_TOOLS')
    def test_call_data_tool_unknown_tool(self, mock_data_tools):
        """Test handling of unknown tool."""
        # Setup: empty DATA_TOOLS dict
        mock_data_tools.__contains__.return_value = False

        # Create state with tool call
        state = create_initial_state("test")
        ai_msg = AIMessage(
            content="",
            tool_calls=[{
                "name": "unknown_tool",
                "args": {},
                "id": "test_id"
            }]
        )
        state["messages"].append(ai_msg)

        # Call node
        result = call_data_tool(state)

        # Verify error handling
        assert "messages" in result
        assert "error" in result["messages"][0].content.lower()
        assert result.get("error_count", 0) > 0

    @patch('uvisbox_assistant.core.nodes.DATA_TOOLS')
    def test_call_data_tool_successful_execution(self, mock_data_tools):
        """Test successful data tool execution."""
        # Setup mock tool
        mock_tool_func = MagicMock()
        mock_tool_func.return_value = {
            "status": "success",
            "message": "Generated curves",
            "output_path": "temp/test.npy"
        }
        mock_data_tools.__contains__.return_value = True
        mock_data_tools.__getitem__.return_value = mock_tool_func

        # Create state with tool call
        state = create_initial_state("test")
        ai_msg = AIMessage(
            content="",
            tool_calls=[{
                "name": "generate_ensemble_curves",
                "args": {"n_curves": 10},
                "id": "test_id"
            }]
        )
        state["messages"].append(ai_msg)
        state["session_files"] = []

        # Call node
        result = call_data_tool(state)

        # Verify success handling
        assert "messages" in result
        assert "current_data_path" in result
        assert result["current_data_path"] == "temp/test.npy"
        assert result["error_count"] == 0

    @patch('uvisbox_assistant.core.nodes.DATA_TOOLS')
    def test_call_data_tool_exception_handling(self, mock_data_tools):
        """Test exception handling in data tool execution."""
        # Setup mock tool that raises exception
        mock_tool_func = MagicMock()
        mock_tool_func.side_effect = RuntimeError("Tool crashed")
        mock_data_tools.__contains__.return_value = True
        mock_data_tools.__getitem__.return_value = mock_tool_func

        # Create state with tool call
        state = create_initial_state("test")
        ai_msg = AIMessage(
            content="",
            tool_calls=[{
                "name": "load_csv_to_numpy",
                "args": {"filepath": "test.csv"},
                "id": "test_id"
            }]
        )
        state["messages"].append(ai_msg)

        # Call node
        result = call_data_tool(state)

        # Verify exception handling
        assert "messages" in result
        assert "error" in result["messages"][0].content.lower()
        assert result.get("error_count", 0) > 0

    @patch('uvisbox_assistant.core.nodes.DATA_TOOLS')
    def test_calls_data_tool_with_valid_result(self, mock_data_tools):
        """Test successful data tool call with output_path."""
        mock_tool = MagicMock()
        mock_tool.return_value = {
            'status': 'success',
            'output_path': '/path/to/data.npy',
            'message': 'Generated'
        }
        mock_data_tools.__contains__.return_value = True
        mock_data_tools.__getitem__.return_value = mock_tool

        state = create_initial_state("test")
        state['session_files'] = []
        state['messages'].append(AIMessage(
            content="",
            tool_calls=[{'name': 'generate_curves', 'args': {'n_curves': 10}, 'id': '123'}]
        ))

        result = call_data_tool(state)

        assert 'messages' in result
        assert len(result['messages']) == 1
        assert 'current_data_path' in result
        assert result['current_data_path'] == '/path/to/data.npy'

    @patch('uvisbox_assistant.core.nodes.DATA_TOOLS')
    def test_handles_tool_not_in_dict(self, mock_data_tools):
        """Test handling when tool not in DATA_TOOLS dict."""
        mock_data_tools.__contains__.return_value = False

        state = create_initial_state("test")
        state['messages'].append(AIMessage(
            content="",
            tool_calls=[{'name': 'nonexistent_tool', 'args': {}, 'id': '123'}]
        ))

        result = call_data_tool(state)

        assert 'error_count' in result
        assert result['error_count'] > 0
        assert 'error' in result['messages'][0].content.lower()


class TestCallVisTool:
    """Test call_vis_tool node."""

    def test_call_vis_tool_no_tool_calls(self):
        """Test error when no tool_calls in message."""
        state = create_initial_state("test")
        state["messages"].append(AIMessage(content="No tools"))

        with pytest.raises(ValueError, match="no tool_calls"):
            call_vis_tool(state)

    @patch('uvisbox_assistant.core.nodes.VIS_TOOLS')
    def test_call_vis_tool_unknown_tool(self, mock_vis_tools):
        """Test handling of unknown visualization tool."""
        mock_vis_tools.__contains__.return_value = False

        # Create state with tool call
        state = create_initial_state("test")
        ai_msg = AIMessage(
            content="",
            tool_calls=[{
                "name": "unknown_vis_tool",
                "args": {},
                "id": "test_id"
            }]
        )
        state["messages"].append(ai_msg)

        # Call node
        result = call_vis_tool(state)

        # Verify error handling
        assert "messages" in result
        assert "error" in result["messages"][0].content.lower()

    @patch('uvisbox_assistant.core.nodes.VIS_TOOLS')
    def test_call_vis_tool_successful_execution(self, mock_vis_tools):
        """Test successful visualization tool execution."""
        # Setup mock tool
        mock_tool_func = MagicMock()
        mock_tool_func.return_value = {
            "status": "success",
            "message": "Plot created",
            "_vis_params": {
                "_tool_name": "plot_functional_boxplot",
                "data_path": "test.npy"
            }
        }
        mock_vis_tools.__contains__.return_value = True
        mock_vis_tools.__getitem__.return_value = mock_tool_func

        # Create state with tool call
        state = create_initial_state("test")
        ai_msg = AIMessage(
            content="",
            tool_calls=[{
                "name": "plot_functional_boxplot",
                "args": {"data_path": "test.npy"},
                "id": "test_id"
            }]
        )
        state["messages"].append(ai_msg)

        # Call node
        result = call_vis_tool(state)

        # Verify success handling
        assert "messages" in result
        assert "last_vis_params" in result
        assert result["error_count"] == 0

    @patch('uvisbox_assistant.core.nodes.VIS_TOOLS')
    def test_calls_vis_tool_with_vis_params(self, mock_vis_tools):
        """Test successful vis tool call that returns vis params."""
        mock_tool = MagicMock()
        mock_tool.return_value = {
            'status': 'success',
            'message': 'Plotted',
            '_vis_params': {'_tool_name': 'plot_test', 'param': 'value'}
        }
        mock_vis_tools.__contains__.return_value = True
        mock_vis_tools.__getitem__.return_value = mock_tool

        state = create_initial_state("test")
        state['messages'].append(AIMessage(
            content="",
            tool_calls=[{'name': 'plot_test', 'args': {'data_path': '/test.npy'}, 'id': '123'}]
        ))

        result = call_vis_tool(state)

        assert 'last_vis_params' in result
        assert result['last_vis_params']['_tool_name'] == 'plot_test'


class TestCallStatisticsTool:
    """Test call_statistics_tool node."""

    def test_call_statistics_tool_no_tool_calls(self):
        """Test error when no tool_calls in message."""
        state = create_initial_state("test")
        state["messages"].append(AIMessage(content="No tools"))

        with pytest.raises(ValueError, match="no tool_calls"):
            call_statistics_tool(state)

    @patch('uvisbox_assistant.core.nodes.STATISTICS_TOOLS')
    def test_call_statistics_tool_successful_execution(self, mock_stats_tools):
        """Test successful statistics tool execution."""
        # Setup mock tool
        mock_tool_func = MagicMock()
        mock_tool_func.return_value = {
            "status": "success",
            "message": "Statistics computed",
            "raw_statistics": {"depths": [0.1, 0.2]},
            "processed_statistics": {"median_trend": "increasing"}
        }
        mock_stats_tools.__contains__.return_value = True
        mock_stats_tools.__getitem__.return_value = mock_tool_func

        # Create state with tool call
        state = create_initial_state("test")
        ai_msg = AIMessage(
            content="",
            tool_calls=[{
                "name": "compute_functional_boxplot_statistics",
                "args": {"data_path": "test.npy"},
                "id": "test_id"
            }]
        )
        state["messages"].append(ai_msg)

        # Call node
        result = call_statistics_tool(state)

        # Verify success handling
        assert "messages" in result
        assert "raw_statistics" in result
        assert "processed_statistics" in result

    @patch('uvisbox_assistant.core.nodes.STATISTICS_TOOLS')
    def test_calls_statistics_tool_with_stats(self, mock_stats_tools):
        """Test successful statistics tool call that returns statistics."""
        mock_tool = MagicMock()
        mock_tool.return_value = {
            'status': 'success',
            'processed_statistics': {'median': {}, 'outliers': {}},
            'raw_statistics': {}
        }
        mock_stats_tools.__contains__.return_value = True
        mock_stats_tools.__getitem__.return_value = mock_tool

        state = create_initial_state("test")
        state['messages'].append(AIMessage(
            content="",
            tool_calls=[{'name': 'compute_stats', 'args': {'data_path': '/test.npy'}, 'id': '123'}]
        ))

        result = call_statistics_tool(state)

        assert 'processed_statistics' in result
        assert 'raw_statistics' in result


class TestCallAnalyzerTool:
    """Test call_analyzer_tool node."""

    def test_call_analyzer_tool_no_tool_calls(self):
        """Test error when no tool_calls in message."""
        state = create_initial_state("test")
        state["messages"].append(AIMessage(content="No tools"))

        with pytest.raises(ValueError, match="no tool_calls"):
            call_analyzer_tool(state)

    @patch('uvisbox_assistant.core.nodes.ANALYZER_TOOLS')
    def test_call_analyzer_tool_without_processed_statistics(self, mock_analyzer_tools):
        """Test analyzer when processed_statistics missing from state."""
        # Setup mock tool
        mock_tool_func = MagicMock()
        mock_tool_func.return_value = {
            "status": "error",
            "message": "Missing processed_statistics"
        }
        mock_analyzer_tools.__contains__.return_value = True
        mock_analyzer_tools.__getitem__.return_value = mock_tool_func

        # Create state with tool call but NO processed_statistics
        state = create_initial_state("test")
        state["processed_statistics"] = None
        ai_msg = AIMessage(
            content="",
            tool_calls=[{
                "name": "generate_uncertainty_report",
                "args": {"analysis_type": "quick"},
                "id": "test_id"
            }]
        )
        state["messages"].append(ai_msg)

        # Call node
        result = call_analyzer_tool(state)

        # Verify error handling
        assert "messages" in result

    @patch('uvisbox_assistant.core.nodes.ANALYZER_TOOLS')
    def test_call_analyzer_tool_successful_execution(self, mock_analyzer_tools):
        """Test successful analyzer tool execution."""
        # Setup mock tool
        mock_tool_func = MagicMock()
        mock_tool_func.return_value = {
            "status": "success",
            "message": "Generated all uncertainty reports",
            "reports": {
                "inline": "This ensemble shows moderate uncertainty.",
                "quick": "The data shows moderate uncertainty with consistent median trend.",
                "detailed": "Full analysis report here..."
            }
        }
        mock_analyzer_tools.__contains__.return_value = True
        mock_analyzer_tools.__getitem__.return_value = mock_tool_func

        # Create state with tool call and processed_statistics
        state = create_initial_state("test")
        state["processed_statistics"] = {"median_trend": "increasing"}
        ai_msg = AIMessage(
            content="",
            tool_calls=[{
                "name": "generate_uncertainty_report",
                "args": {},
                "id": "test_id"
            }]
        )
        state["messages"].append(ai_msg)

        # Call node
        result = call_analyzer_tool(state)

        # Verify success handling
        assert "messages" in result
        assert "analysis_reports" in result
        assert result["analysis_reports"]["inline"] == "This ensemble shows moderate uncertainty."
        assert result["analysis_reports"]["quick"] == "The data shows moderate uncertainty with consistent median trend."
        assert result["analysis_reports"]["detailed"] == "Full analysis report here..."

    @patch('uvisbox_assistant.core.nodes.ANALYZER_TOOLS')
    def test_injects_statistics_into_analyzer(self, mock_analyzer_tools):
        """Test statistics are injected from state for generate_uncertainty_report."""
        mock_tool = MagicMock()
        mock_tool.return_value = {
            'status': 'success',
            'report': 'Analysis report',
            'analysis_type': 'quick'
        }
        mock_analyzer_tools.__contains__.return_value = True
        mock_analyzer_tools.__getitem__.return_value = mock_tool

        state = create_initial_state("test")
        state['processed_statistics'] = {'median': {}, 'outliers': {}}
        state['messages'].append(AIMessage(
            content="",
            tool_calls=[{'name': 'generate_uncertainty_report', 'args': {'analysis_type': 'quick'}, 'id': '123'}]
        ))

        result = call_analyzer_tool(state)

        # Verify tool was called
        assert mock_tool.called
        # Verify statistics were injected
        call_args = mock_tool.call_args[1]
        assert 'processed_statistics' in call_args
        assert call_args['processed_statistics'] == {'median': {}, 'outliers': {}}

    @patch('uvisbox_assistant.core.nodes.ANALYZER_TOOLS')
    def test_handles_missing_statistics_for_report(self, mock_analyzer_tools):
        """Test error when statistics missing for generate_uncertainty_report."""
        mock_analyzer_tools.__contains__.return_value = True

        state = create_initial_state("test")
        # No processed_statistics in state
        state['messages'].append(AIMessage(
            content="",
            tool_calls=[{'name': 'generate_uncertainty_report', 'args': {'analysis_type': 'quick'}, 'id': '123'}]
        ))

        result = call_analyzer_tool(state)

        # Should return error
        assert 'error_count' in result
        assert result['error_count'] > 0
