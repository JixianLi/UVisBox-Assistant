# ABOUTME: Unit tests for session/conversation.py (0 API calls).
# ABOUTME: Tests ConversationSession class with mocked graph execution and error tracking.

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from uvisbox_assistant.session.conversation import ConversationSession


class TestConversationSessionInit:
    """Test ConversationSession initialization."""

    def test_initializes_with_none_state(self):
        """Test session starts with no state."""
        session = ConversationSession()

        assert session.state is None
        assert session.turn_count == 0
        assert session.debug_mode is False
        assert session.verbose_mode is False

    def test_initializes_error_tracking(self):
        """Test error tracking is initialized."""
        session = ConversationSession()

        assert session.error_history == []
        assert session.max_error_history == 20
        assert session._next_error_id == 1
        assert session.auto_fixed_errors == set()


class TestConversationSessionSend:
    """Test ConversationSession.send method."""

    @patch('uvisbox_assistant.session.conversation.graph_app')
    @patch('uvisbox_assistant.session.conversation.is_hybrid_eligible')
    def test_send_creates_initial_state_on_first_turn(self, mock_hybrid, mock_graph):
        """Test send creates state on first turn."""
        mock_hybrid.return_value = False
        mock_graph.invoke.return_value = {
            'messages': [HumanMessage(content='test'), AIMessage(content='response')],
            'current_data_path': None,
            'error_count': 0
        }

        session = ConversationSession()
        result = session.send("test message")

        assert session.turn_count == 1
        assert session.state is not None
        mock_graph.invoke.assert_called_once()

    @patch('uvisbox_assistant.session.conversation.graph_app')
    @patch('uvisbox_assistant.session.conversation.is_hybrid_eligible')
    def test_send_appends_to_existing_state(self, mock_hybrid, mock_graph):
        """Test send appends message to existing state."""
        mock_hybrid.return_value = False

        # First call
        mock_graph.invoke.return_value = {
            'messages': [HumanMessage(content='msg1'), AIMessage(content='resp1')],
            'current_data_path': None,
            'error_count': 0
        }
        session = ConversationSession()
        session.send("first")

        # Second call
        mock_graph.invoke.return_value = {
            'messages': [
                HumanMessage(content='msg1'),
                AIMessage(content='resp1'),
                HumanMessage(content='second'),
                AIMessage(content='resp2')
            ],
            'current_data_path': None,
            'error_count': 0
        }
        session.send("second")

        assert session.turn_count == 2
        assert len(session.state['messages']) == 4

    @patch('uvisbox_assistant.session.conversation.execute_simple_command')
    @patch('uvisbox_assistant.session.conversation.is_hybrid_eligible')
    def test_send_uses_hybrid_control_when_eligible(self, mock_hybrid, mock_execute):
        """Test send uses hybrid control for simple commands."""
        mock_hybrid.return_value = True
        mock_execute.return_value = (True, {'_tool_name': 'plot_test', 'param': 'value'}, 'Updated')

        session = ConversationSession()
        session.state = {
            'messages': [HumanMessage(content='previous')],
            'last_vis_params': {'_tool_name': 'plot_test'}
        }

        result = session.send("colormap plasma")

        assert session.turn_count == 1
        assert result['error_count'] == 0
        mock_execute.assert_called_once()

    @patch('uvisbox_assistant.session.conversation.graph_app')
    @patch('uvisbox_assistant.session.conversation.is_hybrid_eligible')
    def test_send_falls_back_to_graph_when_hybrid_fails(self, mock_hybrid, mock_graph):
        """Test send falls back to full graph when hybrid fails."""
        mock_hybrid.return_value = True

        with patch('uvisbox_assistant.session.conversation.execute_simple_command') as mock_execute:
            mock_execute.return_value = (False, None, "Failed")
            mock_graph.invoke.return_value = {
                'messages': [HumanMessage(content='test'), AIMessage(content='response')],
                'current_data_path': None,
                'error_count': 0
            }

            session = ConversationSession()
            session.state = {'messages': []}
            result = session.send("test")

            mock_graph.invoke.assert_called_once()


class TestConversationSessionGetLastResponse:
    """Test get_last_response method."""

    def test_returns_empty_string_when_no_state(self):
        """Test returns empty string with no state."""
        session = ConversationSession()

        result = session.get_last_response()

        assert result == ""

    def test_returns_last_ai_message(self):
        """Test returns most recent AI message."""
        session = ConversationSession()
        session.state = {
            'messages': [
                HumanMessage(content='user1'),
                AIMessage(content='response1'),
                HumanMessage(content='user2'),
                AIMessage(content='response2')
            ]
        }

        result = session.get_last_response()

        assert result == 'response2'

    def test_returns_empty_when_no_ai_messages(self):
        """Test returns empty when no AI messages."""
        session = ConversationSession()
        session.state = {
            'messages': [HumanMessage(content='user1')]
        }

        result = session.get_last_response()

        assert result == ""


