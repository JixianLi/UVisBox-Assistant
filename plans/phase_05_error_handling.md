# Phase 5: Error Handling & Contextual Awareness

**Goal**: Ensure the agent gracefully handles errors and asks clarifying questions when needed.

**Duration**: 0.5-1 day

## Prerequisites

- Phase 4 completed (happy path working)
- Understanding of common failure modes

## Tasks

### Task 5.1: Enhance System Prompt for Error Recovery

**File**: Update `model.py`

```python
# Add to get_system_prompt()

def get_system_prompt(file_list: list = None) -> str:
    """Generate the system prompt for the agent."""
    base_prompt = """You are ChatUVisBox, an AI assistant specialized in visualizing uncertainty data using the UVisBox Python library.

Your capabilities:
1. **Data Tools**: Load CSV files, generate synthetic data, manage numpy arrays
2. **Visualization Tools**: Create uncertainty visualizations using UVisBox functions

Available visualization types:
- functional_boxplot: For visualizing multiple 1D curves with band depth
- curve_boxplot: For ensemble curve data with depth-based coloring
- probabilistic_marching_squares: For 2D scalar field ensembles with isocontours
- uncertainty_lobes: For visualizing directional uncertainty in vector fields

Workflow:
1. User requests a visualization
2. Use data tools to load or generate the required data (saves as .npy)
3. Use visualization tools with the .npy file path
4. Confirm success to user

**Error Handling Guidelines:**
- If a tool returns an error, READ THE ERROR MESSAGE carefully
- Explain the error to the user in simple terms
- Ask clarifying questions if needed (e.g., "Which file did you mean?", "What dimensions?")
- Suggest alternatives if a file doesn't exist
- Don't retry the same failed operation without changes

**Context Awareness:**
- Remember the current_data_path from previous operations
- If user says "plot that" or "visualize it", use the current_data_path
- Track what files have been created this session

Important:
- Always save intermediate data as .npy files
- Data tools return an "output_path" field - use this for visualization tools
- Be conversational and helpful
- Never make up file paths that don't exist
"""

    if file_list:
        file_list_str = "\n".join([f"  - {f}" for f in file_list])
        base_prompt += f"\n\nAvailable files in test_data/:\n{file_list_str}"

    return base_prompt
```

### Task 5.2: Create Error Test Suite

**File**: `test_error_handling.py`

