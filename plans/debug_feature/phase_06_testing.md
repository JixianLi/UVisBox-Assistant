# Phase 6: Comprehensive Testing

**Priority**: HIGH
**Timeline**: Week 3-4 (Days 3-5)
**Dependencies**: Phases 1-4 (optionally Phase 5)

## Overview

Comprehensive testing strategy covering all debug and verbose mode features:
- Unit tests for individual components
- Integration tests for feature workflows
- End-to-end tests for complete scenarios
- Manual testing checklist
- Performance benchmarking

## Test Categories

### Unit Tests (0 API calls, instant execution)
- Component-level testing
- Isolated functionality
- Fast feedback loop

### Integration Tests (15-25 API calls per file)
- Feature workflow testing
- Component interaction
- Real LangGraph execution

### E2E Tests (20-30 API calls per file)
- Complete user scenarios
- Full system behavior
- Real-world usage patterns

### Manual Tests (User-paced)
- User experience validation
- Edge case exploration
- Regression checking

## Unit Tests

### Test File 1: Error Tracking

**File**: `tests/unit/test_error_tracking.py`

```python
"""Unit tests for error tracking functionality."""

import pytest
from datetime import datetime
from chatuvisbox.error_tracking import ErrorRecord
from chatuvisbox.conversation import ConversationSession

class TestErrorRecord:
    """Test ErrorRecord class."""

    def test_create_error_record():
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

    def test_error_record_summary():
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

    def test_error_record_summary_auto_fixed():
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

    def test_error_record_detailed():
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

    def test_record_error():
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

    def test_error_history_limit():
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

    def test_get_error_by_id():
        """Test get_error() retrieves by ID."""
        session = ConversationSession()

        session.record_error("tool1", ValueError("1"), "...", "...")
        session.record_error("tool2", ValueError("2"), "...", "...")
        session.record_error("tool3", ValueError("3"), "...", "...")

        error = session.get_error(2)

        assert error is not None
        assert error.error_id == 2
        assert error.tool_name == "tool2"

    def test_get_error_not_found():
        """Test get_error() returns None for invalid ID."""
        session = ConversationSession()

        error = session.get_error(999)

        assert error is None

    def test_get_last_error():
        """Test get_last_error() returns most recent."""
        session = ConversationSession()

        session.record_error("tool1", ValueError("1"), "...", "...")
        session.record_error("tool2", ValueError("2"), "...", "...")

        last = session.get_last_error()

        assert last.error_id == 2
        assert last.tool_name == "tool2"

    def test_get_last_error_empty_history():
        """Test get_last_error() with no errors."""
        session = ConversationSession()

        last = session.get_last_error()

        assert last is None

    def test_error_ids_increment():
        """Test error IDs increment correctly."""
        session = ConversationSession()

        ids = []
        for i in range(5):
            record = session.record_error(
                f"tool{i}", ValueError(f"{i}"), "...", "..."
            )
            ids.append(record.error_id)

        assert ids == [1, 2, 3, 4, 5]
```

### Test File 2: Output Control

**File**: `tests/unit/test_output_control.py`

```python
"""Unit tests for verbose mode output control."""

import pytest
from chatuvisbox.output_control import vprint, is_verbose, set_session
from chatuvisbox.conversation import ConversationSession

def test_vprint_verbose_off(capsys):
    """vprint should not output when verbose is OFF."""
    session = ConversationSession()
    session.verbose_mode = False
    set_session(session)

    vprint("Test message")

    captured = capsys.readouterr()
    assert captured.out == ""

def test_vprint_verbose_on(capsys):
    """vprint should output when verbose is ON."""
    session = ConversationSession()
    session.verbose_mode = True
    set_session(session)

    vprint("Test message")

    captured = capsys.readouterr()
    assert "Test message" in captured.out

def test_vprint_force_always_prints(capsys):
    """vprint with force=True should always output."""
    session = ConversationSession()
    session.verbose_mode = False
    set_session(session)

    vprint("Forced message", force=True)

    captured = capsys.readouterr()
    assert "Forced message" in captured.out

def test_is_verbose_returns_correct_state():
    """is_verbose should return correct state."""
    session = ConversationSession()

    session.verbose_mode = False
    set_session(session)
    assert is_verbose() is False

    session.verbose_mode = True
    assert is_verbose() is True

def test_vprint_no_session(capsys):
    """vprint should not crash with no session set."""
    set_session(None)

    vprint("Message")  # Should not print, should not crash

    captured = capsys.readouterr()
    assert captured.out == ""
```

### Test File 3: Error Interpretation

**File**: `tests/unit/test_error_interpretation.py`

