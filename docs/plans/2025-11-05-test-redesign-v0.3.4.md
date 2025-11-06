# Test Redesign for v0.3.4

## Overview

Restructure the test suite to align with the development pipeline and provide budget-conscious LLM test execution.

## Problems Solved

1. **Current test structure doesn't map to development workflow**: Tests are organized by technical layer (unit/integration/e2e) rather than development pipeline stages (pre-planning, iterative, acceptance).

2. **No LLM budget control**: Current test runner treats all API calls equally, but only LLM calls cost money. Need granular control over LLM test execution.

3. **Unclear interface validation gate**: No clear separation between "UVisBox interface tests" and "LLM integration tests", making it unclear when interface changes block feature development.

## Design

### Directory Structure

```
tests/
├── unit/                              # 0 LLM calls
│   └── [existing unit tests]          # No changes to unit tests
│
├── uvisbox_interface/                 # 0 LLM calls, calls UVisBox
│   ├── test_tool_interfaces.py        # Tool → UVisBox interface validation
│   └── test_csv_loading.py            # CSV loading with real data
│
├── llm_integration/                   # LLM calls, tests specific features
│   ├── test_analyzer.py               # Analyzer with LLM
│   ├── test_error_handling.py         # Error recovery
│   ├── test_session.py                # Session management
│   ├── test_hybrid_control.py         # Fast command parsing
│   ├── test_routing.py                # Graph routing logic
│   └── [other LLM-dependent tests]
│
├── e2e/                               # LLM calls, complete workflows
│   ├── test_functional_boxplot.py     # --llm-subset=functional_boxplot
│   ├── test_curve_boxplot.py          # --llm-subset=curve_boxplot
│   ├── test_probabilistic_ms.py       # --llm-subset=probabilistic_ms
│   ├── test_uncertainty_lobes.py      # --llm-subset=uncertainty_lobes
│   ├── test_squid_glyph.py            # --llm-subset=squid_glyph
│   ├── test_contour_boxplot.py        # --llm-subset=contour_boxplot
│   ├── test_analysis_workflows.py     # --llm-subset=analysis
│   └── test_matplotlib_behavior.py    # Visualization behavior
│
├── conftest.py
├── __init__.py
└── test.py                            # New test runner (replaces utils/run_all_tests.py)
```

**Test Categories:**
- `unit/`: Pure logic, mocked dependencies, 0 LLM calls
- `uvisbox_interface/`: Real UVisBox calls, comprehensive interface testing, 0 LLM calls
- `llm_integration/`: Tests specific LLM-powered features (by scope)
- `e2e/`: Complete user workflows end-to-end (by scope)

### Test Runner Interface

**Pipeline-aware modes:**

```bash
# 1. Pre-planning: Verify UVisBox interface before planning features
python tests/test.py --pre-planning
# Runs: unit/ + uvisbox_interface/
# LLM calls: 0

# 2. Iterative development: Fast iteration during development
python tests/test.py --iterative --llm-subset=<subset>
# Runs: unit/ + specified LLM subset
# LLM calls: 5-15 typically
# Requires: Must specify --llm-subset (no default - forces intentional selection)

# 3. Code review: Checkpoint before moving to next task
python tests/test.py --code-review --llm-subset=<subset>
# Runs: unit/ + uvisbox_interface/ + specified LLM subset
# LLM calls: Depends on subset

# 4. Acceptance: Final validation before merge
python tests/test.py --acceptance
# Runs: Everything
# LLM calls: ~100
```

**LLM subset selection (composable, granular):**

```bash
# By component
--llm-subset=analyzer
--llm-subset=routing
--llm-subset=error_handling
--llm-subset=session
--llm-subset=hybrid_control

# By visualization type
--llm-subset=functional_boxplot
--llm-subset=curve_boxplot
--llm-subset=squid_glyph
# ... etc for each viz type

# By workflow
--llm-subset=analysis

# Special
--llm-subset=smoke              # Critical path only (~3 LLM calls)
                                # 1 basic viz workflow + 1 analyzer test

# Combine multiple subsets
--llm-subset=analyzer,routing
```

**Direct pytest passthrough:**

```bash
# Run specific file
python tests/test.py tests/llm_integration/test_analyzer.py

# Run specific test
python tests/test.py tests/e2e/test_functional_boxplot.py::test_basic_workflow
```

**Coverage reporting (matches test scope):**

```bash
python tests/test.py --pre-planning --coverage      # Coverage of unit + interface code
python tests/test.py --acceptance --coverage        # Coverage of all code
```

### Development Pipeline Changes

**1. Pre-planning gate:**
```bash
python tests/test.py --pre-planning
```
- Must pass before creating implementation plans for new features
- If fails: STOP feature planning
- Create patch version for interface updates only
- Resume feature planning after `--pre-planning` passes

**2. Iterative development:**
```bash
python tests/test.py --iterative --llm-subset=<relevant-subset>
```
- Run after each code change
- Choose subset based on feature area
- Examples:
  - Working on analyzer → `--llm-subset=analyzer`
  - Working on squid glyph → `--llm-subset=squid_glyph`
  - Working on graph routing → `--llm-subset=routing,smoke`

**3. Code review checkpoints:**
```bash
python tests/test.py --code-review --llm-subset=<relevant-subset>
```
- Before requesting code review or moving to next task
- Verifies: unit/ + uvisbox_interface/ + relevant LLM tests

**4. Acceptance stage:**
```bash
python tests/test.py --acceptance
```
- Final validation before merge
- Everything must pass
- Full LLM budget (~100 calls)

### Test File Migration

