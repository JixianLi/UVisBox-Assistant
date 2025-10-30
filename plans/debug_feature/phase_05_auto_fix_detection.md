# Phase 5: Auto-Fix Detection

**Priority**: LOW (Optional Enhancement)
**Timeline**: Week 4 (Days 1-2)
**Dependencies**: Phase 1 (error tracking)

## Overview

Track when errors are automatically fixed by the LLM:
- Detect error → retry → success patterns
- Mark errors as auto-fixed in history
- Provide visibility into LLM self-correction
- Help users understand what was automatically recovered

## Problem

Currently, when an error occurs and the LLM retries with corrected parameters, the user only sees:
1. Error message
2. Success message (after retry)

The user doesn't know:
- That an error occurred and was auto-fixed
- What the LLM changed to fix it
- How many attempts were needed

## Solution

Track tool execution sequences to detect auto-fix patterns:
```
Turn N:   call_tool → ERROR → call_model → call_tool → SUCCESS
                      ^                                   ^
                      |___________________________________|
                              Auto-fix detected
```

## Use Cases

### Use Case 1: Silent Auto-Fix
```
You: generate 30 curves and plot them

# Behind the scenes:
# 1. generate_curves → success
# 2. plot_functional_boxplot → ERROR (missing data_path)
# 3. Model retries with correct data_path → SUCCESS

# User sees:
Assistant: Generated 30 curves and displayed functional boxplot.

# With auto-fix tracking:
You: /errors
📋 Error History (1 errors):
[1] 10:23:45 - plot_functional_boxplot: ValueError (auto-fixed)
```

### Use Case 2: Visible Auto-Fix Attempt
```
You: plot with wrong parameters

# Error occurs, model tries to fix
Assistant: I encountered an error but was able to fix it. Displayed functional boxplot.

You: /trace last
# Shows what went wrong and how it was fixed
```

## Deliverables

### 5.1 Add Tool Execution Tracking to GraphState

**File**: `src/chatuvisbox/state.py`

**Add new fields**:

```python
class GraphState(TypedDict):
    # ... existing fields ...

    # New fields for auto-fix detection
    tool_execution_sequence: List[Dict]  # Track tool calls
    last_error_tool: Optional[str]       # Track which tool failed
    last_error_id: Optional[int]         # Link to error record
```

**Tool execution entry**:
```python
{
    "tool_name": "plot_functional_boxplot",
    "status": "error" | "success",
    "timestamp": datetime,
    "error_id": int | None
}
```

### 5.2 Update Nodes to Track Execution

**File**: `src/chatuvisbox/nodes.py`

**Update `call_vis_tool` and `call_data_tool`**:

```python
from datetime import datetime

def call_vis_tool(state: GraphState) -> GraphState:
    # ... existing code ...

    # Track execution start
    execution_entry = {
        "tool_name": tool_name,
        "timestamp": datetime.now(),
        "status": None,
        "error_id": None
    }

    try:
        result = fn(**tool_input)

        if result.get("status") == "error":
            # Record as error execution
            execution_entry["status"] = "error"

            # If error was recorded, link it
            if hasattr(state, "_last_error_id"):
                execution_entry["error_id"] = state["_last_error_id"]

            # Store for auto-fix detection
            state["last_error_tool"] = tool_name
            state["last_error_id"] = execution_entry["error_id"]

        else:
            # Record as success execution
            execution_entry["status"] = "success"

            # Check for auto-fix: was last execution an error with same tool?
            if (state.get("last_error_tool") == tool_name and
                state.get("last_error_id") is not None):

                # Auto-fix detected! Mark previous error
                # TODO: Need way to update error record
                print(f"[AUTO-FIX] {tool_name} succeeded after error")

                # Clear auto-fix tracking
                state["last_error_tool"] = None
                state["last_error_id"] = None

    except Exception as e:
        execution_entry["status"] = "error"

    # Append to execution sequence
    if "tool_execution_sequence" not in state:
        state["tool_execution_sequence"] = []
    state["tool_execution_sequence"].append(execution_entry)

    # ... rest of existing code ...
```

### 5.3 Add Auto-Fix Marking Method

**File**: `src/chatuvisbox/conversation.py`

**Add method to mark error as auto-fixed**:

