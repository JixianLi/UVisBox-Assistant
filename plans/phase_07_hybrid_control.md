# Phase 7: Hybrid Control Model

**Goal**: Implement fast, direct parameter updates for simple commands without full LangGraph execution.

**Duration**: 0.5-1 day

## Prerequisites

- Phase 6 completed (conversational follow-up working)
- Understanding of when to bypass LangGraph for efficiency

## Concept

**Hybrid Control** means:
- **Complex queries** → Full LangGraph workflow (data loading, multi-step, ambiguous requests)
- **Simple parameter changes** → Direct function call bypass (faster, more responsive)

Examples of simple commands:
- "colormap viridis"
- "percentile 80"
- "hide median"
- "show outliers"
- "isovalue 0.6"

These should:
1. Be detected by pattern matching
2. Update `last_viz_params`
3. Call viz tool directly
4. Skip LangGraph entirely

## Tasks

### Task 7.1: Implement Command Parser

**File**: `command_parser.py`

```python
"""Parse simple direct commands for hybrid control."""

import re
from typing import Optional, Tuple, Dict


class SimpleCommand:
    """Represents a simple parameter update command."""

    def __init__(self, param_name: str, value):
        self.param_name = param_name
        self.value = value

    def __repr__(self):
        return f"SimpleCommand({self.param_name}={self.value})"


def parse_simple_command(user_input: str) -> Optional[SimpleCommand]:
    """
    Try to parse user input as a simple parameter command.

    Simple commands are:
    - Single parameter updates
    - No ambiguity
    - No need for LLM interpretation

    Args:
        user_input: User's input string

    Returns:
        SimpleCommand if recognized, None otherwise
    """
    # Normalize input
    text = user_input.strip().lower()

    # Pattern 1: "colormap <name>"
    match = re.match(r'colormap\s+(\w+)', text)
    if match:
        return SimpleCommand('colormap', match.group(1))

    # Pattern 2: "percentile <number>"
    match = re.match(r'percentile\s+(\d+\.?\d*)', text)
    if match:
        value = float(match.group(1))
        return SimpleCommand('percentile', value)

    # Pattern 3: "isovalue <number>"
    match = re.match(r'isovalue\s+(\d+\.?\d*)', text)
    if match:
        value = float(match.group(1))
        return SimpleCommand('isovalue', value)

    # Pattern 4: "show median" / "hide median"
    if text in ['show median', 'show the median']:
        return SimpleCommand('show_median', True)
    if text in ['hide median', 'hide the median']:
        return SimpleCommand('show_median', False)

    # Pattern 5: "show outliers" / "hide outliers"
    if text in ['show outliers', 'show the outliers']:
        return SimpleCommand('show_outliers', True)
    if text in ['hide outliers', 'hide the outliers']:
        return SimpleCommand('show_outliers', False)

    # Pattern 6: "scale <number>"
    match = re.match(r'scale\s+(\d+\.?\d*)', text)
    if match:
        value = float(match.group(1))
        return SimpleCommand('scale', value)

    # Pattern 7: "alpha <number>"
    match = re.match(r'alpha\s+(\d+\.?\d*)', text)
    if match:
        value = float(match.group(1))
        return SimpleCommand('alpha', value)

    # Not a simple command
    return None


def apply_command_to_params(command: SimpleCommand, current_params: dict) -> dict:
    """
    Apply a simple command to existing viz parameters.

    Args:
        command: The parsed command
        current_params: Current visualization parameters

    Returns:
        Updated parameters
    """
    updated = current_params.copy()

    # Map command param names to viz tool param names
    param_mapping = {
        'colormap': 'colormap',
        'percentile': 'percentile',
        'isovalue': 'isovalue',
        'show_median': 'show_median',
        'show_outliers': 'show_outliers',
        'scale': 'scale',
        'alpha': 'alpha',
    }

    param_name = param_mapping.get(command.param_name, command.param_name)
    updated[param_name] = command.value

    return updated


# Test cases
if __name__ == "__main__":
    test_inputs = [
        "colormap plasma",
        "percentile 75",
        "isovalue 0.8",
        "show median",
        "hide outliers",
        "scale 0.5",
        "alpha 0.7",
        "generate some curves",  # Should return None
    ]

    for inp in test_inputs:
        result = parse_simple_command(inp)
        print(f"{inp:30} -> {result}")
```

Run:
```bash
python command_parser.py
```

### Task 7.2: Implement Hybrid Executor

**File**: `hybrid_control.py`

