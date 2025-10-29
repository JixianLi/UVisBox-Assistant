# Phase 9: Comprehensive Testing & Test Reorganization (Updated for BoxplotStyleConfig)

**Goal**: Reorganize test suite with clear structure, comprehensive coverage, and eliminate phase-specific tests that have served their purpose.

**Duration**: 1 day

**Updated**: 2025-01-29 - Reflects BoxplotStyleConfig interface changes

---

## Overview

The current test suite has accumulated ~2600 lines across 17 files organized by implementation phase (test_phase1.py, test_phase2.py, etc.). This made sense during development but is now confusing for maintenance.

**Problems with current structure:**
- Test files named by phase (test_phase1.py, test_phase2.py) don't indicate what they test
- Multiple similar integration tests (test_graph.py, test_graph_quick.py, test_graph_integration.py)
- Unclear which test to run for specific scenarios
- No quick sanity check test
- **Tests don't reflect BoxplotStyleConfig interface changes**

**Goals:**
1. Create clear test categories (unit, integration, e2e, interactive)
2. Keep one simple sanity check: test_simple.py (prompt in → output out)
3. Eliminate redundant and phase-specific tests
4. Document what each test does and when to run it
5. Reduce total test count while improving coverage clarity
6. **Update tests to use new BoxplotStyleConfig parameters**

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
│   ├── test_command_parser.py   # Test command parser patterns (UPDATED)
│   └── test_config.py           # Test configuration loading
│
├── integration/                 # Integration tests (component interactions)
│   ├── __init__.py
│   ├── test_graph_workflow.py   # Test LangGraph execution (consolidated)
│   ├── test_conversation.py     # Test ConversationSession (multi-turn)
│   ├── test_hybrid_control.py   # Test hybrid control fast path (UPDATED)
│   ├── test_error_handling.py   # Test error recovery and circuit breaker
│   └── test_session_management.py # Test session cleanup and stats
│
├── e2e/                         # End-to-end tests (full system)
│   ├── __init__.py
│   ├── test_all_visualizations.py  # Test all 5 vis types end-to-end (UPDATED)
│   ├── test_user_workflows.py   # Test common user scenarios (UPDATED)
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
✅ tests/test_hybrid_control.py  → integration/test_hybrid_control.py (UPDATE for new params)
✅ tests/test_session_management.py → integration/test_session_management.py (keep as-is)
✅ tests/test_matplotlib_behavior.py → e2e/test_matplotlib.py (keep as-is)
✅ tests/interactive_test.py     → interactive/interactive_test.py (UPDATE for new params)
```

### Files to CREATE

```
🆕 test_simple.py                # Quick sanity check (prompt → output)
🆕 unit/test_tools.py            # Test individual tool functions (with BoxplotStyleConfig)
🆕 unit/test_command_parser.py   # Test command parsing (with new styling params)
🆕 unit/test_config.py           # Test configuration (with updated defaults)
🆕 integration/test_graph_workflow.py # Consolidated graph tests
🆕 integration/test_conversation.py   # Consolidated conversation tests
🆕 e2e/test_all_visualizations.py     # Test all 5 vis types (with new params)
🆕 e2e/test_user_workflows.py         # Test common user scenarios (with styling)
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

Test individual tool functions without LangGraph, with BoxplotStyleConfig parameters:

