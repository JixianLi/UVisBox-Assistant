"""Control verbose output based on session settings."""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..session.conversation import ConversationSession

# Global session reference for accessing verbose_mode
# Set by conversation.py when session is created
_current_session: Optional['ConversationSession'] = None


def set_session(session) -> None:
    """
    Set the current session for verbose mode checks.

    Args:
        session: ConversationSession instance
    """
    global _current_session
    _current_session = session


def vprint(message: str, force: bool = False) -> None:
    """
    Print message only if verbose mode is enabled.

    Args:
        message: Message to print
        force: If True, always print regardless of verbose mode

    Example:
        vprint("[DATA TOOL] Calling generate_curves")  # Only if verbose
        vprint("✅ Success!", force=True)  # Always print
    """
    global _current_session
    if force or (_current_session and _current_session.verbose_mode):
        print(message)


def is_verbose() -> bool:
    """
    Check if verbose mode is enabled.

    Returns:
        True if verbose mode is on, False otherwise
    """
    global _current_session
    return _current_session and _current_session.verbose_mode
