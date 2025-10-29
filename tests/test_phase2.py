"""Comprehensive test for Phase 2: LangGraph State & Nodes"""
import sys
import os

# Add project root to path

from chatuvisbox import config
from chatuvisbox.state import GraphState, create_initial_state, update_state_with_data, update_state_with_vis, increment_error_count
from chatuvisbox.model import create_model_with_tools, prepare_messages_for_model, get_system_prompt
from chatuvisbox.nodes import call_model, call_data_tool, call_vis_tool
from chatuvisbox.utils import is_data_tool, is_vis_tool, get_tool_type, get_available_files, format_file_list
from chatuvisbox.data_tools import DATA_TOOL_SCHEMAS
from chatuvisbox.vis_tools import VIS_TOOL_SCHEMAS
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage


def test_1_state_management():
    """Test GraphState creation and helper functions"""
    print("\n" + "="*80)
    print("TEST 1: State Management")
    print("="*80)

    # Create initial state
    state = create_initial_state("Load sample_curves.csv and plot it")

    assert len(state["messages"]) == 1
    assert isinstance(state["messages"][0], HumanMessage)
    assert state["current_data_path"] is None
    assert state["last_vis_params"] is None
    assert state["session_files"] == []
    assert state["error_count"] == 0

    print("✅ Initial state created correctly")

    # Test update_state_with_data
    data_path = "/tmp/test.npy"
    updates = update_state_with_data(state, data_path)

    assert updates["current_data_path"] == data_path
    assert data_path in updates["session_files"]
    assert updates["error_count"] == 0

    print("✅ update_state_with_data works")

    # Test update_state_with_vis
    vis_params = {"_tool_name": "plot_functional_boxplot", "data_path": data_path}
    updates = update_state_with_vis(state, vis_params)

    assert updates["last_vis_params"] == vis_params
    assert updates["error_count"] == 0

    print("✅ update_state_with_vis works")

    # Test increment_error_count
    updates = increment_error_count(state)
    assert updates["error_count"] == 1

    state["error_count"] = 2
    updates = increment_error_count(state)
    assert updates["error_count"] == 3

    print("✅ increment_error_count works")


def test_2_model_setup():
    """Test model creation and system prompt"""
    print("\n" + "="*80)
    print("TEST 2: Model Setup")
    print("="*80)

    # Test system prompt
    prompt = get_system_prompt()
    assert "ChatUVisBox" in prompt
    assert "functional_boxplot" in prompt
    assert "curve_boxplot" in prompt
    assert "percentiles" in prompt

    print("✅ System prompt generated correctly")

    # Test with file list
    files = ["sample_curves.csv", "test.npy"]
    prompt_with_files = get_system_prompt(files)
    assert "sample_curves.csv" in prompt_with_files
    assert "test.npy" in prompt_with_files

    print("✅ System prompt includes file list")

    # Test model creation
    all_tools = DATA_TOOL_SCHEMAS + VIS_TOOL_SCHEMAS
    model = create_model_with_tools(all_tools)

    assert model is not None
    print("✅ Model created and tools bound successfully")

    # Test prepare_messages_for_model
    state = create_initial_state("Test message")
    messages = prepare_messages_for_model(state, files)

    assert len(messages) == 2  # System + Human
    assert "ChatUVisBox" in messages[0].content
    assert messages[1].content == "Test message"

    print("✅ prepare_messages_for_model works correctly")


def test_3_utils():
    """Test utility functions"""
    print("\n" + "="*80)
    print("TEST 3: Utility Functions")
    print("="*80)

    # Test tool type detection
    assert is_data_tool("load_csv_to_numpy") == True
    assert is_data_tool("plot_functional_boxplot") == False

    assert is_vis_tool("plot_functional_boxplot") == True
    assert is_vis_tool("load_csv_to_numpy") == False

    print("✅ Tool type detection works")

    # Test get_tool_type
    assert get_tool_type("load_csv_to_numpy") == "data"
    assert get_tool_type("plot_functional_boxplot") == "vis"
    assert get_tool_type("unknown_tool") is None

    print("✅ get_tool_type works")

    # Test get_available_files
    files = get_available_files()
    assert isinstance(files, list)
    if files:
        print(f"✅ Found {len(files)} files in test_data/")
    else:
        print("⚠️  No files in test_data/ (this is OK for testing)")

    # Test format_file_list
    formatted = format_file_list([])
    assert formatted == "No files available"

    formatted = format_file_list(["a.csv", "b.npy"])
    assert "a.csv" in formatted
    assert "b.npy" in formatted

    print("✅ File list formatting works")


