"""LangGraph workflow definition for UVisBox-Assistant"""
from langgraph.graph import StateGraph, END
from uvisbox_assistant.state import GraphState
from uvisbox_assistant.nodes import (
    call_model, call_data_tool, call_vis_tool,
    call_statistics_tool, call_analyzer_tool
)
from uvisbox_assistant.routing import route_after_model, route_after_tool


def create_graph():
    """
    Create and compile the UVisBox-Assistant LangGraph workflow.

    Graph structure:
        START -> model -> [conditional]
                            ├─> data_tool -> model (loop)
                            ├─> vis_tool -> model (loop)
                            ├─> statistics_tool -> model (loop)
                            ├─> analyzer_tool -> model (loop)
                            └─> END (if no tool call)

    Returns:
        Compiled StateGraph
    """
    # Initialize graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("model", call_model)
    workflow.add_node("data_tool", call_data_tool)
    workflow.add_node("vis_tool", call_vis_tool)
    workflow.add_node("statistics_tool", call_statistics_tool)
    workflow.add_node("analyzer_tool", call_analyzer_tool)

    # Set entry point
    workflow.set_entry_point("model")

    # Add conditional edges from model
    workflow.add_conditional_edges(
        "model",
        route_after_model,
        {
            "data_tool": "data_tool",
            "vis_tool": "vis_tool",
            "statistics_tool": "statistics_tool",
            "analyzer_tool": "analyzer_tool",
            "end": END
        }
    )

    # Add edges back to model after tool execution
    workflow.add_conditional_edges(
        "data_tool",
        route_after_tool,
        {
            "model": "model",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "vis_tool",
        route_after_tool,
        {
            "model": "model",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "statistics_tool",
        route_after_tool,
        {
            "model": "model",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "analyzer_tool",
        route_after_tool,
        {
            "model": "model",
            "end": END
        }
    )

    # Compile the graph
    app = workflow.compile()

    return app


# Create singleton graph instance
graph_app = create_graph()


def run_graph(user_input: str, initial_state: dict = None) -> GraphState:
    """
    Run the graph with user input.

    Args:
        user_input: User's message
        initial_state: Optional initial state (for continuing conversations)

    Returns:
        Final state after graph execution
    """
    from uvisbox_assistant.state import create_initial_state

    if initial_state is None:
        state = create_initial_state(user_input)
    else:
        # Add new user message to existing state
        from langchain_core.messages import HumanMessage
        state = initial_state
        state["messages"].append(HumanMessage(content=user_input))

    # Execute graph
    final_state = graph_app.invoke(state)

    return final_state


def stream_graph(user_input: str, initial_state: dict = None):
    """
    Stream graph execution for real-time updates.

    Args:
        user_input: User's message
        initial_state: Optional initial state

    Yields:
        State updates as they occur
    """
    from uvisbox_assistant.state import create_initial_state

    if initial_state is None:
        state = create_initial_state(user_input)
    else:
        from langchain_core.messages import HumanMessage
        state = initial_state
        state["messages"].append(HumanMessage(content=user_input))

    # Stream execution
    for update in graph_app.stream(state):
        yield update
