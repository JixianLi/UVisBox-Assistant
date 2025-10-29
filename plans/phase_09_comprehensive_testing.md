# Phase 9: Comprehensive Testing & Test Reorganization

**Goal**: Reorganize test suite with clear structure, comprehensive coverage, and eliminate phase-specific tests that have served their purpose.

**Duration**: 1 day

---

## Overview

The current test suite has accumulated ~2600 lines across 17 files organized by implementation phase (test_phase1.py, test_phase2.py, etc.). This made sense during development but is now confusing for maintenance.

**Problems with current structure:**
- Test files named by phase (test_phase1.py, test_phase2.py) don't indicate what they test
- Multiple similar integration tests (test_graph.py, test_graph_quick.py, test_graph_integration.py)
- Unclear which test to run for specific scenarios
- No quick sanity check test

**Goals:**
1. Create clear test categories (unit, integration, e2e, interactive)
2. Keep one simple sanity check: test_simple.py (prompt in → output out)
3. Eliminate redundant and phase-specific tests
4. Document what each test does and when to run it
5. Reduce total test count while improving coverage clarity

---

## Part A: Test Reorganization Strategy

### Proposed New Structure

```
tests/
├── __init__.py                  # Test package marker
├── conftest.py                  # Pytest fixtures (keep as-is)
│
├── test_simple.py               # ⭐ NEW: Quick sanity check (prompt → output)
│
├── unit/                        # Unit tests (individual components)
│   ├── __init__.py
│   ├── test_tools.py            # Test data_tools and vis_tools functions
│   ├── test_routing.py          # Test routing logic (from current test_routing.py)
│   ├── test_command_parser.py   # Test command parser patterns
│   └── test_config.py           # Test configuration loading
│
├── integration/                 # Integration tests (component interactions)
│   ├── __init__.py
│   ├── test_graph_workflow.py   # Test LangGraph execution (consolidated)
│   ├── test_conversation.py     # Test ConversationSession (multi-turn)
│   ├── test_hybrid_control.py   # Test hybrid control fast path
│   ├── test_error_handling.py   # Test error recovery and circuit breaker
│   └── test_session_management.py # Test session cleanup and stats
│
├── e2e/                         # End-to-end tests (full system)
│   ├── __init__.py
│   ├── test_all_visualizations.py  # Test all 5 vis types end-to-end
│   ├── test_user_workflows.py   # Test common user scenarios
│   └── test_matplotlib.py       # Test matplotlib non-blocking behavior
│
├── interactive/                 # Interactive/manual tests
│   ├── __init__.py
│   ├── interactive_test.py      # Menu-driven testing (keep as-is)
│   └── repl_test.py             # Test REPL interface manually
│
└── utils/                       # Test utilities
    ├── __init__.py
    ├── run_all_tests.py         # Run full test suite with delays
    └── test_helpers.py          # Shared test utilities
```

### Files to DELETE (served their purpose during development)

```
❌ tests/test_phase1.py          # 172 lines - Phase 1 validation, now redundant
❌ tests/test_phase2.py          # 290 lines - Phase 2 validation, now redundant
❌ tests/test_graph.py           # 103 lines - Redundant with test_graph_quick.py
❌ tests/test_graph_integration.py # 187 lines - Consolidate into test_graph_workflow.py
❌ tests/test_graph_quick.py     # 96 lines - Consolidate into test_graph_workflow.py
❌ tests/test_happy_path.py      # 245 lines - Redundant, consolidate into e2e tests
❌ tests/test_multiturn.py       # 243 lines - Consolidate into test_conversation.py
❌ tests/run_tests_with_delays.py # 92 lines - Move to utils/run_all_tests.py
❌ tests/simple_test.py          # 16 lines - Replace with new test_simple.py

Total to delete: ~1444 lines
```

### Files to KEEP and REORGANIZE

```
✅ tests/test_routing.py         → unit/test_routing.py (minimal changes)
✅ tests/test_error_handling.py  → integration/test_error_handling.py (keep as-is)
✅ tests/test_hybrid_control.py  → integration/test_hybrid_control.py (keep as-is)
✅ tests/test_session_management.py → integration/test_session_management.py (keep as-is)
✅ tests/test_matplotlib_behavior.py → e2e/test_matplotlib.py (keep as-is)
✅ tests/interactive_test.py     → interactive/interactive_test.py (keep as-is)
```

### Files to CREATE

```
🆕 test_simple.py                # Quick sanity check (prompt → output)
🆕 unit/test_tools.py            # Test individual tool functions
🆕 unit/test_command_parser.py   # Test command parsing
🆕 unit/test_config.py           # Test configuration
🆕 integration/test_graph_workflow.py # Consolidated graph tests
🆕 integration/test_conversation.py   # Consolidated conversation tests
🆕 e2e/test_all_visualizations.py     # Test all 5 vis types
🆕 e2e/test_user_workflows.py         # Test common user scenarios
🆕 utils/run_all_tests.py        # Improved test runner
🆕 utils/test_helpers.py         # Shared utilities
```

