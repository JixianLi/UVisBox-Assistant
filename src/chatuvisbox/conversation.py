"""Conversation management for multi-turn interactions."""

from typing import Optional
from chatuvisbox.state import GraphState, create_initial_state
from chatuvisbox.graph import graph_app
from langchain_core.messages import HumanMessage


class ConversationSession:
    """
    Manages a multi-turn conversation session.

    Maintains state across multiple user inputs, tracking conversation
    history, data paths, visualization parameters, and error count.

    Usage:
        session = ConversationSession()
        session.send("Generate 30 curves")
        session.send("Plot them as functional boxplot")
    """

    def __init__(self):
        """Initialize a new conversation session."""
        self.state: Optional[GraphState] = None
        self.turn_count = 0

    def send(self, user_message: str) -> GraphState:
        """
        Send a user message and get response.

        Args:
            user_message: User's input text

        Returns:
            Updated state after graph execution
        """
        self.turn_count += 1

        if self.state is None:
            # First turn - create initial state
            self.state = create_initial_state(user_message)
        else:
            # Subsequent turn - add to existing state
            self.state["messages"].append(HumanMessage(content=user_message))

        # Run graph with current state
        self.state = graph_app.invoke(self.state)

        return self.state

    def get_last_response(self) -> str:
        """
        Get the last assistant response from conversation history.

        Returns:
            The most recent assistant message, or empty string if none found
        """
        if not self.state:
            return ""

        # Search backwards for the most recent AI message
        for msg in reversed(self.state["messages"]):
            if hasattr(msg, "content") and msg.content:
                if "AI" in msg.__class__.__name__:
                    return msg.content

        return ""

    def get_context_summary(self) -> dict:
        """
        Get a summary of current conversation context.

        Returns:
            Dictionary with:
                - turn_count: Number of turns in conversation
                - current_data: Path to current data file
                - last_vis: Last visualization parameters
                - session_files: List of files created this session
                - error_count: Current error count
                - message_count: Total number of messages
        """
        if not self.state:
            return {
                "turn_count": 0,
                "current_data": None,
                "last_vis": None,
                "session_files": [],
                "error_count": 0,
                "message_count": 0
            }

        return {
            "turn_count": self.turn_count,
            "current_data": self.state.get("current_data_path"),
            "last_vis": self.state.get("last_vis_params"),
            "session_files": self.state.get("session_files", []),
            "error_count": self.state.get("error_count", 0),
            "message_count": len(self.state["messages"])
        }

    def reset(self):
        """Reset the conversation session to initial state."""
        self.state = None
        self.turn_count = 0

    def get_state(self) -> Optional[GraphState]:
        """
        Get the current state (for debugging/inspection).

        Returns:
            Current GraphState or None if no conversation started
        """
        return self.state
