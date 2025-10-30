# Phase 2: Verbose Mode Control

**Priority**: HIGH
**Timeline**: Week 1 (Days 4-5)
**Dependencies**: Phase 1 (ConversationSession with verbose_mode flag)

## Overview

Implement verbose mode to control visibility of internal state messages:
- Create output control utility with vprint function
- Update all internal print statements to use vprint
- Ensure clean conversation by default (verbose OFF)
- Enable debugging visibility on demand (verbose ON)

## Problem

Current code has debug print statements scattered throughout:
```python
print(f"[HYBRID] Executing {vis_tool_name} with updated params")
print(f"[DATA TOOL] Calling {tool_name} with args: {tool_args}")
print(f"[VIS TOOL] Result: {result}")
```

These messages are helpful for debugging but clutter normal conversation.

## Solution

Centralized output control that checks session.verbose_mode before printing.

## Deliverables

### 2.1 Create Output Control Utility

**File**: `src/chatuvisbox/output_control.py` (new)

**Implementation**:

```python
"""Control verbose output based on session settings."""

from typing import Optional

# Global session reference for accessing verbose_mode
# Set by conversation.py when session is created
_current_session: Optional['ConversationSession'] = None

def set_session(session) -> None:
    """
    Set the current session for verbose mode checks.

    Args:
        session: ConversationSession instance
    """
    global _current_session
    _current_session = session

def vprint(message: str, force: bool = False) -> None:
    """
    Print message only if verbose mode is enabled.

    Args:
        message: Message to print
        force: If True, always print regardless of verbose mode

    Example:
        vprint("[DATA TOOL] Calling generate_curves")  # Only if verbose
        vprint("✅ Success!", force=True)  # Always print
    """
    global _current_session
    if force or (_current_session and _current_session.verbose_mode):
        print(message)

def is_verbose() -> bool:
    """
    Check if verbose mode is enabled.

    Returns:
        True if verbose mode is on, False otherwise
    """
    global _current_session
    return _current_session and _current_session.verbose_mode
```

**Design Notes**:
- Uses global session reference (simple, no state changes needed)
- `force=True` parameter for user-facing messages that should always show
- `is_verbose()` helper for conditional logic
- Type hints for clarity

**Tests Required**:
- vprint() with verbose OFF (no output)
- vprint() with verbose ON (output shown)
- vprint() with force=True (always output)
- is_verbose() returns correct value
- set_session() updates global reference

### 2.2 Update ConversationSession to Register

**File**: `src/chatuvisbox/conversation.py`

**Changes**:

```python
from chatuvisbox.output_control import set_session

class ConversationSession:
    def __init__(self):
        # ... existing fields ...
        self.debug_mode: bool = False
        self.verbose_mode: bool = False  # Already added in Phase 1
        # ... rest of initialization ...

        # Register this session for verbose mode checks
        set_session(self)
```

**Key Point**: Call `set_session(self)` at end of `__init__` to register.

### 2.3 Update nodes.py

**File**: `src/chatuvisbox/nodes.py`

**Changes**:

```python
from chatuvisbox.output_control import vprint

def call_data_tool(state: GraphState) -> GraphState:
    """Execute data tool with optional verbose output."""
    # ... existing code ...

    # BEFORE:
    # print(f"[DATA TOOL] Calling {tool_name} with args: {tool_args}")

    # AFTER:
    vprint(f"[DATA TOOL] Calling {tool_name} with args: {tool_args}")

    # Execute tool
    result = fn(**tool_input)

    # BEFORE:
    # print(f"[DATA TOOL] Result: {result}")

    # AFTER:
    vprint(f"[DATA TOOL] Result: {result}")

    # ... error handling ...

    # BEFORE:
    # print(f"[DATA TOOL] Exception: {e}")

    # AFTER:
    vprint(f"[DATA TOOL] Exception: {e}")

    # ... rest of code ...

def call_vis_tool(state: GraphState) -> GraphState:
    """Execute visualization tool with optional verbose output."""
    # ... existing code ...

    vprint(f"[VIS TOOL] Calling {tool_name} with args: {tool_args}")

    # Execute tool
    result = fn(**tool_input)

    vprint(f"[VIS TOOL] Result: {result}")

    # ... error handling ...

    vprint(f"[VIS TOOL] Exception: {e}")

    # ... rest of code ...
```

**Messages to Update**:
- ✅ `[DATA TOOL] Calling ...`
- ✅ `[DATA TOOL] Result: ...`
- ✅ `[DATA TOOL] Exception: ...`
- ✅ `[VIS TOOL] Calling ...`
- ✅ `[VIS TOOL] Result: ...`
- ✅ `[VIS TOOL] Exception: ...`

### 2.4 Update hybrid_control.py

**File**: `src/chatuvisbox/hybrid_control.py`

**Changes**:

```python
from chatuvisbox.output_control import vprint

def execute_hybrid_command(command: str, state: GraphState) -> Optional[Dict]:
    """Execute hybrid command with optional verbose output."""
    # ... existing code ...

    # BEFORE:
    # print(f"[HYBRID] Executing {vis_tool_name} with updated params")

    # AFTER:
    vprint(f"[HYBRID] Executing {vis_tool_name} with updated params")

    # ... rest of code ...
```

**Messages to Update**:
- ✅ `[HYBRID] Executing ...`

### 2.5 Update conversation.py

**File**: `src/chatuvisbox/conversation.py`

**Changes**:

```python
from chatuvisbox.output_control import vprint, set_session

class ConversationSession:
    def send(self, user_message: str) -> GraphState:
        # ... existing code ...

        # When hybrid control succeeds:
        # BEFORE:
        # print(f"[HYBRID] Fast path executed: {message}")

        # AFTER:
        vprint(f"[HYBRID] Fast path executed: {message}")

        # ... rest of code ...

    def clear_session(self):
        # ... existing code ...

        # User-facing messages should always show (keep as regular print)
        print(f"🧹 {result['message']}")  # NO vprint - user should see this
```

**Important Distinction**:
- **Internal messages** → Use `vprint()` (hidden by default)
- **User-facing messages** → Use `print()` (always shown)

**Messages to Update**:
- ✅ `[HYBRID] Fast path executed: ...` → vprint
- ❌ `🧹 Cleared session: ...` → keep as print (user-facing)

### 2.6 Update All Print Statements

**Audit Command**:
```bash
grep -rn "print(f.*\[" src/chatuvisbox/
```

**Expected Output** (after updates):
```
# Should find NO matches (all internal prints converted to vprint)
```

**Verification**:
```bash
grep -rn "vprint" src/chatuvisbox/
```

**Expected Matches**:
- `output_control.py` - Definition
- `nodes.py` - Import and usage (6+ times)
- `hybrid_control.py` - Import and usage (1+ times)
- `conversation.py` - Import and usage (1+ times)

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_output_control.py` (new)

```python
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

def test_vprint_force(capsys):
    """vprint with force=True should always output."""
    session = ConversationSession()
    session.verbose_mode = False
    set_session(session)

    vprint("Forced message", force=True)

    captured = capsys.readouterr()
    assert "Forced message" in captured.out

def test_is_verbose():
    """is_verbose should return correct state."""
    session = ConversationSession()

    session.verbose_mode = False
    set_session(session)
    assert is_verbose() is False

    session.verbose_mode = True
    assert is_verbose() is True
```

### Integration Tests

**File**: `tests/integration/test_verbose_mode_integration.py` (new)

```python
def test_hybrid_command_verbose_off(capsys):
    """Hybrid commands should not print when verbose is OFF."""
    session = ConversationSession()
    session.verbose_mode = False

    # Execute hybrid command
    session.send("colormap plasma")

    captured = capsys.readouterr()
    # Should NOT contain [HYBRID] messages
    assert "[HYBRID]" not in captured.out

def test_hybrid_command_verbose_on(capsys):
    """Hybrid commands should print when verbose is ON."""
    session = ConversationSession()
    session.verbose_mode = True

    # Execute hybrid command
    session.send("colormap plasma")

    captured = capsys.readouterr()
    # SHOULD contain [HYBRID] messages
    assert "[HYBRID]" in captured.out
```

### Manual Testing

**Test Scenario 1: Default (Verbose OFF)**
```
$ python main.py
You: generate 30 curves
Assistant: Generated 30 curves and saved to temp/_temp_ensemble_curves.npy

You: plot functional boxplot
Assistant: Displayed functional boxplot for 30 curves
```
**Expected**: No [HYBRID], [DATA TOOL], or [VIS TOOL] messages.

**Test Scenario 2: Verbose ON**
```
You: /verbose on
Assistant: 📢 Verbose mode enabled - showing internal state messages

You: generate 30 curves
[DATA TOOL] Calling generate_curves with args: {'n_curves': 30}
[DATA TOOL] Result: {'status': 'success', ...}
Assistant: Generated 30 curves and saved to temp/_temp_ensemble_curves.npy

You: colormap plasma
[HYBRID] Executing plot_functional_boxplot with updated params
[HYBRID] Fast path executed: Updated functional boxplot with colormap plasma
Assistant: Updated functional boxplot with colormap plasma
```
**Expected**: All internal messages visible.

## Acceptance Criteria

- ✅ output_control.py created with vprint, set_session, is_verbose
- ✅ ConversationSession calls set_session(self) in __init__
- ✅ All internal print statements converted to vprint
- ✅ User-facing messages still use regular print
- ✅ Verbose OFF by default (clean conversation)
- ✅ Verbose ON shows all internal messages
- ✅ Unit tests pass for output_control
- ✅ Integration tests verify verbose mode behavior
- ✅ Manual testing confirms clean output

## Migration Checklist

**Before starting**:
- [ ] Verify Phase 1 complete (verbose_mode flag exists)
- [ ] Backup current code

**Implementation order**:
1. [ ] Create output_control.py
2. [ ] Add set_session() call to ConversationSession.__init__
3. [ ] Update nodes.py (replace all prints with vprint)
4. [ ] Update hybrid_control.py (replace prints with vprint)
5. [ ] Update conversation.py (replace internal prints with vprint)
6. [ ] Verify no internal prints remain (grep check)
7. [ ] Write unit tests
8. [ ] Write integration tests
9. [ ] Manual testing

**Verification**:
```bash
# Should find no matches:
grep -rn "print(f.*\[DATA" src/chatuvisbox/
grep -rn "print(f.*\[VIS" src/chatuvisbox/
grep -rn "print(f.*\[HYBRID" src/chatuvisbox/

# Should find matches:
grep -rn "vprint" src/chatuvisbox/
```

## Performance Impact

**Overhead**: Minimal (~1-2%)
- Single function call per message
- Single boolean check
- No I/O when verbose is OFF

**Memory**: Negligible
- One global reference
- No additional data structures

## Next Phase

After completing Phase 2, proceed to:
- **Phase 3: User Commands** - Add /verbose on/off command handlers