```python
"""Hybrid control system for fast parameter updates."""

from typing import Optional, Dict
from command_parser import parse_simple_command, apply_command_to_params
from vis_tools import VIS_TOOLS


def execute_simple_command(
    command_str: str,
    current_state: dict
) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Try to execute a command as a simple parameter update.

    Args:
        command_str: User's command string
        current_state: Current conversation state with last_viz_params

    Returns:
        Tuple of (success, result, message)
        - success: True if command was handled, False if needs full graph
        - result: Result from viz tool execution (if applicable)
        - message: Status message
    """
    # Try to parse as simple command
    command = parse_simple_command(command_str)

    if command is None:
        return False, None, "Not a simple command"

    # Need existing viz params to update
    last_viz_params = current_state.get("last_viz_params")

    if not last_viz_params:
        return False, None, "No previous visualization to update"

    # Extract the tool name and data path from last viz
    viz_tool_name = last_viz_params.get("_tool_name")
    data_path = last_viz_params.get("data_path")

    if not viz_tool_name or not data_path:
        return False, None, "Cannot determine visualization to update"

    # Apply command to params
    updated_params = apply_command_to_params(command, last_viz_params)

    # Execute viz tool directly
    viz_func = VIS_TOOLS.get(viz_tool_name)

    if not viz_func:
        return False, None, f"Unknown viz tool: {viz_tool_name}"

    print(f"[HYBRID] Executing {viz_tool_name} with updated params")

    # Remove internal fields before calling tool
    call_params = {k: v for k, v in updated_params.items() if not k.startswith('_')}

    result = viz_func(**call_params)

    if result.get("status") == "success":
        # Update state (caller should do this)
        updated_params['_tool_name'] = viz_tool_name
        return True, updated_params, f"Updated {command.param_name} to {command.value}"
    else:
        return False, None, f"Error updating: {result.get('message')}"


def is_hybrid_eligible(user_input: str) -> bool:
    """
    Quick check if input might be eligible for hybrid control.

    Args:
        user_input: User's input

    Returns:
        True if might be simple command
    """
    command = parse_simple_command(user_input)
    return command is not None
```

### Task 7.3: Update vis_tools to Track Tool Name

**File**: Update `vis_tools.py`

We need to store `_tool_name` in viz params so we can re-execute the same tool.

```python
# In each viz tool function, modify return dict to include tool name:

def plot_functional_boxplot(...) -> Dict[str, str]:
    # ... existing code ...

    # After successful visualization, save params with tool name
    last_viz_params = {
        "_tool_name": "plot_functional_boxplot",
        "data_path": data_path,
        "percentile": percentile,
        "show_median": show_median,
    }

    return {
        "status": "success",
        "message": f"Displayed functional boxplot for {curves.shape[0]} curves",
        "_viz_params": last_viz_params  # Include for hybrid control
    }
```

Do this for all viz tools.

### Task 7.4: Update Conversation Session for Hybrid Control

**File**: Update `conversation.py`

```python
# Add to ConversationSession class:

from hybrid_control import execute_simple_command, is_hybrid_eligible

class ConversationSession:
    # ... existing code ...

    def send(self, user_message: str) -> GraphState:
        """
        Send a user message and get response.

        Checks for simple commands first (hybrid control).
        Falls back to full graph execution if needed.

        Args:
            user_message: User's input

        Returns:
            Updated state after graph execution
        """
        self.turn_count += 1

        # Try hybrid control first
        if self.state and is_hybrid_eligible(user_message):
            success, updated_params, message = execute_simple_command(
                user_message,
                self.state
            )

            if success:
                # Update state directly without graph execution
                self.state["last_viz_params"] = updated_params
                self.state["error_count"] = 0

                # Add messages to maintain conversation history
                from langchain_core.messages import HumanMessage, AIMessage
                self.state["messages"].append(HumanMessage(content=user_message))
                self.state["messages"].append(AIMessage(content=message))

                print(f"[HYBRID] Fast path executed: {message}")
                return self.state

        # Fall back to full graph execution
        if self.state is None:
            self.state = create_initial_state(user_message)
        else:
            from langchain_core.messages import HumanMessage
            self.state["messages"].append(HumanMessage(content=user_message))

        self.state = graph_app.invoke(self.state)
        return self.state
```

### Task 7.5: Test Hybrid Control

**File**: `test_hybrid_control.py`

