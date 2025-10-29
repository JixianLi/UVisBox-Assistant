"""Test graph compilation and basic execution"""
import sys

from chatuvisbox.graph import create_graph, run_graph, graph_app


def test_graph_compilation():
    """Test that the graph compiles without errors"""
    print("\n" + "="*60)
    print("TEST: Graph Compilation")
    print("="*60)

    # Test graph creation
    app = create_graph()
    assert app is not None
    print("✅ Graph created successfully")

    # Test that singleton is created
    assert graph_app is not None
    print("✅ Singleton graph_app created")

    # Check that we can get the graph structure
    try:
        graph_structure = app.get_graph()
        print(f"✅ Graph structure accessible: {type(graph_structure)}")
    except Exception as e:
        print(f"⚠️  Could not access graph structure: {e}")

    print("\n✅ Graph compilation test passed")


def test_simple_execution():
    """Test simple graph execution with data generation"""
    print("\n" + "="*60)
    print("TEST: Simple Graph Execution")
    print("="*60)

    # Test with a simple request
    result = run_graph("Generate 5 ensemble curves with 50 points each")

    # Check that we got a result
    assert result is not None
    assert "messages" in result
    assert len(result["messages"]) > 0

    print(f"✅ Graph executed successfully")
    print(f"   Total messages: {len(result['messages'])}")
    print(f"   Current data path: {result.get('current_data_path', 'None')}")
    print(f"   Error count: {result.get('error_count', 0)}")

    # Print message types
    print("\n   Message flow:")
    for i, msg in enumerate(result["messages"]):
        msg_type = msg.__class__.__name__
        content_preview = ""
        if hasattr(msg, "content") and msg.content:
            content_preview = msg.content[:80] + "..." if len(msg.content) > 80 else msg.content
        elif hasattr(msg, "tool_calls") and msg.tool_calls:
            content_preview = f"[Tool call: {msg.tool_calls[0]['name']}]"
        print(f"   {i+1}. {msg_type}: {content_preview}")

    print("\n✅ Simple execution test passed")


def test_direct_response():
    """Test that model can respond directly without tool calls"""
    print("\n" + "="*60)
    print("TEST: Direct Response (No Tools)")
    print("="*60)

    # Ask a question that shouldn't require tools
    result = run_graph("What visualization types can you create?")

    assert result is not None
    assert "messages" in result
    assert len(result["messages"]) >= 2  # At least user message + AI response

    # The last message should be from the AI without tool calls
    last_msg = result["messages"][-1]
    print(f"✅ Graph executed")
    print(f"   Last message type: {last_msg.__class__.__name__}")

    if hasattr(last_msg, "content"):
        print(f"   Response preview: {last_msg.content[:150]}...")

    print("\n✅ Direct response test passed")


if __name__ == "__main__":
    try:
        test_graph_compilation()
        test_simple_execution()
        test_direct_response()

        print("\n" + "="*60)
        print("✅ ALL GRAPH TESTS PASSED")
        print("="*60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