---

## Part B: Implementation Tasks

### Task 9.1: Create test_simple.py (Quick Sanity Check)

**File**: `tests/test_simple.py` (root level)

**Purpose**: ONE simple test that anyone can run to verify the system works

**Requirements**:
- Input: A prompt string
- Output: Success/failure with basic validation
- Must complete in < 30 seconds
- No API rate limit concerns (single request)
- Clear pass/fail indicator

**Implementation**:

```python
"""
Quick sanity check test.

Run this to verify the system works end-to-end.
Single prompt → single output, no complex scenarios.
"""

from chatuvisbox.conversation import ConversationSession
import matplotlib.pyplot as plt


def test_simple_end_to_end():
    """
    Test: Single prompt generates data and creates visualization.

    This is the simplest possible test - if this passes, core functionality works.
    """
    print("\n" + "="*70)
    print("SIMPLE SANITY CHECK")
    print("="*70)

    session = ConversationSession()

    # Simple prompt that exercises both data generation and visualization
    prompt = "Generate 20 curves and plot functional boxplot"

    print(f"\nPrompt: {prompt}")
    print("\n🔹 Processing...")

    result = session.send(prompt)

    # Verify success
    assert result is not None, "Result should not be None"
    assert result.get("current_data_path") is not None, "Should have generated data"
    assert result.get("last_vis_params") is not None, "Should have created visualization"

    response = session.get_last_response()
    print(f"\n✓ Response: {response}")

    # Cleanup
    session.clear()
    plt.close('all')

    print("\n✅ SIMPLE TEST PASSED")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_simple_end_to_end()
```

**Usage**:
```bash
python tests/test_simple.py        # Quick sanity check
pytest tests/test_simple.py        # Or with pytest
```

---

### Task 9.2: Create Unit Tests

#### File: `tests/unit/test_tools.py`

Test individual tool functions without LangGraph:

```python
"""Unit tests for data_tools and vis_tools."""

def test_generate_ensemble_curves():
    """Test curve generation with various parameters."""
    pass

def test_generate_scalar_field_ensemble():
    """Test scalar field generation."""
    pass

def test_generate_vector_field_ensemble():
    """Test vector field generation."""
    pass

def test_load_csv_to_numpy():
    """Test CSV loading."""
    pass

def test_clear_session():
    """Test session cleanup."""
    pass

def test_plot_functional_boxplot_direct():
    """Test functional boxplot without graph."""
    pass

# ... test all 5 visualization functions directly
```

**Characteristics**:
- 0 API calls (direct function tests)
- Fast execution (< 5 seconds total)
- Test return values, error handling, parameter validation

---

#### File: `tests/unit/test_command_parser.py`

Test command parsing patterns:

```python
"""Unit tests for hybrid control command parser."""

from chatuvisbox.command_parser import parse_simple_command

def test_parse_colormap():
    cmd = parse_simple_command("colormap plasma")
    assert cmd is not None
    assert cmd.param_name == "colormap"
    assert cmd.value == "plasma"

def test_parse_percentile():
    cmd = parse_simple_command("percentile 75")
    assert cmd is not None
    assert cmd.param_name == "percentiles"
    assert cmd.value == [75.0]

# ... test all command patterns
```

---

#### File: `tests/unit/test_config.py`

Test configuration:

```python
"""Unit tests for configuration."""

from chatuvisbox import config

def test_config_paths_exist():
    """Test that all configured paths exist."""
    assert config.TEMP_DIR.exists()
    assert config.TEST_DATA_DIR.exists()
    assert config.LOG_DIR.exists()

def test_default_vis_params():
    """Test that default params are properly set."""
    assert "percentiles" in config.DEFAULT_VIS_PARAMS
    assert config.DEFAULT_VIS_PARAMS["isovalue"] == 0.5
    # ... test all defaults
```

---

### Task 9.3: Create Integration Tests

#### File: `tests/integration/test_graph_workflow.py`

Consolidate test_graph.py, test_graph_quick.py, test_graph_integration.py:

```python
"""Integration tests for LangGraph workflow execution."""

def test_graph_compilation():
    """Test that graph compiles without errors."""
    pass

def test_data_generation_workflow():
    """Test data generation through graph."""
    pass

def test_visualization_workflow():
    """Test visualization through graph."""
    pass

def test_chained_workflow():
    """Test data generation → visualization in one prompt."""
    pass

# 4-5 focused tests, ~150 lines total, 15-20 API calls
```

