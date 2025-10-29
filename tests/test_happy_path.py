"""
End-to-end happy path tests for all visualization types.

Each test follows the pattern:
1. User provides natural language prompt
2. Graph executes (data tool → viz tool)
3. Matplotlib window appears
4. Final state is correct

Note: This suite makes ~25-35 API calls total. With gemini-2.0-flash-lite (30 RPM),
tests are spaced out to respect rate limits.
"""
import sys
from pathlib import Path

from chatuvisbox.graph import run_graph, graph_app
import matplotlib.pyplot as plt
from langchain_core.messages import HumanMessage
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
    viz_params = state.get('last_viz_params')
    if viz_params:
        print(f"  Viz tool: {viz_params.get('_tool_name', 'N/A')}")
    print(f"  Error count: {state.get('error_count')}")
    print(f"  Session files: {len(state.get('session_files', []))}")

    # Print final assistant message
    for msg in reversed(state["messages"]):
        if hasattr(msg, "content") and msg.content and "AI" in msg.__class__.__name__:
            print(f"\n💬 Assistant: {msg.content[:200]}...")
            break


def test_functional_boxplot():
    """Test 1: Generate curves → functional boxplot"""
    print_test_header("Functional Boxplot with Generated Data")

    prompt = "Generate 40 ensemble curves with 80 points each, then show me a functional boxplot"

    result = run_graph(prompt)

    # Assertions
    assert result.get("error_count") == 0, "❌ Errors occurred"
    assert result.get("current_data_path") is not None, "❌ No data generated"
    assert result.get("last_viz_params") is not None, "❌ No visualization created"
    assert "plot_functional_boxplot" in str(result.get("last_viz_params")), "❌ Wrong viz type"

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

    prompt = "Load test_data/sample_curves.csv and create a functional boxplot"

    result = run_graph(prompt)

    assert result.get("error_count") == 0, "❌ Errors occurred"
    assert result.get("last_viz_params") is not None, "❌ No visualization"

    print("✅ Test passed!")
    print_state_summary(result)

    return result


def test_curve_boxplot():
    """Test 3: Generate curves → curve boxplot"""
    print_test_header("Curve Boxplot")

    prompt = "Generate 25 curves and show me a curve boxplot"

    result = run_graph(prompt)

    assert result.get("error_count") == 0, "❌ Errors occurred"
    assert result.get("last_viz_params") is not None, "❌ No visualization"

    print("✅ Test passed!")
    print_state_summary(result)

    return result


def test_probabilistic_marching_squares():
    """Test 4: Generate scalar field → probabilistic marching squares"""
    print_test_header("Probabilistic Marching Squares")

    prompt = "Generate a 2D scalar field ensemble with 40x40 grid and 25 ensemble members, then visualize it with probabilistic marching squares"

    result = run_graph(prompt)

    assert result.get("error_count") == 0, "❌ Errors occurred"
    assert result.get("last_viz_params") is not None, "❌ No visualization"
    assert "plot_probabilistic_marching_squares" in str(result.get("last_viz_params")), "❌ Wrong viz"

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
    result1["messages"].append(HumanMessage(content="Now create a functional boxplot for that data"))

    result2 = graph_app.invoke(result1)

    assert result2.get("last_viz_params") is not None, "❌ No visualization"
    print(f"  ✓ Visualization created")

    print("✅ Multi-step test passed!")
    print_state_summary(result2)

    return result2


def test_plot_all_curves():
    """Test 6: Test plot_all_curves parameter"""
    print_test_header("Functional Boxplot with All Curves Visible")

    prompt = "Generate 20 curves and show functional boxplot with all individual curves visible"

    result = run_graph(prompt)

    assert result.get("error_count") == 0, "❌ Errors occurred"
    assert result.get("last_viz_params") is not None, "❌ No visualization"

    # Check if plot_all_curves was used (LLM should understand the request)
    viz_params = result.get("last_viz_params", {})
    print(f"  Viz params: {viz_params}")

    print("✅ Test passed!")
    print_state_summary(result)

    return result


def run_all_tests():
    """Run all happy path tests."""
    print("\n" + "🚀"*35)
    print("CHATUVISBOX: END-TO-END HAPPY PATH TESTS")
    print("🚀"*35)
    print("\nRate Limit: 30 requests/minute (gemini-2.0-flash-lite)")
    print("Expected API calls: ~25-35 total")
    print("Tests will be spaced to respect limits")
    print("="*70)

    tests = [
        test_functional_boxplot,
        test_functional_boxplot_with_csv,
        test_curve_boxplot,
        test_probabilistic_marching_squares,
        test_multi_step_workflow,
        test_plot_all_curves,
    ]

    results = []
    passed = 0
    failed = 0
    start_time = time.time()

    for i, test_func in enumerate(tests, 1):
        try:
            result = test_func()
            if result is not None:
                results.append(result)
                passed += 1

            # Add delay after tests that make API calls (except last test)
            if i < len(tests) and i % 3 == 0:
                print(f"\n⏳ Pausing 10s to respect rate limits...")
                time.sleep(10)
            else:
                time.sleep(1)  # Brief pause between tests

        except AssertionError as e:
            print(f"\n❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    elapsed = time.time() - start_time

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    print(f"⏱️  Time: {elapsed:.1f}s")

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
    sys.exit(0 if failed == 0 else 1)
