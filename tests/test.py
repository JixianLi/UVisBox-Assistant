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


def build_pytest_commands(args):
    """Build pytest command(s) based on arguments.

    Returns a list of commands to run. Multiple commands are needed when
    we need to run unmarked tests + marked tests separately.
    """
    base_cmd = [sys.executable, "-m", "pytest"]
    commands = []

    if args.pre_planning:
        # Run unit + uvisbox_interface (0 LLM calls)
        cmd = base_cmd.copy()
        cmd.extend(["tests/unit/", "tests/uvisbox_interface/"])
        cmd.append("-v")
        if args.coverage:
            cmd.extend([
                "--cov=src/uvisbox_assistant",
                "--cov-report=term",
                "--cov-report=html"
            ])
        commands.append(cmd)

    elif args.iterative:
        # Run unit + LLM subset
        markers = parse_llm_subsets(args.llm_subset)

        # First command: run unit tests (no marker filter)
        cmd1 = base_cmd.copy()
        cmd1.extend(["tests/unit/", "-v"])
        if args.coverage:
            cmd1.extend(["--cov=src/uvisbox_assistant", "--cov-append"])
        commands.append(cmd1)

        # Second command: run marked tests from llm_integration/ and e2e/
        if markers:
            cmd2 = base_cmd.copy()
            marker_expr = " or ".join(markers)
            cmd2.extend(["tests/llm_integration/", "tests/e2e/", "-m", marker_expr, "-v"])
            if args.coverage:
                cmd2.extend(["--cov=src/uvisbox_assistant", "--cov-append",
                           "--cov-report=term", "--cov-report=html"])
            commands.append(cmd2)

    elif args.code_review:
        # Run unit + uvisbox_interface + LLM subset
        markers = parse_llm_subsets(args.llm_subset)

        # First command: run unit and uvisbox_interface tests
        cmd1 = base_cmd.copy()
        cmd1.extend(["tests/unit/", "tests/uvisbox_interface/", "-v"])
        if args.coverage:
            cmd1.extend(["--cov=src/uvisbox_assistant", "--cov-append"])
        commands.append(cmd1)

        # Second command: run marked tests
        if markers:
            cmd2 = base_cmd.copy()
            marker_expr = " or ".join(markers)
            cmd2.extend(["tests/llm_integration/", "tests/e2e/", "-m", marker_expr, "-v"])
            if args.coverage:
                cmd2.extend(["--cov=src/uvisbox_assistant", "--cov-append",
                           "--cov-report=term", "--cov-report=html"])
            commands.append(cmd2)

    elif args.acceptance:
        # Run everything
        cmd = base_cmd.copy()
        cmd.extend(["tests/", "-v"])
        if args.coverage:
            cmd.extend([
                "--cov=src/uvisbox_assistant",
                "--cov-report=term",
                "--cov-report=html"
            ])
        commands.append(cmd)

    else:
        # No mode specified - this shouldn't happen due to passthrough logic
        print("Error: Must specify a mode (--pre-planning, --iterative, --code-review, or --acceptance)")
        print("Or provide direct pytest arguments")
        sys.exit(1)

    return commands


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

    # Build pytest commands
    cmds = build_pytest_commands(args)

    # Add pytest passthrough args to all commands
    if pytest_args:
        for cmd in cmds:
            # Insert passthrough args before -v (which is always last or second-to-last)
            # Find -v and insert before it
            if "-v" in cmd:
                v_index = cmd.index("-v")
                cmd[v_index:v_index] = pytest_args
            else:
                cmd.extend(pytest_args)

    # Run pytest commands in sequence
    # If any command fails, stop and return that exit code
    for i, cmd in enumerate(cmds):
        if len(cmds) > 1:
            print(f"\n{'='*70}")
            print(f"Running command {i+1}/{len(cmds)}...")
            print(f"{'='*70}\n")

        result = subprocess.run(cmd)
        if result.returncode != 0:
            sys.exit(result.returncode)

    sys.exit(0)


if __name__ == "__main__":
    main()
