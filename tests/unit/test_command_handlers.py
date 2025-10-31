"""Unit tests for command handlers.

These tests verify the command handling logic in main.py.
Since commands are handled inline in the main() function, we test
them by directly manipulating ConversationSession state and using
helper functions.
"""

from uvisbox_assistant.conversation import ConversationSession


class TestDebugCommands:
    """Test /debug on/off commands."""

    def test_debug_mode_defaults_to_false(self):
        """Debug mode should default to OFF."""
        session = ConversationSession()
        assert session.debug_mode is False

    def test_debug_mode_can_be_enabled(self):
        """Test enabling debug mode."""
        session = ConversationSession()
        session.debug_mode = True
        assert session.debug_mode is True

    def test_debug_mode_can_be_disabled(self):
        """Test disabling debug mode."""
        session = ConversationSession()
        session.debug_mode = True
        session.debug_mode = False
        assert session.debug_mode is False

    def test_debug_mode_toggle(self):
        """Test toggling debug mode multiple times."""
        session = ConversationSession()

        # OFF -> ON
        session.debug_mode = True
        assert session.debug_mode is True

        # ON -> OFF
        session.debug_mode = False
        assert session.debug_mode is False

        # OFF -> ON again
        session.debug_mode = True
        assert session.debug_mode is True


class TestVerboseCommands:
    """Test /verbose on/off commands."""

    def test_verbose_mode_defaults_to_false(self):
        """Verbose mode should default to OFF."""
        session = ConversationSession()
        assert session.verbose_mode is False

    def test_verbose_mode_can_be_enabled(self):
        """Test enabling verbose mode."""
        session = ConversationSession()
        session.verbose_mode = True
        assert session.verbose_mode is True

    def test_verbose_mode_can_be_disabled(self):
        """Test disabling verbose mode."""
        session = ConversationSession()
        session.verbose_mode = True
        session.verbose_mode = False
        assert session.verbose_mode is False

    def test_verbose_mode_toggle(self):
        """Test toggling verbose mode multiple times."""
        session = ConversationSession()

        # OFF -> ON
        session.verbose_mode = True
        assert session.verbose_mode is True

        # ON -> OFF
        session.verbose_mode = False
        assert session.verbose_mode is False

        # OFF -> ON again
        session.verbose_mode = True
        assert session.verbose_mode is True


class TestErrorCommands:
    """Test /errors command."""

    def test_errors_command_with_empty_history(self):
        """Test /errors with no error history."""
        session = ConversationSession()
        assert len(session.error_history) == 0

    def test_errors_command_with_history(self):
        """Test /errors with error history."""
        session = ConversationSession()

        # Add mock error
        session.record_error(
            tool_name="test_tool",
            error=ValueError("test error"),
            traceback_str="traceback...",
            user_message="Test error message"
        )

        assert len(session.error_history) == 1
        assert session.error_history[0].error_id == 1
        assert session.error_history[0].tool_name == "test_tool"

    def test_errors_command_with_multiple_errors(self):
        """Test /errors with multiple errors."""
        session = ConversationSession()

        # Add 3 mock errors
        for i in range(3):
            session.record_error(
                tool_name=f"tool_{i}",
                error=ValueError(f"error {i}"),
                traceback_str="...",
                user_message=f"Message {i}"
            )

        assert len(session.error_history) == 3
        assert session.error_history[0].error_id == 1
        assert session.error_history[1].error_id == 2
        assert session.error_history[2].error_id == 3


