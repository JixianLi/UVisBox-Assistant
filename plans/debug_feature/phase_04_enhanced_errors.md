# Phase 4: Enhanced Error Messages

**Priority**: MEDIUM
**Timeline**: Week 3 (Days 1-2)
**Dependencies**: Phase 1 (error tracking), Phase 3 (debug mode)

## Overview

Improve error messages with context-aware interpretation:
- Detect common UVisBox error patterns
- Provide helpful debug hints
- Identify likely causes (e.g., UVisBox bugs vs user errors)
- Enhance error messages when debug mode is enabled

## Problem

Current error messages lack context:
```
Error: Invalid colormap name 'Reds'
```

But "Reds" IS a valid matplotlib colormap! The error is likely in UVisBox.

## Solution

Error interpretation layer that:
1. Analyzes error messages and tracebacks
2. Detects known patterns (colormap, method, shape errors)
3. Provides debug hints when debug mode is enabled
4. Suggests fixes or workarounds

## Deliverables

### 4.1 Create Error Interpretation Module

**File**: `src/chatuvisbox/error_interpretation.py` (new)

**Implementation**:

```python
"""Interpret and enhance error messages with context-aware hints."""

import re
from typing import Tuple, Optional

def interpret_uvisbox_error(
    error: Exception,
    traceback_str: str,
    debug_mode: bool = False
) -> Tuple[str, Optional[str]]:
    """
    Interpret UVisBox errors and provide helpful context.

    Args:
        error: The exception object
        traceback_str: Full traceback string
        debug_mode: Whether debug mode is enabled

    Returns:
        Tuple of (user_message, debug_hint)
        debug_hint is None if debug mode is OFF or no hint available
    """
    error_msg = str(error)
    error_type = type(error).__name__

    # Pattern 1: Colormap errors
    if "colormap" in error_msg.lower():
        colormap_name = _extract_colormap_name(error_msg)
        user_msg = f"Colormap error: {error_msg}"

        if debug_mode:
            if "matplotlib" in traceback_str or "mpl_colors" in traceback_str:
                hint = (
                    f"The colormap '{colormap_name}' may be valid in matplotlib "
                    f"but UVisBox might not be passing it correctly. "
                    f"This could be a UVisBox bug. Try 'viridis', 'plasma', or 'inferno' "
                    f"which are known to work."
                )
            else:
                hint = "Check if the colormap name is supported by UVisBox."
        else:
            hint = None

        return user_msg, hint

    # Pattern 2: Method validation errors
    if "unknown method" in error_msg.lower() or "invalid method" in error_msg.lower():
        method_name = _extract_method_name(error_msg)
        valid_methods = _extract_valid_methods(error_msg)

        user_msg = f"Method validation error: {error_msg}"

        if debug_mode:
            hint = (
                f"UVisBox doesn't recognize method '{method_name}'. "
                f"Valid options: {', '.join(valid_methods)}. "
                f"Note: Check UVisBox documentation - there may be a typo in the validation code."
            )
        else:
            hint = None

        return user_msg, hint

    # Pattern 3: Shape mismatch errors
    if "shape" in error_msg.lower() and ("expected" in error_msg.lower() or "got" in error_msg.lower()):
        shape_info = _extract_shape_info(error_msg)
        user_msg = f"Data shape mismatch: {error_msg}"

        if debug_mode:
            hint = (
                f"Data shape is {shape_info['actual']} but expected {shape_info['expected']}. "
                f"Check if you're using the right data for this visualization type."
            )
        else:
            hint = None

        return user_msg, hint

    # Pattern 4: File not found
    if error_type == "FileNotFoundError":
        user_msg = f"File not found: {error_msg}"

        if debug_mode:
            hint = (
                "The data file may have been deleted or not yet created. "
                "Use '/context' to see available session files."
            )
        else:
            hint = None

        return user_msg, hint

    # Pattern 5: Import errors (UVisBox not installed)
    if error_type == "ImportError" or error_type == "ModuleNotFoundError":
        if "uvisbox" in error_msg.lower():
            user_msg = "UVisBox is not installed or not accessible"

            if debug_mode:
                hint = (
                    "Make sure UVisBox is installed in the 'agent' conda environment. "
                    "Run: conda activate agent && pip install uvisbox"
                )
            else:
                hint = None

            return user_msg, hint

    # Default: return original message
    return error_msg, None


def _extract_colormap_name(error_msg: str) -> str:
    """Extract colormap name from error message."""
    # Try patterns like "colormap 'Reds'" or "Invalid colormap name 'Reds'"
    match = re.search(r"colormap\s+['\"]?(\w+)['\"]?", error_msg, re.IGNORECASE)
    if match:
        return match.group(1)

    match = re.search(r"['\"](\w+)['\"]", error_msg)
    if match:
        return match.group(1)

    return "unknown"


def _extract_method_name(error_msg: str) -> str:
    """Extract method name from error message."""
    # Try patterns like "Unknown method 'fbd'" or "method 'fbd'"
    match = re.search(r"method\s+['\"]?(\w+)['\"]?", error_msg, re.IGNORECASE)
    if match:
        return match.group(1)

    match = re.search(r"['\"](\w+)['\"]", error_msg)
    if match:
        return match.group(1)

    return "unknown"


def _extract_valid_methods(error_msg: str) -> list:
    """Extract list of valid methods from error message."""
    # Try pattern like "Choose 'fdb' or 'mfbd'"
    match = re.search(r"Choose\s+([^.]+)", error_msg, re.IGNORECASE)
    if match:
        methods_str = match.group(1)
        # Extract quoted strings
        methods = re.findall(r"['\"](\w+)['\"]", methods_str)
        return methods

    return ["see documentation"]


def _extract_shape_info(error_msg: str) -> dict:
    """Extract shape information from error message."""
    shape_info = {"actual": "unknown", "expected": "unknown"}

    # Try to extract actual shape
    match = re.search(r"got\s+shape\s+\(([^)]+)\)", error_msg, re.IGNORECASE)
    if match:
        shape_info["actual"] = f"({match.group(1)})"

    # Try to extract expected shape
    match = re.search(r"expected\s+([^,]+)", error_msg, re.IGNORECASE)
    if match:
        shape_info["expected"] = match.group(1).strip()

    return shape_info


def format_error_with_hint(user_message: str, hint: Optional[str]) -> str:
    """
    Format error message with optional debug hint.

    Args:
        user_message: Main error message
        hint: Optional debug hint (shown when debug mode is ON)

    Returns:
        Formatted error message
    """
    if hint:
        return f"{user_message}\n💡 Debug hint: {hint}"
    return user_message
```

