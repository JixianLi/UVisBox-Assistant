"""Routing logic for the LangGraph workflow"""
from typing import Literal
from uvisbox_assistant.state import GraphState
from uvisbox_assistant.utils import get_tool_type


def route_after_model(state: GraphState) -> Literal["data_tool", "vis_tool", "end"]:
    """
    Determine the next node after the model has responded.

    Logic:
    - If the last message contains tool_calls:
      - Route to "data_tool" if it's a data tool
      - Route to "vis_tool" if it's a vis tool
    - Otherwise, route to "end" (conversation response without tool call)

    Args:
        state: Current graph state

    Returns:
        Next node name: "data_tool", "vis_tool", or "end"
    """
    last_message = state["messages"][-1]

    # Check if message has tool calls
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        # No tool call - model is responding directly to user
        return "end"

    # Get the first tool call
    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]

    # Route based on tool type
    tool_type = get_tool_type(tool_name)

    if tool_type == "data":
        return "data_tool"
    elif tool_type == "vis":
        return "vis_tool"
    else:
        # Unknown tool - end and let user see the error
        print(f"WARNING: Unknown tool type for {tool_name}")
        return "end"


def route_after_tool(state: GraphState) -> Literal["model", "end"]:
    """
    Determine the next node after a tool has executed.

    Logic:
    - Always return to "model" so it can:
      - Call another tool if needed (multi-step)
      - Respond to the user about the tool result

    Exception: If error_count exceeds threshold, go to "end" to prevent infinite loops.

    Args:
        state: Current graph state

    Returns:
        Next node name: "model" or "end"
    """
    # Circuit breaker: too many consecutive errors
    MAX_ERRORS = 3
    if state.get("error_count", 0) >= MAX_ERRORS:
        print(f"ERROR: Exceeded {MAX_ERRORS} consecutive errors. Ending.")
        return "end"

    # Default: return to model for next decision
    return "model"


def should_continue(state: GraphState) -> bool:
    """
    Determine if the graph should continue or end.

    This is a simple boolean version for checkpointing.

    Returns:
        True if should continue, False if should end
    """
    last_message = state["messages"][-1]
    has_tool_calls = hasattr(last_message, "tool_calls") and last_message.tool_calls
    return has_tool_calls and state.get("error_count", 0) < 3
