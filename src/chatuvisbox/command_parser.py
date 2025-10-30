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

    # Pattern 8: "median color <color>"
    match = re.match(r'median\s+color\s+(\w+)', text)
    if match:
        return SimpleCommand('median_color', match.group(1))

    # Pattern 9: "median width <number>"
    match = re.match(r'median\s+width\s+(\d+\.?\d*)', text)
    if match:
        value = float(match.group(1))
        return SimpleCommand('median_width', value)

    # Pattern 10: "median alpha <number>"
    match = re.match(r'median\s+alpha\s+(\d+\.?\d*)', text)
    if match:
        value = float(match.group(1))
        return SimpleCommand('median_alpha', value)

    # Pattern 11: "outliers color <color>"
    match = re.match(r'outliers\s+color\s+(\w+)', text)
    if match:
        return SimpleCommand('outliers_color', match.group(1))

    # Pattern 12: "outliers width <number>"
    match = re.match(r'outliers\s+width\s+(\d+\.?\d*)', text)
    if match:
        value = float(match.group(1))
        return SimpleCommand('outliers_width', value)

    # Pattern 13: "outliers alpha <number>"
    match = re.match(r'outliers\s+alpha\s+(\d+\.?\d*)', text)
    if match:
        value = float(match.group(1))
        return SimpleCommand('outliers_alpha', value)

    # Pattern 14: "method <fdb|mfdb>"
    match = re.match(r'method\s+(fdb|mfdb)', text)
    if match:
        return SimpleCommand('method', match.group(1))

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
    # Note: 'colormap' can map to either 'colormap' (for probabilistic_marching_squares)
    # or 'percentile_colormap' (for boxplot functions)
    # The hybrid_control.py will filter based on function signature
    param_mapping = {
        'colormap': ['colormap', 'percentile_colormap'],  # Try both
        'percentiles': 'percentiles',  # For boxplot functions (list)
        'isovalue': 'isovalue',
        'show_median': 'show_median',
        'median_color': 'median_color',
        'median_width': 'median_width',
        'median_alpha': 'median_alpha',
        'show_outliers': 'show_outliers',
        'outliers_color': 'outliers_color',
        'outliers_width': 'outliers_width',
        'outliers_alpha': 'outliers_alpha',
        'scale': 'scale',
        'alpha': 'alpha',
        'method': 'method',
    }

    mapping = param_mapping.get(command.param_name, command.param_name)

    # If mapping is a list, try all possibilities
    if isinstance(mapping, list):
        for param_name in mapping:
            updated[param_name] = command.value
    else:
        updated[mapping] = command.value

    # Special handling: if 'percentiles' was set with a single-item list,
    # also set 'percentile' (for squid_glyph_2D) with the extracted value
    if command.param_name == 'percentiles' and isinstance(command.value, list) and len(command.value) == 1:
        updated['percentile'] = command.value[0]

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
        "median color blue",
        "median width 2.5",
        "median alpha 0.8",
        "outliers color black",
        "outliers width 1.5",
        "outliers alpha 1.0",
        "method fdb",
        "method mfdb",
        "generate some curves",  # Should return None
    ]

    for inp in test_inputs:
        result = parse_simple_command(inp)
        print(f"{inp:30} -> {result}")