### 4.2 Integrate Error Interpretation into Tools

**File**: `src/chatuvisbox/vis_tools.py` (and other tool files)

**Update error handling pattern**:

```python
import traceback
from chatuvisbox.error_interpretation import interpret_uvisbox_error, format_error_with_hint

def plot_functional_boxplot(...) -> Dict[str, str]:
    """Tool function with enhanced error interpretation."""
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

        # Interpret error (but don't pass debug_mode here - do it in nodes.py)
        user_msg, debug_hint = interpret_uvisbox_error(e, tb_str, debug_mode=False)

        # Return error info with interpretation
        return {
            "status": "error",
            "message": user_msg,
            "_error_details": {
                "exception": e,
                "traceback": tb_str,
                "debug_hint": debug_hint  # Store for later use
            }
        }
```

**Wait**: This approach requires access to session.debug_mode in tools.

**Better Approach**: Do interpretation in `conversation.py` when recording error:

```python
# In conversation.py
from chatuvisbox.error_interpretation import interpret_uvisbox_error, format_error_with_hint

def record_error(
    self,
    tool_name: str,
    error: Exception,
    traceback_str: str,
    user_message: str,
    auto_fixed: bool = False,
    context: Optional[Dict] = None
) -> ErrorRecord:
    """Record error with enhanced interpretation."""

    # Interpret error with debug mode context
    interpreted_msg, debug_hint = interpret_uvisbox_error(
        error,
        traceback_str,
        debug_mode=self.debug_mode
    )

    # Format message with hint if available
    enhanced_msg = format_error_with_hint(interpreted_msg, debug_hint)

    # Create record with enhanced message
    record = ErrorRecord(
        error_id=self._next_error_id,
        timestamp=datetime.now(),
        tool_name=tool_name,
        error_type=type(error).__name__,
        error_message=str(error),
        full_traceback=traceback_str,
        user_facing_message=enhanced_msg,  # Use enhanced message
        auto_fixed=auto_fixed,
        context=context
    )

    # ... rest of record_error ...
```

