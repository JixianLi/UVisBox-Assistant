"""Test session management features."""

from uvisbox_assistant.session.conversation import ConversationSession
import matplotlib.pyplot as plt
from pathlib import Path
from uvisbox_assistant import config
import sys
import time


def test_clear_session():
    """Test: Clear session removes temp files."""
    print("\n" + "="*70)
    print("TEST: Clear Session")
    print("="*70)

    session = ConversationSession()

    # Generate some data
    print("\n🔹 Generating data files...")
    session.send("Generate 20 curves")
    time.sleep(2)  # Allow processing
    session.send("Generate scalar field 30x30")
    time.sleep(2)  # Allow processing

    files_before = list(config.TEMP_DIR.glob("_temp_*"))
    print(f"\n📁 Files before clear: {len(files_before)}")

    # Clear session
    session.clear()

    files_after = list(config.TEMP_DIR.glob("_temp_*"))
    print(f"📁 Files after clear: {len(files_after)}")

    assert len(files_after) == 0, "Should have removed all temp files"
    assert session.state is None, "Should have reset state"

    print("\n✅ Clear session test passed")


def test_reset_vs_clear():
    """Test: Reset preserves files, clear removes them."""
    print("\n" + "="*70)
    print("TEST: Reset vs Clear")
    print("="*70)

    session = ConversationSession()

    # Generate data
    print("\n🔹 Generating data...")
    session.send("Generate 15 curves")
    time.sleep(2)
    ctx1 = session.get_context_summary()
    data_path = ctx1["current_data"]

    print(f"\n📁 Data path: {data_path}")
    assert Path(data_path).exists(), "Data file should exist"

    # Reset (preserves files)
    session.reset()
    assert session.state is None, "State should be reset"
    assert Path(data_path).exists(), "Data file should still exist after reset"
    print("✓ Reset preserved files")

    # Clear (removes files)
    session2 = ConversationSession()
    session2.send("Generate 15 curves")
    time.sleep(2)
    ctx2 = session2.get_context_summary()
    data_path2 = ctx2["current_data"]

    session2.clear()
    assert not Path(data_path2).exists(), "Data file should be removed after clear"
    print("✓ Clear removed files")

    # Clean up remaining files
    from uvisbox_assistant.tools.data_tools import clear_session
    clear_session()

    print("\n✅ Reset vs Clear test passed")


def test_session_stats():
    """Test: Session statistics are tracked correctly."""
    print("\n" + "="*70)
    print("TEST: Session Statistics")
    print("="*70)

    session = ConversationSession()

    # Initial stats
    stats0 = session.get_stats()
    print(f"\nInitial stats: {stats0}")
    assert stats0["turns"] == 0

    # After some operations
    print("\n🔹 Performing operations...")
    session.send("Generate 30 curves and plot functional boxplot")
    time.sleep(3)

    stats = session.get_stats()
    print(f"\nFinal stats: {stats}")

    assert stats["turns"] == 1
    assert stats["current_data"] is True
    assert stats["current_vis"] is True, f"Expected current_vis=True but got {stats['current_vis']}. Stats: {stats}"

    # Clean up
    session.clear()

    print("\n✅ Session stats test passed")


def run_all_session_tests():
    """Run all session management tests."""
    print("\n" + "🗂️ "*35)
    print("CHATUVISBOX: SESSION MANAGEMENT TESTS")
    print("🗂️ "*35)
    print("\nNote: These tests make API calls and may take several minutes.")
    print("Tests are spaced to respect rate limits.\n")

    tests = [
        test_clear_session,
        test_reset_vs_clear,
        test_session_stats,
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
    print("SESSION MANAGEMENT TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")

    if failed == 0:
        print("\n🎉 All session management tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_session_tests()
    sys.exit(0 if failed == 0 else 1)