```python
"""Unit tests for data_tools and vis_tools."""

import numpy as np
from chatuvisbox.data_tools import (
    generate_ensemble_curves,
    generate_scalar_field_ensemble,
    generate_vector_field_ensemble,
    load_csv_to_numpy,
    clear_session
)
from chatuvisbox.vis_tools import (
    plot_functional_boxplot,
    plot_curve_boxplot,
    plot_contour_boxplot,
    plot_probabilistic_marching_squares,
    plot_uncertainty_lobes
)
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend


def test_generate_ensemble_curves():
    """Test curve generation with various parameters."""
    result = generate_ensemble_curves(n_curves=10, n_points=50)
    assert result['status'] == 'success'
    assert 'output_path' in result

    data = np.load(result['output_path'])
    assert data.shape == (10, 50)


def test_plot_functional_boxplot_with_styling():
    """Test functional boxplot with BoxplotStyleConfig parameters."""
    # Generate test data
    curves_result = generate_ensemble_curves(n_curves=10, n_points=50)

    # Test with styling parameters
    result = plot_functional_boxplot(
        data_path=curves_result['output_path'],
        percentiles=[25, 50, 75, 90],
        percentile_colormap='plasma',
        show_median=True,
        median_color='blue',
        median_width=2.5,
        median_alpha=0.8,
        show_outliers=True,
        outliers_color='black',
        outliers_width=1.5,
        outliers_alpha=0.7
    )

    assert result['status'] == 'success'
    assert '_vis_params' in result

    # Verify all styling params preserved
    params = result['_vis_params']
    assert params['median_color'] == 'blue'
    assert params['median_width'] == 2.5
    assert params['median_alpha'] == 0.8
    assert params['outliers_color'] == 'black'
    assert params['outliers_width'] == 1.5
    assert params['outliers_alpha'] == 0.7


def test_plot_curve_boxplot_with_workers():
    """Test curve boxplot with workers parameter."""
    curves_result = generate_ensemble_curves(n_curves=10, n_points=50)

    result = plot_curve_boxplot(
        data_path=curves_result['output_path'],
        percentiles=[50, 90],
        percentile_colormap='viridis',
        show_median=True,
        show_outliers=False,
        workers=4
    )

    assert result['status'] == 'success'
    assert result['_vis_params']['workers'] == 4


def test_plot_contour_boxplot_full_params():
    """Test contour boxplot with all BoxplotStyleConfig parameters."""
    field_result = generate_scalar_field_ensemble(nx=20, ny=20, n_ensemble=10)

    result = plot_contour_boxplot(
        data_path=field_result['output_path'],
        isovalue=0.5,
        percentiles=[25, 50, 75],
        percentile_colormap='plasma',
        show_median=True,
        median_color='red',
        median_width=3.0,
        median_alpha=1.0,
        show_outliers=True,
        outliers_color='gray',
        outliers_width=1.0,
        outliers_alpha=0.5,
        workers=8
    )

    assert result['status'] == 'success'
    params = result['_vis_params']
    assert params['workers'] == 8
    assert params['outliers_alpha'] == 0.5


# ... continue with all visualization functions
```

**Characteristics**:
- 0 API calls (direct function tests)
- Fast execution (< 5 seconds total)
- Test return values, error handling, parameter validation
- **Test all new BoxplotStyleConfig parameters**

---

#### File: `tests/unit/test_command_parser.py`

Test command parsing patterns, including new styling parameters:

```python
"""Unit tests for hybrid control command parser."""

from chatuvisbox.command_parser import parse_simple_command, apply_command_to_params


def test_parse_colormap():
    cmd = parse_simple_command("colormap plasma")
    assert cmd is not None
    assert cmd.param_name == "colormap"
    assert cmd.value == "plasma"


def test_parse_median_color():
    """Test parsing median color command."""
    cmd = parse_simple_command("median color blue")
    assert cmd is not None
    assert cmd.param_name == "median_color"
    assert cmd.value == "blue"


def test_parse_median_width():
    """Test parsing median width command."""
    cmd = parse_simple_command("median width 2.5")
    assert cmd is not None
    assert cmd.param_name == "median_width"
    assert cmd.value == 2.5


def test_parse_median_alpha():
    """Test parsing median alpha command."""
    cmd = parse_simple_command("median alpha 0.8")
    assert cmd is not None
    assert cmd.param_name == "median_alpha"
    assert cmd.value == 0.8


def test_parse_outliers_color():
    """Test parsing outliers color command."""
    cmd = parse_simple_command("outliers color black")
    assert cmd is not None
    assert cmd.param_name == "outliers_color"
    assert cmd.value == "black"


def test_parse_outliers_width():
    """Test parsing outliers width command."""
    cmd = parse_simple_command("outliers width 1.5")
    assert cmd is not None
    assert cmd.param_name == "outliers_width"
    assert cmd.value == 1.5


def test_parse_outliers_alpha():
    """Test parsing outliers alpha command."""
    cmd = parse_simple_command("outliers alpha 1.0")
    assert cmd is not None
    assert cmd.param_name == "outliers_alpha"
    assert cmd.value == 1.0


def test_apply_styling_params():
    """Test applying BoxplotStyleConfig params to current params."""
    current = {
        "_tool_name": "plot_functional_boxplot",
        "data_path": "/path/to/data.npy",
        "median_color": "red",
        "outliers_alpha": 0.5
    }

    # Update outliers color
    cmd = parse_simple_command("outliers color black")
    updated = apply_command_to_params(cmd, current)

    assert updated["outliers_color"] == "black"
    assert updated["median_color"] == "red"  # Unchanged
    assert updated["outliers_alpha"] == 0.5  # Unchanged


# ... test all command patterns
```

