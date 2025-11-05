"""
Run all tests with proper delays for rate limits and optional coverage reporting.

Usage:
    python tests/utils/run_all_tests.py                    # Run all
    python tests/utils/run_all_tests.py --unit             # Unit tests only (0 API calls)
    python tests/utils/run_all_tests.py --integration      # Integration tests only
    python tests/utils/run_all_tests.py --e2e              # E2E tests only
    python tests/utils/run_all_tests.py --quick            # Unit + test_simple.py
    python tests/utils/run_all_tests.py --unit --coverage  # Unit tests with coverage
    python tests/utils/run_all_tests.py --coverage         # All tests with coverage
"""

import subprocess
import time
import sys
import argparse
from pathlib import Path


# Test categories
UNIT_TESTS = [
    "tests/unit/test_command_parser.py",
    "tests/unit/test_command_handlers.py",
    "tests/unit/test_config.py",
    "tests/unit/test_routing.py",
    "tests/unit/test_state_extensions.py",
    "tests/unit/test_tools.py",
    "tests/unit/test_statistics_tools.py",
    "tests/unit/test_analyzer_tools.py",
    "tests/unit/test_error_tracking.py",
    "tests/unit/test_error_interpretation.py",
    "tests/unit/test_output_control.py",
]

INTEGRATION_TESTS = [
    "tests/integration/test_hybrid_control.py",
    "tests/integration/test_error_handling.py",
    "tests/integration/test_session_management.py",
]

E2E_TESTS = [
    "tests/e2e/test_matplotlib_behavior.py",
]

def run_tests(test_files, delay=3, use_pytest=True):
    """Run tests with delays between files."""
    passed = 0
    failed = 0
    failed_tests = []

    for i, test_file in enumerate(test_files):
        print(f"\n{'='*70}")
        print(f"Running: {test_file}")
        print('='*70)

        if use_pytest:
            # Use pytest for better output
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v"],
                capture_output=False
            )
        else:
            # Direct execution (legacy)
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=False
            )

        if result.returncode == 0:
            passed += 1
            print(f"✅ {test_file} PASSED")
        else:
            failed += 1
            failed_tests.append(test_file)
            print(f"❌ {test_file} FAILED")

        # Delay between tests
        if i < len(test_files) - 1:
            print(f"\n⏳ Pausing {delay}s to respect rate limits...")
            time.sleep(delay)

    return passed, failed, failed_tests


def run_tests_with_coverage(test_dirs, coverage_target="src/uvisbox_assistant"):
    """Run tests with coverage reporting using pytest."""
    print(f"\n{'='*70}")
    print("Running tests with coverage")
    print('='*70)

    # Build pytest command
    cmd = [
        sys.executable, "-m", "pytest"
    ] + test_dirs + [
        f"--cov={coverage_target}",
        "--cov-report=term",
        "--cov-report=html",
        "-v"
    ]

    print(f"Command: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print("\n✅ All tests passed with coverage!")
        print(f"📊 HTML coverage report: htmlcov/index.html")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Run UVisBox-Assistant test suite")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only (0 API calls)")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run e2e tests only")
    parser.add_argument("--quick", action="store_true", help="Run quick tests (unit + test_simple)")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage reporting")
    args = parser.parse_args()

    print("\n" + "="*70)
    print("UVisBox-Assistant Test Suite")
    print("="*70)

    # Determine which tests to run
    test_dirs = []
    all_tests = []

    if args.unit:
        print("\n📦 Running Unit Tests (0 API calls)")
        all_tests = UNIT_TESTS
        test_dirs = ["tests/unit/"]
        delay = 0  # No delay for unit tests
    elif args.integration:
        print("\n🔗 Running Integration Tests")
        all_tests = INTEGRATION_TESTS
        test_dirs = ["tests/integration/"]
        delay = 5  # 5s delay between integration tests
    elif args.e2e:
        print("\n🎯 Running E2E Tests")
        all_tests = E2E_TESTS
        test_dirs = ["tests/e2e/"]
        delay = 5  # 5s delay between e2e tests
    elif args.quick:
        print("\n⚡ Running Quick Tests (unit + sanity check)")
        all_tests = ["tests/test_simple.py"] + UNIT_TESTS
        test_dirs = ["tests/test_simple.py", "tests/unit/"]
        delay = 2
    else:
        print("\n📋 Running All Tests")
        all_tests = ["tests/test_simple.py"] + UNIT_TESTS + INTEGRATION_TESTS + E2E_TESTS
        test_dirs = ["tests/"]
        delay = 3

    # Coverage mode
    if args.coverage:
        print(f"\n📊 Coverage reporting enabled")
        return run_tests_with_coverage(test_dirs)

    # Filter to only existing files
    existing_tests = [t for t in all_tests if Path(t).exists()]
    missing_tests = [t for t in all_tests if not Path(t).exists()]

    if missing_tests:
        print(f"\n⚠️  Warning: {len(missing_tests)} test files not found:")
        for t in missing_tests:
            print(f"  - {t}")

    if not existing_tests:
        print("\n❌ No test files found!")
        return 1

    print(f"\n📊 Will run {len(existing_tests)} test files")

    passed, failed, failed_tests = run_tests(existing_tests, delay)

    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total:  {passed + failed}")

    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        print("\n❌ Failed tests:")
        for test_file in failed_tests:
            print(f"  - {test_file}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
