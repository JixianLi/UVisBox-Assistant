# Test Redesign v0.3.4 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restructure test suite to align with development pipeline and provide granular LLM budget control.

**Architecture:** Reorganize tests into 4 categories (unit/, uvisbox_interface/, llm_integration/, e2e/) and implement pipeline-aware test runner (test.py) with subset selection.

**Tech Stack:** pytest, pytest markers, argparse, Python 3.12

---

## Task 1: Create New Directory Structure

**Files:**
- Create: `tests/uvisbox_interface/__init__.py`
- Create: `tests/llm_integration/__init__.py`

**Step 1: Create uvisbox_interface directory**

```bash
mkdir -p tests/uvisbox_interface
```

**Step 2: Create __init__.py for uvisbox_interface**

```python
# tests/uvisbox_interface/__init__.py
"""
ABOUTME: UVisBox interface tests - verify tool → UVisBox integration.
ABOUTME: Tests call real UVisBox functions but make 0 LLM calls.
"""
```

**Step 3: Create llm_integration directory**

```bash
mkdir -p tests/llm_integration
```

**Step 4: Create __init__.py for llm_integration**

```python
# tests/llm_integration/__init__.py
"""
ABOUTME: LLM integration tests - test specific LLM-powered features.
ABOUTME: Tests individual features that require LLM calls (analyzer, routing, error handling).
"""
```

**Step 5: Verify directories created**

Run: `ls -la tests/`
Expected: See `uvisbox_interface/` and `llm_integration/` directories

**Step 6: Commit**

```bash
git add tests/uvisbox_interface/__init__.py tests/llm_integration/__init__.py
git commit -m "chore: create new test directory structure for v0.3.4

Add uvisbox_interface/ and llm_integration/ test directories to
support pipeline-aware test execution with LLM budget control.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: Verify and Categorize test_error_recording.py

**Files:**
- Read: `tests/integration/test_error_recording.py`

**Step 1: Check if test uses LLM**

Inspect the file - look for:
- `ConversationSession().send()` calls → uses LLM
- Direct node calls (`call_vis_tool()`, etc.) → no LLM if no session.send()
- Mock states with AIMessage → no LLM (unit test)

**Step 2: Determine category**

Based on inspection:
- If calls `session.send()` → move to `llm_integration/`
- If only calls nodes directly with mock states → move to `unit/`
- If calls UVisBox directly → move to `uvisbox_interface/`

**Decision:** File calls nodes directly with mock states, no session.send(). **Move to `unit/`**.

**Step 3: Move file**

```bash
git mv tests/integration/test_error_recording.py tests/unit/test_error_recording.py
```

**Step 4: Verify move**

Run: `ls tests/unit/test_error_recording.py`
Expected: File exists

**Step 5: Commit**

```bash
git add -A
git commit -m "test: move test_error_recording to unit/ (0 LLM calls)

test_error_recording.py tests error tracking by calling nodes directly
with mock states. Does not use ConversationSession.send(), so makes
0 LLM calls. Properly categorized as unit test.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: Move test_report_switching.py to llm_integration/

**Files:**
- Move: `tests/integration/test_report_switching.py` → `tests/llm_integration/test_report_switching.py`

**Step 1: Move file**

```bash
git mv tests/integration/test_report_switching.py tests/llm_integration/test_report_switching.py
```

**Step 2: Add pytest marker to file**

Edit `tests/llm_integration/test_report_switching.py` - add after imports:

```python
pytestmark = pytest.mark.llm_subset_analysis
```

**Step 3: Verify file**

Run: `ls tests/llm_integration/test_report_switching.py`
Expected: File exists

**Step 4: Commit**

```bash
git add -A
git commit -m "test: move test_report_switching to llm_integration/

Uses ConversationSession.send() which makes LLM calls. Add marker
for llm_subset_analysis to support granular test selection.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: Move UVisBox Interface Tests

**Files:**
- Move: `tests/integration/test_tool_interfaces.py` → `tests/uvisbox_interface/test_tool_interfaces.py`
- Move: `tests/integration/test_csv_loading.py` → `tests/uvisbox_interface/test_csv_loading.py`

**Step 1: Move test_tool_interfaces.py**

```bash
git mv tests/integration/test_tool_interfaces.py tests/uvisbox_interface/test_tool_interfaces.py
```

**Step 2: Move test_csv_loading.py**

```bash
git mv tests/integration/test_csv_loading.py tests/uvisbox_interface/test_csv_loading.py
```

**Step 3: Verify moves**

Run: `ls tests/uvisbox_interface/`
Expected: See `test_tool_interfaces.py` and `test_csv_loading.py`

**Step 4: Commit**

```bash
git add -A
git commit -m "test: move interface tests to uvisbox_interface/

