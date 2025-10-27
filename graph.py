"""LangGraph workflow definition for ChatUVisBox"""
from langgraph.graph import StateGraph, END
from state import GraphState
from nodes import call_model, call_data_tool, call_viz_tool
from routing import route_after_model, route_after_tool


def create_graph():
    """
    Create and compile the ChatUVisBox LangGraph workflow.

    Graph structure:
        START -> model -> [conditional]
                            ├─> data_tool -> model (loop)
                            ├─> viz_tool -> model (loop)
                            └─> END (if no tool call)

    Returns:
        Compiled StateGraph
    """
    # Initialize graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("model", call_model)
    workflow.add_node("data_tool", call_data_tool)
    workflow.add_node("viz_tool", call_viz_tool)

    # Set entry point
    workflow.set_entry_point("model")

    # Add conditional edges from model
    workflow.add_conditional_edges(
        "model",
        route_after_model,
        {
            "data_tool": "data_tool",
            "viz_tool": "viz_tool",
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
        "viz_tool",
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
    from state import create_initial_state

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
    from state import create_initial_state

    if initial_state is None:
        state = create_initial_state(user_input)
    else:
        from langchain_core.messages import HumanMessage
        state = initial_state
        state["messages"].append(HumanMessage(content=user_input))

    # Stream execution
    for update in graph_app.stream(state):
        yield update
