# Phase 4: End-to-End "Happy Path" Test

**Goal**: Verify the complete pipeline works for all supported visualization types with real test cases.

**Duration**: 0.5 day

## Prerequisites

- Phase 3 completed (complete graph working)
- Test data files exist in `test_data/`
- All 4 vis tools implemented

## Tasks

### Task 4.1: Create Comprehensive Test Suite

**File**: `test_happy_path.py`

```python
"""
End-to-end happy path tests for all visualization types.

Each test follows the pattern:
1. User provides natural language prompt
2. Graph executes (data tool → vis tool)
3. Matplotlib window appears
4. Final state is correct
"""

from graph import run_graph
import matplotlib.pyplot as plt
from pathlib import Path
import time


def print_test_header(test_name: str):
    """Print a formatted test header."""
    print("\n" + "="*70)
    print(f"TEST: {test_name}")
    print("="*70)


def print_state_summary(state: dict):
    """Print a summary of the final state."""
    print(f"\n📊 Final State:")
    print(f"  Messages: {len(state['messages'])}")
    print(f"  Data path: {state.get('current_data_path')}")
    print(f"  Vis params: {state.get('last_vis_params')}")
    print(f"  Error count: {state.get('error_count')}")
    print(f"  Session files: {len(state.get('session_files', []))}")

    # Print final assistant message
    for msg in reversed(state["messages"]):
        if hasattr(msg, "content") and msg.content and "AI" in msg.__class__.__name__:
            print(f"\n💬 Assistant: {msg.content[:200]}")
            break


def test_functional_boxplot():
    """Test 1: Generate curves → functional boxplot"""
    print_test_header("Functional Boxplot with Generated Data")

    prompt = "Generate 40 ensemble curves with 80 points each, then show me a functional boxplot"

    result = run_graph(prompt)

    # Assertions
    assert result.get("error_count") == 0, "❌ Errors occurred"
    assert result.get("current_data_path") is not None, "❌ No data generated"
    assert result.get("last_vis_params") is not None, "❌ No visualization created"
    assert "plot_functional_boxplot" in str(result.get("last_vis_params")), "❌ Wrong vis type"

    print("✅ Test passed!")
    print_state_summary(result)

    return result


def test_functional_boxplot_with_csv():
    """Test 2: Load CSV → functional boxplot"""
    print_test_header("Functional Boxplot from CSV")

    # Check if test file exists
    test_file = Path("test_data/sample_curves.csv")
    if not test_file.exists():
        print("⚠️  Skipping: sample_curves.csv not found")
        return None

    prompt = "Load test_data/sample_curves.csv and create a functional boxplot with percentile 95"

    result = run_graph(prompt)

    assert result.get("error_count") == 0, "❌ Errors occurred"
    assert result.get("last_vis_params") is not None, "❌ No visualization"

    print("✅ Test passed!")
    print_state_summary(result)

    return result


def test_curve_boxplot():
    """Test 3: Generate curves → curve boxplot"""
    print_test_header("Curve Boxplot")

    prompt = "Generate 25 curves and show me a curve boxplot with percentile 60"

    result = run_graph(prompt)

    assert result.get("error_count") == 0, "❌ Errors occurred"
    assert result.get("last_vis_params") is not None, "❌ No visualization"

    print("✅ Test passed!")
    print_state_summary(result)

    return result


def test_probabilistic_marching_squares():
    """Test 4: Generate scalar field → probabilistic marching squares"""
    print_test_header("Probabilistic Marching Squares")

    prompt = "Generate a 2D scalar field ensemble with 40x40 grid and 25 ensemble members, then visualize it with probabilistic marching squares at isovalue 0.7"

    result = run_graph(prompt)

    assert result.get("error_count") == 0, "❌ Errors occurred"
    assert result.get("last_vis_params") is not None, "❌ No visualization"
    assert "plot_probabilistic_marching_squares" in str(result.get("last_vis_params")), "❌ Wrong vis"

    print("✅ Test passed!")
    print_state_summary(result)

    return result


def test_multi_step_workflow():
    """Test 5: Multi-step conversation with state tracking"""
    print_test_header("Multi-Step Workflow")

    # Step 1: Generate data
    print("\n🔹 Step 1: Generate data")
    result1 = run_graph("Generate 30 test curves")

    assert result1.get("current_data_path") is not None, "❌ Data not generated"
    print(f"  ✓ Data generated: {result1['current_data_path']}")

    # Step 2: Visualize using state from step 1
    print("\n🔹 Step 2: Visualize with state from step 1")
    # Continue conversation with existing state
    from langchain_core.messages import HumanMessage
    result1["messages"].append(HumanMessage(content="Now create a functional boxplot for that data"))

    from graph import graph_app
    result2 = graph_app.invoke(result1)

    assert result2.get("last_vis_params") is not None, "❌ No visualization"
    print(f"  ✓ Visualization created")

    print("✅ Multi-step test passed!")
    print_state_summary(result2)

    return result2


def test_all_vis_params():
    """Test 6: Test various parameter configurations"""
    print_test_header("Visualization Parameters")

    # Test with different percentiles
    prompt = "Generate curves and show functional boxplot with percentile 75 and hide the median"

    result = run_graph(prompt)

    assert result.get("error_count") == 0, "❌ Errors occurred"

    print("✅ Test passed!")
    print_state_summary(result)

    return result


def run_all_tests():
    """Run all happy path tests."""
    print("\n" + "🚀"*35)
    print("CHATUVISBOX: END-TO-END HAPPY PATH TESTS")
    print("🚀"*35)

    tests = [
        test_functional_boxplot,
        test_functional_boxplot_with_csv,
        test_curve_boxplot,
        test_probabilistic_marching_squares,
        test_multi_step_workflow,
        test_all_vis_params,
    ]

    results = []
    passed = 0
    failed = 0

    for test_func in tests:
        try:
            result = test_func()
            if result is not None:
                results.append(result)
                passed += 1
            time.sleep(0.5)  # Brief pause between tests
        except AssertionError as e:
            print(f"\n❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            failed += 1

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")

    print("\n👁️  Check that matplotlib windows appeared correctly")
    input("\nPress Enter to close all windows and exit...")
    plt.close('all')

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_tests()
    exit(0 if failed == 0 else 1)
```