Moves test_tool_interfaces.py and test_csv_loading.py to dedicated
uvisbox_interface/ directory. These tests call real UVisBox functions
but make 0 LLM calls.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: Move and Rename LLM Integration Tests

**Files:**
- Move: `tests/integration/test_analyzer_tool.py` → `tests/llm_integration/test_analyzer.py`
- Move: `tests/integration/test_error_handling.py` → `tests/llm_integration/test_error_handling.py`
- Move: `tests/integration/test_hybrid_control.py` → `tests/llm_integration/test_hybrid_control.py`
- Move: `tests/integration/test_session_management.py` → `tests/llm_integration/test_session.py`

**Step 1: Move and rename test_analyzer_tool.py**

```bash
git mv tests/integration/test_analyzer_tool.py tests/llm_integration/test_analyzer.py
```

**Step 2: Add pytest marker to test_analyzer.py**

Edit `tests/llm_integration/test_analyzer.py` - add after imports:

```python
pytestmark = pytest.mark.llm_subset_analyzer
```

**Step 3: Move test_error_handling.py**

```bash
git mv tests/integration/test_error_handling.py tests/llm_integration/test_error_handling.py
```

**Step 4: Add pytest marker to test_error_handling.py**

Edit `tests/llm_integration/test_error_handling.py` - add after imports:

```python
pytestmark = pytest.mark.llm_subset_error_handling
```

**Step 5: Move test_hybrid_control.py**

```bash
git mv tests/integration/test_hybrid_control.py tests/llm_integration/test_hybrid_control.py
```

**Step 6: Add pytest marker to test_hybrid_control.py**

Edit `tests/llm_integration/test_hybrid_control.py` - add after imports:

```python
pytestmark = pytest.mark.llm_subset_hybrid_control
```

**Step 7: Move and rename test_session_management.py**

```bash
git mv tests/integration/test_session_management.py tests/llm_integration/test_session.py
```

**Step 8: Add pytest marker to test_session.py**

Edit `tests/llm_integration/test_session.py` - add after imports:

```python
pytestmark = pytest.mark.llm_subset_session
```

**Step 9: Verify all files moved**

Run: `ls tests/llm_integration/`
Expected: See test_analyzer.py, test_error_handling.py, test_hybrid_control.py, test_session.py, test_report_switching.py

**Step 10: Commit**

```bash
git add -A
git commit -m "test: move LLM integration tests with markers

Moves and renames LLM integration tests to llm_integration/:
- test_analyzer_tool.py → test_analyzer.py
- test_error_handling.py (kept name)
- test_hybrid_control.py (kept name)
- test_session_management.py → test_session.py

Adds pytest markers for granular subset selection.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: Split test_e2e_pipelines.py into Per-Viz-Type Files

**Files:**
- Read: `tests/integration/test_e2e_pipelines.py`
- Create: `tests/e2e/test_functional_boxplot.py`
- Create: `tests/e2e/test_curve_boxplot.py`
- Create: `tests/e2e/test_contour_boxplot.py`
- Create: `tests/e2e/test_probabilistic_ms.py`
- Create: `tests/e2e/test_uncertainty_lobes.py`
- Create: `tests/e2e/test_squid_glyph.py`
- Delete: `tests/integration/test_e2e_pipelines.py`

**Step 1: Read test_e2e_pipelines.py to identify test classes**

Run: `grep "^class Test" tests/integration/test_e2e_pipelines.py`
Expected: List of test classes by viz type

**Step 2: Create test_functional_boxplot.py**

Extract TestFunctionalBoxplotPipeline class and dependencies:

```python
# tests/e2e/test_functional_boxplot.py
"""End-to-end tests for functional boxplot workflows."""

import pytest
import time
import matplotlib.pyplot as plt
from uvisbox_assistant.session.conversation import ConversationSession

pytestmark = pytest.mark.llm_subset_functional_boxplot


@pytest.fixture
def session():
    """Create a fresh conversation session for each test."""
    sess = ConversationSession()
    yield sess
    sess.clear()
    plt.close('all')


def wait_for_rate_limit():
    """Wait between tests to respect API rate limits."""
    time.sleep(2)