```python
def mark_error_auto_fixed(self, error_id: int) -> bool:
    """
    Mark an error as auto-fixed.

    Args:
        error_id: ID of the error to mark

    Returns:
        True if error was found and marked, False otherwise
    """
    for err in self.error_history:
        if err.error_id == error_id:
            # Update the error record (need to make it mutable)
            # Note: dataclass is frozen by default
            err.auto_fixed = True
            return True
    return False
```

**Note**: Need to make ErrorRecord mutable or use different approach.

**Alternative**: Store auto-fix status separately:

```python
class ConversationSession:
    def __init__(self):
        # ... existing fields ...
        self.auto_fixed_errors: Set[int] = set()  # IDs of auto-fixed errors

    def mark_error_auto_fixed(self, error_id: int):
        """Mark error as auto-fixed."""
        self.auto_fixed_errors.add(error_id)

    def is_error_auto_fixed(self, error_id: int) -> bool:
        """Check if error was auto-fixed."""
        return error_id in self.auto_fixed_errors
```

Then update `ErrorRecord.summary()` to check this set.

### 5.4 Update Error Display to Show Auto-Fix Status

**File**: `src/chatuvisbox/main.py`

**Update `/errors` command**:

```python
elif user_input == "/errors":
    if not session.error_history:
        print("No errors recorded in this session.")
    else:
        print(f"\n📋 Error History ({len(session.error_history)} errors):\n")
        for err in session.error_history:
            # Check if auto-fixed
            is_auto_fixed = session.is_error_auto_fixed(err.error_id)
            status = "auto-fixed ✓" if is_auto_fixed else "failed"
            print(f"[{err.error_id}] {err.timestamp.strftime('%H:%M:%S')} - {err.tool_name}: {err.error_type} ({status})")
        print("\n💡 Use '/trace <id>' or '/trace last' to see full details")
    return True
```

### 5.5 Auto-Fix Detection Logic

**File**: `src/chatuvisbox/auto_fix_detector.py` (new)

**Implementation**:

```python
"""Detect auto-fix patterns in tool execution sequences."""

from typing import List, Dict, Optional

def detect_auto_fix(
    tool_sequence: List[Dict],
    lookback: int = 5
) -> Optional[tuple]:
    """
    Detect if recent tool executions show auto-fix pattern.

    Pattern: tool_X fails → model → tool_X succeeds

    Args:
        tool_sequence: List of tool execution entries
        lookback: How many recent executions to check

    Returns:
        (error_id, fixed_error_id) if auto-fix detected, None otherwise
    """
    if len(tool_sequence) < 2:
        return None

    # Check last N executions
    recent = tool_sequence[-lookback:]

    # Look for pattern: ERROR followed by SUCCESS with same tool
    for i in range(len(recent) - 1):
        curr = recent[i]
        next_exec = recent[i + 1]

        if (curr["status"] == "error" and
            next_exec["status"] == "success" and
            curr["tool_name"] == next_exec["tool_name"]):

            # Auto-fix detected!
            return (curr.get("error_id"), next_exec["tool_name"])

    return None
```

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_auto_fix_detection.py` (new)

```python
def test_detect_auto_fix_simple():
    """Test simple auto-fix pattern detection."""
    sequence = [
        {"tool_name": "plot_boxplot", "status": "error", "error_id": 1},
        {"tool_name": "plot_boxplot", "status": "success", "error_id": None}
    ]

    result = detect_auto_fix(sequence)

    assert result is not None
    assert result[0] == 1  # error_id
    assert result[1] == "plot_boxplot"

def test_detect_auto_fix_no_pattern():
    """Test when no auto-fix pattern exists."""
    sequence = [
        {"tool_name": "generate_curves", "status": "success", "error_id": None},
        {"tool_name": "plot_boxplot", "status": "success", "error_id": None}
    ]

    result = detect_auto_fix(sequence)

    assert result is None

def test_detect_auto_fix_different_tool():
    """Test that different tools don't trigger auto-fix."""
    sequence = [
        {"tool_name": "plot_boxplot", "status": "error", "error_id": 1},
        {"tool_name": "plot_curves", "status": "success", "error_id": None}
    ]

    result = detect_auto_fix(sequence)

    assert result is None

