"""Node implementations for the LangGraph workflow"""
from typing import Dict
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from datetime import datetime
import os

from chatuvisbox.state import GraphState, update_state_with_data, update_state_with_vis, increment_error_count
from chatuvisbox.model import create_model_with_tools, prepare_messages_for_model
from chatuvisbox.data_tools import DATA_TOOLS, DATA_TOOL_SCHEMAS
from chatuvisbox.vis_tools import VIS_TOOLS, VIS_TOOL_SCHEMAS
from chatuvisbox import config
from chatuvisbox.logger import log_tool_call, log_tool_result, log_error
from chatuvisbox.output_control import vprint


# Create model with all tools
ALL_TOOL_SCHEMAS = DATA_TOOL_SCHEMAS + VIS_TOOL_SCHEMAS
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

    vprint(f"[DATA TOOL] Calling {tool_name} with args: {tool_args}")
    log_tool_call(tool_name, tool_args)

    # Track execution start
    execution_entry = {
        "tool_name": tool_name,
        "timestamp": datetime.now(),
        "status": None,
        "error_id": None
    }

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

        vprint(f"[DATA TOOL] Result: {result}")
        log_tool_result(tool_name, result)

        # Create tool message
        tool_message = ToolMessage(
            content=str(result),
            tool_call_id=tool_call_id
        )

        # Update state if successful
        state_updates = {"messages": [tool_message]}

        if result.get("status") == "success" and "output_path" in result:
            execution_entry["status"] = "success"
            state_updates.update(update_state_with_data(state, result["output_path"]))

            # Check for auto-fix pattern
            _check_and_mark_auto_fix(state, tool_name, state_updates)
        else:
            execution_entry["status"] = "error"
            state_updates.update(increment_error_count(state))
            # Store error info for auto-fix detection
            state_updates["last_error_tool"] = tool_name
            state_updates["last_error_id"] = state.get("_pending_error_id")

        # Add execution to sequence
        _add_execution_entry(state, execution_entry, state_updates)

        return state_updates

    except Exception as e:
        vprint(f"[DATA TOOL] Exception: {e}")
        log_error(f"Exception in {tool_name}: {str(e)}")
        error_result = {
            "status": "error",
            "message": f"Exception in {tool_name}: {str(e)}"
        }

        execution_entry["status"] = "error"

        tool_message = ToolMessage(
            content=str(error_result),
            tool_call_id=tool_call_id
        )

        state_updates = {
            "messages": [tool_message],
            **increment_error_count(state),
            "last_error_tool": tool_name,
            "last_error_id": state.get("_pending_error_id")
        }

        # Add execution to sequence
        _add_execution_entry(state, execution_entry, state_updates)

        return state_updates


def call_vis_tool(state: GraphState) -> Dict:
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
        raise ValueError("call_vis_tool invoked but no tool_calls in last message")

    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    tool_call_id = tool_call["id"]

    vprint(f"[VIS TOOL] Calling {tool_name} with args: {tool_args}")
    log_tool_call(tool_name, tool_args)

    # Track execution start
    execution_entry = {
        "tool_name": tool_name,
        "timestamp": datetime.now(),
        "status": None,
        "error_id": None
    }

    # Execute tool
    try:
        if tool_name not in VIS_TOOLS:
            result = {
                "status": "error",
                "message": f"Unknown vis tool: {tool_name}"
            }
        else:
            tool_func = VIS_TOOLS[tool_name]
            result = tool_func(**tool_args)

        vprint(f"[VIS TOOL] Result: {result}")
        log_tool_result(tool_name, result)

        # Create tool message
        tool_message = ToolMessage(
            content=str(result),
            tool_call_id=tool_call_id
        )

        # Update state
        state_updates = {"messages": [tool_message]}

        if result.get("status") == "success" and "_vis_params" in result:
            execution_entry["status"] = "success"
            # Extract _vis_params from result for state storage
            state_updates.update(update_state_with_vis(state, result["_vis_params"]))

            # Check for auto-fix pattern
            _check_and_mark_auto_fix(state, tool_name, state_updates)
        else:
            execution_entry["status"] = "error"
            state_updates.update(increment_error_count(state))
            # Store error info for auto-fix detection
            state_updates["last_error_tool"] = tool_name
            state_updates["last_error_id"] = state.get("_pending_error_id")

        # Add execution to sequence
        _add_execution_entry(state, execution_entry, state_updates)

        return state_updates

    except Exception as e:
        vprint(f"[VIS TOOL] Exception: {e}")
        log_error(f"Exception in {tool_name}: {str(e)}")
        error_result = {
            "status": "error",
            "message": f"Exception in {tool_name}: {str(e)}"
        }

        execution_entry["status"] = "error"

        tool_message = ToolMessage(
            content=str(error_result),
            tool_call_id=tool_call_id
        )

        state_updates = {
            "messages": [tool_message],
            **increment_error_count(state),
            "last_error_tool": tool_name,
            "last_error_id": state.get("_pending_error_id")
        }

        # Add execution to sequence
        _add_execution_entry(state, execution_entry, state_updates)

        return state_updates


def _add_execution_entry(state: GraphState, entry: Dict, state_updates: Dict):
    """Add execution entry to state tracking sequence."""
    current_sequence = state.get("tool_execution_sequence", [])
    state_updates["tool_execution_sequence"] = current_sequence + [entry]


def _check_and_mark_auto_fix(state: GraphState, tool_name: str, state_updates: Dict):
    """Check if this execution represents an auto-fix and mark it."""
    # Check if last execution was an error with the same tool
    if (state.get("last_error_tool") == tool_name and
        state.get("last_error_id") is not None):

        vprint(f"[AUTO-FIX] {tool_name} succeeded after error (ID: {state.get('last_error_id')})")

        # Store auto-fix marker for conversation.py to process
        state_updates["_auto_fixed_error_id"] = state.get("last_error_id")

        # Clear auto-fix tracking
        state_updates["last_error_tool"] = None
        state_updates["last_error_id"] = None