class TestFunctionalBoxplotPipeline:
    """Test data → functional_boxplot pipeline."""

    def test_generate_and_visualize(self, session):
        """Complete workflow: generate curves and plot functional boxplot."""
        wait_for_rate_limit()

        session.send("Generate 30 curves and plot functional boxplot")

        # [Copy remaining test code from original file]
```

**Step 3: Create test_curve_boxplot.py**

Extract TestCurveBoxplotPipeline class:

```python
# tests/e2e/test_curve_boxplot.py
"""End-to-end tests for curve boxplot workflows."""

import pytest
import time
import matplotlib.pyplot as plt
from uvisbox_assistant.session.conversation import ConversationSession

pytestmark = pytest.mark.llm_subset_curve_boxplot


@pytest.fixture
def session():
    """Create a fresh conversation session for each test."""
    sess = ConversationSession()
    yield sess
    sess.clear()
    plt.close('all')


def wait_for_rate_limit():
    """Wait between tests to respect API rate limits."""
    time.sleep(2)


class TestCurveBoxplotPipeline:
    """Test data → curve_boxplot pipeline."""

    # [Copy test methods from original file]
```

**Step 4: Create test_contour_boxplot.py**

```python
# tests/e2e/test_contour_boxplot.py
"""End-to-end tests for contour boxplot workflows."""

import pytest
import time
import matplotlib.pyplot as plt
from uvisbox_assistant.session.conversation import ConversationSession

pytestmark = pytest.mark.llm_subset_contour_boxplot


@pytest.fixture
def session():
    """Create a fresh conversation session for each test."""
    sess = ConversationSession()
    yield sess
    sess.clear()
    plt.close('all')


def wait_for_rate_limit():
    """Wait between tests to respect API rate limits."""
    time.sleep(2)


class TestContourBoxplotPipeline:
    """Test data → contour_boxplot pipeline."""

    # [Copy test methods from original file]
```

**Step 5: Create test_probabilistic_ms.py**

```python
# tests/e2e/test_probabilistic_ms.py
"""End-to-end tests for probabilistic marching squares workflows."""

import pytest
import time
import matplotlib.pyplot as plt
from uvisbox_assistant.session.conversation import ConversationSession

pytestmark = pytest.mark.llm_subset_probabilistic_ms


@pytest.fixture
def session():
    """Create a fresh conversation session for each test."""
    sess = ConversationSession()
    yield sess
    sess.clear()
    plt.close('all')


def wait_for_rate_limit():
    """Wait between tests to respect API rate limits."""
    time.sleep(2)


class TestProbabilisticMarchingSquaresPipeline:
    """Test data → probabilistic_marching_squares pipeline."""

    # [Copy test methods from original file]
```

**Step 6: Create test_uncertainty_lobes.py**

```python
# tests/e2e/test_uncertainty_lobes.py
"""End-to-end tests for uncertainty lobes workflows."""

import pytest
import time
import matplotlib.pyplot as plt
from uvisbox_assistant.session.conversation import ConversationSession

pytestmark = pytest.mark.llm_subset_uncertainty_lobes


@pytest.fixture
def session():
    """Create a fresh conversation session for each test."""
    sess = ConversationSession()
    yield sess
    sess.clear()
    plt.close('all')


def wait_for_rate_limit():
    """Wait between tests to respect API rate limits."""
    time.sleep(2)


class TestUncertaintyLobesPipeline:
    """Test data → uncertainty_lobes pipeline."""

    # [Copy test methods from original file]
```

**Step 7: Create test_squid_glyph.py**

```python
# tests/e2e/test_squid_glyph.py
"""End-to-end tests for squid glyph workflows."""

import pytest
import time
import matplotlib.pyplot as plt
from uvisbox_assistant.session.conversation import ConversationSession

pytestmark = pytest.mark.llm_subset_squid_glyph


@pytest.fixture
def session():
    """Create a fresh conversation session for each test."""
    sess = ConversationSession()
    yield sess
    sess.clear()
    plt.close('all')


def wait_for_rate_limit():
    """Wait between tests to respect API rate limits."""
    time.sleep(2)


class TestSquidGlyphPipeline:
    """Test data → squid_glyph_2D pipeline."""

    # [Copy test methods from original file]