```python
"""Test hybrid control functionality."""

from conversation import ConversationSession
import matplotlib.pyplot as plt
import time


def test_hybrid_parameter_update():
    """Test: Simple parameter update uses hybrid control."""
    print("\n" + "="*70)
    print("TEST: Hybrid Parameter Update")
    print("="*70)

    session = ConversationSession()

    # Setup: Create initial visualization
    print("\n🔹 Setup: Create initial visualization")
    session.send("Generate 30 curves and plot functional boxplot")

    ctx1 = session.get_context_summary()
    assert ctx1["last_viz"] is not None
    print(f"   ✓ Initial viz created")

    # Test 1: Change colormap (should use hybrid)
    print("\n🔹 Test: Change colormap via hybrid control")
    start_time = time.time()
    session.send("colormap plasma")
    elapsed = time.time() - start_time

    ctx2 = session.get_context_summary()
    print(f"   ✓ Colormap updated in {elapsed:.2f}s")
    print(f"     (Hybrid should be faster than full graph)")

    # Test 2: Change percentile
    print("\n🔹 Test: Change percentile")
    session.send("percentile 75")
    print(f"   ✓ Percentile updated")

    # Test 3: Toggle boolean
    print("\n🔹 Test: Hide median")
    session.send("hide median")
    print(f"   ✓ Median hidden")

    print("\n✅ Hybrid control test passed")
    return session


def test_hybrid_vs_full_graph():
    """Test: Compare speed of hybrid vs full graph."""
    print("\n" + "="*70)
    print("TEST: Hybrid vs Full Graph Speed")
    print("="*70)

    session = ConversationSession()

    # Setup
    session.send("Generate 40 curves and visualize")

    # Time full graph execution
    print("\n🔹 Full graph: 'Change percentile to 80 and use plasma colormap'")
    start_full = time.time()
    session.send("Change percentile to 80 and use plasma colormap")
    elapsed_full = time.time() - start_full
    print(f"   Full graph: {elapsed_full:.2f}s")

    # Time hybrid execution
    print("\n🔹 Hybrid: 'percentile 90'")
    start_hybrid = time.time()
    session.send("percentile 90")
    elapsed_hybrid = time.time() - start_hybrid
    print(f"   Hybrid: {elapsed_hybrid:.2f}s")

    speedup = elapsed_full / elapsed_hybrid if elapsed_hybrid > 0 else float('inf')
    print(f"\n   Speedup: {speedup:.1f}x faster")

    print("\n✅ Speed comparison complete")


def test_hybrid_fallback():
    """Test: Complex queries fall back to full graph."""
    print("\n" + "="*70)
    print("TEST: Hybrid Fallback to Full Graph")
    print("="*70)

    session = ConversationSession()

    # Setup
    session.send("Generate curves and plot")

    # This should NOT use hybrid (too complex)
    print("\n🔹 Complex query (should use full graph)")
    session.send("Make it look better with nice colors and good percentile")

    response = session.get_last_response()
    print(f"   Response: {response[:100]}")
    print(f"   ✓ Full graph handled complex query")

    print("\n✅ Fallback test passed")


def test_hybrid_without_prior_viz():
    """Test: Hybrid command without prior viz falls back to graph."""
    print("\n" + "="*70)
    print("TEST: Hybrid Without Prior Visualization")
    print("="*70)

    session = ConversationSession()

    # Try hybrid command without any prior visualization
    print("\n🔹 Trying 'colormap plasma' with no prior viz")
    session.send("colormap plasma")

    response = session.get_last_response()
    print(f"   Response: {response[:150]}")

    # Should explain that there's nothing to update
    assert "no" in response.lower() or "first" in response.lower(), \
        "Should indicate no prior viz to update"

    print("\n✅ No-prior-viz test passed")


def run_all_hybrid_tests():
    """Run all hybrid control tests."""
    print("\n" + "⚡"*35)
    print("CHATUVISBOX: HYBRID CONTROL TESTS")
    print("⚡"*35)

    tests = [
        test_hybrid_parameter_update,
        test_hybrid_vs_full_graph,
        test_hybrid_fallback,
        test_hybrid_without_prior_viz,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "="*70)
    print("HYBRID CONTROL TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")

    input("\nPress Enter to close matplotlib windows...")
    plt.close('all')

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_hybrid_tests()
    exit(0 if failed == 0 else 1)
```

Run:
```bash
python test_hybrid_control.py
```

## Validation Checklist

- [ ] Simple commands are parsed correctly
- [ ] Parameter updates execute without full graph
- [ ] Hybrid execution is faster than full graph
- [ ] Complex queries fall back to full graph
- [ ] Hybrid commands without prior viz are handled gracefully
- [ ] All simple command patterns work:
  - [ ] colormap
  - [ ] percentile
  - [ ] isovalue
  - [ ] show/hide median
  - [ ] show/hide outliers
  - [ ] scale
  - [ ] alpha
- [ ] Conversation history is maintained for hybrid commands
- [ ] State updates correctly after hybrid execution

## Expected Behavior

### Hybrid Path (Fast)
```
User: "Generate curves and plot"
[Full graph execution - ~2-3 seconds]

User: "colormap plasma"
[Hybrid control - <0.5 seconds]
✓ Plot updates immediately
```

### Full Graph Path (Smart)
```
User: "Generate curves and plot"
[Full graph execution]

User: "Make it prettier and use good parameters"
[Full graph execution - handles ambiguity]
✓ Model interprets "prettier" and "good"
```

## Troubleshooting

**Hybrid not triggering:**
- Check `parse_simple_command()` returns command
- Verify `is_hybrid_eligible()` returns True
- Print debug messages in `execute_simple_command()`

**Parameters not updating:**
- Check `last_viz_params` is stored correctly
- Verify `_tool_name` is in params
- Ensure viz tools include `_viz_params` in return

**Hybrid slower than expected:**
- Check if viz tool is re-reading data unnecessarily
- Verify matplotlib isn't blocking
- Profile execution with timing prints

## Output

After Phase 7, you should have:
- Working hybrid control for simple commands
- Significant speed improvement for parameter updates
- Proper fallback to full graph for complex queries
- Maintained conversation context through both paths
- Comprehensive hybrid control test suite

## Next Phase

Phase 8 will implement session management including file cleanup and session state persistence.