def test_mark_error_auto_fixed():
    """Test marking error as auto-fixed."""
    session = ConversationSession()

    # Record error
    session.record_error(
        tool_name="test_tool",
        error=ValueError("test"),
        traceback_str="...",
        user_message="Test error"
    )

    # Mark as auto-fixed
    session.mark_error_auto_fixed(1)

    # Verify
    assert session.is_error_auto_fixed(1)
    assert not session.is_error_auto_fixed(2)
```

### Integration Tests

**File**: `tests/integration/test_auto_fix_workflow.py` (new)

```python
def test_auto_fix_workflow():
    """Test complete auto-fix detection workflow."""
    session = ConversationSession()

    # Step 1: Trigger error
    # ... trigger error in tool ...

    # Step 2: LLM retries and succeeds
    # ... successful retry ...

    # Step 3: Check error history
    errors = session.error_history
    assert len(errors) == 1

    # Step 4: Verify auto-fix detected
    assert session.is_error_auto_fixed(errors[0].error_id)

def test_failed_error_not_marked():
    """Test that unrecovered errors are not marked auto-fixed."""
    session = ConversationSession()

    # Trigger error that is NOT fixed
    # ... trigger error ...

    # Check error history
    errors = session.error_history
    assert len(errors) == 1

    # Verify NOT marked as auto-fixed
    assert not session.is_error_auto_fixed(errors[0].error_id)
```

## Manual Testing

### Test Scenario 1: Successful Auto-Fix
```bash
You: generate curves and plot them with wrong colormap
# Model generates curves successfully
# Model tries to plot with invalid colormap → ERROR
# Model retries with valid colormap → SUCCESS

You: /errors
📋 Error History (1 errors):
[1] 10:23:45 - plot_functional_boxplot: ValueError (auto-fixed ✓)

You: /trace 1
# Shows original error and that it was auto-fixed
```

### Test Scenario 2: Failed Error (Not Auto-Fixed)
```bash
You: plot with fundamentally incompatible data

# Error occurs, model can't fix it

You: /errors
📋 Error History (1 errors):
[1] 10:25:30 - plot_functional_boxplot: ValueError (failed)
```

## Challenges & Limitations

### Challenge 1: False Positives
**Problem**: Same tool called twice in sequence (success → success) might be misdetected.

**Solution**: Only detect if first call was error, second was success.

### Challenge 2: Multiple Retries
**Problem**: Error → Error → Error → Success (3 retries).

**Solution**: Only mark the most recent error as auto-fixed, or track retry count.

### Challenge 3: Partial Fix
**Problem**: Error A → partial fix → Error B → full fix.

**Solution**: Mark both errors, or only final one. Needs design decision.

### Challenge 4: Concurrent Tools
**Problem**: Multiple tools failing and succeeding in complex patterns.

**Solution**: Use sequence matching with tool name checks.

## Acceptance Criteria

- ✅ Tool execution sequence tracked in GraphState
- ✅ Auto-fix detection logic implemented
- ✅ Errors can be marked as auto-fixed
- ✅ `/errors` command shows auto-fixed status
- ✅ False positives minimized
- ✅ Unit tests pass
- ✅ Integration tests verify auto-fix detection
- ✅ Manual testing confirms correct marking

## Optional Enhancements

### Enhancement 1: Auto-Fix Notification
Show user when auto-fix occurs:
```
Assistant: I encountered an error with the colormap but fixed it automatically. Displayed functional boxplot with colormap 'viridis'.
```

### Enhancement 2: Auto-Fix Statistics
Add to `/stats` command:
```
Auto-fix rate: 3/5 errors (60%)
Most common auto-fixes: colormap errors (2), method errors (1)
```

### Enhancement 3: Diff View
Show what changed between error and fix:
```
You: /trace 1 --diff
Original call: plot_functional_boxplot(colormap='Reds')
Fixed call:    plot_functional_boxplot(colormap='viridis')
```

## Decision: Implement or Skip?

**Arguments FOR**:
- Provides visibility into LLM behavior
- Helps users trust auto-correction
- Useful for debugging conversation flow

**Arguments AGAINST**:
- Complex to implement correctly
- Many edge cases and false positives
- Low user-facing value (errors are already fixed)
- Better to focus on preventing errors

**Recommendation**: **SKIP for MVP**, consider for v2 if users request it.

Alternative: Simple logging of retries without auto-fix tracking.

## Next Phase

After deciding on Phase 5, proceed to:
- **Phase 6: Testing** - Comprehensive test suite for all features