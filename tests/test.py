#!/usr/bin/env python3
"""
ABOUTME: Pipeline-aware test runner with LLM budget control.
ABOUTME: Supports --pre-planning, --iterative, --code-review, --acceptance modes.
"""

import subprocess
import sys
import argparse
from pathlib import Path


def parse_llm_subsets(subset_str):
    """Parse --llm-subset argument into pytest markers."""
    if not subset_str:
        return []

    subsets = [s.strip() for s in subset_str.split(",")]
    markers = []

    for subset in subsets:
        if subset == "smoke":
            markers.append("smoke")
        else:
            markers.append(f"llm_subset_{subset}")

    return markers


def build_pytest_command(args):
    """Build pytest command based on arguments."""
    cmd = [sys.executable, "-m", "pytest"]

    # Determine test paths and markers
    test_paths = []
    markers = []

    if args.pre_planning:
        # Run unit + uvisbox_interface (0 LLM calls)
        test_paths = ["tests/unit/", "tests/uvisbox_interface/"]

    elif args.iterative:
        # Run unit + LLM subset
        test_paths = ["tests/unit/"]
        markers = parse_llm_subsets(args.llm_subset)

    elif args.code_review:
        # Run unit + uvisbox_interface + LLM subset
        test_paths = ["tests/unit/", "tests/uvisbox_interface/"]
        markers = parse_llm_subsets(args.llm_subset)

    elif args.acceptance:
        # Run everything
        test_paths = ["tests/"]

    else:
        # No mode specified - this shouldn't happen due to passthrough logic
        print("Error: Must specify a mode (--pre-planning, --iterative, --code-review, or --acceptance)")
        print("Or provide direct pytest arguments")
        sys.exit(1)

    # Add test paths
    cmd.extend(test_paths)

    # Add markers
    if markers:
        marker_expr = " or ".join(markers)
        cmd.extend(["-m", marker_expr])

    # Add coverage if requested
    if args.coverage:
        cmd.extend([
            "--cov=src/uvisbox_assistant",
            "--cov-report=term",
            "--cov-report=html"
        ])

    # Add verbosity
    cmd.append("-v")

    return cmd


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline-aware test runner for UVisBox-Assistant"
    )

    # Pipeline modes
    parser.add_argument(
        "--pre-planning",
        action="store_true",
        help="Run unit + uvisbox_interface tests (0 LLM calls)"
    )
    parser.add_argument(
        "--iterative",
        action="store_true",
        help="Run unit + LLM subset (requires --llm-subset)"
    )
    parser.add_argument(
        "--code-review",
        action="store_true",
        help="Run unit + uvisbox_interface + LLM subset (requires --llm-subset)"
    )
    parser.add_argument(
        "--acceptance",
        action="store_true",
        help="Run all tests (~100 LLM calls)"
    )

    # LLM subset selection
    parser.add_argument(
        "--llm-subset",
        type=str,
        help="Comma-separated LLM test subsets (analyzer,routing,smoke,etc)"
    )

    # Coverage
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )

    args, pytest_args = parser.parse_known_args()

    # If pytest args provided without mode, pass through directly
    if pytest_args and not any([
        args.pre_planning,
        args.iterative,
        args.code_review,
        args.acceptance
    ]):
        # Direct pytest passthrough
        cmd = [sys.executable, "-m", "pytest"] + pytest_args
        if args.coverage:
            cmd.extend([
                "--cov=src/uvisbox_assistant",
                "--cov-report=term",
                "--cov-report=html"
            ])
        result = subprocess.run(cmd)
        sys.exit(result.returncode)

    # Validate arguments
    if args.iterative and not args.llm_subset:
        print("Error: --iterative requires --llm-subset")
        print("Example: python tests/test.py --iterative --llm-subset=smoke")
        sys.exit(1)

    if args.code_review and not args.llm_subset:
        print("Error: --code-review requires --llm-subset")
        print("Example: python tests/test.py --code-review --llm-subset=analyzer")
        sys.exit(1)

    # Build pytest command
    cmd = build_pytest_command(args)

    # Add pytest passthrough args
    if pytest_args:
        cmd.extend(pytest_args)

    # Run pytest
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
