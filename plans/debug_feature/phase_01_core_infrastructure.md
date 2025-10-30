# Phase 1: Core Infrastructure

**Priority**: HIGH
**Timeline**: Week 1 (Days 1-3)
**Dependencies**: None

## Overview

Establish the foundational infrastructure for error tracking and debugging:
- ErrorRecord class to capture full error details
- Error history storage in ConversationSession
- Enhanced error handling in tools
- Error recording in node functions

## Deliverables

### 1.1 Create ErrorRecord Class

**File**: `src/chatuvisbox/error_tracking.py` (new)

**Implementation**:

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
        """Brief one-line summary for error list."""
        status = "auto-fixed" if self.auto_fixed else "failed"
        return f"[{self.error_id}] {self.timestamp.strftime('%H:%M:%S')} - {self.tool_name}: {self.error_type} ({status})"

    def detailed(self) -> str:
        """Detailed multi-line description with full traceback."""
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

**Tests Required**:
- ErrorRecord creation with all fields
- summary() format correctness
- detailed() format with/without context
- Timestamp handling

### 1.2 Add Error History to ConversationSession

**File**: `src/chatuvisbox/conversation.py`

**Changes**:

```python
from typing import List, Optional
from datetime import datetime
from chatuvisbox.error_tracking import ErrorRecord

class ConversationSession:
    def __init__(self):
        # ... existing fields ...

        # New fields for error tracking and modes
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
        """
        Record an error in history.

        Args:
            tool_name: Name of the tool that failed
            error: The exception object
            traceback_str: Full traceback string from traceback.format_exc()
            user_message: User-friendly error message
            auto_fixed: Whether this error was automatically fixed
            context: Optional context dict (e.g., state snapshot)

        Returns:
            ErrorRecord object
        """
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

        # Log to file (if logger integration added later)
        # logger.log_error_record(record)

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

**Tests Required**:
- record_error() creates ErrorRecord correctly
- Error history respects max_error_history limit
- get_error() retrieves by ID
- get_last_error() returns most recent
- Error IDs increment correctly

### 1.3 Update Tool Error Handling Pattern

**Files**: `src/chatuvisbox/vis_tools.py`, `src/chatuvisbox/data_tools.py`

**Pattern** (apply to all tool functions):

```python
import traceback

def plot_functional_boxplot(...) -> Dict[str, str]:
    """Tool function with enhanced error handling."""
    try:
        # ... existing implementation ...

        return {
            "status": "success",
            "message": "...",
            "_vis_params": {...}
        }

    except Exception as e:
        # Capture full traceback
        tb_str = traceback.format_exc()

        # Create user-friendly message
        user_msg = f"Error creating functional boxplot: {str(e)}"

        # Return error info with traceback for recording
        return {
            "status": "error",
            "message": user_msg,
            "_error_details": {
                "exception": e,
                "traceback": tb_str
            }
        }
```

**Key Points**:
- Use `traceback.format_exc()` to capture full stack
- Keep user message concise and friendly
- Include `_error_details` dict with exception and traceback
- Don't change existing return format (backward compatible)

**Files to Update**:
- `plot_functional_boxplot` ✅
- `plot_curve_boxplot` ✅
- `plot_probabilistic_marching_squares` ✅
- `plot_uncertainty_lobes` ✅
- `plot_squid_glyph_2D` ✅
- `plot_contour_boxplot` ✅
- `generate_curves` ✅
- `load_data` ✅
- Any other data tools ✅

**Tests Required**:
- Error return format includes _error_details
- Traceback is captured correctly
- User message remains friendly

### 1.4 Update Tool Nodes to Record Errors

**File**: `src/chatuvisbox/nodes.py`

**Changes to `call_data_tool` and `call_vis_tool`**:

```python
from chatuvisbox.error_tracking import ErrorRecord

def call_data_tool(state: GraphState) -> GraphState:
    # ... existing code to get tool and input ...

    # Execute tool
    result = fn(**tool_input)

    # Check for error details and record if present
    if result.get("status") == "error" and "_error_details" in result:
        # TODO: Need to pass session reference to record error
        # Option 1: Add session to GraphState
        # Option 2: Use global/context manager
        # Option 3: Post-process in conversation.py

        # For now, just pass error details through
        error_details = result["_error_details"]
        # Future: session.record_error(...)

    # ... rest of existing code ...

    return state

def call_vis_tool(state: GraphState) -> GraphState:
    # ... similar pattern ...
    pass
```

**Open Question**: How to pass ConversationSession to node functions?

**Options**:
1. **Add to GraphState** (cleanest)
   - Pros: Explicit, type-safe
   - Cons: Changes state schema

2. **Use global/context manager** (simplest)
   - Pros: No state changes, easy to implement
   - Cons: Less clean, harder to test

3. **Post-process in conversation.py** (delayed)
   - Pros: No changes to nodes or state
   - Cons: Can't record errors in real-time

**Recommendation**: Start with Option 3 (post-process), migrate to Option 1 if needed.

**Post-Process Implementation** (in `conversation.py`):

```python
def send(self, user_message: str) -> GraphState:
    # ... existing code ...

    # After graph execution, check for errors in messages
    for message in state["messages"]:
        if isinstance(message, ToolMessage):
            try:
                content = json.loads(message.content)
                if content.get("status") == "error" and "_error_details" in content:
                    # Record error after the fact
                    error_details = content["_error_details"]
                    self.record_error(
                        tool_name=message.name,
                        error=error_details["exception"],
                        traceback_str=error_details["traceback"],
                        user_message=content["message"],
                        auto_fixed=False
                    )
            except (json.JSONDecodeError, KeyError):
                pass  # Not an error message

    return state
```

**Tests Required**:
- Error recording triggered on tool failure
- Error details properly extracted
- Non-error messages ignored

## Acceptance Criteria

- ✅ ErrorRecord class created with all required fields
- ✅ ConversationSession has error_history list
- ✅ record_error() method works correctly
- ✅ get_error() and get_last_error() work
- ✅ All tool functions capture traceback in _error_details
- ✅ Error recording integrated (via post-process or other method)
- ✅ Backward compatible - existing code works without changes
- ✅ Unit tests pass for all new functionality

## Migration Notes

- No breaking changes to existing code
- `_error_details` is optional in tool return dict
- Error history starts empty, populated over time
- Old tools without traceback capture still work (no traceback recorded)

## Next Phase

After completing Phase 1, proceed to:
- **Phase 2: Verbose Mode Control** - Add vprint utility for internal messages