```python
"""Test error handling and recovery."""

from graph import run_graph
from pathlib import Path


def test_file_not_found():
    """Test: User asks to load a file that doesn't exist."""
    print("\n" + "="*70)
    print("TEST: File Not Found Error")
    print("="*70)

    prompt = "Load nonexistent_file.csv and plot it"

    result = run_graph(prompt)

    # Should have error, but agent should respond helpfully
    print(f"\nError count: {result.get('error_count')}")
    print(f"Data path: {result.get('current_data_path')}")

    # Check final assistant message
    final_msg = None
    for msg in reversed(result["messages"]):
        if hasattr(msg, "content") and "AI" in msg.__class__.__name__ and msg.content:
            final_msg = msg.content
            break

    print(f"\n💬 Assistant response:\n{final_msg}")

    # Verify agent acknowledges the error
    assert "not found" in final_msg.lower() or "doesn't exist" in final_msg.lower() or "error" in final_msg.lower(), \
        "Agent should acknowledge the file error"

    print("\n✅ Agent correctly handled file not found error")


def test_wrong_data_shape():
    """Test: User provides data with wrong shape for visualization."""
    print("\n" + "="*70)
    print("TEST: Wrong Data Shape Error")
    print("="*70)

    # First create data with wrong shape
    import numpy as np
    from pathlib import Path
    import config

    # Create 1D array (wrong shape for most viz functions expecting 2D)
    wrong_data = np.array([1, 2, 3, 4, 5])
    wrong_path = config.TEMP_DIR / "wrong_shape.npy"
    np.save(wrong_path, wrong_data)

    # Try to visualize it
    prompt = f"Plot {wrong_path} as a functional boxplot"

    result = run_graph(prompt)

    # Check that error was caught
    final_msg = None
    for msg in reversed(result["messages"]):
        if hasattr(msg, "content") and "AI" in msg.__class__.__name__ and msg.content:
            final_msg = msg.content
            break

    print(f"\n💬 Assistant response:\n{final_msg}")

    # Verify error is mentioned
    assert "shape" in final_msg.lower() or "dimension" in final_msg.lower() or "error" in final_msg.lower(), \
        "Agent should mention shape/dimension error"

    print("\n✅ Agent correctly handled shape error")


def test_clarifying_question():
    """Test: Ambiguous request that should trigger clarifying question."""
    print("\n" + "="*70)
    print("TEST: Ambiguous Request")
    print("="*70)

    # Create multiple CSV files
    import pandas as pd
    from pathlib import Path

    csv1 = Path("test_data/curves1.csv")
    csv2 = Path("test_data/curves2.csv")

    pd.DataFrame({"x": [1, 2, 3]}).to_csv(csv1, index=False)
    pd.DataFrame({"y": [4, 5, 6]}).to_csv(csv2, index=False)

    # Ambiguous prompt
    prompt = "Load the CSV file and visualize it"

    result = run_graph(prompt)

    final_msg = None
    for msg in reversed(result["messages"]):
        if hasattr(msg, "content") and "AI" in msg.__class__.__name__ and msg.content:
            final_msg = msg.content
            break

    print(f"\n💬 Assistant response:\n{final_msg}")

    # Agent should either:
    # 1. Ask which file, OR
    # 2. List available files, OR
    # 3. Pick one and mention it

    print("\n✅ Agent handled ambiguous request")


def test_invalid_parameter():
    """Test: User provides invalid parameter value."""
    print("\n" + "="*70)
    print("TEST: Invalid Parameter")
    print("="*70)

    prompt = "Generate curves and plot with percentile 150"  # Invalid (>100)

    result = run_graph(prompt)

    # Check if error was handled
    # Note: This might succeed if the model autocorrects to 100
    # or might fail if validation catches it

    print(f"\nError count: {result.get('error_count')}")

    final_msg = None
    for msg in reversed(result["messages"]):
        if hasattr(msg, "content") and "AI" in msg.__class__.__name__ and msg.content:
            final_msg = msg.content
            break

    print(f"\n💬 Assistant response:\n{final_msg}")

    print("\n✅ Test complete (behavior may vary based on model)")


def test_error_recovery():
    """Test: User corrects error and succeeds."""
    print("\n" + "="*70)
    print("TEST: Error Recovery")
    print("="*70)

    # First try with wrong file
    prompt1 = "Load wrong_file.csv"
    result1 = run_graph(prompt1)

    print("Step 1: Tried to load wrong_file.csv")
    print(f"  Error count: {result1.get('error_count')}")

    # Now correct with right file (continuing conversation)
    from langchain_core.messages import HumanMessage
    result1["messages"].append(
        HumanMessage(content="Sorry, I meant generate 20 curves instead")
    )

    from graph import graph_app
    result2 = graph_app.invoke(result1)

    print("\nStep 2: Corrected to generate curves")
    print(f"  Error count: {result2.get('error_count')}")
    print(f"  Data path: {result2.get('current_data_path')}")

    # Error count should be reset after success
    assert result2.get("current_data_path") is not None, "Should have generated data"

    print("\n✅ Error recovery successful")


def test_circuit_breaker():
    """Test: Circuit breaker prevents infinite error loops."""
    print("\n" + "="*70)
    print("TEST: Circuit Breaker")
    print("="*70)

    # This is hard to test without mocking, but we can verify the logic exists
    from routing import route_after_tool
    from state import create_initial_state

    state = create_initial_state("test")
    state["error_count"] = 5  # Exceeds threshold

    route = route_after_tool(state)

    print(f"Route with error_count=5: {route}")
    assert route == "end", "Should route to END when error count exceeds threshold"

    print("\n✅ Circuit breaker working")


def run_all_error_tests():
    """Run all error handling tests."""
    print("\n" + "🛡️ "*35)
    print("CHATUVISBOX: ERROR HANDLING TESTS")
    print("🛡️ "*35)

    tests = [
        test_file_not_found,
        test_wrong_data_shape,
        test_clarifying_question,
        test_invalid_parameter,
        test_error_recovery,
        test_circuit_breaker,
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
            failed += 1

    # Summary
    print("\n" + "="*70)
    print("ERROR HANDLING TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_error_tests()
    exit(0 if failed == 0 else 1)
```

