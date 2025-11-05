"""Error handling infrastructure."""

from uvisbox_assistant.errors.error_tracking import ErrorRecord
from uvisbox_assistant.errors.error_interpretation import interpret_uvisbox_error, format_error_with_hint

__all__ = [
    "ErrorRecord",
    "interpret_uvisbox_error",
    "format_error_with_hint",
]