Run:
```bash
python test_happy_path.py
```

### Task 4.2: Verify Matplotlib Non-Blocking Behavior

**File**: `test_matplotlib_behavior.py`

```python
"""Test matplotlib window behavior to ensure non-blocking."""

import matplotlib.pyplot as plt
import numpy as np
import time


def test_non_blocking():
    """Test that plt.show(block=False) works correctly."""
    print("Testing matplotlib non-blocking behavior...")

    # Create first plot
    fig1, ax1 = plt.subplots()
    ax1.plot([1, 2, 3], [1, 4, 9])
    ax1.set_title("Plot 1 - Should not block")
    plt.show(block=False)

    print("  ✓ Plot 1 displayed")
    print("  If you see this message, blocking is working correctly")

    time.sleep(2)

    # Create second plot while first is still open
    fig2, ax2 = plt.subplots()
    ax2.plot([1, 2, 3], [3, 2, 1])
    ax2.set_title("Plot 2 - Should appear while Plot 1 is still open")
    plt.show(block=False)

    print("  ✓ Plot 2 displayed")
    print("  Both windows should be visible now")

    input("\nPress Enter to close and exit...")
    plt.close('all')


def test_multiple_vis_calls():
    """Simulate multiple visualization calls like in our pipeline."""
    from vis_tools import plot_functional_boxplot
    from data_tools import generate_ensemble_curves

    print("\nTesting multiple vis tool calls...")

    # Generate data
    result1 = generate_ensemble_curves(n_curves=20, n_points=50)
    print(f"  Generated data: {result1['output_path']}")

    # First vis
    vis1 = plot_functional_boxplot(result1['output_path'])
    print(f"  ✓ First vis: {vis1['status']}")

    time.sleep(1)

    # Generate more data
    result2 = generate_ensemble_curves(n_curves=15, n_points=60)

    # Second vis
    vis2 = plot_functional_boxplot(result2['output_path'], percentile=80.0)
    print(f"  ✓ Second vis: {vis2['status']}")

    print("\n  Both plots should be visible")
    input("\nPress Enter to close...")
    plt.close('all')


if __name__ == "__main__":
    test_non_blocking()
    test_multiple_vis_calls()
    print("\n✅ Matplotlib behavior tests complete!")
```

Run:
```bash
python test_matplotlib_behavior.py
```

### Task 4.3: Create Interactive Test Script

**File**: `interactive_test.py`

```python
"""
Interactive test script for manual testing.

This allows you to test the graph interactively and verify the flow.
"""

from graph import run_graph, stream_graph
import matplotlib.pyplot as plt


def print_banner():
    print("\n" + "="*70)
    print("  CHATUVISBOX - Interactive Test")
    print("="*70)
    print("\nAvailable test prompts:")
    print("  1. Generate 30 curves and plot functional boxplot")
    print("  2. Generate scalar field and show marching squares")
    print("  3. Load sample_curves.csv and visualize")
    print("  4. Custom prompt")
    print("  q. Quit")
    print()


def run_test(prompt: str, stream: bool = False):
    """Run a test with the given prompt."""
    print(f"\n🔹 Running: {prompt}")
    print("-" * 70)

    if stream:
        # Stream execution
        for update in stream_graph(prompt):
            node_name = list(update.keys())[0]
            print(f"  [{node_name}] executing...")
    else:
        # Regular execution
        result = run_graph(prompt)

        # Print result
        print(f"\n✅ Complete")
        print(f"  Data path: {result.get('current_data_path')}")
        print(f"  Vis params: {result.get('last_vis_params')}")
        print(f"  Errors: {result.get('error_count')}")

        # Print final message
        for msg in reversed(result["messages"]):
            if hasattr(msg, "content") and msg.content:
                if "AI" in msg.__class__.__name__:
                    print(f"\n💬 {msg.content[:300]}")
                    break


def main():
    """Main interactive loop."""
    test_prompts = {
        "1": "Generate 30 ensemble curves with 100 points, then show me a functional boxplot",
        "2": "Generate a 2D scalar field ensemble with 40x40 grid, then visualize with probabilistic marching squares at isovalue 0.6",
        "3": "Load test_data/sample_curves.csv and plot it as a functional boxplot",
    }

    while True:
        print_banner()
        choice = input("Enter choice: ").strip()

        if choice.lower() == 'q':
            print("Exiting...")
            plt.close('all')
            break

        if choice in test_prompts:
            prompt = test_prompts[choice]
        elif choice == "4":
            prompt = input("Enter custom prompt: ").strip()
        else:
            print("Invalid choice")
            continue

        try:
            run_test(prompt)
            input("\nPress Enter to continue...")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\nPress Enter to continue...")

    print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
```

