"""Conversation management for multi-turn interactions."""

from typing import Optional, Dict, List
from datetime import datetime
from uvisbox_assistant.state import GraphState, create_initial_state
from uvisbox_assistant.graph import graph_app
from uvisbox_assistant.hybrid_control import execute_simple_command, is_hybrid_eligible
from uvisbox_assistant.error_tracking import ErrorRecord
from uvisbox_assistant.output_control import set_session, vprint
from uvisbox_assistant.error_interpretation import interpret_uvisbox_error, format_error_with_hint
from langchain_core.messages import HumanMessage, AIMessage


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

        # Debug and verbose mode flags
        self.debug_mode: bool = False      # Verbose error output with tracebacks
        self.verbose_mode: bool = False    # Show internal state messages

        # Error tracking
        self.error_history: List[ErrorRecord] = []
        self.max_error_history: int = 20
        self._next_error_id: int = 1

        # Auto-fix tracking
        self.auto_fixed_errors: set = set()  # IDs of auto-fixed errors

        # Register this session for verbose mode checks
        set_session(self)

    def send(self, user_message: str) -> GraphState:
        """
        Send a user message and get response.

        Checks for simple commands first (hybrid control).
        Falls back to full graph execution if needed.

        Args:
            user_message: User's input text

        Returns:
            Updated state after graph execution
        """
        self.turn_count += 1

        # Try hybrid control first (only if we have existing state)
        if self.state and is_hybrid_eligible(user_message):
            success, updated_params, message = execute_simple_command(
                user_message,
                self.state
            )

            if success:
                # Update state directly without graph execution
                self.state["last_vis_params"] = updated_params
                self.state["error_count"] = 0

                # Add messages to maintain conversation history
                self.state["messages"].append(HumanMessage(content=user_message))
                self.state["messages"].append(AIMessage(content=message))

                vprint(f"[HYBRID] Fast path executed: {message}")
                return self.state

        # Fall back to full graph execution
        if self.state is None:
            # First turn - create initial state
            self.state = create_initial_state(user_message)
        else:
            # Subsequent turn - add to existing state
            self.state["messages"].append(HumanMessage(content=user_message))

        # Run graph with current state
        self.state = graph_app.invoke(self.state)

        # Check for auto-fix markers in state
        if "_auto_fixed_error_id" in self.state:
            error_id = self.state["_auto_fixed_error_id"]
            self.mark_error_auto_fixed(error_id)
            # Clean up marker
            del self.state["_auto_fixed_error_id"]

        # Process tool messages to record errors
        self._process_tool_errors()

        return self.state

    def _process_tool_errors(self):
        """Process tool messages to detect and record errors."""
        if not self.state:
            return

        from langchain_core.messages import ToolMessage

        for message in self.state["messages"]:
            if isinstance(message, ToolMessage):
                try:
                    import json
                    # Try to parse message content as JSON
                    if isinstance(message.content, str):
                        try:
                            content = json.loads(message.content)
                        except json.JSONDecodeError:
                            # Content might be dict-like string representation
                            import ast
                            try:
                                content = ast.literal_eval(message.content)
                            except (ValueError, SyntaxError):
                                continue
                    else:
                        content = message.content

                    # Check if this is an error message
                    if isinstance(content, dict) and content.get("status") == "error":
                        # Check if we have error details
                        if "_error_details" in content:
                            error_details = content["_error_details"]
                            error = error_details.get("exception")
                            traceback_str = error_details.get("traceback", "")

                            # Only record if we haven't already recorded this error
                            # (avoid duplicates on multiple send() calls with same state)
                            tool_name = getattr(message, 'name', 'unknown_tool')

                            # Record error with interpretation
                            if error:
                                error_record = self.record_error(
                                    tool_name=tool_name,
                                    error=error,
                                    traceback_str=traceback_str,
                                    user_message=content.get("message", str(error)),
                                    auto_fixed=False
                                )

                                # Store error ID in state for auto-fix detection
                                self.state["_pending_error_id"] = error_record.error_id

                except Exception:
                    # Silently skip malformed messages
                    pass

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
                "statistics": None,
                "analysis": None,
                "session_files": [],
                "error_count": 0,
                "message_count": 0
            }

        return {
            "turn_count": self.turn_count,
            "current_data": self.state.get("current_data_path"),
            "last_vis": self.state.get("last_vis_params"),
            "statistics": "computed" if self.state.get("processed_statistics") else None,
            "analysis": self.state.get("analysis_type") if self.state.get("analysis_report") else None,
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

    def clear(self):
        """Clear session data and temporary files."""
        from uvisbox_assistant.data_tools import clear_session

        # Clear temp files
        result = clear_session()
        print(f"🧹 {result['message']}")

        # Reset state
        self.reset()

    def get_session_files(self) -> list:
        """Get list of session files."""
        if not self.state:
            return []
        return self.state.get("session_files", [])

    def get_stats(self) -> dict:
        """Get session statistics."""
        ctx = self.get_context_summary()
        return {
            "turns": ctx["turn_count"],
            "messages": ctx["message_count"],
            "files_created": len(ctx.get("session_files", [])),
            "current_data": ctx.get("current_data") is not None,
            "current_vis": ctx.get("last_vis") is not None,
        }

    def record_error(
        self,
        tool_name: str,
        error: Exception,
        traceback_str: str,
        user_message: str,
        auto_fixed: bool = False,
        context: Optional[Dict] = None
    ) -> ErrorRecord:
        """
        Record an error in history with enhanced interpretation.

        Args:
            tool_name: Name of the tool that failed
            error: The exception object
            traceback_str: Full traceback string from traceback.format_exc()
            user_message: User-friendly error message
            auto_fixed: Whether this error was automatically fixed
            context: Optional context dict (e.g., state snapshot)

        Returns:
            ErrorRecord object
        """
        # Interpret error with debug mode context
        interpreted_msg, debug_hint = interpret_uvisbox_error(
            error,
            traceback_str,
            debug_mode=self.debug_mode
        )

        # Format message with hint if available
        enhanced_msg = format_error_with_hint(interpreted_msg, debug_hint)

        record = ErrorRecord(
            error_id=self._next_error_id,
            timestamp=datetime.now(),
            tool_name=tool_name,
            error_type=type(error).__name__,
            error_message=str(error),
            full_traceback=traceback_str,
            user_facing_message=enhanced_msg,  # Use enhanced message
            auto_fixed=auto_fixed,
            context=context
        )

        self.error_history.append(record)
        self._next_error_id += 1

        # Keep only last N errors
        if len(self.error_history) > self.max_error_history:
            self.error_history.pop(0)

        return record

    def get_error(self, error_id: int) -> Optional[ErrorRecord]:
        """
        Get error by ID.

        Args:
            error_id: ID of error to retrieve

        Returns:
            ErrorRecord or None if not found
        """
        for err in self.error_history:
            if err.error_id == error_id:
                return err
        return None

    def get_last_error(self) -> Optional[ErrorRecord]:
        """
        Get most recent error.

        Returns:
            ErrorRecord or None if no errors
        """
        return self.error_history[-1] if self.error_history else None

    def mark_error_auto_fixed(self, error_id: int):
        """
        Mark an error as auto-fixed.

        Args:
            error_id: ID of the error to mark
        """
        self.auto_fixed_errors.add(error_id)
        vprint(f"[AUTO-FIX] Marked error {error_id} as auto-fixed")

    def is_error_auto_fixed(self, error_id: int) -> bool:
        """
        Check if error was auto-fixed.

        Args:
            error_id: ID of error to check

        Returns:
            True if error was auto-fixed, False otherwise
        """
        return error_id in self.auto_fixed_errors

    def get_analysis_summary(self) -> Optional[str]:
        """
        Get summary of current analysis state.

        Returns:
            Formatted string with analysis info, or None if no analysis
        """
        if not self.state:
            return None

        has_stats = self.state.get("processed_statistics") is not None
        has_report = self.state.get("analysis_report") is not None

        if not has_stats and not has_report:
            return None

        lines = ["📊 Analysis State:"]

        if has_stats:
            stats = self.state["processed_statistics"]
            data_shape = stats.get("data_shape", {})
            n_curves = data_shape.get("n_curves", "?")
            n_points = data_shape.get("n_points", "?")
            lines.append(f"  ✓ Statistics computed: {n_curves} curves, {n_points} points")

            median = stats.get("median", {})
            lines.append(f"  - Median trend: {median.get('trend', 'unknown')}")

            outliers = stats.get("outliers", {})
            outlier_count = outliers.get("count", 0)
            lines.append(f"  - Outliers: {outlier_count}")

        if has_report:
            report = self.state["analysis_report"]
            analysis_type = self.state.get("analysis_type", "unknown")
            word_count = len(report.split())
            lines.append(f"  ✓ Report generated: {analysis_type} ({word_count} words)")
            lines.append(f"  - Preview: {report[:100]}...")

        return "\n".join(lines)
