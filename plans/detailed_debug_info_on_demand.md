# Plan: Detailed Debug Information On Demand

## Problem Statement

Currently, error messages in ChatUVisBox are too vague for debugging:
- Example: "I can't use 'Reds' as a colormap" when Reds IS a valid matplotlib colormap
- No access to full stack traces
- Auto-fixed errors are invisible - can't inspect what went wrong
- Difficult to debug UVisBox integration issues

Additionally, internal state messages clutter the conversation:
- Example: "[HYBRID] Executing plot_functional_boxplot with updated params"
- Example: "[DATA TOOL] Calling generate_curves with args: ..."
- Example: "[VIS TOOL] Result: {'status': 'success', ...}"
- These messages are helpful for debugging but noisy for normal use

## Goals

1. Provide detailed stack traces on demand without cluttering normal conversation
2. Capture and store all errors (including auto-fixed ones) for inspection
3. Add user-facing commands to access debug information
4. **Add verbose mode to hide/show internal state messages**
5. Maintain backward compatibility with existing error handling
6. **Clean conversation experience by default (verbose OFF)**

## Design Overview

### Mode Comparison

| Feature | Default (OFF) | Debug Mode (`/debug on`) | Verbose Mode (`/verbose on`) |
|---------|---------------|-------------------------|------------------------------|
| Error messages | Concise, user-friendly | Full traceback inline | Concise, user-friendly |
| Error history | ✅ Recorded | ✅ Recorded | ✅ Recorded |
| Internal messages | ❌ Hidden | ❌ Hidden | ✅ Shown |
| `[HYBRID]` messages | ❌ Hidden | ❌ Hidden | ✅ Shown |
| `[DATA TOOL]` messages | ❌ Hidden | ❌ Hidden | ✅ Shown |
| `[VIS TOOL]` messages | ❌ Hidden | ❌ Hidden | ✅ Shown |
| Error interpretation | ✅ Basic | ✅ Enhanced with hints | ✅ Basic |
| Use case | Normal conversation | Error investigation | Execution flow debugging |

**Key Insight**: Debug and verbose modes are **independent** and can be combined:
- **Debug OFF + Verbose OFF** (default): Clean conversation
- **Debug ON + Verbose OFF**: See detailed errors, hide execution flow
- **Debug OFF + Verbose ON**: See execution flow, concise errors
- **Debug ON + Verbose ON**: Full visibility (maximum debugging)

### Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                    User Commands                             │
│  /debug on|off     - Toggle verbose error output            │
│  /verbose on|off   - Toggle internal state messages         │
│  /errors           - Show recent error summary               │
│  /trace [N]        - Show full stack trace for error N      │
│  /trace last       - Show last error stack trace             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              ConversationSession (Enhanced)                  │
│  - debug_mode: bool        (default: False)                  │
│  - verbose_mode: bool      (default: False)                  │
│  - error_history: List[ErrorRecord]                          │
│  - max_error_history: int = 20                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  ErrorRecord (New Class)                     │
│  - timestamp: datetime                                       │
│  - error_id: int                                             │
│  - tool_name: str                                            │
│  - error_type: str                                           │
│  - error_message: str                                        │
│  - full_traceback: str                                       │
│  - user_facing_message: str                                  │
│  - auto_fixed: bool                                          │
│  - context: Dict (state snapshot)                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Enhanced Error Handling in Tools                │
│  - Capture full traceback with traceback.format_exc()       │
│  - Create ErrorRecord for each exception                     │
│  - Return both user message + error record                   │
│  - Log to error_history in ConversationSession              │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Core Infrastructure (Priority: HIGH)

#### 1.1 Create ErrorRecord Class
**File**: `src/chatuvisbox/error_tracking.py` (new)

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