```python
"""Unit tests for error interpretation."""

import pytest
from chatuvisbox.error_interpretation import (
    interpret_uvisbox_error,
    format_error_with_hint,
    _extract_colormap_name,
    _extract_method_name,
    _extract_valid_methods
)

def test_colormap_error_no_debug():
    """Test colormap error without debug mode."""
    error = ValueError("Invalid colormap name 'Reds'")
    traceback = "...matplotlib..."

    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=False)

    assert "Colormap error" in user_msg
    assert hint is None

def test_colormap_error_with_debug():
    """Test colormap error with debug mode."""
    error = ValueError("Invalid colormap name 'Reds'")
    traceback = "...matplotlib...mpl_colors..."

    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=True)

    assert "Colormap error" in user_msg
    assert hint is not None
    assert "UVisBox" in hint

def test_method_error():
    """Test method validation error."""
    error = ValueError("Unknown method 'fbd'. Choose 'fdb' or 'mfbd'.")
    traceback = "..."

    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=True)

    assert "Method validation error" in user_msg
    assert hint is not None
    assert "'fbd'" in hint

def test_shape_error():
    """Test shape mismatch error."""
    error = ValueError("Expected 2D array, got shape (100, 50, 3)")
    traceback = "..."

    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=True)

    assert "shape" in user_msg.lower()
    assert hint is not None

def test_format_error_with_hint():
    """Test error formatting with hint."""
    formatted = format_error_with_hint("Error", "Hint here")

    assert "Error" in formatted
    assert "💡 Debug hint:" in formatted
    assert "Hint here" in formatted

def test_format_error_without_hint():
    """Test error formatting without hint."""
    formatted = format_error_with_hint("Error", None)

    assert formatted == "Error"
    assert "💡" not in formatted
```

### Test File 4: Command Handlers

**File**: `tests/unit/test_command_handlers.py`

```python
"""Unit tests for command handlers."""

import pytest
from chatuvisbox.conversation import ConversationSession
from chatuvisbox.main import handle_command

def test_debug_on():
    """Test /debug on command."""
    session = ConversationSession()
    assert session.debug_mode is False

    result = handle_command("/debug on", session)

    assert result is True
    assert session.debug_mode is True

def test_debug_off():
    """Test /debug off command."""
    session = ConversationSession()
    session.debug_mode = True

    result = handle_command("/debug off", session)

    assert result is True
    assert session.debug_mode is False

def test_verbose_on():
    """Test /verbose on command."""
    session = ConversationSession()
    assert session.verbose_mode is False

    result = handle_command("/verbose on", session)

    assert result is True
    assert session.verbose_mode is True

def test_verbose_off():
    """Test /verbose off command."""
    session = ConversationSession()
    session.verbose_mode = True

    result = handle_command("/verbose off", session)

    assert result is True
    assert session.verbose_mode is False

def test_errors_command_empty(capsys):
    """Test /errors with no history."""
    session = ConversationSession()

    handle_command("/errors", session)

    captured = capsys.readouterr()
    assert "No errors recorded" in captured.out

def test_errors_command_with_history(capsys):
    """Test /errors with error history."""
    session = ConversationSession()
    session.record_error("tool", ValueError("test"), "...", "...")

    handle_command("/errors", session)

    captured = capsys.readouterr()
    assert "Error History" in captured.out

def test_trace_last(capsys):
    """Test /trace last command."""
    session = ConversationSession()
    session.record_error("tool", ValueError("test"), "full trace...", "...")

    handle_command("/trace last", session)

    captured = capsys.readouterr()
    assert "full trace..." in captured.out

def test_trace_by_id(capsys):
    """Test /trace <id> command."""
    session = ConversationSession()
    session.record_error("tool", ValueError("test"), "trace...", "...")

    handle_command("/trace 1", session)

    captured = capsys.readouterr()
    assert "trace..." in captured.out

def test_non_command_returns_false():
    """Test non-command input returns False."""
    session = ConversationSession()

    result = handle_command("generate curves", session)

    assert result is False
```

## Integration Tests

### Test File 5: Verbose Mode Integration

**File**: `tests/integration/test_verbose_mode_integration.py`

