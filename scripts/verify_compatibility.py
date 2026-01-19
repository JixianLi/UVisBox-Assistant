#!/usr/bin/env python3
"""
Verify backward compatibility after restructure.

Tests that all legacy import patterns still work via root __init__.py.
"""

def test_legacy_imports():
    """Test that legacy imports work."""

    # Core imports
    from uvisbox_assistant import graph_app, create_graph
    from uvisbox_assistant import ConversationSession

    # Data tools
    from uvisbox_assistant import (
        generate_ensemble_curves,
        load_csv_to_numpy,
        load_npy,
    )

    # Visualization tools
    from uvisbox_assistant import (
        plot_functional_boxplot,
        plot_curve_boxplot,
    )

    # Statistics tools (v0.3.0)
    from uvisbox_assistant import compute_functional_boxplot_statistics

    # Analyzer tools (v0.3.0)
    from uvisbox_assistant import generate_uncertainty_report

    # Error tracking
    from uvisbox_assistant import ErrorRecord

    # Config (now accessed via config module)
    from uvisbox_assistant import config
    _ = config.TEMP_DIR, config.TEST_DATA_DIR

    print("✓ All legacy imports successful!")
    return True

def test_new_imports():
    """Test that new structured imports work."""

    # Core
    from uvisbox_assistant.core import graph_app
    from uvisbox_assistant.session import ConversationSession

    # Tools
    from uvisbox_assistant.tools import generate_ensemble_curves
    from uvisbox_assistant.tools import plot_functional_boxplot
    from uvisbox_assistant.tools import compute_functional_boxplot_statistics
    from uvisbox_assistant.tools import generate_uncertainty_report

    # Errors
    from uvisbox_assistant.errors import ErrorRecord

    print("✓ All new imports successful!")
    return True

if __name__ == "__main__":
    print("Testing backward compatibility...")
    test_legacy_imports()
    print()
    print("Testing new structured imports...")
    test_new_imports()
    print()
    print("✓ All compatibility tests passed!")
