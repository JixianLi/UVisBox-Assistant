"""Test error handling and recovery."""
import sys
from pathlib import Path

from chatuvisbox.graph import run_graph, graph_app
from chatuvisbox.routing import route_after_tool
from chatuvisbox.state import create_initial_state
import matplotlib.pyplot as plt


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
    assert final_msg is not None, "No assistant response found"
    assert "not found" in final_msg.lower() or "doesn't exist" in final_msg.lower() or "error" in final_msg.lower() or "cannot" in final_msg.lower() or "couldn't" in final_msg.lower(), \
        "Agent should acknowledge the file error"

    print("\n✅ Agent correctly handled file not found error")


def test_wrong_data_shape():
    """Test: Generate data then try to use with wrong visualization."""
    print("\n" + "="*70)
    print("TEST: Wrong Data Shape Error")
    print("="*70)

    # Generate scalar field data (3D array)
    prompt = "Generate a 20x20 scalar field ensemble with 10 members"
    result1 = run_graph(prompt)

    print(f"\nStep 1: Generated scalar field")
    print(f"  Data path: {result1.get('current_data_path')}")

    # Now try to use it with functional_boxplot (which expects 2D curve data)
    from langchain_core.messages import HumanMessage
    result1["messages"].append(
        HumanMessage(content="Now plot that data as a functional boxplot")
    )

    result2 = graph_app.invoke(result1)

    print("\nStep 2: Tried to use scalar field with functional boxplot")

    # Check final assistant message
    final_msg = None
    for msg in reversed(result2["messages"]):
        if hasattr(msg, "content") and "AI" in msg.__class__.__name__ and msg.content:
            final_msg = msg.content
            break

    print(f"\n💬 Assistant response:\n{final_msg}")

    # Verify agent provides a helpful response about the issue
    assert final_msg is not None, "No assistant response found"

    # Agent should either:
    # 1. Show an error message, OR
    # 2. Generate appropriate data instead, OR
    # 3. Explain the incompatibility
    # Any of these is acceptable - the test just verifies the agent doesn't crash

    print("\n✅ Agent handled incompatible data/visualization request")


def test_clarifying_question():
    """Test: Ambiguous request that should trigger clarifying question."""
    print("\n" + "="*70)
    print("TEST: Ambiguous Request")
    print("="*70)

    # Create multiple CSV files
    import pandas as pd

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
    # Any of these is acceptable

    print("\n✅ Agent handled ambiguous request")

    # Cleanup test files
    if csv1.exists():
        csv1.unlink()
    if csv2.exists():
        csv2.unlink()


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
    print("\nNote: These tests make API calls and may take several minutes.")
    print("Tests are spaced to respect rate limits.\n")

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

    for i, test_func in enumerate(tests, 1):
        try:
            test_func()
            passed += 1

            # Add delay between tests to respect rate limits
            if i < len(tests):
                import time
                if test_func.__name__ != "test_circuit_breaker":  # Skip delay for non-API test
                    print("\n⏳ Pausing 3s to respect rate limits...")
                    time.sleep(3)
        except AssertionError as e:
            print(f"\n❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Close any matplotlib windows
    plt.close('all')

    # Summary
    print("\n" + "="*70)
    print("ERROR HANDLING TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print("\n🎉 All error handling tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_error_tests()
    sys.exit(0 if failed == 0 else 1)
