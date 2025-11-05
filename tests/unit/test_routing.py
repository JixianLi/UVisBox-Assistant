"""Test routing logic"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from uvisbox_assistant.core.routing import route_after_model, route_after_tool, should_continue
from uvisbox_assistant.core.state import create_initial_state
from langchain_core.messages import AIMessage, HumanMessage


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

    # Test 2: Route with vis tool
    state2 = create_initial_state("test")
    ai_msg_with_vis_tool = AIMessage(
        content="",
        tool_calls=[{
            "name": "plot_functional_boxplot",
            "args": {"data_path": "test.npy"},
            "id": "456"
        }]
    )
    state2["messages"].append(ai_msg_with_vis_tool)

    route2 = route_after_model(state2)
    assert route2 == "vis_tool", f"Expected 'vis_tool', got '{route2}'"
    print(f"✅ Route with vis tool: {route2}")

    # Test 3: Route without tool call (direct response)
    state3 = create_initial_state("test")
    ai_msg_no_tool = AIMessage(content="Here's what I can do for you...")
    state3["messages"].append(ai_msg_no_tool)

    route3 = route_after_model(state3)
    assert route3 == "end", f"Expected 'end', got '{route3}'"
    print(f"✅ Route with no tool call: {route3}")

    # Test 4: Route with statistics tool
    state4 = create_initial_state("test")
    ai_msg_statistics = AIMessage(
        content="",
        tool_calls=[{
            "name": "compute_functional_boxplot_statistics",
            "args": {"data_path": "test.npy"},
            "id": "789"
        }]
    )
    state4["messages"].append(ai_msg_statistics)

    route4 = route_after_model(state4)
    assert route4 == "statistics_tool", f"Expected 'statistics_tool', got '{route4}'"
    print(f"✅ Route with statistics tool: {route4}")

    # Test 5: Route with analyzer tool
    state5 = create_initial_state("test")
    ai_msg_analyzer = AIMessage(
        content="",
        tool_calls=[{
            "name": "generate_uncertainty_report",
            "args": {"statistics_summary": {}, "analysis_type": "quick"},
            "id": "abc"
        }]
    )
    state5["messages"].append(ai_msg_analyzer)

    route5 = route_after_model(state5)
    assert route5 == "analyzer_tool", f"Expected 'analyzer_tool', got '{route5}'"
    print(f"✅ Route with analyzer tool: {route5}")

    # Test 6: Route with unknown tool
    state6 = create_initial_state("test")
    ai_msg_unknown = AIMessage(
        content="",
        tool_calls=[{
            "name": "unknown_tool",
            "args": {},
            "id": "def"
        }]
    )
    state6["messages"].append(ai_msg_unknown)

    route6 = route_after_model(state6)
    assert route6 == "end", f"Expected 'end' for unknown tool, got '{route6}'"
    print(f"✅ Route with unknown tool: {route6}")


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


def test_should_continue():
    """Test should_continue logic"""
    print("\n" + "="*60)
    print("TEST: should_continue")
    print("="*60)

    # Test 1: Should continue with tool calls and low error count
    state = create_initial_state("test")
    ai_msg_with_tool = AIMessage(
        content="",
        tool_calls=[{
            "name": "load_csv_to_numpy",
            "args": {"filepath": "test.csv"},
            "id": "123"
        }]
    )
    state["messages"].append(ai_msg_with_tool)
    state["error_count"] = 0

    should_cont = should_continue(state)
    assert should_cont is True, f"Expected True, got {should_cont}"
    print(f"✅ Should continue with tool calls (error_count=0): {should_cont}")

    # Test 2: Should continue with tool calls and 2 errors (below threshold)
    state2 = create_initial_state("test")
    state2["messages"].append(ai_msg_with_tool)
    state2["error_count"] = 2

    should_cont2 = should_continue(state2)
    assert should_cont2 is True, f"Expected True, got {should_cont2}"
    print(f"✅ Should continue with tool calls (error_count=2): {should_cont2}")

    # Test 3: Should NOT continue with tool calls but 3 errors (at threshold)
    state3 = create_initial_state("test")
    state3["messages"].append(ai_msg_with_tool)
    state3["error_count"] = 3

    should_cont3 = should_continue(state3)
    assert not should_cont3, f"Expected falsy value, got {should_cont3}"
    print(f"✅ Should NOT continue with tool calls (error_count=3): {should_cont3}")

    # Test 4: Should NOT continue without tool calls
    state4 = create_initial_state("test")
    ai_msg_no_tool = AIMessage(content="Here's my response...")
    state4["messages"].append(ai_msg_no_tool)
    state4["error_count"] = 0

    should_cont4 = should_continue(state4)
    assert not should_cont4, f"Expected falsy value, got {should_cont4}"
    print(f"✅ Should NOT continue without tool calls: {should_cont4}")

    # Test 5: Should NOT continue with empty tool_calls list
    state5 = create_initial_state("test")
    ai_msg_empty_tools = AIMessage(content="", tool_calls=[])
    state5["messages"].append(ai_msg_empty_tools)
    state5["error_count"] = 0

    should_cont5 = should_continue(state5)
    assert not should_cont5, f"Expected falsy value, got {should_cont5}"
    print(f"✅ Should NOT continue with empty tool_calls: {should_cont5}")


def test_route_after_model_edge_cases():
    """Test edge cases for route_after_model"""
    print("\n" + "="*60)
    print("TEST: route_after_model edge cases")
    print("="*60)

    # Test 1: Message without tool_calls attribute
    state = create_initial_state("test")
    # Add a message without tool_calls attribute
    state["messages"].append(HumanMessage(content="test"))

    route = route_after_model(state)
    assert route == "end", f"Expected 'end', got '{route}'"
    print(f"✅ Route with message without tool_calls attribute: {route}")

    # Test 2: Empty messages list (edge case - should handle gracefully)
    state2 = create_initial_state("test")
    state2["messages"] = []

    try:
        route2 = route_after_model(state2)
        # If it doesn't crash, it should be either "end" or "tool"
        assert route2 in ["end", "tool", "data_tool", "vis_tool", "statistics_tool", "analyzer_tool"], \
            f"Expected valid route, got '{route2}'"
        print(f"✅ Route with empty messages (handled gracefully): {route2}")
    except IndexError:
        # If it raises IndexError, that's expected for empty list
        print(f"✅ Route with empty messages (raises IndexError as expected)")


def test_route_after_tool_edge_cases():
    """Test edge cases for route_after_tool"""
    print("\n" + "="*60)
    print("TEST: route_after_tool edge cases")
    print("="*60)

    # Test 1: Missing error_count key
    state = create_initial_state("test")
    if 'error_count' in state:
        del state['error_count']

    route = route_after_tool(state)
    # Should handle gracefully with .get() default
    assert route in ["model", "end"], f"Expected 'model' or 'end', got '{route}'"
    print(f"✅ Route with missing error_count (handled gracefully): {route}")

    # Test 2: Exactly at threshold (already tested in main test, but explicit edge case)
    state2 = create_initial_state("test")
    state2["error_count"] = 3  # Exactly at threshold

    route2 = route_after_tool(state2)
    assert route2 == "end", f"Expected 'end', got '{route2}'"
    print(f"✅ Route exactly at MAX_ERRORS threshold (3): {route2}")


if __name__ == "__main__":
    try:
        test_route_after_model()
        test_route_after_tool()
        test_should_continue()
        test_route_after_model_edge_cases()
        test_route_after_tool_edge_cases()

        print("\n" + "="*60)
        print("✅ ALL ROUTING TESTS PASSED")
        print("="*60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
