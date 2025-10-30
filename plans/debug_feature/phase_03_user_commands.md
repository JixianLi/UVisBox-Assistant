# Phase 3: User Commands

**Priority**: HIGH
**Timeline**: Week 2 (Days 1-3)
**Dependencies**: Phase 1 (error history), Phase 2 (verbose mode)

## Overview

Implement user-facing commands to control debug and verbose modes:
- `/debug on/off` - Toggle verbose error output with tracebacks
- `/verbose on/off` - Toggle internal state messages
- `/errors` - List recent errors
- `/trace <id>` - Show full stack trace for specific error
- `/trace last` - Show last error stack trace
- Update `/help` command with new documentation

## Commands Summary

| Command | Description | Default State |
|---------|-------------|---------------|
| `/debug on` | Enable full error tracebacks | OFF |
| `/debug off` | Disable full error tracebacks | OFF |
| `/verbose on` | Show internal messages ([HYBRID], [TOOL]) | OFF |
| `/verbose off` | Hide internal messages | OFF |
| `/errors` | List error history with IDs | N/A |
| `/trace <id>` | Show full trace for error ID | N/A |
| `/trace last` | Show last error trace | N/A |

## Deliverables

### 3.1 Add Command Handlers to main.py

**File**: `src/chatuvisbox/main.py`

**Current Command Structure**:
```python
def handle_command(user_input: str, session: ConversationSession) -> bool:
    """Handle special commands. Returns True if command was handled."""

    if user_input == "/help":
        # ... existing help text ...
        return True

    elif user_input == "/context":
        # ... existing context display ...
        return True

    elif user_input == "/stats":
        # ... existing stats display ...
        return True

    elif user_input == "/clear":
        # ... existing clear logic ...
        return True

    elif user_input == "/reset":
        # ... existing reset logic ...
        return True

    elif user_input == "/quit":
        # ... existing quit logic ...
        return True

    return False
```

**New Commands to Add**:

```python
def handle_command(user_input: str, session: ConversationSession) -> bool:
    """Handle special commands. Returns True if command was handled."""

    # ... existing commands ...

    # ===== NEW: Debug Mode Commands =====
    elif user_input == "/debug on":
        session.debug_mode = True
        print("🐛 Debug mode enabled - verbose error output with full tracebacks")
        print("   Errors will show detailed stack traces and debug hints")
        return True

    elif user_input == "/debug off":
        session.debug_mode = False
        print("✓ Debug mode disabled - concise error messages")
        return True

    # ===== NEW: Verbose Mode Commands =====
    elif user_input == "/verbose on":
        session.verbose_mode = True
        print("📢 Verbose mode enabled - showing internal state messages")
        print("   You will see [HYBRID], [DATA TOOL], and [VIS TOOL] messages")
        return True

    elif user_input == "/verbose off":
        session.verbose_mode = False
        print("🔇 Verbose mode disabled - clean conversation output")
        return True

    # ===== NEW: Error History Commands =====
    elif user_input == "/errors":
        if not session.error_history:
            print("No errors recorded in this session.")
        else:
            print(f"\n📋 Error History ({len(session.error_history)} errors):\n")
            for err in session.error_history:
                print(err.summary())
            print("\n💡 Use '/trace <id>' or '/trace last' to see full details")
        return True

    # ===== NEW: Trace Commands =====
    elif user_input.startswith("/trace"):
        parts = user_input.split()
        if len(parts) == 1:
            print("Usage: /trace <error_id> or /trace last")
            print("\nExamples:")
            print("  /trace 3      - Show full trace for error ID 3")
            print("  /trace last   - Show trace for most recent error")
            return True

        elif parts[1] == "last":
            err = session.get_last_error()
            if err:
                print("\n" + "="*70)
                print(err.detailed())
                print("="*70)
            else:
                print("No errors recorded yet.")
            return True

        else:
            try:
                error_id = int(parts[1])
                err = session.get_error(error_id)
                if err:
                    print("\n" + "="*70)
                    print(err.detailed())
                    print("="*70)
                else:
                    print(f"Error ID {error_id} not found.")
                    print(f"\nAvailable error IDs: {[e.error_id for e in session.error_history]}")
            except ValueError:
                print(f"Invalid error ID: '{parts[1]}'. Must be a number or 'last'.")
            return True

    return False
```

### 3.2 Update Help Command

**File**: `src/chatuvisbox/main.py`

**Update the `/help` command output**:

```python
def show_help():
    """Display help text with all commands."""
    help_text = """
ChatUVisBox - Natural Language Interface for UVisBox

BASIC COMMANDS:
  /help          - Show this help message
  /context       - Display current conversation context (data, vis params)
  /stats         - Show session statistics
  /clear         - Clear temporary files and reset state
  /reset         - Reset conversation only (preserve files)
  /quit          - Exit the application

DEBUG & VERBOSE COMMANDS:
  /debug on      - Enable verbose error output with full stack traces
  /debug off     - Disable verbose error output (default)
  /verbose on    - Show internal state messages ([HYBRID], [TOOL], etc.)
  /verbose off   - Hide internal state messages (default)

ERROR TRACKING COMMANDS:
  /errors        - List recent errors with IDs
  /trace <id>    - Show full stack trace for specific error ID
  /trace last    - Show stack trace for most recent error

USAGE TIPS:
  - Both debug and verbose modes are OFF by default for clean conversation
  - Enable debug mode when investigating errors to see full tracebacks
  - Enable verbose mode to see execution flow and internal operations
  - Both modes can be enabled independently or together

EXAMPLES:
  # Normal conversation (default)
  You: generate 30 curves
  You: plot functional boxplot

  # Debug an error
  You: /debug on
  You: plot with colormap Reds
  You: /trace last

  # See execution flow
  You: /verbose on
  You: colormap plasma

  # View error history
  You: /errors
  You: /trace 3

For more information, see docs/USER_GUIDE.md
"""
    print(help_text)
```

**Notes on Help Text**:
- Grouped commands by category
- Clear descriptions with defaults
- Usage tips explaining when to use each mode
- Examples showing common workflows

### 3.3 Add Status Indicator to Prompt (Optional Enhancement)

**Current Prompt**:
```python
You: _
```

**Enhanced Prompt with Mode Indicators**:
```python
def get_prompt(session: ConversationSession) -> str:
    """Get input prompt with mode indicators."""
    indicators = []
    if session.debug_mode:
        indicators.append("🐛")
    if session.verbose_mode:
        indicators.append("📢")

    if indicators:
        prefix = "".join(indicators) + " "
    else:
        prefix = ""

    return f"{prefix}You: "
```

**Usage in REPL**:
```python
while True:
    user_input = input(get_prompt(session))
    # ... rest of REPL ...
```

**Example Output**:
```
You: /debug on
🐛 Debug mode enabled

🐛 You: /verbose on
📢 Verbose mode enabled

🐛📢 You: generate curves
[DATA TOOL] Calling generate_curves...
```

**Benefits**:
- Visual reminder of active modes
- Clear indication when debugging
- No additional complexity

### 3.4 Add Mode Status to /context Command

**File**: `src/chatuvisbox/main.py`

**Enhance `/context` output to show mode states**:

```python
elif user_input == "/context":
    context = session.get_context_summary()

    print("\n📊 Current Context:")
    print(f"  Turn count: {context['turn_count']}")
    print(f"  Message count: {context['message_count']}")

    # NEW: Show mode states
    print(f"\n⚙️  Mode Settings:")
    print(f"  Debug mode: {'🐛 ON' if session.debug_mode else '✓ OFF'}")
    print(f"  Verbose mode: {'📢 ON' if session.verbose_mode else '🔇 OFF'}")

    # Existing context info
    if context['current_data']:
        print(f"\n📁 Current Data:")
        print(f"  {context['current_data']}")

    if context['last_vis']:
        print(f"\n📊 Last Visualization:")
        print(f"  Tool: {context['last_vis'].get('_tool_name', 'unknown')}")
        for k, v in context['last_vis'].items():
            if k != '_tool_name':
                print(f"  {k}: {v}")

    if context['session_files']:
        print(f"\n📦 Session Files ({len(context['session_files'])}):")
        for f in context['session_files'][-5:]:  # Show last 5
            print(f"  - {f}")

    print(f"\n❌ Error count: {context['error_count']}")

    # NEW: Show error history summary
    if session.error_history:
        print(f"\n🐛 Error History ({len(session.error_history)} errors):")
        print(f"   Use '/errors' to see list or '/trace last' for details")

    print()
    return True
```

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_command_handlers.py` (new)

```python
def test_debug_on_command():
    """Test /debug on command."""
    session = ConversationSession()
    assert session.debug_mode is False

    result = handle_command("/debug on", session)

    assert result is True
    assert session.debug_mode is True

def test_debug_off_command():
    """Test /debug off command."""
    session = ConversationSession()
    session.debug_mode = True

    result = handle_command("/debug off", session)

    assert result is True
    assert session.debug_mode is False

def test_verbose_on_command():
    """Test /verbose on command."""
    session = ConversationSession()
    assert session.verbose_mode is False

    result = handle_command("/verbose on", session)

    assert result is True
    assert session.verbose_mode is True

def test_errors_command_empty(capsys):
    """Test /errors with no error history."""
    session = ConversationSession()

    handle_command("/errors", session)

    captured = capsys.readouterr()
    assert "No errors recorded" in captured.out

def test_errors_command_with_history(capsys):
    """Test /errors with error history."""
    session = ConversationSession()
    # Add mock error
    session.record_error(
        tool_name="test_tool",
        error=ValueError("test error"),
        traceback_str="traceback...",
        user_message="Test error message"
    )

    handle_command("/errors", session)

    captured = capsys.readouterr()
    assert "Error History" in captured.out
    assert "[1]" in captured.out

def test_trace_last_command():
    """Test /trace last command."""
    session = ConversationSession()
    # Add mock error
    session.record_error(
        tool_name="test_tool",
        error=ValueError("test error"),
        traceback_str="full traceback...",
        user_message="Test error"
    )

    handle_command("/trace last", session)
    # Verify output contains traceback (use capsys)

