"""Logging utilities for debugging."""
import logging
from chatuvisbox import config

# Configure logging (LOG_DIR already created in config.py)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_DIR / "chatuvisbox.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("chatuvisbox")


def log_tool_call(tool_name: str, args: dict):
    """Log a tool call."""
    logger.info(f"Tool call: {tool_name} with args {args}")


def log_tool_result(tool_name: str, result: dict):
    """Log a tool result."""
    status = result.get("status", "unknown")
    message = result.get("message", "")
    logger.info(f"Tool result: {tool_name} -> {status}: {message}")


def log_error(error_msg: str):
    """Log an error."""
    logger.error(error_msg)


def log_state_update(field: str, value):
    """Log a state update."""
    logger.debug(f"State update: {field} = {value}")