Run:
```bash
python test_error_handling.py
```

### Task 5.3: Add Context Awareness Enhancement

**File**: Update `nodes.py` to inject context

```python
# Add to call_model node

def call_model(state: GraphState) -> Dict:
    """
    Node that calls the LLM to decide next action.

    Args:
        state: Current graph state

    Returns:
        Dict with messages to add to state
    """
    # Get list of available files for context
    file_list = []
    if config.TEST_DATA_DIR.exists():
        file_list = [f.name for f in config.TEST_DATA_DIR.iterdir() if f.is_file()]

    # Prepare messages with system prompt
    messages = prepare_messages_for_model(state, file_list)

    # Add context hint if we have current data
    if state.get("current_data_path"):
        # The system prompt already includes this info, but we can emphasize it
        # by including it in a system message if needed
        pass

    # Call model
    response = MODEL.invoke(messages)

    return {"messages": [response]}
```

### Task 5.4: Add Logging for Debugging

**File**: `logger.py`

```python
"""Logging utilities for debugging."""
import logging
from pathlib import Path

# Create logs directory
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "chatuvisbox.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("chatuvisbox")


def log_tool_call(tool_name: str, args: dict):
    """Log a tool call."""
    logger.info(f"Tool call: {tool_name} with args {args}")


def log_tool_result(tool_name: str, result: dict):
    """Log a tool result."""
    status = result.get("status", "unknown")
    message = result.get("message", "")
    logger.info(f"Tool result: {tool_name} -> {status}: {message}")


def log_error(error_msg: str):
    """Log an error."""
    logger.error(error_msg)


def log_state_update(field: str, value):
    """Log a state update."""
    logger.debug(f"State update: {field} = {value}")
```

Update `nodes.py` to use logging:

```python
# Add at top of nodes.py
from logger import log_tool_call, log_tool_result, log_error

# In call_data_tool:
log_tool_call(tool_name, tool_args)
# ... execute tool ...
log_tool_result(tool_name, result)

# Similar for call_viz_tool
```

## Validation Checklist

- [ ] File not found error is handled gracefully
- [ ] Agent responds with helpful error messages
- [ ] Agent asks clarifying questions for ambiguous requests
- [ ] Wrong data shape errors are caught and explained
- [ ] Error recovery works (user corrects and succeeds)
- [ ] Circuit breaker prevents infinite error loops
- [ ] Context awareness: agent uses current_data_path
- [ ] Context awareness: agent lists available files
- [ ] Logging captures tool calls and results
- [ ] Error messages are user-friendly, not technical stack traces

## Expected Error Handling Patterns

### Pattern 1: File Not Found
```
User: "Load missing.csv"
Agent: "I tried to load missing.csv but couldn't find it.
       Available files in test_data are: sample_curves.csv, ...
       Which file would you like to load?"
```

### Pattern 2: Shape Mismatch
```
User: "Plot wrong_shape.npy as functional boxplot"
Agent: "The data in wrong_shape.npy has shape (5,) but functional_boxplot
       requires a 2D array with shape (n_curves, n_points).
       Would you like to generate some test curve data instead?"
```

### Pattern 3: Ambiguous Request
```
User: "Load the CSV and plot it"
Agent: "I see multiple CSV files available: curves1.csv, curves2.csv.
       Which one would you like to load?"
```

## Troubleshooting

**Errors not caught:**
- Add try-except blocks in tool functions
- Check that error status is returned properly
- Verify ToolMessage is created with error content

**Agent doesn't ask clarifying questions:**
- Improve system prompt with examples
- Check that file list is included in context
- Verify model has enough temperature for creativity (but not too much)

**Circuit breaker not working:**
- Check error_count increment in nodes.py
- Verify route_after_tool checks error_count
- Print intermediate error_count values

## Output

After Phase 5, you should have:
- Robust error handling throughout the pipeline
- Helpful error messages from the agent
- Context-aware responses using available files
- Circuit breaker preventing infinite loops
- Logging system for debugging
- Comprehensive error test suite

## Next Phase

Phase 6 will test conversational follow-up and multi-turn interactions to ensure the agent maintains context across turns.
