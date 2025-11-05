"""Unit tests for session/hybrid_control.py (0 API calls)."""
# ABOUTME: Unit tests for hybrid control system with mocked vis tools
# ABOUTME: Tests simple command execution and eligibility checking with 0 API calls

import pytest
from unittest.mock import patch, MagicMock
from uvisbox_assistant.session.hybrid_control import (
    execute_simple_command,
    is_hybrid_eligible
)
from uvisbox_assistant.core.state import create_initial_state


class TestIsHybridEligible:
    """Test is_hybrid_eligible function."""

    @patch('uvisbox_assistant.session.hybrid_control.parse_simple_command')
    def test_returns_true_for_simple_command(self, mock_parse):
        """Test returns True when parse succeeds."""
        mock_parse.return_value = MagicMock()  # Non-None

        result = is_hybrid_eligible("colormap plasma")

        assert result is True
        mock_parse.assert_called_once_with("colormap plasma")

    @patch('uvisbox_assistant.session.hybrid_control.parse_simple_command')
    def test_returns_false_for_complex_command(self, mock_parse):
        """Test returns False when parse fails."""
        mock_parse.return_value = None

        result = is_hybrid_eligible("make it look better")

        assert result is False

    @patch('uvisbox_assistant.session.hybrid_control.parse_simple_command')
    def test_handles_empty_string(self, mock_parse):
        """Test handles empty input."""
        mock_parse.return_value = None

        result = is_hybrid_eligible("")

        assert result is False