```

**Step 8: Delete original file**

```bash
git rm tests/integration/test_e2e_pipelines.py
```

**Step 9: Verify split files**

Run: `ls tests/e2e/test_*.py`
Expected: See 6 new test files plus existing test_matplotlib_behavior.py and test_analysis_workflows.py

**Step 10: Run one test to verify structure**

Run: `poetry run pytest tests/e2e/test_functional_boxplot.py -v`
Expected: Tests collected and structure valid (may fail due to LLM, that's OK)

**Step 11: Commit**

```bash
git add tests/e2e/
git commit -m "test: split test_e2e_pipelines into per-viz-type files

Splits monolithic test_e2e_pipelines.py into 6 files:
- test_functional_boxplot.py
- test_curve_boxplot.py
- test_contour_boxplot.py
- test_probabilistic_ms.py
- test_uncertainty_lobes.py
- test_squid_glyph.py

Each file has pytest marker for granular subset selection.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: Add Smoke Test Markers

**Files:**
- Modify: `tests/e2e/test_functional_boxplot.py`
- Modify: `tests/llm_integration/test_analyzer.py`

**Step 1: Identify smoke tests**

Critical path tests:
- 1 basic visualization workflow (functional boxplot)
- 1 analyzer test

**Step 2: Add @pytest.mark.smoke to functional boxplot test**

Edit `tests/e2e/test_functional_boxplot.py`:

```python
class TestFunctionalBoxplotPipeline:
    """Test data → functional_boxplot pipeline."""

    @pytest.mark.smoke
    def test_generate_and_visualize(self, session):
        """Smoke test: Complete workflow - generate curves and plot functional boxplot."""
        wait_for_rate_limit()
        # [existing test code]
```

**Step 3: Add @pytest.mark.smoke to analyzer test**

Edit `tests/llm_integration/test_analyzer.py` - find first/simplest test and add marker:

```python
@pytest.mark.smoke
def test_analyzer_basic(session):
    """Smoke test: Basic analyzer functionality."""
    # [existing test code]
```

**Step 4: Verify markers**

Run: `poetry run pytest -m smoke --collect-only`
Expected: Shows 2 tests collected

**Step 5: Commit**

```bash
git add tests/e2e/test_functional_boxplot.py tests/llm_integration/test_analyzer.py
git commit -m "test: add smoke test markers for critical path

Marks 2 tests as smoke tests (~3 LLM calls total):
- Basic functional boxplot workflow
- Basic analyzer functionality

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 8: Implement test.py - Part 1 (Basic Structure)

**Files:**
- Create: `tests/test.py`

**Step 1: Create test.py with imports and argument parser**

```python
#!/usr/bin/env python3
"""
ABOUTME: Pipeline-aware test runner with LLM budget control.
ABOUTME: Supports --pre-planning, --iterative, --code-review, --acceptance modes.
"""

import subprocess
import sys
import argparse
from pathlib import Path


def build_pytest_command(args):
    """Build pytest command based on arguments."""
    cmd = [sys.executable, "-m", "pytest"]

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
```

**Step 2: Make test.py executable**

```bash
chmod +x tests/test.py
```

**Step 3: Test basic invocation**

Run: `python tests/test.py --help`
Expected: Shows help message with all options

**Step 4: Commit**

```bash
git add tests/test.py
git commit -m "test: add test.py with basic argument parsing

Implements pipeline-aware test runner structure with modes:
- --pre-planning
- --iterative (requires --llm-subset)
- --code-review (requires --llm-subset)
- --acceptance

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 9: Implement test.py - Part 2 (Mode Logic)

**Files:**
- Modify: `tests/test.py`

**Step 1: Implement build_pytest_command logic for each mode**

```python
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
        # No mode specified - show error
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
```

**Step 2: Test --pre-planning mode**

Run: `python tests/test.py --pre-planning --collect-only`
Expected: Collects tests from unit/ and uvisbox_interface/ only

**Step 3: Test --iterative mode validation**

Run: `python tests/test.py --iterative`
Expected: Error message "requires --llm-subset"

**Step 4: Test --iterative with smoke**

Run: `python tests/test.py --iterative --llm-subset=smoke --collect-only`
Expected: Collects unit tests + smoke tests

**Step 5: Commit**