class TestTraceCommands:
    """Test /trace <id> and /trace last commands."""

    def test_trace_by_id_valid(self):
        """Test /trace <id> with valid ID."""
        session = ConversationSession()

        # Add mock error
        session.record_error(
            tool_name="test_tool",
            error=ValueError("test error"),
            traceback_str="full traceback...",
            user_message="Test error"
        )

        error = session.get_error(1)
        assert error is not None
        assert error.error_id == 1
        assert "full traceback..." in error.full_traceback

    def test_trace_by_id_invalid(self):
        """Test /trace <id> with invalid ID."""
        session = ConversationSession()

        error = session.get_error(999)
        assert error is None

    def test_trace_last_with_errors(self):
        """Test /trace last with error history."""
        session = ConversationSession()

        # Add multiple errors
        session.record_error("tool1", ValueError("1"), "trace1", "msg1")
        session.record_error("tool2", ValueError("2"), "trace2", "msg2")
        session.record_error("tool3", ValueError("3"), "trace3", "msg3")

        last_error = session.get_last_error()
        assert last_error is not None
        assert last_error.error_id == 3
        assert last_error.tool_name == "tool3"
        assert "trace3" in last_error.full_traceback

    def test_trace_last_with_no_errors(self):
        """Test /trace last with no error history."""
        session = ConversationSession()

        last_error = session.get_last_error()
        assert last_error is None

    def test_trace_specific_error_in_history(self):
        """Test /trace <id> retrieves specific error from history."""
        session = ConversationSession()

        # Add 3 errors
        session.record_error("tool1", ValueError("1"), "trace1", "msg1")
        session.record_error("tool2", ValueError("2"), "trace2", "msg2")
        session.record_error("tool3", ValueError("3"), "trace3", "msg3")

        # Get middle error
        error = session.get_error(2)
        assert error is not None
        assert error.error_id == 2
        assert error.tool_name == "tool2"
        assert "trace2" in error.full_traceback


class TestIndependentModes:
    """Test that debug and verbose modes are independent."""

    def test_debug_and_verbose_independent(self):
        """Test debug and verbose can be set independently."""
        session = ConversationSession()

        # Enable only debug
        session.debug_mode = True
        session.verbose_mode = False
        assert session.debug_mode is True
        assert session.verbose_mode is False

        # Enable only verbose
        session.debug_mode = False
        session.verbose_mode = True
        assert session.debug_mode is False
        assert session.verbose_mode is True

        # Enable both
        session.debug_mode = True
        session.verbose_mode = True
        assert session.debug_mode is True
        assert session.verbose_mode is True

        # Disable both
        session.debug_mode = False
        session.verbose_mode = False
        assert session.debug_mode is False
        assert session.verbose_mode is False

    def test_disabling_debug_keeps_verbose(self):
        """Test disabling debug doesn't affect verbose."""
        session = ConversationSession()

        session.debug_mode = True
        session.verbose_mode = True

        session.debug_mode = False

        assert session.debug_mode is False
        assert session.verbose_mode is True

    def test_disabling_verbose_keeps_debug(self):
        """Test disabling verbose doesn't affect debug."""
        session = ConversationSession()

        session.debug_mode = True
        session.verbose_mode = True

        session.verbose_mode = False

        assert session.debug_mode is True
        assert session.verbose_mode is False


class TestAutoFixTracking:
    """Test auto-fix status tracking in error history."""

    def test_auto_fix_status_displayed(self):
        """Test auto-fix status is tracked correctly."""
        session = ConversationSession()

        # Record error
        error = session.record_error("tool1", ValueError("1"), "trace1", "msg1")

        # Initially not auto-fixed
        assert not session.is_error_auto_fixed(error.error_id)

        # Mark as auto-fixed
        session.mark_error_auto_fixed(error.error_id)

        # Should now be auto-fixed
        assert session.is_error_auto_fixed(error.error_id)

    def test_multiple_errors_auto_fix_tracking(self):
        """Test auto-fix tracking with multiple errors."""
        session = ConversationSession()

        # Record 3 errors
        err1 = session.record_error("tool1", ValueError("1"), "t1", "m1")
        err2 = session.record_error("tool2", ValueError("2"), "t2", "m2")
        err3 = session.record_error("tool3", ValueError("3"), "t3", "m3")

        # Mark only error 2 as auto-fixed
        session.mark_error_auto_fixed(err2.error_id)

        # Check status
        assert not session.is_error_auto_fixed(err1.error_id)
        assert session.is_error_auto_fixed(err2.error_id)
        assert not session.is_error_auto_fixed(err3.error_id)