---

#### File: `tests/integration/test_conversation.py`

Consolidate test_multiturn.py:

```python
"""Integration tests for multi-turn conversations."""

def test_conversation_state_persistence():
    """Test state persists across turns."""
    pass

def test_conversation_context_reference():
    """Test 'plot that', 'change it' references work."""
    pass

def test_conversation_reset():
    """Test reset clears state."""
    pass

# 5-6 focused tests, ~150 lines total, 20-25 API calls
```

---

### Task 9.4: Create End-to-End Tests

#### File: `tests/e2e/test_all_visualizations.py`

Test all 5 visualization types end-to-end:

```python
"""End-to-end tests for all visualization types."""

def test_functional_boxplot_e2e():
    """Generate curves → plot functional boxplot."""
    pass

def test_curve_boxplot_e2e():
    """Generate curves → plot curve boxplot."""
    pass

def test_probabilistic_marching_squares_e2e():
    """Generate scalar field → plot PMS."""
    pass

def test_uncertainty_lobes_e2e():
    """Generate vector field → plot lobes."""
    pass

def test_contour_boxplot_e2e():
    """Generate scalar field → plot contour boxplot."""
    pass

# 5 tests, ~120 lines, 25-30 API calls
```

---

#### File: `tests/e2e/test_user_workflows.py`

Test common user scenarios:

```python
"""End-to-end tests for common user workflows."""

def test_load_csv_and_visualize():
    """Load CSV → visualize workflow."""
    pass

def test_generate_and_modify():
    """Generate → visualize → modify parameters workflow."""
    pass

def test_hybrid_control_workflow():
    """Test quick parameter updates via hybrid control."""
    pass

def test_session_cleanup_workflow():
    """Test full session with cleanup."""
    pass

# 4-5 tests, ~100 lines, 20-25 API calls
```

---

### Task 9.5: Create Test Utilities

#### File: `tests/utils/run_all_tests.py`

Improved test runner:

```python
"""
Run all tests with proper delays for rate limits.

Usage:
    python tests/utils/run_all_tests.py               # Run all
    python tests/utils/run_all_tests.py --unit        # Unit tests only
    python tests/utils/run_all_tests.py --integration # Integration tests only
    python tests/utils/run_all_tests.py --e2e         # E2E tests only
    python tests/utils/run_all_tests.py --quick       # Unit + test_simple.py
"""

import subprocess
import time
import sys
import argparse

UNIT_TESTS = [
    "tests/unit/test_tools.py",
    "tests/unit/test_routing.py",
    "tests/unit/test_command_parser.py",
    "tests/unit/test_config.py",
]

INTEGRATION_TESTS = [
    "tests/integration/test_graph_workflow.py",
    "tests/integration/test_conversation.py",
    "tests/integration/test_hybrid_control.py",
    "tests/integration/test_error_handling.py",
    "tests/integration/test_session_management.py",
]

E2E_TESTS = [
    "tests/e2e/test_all_visualizations.py",
    "tests/e2e/test_user_workflows.py",
    "tests/e2e/test_matplotlib.py",
]

def run_tests(test_files, delay=3):
    """Run tests with delays between files."""
    passed = 0
    failed = 0

    for i, test_file in enumerate(test_files):
        print(f"\n{'='*70}")
        print(f"Running: {test_file}")
        print('='*70)

        result = subprocess.run(
            ["python", test_file],
            capture_output=False
        )

        if result.returncode == 0:
            passed += 1
        else:
            failed += 1

        # Delay between tests
        if i < len(test_files) - 1:
            print(f"\n⏳ Pausing {delay}s to respect rate limits...")
            time.sleep(delay)

    return passed, failed

# ... implementation
```

---

### Task 9.6: Create Documentation

#### File: `tests/README.md`

```markdown
# ChatUVisBox Test Suite

## Quick Start

```bash
# Quick sanity check (30 seconds)
python tests/test_simple.py

# Run all tests with automatic delays (~10 minutes)
python tests/utils/run_all_tests.py

# Run specific test category
python tests/utils/run_all_tests.py --unit          # Fast, no API calls
python tests/utils/run_all_tests.py --integration  # 3-4 minutes
python tests/utils/run_all_tests.py --e2e          # 4-5 minutes
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual functions and components in isolation
- **API Calls**: 0 (no LLM calls)
- **Duration**: < 10 seconds
- **When to run**: After modifying individual functions

**Files**:
- `test_tools.py` - Test data_tools and vis_tools functions
- `test_routing.py` - Test routing logic
- `test_command_parser.py` - Test hybrid control command parsing
- `test_config.py` - Test configuration loading

### Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions (LangGraph, ConversationSession)
- **API Calls**: 15-25 per file
- **Duration**: 2-4 minutes per file
- **When to run**: After modifying workflows or state management

