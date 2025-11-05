"""Hybrid control system for fast parameter updates."""

from typing import Optional, Dict, Tuple
from uvisbox_assistant.session.command_parser import parse_simple_command, apply_command_to_params, SimpleCommand
from uvisbox_assistant.tools.vis_tools import VIS_TOOLS
from uvisbox_assistant.utils.output_control import vprint


def execute_simple_command(
    command_str: str,
    current_state: dict
) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Try to execute a command as a simple parameter update or report retrieval.

    Args:
        command_str: User's command string
        current_state: Current conversation state with last_vis_params and analysis_reports

    Returns:
        Tuple of (success, result, message)
        - success: True if command was handled, False if needs full graph
        - result: Result from operation (updated_params dict OR report_text str)
        - message: Status message
    """
    # Try to parse as simple command
    command = parse_simple_command(command_str)

    if command is None:
        return False, None, "Not a simple command"

    # Route to appropriate handler
    if command.param_name == 'report_type':
        return execute_report_retrieval(command, current_state)

    # Existing visualization parameter update logic continues below...
    # Need existing vis params to update
    last_vis_params = current_state.get("last_vis_params")

    if not last_vis_params:
        return False, None, "No previous visualization to update"

    # Extract the tool name and data path from last vis
    vis_tool_name = last_vis_params.get("_tool_name")
    data_path = last_vis_params.get("data_path")

    if not vis_tool_name or not data_path:
        return False, None, "Cannot determine visualization to update"

    # Apply command to params
    updated_params = apply_command_to_params(command, last_vis_params)

    # Execute vis tool directly
    vis_func = VIS_TOOLS.get(vis_tool_name)

    if not vis_func:
        return False, None, f"Unknown vis tool: {vis_tool_name}"

    vprint(f"[HYBRID] Executing {vis_tool_name} with updated params")

    # Remove internal fields before calling tool
    call_params = {k: v for k, v in updated_params.items() if not k.startswith('_')}

    # Get the function signature to check valid parameters
    import inspect
    sig = inspect.signature(vis_func)
    valid_params = set(sig.parameters.keys())

    # Filter out parameters that aren't valid for this function
    filtered_params = {k: v for k, v in call_params.items() if k in valid_params}

    # Check if the requested parameter is valid for this vis tool
    requested_param = command.param_name
    if requested_param not in valid_params:
        return False, None, f"Parameter '{requested_param}' not available for {vis_tool_name}"

    result = vis_func(**filtered_params)

    if result.get("status") == "success":
        # Update state (caller should do this)
        updated_params['_tool_name'] = vis_tool_name
        return True, updated_params, f"Updated {command.param_name} to {command.value}"
    else:
        return False, None, f"Error updating: {result.get('message')}"


def execute_report_retrieval(
    command: SimpleCommand,
    current_state: dict
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Retrieve a specific report type from state.

    Args:
        command: Parsed simple command with param_name='report_type'
        current_state: Current conversation state

    Returns:
        Tuple of (success, report_text, message)
        - success: True if report retrieved, False if not available
        - report_text: The report content (str)
        - message: Status message
    """
    if command.param_name != 'report_type':
        return False, None, "Not a report retrieval command"

    analysis_reports = current_state.get("analysis_reports")

    if not analysis_reports:
        return False, None, "No analysis reports available yet"

    report_type = command.value
    report_text = analysis_reports.get(report_type)

    if not report_text:
        return False, None, f"Report type '{report_type}' not found"

    return True, report_text, f"Retrieved {report_type} report"


def is_hybrid_eligible(user_input: str) -> bool:
    """
    Quick check if input might be eligible for hybrid control.

    Args:
        user_input: User's input

    Returns:
        True if might be simple command
    """
    command = parse_simple_command(user_input)
    return command is not None