| Current Location | New Location | Changes |
|-----------------|--------------|---------|
| `tests/unit/*` | `tests/unit/*` | No change |
| `tests/integration/test_tool_interfaces.py` | `tests/uvisbox_interface/test_tool_interfaces.py` | Move only |
| `tests/integration/test_csv_loading.py` | `tests/uvisbox_interface/test_csv_loading.py` | Move only |
| `tests/integration/test_analyzer_tool.py` | `tests/llm_integration/test_analyzer.py` | Move + rename |
| `tests/integration/test_error_handling.py` | `tests/llm_integration/test_error_handling.py` | Move only |
| `tests/integration/test_hybrid_control.py` | `tests/llm_integration/test_hybrid_control.py` | Move only |
| `tests/integration/test_session_management.py` | `tests/llm_integration/test_session.py` | Move + rename |
| `tests/integration/test_e2e_pipelines.py` | Split into `tests/e2e/test_*_boxplot.py` etc | Split + rename |
| `tests/e2e/test_matplotlib_behavior.py` | `tests/e2e/test_matplotlib_behavior.py` | No change |
| `tests/e2e/test_analysis_workflows.py` | `tests/e2e/test_analysis_workflows.py` | No change |

**Files needing verification (check LLM usage first):**
- `tests/integration/test_error_recording.py` → If no LLM: `unit/`, if UVisBox: `uvisbox_interface/`
- `tests/integration/test_report_switching.py` → If no LLM: `unit/`, if UVisBox: `uvisbox_interface/`

**Files to delete:**
- `tests/utils/run_all_tests.py` (replaced by `tests/test.py`)
- `tests/interactive/interactive_test.py` (use `uva` main instead)
- `tests/interactive/` directory (remove entire directory)

### Implementation Details

**1. Pytest markers for test discovery:**

```python
# Smoke tests marked in individual test files
@pytest.mark.smoke
def test_basic_visualization_workflow(session):
    """Smoke test: Load data and create functional boxplot."""
    ...

# Module-level markers for subset selection
# tests/llm_integration/test_analyzer.py
pytestmark = pytest.mark.llm_subset_analyzer

# tests/e2e/test_functional_boxplot.py
pytestmark = pytest.mark.llm_subset_functional_boxplot
```

**2. test.py implementation approach:**
- Parse arguments to determine mode (--pre-planning, --iterative, etc.)
- Map mode → test directories/markers
- Build pytest command with appropriate markers/paths
- Support direct pytest passthrough for specific files/tests
- Handle coverage reporting based on scope
- Enforce `--llm-subset` requirement for `--iterative` mode

**3. Smoke test composition (critical path only):**
- 1 basic visualization workflow (load → functional boxplot)
- 1 analyzer test (most complex LLM feature)
- Total: ~3 LLM calls

### Documentation Updates

Files requiring updates:
1. `TESTING.md`: Complete rewrite with new structure and pipeline examples
2. `CONTRIBUTING.md`: Update test running instructions
3. `CLAUDE.md`: Update development pipeline section + fix unicode bug in workflow diagram
4. `README.md`: Update quick start test commands

**CLAUDE.md unicode fix:**
```
# Current (broken - has non-printable unicode characters)
START � model � [conditional routing]
         �         � data_tool � model

# Fixed (ASCII only)
START -> model -> [conditional routing]
              -> data_tool -> model
              -> vis_tool -> model
              -> statistics_tool -> model
              -> analyzer_tool -> model
              -> END
```

## Migration Checklist

1. Create new directory structure (`uvisbox_interface/`, `llm_integration/`, keep `e2e/`)
2. Verify LLM usage in `test_error_recording.py` and `test_report_switching.py`
3. Split `test_e2e_pipelines.py` into per-viz-type files
4. Move/rename files according to migration plan
5. Add pytest markers (`@pytest.mark.smoke`, `@pytest.mark.llm_subset_*`)
6. Implement `tests/test.py` with all modes and subset support
7. Delete old files (`run_all_tests.py`, `interactive/` directory)
8. Update all documentation (TESTING.md, CONTRIBUTING.md, CLAUDE.md, README.md)
9. Run `python tests/test.py --acceptance` to verify everything works
10. Update any CI/CD configurations if applicable

## Success Criteria

1. `python tests/test.py --pre-planning` runs 0 LLM calls
2. `python tests/test.py --iterative` without `--llm-subset` shows clear error message
3. `python tests/test.py --iterative --llm-subset=smoke` runs ~3 LLM calls
4. `python tests/test.py --acceptance` runs all tests (~100 LLM calls)
5. All documentation reflects new test structure
6. CLAUDE.md workflow diagram uses ASCII characters only
7. Can run specific tests via pytest passthrough
8. Coverage reporting works for all modes

## Rationale

**Why split by scope (llm_integration vs e2e)?**
- `llm_integration/`: Tests specific LLM-powered features in isolation
- `e2e/`: Tests complete user workflows end-to-end
- Allows granular subset selection during development

**Why require explicit --llm-subset for --iterative?**
- Forces intentional test selection
- Prevents accidental LLM budget burn
- Makes developers think about what they need to test

**Why comprehensive uvisbox_interface/ tests?**
- Catches UVisBox API changes before they block feature development
- Fast (0 LLM calls) so can be comprehensive
- Acts as gate: interface must be stable before planning features

**Why smoke tests use markers instead of hardcoded list?**
- Self-documenting in test files
- Can run with standard pytest (`pytest -m smoke`)
- Easy to update as critical paths change

**Why one file per visualization type in e2e/?**
- Maximum granular control over LLM test execution
- Example: Testing squid glyph doesn't require running functional boxplot tests
- Aligns with feature development (often work on one viz type at a time)