class TestConversationSessionGetContextSummary:
    """Test get_context_summary method."""

    def test_returns_empty_context_when_no_state(self):
        """Test returns empty context with no state."""
        session = ConversationSession()

        result = session.get_context_summary()

        assert result['turn_count'] == 0
        assert result['current_data'] is None
        assert result['error_count'] == 0

    def test_returns_context_with_state(self):
        """Test returns context summary from state."""
        session = ConversationSession()
        session.state = {
            'messages': [HumanMessage(content='m1'), AIMessage(content='m2')],
            'current_data_path': '/path/to/data.npy',
            'last_vis_params': {'_tool_name': 'plot_test'},
            'processed_statistics': {'median': {}},
            'analysis_report': 'Test report',
            'analysis_type': 'quick',
            'session_files': ['file1.npy', 'file2.npy'],
            'error_count': 1
        }
        session.turn_count = 5

        result = session.get_context_summary()

        assert result['turn_count'] == 5
        assert result['current_data'] == '/path/to/data.npy'
        assert result['statistics'] == 'computed'
        assert result['analysis'] == 'quick'
        assert len(result['session_files']) == 2
        assert result['error_count'] == 1
        assert result['message_count'] == 2


class TestConversationSessionReset:
    """Test reset and clear methods."""

    def test_reset_clears_state(self):
        """Test reset clears conversation state."""
        session = ConversationSession()
        session.state = {'messages': []}
        session.turn_count = 5

        session.reset()

        assert session.state is None
        assert session.turn_count == 0

    @patch('uvisbox_assistant.tools.data_tools.clear_session')
    def test_clear_removes_files_and_resets(self, mock_clear):
        """Test clear removes files and resets state."""
        mock_clear.return_value = {'status': 'success', 'message': 'Cleared'}

        session = ConversationSession()
        session.state = {'messages': []}
        session.turn_count = 3

        with patch('builtins.print'):
            session.clear()

        mock_clear.assert_called_once()
        assert session.state is None
        assert session.turn_count == 0


class TestConversationSessionErrorTracking:
    """Test error tracking functionality."""

    def test_record_error_creates_error_record(self):
        """Test record_error creates and stores ErrorRecord."""
        session = ConversationSession()

        error = ValueError("Test error")
        record = session.record_error(
            tool_name='test_tool',
            error=error,
            traceback_str='traceback here',
            user_message='Error occurred'
        )

        assert record.error_id == 1
        assert record.tool_name == 'test_tool'
        assert record.error_type == 'ValueError'
        assert len(session.error_history) == 1

    def test_record_error_increments_id(self):
        """Test error ID increments."""
        session = ConversationSession()

        error1 = ValueError("Error 1")
        error2 = ValueError("Error 2")

        record1 = session.record_error('tool1', error1, '', 'msg1')
        record2 = session.record_error('tool2', error2, '', 'msg2')

        assert record1.error_id == 1
        assert record2.error_id == 2
        assert session._next_error_id == 3

    def test_get_error_returns_correct_error(self):
        """Test get_error retrieves by ID."""
        session = ConversationSession()

        error = ValueError("Test")
        record = session.record_error('tool', error, '', 'msg')

        retrieved = session.get_error(record.error_id)

        assert retrieved is record

    def test_get_error_returns_none_when_not_found(self):
        """Test get_error returns None for missing ID."""
        session = ConversationSession()

        result = session.get_error(999)

        assert result is None

    def test_get_last_error_returns_most_recent(self):
        """Test get_last_error returns most recent error."""
        session = ConversationSession()

        error1 = ValueError("Error 1")
        error2 = ValueError("Error 2")

        session.record_error('tool1', error1, '', 'msg1')
        record2 = session.record_error('tool2', error2, '', 'msg2')

        result = session.get_last_error()

        assert result is record2

    def test_mark_error_auto_fixed(self):
        """Test marking error as auto-fixed."""
        session = ConversationSession()

        with patch('uvisbox_assistant.session.conversation.vprint'):
            session.mark_error_auto_fixed(1)

        assert session.is_error_auto_fixed(1) is True
        assert session.is_error_auto_fixed(2) is False


class TestConversationSessionAnalysis:
    """Test analysis-related methods."""

    def test_get_analysis_summary_returns_none_when_no_analysis(self):
        """Test returns None when no analysis in state."""
        session = ConversationSession()
        session.state = {'messages': []}

        result = session.get_analysis_summary()

        assert result is None

    def test_get_analysis_summary_with_statistics(self):
        """Test returns summary with statistics."""
        session = ConversationSession()
        session.state = {
            'processed_statistics': {
                'data_shape': {'n_curves': 100, 'n_points': 50},
                'median': {'trend': 'increasing'},
                'outliers': {'count': 3}
            }
        }

        result = session.get_analysis_summary()

        assert '100 curves' in result
        assert '50 points' in result
        assert 'increasing' in result
        assert '3' in result

    def test_get_analysis_summary_with_report(self):
        """Test returns summary with report."""
        session = ConversationSession()
        session.state = {
            'analysis_report': 'This is a detailed analysis report about the data.',
            'analysis_type': 'detailed'
        }

        result = session.get_analysis_summary()

        assert 'detailed' in result
        assert 'This is a detailed' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