@dataclass
class ErrorRecord:
    """Record of an error that occurred during execution."""
    error_id: int
    timestamp: datetime
    tool_name: str
    error_type: str
    error_message: str
    full_traceback: str
    user_facing_message: str
    auto_fixed: bool
    context: Optional[Dict] = None

    def summary(self) -> str:
        """Brief one-line summary."""
        status = "auto-fixed" if self.auto_fixed else "failed"
        return f"[{self.error_id}] {self.timestamp.strftime('%H:%M:%S')} - {self.tool_name}: {self.error_type} ({status})"

    def detailed(self) -> str:
        """Detailed multi-line description."""
        lines = [
            f"Error ID: {self.error_id}",
            f"Timestamp: {self.timestamp.isoformat()}",
            f"Tool: {self.tool_name}",
            f"Type: {self.error_type}",
            f"Message: {self.error_message}",
            f"Auto-fixed: {self.auto_fixed}",
            f"User-facing message: {self.user_facing_message}",
            "",
            "Full Traceback:",
            self.full_traceback
        ]
        if self.context:
            lines.extend(["", "Context:", str(self.context)])
        return "\n".join(lines)
```

#### 1.2 Add Error History and Mode Flags to ConversationSession
**File**: `src/chatuvisbox/conversation.py`

**Changes**:
```python
class ConversationSession:
    def __init__(self):
        # ... existing fields ...
        self.debug_mode: bool = False      # Verbose error output with tracebacks
        self.verbose_mode: bool = False    # Show internal state messages
        self.error_history: List[ErrorRecord] = []
        self.max_error_history: int = 20
        self._next_error_id: int = 1

    def record_error(
        self,
        tool_name: str,
        error: Exception,
        traceback_str: str,
        user_message: str,
        auto_fixed: bool = False,
        context: Optional[Dict] = None
    ) -> ErrorRecord:
        """Record an error in history."""
        record = ErrorRecord(
            error_id=self._next_error_id,
            timestamp=datetime.now(),
            tool_name=tool_name,
            error_type=type(error).__name__,
            error_message=str(error),
            full_traceback=traceback_str,
            user_facing_message=user_message,
            auto_fixed=auto_fixed,
            context=context
        )

        self.error_history.append(record)
        self._next_error_id += 1

        # Keep only last N errors
        if len(self.error_history) > self.max_error_history:
            self.error_history.pop(0)

        # Log to file
        logger.log_error_record(record)

        return record

    def get_error(self, error_id: int) -> Optional[ErrorRecord]:
        """Get error by ID."""
        for err in self.error_history:
            if err.error_id == error_id:
                return err
        return None

    def get_last_error(self) -> Optional[ErrorRecord]:
        """Get most recent error."""
        return self.error_history[-1] if self.error_history else None
```

#### 1.3 Update Tool Error Handling Pattern
**File**: `src/chatuvisbox/vis_tools.py` (and all tool files)

**Pattern** (example for `plot_functional_boxplot`):
```python
import traceback
from chatuvisbox.error_tracking import ErrorRecord

def plot_functional_boxplot(...) -> Dict[str, str]:
    try:
        # ... existing code ...

    except Exception as e:
        # Capture full traceback
        tb_str = traceback.format_exc()

        # Create user-friendly message
        user_msg = f"Error creating functional boxplot: {str(e)}"

        # Return error info (will be recorded by node)
        return {
            "status": "error",
            "message": user_msg,
            "_error_details": {
                "exception": e,
                "traceback": tb_str
            }
        }
```

#### 1.4 Update Tool Nodes to Record Errors
**File**: `src/chatuvisbox/nodes.py`

**Changes** to `call_data_tool` and `call_vis_tool`:
```python
def call_data_tool(state: GraphState) -> GraphState:
    # ... existing code ...

    result = fn(**tool_input)

    # Check for error details
    if result.get("status") == "error" and "_error_details" in result:
        # Record error in session (if available)
        # Note: Need to pass session reference or use global/context
        if hasattr(state, "_session"):
            error_details = result["_error_details"]
            state["_session"].record_error(
                tool_name=tool_call.name,
                error=error_details["exception"],
                traceback_str=error_details["traceback"],
                user_message=result["message"],
                auto_fixed=False
            )

    # ... rest of existing code ...
```

### Phase 1.5: Verbose Mode Control (Priority: HIGH)

#### 1.5.1 Create Output Control Utility
**File**: `src/chatuvisbox/output_control.py` (new)

```python
"""Control verbose output based on session settings."""

# Global session reference for accessing verbose_mode
# Set by conversation.py when session is created
_current_session = None

def set_session(session):
    """Set the current session for verbose mode checks."""
    global _current_session
    _current_session = session