**Even Better**: Keep tools simple, do interpretation at display time:

```python
# In main.py or nodes.py, when showing error to user
from chatuvisbox.error_interpretation import interpret_uvisbox_error, format_error_with_hint

# When displaying error
if session.debug_mode:
    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=True)
    display_msg = format_error_with_hint(user_msg, hint)
else:
    display_msg = user_message

print(display_msg)
```

**Recommendation**: Keep interpretation at display/recording time, not in tools themselves.

### 4.3 Update Error Display in Nodes

**File**: `src/chatuvisbox/nodes.py`

**Enhance error display**:

```python
from chatuvisbox.error_interpretation import interpret_uvisbox_error, format_error_with_hint
from chatuvisbox.output_control import vprint

def call_vis_tool(state: GraphState) -> GraphState:
    # ... existing code ...

    try:
        result = fn(**tool_input)

        if result.get("status") == "error":
            # Extract error details
            if "_error_details" in result:
                error_details = result["_error_details"]
                error = error_details["exception"]
                traceback_str = error_details["traceback"]

                # Interpret error (need session for debug_mode)
                # TODO: How to access session.debug_mode here?
                # Option: Pass through state, or do interpretation in conversation.py

                vprint(f"[VIS TOOL] Exception: {error}")

        # ... rest of code ...

    except Exception as e:
        # ... existing error handling ...
```

**Challenge**: Still need access to session.debug_mode.

**Final Recommendation**: Do all error interpretation in `conversation.py` after graph execution, where we have full access to session state.

### 4.4 Error Interpretation in Conversation.py

**File**: `src/chatuvisbox/conversation.py`

**Complete implementation**:

```python
from chatuvisbox.error_interpretation import interpret_uvisbox_error, format_error_with_hint

def send(self, user_message: str) -> GraphState:
    # ... existing code ...

    # After graph execution, interpret and display errors
    for message in state["messages"]:
        if isinstance(message, ToolMessage):
            try:
                content = json.loads(message.content) if isinstance(message.content, str) else message.content

                if content.get("status") == "error":
                    error_msg = content.get("message", "Unknown error")

                    # If we have error details, interpret them
                    if "_error_details" in content:
                        error_details = content["_error_details"]
                        error = error_details.get("exception")
                        traceback_str = error_details.get("traceback", "")

                        # Interpret with current debug mode
                        interpreted_msg, debug_hint = interpret_uvisbox_error(
                            error,
                            traceback_str,
                            debug_mode=self.debug_mode
                        )

                        # Format with hint
                        enhanced_msg = format_error_with_hint(interpreted_msg, debug_hint)

                        # Update message content
                        content["message"] = enhanced_msg

                        # Record error with enhanced message
                        self.record_error(
                            tool_name=message.name,
                            error=error,
                            traceback_str=traceback_str,
                            user_message=enhanced_msg,
                            auto_fixed=False
                        )

            except (json.JSONDecodeError, KeyError, AttributeError):
                pass  # Not an error message or malformed

    return state
```

## Testing Strategy

### Unit Tests

**File**: `tests/unit/test_error_interpretation.py` (new)