```bash
git add tests/test.py
git commit -m "test: implement mode logic in test.py

Implements test selection for each pipeline mode:
- --pre-planning: unit + uvisbox_interface
- --iterative: unit + LLM subset markers
- --code-review: unit + uvisbox_interface + LLM subset
- --acceptance: all tests

Adds parse_llm_subsets() to map subset names to pytest markers.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 10: Implement test.py - Part 3 (Pytest Passthrough)

**Files:**
- Modify: `tests/test.py`

**Step 1: Update main() to handle pytest passthrough**

```python
def main():
    parser = argparse.ArgumentParser(
        description="Pipeline-aware test runner for UVisBox-Assistant"
    )

    # [... existing argument definitions ...]

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

    # [... existing validation and mode logic ...]
```

**Step 2: Test direct file passthrough**

Run: `python tests/test.py tests/unit/test_config.py -v --collect-only`
Expected: Runs pytest directly on specified file

**Step 3: Test specific test passthrough**

Run: `python tests/test.py tests/unit/test_config.py::test_temp_dir_exists --collect-only`
Expected: Collects only that specific test

**Step 4: Commit**

```bash
git add tests/test.py
git commit -m "test: add pytest passthrough support to test.py

Allows direct pytest-style test selection:
- python tests/test.py tests/unit/test_config.py
- python tests/test.py tests/unit/test_config.py::test_specific

Enables surgical test execution for debugging.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 11: Register Pytest Markers in pyproject.toml

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add markers section to pyproject.toml**

Find `[tool.pytest.ini_options]` section and add markers:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
markers = [
    "smoke: critical path smoke tests (~3 LLM calls)",
    "llm_subset_analyzer: analyzer LLM integration tests",
    "llm_subset_routing: routing LLM integration tests",
    "llm_subset_error_handling: error handling LLM integration tests",
    "llm_subset_session: session management LLM integration tests",
    "llm_subset_hybrid_control: hybrid control LLM integration tests",
    "llm_subset_analysis: analysis workflow LLM integration tests",
    "llm_subset_functional_boxplot: functional boxplot e2e tests",
    "llm_subset_curve_boxplot: curve boxplot e2e tests",
    "llm_subset_contour_boxplot: contour boxplot e2e tests",
    "llm_subset_probabilistic_ms: probabilistic marching squares e2e tests",
    "llm_subset_uncertainty_lobes: uncertainty lobes e2e tests",
    "llm_subset_squid_glyph: squid glyph e2e tests",
]
```

**Step 2: Verify markers registered**

Run: `poetry run pytest --markers`
Expected: Shows all custom markers

**Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "test: register pytest markers in pyproject.toml

Registers all LLM subset markers and smoke marker for:
- Component-based subsets (analyzer, routing, error_handling, etc.)
- Viz-type subsets (functional_boxplot, curve_boxplot, etc.)
- Special markers (smoke)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 12: Delete Old Files

**Files:**
- Delete: `tests/utils/run_all_tests.py`
- Delete: `tests/interactive/interactive_test.py`
- Delete: `tests/interactive/__init__.py`
- Delete: `tests/interactive/` directory

**Step 1: Remove run_all_tests.py**

```bash
git rm tests/utils/run_all_tests.py
```

**Step 2: Remove interactive directory**

```bash
git rm -r tests/interactive/
```

**Step 3: Check if utils directory is empty**

Run: `ls tests/utils/`

If empty or only has `__init__.py`:
```bash
git rm -r tests/utils/
```

**Step 4: Verify deletions**

Run: `ls tests/`
Expected: No `utils/` or `interactive/` directories

**Step 5: Commit**

```bash
git add -A
git commit -m "test: remove old test infrastructure

Removes:
- tests/utils/run_all_tests.py (replaced by tests/test.py)
- tests/interactive/ (use 'uva' main for interactive testing)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 13: Fix CLAUDE.md Unicode Bug

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Find and fix unicode characters in workflow diagram**

Edit `CLAUDE.md` - find the LangGraph Workflow section (around line 20-30):

Replace:
```
START � model � [conditional routing]
         �         � data_tool � model
         �         � vis_tool � model
         �         � statistics_tool � model
         �         � analyzer_tool � model
         �         � END
```

With:
```
START -> model -> [conditional routing]
              -> data_tool -> model
              -> vis_tool -> model
              -> statistics_tool -> model
              -> analyzer_tool -> model
              -> END
```

**Step 2: Verify ASCII only**

Run: `grep -n "[^[:print:][:space:]]" CLAUDE.md`
Expected: No matches (no non-printable characters)

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: fix non-printable unicode in CLAUDE.md workflow diagram

Replace unicode arrows with ASCII arrows (->) for better compatibility.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 14: Update TESTING.md

**Files:**
- Modify: `TESTING.md`

