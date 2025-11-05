"""State definition for the LangGraph workflow"""
from typing import TypedDict, List, Optional, Annotated, Dict
from langchain_core.messages import BaseMessage
import operator


class GraphState(TypedDict):
    """
    State for the UVisBox-Assistant conversation graph.

    Attributes:
        messages: List of conversation messages (user, assistant, tool messages)
        current_data_path: Path to the most recently created/loaded .npy data file
        last_vis_params: Parameters used in the last visualization call (for hybrid control)
        session_files: List of temporary files created during this session
        error_count: Number of consecutive errors (for circuit breaking)
        tool_execution_sequence: List of tool execution records for auto-fix detection
        last_error_tool: Name of tool that last failed (for auto-fix detection)
        last_error_id: ID of last error (for auto-fix detection)

        # NEW: Uncertainty analysis fields (v0.3.0)
        raw_statistics: Raw output from functional_boxplot_summary_statistics (numpy arrays)
        processed_statistics: LLM-friendly structured summary from statistics_tool
        analysis_report: Generated text report from analyzer_tool
        analysis_type: Report format - "inline" | "quick" | "detailed" | None
    """
    # Messages list - appended to over time
    messages: Annotated[List[BaseMessage], operator.add]

    # Single-value state fields (overwritten, not appended)
    current_data_path: Optional[str]
    last_vis_params: Optional[dict]
    session_files: List[str]
    error_count: int

    # Auto-fix detection fields
    tool_execution_sequence: List[Dict]
    last_error_tool: Optional[str]
    last_error_id: Optional[int]

    # NEW: Uncertainty analysis state (v0.3.0)
    raw_statistics: Optional[dict]
    processed_statistics: Optional[dict]
    analysis_report: Optional[str]
    analysis_type: Optional[str]


def create_initial_state(user_message: str) -> GraphState:
    """
    Create the initial state for a new conversation turn.

    Args:
        user_message: The user's input message

    Returns:
        Initial GraphState
    """
    from langchain_core.messages import HumanMessage

    return GraphState(
        messages=[HumanMessage(content=user_message)],
        current_data_path=None,
        last_vis_params=None,
        session_files=[],
        error_count=0,
        tool_execution_sequence=[],
        last_error_tool=None,
        last_error_id=None,
        # NEW: Initialize analysis state (v0.3.0)
        raw_statistics=None,
        processed_statistics=None,
        analysis_report=None,
        analysis_type=None
    )


def update_state_with_data(state: GraphState, data_path: str) -> dict:
    """
    Update state after successful data tool execution.

    Returns:
        Dict of updates to merge into state
    """
    return {
        "current_data_path": data_path,
        "session_files": state["session_files"] + [data_path],
        "error_count": 0  # Reset error count on success
    }


def update_state_with_vis(state: GraphState, vis_params: dict) -> dict:
    """
    Update state after successful vis tool execution.

    Returns:
        Dict of updates to merge into state
    """
    return {
        "last_vis_params": vis_params,
        "error_count": 0  # Reset error count on success
    }


def increment_error_count(state: GraphState) -> dict:
    """
    Increment error count after tool failure.

    Returns:
        Dict of updates to merge into state
    """
    return {
        "error_count": state.get("error_count", 0) + 1
    }


def update_state_with_statistics(state: GraphState, raw_stats: dict, processed_stats: dict) -> dict:
    """
    Update state after successful statistics tool execution.

    Args:
        state: Current graph state
        raw_stats: Raw output from functional_boxplot_summary_statistics (numpy arrays)
        processed_stats: Processed LLM-friendly summary

    Returns:
        Dict of updates to merge into state
    """
    return {
        "raw_statistics": raw_stats,
        "processed_statistics": processed_stats,
        "error_count": 0  # Reset error count on success
    }


def update_state_with_analysis(state: GraphState, report: str, analysis_type: str) -> dict:
    """
    Update state after successful analyzer tool execution.

    Args:
        state: Current graph state
        report: Generated text report
        analysis_type: Type of report ("inline" | "quick" | "detailed")

    Returns:
        Dict of updates to merge into state
    """
    return {
        "analysis_report": report,
        "analysis_type": analysis_type,
        "error_count": 0  # Reset error count on success
    }