```python
import pytest
from chatuvisbox.error_interpretation import (
    interpret_uvisbox_error,
    format_error_with_hint,
    _extract_colormap_name,
    _extract_method_name,
    _extract_valid_methods
)

def test_colormap_error_no_debug():
    """Test colormap error interpretation without debug mode."""
    error = ValueError("Invalid colormap name 'Reds'")
    traceback = "...matplotlib..."

    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=False)

    assert "Colormap error" in user_msg
    assert hint is None  # No hint when debug OFF

def test_colormap_error_with_debug():
    """Test colormap error interpretation with debug mode."""
    error = ValueError("Invalid colormap name 'Reds'")
    traceback = "...matplotlib...mpl_colors..."

    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=True)

    assert "Colormap error" in user_msg
    assert hint is not None
    assert "UVisBox" in hint
    assert "bug" in hint.lower()

def test_method_error_with_debug():
    """Test method validation error."""
    error = ValueError("Unknown method 'fbd'. Choose 'fdb' or 'mfbd'.")
    traceback = "..."

    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=True)

    assert "Method validation error" in user_msg
    assert hint is not None
    assert "'fbd'" in hint
    assert "fdb" in hint or "mfbd" in hint

def test_shape_error_with_debug():
    """Test shape mismatch error."""
    error = ValueError("Expected 2D array, got shape (100, 50, 3)")
    traceback = "..."

    user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=True)

    assert "shape" in user_msg.lower()
    assert hint is not None
    assert "(100, 50, 3)" in hint

def test_extract_colormap_name():
    """Test colormap name extraction."""
    assert _extract_colormap_name("Invalid colormap 'Reds'") == "Reds"
    assert _extract_colormap_name("colormap Plasma not found") == "Plasma"

def test_extract_method_name():
    """Test method name extraction."""
    assert _extract_method_name("Unknown method 'fbd'") == "fbd"
    assert _extract_method_name("Invalid method: mfbd") == "mfbd"

def test_extract_valid_methods():
    """Test valid methods extraction."""
    methods = _extract_valid_methods("Choose 'fdb' or 'mfbd'")
    assert "fdb" in methods
    assert "mfbd" in methods

def test_format_error_with_hint():
    """Test error formatting with hint."""
    formatted = format_error_with_hint("Error message", "This is a hint")
    assert "Error message" in formatted
    assert "💡 Debug hint:" in formatted
    assert "This is a hint" in formatted

def test_format_error_without_hint():
    """Test error formatting without hint."""
    formatted = format_error_with_hint("Error message", None)
    assert formatted == "Error message"
    assert "💡" not in formatted
```

### Integration Tests

**File**: `tests/integration/test_error_interpretation_integration.py` (new)

```python
def test_colormap_error_interpretation_workflow():
    """Test full workflow with colormap error interpretation."""
    session = ConversationSession()
    session.debug_mode = True

    # Trigger colormap error (mock)
    # ... trigger error ...

    # Check that error was interpreted
    last_error = session.get_last_error()
    assert last_error is not None
    assert "UVisBox" in last_error.user_facing_message or "bug" in last_error.user_facing_message.lower()

def test_debug_mode_affects_error_hints():
    """Test that debug mode controls hint visibility."""
    # With debug OFF
    session1 = ConversationSession()
    session1.debug_mode = False
    # ... trigger error ...
    # ... verify no hint in message ...

    # With debug ON
    session2 = ConversationSession()
    session2.debug_mode = True
    # ... trigger same error ...
    # ... verify hint appears in message ...
```

## Manual Testing Scenarios

### Scenario 1: Colormap Error

**Without Debug Mode**:
```
You: plot with colormap Reds
Assistant: Colormap error: Invalid colormap name 'Reds'
```

**With Debug Mode**:
```
You: /debug on
You: plot with colormap Reds
Assistant: Colormap error: Invalid colormap name 'Reds'
💡 Debug hint: The colormap 'Reds' may be valid in matplotlib but UVisBox might not be passing it correctly. This could be a UVisBox bug. Try 'viridis', 'plasma', or 'inferno' which are known to work.
```

### Scenario 2: Method Error

**With Debug Mode**:
```
You: plot with method fbd
Assistant: Method validation error: Unknown method 'fbd'. Choose 'fdb' or 'mfbd'.
💡 Debug hint: UVisBox doesn't recognize method 'fbd'. Valid options: fdb, mfbd. Note: Check UVisBox documentation - there may be a typo in the validation code.
```

## Acceptance Criteria

- ✅ error_interpretation.py module created
- ✅ Colormap errors interpreted with helpful hints
- ✅ Method validation errors interpreted
- ✅ Shape mismatch errors interpreted
- ✅ File not found errors interpreted
- ✅ Import errors (UVisBox not installed) interpreted
- ✅ Debug hints only shown when debug mode is ON
- ✅ Error interpretation integrated into conversation.py
- ✅ Unit tests pass (100% coverage for interpretation logic)
- ✅ Integration tests verify hint visibility based on debug mode
- ✅ Manual testing confirms improved error messages

## Next Phase

After completing Phase 4, proceed to:
- **Phase 5: Auto-Fix Detection** (Optional) - Track retry attempts
- **Phase 6: Testing** - Comprehensive test suite