**Step 1: Rewrite Quick Start section**

```markdown
# Testing Guide

## Quick Start

```bash
# Pre-planning: Verify UVisBox interface (0 LLM calls)
python tests/test.py --pre-planning

# Iterative development: Unit + specific LLM subset
python tests/test.py --iterative --llm-subset=analyzer

# Smoke test: Critical path only (~3 LLM calls)
python tests/test.py --iterative --llm-subset=smoke

# Code review checkpoint: Full interface + LLM subset
python tests/test.py --code-review --llm-subset=analyzer,routing

# Acceptance: All tests (~100 LLM calls)
python tests/test.py --acceptance

# Direct test selection (pytest-style)
python tests/test.py tests/unit/test_config.py
python tests/test.py tests/llm_integration/test_analyzer.py::test_specific

# With coverage
python tests/test.py --pre-planning --coverage
```

---
```

**Step 2: Rewrite Test Structure section**

```markdown
## Test Structure

```
tests/
├── test.py                     # Pipeline-aware test runner
│
├── unit/                       # 277 tests, 0 LLM calls
│   ├── test_command_parser.py      # Hybrid command parsing
│   ├── test_routing.py             # Graph routing logic
│   ├── test_tools.py               # Data/vis tool functions
│   └── [... other unit tests]
│
├── uvisbox_interface/          # 23 tests, 0 LLM calls, calls UVisBox
│   ├── test_tool_interfaces.py     # Tool → UVisBox interface validation
│   └── test_csv_loading.py         # CSV loading with real data
│
├── llm_integration/            # ~20 tests, ~40 LLM calls
│   ├── test_analyzer.py            # Analyzer with LLM
│   ├── test_error_handling.py      # Error recovery
│   ├── test_session.py             # Session management
│   ├── test_hybrid_control.py      # Hybrid control workflows
│   └── test_routing.py             # Graph routing with LLM
│
├── e2e/                        # ~30 tests, ~60 LLM calls
│   ├── test_functional_boxplot.py  # Functional boxplot workflows
│   ├── test_curve_boxplot.py       # Curve boxplot workflows
│   ├── test_contour_boxplot.py     # Contour boxplot workflows
│   ├── test_probabilistic_ms.py    # PMS workflows
│   ├── test_uncertainty_lobes.py   # Uncertainty lobes workflows
│   ├── test_squid_glyph.py         # Squid glyph workflows
│   ├── test_analysis_workflows.py  # Analysis pipelines
│   └── test_matplotlib_behavior.py # Visualization behavior
│
├── conftest.py
└── __init__.py
```

### LLM Call Estimates

| Category | Tests | LLM Calls | Duration |
|----------|-------|-----------|----------|
| **Unit** | 277 | 0 | < 10 seconds |
| **UVisBox Interface** | 23 | 0 | < 30 seconds |
| **LLM Integration** | ~20 | ~40 | 2-3 minutes |
| **E2E** | ~30 | ~60 | 3-5 minutes |
| **Total** | ~350 | ~100 | 8-10 minutes |

**Note**: LLM call estimates are approximate and may vary by ±20%.

---
```

**Step 3: Add Pipeline Stages section**

```markdown
## Development Pipeline Stages

### 1. Pre-Planning (Before Feature Planning)

**Purpose**: Verify UVisBox interface is stable before planning new features.

```bash
python tests/test.py --pre-planning
```

**Must pass before:**
- Creating implementation plans
- Starting feature development

**If fails:**
- STOP feature planning
- Create patch version for interface fixes only
- Resume after `--pre-planning` passes

### 2. Iterative Development (During Development)

**Purpose**: Fast iteration with minimal LLM budget.

```bash
# Working on analyzer
python tests/test.py --iterative --llm-subset=analyzer

# Working on squid glyph
python tests/test.py --iterative --llm-subset=squid_glyph

# Multiple subsets
python tests/test.py --iterative --llm-subset=analyzer,routing

# Smoke test only
python tests/test.py --iterative --llm-subset=smoke
```

**Run after**: Each code change

### 3. Code Review Checkpoints (Before Review)

**Purpose**: Verify implementation before requesting review.

```bash
python tests/test.py --code-review --llm-subset=analyzer
```

**Run before:**
- Requesting code review
- Moving to next task in plan

### 4. Acceptance (Before Merge)

**Purpose**: Final validation with full test suite.

```bash
python tests/test.py --acceptance
```

**Run before:**
- Merging to main
- Creating release

**Budget**: ~100 LLM calls, 8-10 minutes

---
```