class TestExecuteSimpleCommand:
    """Test execute_simple_command function."""

    @patch('uvisbox_assistant.session.hybrid_control.parse_simple_command')
    def test_returns_false_when_not_simple_command(self, mock_parse):
        """Test returns failure when command can't be parsed."""
        mock_parse.return_value = None
        state = {}

        success, result, message = execute_simple_command("complex query", state)

        assert success is False
        assert result is None
        assert "Not a simple command" in message

    @patch('uvisbox_assistant.session.hybrid_control.parse_simple_command')
    def test_returns_false_when_no_previous_vis(self, mock_parse):
        """Test returns failure when no previous visualization."""
        mock_command = MagicMock()
        mock_parse.return_value = mock_command
        state = {}  # No last_vis_params

        success, result, message = execute_simple_command("colormap plasma", state)

        assert success is False
        assert "No previous visualization" in message

    @patch('uvisbox_assistant.session.hybrid_control.parse_simple_command')
    def test_returns_false_when_missing_tool_name(self, mock_parse):
        """Test returns failure when vis params missing tool name."""
        mock_command = MagicMock()
        mock_parse.return_value = mock_command
        state = {
            'last_vis_params': {
                'data_path': '/path/to/data.npy'
                # Missing _tool_name
            }
        }

        success, result, message = execute_simple_command("colormap plasma", state)

        assert success is False
        assert "Cannot determine visualization" in message

    @patch('uvisbox_assistant.session.hybrid_control.VIS_TOOLS', {})
    @patch('uvisbox_assistant.session.hybrid_control.apply_command_to_params')
    @patch('uvisbox_assistant.session.hybrid_control.parse_simple_command')
    def test_returns_false_when_unknown_vis_tool(self, mock_parse, mock_apply):
        """Test returns failure for unknown vis tool."""
        mock_command = MagicMock()
        mock_parse.return_value = mock_command
        mock_apply.return_value = {}

        state = {
            'last_vis_params': {
                '_tool_name': 'unknown_tool',
                'data_path': '/path/to/data.npy'
            }
        }

        success, result, message = execute_simple_command("colormap plasma", state)

        assert success is False
        assert "Unknown vis tool" in message

    @patch('uvisbox_assistant.session.hybrid_control.VIS_TOOLS')
    @patch('uvisbox_assistant.session.hybrid_control.apply_command_to_params')
    @patch('uvisbox_assistant.session.hybrid_control.parse_simple_command')
    @patch('uvisbox_assistant.session.hybrid_control.vprint')
    def test_executes_vis_tool_successfully(self, mock_vprint, mock_parse, mock_apply, mock_vis_tools):
        """Test successful vis tool execution."""
        # Setup mocks
        mock_command = MagicMock()
        mock_command.param_name = 'percentile_colormap'
        mock_command.value = 'plasma'
        mock_parse.return_value = mock_command

        updated_params = {
            '_tool_name': 'plot_functional_boxplot',
            'data_path': '/path/to/data.npy',
            'percentile_colormap': 'plasma'
        }
        mock_apply.return_value = updated_params

        mock_vis_func = MagicMock()
        mock_vis_func.return_value = {'status': 'success', 'message': 'Done'}
        # Mock signature to include valid params
        import inspect
        mock_sig = MagicMock()
        mock_sig.parameters.keys.return_value = ['data_path', 'percentile_colormap']
        with patch('inspect.signature', return_value=mock_sig):
            mock_vis_tools.get.return_value = mock_vis_func

            state = {
                'last_vis_params': {
                    '_tool_name': 'plot_functional_boxplot',
                    'data_path': '/path/to/data.npy'
                }
            }

            success, result, message = execute_simple_command("colormap plasma", state)

        assert success is True
        assert result['_tool_name'] == 'plot_functional_boxplot'
        assert 'percentile_colormap' in message

    @patch('uvisbox_assistant.session.hybrid_control.VIS_TOOLS')
    @patch('uvisbox_assistant.session.hybrid_control.apply_command_to_params')
    @patch('uvisbox_assistant.session.hybrid_control.parse_simple_command')
    def test_returns_false_when_param_not_valid_for_tool(self, mock_parse, mock_apply, mock_vis_tools):
        """Test returns failure when parameter not valid for vis tool."""
        mock_command = MagicMock()
        mock_command.param_name = 'invalid_param'
        mock_parse.return_value = mock_command

        mock_apply.return_value = {'invalid_param': 'value'}

        mock_vis_func = MagicMock()
        import inspect
        mock_sig = MagicMock()
        mock_sig.parameters.keys.return_value = ['data_path']  # Doesn't include invalid_param

        with patch('inspect.signature', return_value=mock_sig):
            mock_vis_tools.get.return_value = mock_vis_func

            state = {
                'last_vis_params': {
                    '_tool_name': 'plot_functional_boxplot',
                    'data_path': '/path/to/data.npy'
                }
            }

            success, result, message = execute_simple_command("invalid_param test", state)

        assert success is False
        assert "not available" in message

    @patch('uvisbox_assistant.session.hybrid_control.VIS_TOOLS')
    @patch('uvisbox_assistant.session.hybrid_control.apply_command_to_params')
    @patch('uvisbox_assistant.session.hybrid_control.parse_simple_command')
    @patch('uvisbox_assistant.session.hybrid_control.vprint')
    def test_returns_false_when_vis_tool_fails(self, mock_vprint, mock_parse, mock_apply, mock_vis_tools):
        """Test returns failure when vis tool execution fails."""
        mock_command = MagicMock()
        mock_command.param_name = 'percentile_colormap'
        mock_parse.return_value = mock_command

        mock_apply.return_value = {
            '_tool_name': 'plot_functional_boxplot',
            'data_path': '/path/to/data.npy',
            'percentile_colormap': 'invalid'
        }

        mock_vis_func = MagicMock()
        mock_vis_func.return_value = {'status': 'error', 'message': 'Invalid colormap'}

        import inspect
        mock_sig = MagicMock()
        mock_sig.parameters.keys.return_value = ['data_path', 'percentile_colormap']

        with patch('inspect.signature', return_value=mock_sig):
            mock_vis_tools.get.return_value = mock_vis_func

            state = {
                'last_vis_params': {
                    '_tool_name': 'plot_functional_boxplot',
                    'data_path': '/path/to/data.npy'
                }
            }

            success, result, message = execute_simple_command("colormap invalid", state)

        assert success is False
        assert "Error updating" in message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
