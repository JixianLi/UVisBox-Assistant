"""
Validation script for Phase 6: ConversationSession.

Quick checks to ensure the implementation is correct before running full tests.
"""

def test_imports():
    """Test that all Phase 6 components can be imported."""
    print("✓ Testing imports...")

    # Test direct import
    from chatuvisbox.conversation import ConversationSession

    # Test package-level import
    from chatuvisbox import ConversationSession as CS

    assert ConversationSession == CS, "Package-level import should match direct import"

    print("  ✓ ConversationSession imports correctly")
    return True


def test_instantiation():
    """Test that ConversationSession can be instantiated."""
    print("\n✓ Testing instantiation...")

    from chatuvisbox.conversation import ConversationSession

    session = ConversationSession()
    assert session.state is None, "Initial state should be None"
    assert session.turn_count == 0, "Initial turn count should be 0"

    print("  ✓ ConversationSession instantiates correctly")
    return True


def test_context_methods():
    """Test context methods work without state."""
    print("\n✓ Testing context methods...")

    from chatuvisbox.conversation import ConversationSession

    session = ConversationSession()

    # Test get_last_response
    response = session.get_last_response()
    assert response == "", "Empty response when no state"

    # Test get_context_summary
    ctx = session.get_context_summary()
    assert ctx["turn_count"] == 0
    assert ctx["current_data"] is None
    assert ctx["message_count"] == 0

    # Test get_state
    state = session.get_state()
    assert state is None, "State should be None initially"

    print("  ✓ Context methods work correctly")
    return True


def test_reset():
    """Test reset method."""
    print("\n✓ Testing reset method...")

    from chatuvisbox.conversation import ConversationSession

    session = ConversationSession()
    session.turn_count = 5  # Manually set
    session.reset()

    assert session.state is None
    assert session.turn_count == 0

    print("  ✓ Reset works correctly")
    return True


def run_validation():
    """Run all validation checks."""
    print("="*70)
    print("PHASE 6 VALIDATION")
    print("="*70)

    tests = [
        test_imports,
        test_instantiation,
        test_context_methods,
        test_reset,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 All validation checks passed!")
        print("\nReady to run full test suite:")
        print("  python tests/test_multiturn.py")
    else:
        print(f"\n⚠️  {failed} check(s) failed")

    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_validation()
    sys.exit(0 if success else 1)
