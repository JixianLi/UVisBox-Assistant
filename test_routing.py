"""Test routing logic"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from routing import route_after_model, route_after_tool
from state import create_initial_state
from langchain_core.messages import AIMessage


def test_route_after_model():
    """Test route_after_model routing logic"""
    print("\n" + "="*60)
    print("TEST: route_after_model")
    print("="*60)

    # Test 1: Route with data tool
    state = create_initial_state("test")
    ai_msg_with_data_tool = AIMessage(
        content="",
        tool_calls=[{
            "name": "load_csv_to_numpy",
            "args": {"filepath": "test.csv"},
            "id": "123"
        }]
    )
    state["messages"].append(ai_msg_with_data_tool)

    route = route_after_model(state)
    assert route == "data_tool", f"Expected 'data_tool', got '{route}'"
    print(f"✅ Route with data tool: {route}")

    # Test 2: Route with viz tool
    state2 = create_initial_state("test")
    ai_msg_with_viz_tool = AIMessage(
        content="",
        tool_calls=[{
            "name": "plot_functional_boxplot",
            "args": {"data_path": "test.npy"},
            "id": "456"
        }]
    )
    state2["messages"].append(ai_msg_with_viz_tool)

    route2 = route_after_model(state2)
    assert route2 == "viz_tool", f"Expected 'viz_tool', got '{route2}'"
    print(f"✅ Route with viz tool: {route2}")

    # Test 3: Route without tool call (direct response)
    state3 = create_initial_state("test")
    ai_msg_no_tool = AIMessage(content="Here's what I can do for you...")
    state3["messages"].append(ai_msg_no_tool)

    route3 = route_after_model(state3)
    assert route3 == "end", f"Expected 'end', got '{route3}'"
    print(f"✅ Route with no tool call: {route3}")

    # Test 4: Route with unknown tool
    state4 = create_initial_state("test")
    ai_msg_unknown = AIMessage(
        content="",
        tool_calls=[{
            "name": "unknown_tool",
            "args": {},
            "id": "789"
        }]
    )
    state4["messages"].append(ai_msg_unknown)

    route4 = route_after_model(state4)
    assert route4 == "end", f"Expected 'end' for unknown tool, got '{route4}'"
    print(f"✅ Route with unknown tool: {route4}")


def test_route_after_tool():
    """Test route_after_tool routing logic"""
    print("\n" + "="*60)
    print("TEST: route_after_tool")
    print("="*60)

    # Test 1: Normal case - return to model
    state = create_initial_state("test")
    state["error_count"] = 0

    route = route_after_tool(state)
    assert route == "model", f"Expected 'model', got '{route}'"
    print(f"✅ Route after successful tool: {route}")

    # Test 2: Some errors but not at threshold
    state2 = create_initial_state("test")
    state2["error_count"] = 2

    route2 = route_after_tool(state2)
    assert route2 == "model", f"Expected 'model', got '{route2}'"
    print(f"✅ Route with 2 errors (below threshold): {route2}")

    # Test 3: At error threshold - circuit breaker
    state3 = create_initial_state("test")
    state3["error_count"] = 3

    route3 = route_after_tool(state3)
    assert route3 == "end", f"Expected 'end', got '{route3}'"
    print(f"✅ Route with 3 errors (at threshold): {route3}")

    # Test 4: Beyond threshold
    state4 = create_initial_state("test")
    state4["error_count"] = 5

    route4 = route_after_tool(state4)
    assert route4 == "end", f"Expected 'end', got '{route4}'"
    print(f"✅ Route with 5 errors (beyond threshold): {route4}")


if __name__ == "__main__":
    try:
        test_route_after_model()
        test_route_after_tool()

        print("\n" + "="*60)
        print("✅ ALL ROUTING TESTS PASSED")
        print("="*60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