def vprint(message: str, force: bool = False):
    """
    Print message only if verbose mode is enabled.

    Args:
        message: Message to print
        force: If True, always print regardless of verbose mode
    """
    global _current_session
    if force or (_current_session and _current_session.verbose_mode):
        print(message)

def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    global _current_session
    return _current_session and _current_session.verbose_mode
```

#### 1.5.2 Update Print Statements for Verbose Control
**Files**: `nodes.py`, `hybrid_control.py`, `conversation.py`

**In `src/chatuvisbox/nodes.py`**:
```python
from chatuvisbox.output_control import vprint

def call_data_tool(state: GraphState) -> GraphState:
    # ... existing code ...

    vprint(f"[DATA TOOL] Calling {tool_name} with args: {tool_args}")

    # ... execute tool ...

    vprint(f"[DATA TOOL] Result: {result}")

    # On error:
    vprint(f"[DATA TOOL] Exception: {e}")

    # ... rest of code ...

def call_vis_tool(state: GraphState) -> GraphState:
    # ... existing code ...

    vprint(f"[VIS TOOL] Calling {tool_name} with args: {tool_args}")

    # ... execute tool ...

    vprint(f"[VIS TOOL] Result: {result}")

    # On error:
    vprint(f"[VIS TOOL] Exception: {e}")

    # ... rest of code ...
```

**In `src/chatuvisbox/hybrid_control.py`**:
```python
from chatuvisbox.output_control import vprint

def execute_hybrid_command(command: str, state: GraphState) -> Optional[Dict]:
    # ... existing code ...

    vprint(f"[HYBRID] Executing {vis_tool_name} with updated params")

    # ... rest of code ...
```

**In `src/chatuvisbox/conversation.py`**:
```python
from chatuvisbox.output_control import vprint, set_session

class ConversationSession:
    def __init__(self):
        # ... existing fields ...
        set_session(self)  # Register for verbose mode checks

    def send(self, user_message: str) -> GraphState:
        # ... existing code ...

        # When hybrid control succeeds:
        vprint(f"[HYBRID] Fast path executed: {message}")

        # ... rest of code ...

    def clear_session(self):
        # ... existing code ...

        # The cleanup message should always show (user-facing)
        print(f"🧹 {result['message']}")  # Keep as regular print
```

### Phase 2: User Commands (Priority: HIGH)

#### 2.1 Add Debug and Verbose Commands to main.py
**File**: `src/chatuvisbox/main.py`

**New commands**:
```python
def handle_command(user_input: str, session: ConversationSession) -> bool:
    """Handle special commands. Returns True if command was handled."""

    # ... existing commands ...

    elif user_input == "/debug on":
        session.debug_mode = True
        print("🐛 Debug mode enabled - verbose error output with tracebacks")
        return True

    elif user_input == "/debug off":
        session.debug_mode = False
        print("✓ Debug mode disabled - concise error messages")
        return True

    elif user_input == "/verbose on":
        session.verbose_mode = True
        print("📢 Verbose mode enabled - showing internal state messages")
        return True

    elif user_input == "/verbose off":
        session.verbose_mode = False
        print("🔇 Verbose mode disabled - clean conversation output")
        return True

    elif user_input == "/errors":
        if not session.error_history:
            print("No errors recorded in this session.")
        else:
            print(f"\n📋 Error History ({len(session.error_history)} errors):\n")
            for err in session.error_history:
                print(err.summary())
            print("\nUse '/trace <id>' or '/trace last' to see full details")
        return True

    elif user_input.startswith("/trace"):
        parts = user_input.split()
        if len(parts) == 1:
            print("Usage: /trace <error_id> or /trace last")
        elif parts[1] == "last":
            err = session.get_last_error()
            if err:
                print("\n" + "="*70)
                print(err.detailed())
                print("="*70)
            else:
                print("No errors recorded yet.")
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
            except ValueError:
                print(f"Invalid error ID: {parts[1]}")
        return True

    return False
