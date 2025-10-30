"""
ChatUVisBox: Natural language interface for UVisBox uncertainty visualization.

A LangGraph-based conversational agent that translates natural language requests
into data processing and visualization operations using the UVisBox library.
"""

__version__ = "0.1.1"

# Expose main API
from chatuvisbox.graph import run_graph, stream_graph, graph_app
from chatuvisbox.state import GraphState
from chatuvisbox.conversation import ConversationSession

__all__ = [
    "run_graph",
    "stream_graph",
    "graph_app",
    "GraphState",
    "ConversationSession",
    "__version__",
]
