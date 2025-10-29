"""Test multi-turn conversations."""

import sys
import time
import matplotlib.pyplot as plt

from chatuvisbox.conversation import ConversationSession


def test_sequential_operations():
    """Test: User does operations in sequence."""
    print("\n" + "="*70)
    print("TEST: Sequential Operations")
    print("="*70)

    session = ConversationSession()

    # Turn 1: Generate data
    print("\n🔹 Turn 1: Generate data")
    session.send("Generate 30 curves with 100 points")
    response1 = session.get_last_response()
    print(f"   Response: {response1[:150]}")

    ctx = session.get_context_summary()
    assert ctx["current_data"] is not None, "Should have data path"
    print(f"   ✓ Data generated: {ctx['current_data']}")

    # Turn 2: Visualize using implicit reference
    print("\n🔹 Turn 2: Visualize (implicit reference)")
    session.send("Show me a functional boxplot of that")
    response2 = session.get_last_response()
    print(f"   Response: {response2[:150]}")

    ctx = session.get_context_summary()
    assert ctx["last_vis"] is not None, "Should have vis params"
    print(f"   ✓ Visualization created")

    # Turn 3: Modify vis
    print("\n🔹 Turn 3: Modify visualization")
    session.send("Change the percentile to 80")
    response3 = session.get_last_response()
    print(f"   Response: {response3[:150]}")

    print("\n✅ Sequential operations test passed")
    return session


def test_context_preservation():
    """Test: Context is preserved across turns."""
    print("\n" + "="*70)
    print("TEST: Context Preservation")
    print("="*70)

    session = ConversationSession()

    # Turn 1
    session.send("Generate 25 curves")
    ctx1 = session.get_context_summary()
    data_path_1 = ctx1["current_data"]

    # Turn 2: Should remember data from turn 1
    session.send("Plot it as functional boxplot")
    ctx2 = session.get_context_summary()

    assert ctx2["current_data"] == data_path_1, "Data path should be preserved"
    assert ctx2["turn_count"] == 2, "Should track turns"

    print(f"✓ Context preserved across {ctx2['turn_count']} turns")
    print(f"✓ Data path: {ctx2['current_data']}")

    # Turn 3: Generate new data
    session.send("Now generate a scalar field ensemble with 30x30 grid")
    ctx3 = session.get_context_summary()

    assert ctx3["current_data"] != data_path_1, "Should have new data path"
    print(f"✓ New data path: {ctx3['current_data']}")

    # Turn 4: Visualize new data
    session.send("Show probabilistic marching squares at isovalue 0.6")
    ctx4 = session.get_context_summary()

    assert ctx4["last_vis"] is not None, "Should have new vis"
    print(f"✓ New visualization created")

    print("\n✅ Context preservation test passed")
    return session


def test_pronoun_reference():
    """Test: Agent understands pronouns and references."""
    print("\n" + "="*70)
    print("TEST: Pronoun Reference")
    print("="*70)

    session = ConversationSession()

    # Generate data
    session.send("Generate some test curves")
    ctx1 = session.get_context_summary()
    data_path = ctx1["current_data"]

    # Use pronoun reference
    session.send("Plot it")  # "it" should refer to the generated data
    ctx2 = session.get_context_summary()

    assert ctx2["last_vis"] is not None, "Should have created vis"
    print(f"✓ Agent understood 'it' refers to {data_path}")

    # Another reference
    session.send("Make it prettier")  # Should modify last vis
    response = session.get_last_response()

    print(f"   Response: {response[:150]}")
    print("\n✅ Pronoun reference test passed")

    return session


def test_error_and_recovery_in_conversation():
    """Test: Error in middle of conversation doesn't break context."""
    print("\n" + "="*70)
    print("TEST: Error and Recovery in Conversation")
    print("="*70)

    session = ConversationSession()

    # Turn 1: Success
    session.send("Generate 20 curves")
    ctx1 = session.get_context_summary()
    assert ctx1["error_count"] == 0

    # Turn 2: Error
    session.send("Load nonexistent_file.csv")
    ctx2 = session.get_context_summary()
    print(f"   Error count after bad load: {ctx2['error_count']}")

    # Turn 3: Recovery - use previous data
    session.send("Actually, just plot the curves I generated earlier")
    ctx3 = session.get_context_summary()

    # Should have reset error count and created vis
    assert ctx3["error_count"] == 0, "Error count should reset after success"
    print(f"   ✓ Recovered: error_count = {ctx3['error_count']}")

    print("\n✅ Error and recovery test passed")
    return session


def test_multi_vis_same_data():
    """Test: Multiple visualizations from same data."""
    print("\n" + "="*70)
    print("TEST: Multiple Visualizations from Same Data")
    print("="*70)

    session = ConversationSession()

    # Generate data
    session.send("Generate 40 curves")
    ctx1 = session.get_context_summary()
    data_path = ctx1["current_data"]

    # Vis 1
    session.send("Show functional boxplot")
    ctx2 = session.get_context_summary()
    vis1 = ctx2["last_vis"]

    # Vis 2 from same data - be more explicit about using same data
    session.send("Now show curve boxplot from that same data with percentiles 50, 75, 90")
    ctx3 = session.get_context_summary()
    vis2 = ctx3["last_vis"]

    assert ctx3["current_data"] == data_path, "Should still use same data"
    assert vis2 is not None, "Should have created second visualization"
    assert vis1["_tool_name"] != vis2["_tool_name"], "Should have different vis types"

    print(f"   ✓ Created 2 visualizations from {data_path}")
    print("\n✅ Multiple vis test passed")

    return session


def run_all_multiturn_tests():
    """Run all multi-turn conversation tests."""
    print("\n" + "💬 "*35)
    print("CHATUVISBOX: MULTI-TURN CONVERSATION TESTS")
    print("💬 "*35)
    print("\nNote: These tests make API calls and may take several minutes.")
    print("Tests are spaced to respect rate limits.\n")

    tests = [
        test_sequential_operations,
        test_context_preservation,
        test_pronoun_reference,
        test_error_and_recovery_in_conversation,
        test_multi_vis_same_data,
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
    print("MULTI-TURN TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print("\n🎉 All multi-turn conversation tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_multiturn_tests()
    sys.exit(0 if failed == 0 else 1)