```

#### 2.2 Update Help Command
**File**: `src/chatuvisbox/main.py`

Add to help output:
```
Debug & Verbose Commands:
  /debug on      - Enable verbose error output with full tracebacks
  /debug off     - Disable verbose error output (default)
  /verbose on    - Show internal state messages ([HYBRID], [TOOL], etc.)
  /verbose off   - Hide internal state messages (default)
  /errors        - List recent errors with IDs
  /trace <id>    - Show full stack trace for specific error
  /trace last    - Show last error stack trace
```

**Note**: Internal messages affected by `/verbose` mode:
- `[DATA TOOL]` - Data tool execution messages
- `[VIS TOOL]` - Visualization tool execution messages
- `[HYBRID]` - Hybrid fast path execution messages

### Phase 3: Enhanced Error Messages (Priority: MEDIUM)

#### 3.1 Improve UVisBox Error Interpretation
**File**: `src/chatuvisbox/error_interpretation.py` (new)

```python
import re
from typing import Tuple

def interpret_uvisbox_error(error: Exception, traceback_str: str) -> Tuple[str, str]:
    """
    Interpret UVisBox errors and provide helpful context.

    Returns:
        (user_message, debug_hint)
    """
    error_msg = str(error)

    # Colormap errors
    if "colormap" in error_msg.lower():
        # Extract actual error from UVisBox
        if "matplotlib" in traceback_str:
            return (
                f"Colormap error: {error_msg}",
                "This may be a UVisBox bug. Check if UVisBox is using the colormap correctly."
            )

    # Method validation errors
    if "unknown method" in error_msg.lower():
        return (
            f"Method validation error: {error_msg}",
            "Check if UVisBox validation matches its documentation."
        )

    # Shape errors
    if "shape" in error_msg.lower():
        match = re.search(r"shape \((\d+(?:, \d+)*)\)", error_msg)
        if match:
            return (
                f"Data shape mismatch: {error_msg}",
                f"Data has shape {match.group(1)}. Check expected dimensions."
            )

    # Default
    return (error_msg, "")
```

Use in tools:
```python
except Exception as e:
    tb_str = traceback.format_exc()
    user_msg, debug_hint = interpret_uvisbox_error(e, tb_str)

    if debug_hint and session.debug_mode:
        user_msg += f"\n💡 Debug hint: {debug_hint}"

    return {
        "status": "error",
        "message": user_msg,
        "_error_details": {"exception": e, "traceback": tb_str}
    }
