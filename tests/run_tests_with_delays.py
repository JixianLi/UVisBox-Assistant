"""Test runner that respects Gemini API rate limits

Gemini Free Tier: 30 requests per minute (gemini-2.0-flash-lite)
This script adds delays between test suites to avoid rate limiting.
"""
import subprocess
import time
import sys


def run_test(script_name, description, delay_after=0):
    """Run a test script and optionally delay after completion"""
    print("\n" + "="*70)
    print(f"RUNNING: {description}")
    print(f"Script: {script_name}")
    print("="*70 + "\n")

    start = time.time()
    result = subprocess.run([sys.executable, script_name])
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"\n❌ {script_name} FAILED")
        return False

    print(f"\n✅ {script_name} PASSED in {elapsed:.1f}s")

    if delay_after > 0:
        print(f"\n⏳ Waiting {delay_after}s for API rate limit reset...")
        for i in range(delay_after, 0, -1):
            print(f"   {i}s remaining...", end='\r')
            time.sleep(1)
        print("\n")

    return True


def main():
    """Run all test suites with appropriate delays"""
    print("\n" + "="*70)
    print("CHATUVISBOX TEST SUITE - GEMINI FREE TIER FRIENDLY")
    print("="*70)
    print("\nFree Tier Limits:")
    print("  - 30 requests per minute (gemini-2.0-flash-lite)")
    print("  - Tests will be spaced out to respect limits")
    print("\nTest Plan:")
    print("  1. Quick test (6-10 API calls)")
    print("  2. 60s delay")
    print("  3. Phase 1 tests (no API calls)")
    print("  4. Phase 2 tests (10-15 API calls)")
    print("  5. 60s delay")
    print("  6. Routing tests (no API calls)")
    print("  7. Graph tests (5-8 API calls)")
    print("="*70)

    input("\nPress Enter to start tests...")

    tests = [
        ("test_graph_quick.py", "Quick Integration Test (6-10 API calls)", 60),
        ("test_phase1.py", "Phase 1: Tool Schemas (0 API calls)", 0),
        ("test_phase2.py", "Phase 2: State & Nodes (10-15 API calls)", 60),
        ("test_routing.py", "Phase 3: Routing Logic (0 API calls)", 0),
        ("test_graph.py", "Phase 3: Graph Compilation (5-8 API calls)", 0),
    ]

    passed = 0
    failed = 0

    for script, desc, delay in tests:
        if run_test(script, desc, delay):
            passed += 1
        else:
            failed += 1
            print(f"\n⚠️  Stopping test suite due to failure in {script}")
            break

    print("\n" + "="*70)
    print("TEST SUITE SUMMARY")
    print("="*70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
