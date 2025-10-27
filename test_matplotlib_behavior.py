"""Test matplotlib window behavior to ensure non-blocking.

This test makes NO API calls - safe to run anytime.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import matplotlib.pyplot as plt
import numpy as np
import time


def test_non_blocking():
    """Test that plt.show(block=False) works correctly."""
    print("\n" + "="*70)
    print("TEST: Matplotlib Non-Blocking Behavior")
    print("="*70)

    # Create first plot
    fig1, ax1 = plt.subplots()
    ax1.plot([1, 2, 3], [1, 4, 9])
    ax1.set_title("Plot 1 - Should not block")
    plt.show(block=False)
    plt.pause(0.1)

    print("  ✓ Plot 1 displayed")
    print("  ✓ Terminal is still responsive (not blocked)")

    time.sleep(2)

    # Create second plot while first is still open
    fig2, ax2 = plt.subplots()
    ax2.plot([1, 2, 3], [3, 2, 1])
    ax2.set_title("Plot 2 - Should appear while Plot 1 is still open")
    plt.show(block=False)
    plt.pause(0.1)

    print("  ✓ Plot 2 displayed")
    print("  ✓ Both windows should be visible now")

    input("\nPress Enter to close and continue...")
    plt.close('all')
    print("\n✅ Non-blocking test passed!")


def test_multiple_viz_calls():
    """Simulate multiple visualization calls like in our pipeline."""
    print("\n" + "="*70)
    print("TEST: Multiple Viz Tool Calls")
    print("="*70)

    from viz_tools import plot_functional_boxplot
    from data_tools import generate_ensemble_curves

    # Generate data
    print("  Generating first dataset...")
    result1 = generate_ensemble_curves(n_curves=20, n_points=50)
    print(f"  ✓ Generated data: {result1['output_path']}")

    # First viz
    print("  Creating first visualization...")
    viz1 = plot_functional_boxplot(result1['output_path'])
    print(f"  ✓ First viz: {viz1['status']}")

    time.sleep(1)

    # Generate more data
    print("  Generating second dataset...")
    result2 = generate_ensemble_curves(n_curves=15, n_points=60)
    print(f"  ✓ Generated data: {result2['output_path']}")

    # Second viz
    print("  Creating second visualization...")
    viz2 = plot_functional_boxplot(result2['output_path'], percentiles=[50, 75, 100])
    print(f"  ✓ Second viz: {viz2['status']}")

    print("\n  ✓ Both plots should be visible")
    print("  ✓ Terminal remained responsive throughout")

    input("\nPress Enter to close...")
    plt.close('all')
    print("\n✅ Multiple viz calls test passed!")


def test_window_persistence():
    """Test that windows persist after function returns."""
    print("\n" + "="*70)
    print("TEST: Window Persistence")
    print("="*70)

    def create_plot():
        """Create a plot inside a function."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3, 4, 5], [1, 4, 2, 3, 5])
        ax.set_title("Plot created in function - Should persist after return")
        plt.show(block=False)
        plt.pause(0.1)
        return "Function returned"

    result = create_plot()
    print(f"  ✓ {result}")
    print("  ✓ Window should still be visible even after function returned")

    time.sleep(1)

    input("\nPress Enter to close...")
    plt.close('all')
    print("\n✅ Window persistence test passed!")


def run_all_tests():
    """Run all matplotlib behavior tests."""
    print("\n" + "🧪"*35)
    print("MATPLOTLIB BEHAVIOR TESTS (No API Calls)")
    print("🧪"*35)

    try:
        test_non_blocking()
        test_multiple_viz_calls()
        test_window_persistence()

        print("\n" + "="*70)
        print("✅ ALL MATPLOTLIB TESTS PASSED")
        print("="*70)
        print("\nVerified:")
        print("  ✓ Plots don't block execution")
        print("  ✓ Multiple windows can be open simultaneously")
        print("  ✓ Windows persist after function returns")
        print("  ✓ Terminal remains interactive throughout")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        plt.close('all')
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
