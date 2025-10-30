"""Unit tests for error tracking functionality."""

import pytest
from datetime import datetime
from chatuvisbox.error_tracking import ErrorRecord
from chatuvisbox.conversation import ConversationSession


class TestErrorRecord:
    """Test ErrorRecord class."""

    def test_create_error_record(self):
        """Test ErrorRecord creation with all fields."""
        record = ErrorRecord(
            error_id=1,
            timestamp=datetime.now(),
            tool_name="test_tool",
            error_type="ValueError",
            error_message="Test error message",
            full_traceback="Traceback...",
            user_facing_message="User-friendly message",
            auto_fixed=False,
            context={"key": "value"}
        )

        assert record.error_id == 1
        assert record.tool_name == "test_tool"
        assert record.error_type == "ValueError"
        assert record.auto_fixed is False

    def test_error_record_summary(self):
        """Test ErrorRecord.summary() format."""
        record = ErrorRecord(
            error_id=5,
            timestamp=datetime(2025, 1, 30, 10, 23, 45),
            tool_name="plot_boxplot",
            error_type="TypeError",
            error_message="...",
            full_traceback="...",
            user_facing_message="...",
            auto_fixed=False
        )

        summary = record.summary()

        assert "[5]" in summary
        assert "10:23:45" in summary
        assert "plot_boxplot" in summary
        assert "TypeError" in summary
        assert "failed" in summary

    def test_error_record_summary_auto_fixed(self):
        """Test ErrorRecord.summary() shows auto-fixed status."""
        record = ErrorRecord(
            error_id=1,
            timestamp=datetime.now(),
            tool_name="test_tool",
            error_type="ValueError",
            error_message="...",
            full_traceback="...",
            user_facing_message="...",
            auto_fixed=True
        )

        summary = record.summary()

        assert "auto-fixed" in summary

    def test_error_record_detailed(self):
        """Test ErrorRecord.detailed() includes all information."""
        record = ErrorRecord(
            error_id=1,
            timestamp=datetime.now(),
            tool_name="test_tool",
            error_type="ValueError",
            error_message="Test error",
            full_traceback="Full traceback...\nline 2\nline 3",
            user_facing_message="User message",
            auto_fixed=False,
            context={"data_path": "/tmp/test.npy"}
        )

        detailed = record.detailed()

        assert "Error ID: 1" in detailed
        assert "Tool: test_tool" in detailed
        assert "Type: ValueError" in detailed
        assert "Full traceback..." in detailed
        assert "Context:" in detailed
        assert "data_path" in detailed


class TestConversationSessionErrorTracking:
    """Test error tracking in ConversationSession."""

    def test_record_error(self):
        """Test record_error() creates ErrorRecord."""
        session = ConversationSession()

        error = ValueError("Test error")
        record = session.record_error(
            tool_name="test_tool",
            error=error,
            traceback_str="Traceback...",
            user_message="User-friendly message"
        )

        assert record.error_id == 1
        assert record.tool_name == "test_tool"
        assert record.error_type == "ValueError"
        assert len(session.error_history) == 1

    def test_error_history_limit(self):
        """Test error history respects max_error_history."""
        session = ConversationSession()
        session.max_error_history = 3

        # Record 5 errors
        for i in range(5):
            session.record_error(
                tool_name=f"tool_{i}",
                error=ValueError(f"Error {i}"),
                traceback_str="...",
                user_message=f"Message {i}"
            )

        # Should only keep last 3
        assert len(session.error_history) == 3
        assert session.error_history[0].error_id == 3  # Oldest kept
        assert session.error_history[-1].error_id == 5  # Most recent

    def test_get_error_by_id(self):
        """Test get_error() retrieves by ID."""
        session = ConversationSession()

        session.record_error("tool1", ValueError("1"), "...", "...")
        session.record_error("tool2", ValueError("2"), "...", "...")
        session.record_error("tool3", ValueError("3"), "...", "...")

        error = session.get_error(2)

        assert error is not None
        assert error.error_id == 2
        assert error.tool_name == "tool2"

    def test_get_error_not_found(self):
        """Test get_error() returns None for invalid ID."""
        session = ConversationSession()

        error = session.get_error(999)

        assert error is None

    def test_get_last_error(self):
        """Test get_last_error() returns most recent."""
        session = ConversationSession()

        session.record_error("tool1", ValueError("1"), "...", "...")
        session.record_error("tool2", ValueError("2"), "...", "...")

        last = session.get_last_error()

        assert last.error_id == 2
        assert last.tool_name == "tool2"

    def test_get_last_error_empty_history(self):
        """Test get_last_error() with no errors."""
        session = ConversationSession()

        last = session.get_last_error()

        assert last is None

    def test_error_ids_increment(self):
        """Test error IDs increment correctly."""
        session = ConversationSession()

        ids = []
        for i in range(5):
            record = session.record_error(
                f"tool{i}", ValueError(f"{i}"), "...", "..."
            )
            ids.append(record.error_id)

        assert ids == [1, 2, 3, 4, 5]

    def test_auto_fix_tracking(self):
        """Test auto-fix detection and marking."""
        session = ConversationSession()

        # Record an error
        record = session.record_error("tool1", ValueError("1"), "...", "...")

        # Initially not auto-fixed
        assert not session.is_error_auto_fixed(record.error_id)

        # Mark as auto-fixed
        session.mark_error_auto_fixed(record.error_id)

        # Now should be auto-fixed
        assert session.is_error_auto_fixed(record.error_id)