---

#### File: `tests/unit/test_config.py`

Test configuration with updated BoxplotStyleConfig defaults:

```python
"""Unit tests for configuration."""

from chatuvisbox import config


def test_config_paths_exist():
    """Test that all configured paths exist."""
    assert config.TEMP_DIR.exists()
    assert config.TEST_DATA_DIR.exists()
    assert config.LOG_DIR.exists()


def test_boxplot_style_config_defaults():
    """Test BoxplotStyleConfig default parameters."""
    params = config.DEFAULT_VIS_PARAMS

    # Percentiles and colormap
    assert params["percentiles"] == [25, 50, 90, 100]
    assert params["percentile_colormap"] == "viridis"

    # Median styling
    assert params["show_median"] == True
    assert params["median_color"] == "red"
    assert params["median_width"] == 3.0
    assert params["median_alpha"] == 1.0

    # Outliers styling
    assert params["show_outliers"] == False
    assert params["outliers_color"] == "gray"
    assert params["outliers_width"] == 1.0
    assert params["outliers_alpha"] == 0.5

    # Parallel computation
    assert params["workers"] == 12


def test_no_plot_all_curves_param():
    """Verify plot_all_curves parameter is removed."""
    params = config.DEFAULT_VIS_PARAMS
    assert "plot_all_curves" not in params


# ... test all defaults
```

---

### Task 9.3: Create Integration Tests

#### File: `tests/integration/test_graph_workflow.py`

Consolidate test_graph.py, test_graph_quick.py, test_graph_integration.py with updated parameters:

```python
"""Integration tests for LangGraph workflow execution."""

def test_functional_boxplot_with_styling():
    """Test functional boxplot with styling parameters through graph."""
    session = ConversationSession()

    # Request with specific styling
    result = session.send(
        "Generate 20 curves and plot functional boxplot with "
        "median color blue and outliers color black"
    )

    assert result['last_vis_params'] is not None
    params = result['last_vis_params']

    # Verify styling applied (may be defaults if LLM didn't parse)
    assert 'median_color' in params
    assert 'outliers_color' in params

    session.clear()


# 4-5 focused tests, ~150 lines total, 15-20 API calls
```

---

#### File: `tests/integration/test_hybrid_control.py`

**UPDATED** - Test fast parameter updates with new styling parameters:

```python
"""Integration tests for hybrid control fast path."""

from chatuvisbox.hybrid_control import try_hybrid_control
from chatuvisbox.data_tools import generate_ensemble_curves
import matplotlib.pyplot as plt


def test_hybrid_median_styling():
    """Test fast update of median styling parameters."""
    # Generate initial visualization
    curves_result = generate_ensemble_curves(n_curves=10, n_points=50)

    initial_params = {
        "_tool_name": "plot_functional_boxplot",
        "data_path": curves_result['output_path'],
        "median_color": "red",
        "median_width": 3.0,
        "median_alpha": 1.0
    }

    # Try hybrid update - median color
    result = try_hybrid_control("median color blue", initial_params)
    assert result is not None
    assert result['_vis_params']['median_color'] == "blue"

    # Try hybrid update - median width
    result = try_hybrid_control("median width 2.0", initial_params)
    assert result is not None
    assert result['_vis_params']['median_width'] == 2.0

    plt.close('all')


def test_hybrid_outliers_styling():
    """Test fast update of outliers styling parameters."""
    curves_result = generate_ensemble_curves(n_curves=10, n_points=50)

    initial_params = {
        "_tool_name": "plot_functional_boxplot",
        "data_path": curves_result['output_path'],
        "show_outliers": True,
        "outliers_color": "gray",
        "outliers_alpha": 0.5
    }

    # Update outliers color
    result = try_hybrid_control("outliers color black", initial_params)
    assert result is not None
    assert result['_vis_params']['outliers_color'] == "black"

    # Update outliers alpha
    result = try_hybrid_control("outliers alpha 1.0", initial_params)
    assert result is not None
    assert result['_vis_params']['outliers_alpha'] == 1.0

    plt.close('all')


# 8-10 focused tests covering all new parameters
```

