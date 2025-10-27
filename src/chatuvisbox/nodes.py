"""Node implementations for the LangGraph workflow"""
from typing import Dict
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
import os

from chatuvisbox.state import GraphState, update_state_with_data, update_state_with_viz, increment_error_count
from chatuvisbox.model import create_model_with_tools, prepare_messages_for_model
from chatuvisbox.data_tools import DATA_TOOLS, DATA_TOOL_SCHEMAS
from chatuvisbox.viz_tools import VIZ_TOOLS, VIZ_TOOL_SCHEMAS
from chatuvisbox import config


# Create model with all tools
ALL_TOOL_SCHEMAS = DATA_TOOL_SCHEMAS + VIZ_TOOL_SCHEMAS
MODEL = create_model_with_tools(ALL_TOOL_SCHEMAS)


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

    # Call model
    response = MODEL.invoke(messages)

    # Return as state update
    return {"messages": [response]}


def call_data_tool(state: GraphState) -> Dict:
    """
    Node that executes a data tool based on the last AI message.

    Args:
        state: Current graph state

    Returns:
        Dict with tool result message and state updates
    """
    last_message = state["messages"][-1]

    # Extract tool call from AI message
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        raise ValueError("call_data_tool invoked but no tool_calls in last message")

    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    tool_call_id = tool_call["id"]

    print(f"[DATA TOOL] Calling {tool_name} with args: {tool_args}")

    # Execute tool with error handling
    try:
        if tool_name not in DATA_TOOLS:
            result = {
                "status": "error",
                "message": f"Unknown data tool: {tool_name}"
            }
        else:
            tool_func = DATA_TOOLS[tool_name]
            result = tool_func(**tool_args)

        print(f"[DATA TOOL] Result: {result}")

        # Create tool message
        tool_message = ToolMessage(
            content=str(result),
            tool_call_id=tool_call_id
        )

        # Update state if successful
        state_updates = {"messages": [tool_message]}

        if result.get("status") == "success" and "output_path" in result:
            state_updates.update(update_state_with_data(state, result["output_path"]))
        else:
            state_updates.update(increment_error_count(state))

        return state_updates

    except Exception as e:
        print(f"[DATA TOOL] Exception: {e}")
        error_result = {
            "status": "error",
            "message": f"Exception in {tool_name}: {str(e)}"
        }

        tool_message = ToolMessage(
            content=str(error_result),
            tool_call_id=tool_call_id
        )

        return {
            "messages": [tool_message],
            **increment_error_count(state)
        }


def call_viz_tool(state: GraphState) -> Dict:
    """
    Node that executes a visualization tool.

    Args:
        state: Current graph state

    Returns:
        Dict with tool result message and state updates
    """
    last_message = state["messages"][-1]

    # Extract tool call
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        raise ValueError("call_viz_tool invoked but no tool_calls in last message")

    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    tool_call_id = tool_call["id"]

    print(f"[VIZ TOOL] Calling {tool_name} with args: {tool_args}")

    # Execute tool
    try:
        if tool_name not in VIZ_TOOLS:
            result = {
                "status": "error",
                "message": f"Unknown viz tool: {tool_name}"
            }
        else:
            tool_func = VIZ_TOOLS[tool_name]
            result = tool_func(**tool_args)

        print(f"[VIZ TOOL] Result: {result}")

        # Create tool message
        tool_message = ToolMessage(
            content=str(result),
            tool_call_id=tool_call_id
        )

        # Update state
        state_updates = {"messages": [tool_message]}

        if result.get("status") == "success" and "_viz_params" in result:
            # Extract _viz_params from result for state storage
            state_updates.update(update_state_with_viz(state, result["_viz_params"]))
        else:
            state_updates.update(increment_error_count(state))

        return state_updates

    except Exception as e:
        print(f"[VIZ TOOL] Exception: {e}")
        error_result = {
            "status": "error",
            "message": f"Exception in {tool_name}: {str(e)}"
        }

        tool_message = ToolMessage(
            content=str(error_result),
            tool_call_id=tool_call_id
        )

        return {
            "messages": [tool_message],
            **increment_error_count(state)
        }