```

### Phase 4: Auto-Fix Detection (Priority: LOW)

#### 4.1 Track Retry Attempts
**File**: `src/chatuvisbox/nodes.py`

When the graph loops back to model after an error, mark the previous error as "auto-fix attempted".

If the next tool execution succeeds, mark the previous error as "auto-fixed: true".

This requires:
1. Tracking tool execution sequences
2. Detecting when an error is followed by successful execution
3. Updating error records retroactively

### Phase 5: Testing (Priority: HIGH)

#### 5.1 Unit Tests
**File**: `tests/unit/test_error_tracking.py` (new)

Test:
- ErrorRecord creation and formatting
- ConversationSession.record_error()
- Error history limits
- Error retrieval by ID

#### 5.2 Integration Tests
**File**: `tests/integration/test_debug_commands.py` (new)

Test:
- `/debug on/off` toggle
- `/verbose on/off` toggle
- `/errors` command output
- `/trace` command with various IDs
- Error recording during tool execution
- Verbose mode suppressing/showing internal messages
- Independent operation of debug and verbose modes

#### 5.3 Manual Testing Scenarios

1. **Invalid colormap**: Test "Reds" error and inspect full trace
2. **Method error**: Test 'fbd' vs 'fdb' issue with full trace
3. **Shape mismatch**: Test wrong data shape and inspect trace
4. **Auto-fix**: Trigger error, then successful retry, check error history

## Implementation Order

### Week 1: Core Infrastructure
1. ✅ Create `error_tracking.py` with ErrorRecord class
2. ✅ Add error_history and mode flags to ConversationSession
3. ✅ Update tool error handling pattern in vis_tools.py
4. ✅ Update nodes.py to record errors
5. ✅ Create `output_control.py` with vprint utility
6. ✅ Update all print statements to use vprint for verbose control

### Week 2: User Interface
7. ✅ Add `/debug`, `/verbose`, `/errors`, `/trace` commands to main.py
8. ✅ Update help text with all new commands
9. ✅ Test basic workflow with verbose on/off

### Week 3: Enhancement & Testing
10. ✅ Create error_interpretation.py for better messages
11. ✅ Write unit tests (ErrorRecord, verbose mode)
12. ✅ Write integration tests (debug commands, verbose toggle)
13. ✅ Manual testing with real UVisBox errors

### Week 4: Polish & Documentation
14. ✅ Implement auto-fix detection (optional)
15. ✅ Update USER_GUIDE.md with debug and verbose commands
16. ✅ Update CLAUDE.md with error handling patterns
17. ✅ Update API.md with ErrorRecord and output_control documentation

## Success Criteria

### Debug Features
✅ User can enable debug mode with `/debug on` for verbose error output
✅ All tool errors are captured with full stack traces
✅ User can list recent errors with `/errors`
✅ User can view full trace with `/trace <id>` or `/trace last`
✅ Error messages include helpful context (e.g., "Reds IS a valid matplotlib colormap - this may be a UVisBox bug")
✅ Auto-fixed errors are tracked and visible
✅ Debug mode doesn't break existing functionality

### Verbose Mode Features
✅ User can toggle verbose mode with `/verbose on` and `/verbose off`
✅ Internal state messages are hidden by default (verbose OFF)
✅ All `[HYBRID]`, `[DATA TOOL]`, `[VIS TOOL]` messages controlled by verbose mode
✅ Conversation is clean and user-friendly when verbose is OFF
✅ Debug information is available on demand when verbose is ON

### Performance & Compatibility
✅ Performance impact is minimal (< 5% overhead)
✅ Both modes are independent (can enable debug without verbose, etc.)
✅ Backward compatible with existing code

## Future Enhancements (Post-MVP)

1. **Export errors to file**: `/errors export errors.json`
2. **Error filtering**: `/errors --tool plot_functional_boxplot`
3. **Error search**: `/errors --contains colormap`
4. **Integration with logger**: Cross-reference error IDs with log file
5. **Error statistics**: `/stats errors` showing most common error types
6. **Diff view**: Show what changed between failed and successful auto-fix

## Migration Notes

- ✅ Backward compatible - existing code works without changes
- ✅ Opt-in feature - debug mode off by default
- ✅ No breaking changes to tool return format (uses optional `_error_details`)
- ⚠️ Need to thread ConversationSession reference through graph execution (or use context/global)

## Open Questions

1. **Session reference in nodes**: How to pass ConversationSession to node functions?
   - Option A: Add to GraphState (clean but changes state schema)
   - Option B: Use context manager / global (less clean but simpler)
   - Option C: Post-process from conversation.py (delayed recording)

2. **Log file integration**: Should error history be persisted to logs?
   - Pros: Survives session restart
   - Cons: Log file parsing complexity

3. **Max history size**: Is 20 errors enough? Too many?
   - Consider session length vs memory usage

4. **Auto-fix heuristics**: How to reliably detect when error was auto-fixed?
   - Sequence matching (error → model → tool → success)
   - May have false positives

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Performance overhead | Low | Low | Profile before/after, optimize if needed |
| Memory usage | Low | Medium | Limit history size, trim old errors |
| Breaking changes | Low | High | Careful backward compatibility testing |
| Complex state threading | Medium | Medium | Start with Option C (post-process) |

## Alternatives Considered

### Alternative 1: Always Verbose Errors
**Rejected**: Too noisy for normal conversation flow

### Alternative 2: Separate Debug Log File
**Rejected**: Less discoverable, requires file access

### Alternative 3: Error Codes + Lookup
**Rejected**: Overhead of maintaining error catalog

## Example Usage Scenarios

### Scenario 1: Clean Conversation (Default)
```
You: generate 30 curves
Assistant: Generated 30 curves and saved to temp/_temp_ensemble_curves.npy

You: plot functional boxplot
Assistant: Displayed functional boxplot for 30 curves

You: change colormap to plasma
Assistant: Updated functional boxplot with colormap plasma
```
**Note**: No internal messages shown - clean user experience.

### Scenario 2: Debugging with Verbose Mode
```
You: /verbose on
Assistant: 📢 Verbose mode enabled - showing internal state messages

