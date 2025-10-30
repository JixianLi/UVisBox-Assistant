"""Error tracking functionality for debugging and troubleshooting."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class ErrorRecord:
    """Record of an error that occurred during execution."""

    error_id: int
    timestamp: datetime
    tool_name: str
    error_type: str
    error_message: str
    full_traceback: str
    user_facing_message: str
    auto_fixed: bool
    context: Optional[Dict] = None

    def summary(self) -> str:
        """
        Brief one-line summary for error list display.

        Returns:
            Formatted summary string like:
            [3] 10:23:45 - plot_boxplot: ValueError (failed)
        """
        status = "auto-fixed" if self.auto_fixed else "failed"
        time_str = self.timestamp.strftime('%H:%M:%S')
        return f"[{self.error_id}] {time_str} - {self.tool_name}: {self.error_type} ({status})"

    def detailed(self) -> str:
        """
        Detailed multi-line description with full traceback.

        Returns:
            Multi-line formatted string with all error details
        """
        lines = [
            f"Error ID: {self.error_id}",
            f"Timestamp: {self.timestamp.isoformat()}",
            f"Tool: {self.tool_name}",
            f"Type: {self.error_type}",
            f"Message: {self.error_message}",
            f"Auto-fixed: {self.auto_fixed}",
            f"User-facing message: {self.user_facing_message}",
            "",
            "Full Traceback:",
            self.full_traceback
        ]
        if self.context:
            lines.extend(["", "Context:", str(self.context)])
        return "\n".join(lines)