def test_trace_by_id_command():
    """Test /trace <id> command."""
    session = ConversationSession()
    # Add mock error
    session.record_error(
        tool_name="test_tool",
        error=ValueError("test error"),
        traceback_str="full traceback...",
        user_message="Test error"
    )

    handle_command("/trace 1", session)
    # Verify output contains traceback

def test_trace_invalid_id():
    """Test /trace with invalid ID."""
    session = ConversationSession()

    handle_command("/trace 999", session)
    # Verify "not found" message
```

### Integration Tests

**File**: `tests/integration/test_command_workflow.py` (new)

```python
def test_debug_workflow():
    """Test complete debug workflow."""
    session = ConversationSession()

    # Enable debug mode
    handle_command("/debug on", session)
    assert session.debug_mode is True

    # Trigger an error (mock)
    # ... trigger error ...

    # Check error history
    handle_command("/errors", session)

    # View trace
    handle_command("/trace last", session)

    # Disable debug mode
    handle_command("/debug off", session)
    assert session.debug_mode is False

def test_verbose_workflow():
    """Test verbose mode toggling."""
    session = ConversationSession()

    # Enable verbose
    handle_command("/verbose on", session)
    assert session.verbose_mode is True

    # Execute command (should show internal messages)
    # ... test with vprint calls ...

    # Disable verbose
    handle_command("/verbose off", session)
    assert session.verbose_mode is False

def test_independent_modes():
    """Test that debug and verbose modes are independent."""
    session = ConversationSession()

    # Enable only debug
    handle_command("/debug on", session)
    assert session.debug_mode is True
    assert session.verbose_mode is False

    # Enable verbose too
    handle_command("/verbose on", session)
    assert session.debug_mode is True
    assert session.verbose_mode is True

    # Disable debug, keep verbose
    handle_command("/debug off", session)
    assert session.debug_mode is False
    assert session.verbose_mode is True
```

### Manual Testing Checklist

**Test 1: Help Command**
- [ ] Run `/help`
- [ ] Verify all new commands are documented
- [ ] Verify examples are clear

**Test 2: Debug Mode**
- [ ] Run `/debug on` - verify confirmation message
- [ ] Trigger an error - verify full traceback shown
- [ ] Run `/debug off` - verify confirmation
- [ ] Trigger same error - verify concise message

**Test 3: Verbose Mode**
- [ ] Run `/verbose on` - verify confirmation
- [ ] Execute command - verify [HYBRID]/[TOOL] messages shown
- [ ] Run `/verbose off` - verify confirmation
- [ ] Execute command - verify clean output

**Test 4: Error Tracking**
- [ ] Trigger 3 different errors
- [ ] Run `/errors` - verify 3 errors listed with IDs
- [ ] Run `/trace 2` - verify specific error shown
- [ ] Run `/trace last` - verify last error shown
- [ ] Run `/trace 999` - verify "not found" message

**Test 5: Context Command**
- [ ] Run `/context` - verify mode states shown
- [ ] Enable debug mode - run `/context` - verify 🐛 ON
- [ ] Enable verbose mode - run `/context` - verify 📢 ON

**Test 6: Combined Modes**
- [ ] Enable both modes
- [ ] Execute command with error
- [ ] Verify full traceback + internal messages both shown

## Acceptance Criteria

- ✅ `/debug on/off` commands work correctly
- ✅ `/verbose on/off` commands work correctly
- ✅ `/errors` command lists error history
- ✅ `/trace <id>` shows specific error trace
- ✅ `/trace last` shows most recent error
- ✅ `/help` updated with all new commands
- ✅ `/context` shows mode states
- ✅ Mode indicators optional enhancement (nice to have)
- ✅ All commands have confirmation messages
- ✅ Error messages for invalid input
- ✅ Unit tests pass
- ✅ Integration tests pass
- ✅ Manual testing complete

## User Experience Examples

### Example 1: Debugging an Error
```
You: plot with colormap Reds
Assistant: Error: I can't use "Reds" as a colormap

You: /trace last
======================================================================
Error ID: 1
Timestamp: 2025-01-30T10:23:45
Tool: plot_functional_boxplot
Type: ValueError
Message: Invalid colormap name 'Reds'
...
[full traceback]
======================================================================

You: /debug on
🐛 Debug mode enabled - verbose error output with full tracebacks

You: plot with colormap Reds
[full traceback shown inline]
```

### Example 2: Watching Execution Flow
```
You: /verbose on
📢 Verbose mode enabled - showing internal state messages

You: generate 30 curves
[DATA TOOL] Calling generate_curves with args: {'n_curves': 30}
[DATA TOOL] Result: {'status': 'success', ...}
Assistant: Generated 30 curves

You: colormap plasma
[HYBRID] Executing plot_functional_boxplot with updated params
Assistant: Updated functional boxplot
```

## Next Phase

After completing Phase 3, proceed to:
- **Phase 4: Enhanced Error Messages** - Add UVisBox error interpretation
