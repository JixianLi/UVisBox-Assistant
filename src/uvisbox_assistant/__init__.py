"""
UVisBox-Assistant: Natural language interface for UVisBox uncertainty visualization.

A LangGraph-based conversational agent that translates natural language requests
into data processing and visualization operations using the UVisBox library.
"""

__version__ = "0.2.0"

# Expose main API
from uvisbox_assistant.graph import run_graph, stream_graph, graph_app
from uvisbox_assistant.state import GraphState
from uvisbox_assistant.conversation import ConversationSession

__all__ = [
    "run_graph",
    "stream_graph",
    "graph_app",
    "GraphState",
    "ConversationSession",
    "__version__",
]