---

### Task 9.4: Create End-to-End Tests

#### File: `tests/e2e/test_all_visualizations.py`

**UPDATED** - Test all 5 visualization types with BoxplotStyleConfig parameters:

```python
"""End-to-end tests for all visualization types."""

from chatuvisbox.conversation import ConversationSession
import matplotlib.pyplot as plt


def test_functional_boxplot_full_styling_e2e():
    """Test functional boxplot with all BoxplotStyleConfig parameters."""
    session = ConversationSession()

    # Request with multiple styling parameters
    result = session.send(
        "Generate 20 curves and plot functional boxplot with "
        "percentiles 25, 50, 75, 90, show outliers, "
        "median color blue, outliers color black"
    )

    assert result['last_vis_params'] is not None
    params = result['last_vis_params']
    assert params['_tool_name'] == 'plot_functional_boxplot'

    # Verify parameters present (values may vary based on LLM interpretation)
    assert 'median_color' in params
    assert 'outliers_color' in params
    assert 'show_outliers' in params

    session.clear()
    plt.close('all')


def test_curve_boxplot_with_workers_e2e():
    """Test curve boxplot end-to-end with workers parameter."""
    session = ConversationSession()

    result = session.send(
        "Generate 15 curves and plot curve boxplot"
    )

    assert result['last_vis_params'] is not None
    params = result['last_vis_params']

    # Workers should have default value
    assert 'workers' in params
    assert params['workers'] == 12  # Default

    session.clear()
    plt.close('all')


def test_contour_boxplot_full_params_e2e():
    """Test contour boxplot with all parameters."""
    session = ConversationSession()

    result = session.send(
        "Generate 20x20 scalar field with 15 members and "
        "plot contour boxplot at isovalue 0.5 with "
        "show median and show outliers"
    )

    assert result['last_vis_params'] is not None
    params = result['last_vis_params']
    assert params['_tool_name'] == 'plot_contour_boxplot'
    assert 'workers' in params
    assert 'median_color' in params
    assert 'outliers_color' in params

    session.clear()
    plt.close('all')


# 5-6 tests covering all visualizations with new parameters
# ~150 lines, 25-30 API calls
```

---

#### File: `tests/e2e/test_user_workflows.py`

**UPDATED** - Test common workflows with styling parameter updates:

```python
"""End-to-end tests for common user workflows."""

from chatuvisbox.conversation import ConversationSession
import matplotlib.pyplot as plt


def test_iterative_styling_workflow():
    """Test workflow of generating data then iteratively adjusting styling."""
    session = ConversationSession()

    # Generate and visualize
    result1 = session.send("Generate 20 curves and plot functional boxplot")
    assert result1['last_vis_params'] is not None

    # Update median styling
    result2 = session.send("median color blue")
    assert result2['last_vis_params']['median_color'] == 'blue'

    # Update outliers
    result3 = session.send("show outliers")
    assert result3['last_vis_params']['show_outliers'] == True

    # Update outliers styling
    result4 = session.send("outliers color black")
    assert result4['last_vis_params']['outliers_color'] == 'black'

    # Update outliers alpha
    result5 = session.send("outliers alpha 1.0")
    assert result5['last_vis_params']['outliers_alpha'] == 1.0

    session.clear()
    plt.close('all')


def test_full_customization_workflow():
    """Test comprehensive styling customization."""
    session = ConversationSession()

    # Start with visualization
    session.send("Generate 25 curves and show functional boxplot")

    # Customize median
    session.send("median color red")
    session.send("median width 4.0")
    session.send("median alpha 0.9")

    # Customize outliers
    session.send("show outliers")
    session.send("outliers color darkgray")
    session.send("outliers width 2.0")
    result = session.send("outliers alpha 0.7")

    # Verify final state
    params = result['last_vis_params']
    assert params['median_color'] == 'red'
    assert params['median_width'] == 4.0
    assert params['outliers_alpha'] == 0.7

    session.clear()
    plt.close('all')


# 5-6 tests covering common workflows with styling
# ~150 lines, 25-30 API calls
```

