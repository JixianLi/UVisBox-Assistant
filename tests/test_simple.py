"""
Quick sanity check test.

Run this to verify the system works end-to-end.
Single prompt → single output, no complex scenarios.

Usage:
    python tests/test_simple.py
    pytest tests/test_simple.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from uvisbox_assistant.graph import create_graph
from uvisbox_assistant.state import create_initial_state
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt


def test_simple_end_to_end():
    """
    Test: Single prompt generates data and creates visualization.

    This is the simplest possible test - if this passes, core functionality works.
    """
    print("\n" + "="*70)
    print("SIMPLE SANITY CHECK")
    print("="*70)

    # Create graph
    graph = create_graph()

    # Simple prompt that exercises both data generation and visualization
    prompt = "Generate 20 curves and plot functional boxplot"

    print(f"\nPrompt: {prompt}")
    print("\n🔹 Processing...")

    # Run the graph with proper state initialization
    initial_state = create_initial_state(prompt)
    result = graph.invoke(initial_state)

    # Verify success
    assert result is not None, "Result should not be None"
    assert "current_data_path" in result, "Should have current_data_path in result"
    assert result.get("current_data_path") is not None, "Should have generated data"
    assert "last_vis_params" in result, "Should have last_vis_params in result"
    assert result.get("last_vis_params") is not None, "Should have created visualization"

    # Get last message from AI
    messages = result.get("messages", [])
    if messages:
        last_message = messages[-1]
        response = last_message.content if hasattr(last_message, 'content') else str(last_message)
        print(f"\n✓ Response: {response[:200]}...")

    # Cleanup
    plt.close('all')

    print("\n✅ SIMPLE TEST PASSED")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_simple_end_to_end()