**Step 4: Add LLM Subset Reference section**

```markdown
## LLM Subset Reference

### Component-Based Subsets

| Subset | Marker | Tests | LLM Calls |
|--------|--------|-------|-----------|
| `analyzer` | `llm_subset_analyzer` | Analyzer tests | ~5 |
| `routing` | `llm_subset_routing` | Routing tests | ~5 |
| `error_handling` | `llm_subset_error_handling` | Error recovery | ~5 |
| `session` | `llm_subset_session` | Session management | ~3 |
| `hybrid_control` | `llm_subset_hybrid_control` | Hybrid control | ~3 |

### Workflow-Based Subsets

| Subset | Marker | Tests | LLM Calls |
|--------|--------|-------|-----------|
| `analysis` | `llm_subset_analysis` | Analysis workflows | ~10 |

### Visualization Type Subsets

| Subset | Marker | Tests | LLM Calls |
|--------|--------|-------|-----------|
| `functional_boxplot` | `llm_subset_functional_boxplot` | Functional boxplot | ~8 |
| `curve_boxplot` | `llm_subset_curve_boxplot` | Curve boxplot | ~8 |
| `contour_boxplot` | `llm_subset_contour_boxplot` | Contour boxplot | ~8 |
| `probabilistic_ms` | `llm_subset_probabilistic_ms` | PMS | ~8 |
| `uncertainty_lobes` | `llm_subset_uncertainty_lobes` | Uncertainty lobes | ~8 |
| `squid_glyph` | `llm_subset_squid_glyph` | Squid glyph | ~8 |

### Special Subsets

| Subset | Marker | Tests | LLM Calls |
|--------|--------|-------|-----------|
| `smoke` | `smoke` | Critical path only | ~3 |

**Combine subsets**: `--llm-subset=analyzer,routing,smoke`

---
```

**Step 5: Update remaining sections**

Update "Test Roles" section to reflect new categories (unit, uvisbox_interface, llm_integration, e2e).

Remove references to old `run_all_tests.py`.

**Step 6: Commit**

```bash
git add TESTING.md
git commit -m "docs: update TESTING.md for v0.3.4 test redesign

Complete rewrite to document:
- New test.py runner with pipeline modes
- 4-category test structure (unit, uvisbox_interface, llm_integration, e2e)
- LLM subset reference table
- Development pipeline stages

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 15: Update CONTRIBUTING.md

**Files:**
- Modify: `CONTRIBUTING.md`

**Step 1: Update test running section**

Find the testing section and replace with:

```markdown
## Running Tests

### During Development

```bash
# Before feature planning - verify UVisBox interface
python tests/test.py --pre-planning

# During development - test specific feature
python tests/test.py --iterative --llm-subset=analyzer

# Before code review - comprehensive check
python tests/test.py --code-review --llm-subset=analyzer,routing

# Before merge - full acceptance
python tests/test.py --acceptance
```

### Test a Specific File

```bash
python tests/test.py tests/unit/test_config.py
python tests/test.py tests/llm_integration/test_analyzer.py::test_specific
```

### With Coverage

```bash
python tests/test.py --pre-planning --coverage
```

See [TESTING.md](TESTING.md) for comprehensive testing guide.
```

**Step 2: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs: update CONTRIBUTING.md with new test commands

Replace run_all_tests.py references with test.py pipeline modes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 16: Update README.md

**Files:**
- Modify: `README.md`

**Step 1: Update testing quick start**

Find the testing section and update:

```markdown
## Testing

```bash
# Quick validation (0 LLM calls, < 30 seconds)
python tests/test.py --pre-planning

# Smoke test (minimal LLM usage, ~3 calls)
python tests/test.py --iterative --llm-subset=smoke

# Full test suite (~100 LLM calls, 8-10 minutes)
python tests/test.py --acceptance
```

See [TESTING.md](TESTING.md) for details.
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README.md with new test commands

Update testing section to use test.py with pipeline modes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 17: Update CLAUDE.md Development Pipeline

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update test runner references**

Find test runner references and update:

Replace:
```bash
poetry run python tests/utils/run_all_tests.py
```

With:
```bash
python tests/test.py --acceptance
```

**Step 2: Update development pipeline section**

Find "Common Development Tasks" or similar section, update test commands:

```markdown
## Development Pipeline

**Pre-planning gate:**
```bash
python tests/test.py --pre-planning
```
Must pass before creating implementation plans.

**Iterative development:**
```bash
python tests/test.py --iterative --llm-subset=<relevant-subset>
```

**Code review:**
```bash
python tests/test.py --code-review --llm-subset=<relevant-subset>
```

**Acceptance:**
```bash
python tests/test.py --acceptance
```
```

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with new test pipeline

Update development pipeline to use test.py with pipeline modes.
Replace run_all_tests.py references.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 18: Verify Pre-Planning Tests Pass

**Files:**
- None (verification only)

**Step 1: Run pre-planning tests**

Run: `python tests/test.py --pre-planning`
Expected: All unit and uvisbox_interface tests pass (0 LLM calls)

**Step 2: If failures, debug**

If any tests fail:
- Check if UVisBox installed correctly
- Check if file moves broke imports
- Fix issues before proceeding

**Step 3: Document result**

Note: No commit needed unless fixes required

---

## Task 19: Verify Smoke Tests Work

**Files:**
- None (verification only)

**Step 1: Collect smoke tests**

Run: `python tests/test.py --iterative --llm-subset=smoke --collect-only`
Expected: Shows 2 smoke tests collected

**Step 2: Run smoke tests (USES LLM)**

**WARNING**: This will make ~3 LLM calls.

Run: `python tests/test.py --iterative --llm-subset=smoke`
Expected: 2 tests run successfully

**Step 3: Verify LLM call count**

Check that only ~3 LLM calls were made (check Gemini API dashboard or count from test output)

**Step 4: Document result**

Note: No commit needed

---

## Task 20: Final Integration Test

**Files:**
- None (verification only)

**Step 1: Test each pipeline mode**

```bash
# Pre-planning
python tests/test.py --pre-planning --collect-only

# Iterative with subset
python tests/test.py --iterative --llm-subset=analyzer --collect-only

# Code review with subset
python tests/test.py --code-review --llm-subset=analyzer --collect-only

# Acceptance
python tests/test.py --acceptance --collect-only
```

Expected: Each mode collects correct test set

**Step 2: Test pytest passthrough**

```bash
python tests/test.py tests/unit/test_config.py --collect-only
python tests/test.py tests/llm_integration/test_analyzer.py -v --collect-only
```

Expected: Direct pytest-style selection works

**Step 3: Test error handling**

```bash
python tests/test.py --iterative
```

Expected: Clear error "requires --llm-subset"

**Step 4: Document any issues**

Note: Fix any issues found before final commit

---

## Task 21: Final Documentation Review

**Files:**
- Read: `TESTING.md`
- Read: `CONTRIBUTING.md`
- Read: `README.md`
- Read: `CLAUDE.md`

**Step 1: Review TESTING.md**

Check:
- [ ] All commands use `test.py`
- [ ] Pipeline stages documented
- [ ] LLM subset reference complete
- [ ] Test structure accurate

**Step 2: Review CONTRIBUTING.md**

Check:
- [ ] Test commands updated
- [ ] No references to `run_all_tests.py`

**Step 3: Review README.md**

Check:
- [ ] Quick start commands updated
- [ ] Links to TESTING.md correct

**Step 4: Review CLAUDE.md**

Check:
- [ ] Unicode bug fixed
- [ ] Pipeline commands updated
- [ ] Development workflow accurate

**Step 5: Make any final corrections**

If issues found, fix and commit:
```bash
git add [files]
git commit -m "docs: final corrections to test redesign docs"
```

---

## Success Criteria Checklist

Verify all success criteria from design doc:

- [ ] `python tests/test.py --pre-planning` runs 0 LLM calls
- [ ] `python tests/test.py --iterative` without `--llm-subset` shows clear error
- [ ] `python tests/test.py --iterative --llm-subset=smoke` runs ~3 LLM calls
- [ ] `python tests/test.py --acceptance --collect-only` collects all tests
- [ ] All documentation reflects new test structure
- [ ] CLAUDE.md workflow diagram uses ASCII only
- [ ] Can run specific tests via pytest passthrough
- [ ] Coverage reporting works for all modes

---

## Completion

After all tasks complete:

1. **Run full acceptance test** (WARNING: ~100 LLM calls)
   ```bash
   python tests/test.py --acceptance
   ```

2. **Push branch**
   ```bash
   git push -u origin feature/v0.3.4-test-redesign
   ```

3. **Use finishing-a-development-branch skill** to complete merge workflow
