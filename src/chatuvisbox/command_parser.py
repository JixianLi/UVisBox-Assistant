"""Parse simple direct commands for hybrid control."""

import re
from typing import Optional


class SimpleCommand:
    """Represents a simple parameter update command."""

    def __init__(self, param_name: str, value):
        self.param_name = param_name
        self.value = value

    def __repr__(self):
        return f"SimpleCommand({self.param_name}={self.value})"


def parse_simple_command(user_input: str) -> Optional[SimpleCommand]:
    """
    Try to parse user input as a simple parameter command.

    Simple commands are:
    - Single parameter updates
    - No ambiguity
    - No need for LLM interpretation

    Args:
        user_input: User's input string

    Returns:
        SimpleCommand if recognized, None otherwise
    """
    # Normalize input
    text = user_input.strip().lower()

    # Pattern 1: "colormap <name>"
    match = re.match(r'colormap\s+(\w+)', text)
    if match:
        return SimpleCommand('colormap', match.group(1))

    # Pattern 2: "percentile <number>"
    match = re.match(r'percentile\s+(\d+\.?\d*)', text)
    if match:
        value = float(match.group(1))
        return SimpleCommand('percentiles', [value])  # Return as list for percentiles parameter

    # Pattern 3: "isovalue <number>"
    match = re.match(r'isovalue\s+(\d+\.?\d*)', text)
    if match:
        value = float(match.group(1))
        return SimpleCommand('isovalue', value)

    # Pattern 4: "show median" / "hide median"
    if text in ['show median', 'show the median']:
        return SimpleCommand('show_median', True)
    if text in ['hide median', 'hide the median']:
        return SimpleCommand('show_median', False)

    # Pattern 5: "show outliers" / "hide outliers"
    if text in ['show outliers', 'show the outliers']:
        return SimpleCommand('show_outliers', True)
    if text in ['hide outliers', 'hide the outliers']:
        return SimpleCommand('show_outliers', False)

    # Pattern 6: "scale <number>"
    match = re.match(r'scale\s+(\d+\.?\d*)', text)
    if match:
        value = float(match.group(1))
        return SimpleCommand('scale', value)

    # Pattern 7: "alpha <number>"
    match = re.match(r'alpha\s+(\d+\.?\d*)', text)
    if match:
        value = float(match.group(1))
        return SimpleCommand('alpha', value)

    # Not a simple command
    return None


def apply_command_to_params(command: SimpleCommand, current_params: dict) -> dict:
    """
    Apply a simple command to existing vis parameters.

    Args:
        command: The parsed command
        current_params: Current visualization parameters

    Returns:
        Updated parameters
    """
    updated = current_params.copy()

    # Map command param names to vis tool param names
    param_mapping = {
        'colormap': 'colormap',
        'percentiles': 'percentiles',
        'isovalue': 'isovalue',
        'show_median': 'show_median',
        'show_outliers': 'show_outliers',
        'scale': 'scale',
        'alpha': 'alpha',
    }

    param_name = param_mapping.get(command.param_name, command.param_name)
    updated[param_name] = command.value

    return updated


# Test cases
if __name__ == "__main__":
    test_inputs = [
        "colormap plasma",
        "percentile 75",
        "isovalue 0.8",
        "show median",
        "hide outliers",
        "scale 0.5",
        "alpha 0.7",
        "generate some curves",  # Should return None
    ]

    for inp in test_inputs:
        result = parse_simple_command(inp)
        print(f"{inp:30} -> {result}")