You: generate 30 curves
[DATA TOOL] Calling generate_curves with args: {'n_curves': 30}
[DATA TOOL] Result: {'status': 'success', ...}
Assistant: Generated 30 curves and saved to temp/_temp_ensemble_curves.npy

You: change colormap to plasma
[HYBRID] Executing plot_functional_boxplot with updated params
[HYBRID] Fast path executed: Updated functional boxplot with colormap plasma
Assistant: Updated functional boxplot with colormap plasma

You: /verbose off
Assistant: 🔇 Verbose mode disabled - clean conversation output
```

### Scenario 3: Error Debugging with Debug Mode
```
You: plot functional boxplot with colormap Reds
Assistant: Error: I can't use "Reds" as a colormap

You: /trace last
======================================================================
Error ID: 1
Timestamp: 2025-01-30T10:23:45.123456
Tool: plot_functional_boxplot
Type: ValueError
Message: Invalid colormap name 'Reds'
Auto-fixed: False
User-facing message: I can't use "Reds" as a colormap

Full Traceback:
Traceback (most recent call last):
  File "/path/to/uvisbox/...", line 123, in functional_boxplot
    ...
  [full stack trace showing UVisBox internals]
ValueError: Invalid colormap name 'Reds'
======================================================================

You: /debug on
Assistant: 🐛 Debug mode enabled - verbose error output with tracebacks

You: plot functional boxplot with colormap Reds
Assistant: Error: Colormap error: Invalid colormap name 'Reds'
💡 Debug hint: This may be a UVisBox bug. Check if UVisBox is using the colormap correctly.

[Full traceback shown inline]
```

### Scenario 4: Combined Debug + Verbose
```
You: /debug on
Assistant: 🐛 Debug mode enabled - verbose error output with tracebacks

You: /verbose on
Assistant: 📢 Verbose mode enabled - showing internal state messages

You: generate curves
[DATA TOOL] Calling generate_curves with args: {'n_curves': 30}
[DATA TOOL] Result: {'status': 'success', ...}
Assistant: Generated 30 curves

You: plot with method fbd
[VIS TOOL] Calling plot_functional_boxplot with args: {'method': 'fbd'}
[VIS TOOL] Exception: Unknown method 'fbd'. Choose 'fdb' or 'mfbd'.
Assistant: Error: Method validation error: Unknown method 'fbd'. Choose 'fdb' or 'mfbd'.
💡 Debug hint: Check if UVisBox validation matches its documentation.

[Full traceback shown]

You: /errors
📋 Error History (1 errors):

[1] 10:23:45 - plot_functional_boxplot: ValueError (failed)

Use '/trace <id>' or '/trace last' to see full details
```

## Conclusion

This plan provides a comprehensive, user-friendly debug system that:
- ✅ Solves the immediate problem (vague error messages)
- ✅ Enables inspection of auto-fixed errors
- ✅ Maintains clean conversation UX by default
- ✅ Provides powerful debugging capabilities on demand
- ✅ Separates error debugging (debug mode) from execution visibility (verbose mode)
- ✅ Backward compatible
- ✅ Extensible for future enhancements

**Recommended start**: Phase 1 + Phase 1.5 + Phase 2 (Weeks 1-2) for immediate value.

---

## Implementation Phases

This plan has been broken down into detailed phase documents:

📂 **See `plans/debug_feature/` for detailed phase-by-phase implementation plans:**

- **Phase 1**: Core Infrastructure - ErrorRecord, error history, tool updates
- **Phase 2**: Verbose Mode Control - vprint utility, output control
- **Phase 3**: User Commands - /debug, /verbose, /errors, /trace commands
- **Phase 4**: Enhanced Error Messages - Error interpretation, hints
- **Phase 5**: Auto-Fix Detection (Optional) - Retry tracking, auto-fix marking
- **Phase 6**: Testing - Unit, integration, E2E, manual tests
- **Phase 7**: Documentation & Version - Docs update, v0.1.2 release

Each phase document includes:
- Detailed implementation steps with code examples
- Testing requirements and acceptance criteria
- Manual testing scenarios and checklists
- Dependencies and timeline estimates

👉 **Start here**: `plans/debug_feature/README.md`
