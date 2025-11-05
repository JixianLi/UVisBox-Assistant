# ABOUTME: Unit tests for utils/logger.py
# ABOUTME: Tests logging functions with mock file I/O (0 API calls)

import pytest
from unittest.mock import patch, MagicMock, call
from uvisbox_assistant.utils.logger import (
    log_tool_call,
    log_tool_result,
    log_error,
    log_state_update,
    logger
)


class TestLogToolCall:
    """Test log_tool_call function."""

    @patch('uvisbox_assistant.utils.logger.logger')
    def test_logs_tool_call_with_args(self, mock_logger):
        """Test logging of tool call with arguments."""
        tool_name = 'test_tool'
        args = {'param1': 'value1', 'param2': 42}

        log_tool_call(tool_name, args)

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert 'test_tool' in call_args
        assert 'param1' in call_args or str(args) in call_args

    @patch('uvisbox_assistant.utils.logger.logger')
    def test_logs_tool_call_with_empty_args(self, mock_logger):
        """Test logging tool call with empty args."""
        log_tool_call('empty_tool', {})

        mock_logger.info.assert_called_once()


class TestLogToolResult:
    """Test log_tool_result function."""

    @patch('uvisbox_assistant.utils.logger.logger')
    def test_logs_success_result(self, mock_logger):
        """Test logging successful tool result."""
        result = {'status': 'success', 'message': 'Operation completed'}

        log_tool_result('test_tool', result)

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert 'test_tool' in call_args
        assert 'success' in call_args
        assert 'Operation completed' in call_args

    @patch('uvisbox_assistant.utils.logger.logger')
    def test_logs_error_result(self, mock_logger):
        """Test logging error tool result."""
        result = {'status': 'error', 'message': 'Failed'}

        log_tool_result('test_tool', result)

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert 'error' in call_args

    @patch('uvisbox_assistant.utils.logger.logger')
    def test_handles_missing_status(self, mock_logger):
        """Test logging result without status field."""
        result = {'message': 'No status'}

        log_tool_result('test_tool', result)

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert 'unknown' in call_args

    @patch('uvisbox_assistant.utils.logger.logger')
    def test_handles_missing_message(self, mock_logger):
        """Test logging result without message field."""
        result = {'status': 'success'}

        log_tool_result('test_tool', result)

        mock_logger.info.assert_called_once()


class TestLogError:
    """Test log_error function."""

    @patch('uvisbox_assistant.utils.logger.logger')
    def test_logs_error_message(self, mock_logger):
        """Test logging error messages."""
        error_msg = 'Critical error occurred'

        log_error(error_msg)

        mock_logger.error.assert_called_once_with(error_msg)

    @patch('uvisbox_assistant.utils.logger.logger')
    def test_logs_empty_error(self, mock_logger):
        """Test logging empty error message."""
        log_error('')

        mock_logger.error.assert_called_once_with('')


class TestLogStateUpdate:
    """Test log_state_update function."""

    @patch('uvisbox_assistant.utils.logger.logger')
    def test_logs_state_update(self, mock_logger):
        """Test logging state updates."""
        log_state_update('current_data_path', '/path/to/data.npy')

        mock_logger.debug.assert_called_once()
        call_args = mock_logger.debug.call_args[0][0]
        assert 'current_data_path' in call_args
        assert '/path/to/data.npy' in call_args

    @patch('uvisbox_assistant.utils.logger.logger')
    def test_logs_state_update_with_complex_value(self, mock_logger):
        """Test logging state update with dict value."""
        value = {'key': 'value', 'nested': {'a': 1}}

        log_state_update('complex_field', value)

        mock_logger.debug.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
