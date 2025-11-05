# ABOUTME: Unit tests for llm/model.py (0 API calls).
# ABOUTME: Tests system prompt generation, model creation, and message preparation with comprehensive mocking.

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import SystemMessage, HumanMessage
from uvisbox_assistant.llm.model import (
    get_system_prompt,
    create_model_with_tools,
    prepare_messages_for_model
)


class TestGetSystemPrompt:
    """Test get_system_prompt function."""

    def test_returns_base_prompt_without_files(self):
        """Test base prompt generation without file list."""
        prompt = get_system_prompt()

        assert 'UVisBox-Assistant' in prompt
        assert 'functional_boxplot' in prompt
        assert 'curve_boxplot' in prompt
        assert 'statistics_tool' in prompt
        assert 'analyzer_tool' in prompt

    def test_includes_file_list_when_provided(self):
        """Test prompt includes file list."""
        files = ['data1.csv', 'data2.npy', 'data3.txt']

        prompt = get_system_prompt(file_list=files)

        assert 'data1.csv' in prompt
        assert 'data2.npy' in prompt
        assert 'data3.txt' in prompt
        assert 'Available files' in prompt

    def test_handles_empty_file_list(self):
        """Test prompt with empty file list."""
        prompt = get_system_prompt(file_list=[])

        # Should still have base prompt
        assert 'UVisBox-Assistant' in prompt

    def test_includes_workflow_patterns(self):
        """Test prompt includes all workflow patterns."""
        prompt = get_system_prompt()

        assert 'VISUALIZATION ONLY' in prompt
        assert 'TEXT ANALYSIS ONLY' in prompt
        assert 'COMBINED VISUALIZATION + ANALYSIS' in prompt

    def test_includes_tool_sequence_rules(self):
        """Test prompt includes critical tool sequence rules."""
        prompt = get_system_prompt()

        assert 'compute_functional_boxplot_statistics' in prompt
        assert 'generate_uncertainty_report' in prompt
        assert 'sequence' in prompt.lower()

    def test_includes_error_handling_guidance(self):
        """Test prompt includes error handling guidance."""
        prompt = get_system_prompt()

        assert 'error' in prompt.lower()
        assert 'Error Handling' in prompt or 'error' in prompt


class TestCreateModelWithTools:
    """Test create_model_with_tools function."""

    @patch('uvisbox_assistant.llm.model.ChatGoogleGenerativeAI')
    @patch('uvisbox_assistant.llm.model.config.MODEL_NAME', 'gemini-2.0-flash-lite')
    @patch('uvisbox_assistant.llm.model.config.GEMINI_API_KEY', 'test-api-key')
    def test_creates_model_with_config(self, mock_model_class):
        """Test model creation with configuration."""
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model

        tools = [{'name': 'test_tool'}]
        result = create_model_with_tools(tools, temperature=0.5)

        mock_model_class.assert_called_once_with(
            model='gemini-2.0-flash-lite',
            google_api_key='test-api-key',
            temperature=0.5
        )

    @patch('uvisbox_assistant.llm.model.ChatGoogleGenerativeAI')
    def test_binds_tools_when_provided(self, mock_model_class):
        """Test tools are bound to model."""
        mock_model = MagicMock()
        mock_bound_model = MagicMock()
        mock_model.bind_tools.return_value = mock_bound_model
        mock_model_class.return_value = mock_model

        tools = [{'name': 'tool1'}, {'name': 'tool2'}]
        result = create_model_with_tools(tools)

        mock_model.bind_tools.assert_called_once_with(tools)
        assert result is mock_bound_model

    @patch('uvisbox_assistant.llm.model.ChatGoogleGenerativeAI')
    def test_returns_model_without_tools(self, mock_model_class):
        """Test returns unbound model when no tools."""
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model

        result = create_model_with_tools([])

        mock_model.bind_tools.assert_not_called()
        assert result is mock_model

    @patch('uvisbox_assistant.llm.model.ChatGoogleGenerativeAI')
    def test_uses_default_temperature(self, mock_model_class):
        """Test uses default temperature of 0.0."""
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model

        create_model_with_tools([])

        call_kwargs = mock_model_class.call_args[1]
        assert call_kwargs['temperature'] == 0.0


class TestPrepareMessagesForModel:
    """Test prepare_messages_for_model function."""

    def test_prepends_system_message(self):
        """Test system message is prepended."""
        state = {
            'messages': [
                HumanMessage(content='user message'),
            ]
        }

        result = prepare_messages_for_model(state)

        assert len(result) == 2
        assert isinstance(result[0], SystemMessage)
        assert result[1].content == 'user message'

    def test_includes_file_list_in_system_prompt(self):
        """Test file list is included in system prompt."""
        state = {'messages': []}
        files = ['test1.csv', 'test2.npy']

        result = prepare_messages_for_model(state, file_list=files)

        system_msg = result[0]
        assert 'test1.csv' in system_msg.content
        assert 'test2.npy' in system_msg.content

    def test_preserves_message_order(self):
        """Test original message order is preserved."""
        state = {
            'messages': [
                HumanMessage(content='msg1'),
                HumanMessage(content='msg2'),
                HumanMessage(content='msg3'),
            ]
        }

        result = prepare_messages_for_model(state)

        # First is system, then original messages
        assert len(result) == 4
        assert result[1].content == 'msg1'
        assert result[2].content == 'msg2'
        assert result[3].content == 'msg3'

    def test_handles_empty_messages(self):
        """Test handles state with no messages."""
        state = {'messages': []}

        result = prepare_messages_for_model(state)

        assert len(result) == 1
        assert isinstance(result[0], SystemMessage)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