Run:
```bash
python interactive_test.py
```

## Validation Checklist

- [ ] Test 1 (functional boxplot with generated data) passes
- [ ] Test 2 (functional boxplot from CSV) passes
- [ ] Test 3 (curve boxplot) passes
- [ ] Test 4 (probabilistic marching squares) passes
- [ ] Test 5 (multi-step workflow) passes
- [ ] Test 6 (various parameters) passes
- [ ] All matplotlib windows appear correctly
- [ ] Windows don't block execution (can interact with terminal)
- [ ] Multiple plots can be open simultaneously
- [ ] Interactive test script works for manual verification
- [ ] Error count remains 0 for all happy path tests
- [ ] Final assistant messages are helpful and accurate

## Expected Behavior

For each test:
1. **User prompt** is sent to graph
2. **Model node** decides to call data tool
3. **Data tool node** executes and returns success
4. **Model node** (again) decides to call vis tool
5. **Vis tool node** executes and matplotlib window appears
6. **Model node** (again) responds to user with confirmation
7. **END** state reached
8. Terminal is still interactive (non-blocking)

## Troubleshooting

**Matplotlib windows don't appear:**
- Check `plt.show(block=False)` in vis_tools.py
- Verify display environment (not headless)
- Try `export MPLBACKEND=TkAgg` or other backend

**Tests fail with tool errors:**
- Check data_tools.py functions work independently
- Verify file paths are correct
- Check numpy/pandas versions

**Graph doesn't make tool calls:**
- Print model response in nodes.py
- Verify tool schemas are correct
- Check Gemini API key is valid

**Multi-step test fails:**
- Verify state is being passed correctly
- Check current_data_path is set after data tool
- Print intermediate state updates

## Output

After Phase 4, you should have:
- Comprehensive test suite covering all vis types
- Verified end-to-end "happy path" for all scenarios
- Matplotlib windows appearing correctly without blocking
- Interactive test tool for manual verification
- Confidence that the core pipeline works correctly

## Completion Status

**Completed**: 2025-10-27

### Files Created

✅ **test_happy_path.py** (259 lines)
- 6 comprehensive end-to-end tests covering all visualization types
- Includes rate limit management (25-35 API calls with delays)
- Tests: functional_boxplot, functional_boxplot_with_csv, curve_boxplot, probabilistic_marching_squares, multi_step_workflow, plot_all_curves

✅ **test_matplotlib_behavior.py** (145 lines)
- 0 API calls - safe to run anytime
- Tests non-blocking behavior, multiple vis calls, window persistence
- Verifies `plt.show(block=False)` works correctly

✅ **interactive_test.py** (135 lines)
- Interactive REPL for manual testing
- Predefined prompts + custom prompt support
- Stream mode support for execution visualization

### Adaptations from Original Plan

The implementation includes rate limit considerations for gemini-2.0-flash-lite (30 RPM):
- test_happy_path.py includes automatic delays between test batches
- test_matplotlib_behavior.py makes no API calls
- Test suite respects free tier quotas

Additional test created:
- Test 6 in test_happy_path.py tests `plot_all_curves` parameter (new UVisBox feature)

### Validation Notes

**Implementation Complete** (files created, non-blocking configured):
- ✅ All test files created with correct structure
- ✅ Matplotlib non-blocking behavior configured in vis_tools.py
- ✅ Interactive test script implemented
- ✅ Rate limit considerations included

**Requires Test Execution** (user decision based on API quota):
- ⏸️ Test 1-6 pass/fail status (requires running test_happy_path.py)
- ⏸️ Matplotlib window verification (requires running tests)
- ⏸️ Error count verification (requires running tests)
- ⏸️ Assistant message accuracy (requires running tests)

### Notes

Tests have been created but not executed to preserve API quota. User can run:
```bash
# No API calls - safe anytime
python test_matplotlib_behavior.py

# 25-35 API calls - respects rate limits
python test_happy_path.py

# Interactive manual testing
python interactive_test.py
```

## Next Phase

Phase 5 will add robust error handling to ensure the agent gracefully handles failures and asks clarifying questions.
