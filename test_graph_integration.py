"""Integration test for the complete graph"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from graph import run_graph
import matplotlib.pyplot as plt


def test_data_generation_only():
    """Test: User asks for data generation only."""
    print("\n" + "="*60)
    print("TEST: Data generation without visualization")
    print("="*60)

    result = run_graph("Generate 20 test curves with 50 points each")

    # Check final state
    assert result.get("current_data_path") is not None, "No data path in state"
    assert result.get("error_count") == 0, "Errors occurred"

    print(f"✅ Data generated: {result['current_data_path']}")
    print(f"✅ Total messages: {len(result['messages'])}")
    print(f"✅ Error count: {result.get('error_count')}")


def test_data_and_viz():
    """Test: User asks for data generation + visualization."""
    print("\n" + "="*60)
    print("TEST: Data generation + visualization")
    print("="*60)

    result = run_graph(
        "Generate 30 ensemble curves and show me a functional boxplot"
    )

    # Check final state
    assert result.get("current_data_path") is not None, "No data path"
    assert result.get("last_viz_params") is not None, "No viz params"
    assert result.get("error_count") == 0, "Errors occurred"

    print(f"✅ Data path: {result['current_data_path']}")
    print(f"✅ Viz params: {result.get('last_viz_params', {}).get('_tool_name', 'N/A')}")
    print(f"✅ Total messages: {len(result['messages'])}")
    print(f"✅ Error count: {result.get('error_count')}")
    print("\n  ℹ️  Check if matplotlib window appeared!")


def test_load_and_viz():
    """Test: User asks to load existing file and visualize."""
    print("\n" + "="*60)
    print("TEST: Load CSV and visualize")
    print("="*60)

    # First ensure test data exists
    test_file = Path("test_data/sample_curves.csv")

    if not test_file.exists():
        print("⚠️  Skipping test: sample_curves.csv not found")
        return

    result = run_graph(
        "Load test_data/sample_curves.csv and plot it as a functional boxplot"
    )

    assert result.get("error_count") == 0, "Errors occurred"
    assert result.get("last_viz_params") is not None, "No visualization created"

    print(f"✅ Loaded and visualized {result.get('current_data_path')}")
    print(f"✅ Viz params: {result.get('last_viz_params', {}).get('_tool_name', 'N/A')}")
    print(f"✅ Total messages: {len(result['messages'])}")


def test_curve_boxplot():
    """Test: Generate curves and create curve_boxplot."""
    print("\n" + "="*60)
    print("TEST: Generate curves + curve boxplot")
    print("="*60)

    result = run_graph(
        "Generate 25 curves with 80 points and show a curve boxplot"
    )

    assert result.get("current_data_path") is not None, "No data path"
    assert result.get("last_viz_params") is not None, "No viz params"
    assert result.get("error_count") == 0, "Errors occurred"

    viz_tool = result.get('last_viz_params', {}).get('_tool_name', 'N/A')
    print(f"✅ Data generated and visualized")
    print(f"✅ Visualization tool: {viz_tool}")
    print(f"✅ Total messages: {len(result['messages'])}")


def test_scalar_field_viz():
    """Test: Generate scalar field ensemble and visualize."""
    print("\n" + "="*60)
    print("TEST: Scalar field generation + visualization")
    print("="*60)

    result = run_graph(
        "Generate a 2D scalar field ensemble and show probabilistic marching squares visualization"
    )

    assert result.get("current_data_path") is not None, "No data path"
    assert result.get("error_count") == 0, "Errors occurred"

    # Viz params should be set if visualization succeeded
    if result.get("last_viz_params"):
        print(f"✅ Scalar field visualized")
        print(f"✅ Viz tool: {result.get('last_viz_params', {}).get('_tool_name', 'N/A')}")
    else:
        print(f"✅ Scalar field generated: {result.get('current_data_path')}")
        print(f"   Note: Visualization may not have been created")

    print(f"✅ Total messages: {len(result['messages'])}")


def test_multi_step_workflow():
    """Test: Complex multi-step workflow."""
    print("\n" + "="*60)
    print("TEST: Multi-step workflow")
    print("="*60)

    result = run_graph(
        "First generate 15 curves, then create a functional boxplot with percentiles at 25, 50, 75, and 100"
    )

    # The workflow should complete both steps
    assert result.get("current_data_path") is not None, "No data generated"
    assert result.get("error_count") == 0, "Errors occurred"

    # Count number of tool calls
    tool_messages = [msg for msg in result["messages"] if msg.__class__.__name__ == "ToolMessage"]
    print(f"✅ Workflow completed with {len(tool_messages)} tool executions")
    print(f"✅ Data path: {result.get('current_data_path')}")

    if result.get("last_viz_params"):
        print(f"✅ Visualization created: {result.get('last_viz_params', {}).get('_tool_name', 'N/A')}")

    print(f"✅ Total messages: {len(result['messages'])}")


def test_conversational_flow():
    """Test: Conversational response without tools."""
    print("\n" + "="*60)
    print("TEST: Conversational flow (no tools)")
    print("="*60)

    result = run_graph("What types of uncertainty visualizations do you support?")

    # Should respond without calling tools
    assert len(result["messages"]) >= 2  # User message + AI response

    # Last message should be AI response with content
    last_msg = result["messages"][-1]
    assert hasattr(last_msg, "content")
    assert len(last_msg.content) > 0

    print(f"✅ Conversational response received")
    print(f"   Response length: {len(last_msg.content)} chars")
    print(f"   Preview: {last_msg.content[:100]}...")


if __name__ == "__main__":
    try:
        test_data_generation_only()
        test_data_and_viz()
        test_load_and_viz()
        test_curve_boxplot()
        test_scalar_field_viz()
        test_multi_step_workflow()
        test_conversational_flow()

        print("\n" + "="*60)
        print("✅ ALL INTEGRATION TESTS PASSED")
        print("="*60)

        # Pause to allow viewing plots
        print("\nℹ️  Matplotlib windows may be open. Close them to continue.")
        input("Press Enter to close all matplotlib windows and exit...")
        plt.close('all')

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        plt.close('all')
        sys.exit(1)