---

## Part C: Migration Steps

### Step 1: Create New Structure
```bash
mkdir -p tests/unit tests/integration tests/e2e tests/interactive tests/utils
```

### Step 2: Create Core Files with BoxplotStyleConfig Updates
1. Create `test_simple.py` (root level)
2. Create all unit tests **with BoxplotStyleConfig parameters**
3. Create all integration tests **with hybrid control styling tests**
4. Create all e2e tests **with full parameter coverage**
5. Create test runner and README

### Step 3: Move and Update Existing Tests
1. Move `test_routing.py` → `unit/test_routing.py`
2. Move `test_error_handling.py` → `integration/`
3. **Update** `test_hybrid_control.py` → `integration/` (**add styling param tests**)
4. Move `test_session_management.py` → `integration/`
5. Move `test_matplotlib_behavior.py` → `e2e/test_matplotlib.py`
6. **Update** `interactive_test.py` → `interactive/` (**add styling scenarios**)

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
Update documentation to reflect:
- New test structure
- **BoxplotStyleConfig parameter testing**
- **New hybrid control commands for styling**

---

## Validation Checklist

- [ ] test_simple.py works as quick sanity check
- [ ] All unit tests pass (0 API calls)
- [ ] **Unit tests cover all BoxplotStyleConfig parameters**
- [ ] All integration tests pass with delays
- [ ] **Hybrid control tests cover all new styling commands**
- [ ] All e2e tests pass with delays
- [ ] **E2E tests verify full parameter preservation**
- [ ] Test README clearly explains structure
- [ ] CLAUDE.md updated with BoxplotStyleConfig interface
- [ ] TESTING.md updated with new commands
- [ ] Old test files deleted
- [ ] Total line count reduced by ~1000+ lines
- [ ] New tests are more maintainable and clearer
- [ ] **No references to deprecated plot_all_curves parameter**

---

## Key Updates for BoxplotStyleConfig

### Parameters to Test:

**Core Parameters:**
- `percentiles`: List[float]
- `percentile_colormap`: str

**Median Styling:**
- `show_median`: bool
- `median_color`: str
- `median_width`: float
- `median_alpha`: float

**Outliers Styling:**
- `show_outliers`: bool
- `outliers_color`: str
- `outliers_width`: float
- `outliers_alpha`: float

**Performance:**
- `workers`: int (for curve_boxplot and contour_boxplot)

### Deprecated Parameters:
- ❌ `plot_all_curves` - REMOVED, do not test

### New Hybrid Commands to Test:
- `median color <color>`
- `median width <number>`
- `median alpha <number>`
- `outliers color <color>`
- `outliers width <number>`
- `outliers alpha <number>`

---

## Expected Outcomes

**Before (Current)**:
- 17 test files, ~2600 lines
- Unclear naming (test_phase1.py, test_graph.py)
- Redundant tests (3 graph tests)
- Hard to know what to run
- **Tests don't cover BoxplotStyleConfig parameters**

**After (Phase 9)**:
- ~14 test files, ~1600-1800 lines
- Clear categories (unit/, integration/, e2e/)
- One simple sanity check (test_simple.py)
- Clear documentation (tests/README.md)
- Consolidated redundant tests
- Easy to run subset of tests
- **Comprehensive BoxplotStyleConfig parameter coverage**
- **All 13 new styling commands tested**

**Benefits**:
1. ✅ Clear test organization
2. ✅ Easy to find relevant tests
3. ✅ Quick sanity check available
4. ✅ Reduced redundancy
5. ✅ Better maintainability
6. ✅ Clear documentation
7. ✅ **Full BoxplotStyleConfig interface coverage**
8. ✅ **Styling parameter validation**

---

## Next Phase

Phase 10 will focus on final documentation, packaging, and distribution preparation with updated BoxplotStyleConfig API documentation.