```python
"""Integration tests for verbose mode."""

import pytest
from chatuvisbox.conversation import ConversationSession

def test_verbose_off_hides_messages(capsys):
    """Test verbose OFF hides internal messages."""
    session = ConversationSession()
    session.verbose_mode = False

    # Execute command (would trigger vprint calls)
    # ... execute ...

    captured = capsys.readouterr()
    assert "[HYBRID]" not in captured.out
    assert "[DATA TOOL]" not in captured.out

def test_verbose_on_shows_messages(capsys):
    """Test verbose ON shows internal messages."""
    session = ConversationSession()
    session.verbose_mode = True

    # Execute command
    # ... execute ...

    captured = capsys.readouterr()
    # Should contain internal messages
    # (exact assertion depends on execution)

def test_independent_debug_verbose_modes():
    """Test debug and verbose modes are independent."""
    session = ConversationSession()

    # Enable only debug
    session.debug_mode = True
    session.verbose_mode = False
    assert session.debug_mode is True
    assert session.verbose_mode is False

    # Enable both
    session.verbose_mode = True
    assert session.debug_mode is True
    assert session.verbose_mode is True

    # Disable debug, keep verbose
    session.debug_mode = False
    assert session.debug_mode is False
    assert session.verbose_mode is True
```

### Test File 6: Error Tracking Workflow

**File**: `tests/integration/test_error_tracking_workflow.py`

```python
"""Integration tests for error tracking workflow."""

import pytest
from chatuvisbox.conversation import ConversationSession

def test_error_recorded_on_tool_failure():
    """Test error is recorded when tool fails."""
    session = ConversationSession()

    # Trigger tool error (mock or real)
    # ... trigger error ...

    # Verify error was recorded
    assert len(session.error_history) > 0
    last_error = session.get_last_error()
    assert last_error is not None

def test_error_interpretation_applied():
    """Test error interpretation is applied."""
    session = ConversationSession()
    session.debug_mode = True

    # Trigger known error pattern (e.g., colormap error)
    # ... trigger error ...

    # Verify interpreted message
    last_error = session.get_last_error()
    assert "Debug hint" in last_error.user_facing_message or "hint" in last_error.user_facing_message.lower()

def test_multiple_errors_tracked():
    """Test multiple errors are tracked correctly."""
    session = ConversationSession()

    # Trigger 3 different errors
    # ... trigger errors ...

    assert len(session.error_history) == 3
    assert session.error_history[0].error_id == 1
    assert session.error_history[-1].error_id == 3
```

## E2E Tests

### Test File 7: Complete Debug Workflow

**File**: `tests/e2e/test_debug_workflow.py`

```python
"""End-to-end tests for complete debug workflows."""

import pytest
from chatuvisbox.conversation import ConversationSession

def test_complete_debug_workflow():
    """Test complete debug workflow from user perspective."""
    session = ConversationSession()

    # Step 1: Normal operation (debug OFF)
    response1 = session.send("generate 30 curves")
    assert response1 is not None

    # Step 2: Trigger error
    response2 = session.send("plot with invalid colormap Reds")
    # Error should occur

    # Step 3: Enable debug mode
    session.debug_mode = True

    # Step 4: Trigger same error
    response3 = session.send("plot with colormap Reds")
    # Should see enhanced error message

    # Step 5: Check error history
    assert len(session.error_history) >= 2

    # Step 6: View trace
    last_error = session.get_last_error()
    assert last_error is not None
    assert len(last_error.full_traceback) > 0

def test_verbose_mode_workflow():
    """Test complete verbose mode workflow."""
    session = ConversationSession()

    # Enable verbose
    session.verbose_mode = True

    # Execute commands
    response1 = session.send("generate 30 curves")
    response2 = session.send("plot functional boxplot")

    # Should have internal messages (check logs or captured output)

    # Disable verbose
    session.verbose_mode = False

    # Execute again
    response3 = session.send("colormap plasma")

    # Should NOT have internal messages
```

## Manual Testing Checklist

### Debug Mode Testing

- [ ] `/debug on` - Verify confirmation message
- [ ] Trigger error with debug OFF - Verify concise message
- [ ] Trigger same error with debug ON - Verify full traceback
- [ ] `/debug off` - Verify confirmation
- [ ] Colormap error with debug ON - Verify helpful hint
- [ ] Method error with debug ON - Verify method suggestions
- [ ] Shape error with debug ON - Verify shape information

### Verbose Mode Testing

- [ ] Default (verbose OFF) - Verify clean output, no [TOOL] messages
- [ ] `/verbose on` - Verify confirmation
- [ ] Execute hybrid command - Verify [HYBRID] messages shown
- [ ] Execute data tool - Verify [DATA TOOL] messages shown
- [ ] Execute vis tool - Verify [VIS TOOL] messages shown
- [ ] `/verbose off` - Verify confirmation
- [ ] Execute command - Verify clean output again

### Error Tracking Testing