**Files**:
- `test_graph_workflow.py` - LangGraph execution workflows
- `test_conversation.py` - Multi-turn conversation state
- `test_hybrid_control.py` - Fast parameter updates
- `test_error_handling.py` - Error recovery and circuit breaker
- `test_session_management.py` - Session cleanup and stats

### End-to-End Tests (`tests/e2e/`)
- **Purpose**: Test complete user workflows
- **API Calls**: 20-30 per file
- **Duration**: 3-5 minutes per file
- **When to run**: Before releases or major changes

**Files**:
- `test_all_visualizations.py` - All 5 visualization types
- `test_user_workflows.py` - Common user scenarios
- `test_matplotlib.py` - Matplotlib non-blocking behavior

### Interactive Tests (`tests/interactive/`)
- **Purpose**: Manual testing and exploration
- **API Calls**: User-paced
- **Duration**: User-controlled
- **When to run**: For manual verification

**Files**:
- `interactive_test.py` - Menu-driven testing with 24+ scenarios

## Test Coverage

| Component | Unit | Integration | E2E |
|-----------|------|-------------|-----|
| Data Tools | ✓ | ✓ | ✓ |
| Vis Tools | ✓ | ✓ | ✓ |
| LangGraph | - | ✓ | ✓ |
| Conversation | - | ✓ | ✓ |
| Hybrid Control | ✓ | ✓ | ✓ |
| Error Handling | - | ✓ | ✓ |
| Session Mgmt | ✓ | ✓ | ✓ |

## Rate Limit Guidelines

**Gemini Free Tier**: 30 requests per minute

- Unit tests: 0 API calls (safe to run repeatedly)
- Integration tests: Wait 60s between runs
- E2E tests: Wait 60s between runs
- Full suite: Automatic delays built-in

## CI/CD Recommendations

```yaml
# Fast feedback loop (on every commit)
- Unit tests (< 10s, no API calls)
- test_simple.py (30s, 1-2 API calls)

# Pull request validation
- Unit tests
- Integration tests
- test_simple.py

# Pre-release validation
- All tests (unit + integration + e2e)
```
```

---

## Part C: Migration Steps

### Step 1: Create New Structure
```bash
mkdir -p tests/unit tests/integration tests/e2e tests/interactive tests/utils
```

### Step 2: Create Core Files
1. Create `test_simple.py` (root level)
2. Create all unit tests
3. Create all integration tests (consolidate existing)
4. Create all e2e tests (consolidate existing)
5. Create test runner and README

### Step 3: Move and Adapt Existing Tests
1. Move `test_routing.py` → `unit/test_routing.py`
2. Move `test_error_handling.py` → `integration/`
3. Move `test_hybrid_control.py` → `integration/`
4. Move `test_session_management.py` → `integration/`
5. Move `test_matplotlib_behavior.py` → `e2e/test_matplotlib.py`
6. Move `interactive_test.py` → `interactive/`

### Step 4: Delete Obsolete Tests
```bash
rm tests/test_phase1.py
rm tests/test_phase2.py
rm tests/test_graph.py
rm tests/test_graph_integration.py
rm tests/test_graph_quick.py
rm tests/test_happy_path.py
rm tests/test_multiturn.py
rm tests/run_tests_with_delays.py
rm tests/simple_test.py
```

### Step 5: Update CLAUDE.md and TESTING.md
Update documentation to reflect new structure.

---

## Validation Checklist

- [ ] test_simple.py works as quick sanity check
- [ ] All unit tests pass (0 API calls)
- [ ] All integration tests pass with delays
- [ ] All e2e tests pass with delays
- [ ] Test README clearly explains structure
- [ ] CLAUDE.md updated with new test structure
- [ ] TESTING.md updated with new commands
- [ ] Old test files deleted
- [ ] Total line count reduced by ~1000+ lines
- [ ] New tests are more maintainable and clearer

---

## Expected Outcomes

**Before (Current)**:
- 17 test files, ~2600 lines
- Unclear naming (test_phase1.py, test_graph.py)
- Redundant tests (3 graph tests)
- Hard to know what to run

**After (Phase 9)**:
- ~14 test files, ~1500-1700 lines
- Clear categories (unit/, integration/, e2e/)
- One simple sanity check (test_simple.py)
- Clear documentation (tests/README.md)
- Consolidated redundant tests
- Easy to run subset of tests

**Benefits**:
1. ✅ Clear test organization
2. ✅ Easy to find relevant tests
3. ✅ Quick sanity check available
4. ✅ Reduced redundancy
5. ✅ Better maintainability
6. ✅ Clear documentation

---

## Next Phase

Phase 10 will focus on final documentation, packaging, and distribution preparation.
