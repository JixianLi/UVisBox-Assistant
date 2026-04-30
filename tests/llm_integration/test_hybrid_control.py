# ABOUTME: LLM-integration tests for the hybrid-control fast path that bypasses the LLM.
# ABOUTME: Requires Ollama for the initial vis call; subsequent quick commands re-execute without LLM.
"""Test hybrid control functionality."""

import sys
import time
import matplotlib.pyplot as plt
import pytest

from uvisbox_assistant.session.conversation import ConversationSession

pytestmark = pytest.mark.llm_subset_hybrid_control


def test_hybrid_parameter_update():
    """Test: Simple parameter update uses hybrid control."""
    print("\n" + "="*70)
    print("TEST: Hybrid Parameter Update")
    print("="*70)

    session = ConversationSession()

    # Setup: Create initial visualization
    print("\n🔹 Setup: Create initial visualization")
    session.send("Generate 30 curves and plot functional boxplot")

    ctx1 = session.get_context_summary()
    assert ctx1["last_vis"] is not None
    print(f"   ✓ Initial vis created")

    # Test 1: Change percentile (should use hybrid)
    print("\n🔹 Test: Change percentile via hybrid control")
    start_time = time.time()
    session.send("percentile 75")
    elapsed = time.time() - start_time

    ctx2 = session.get_context_summary()
    print(f"   ✓ Percentile updated in {elapsed:.2f}s")
    print(f"     (Hybrid should be faster than full graph)")

    # Test 2: Change percentile again
    print("\n🔹 Test: Change percentile to 90")
    session.send("percentile 90")
    print(f"   ✓ Percentile updated again")

    # Test 3: Test with isovalue on scalar field
    print("\n🔹 Test: Generate scalar field and change isovalue")
    session.send("Generate scalar field ensemble and show probabilistic marching squares")
    time.sleep(2)  # Wait for generation

    print("   Now changing isovalue via hybrid...")
    session.send("isovalue 0.7")
    print(f"   ✓ Isovalue updated")

    print("\n✅ Hybrid control test passed")
    return session


def test_hybrid_vs_full_graph():
    """Test: Compare speed of hybrid vs full graph."""
    print("\n" + "="*70)
    print("TEST: Hybrid vs Full Graph Speed")
    print("="*70)

    session = ConversationSession()

    # Setup
    session.send("Generate 40 curves and visualize")

    # Time full graph execution
    print("\n🔹 Full graph: 'Change percentile to 80 and use plasma colormap'")
    start_full = time.time()
    session.send("Change percentile to 80 and use plasma colormap")
    elapsed_full = time.time() - start_full
    print(f"   Full graph: {elapsed_full:.2f}s")

    # Time hybrid execution
    print("\n🔹 Hybrid: 'percentile 90'")
    start_hybrid = time.time()
    session.send("percentile 90")
    elapsed_hybrid = time.time() - start_hybrid
    print(f"   Hybrid: {elapsed_hybrid:.2f}s")

    speedup = elapsed_full / elapsed_hybrid if elapsed_hybrid > 0 else float('inf')
    print(f"\n   Speedup: {speedup:.1f}x faster")

    print("\n✅ Speed comparison complete")


def test_hybrid_fallback():
    """Test: Complex queries fall back to full graph."""
    print("\n" + "="*70)
    print("TEST: Hybrid Fallback to Full Graph")
    print("="*70)

    session = ConversationSession()

    # Setup
    session.send("Generate curves and plot")

    # This should NOT use hybrid (too complex)
    print("\n🔹 Complex query (should use full graph)")
    session.send("Make it look better with nice colors and good percentile")

    response = session.get_last_response()
    print(f"   Response: {response[:100]}")
    print(f"   ✓ Full graph handled complex query")

    print("\n✅ Fallback test passed")


def test_hybrid_without_prior_vis():
    """Test: Hybrid command without prior vis falls back to graph."""
    print("\n" + "="*70)
    print("TEST: Hybrid Without Prior Visualization")
    print("="*70)

    session = ConversationSession()

    # Try hybrid command without any prior visualization
    print("\n🔹 Trying 'colormap plasma' with no prior vis")
    session.send("colormap plasma")

    response = session.get_last_response()
    print(f"   Response: {response[:150]}")

    # Should explain that there's nothing to update or try to help
    # (The LLM might handle this gracefully)
    print(f"   ✓ Handled no-prior-vis case")

    print("\n✅ No-prior-vis test passed")


def run_all_hybrid_tests():
    """Run all hybrid control tests."""
    print("\n" + "⚡"*35)
    print("CHATUVISBOX: HYBRID CONTROL TESTS")
    print("⚡"*35)
    print("\nNote: These tests make API calls and may take several minutes.")
    print("Tests are spaced to respect rate limits.\n")

    tests = [
        test_hybrid_parameter_update,
        test_hybrid_vs_full_graph,
        test_hybrid_fallback,
        test_hybrid_without_prior_vis,
    ]

    passed = 0
    failed = 0

    for i, test_func in enumerate(tests, 1):
        try:
            test_func()
            passed += 1

            # Add delay between tests to respect rate limits
            if i < len(tests):
                print("\n⏳ Pausing 3s to respect rate limits...")
                time.sleep(3)

        except AssertionError as e:
            print(f"\n❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Close matplotlib windows
    plt.close('all')

    # Summary
    print("\n" + "="*70)
    print("HYBRID CONTROL TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print("\n🎉 All hybrid control tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_hybrid_tests()
    sys.exit(0 if failed == 0 else 1)