- [ ] Trigger 3 errors - Verify all recorded
- [ ] `/errors` - Verify all 3 listed with IDs
- [ ] `/trace 1` - Verify specific error shown
- [ ] `/trace 2` - Verify different error shown
- [ ] `/trace last` - Verify most recent error shown
- [ ] `/trace 999` - Verify "not found" message
- [ ] `/trace invalid` - Verify error message for invalid ID

### Combined Modes Testing

- [ ] Enable both debug and verbose
- [ ] Trigger error - Verify full traceback + internal messages
- [ ] Execute successful command - Verify internal messages only
- [ ] Disable debug only - Verify verbose still works
- [ ] Disable verbose only - Verify debug still works

### Context Command Testing

- [ ] `/context` - Verify mode states shown (both OFF)
- [ ] Enable debug - `/context` - Verify 🐛 ON
- [ ] Enable verbose - `/context` - Verify 📢 ON
- [ ] `/context` - Verify error history count shown

### Help Command Testing

- [ ] `/help` - Verify all debug/verbose commands documented
- [ ] Verify examples are clear
- [ ] Verify grouped sections (basic, debug, error tracking)

## Performance Benchmarks

### Benchmark 1: vprint Overhead

**Test**: Measure execution time with verbose ON vs OFF

```python
import time

def benchmark_vprint_overhead():
    """Measure vprint performance overhead."""
    session = ConversationSession()

    # Test with verbose OFF
    session.verbose_mode = False
    start = time.time()
    for i in range(10000):
        vprint(f"Message {i}")
    time_off = time.time() - start

    # Test with verbose ON
    session.verbose_mode = True
    start = time.time()
    for i in range(10000):
        vprint(f"Message {i}")
    time_on = time.time() - start

    overhead = (time_on - time_off) / time_off * 100
    print(f"Verbose OFF: {time_off:.3f}s")
    print(f"Verbose ON: {time_on:.3f}s")
    print(f"Overhead: {overhead:.1f}%")

    # Should be < 5% overhead when OFF
    assert overhead < 5
```

### Benchmark 2: Error Recording Overhead

**Test**: Measure error recording performance

```python
def benchmark_error_recording():
    """Measure error recording performance."""
    session = ConversationSession()

    start = time.time()
    for i in range(1000):
        session.record_error(
            f"tool{i}",
            ValueError(f"Error {i}"),
            "Traceback...",
            f"Message {i}"
        )
    elapsed = time.time() - start

    print(f"1000 errors recorded in {elapsed:.3f}s")
    print(f"Per-error: {elapsed/1000*1000:.2f}ms")

    # Should be < 1ms per error
    assert elapsed / 1000 < 0.001
```

## Test Execution Strategy

### Quick Tests (Daily Development)
```bash
# Run only unit tests (instant, 0 API calls)
pytest tests/unit/ -v
```

### Standard Tests (Before PR)
```bash
# Run unit + integration (some API calls)
pytest tests/unit/ tests/integration/ -v
```

### Full Tests (Before Release)
```bash
# Run everything including E2E
pytest tests/ -v
```

## Acceptance Criteria

### Unit Tests
- ✅ All ErrorRecord tests pass
- ✅ All output control tests pass
- ✅ All error interpretation tests pass
- ✅ All command handler tests pass
- ✅ 100% coverage for new modules

### Integration Tests
- ✅ Verbose mode integration tests pass
- ✅ Error tracking workflow tests pass
- ✅ Independent mode operation verified

### E2E Tests
- ✅ Complete debug workflow test passes
- ✅ Complete verbose workflow test passes
- ✅ Combined modes test passes

### Manual Tests
- ✅ All manual checklist items verified
- ✅ No regressions in existing functionality
- ✅ User experience is smooth and intuitive

### Performance
- ✅ vprint overhead < 5% when verbose OFF
- ✅ Error recording < 1ms per error
- ✅ No noticeable slowdown in conversation

## Documentation Updates

After testing complete, update:
- ✅ `docs/USER_GUIDE.md` - Add debug/verbose mode section
- ✅ `docs/API.md` - Document new classes and functions
- ✅ `CLAUDE.md` - Update with error handling patterns
- ✅ `TESTING.md` - Add debug feature testing notes
- ✅ `CHANGELOG.md` - Document new features

## Final Release Checklist

- [ ] All unit tests pass (100%)
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] Manual testing complete
- [ ] Performance benchmarks acceptable
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] README updated (if needed)
- [ ] No regressions
- [ ] User experience validated

## Next Steps

After Phase 6 complete:
- 🎉 **Feature ready for release!**
- Create PR with all changes
- Request code review
- Merge to main
- Tag release version
- Announce new features to users