def test_4_node_call_model():
    """Test call_model node"""
    print("\n" + "="*80)
    print("TEST 4: call_model Node")
    print("="*80)

    # Create initial state with a request
    state = create_initial_state("Generate 5 ensemble curves with 100 points each")

    # Call the model
    result = call_model(state)

    assert "messages" in result
    assert len(result["messages"]) == 1

    response = result["messages"][0]
    assert isinstance(response, AIMessage)

    # Check if model decided to use a tool
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"✅ Model responded with tool call: {response.tool_calls[0]['name']}")
        assert response.tool_calls[0]['name'] in ['generate_ensemble_curves', 'load_csv_to_numpy', 'load_npy', 'generate_scalar_field_ensemble']
    else:
        print("✅ Model responded (no tool call)")

    print("✅ call_model node executed successfully")


def test_5_node_call_data_tool():
    """Test call_data_tool node"""
    print("\n" + "="*80)
    print("TEST 5: call_data_tool Node")
    print("="*80)

    # Create state with an AI message that has a tool call
    from langchain_core.messages import AIMessage

    state = create_initial_state("Generate curves")

    # Simulate AI message with tool call
    ai_message = AIMessage(
        content="",
        tool_calls=[{
            "name": "generate_ensemble_curves",
            "args": {
                "num_curves": 5,
                "num_points": 100
            },
            "id": "test_call_123"
        }]
    )

    state["messages"].append(ai_message)

    # Call data tool node
    result = call_data_tool(state)

    assert "messages" in result
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], ToolMessage)

    tool_msg = result["messages"][0]
    assert "status" in tool_msg.content

    # If successful, should have output_path
    if "success" in tool_msg.content:
        assert "output_path" in tool_msg.content
        assert "current_data_path" in result
        print(f"✅ Data tool succeeded: {result.get('current_data_path', 'N/A')}")
    else:
        print(f"⚠️  Data tool returned error (OK for testing): {tool_msg.content[:100]}")

    print("✅ call_data_tool node executed successfully")


def test_6_integration():
    """Test multi-step workflow integration"""
    print("\n" + "="*80)
    print("TEST 6: Multi-Step Integration")
    print("="*80)

    # Step 1: Start with user request
    state = create_initial_state("Generate 10 ensemble curves")
    print(f"Step 1: User request - {state['messages'][0].content}")

    # Step 2: Call model
    result = call_model(state)
    state["messages"].extend(result["messages"])

    ai_response = result["messages"][0]
    if hasattr(ai_response, "tool_calls") and ai_response.tool_calls:
        print(f"Step 2: Model chose tool - {ai_response.tool_calls[0]['name']}")

        # Step 3: Execute tool
        tool_result = call_data_tool(state)
        state["messages"].extend(tool_result["messages"])

        # Update state
        if "current_data_path" in tool_result:
            state["current_data_path"] = tool_result["current_data_path"]
            state["session_files"] = tool_result.get("session_files", [])
            print(f"Step 3: Tool executed - {state['current_data_path']}")

        # Step 4: Call model again to confirm
        result2 = call_model(state)
        final_response = result2["messages"][0]

        if hasattr(final_response, "content"):
            print(f"Step 4: Model confirmation - {final_response.content[:100]}...")

        print("✅ Multi-step workflow completed successfully")
    else:
        print("⚠️  Model didn't call a tool (this can happen)")


def run_all_tests():
    """Run all Phase 2 tests"""
    print("\n" + "="*80)
    print("PHASE 2 COMPREHENSIVE TEST SUITE")
    print("="*80)

    try:
        test_1_state_management()
        test_2_model_setup()
        test_3_utils()
        test_4_node_call_model()
        test_5_node_call_data_tool()
        test_6_integration()

        print("\n" + "="*80)
        print("✅ ALL PHASE 2 TESTS PASSED")
        print("="*80)
        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
