# Testing Guide

## Quick Start

```bash
# Pre-planning: Verify UVisBox interface (0 LLM calls)
python tests/test.py --pre-planning

# Iterative development: Unit + specific LLM subset
python tests/test.py --iterative --llm-subset=routing

# Smoke test: Critical path only (~3 LLM calls)
python tests/test.py --iterative --llm-subset=smoke

# Code review checkpoint: Full interface + LLM subset
python tests/test.py --code-review --llm-subset=hybrid_control,routing

# Acceptance: All tests
python tests/test.py --acceptance

# Direct test selection (pytest-style)
python tests/test.py tests/unit/test_config.py
python tests/test.py tests/llm_integration/test_session.py::test_specific

# With coverage
python tests/test.py --pre-planning --coverage
```

---

## Test Structure

```
tests/
├── test.py                     # Pipeline-aware test runner
│
├── unit/                       # ~291 tests, 0 UVisBox calls
│   ├── test_command_parser.py      # Hybrid command parsing
│   ├── test_routing.py             # Graph routing logic
│   ├── test_tools.py               # Data/vis tool functions
│   └── [... other unit tests]
│
├── uvisbox_interface/          # 23 tests, 0 LLM calls, calls UVisBox
│   ├── test_tool_interfaces.py     # Tool → UVisBox interface validation
│   └── test_csv_loading.py         # CSV loading with real data
│
├── llm_integration/            # LLM-powered features
│   ├── test_error_handling.py      # Error recovery
│   ├── test_session.py             # Session management
│   └── test_hybrid_control.py      # Hybrid control workflows
│
├── e2e/                        # End-to-end visualization workflows
│   ├── test_functional_boxplot.py  # Functional boxplot workflows
│   ├── test_curve_boxplot.py       # Curve boxplot workflows
│   ├── test_contour_boxplot.py     # Contour boxplot workflows
│   ├── test_probabilistic_ms.py    # PMS workflows
│   ├── test_uncertainty_lobes.py   # Uncertainty lobes workflows
│   ├── test_squid_glyph.py         # Squid glyph workflows
│   └── test_matplotlib_behavior.py # Visualization behavior
│
├── conftest.py
└── __init__.py
```

### LLM Call Estimates

| Category | LLM Calls | Duration |
|----------|-----------|----------|
| **Unit** | 0 | < 5 seconds |
| **UVisBox Interface** | 0 | < 30 seconds |
| **LLM Integration** | small | 2-3 minutes |
| **E2E** | larger | 3-5 minutes |

**Note**: LLM call estimates are approximate and may vary by ±20%.

**Unit Test Independence**: All unit tests mock external dependencies (UVisBox, file I/O, LLM). They can run without UVisBox installed, making them ideal for fast iteration and CI environments.

---

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
# Working on routing
python tests/test.py --iterative --llm-subset=routing

# Working on squid glyph
python tests/test.py --iterative --llm-subset=squid_glyph

# Multiple subsets
python tests/test.py --iterative --llm-subset=hybrid_control,routing

# Smoke test only
python tests/test.py --iterative --llm-subset=smoke
```

**Run after**: Each code change

### 3. Code Review Checkpoints (Before Review)

**Purpose**: Verify implementation before requesting review.

```bash
python tests/test.py --code-review --llm-subset=hybrid_control
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

---

## LLM Subset Reference

### Component-Based Subsets

| Subset | Marker | Tests |
|--------|--------|-------|
| `error_handling` | `llm_subset_error_handling` | Error recovery |
| `session` | `llm_subset_session` | Session management |
| `hybrid_control` | `llm_subset_hybrid_control` | Hybrid control |

### Visualization Type Subsets

| Subset | Marker | Tests |
|--------|--------|-------|
| `functional_boxplot` | `llm_subset_functional_boxplot` | Functional boxplot |
| `curve_boxplot` | `llm_subset_curve_boxplot` | Curve boxplot |
| `contour_boxplot` | `llm_subset_contour_boxplot` | Contour boxplot |
| `probabilistic_ms` | `llm_subset_probabilistic_ms` | PMS |
| `uncertainty_lobes` | `llm_subset_uncertainty_lobes` | Uncertainty lobes |
| `squid_glyph` | `llm_subset_squid_glyph` | Squid glyph |

### Special Subsets

| Subset | Marker | Tests |
|--------|--------|-------|
| `smoke` | `smoke` | Critical path only |

**Combine subsets**: `--llm-subset=hybrid_control,routing,smoke`

---

## Test Roles

### Unit Tests (0 LLM Calls)
**Purpose**: Test individual functions and logic in isolation without external dependencies.

**Responsibilities**:
- Function logic correctness
- Parameter validation
- Error handling paths
- Edge cases (empty data, boundary values)
- Mock external dependencies (UVisBox, file I/O, LLM)

**When to add unit tests**:
- **New feature**: Write tests for all new functions before implementation (TDD)
- **Bug fix**: Add test reproducing the bug, verify it fails, then fix
- **Refactoring**: Maintain existing test coverage

**Example**:
```python
def test_generate_ensemble_curves_with_valid_params():
    """Test curve generation with valid parameters."""
    result = generate_ensemble_curves(n_curves=10, n_points=50)

    assert result['status'] == 'success'
    assert Path(result['data_path']).exists()
    data = np.load(result['data_path'])
    assert data.shape == (10, 50)
```

### UVisBox Interface Tests (0 LLM Calls, Calls UVisBox)
**Purpose**: Test tool → UVisBox integration without LLM involvement.

**Responsibilities**:
- Verify tools call UVisBox functions correctly
- Validate parameter passing to UVisBox
- Test with real UVisBox library
- Catch UVisBox API changes early
- Test error handling for UVisBox failures

**When to add interface tests**:
- **New UVisBox function**: Add test when wrapping new UVisBox visualization
- **UVisBox update**: Run after updating UVisBox dependency
- **Parameter changes**: Add test when modifying tool parameters

**Example**:
```python
def test_functional_boxplot_interface():
    """Test plot_functional_boxplot with real UVisBox."""
    result = plot_functional_boxplot(data_path="curves.npy")

    # Verify exact structure (catches API changes)
    assert result['status'] == 'success'
    assert '_vis_params' in result
    assert result['_vis_params']['_tool_name'] == 'plot_functional_boxplot'
```

### LLM Integration Tests
**Purpose**: Test specific LLM-powered features in isolation.

**Responsibilities**:
- Test routing decisions with LLM
- Test error recovery workflows
- Test session state management with LLM
- Test hybrid control mode

**When to add LLM integration tests**:
- **New LLM feature**: Add test for specific LLM-powered functionality
- **Routing change**: Add test when modifying graph routing logic
- **Error handling**: Add test when improving error recovery

**Example**:
```python
def test_session_basic(session):
    """Test basic session functionality."""
    session.send("Generate 30 curves and plot functional boxplot")

    stats = session.get_stats()
    assert stats["current_data"] is True
    assert stats["current_vis"] is True
```

### E2E Tests
**Purpose**: Test complete user scenarios from natural language input to final output.

**Responsibilities**:
- Full visualization pipelines
- Multi-turn conversations
- Matplotlib non-blocking behavior

**When to add E2E tests**:
- **New visualization type**: Add test for complete workflow
- **Before release**: Run full E2E suite to verify everything works

**Example**:
```python
def test_full_visualization_pipeline(session):
    """Test data → vis workflow."""
    session.send("Generate curves and plot boxplot")

    stats = session.get_stats()
    assert stats["current_vis"] is True
```

---

## Code Coverage

### Coverage Targets

```
Key modules:
- vis_tools.py
- data_tools.py
- command_parser.py
- routing.py
- state.py
- hybrid_control.py
```

**Run coverage report**:
```bash
# Generate coverage report
python tests/test.py --pre-planning --coverage

# View HTML report
open htmlcov/index.html
```

### Interpreting Coverage

**Coverage Percentage Meaning**:
- **90-100%**: Excellent - All paths tested including error handling
- **80-89%**: Good - Core functionality covered, some edge cases may be missing
- **70-79%**: Needs work - Missing error path tests
- **Below 70%**: Critical - Significant gaps, high risk of bugs

**What the numbers mean**:
```
Name                    Stmts   Miss  Cover
-------------------------------------------
tools/vis_tools.py        151      5  96.69%
```
- **Stmts**: Total lines of executable code (151)
- **Miss**: Lines not executed by tests (5)
- **Cover**: Percentage covered (96.69%)

**HTML Report Features**:
- **Green lines**: Covered by tests
- **Red lines**: Not covered (need tests)
- **Yellow lines**: Partially covered (branches not fully tested)
- Click files to see line-by-line coverage

**What's NOT covered** (by design):
- Interactive REPL in main.py (manual testing)
- Entry points __main__.py
- Debug code marked with `# pragma: no cover`

### Coverage Best Practices

**When adding new features**:
1. Write unit tests first (TDD)
2. Aim for 90%+ coverage on new code
3. Run `--pre-planning --coverage` to verify
4. Add mock-based tests for error paths

**When modifying existing code**:
1. Check current coverage: `python tests/test.py --pre-planning --coverage`
2. Add tests for new branches
3. Maintain or improve coverage percentage
4. Don't remove tests without replacement

**Finding coverage gaps**:
```bash
# Generate report
python tests/test.py --pre-planning --coverage

# Open HTML report
open htmlcov/index.html

# Look for red lines (uncovered code)
# Add tests for those lines
# Re-run to verify
```

**Mock-based testing for error paths**:
```python
from unittest.mock import patch

@patch('uvisbox_assistant.tools.vis_tools.functional_boxplot')
def test_uvisbox_exception(mock_uvisbox):
    """Test error handling when UVisBox raises exception."""
    mock_uvisbox.side_effect = RuntimeError("UVisBox error")

    result = plot_functional_boxplot("data.npy")

    assert result['status'] == 'error'
    assert '_error_details' in result
```

---

## Error Handling

### 429 Error (Resource Exhausted)

If you see this error:
```
ResourceExhausted: 429 You exceeded your current quota
Please retry in 17.461429122s
```

**Solution**: Wait the specified time (e.g., 17s) plus a buffer (60s total recommended).

**Prevention**:
- Use `python tests/test.py` with appropriate mode
- Run unit tests first (0 LLM calls)
- Use `--llm-subset` to limit LLM budget during iteration
- Add delay between heavy test runs

---

## Test Runner Usage

### Pipeline Modes

```bash
# Pre-planning: Unit + UVisBox interface (0 LLM calls)
python tests/test.py --pre-planning

# Iterative: Unit + LLM subset (requires --llm-subset)
python tests/test.py --iterative --llm-subset=routing

# Code review: Unit + UVisBox interface + LLM subset
python tests/test.py --code-review --llm-subset=hybrid_control

# Acceptance: All tests
python tests/test.py --acceptance
```

### Direct Test Selection

```bash
# Run specific test file
python tests/test.py tests/unit/test_config.py -v

# Run specific test
python tests/test.py tests/unit/test_config.py::test_temp_dir_exists -v

# Run specific test class
python tests/test.py tests/e2e/test_functional_boxplot.py::TestFunctionalBoxplotPipeline -v
```

### With Coverage

```bash
# Pre-planning with coverage (recommended)
python tests/test.py --pre-planning --coverage

# Acceptance with coverage
python tests/test.py --acceptance --coverage
```

### LLM Subset Selection

```bash
# Single subset
python tests/test.py --iterative --llm-subset=smoke

# Multiple subsets
python tests/test.py --iterative --llm-subset=hybrid_control,routing,smoke

# Component-based
python tests/test.py --code-review --llm-subset=session,error_handling

# Visualization-based
python tests/test.py --iterative --llm-subset=functional_boxplot,curve_boxplot
```

---

## Development Workflow

### During Active Development
1. **Run unit tests** after code changes (instant feedback):
   ```bash
   python tests/test.py tests/unit/
   ```

2. **Run subset tests** for feature being developed:
   ```bash
   python tests/test.py --iterative --llm-subset=routing
   ```

3. **Run coverage** to verify new code is tested:
   ```bash
   python tests/test.py --pre-planning --coverage
   ```

### Before Requesting Code Review
1. **Run code review checkpoint**:
   ```bash
   python tests/test.py --code-review --llm-subset=<relevant-subset>
   ```

2. **Verify coverage maintained**:
   ```bash
   python tests/test.py --pre-planning --coverage
   open htmlcov/index.html
   ```

### Before Merging
1. **Run full acceptance test**:
   ```bash
   python tests/test.py --acceptance
   ```

2. **Verify coverage meets targets**:
   - Overall: ≥80%
   - Tools modules: ≥90%

3. **Check HTML coverage report**:
   ```bash
   open htmlcov/index.html
   ```

---

## Troubleshooting

### ImportError: No module named 'uvisbox_assistant'
Run from project root:
```bash
cd /path/to/uvisbox-assistant
python tests/test.py --pre-planning
```

### Test Failures
1. Verify Ollama is running and the configured model is pulled
2. Verify conda environment `agent` is active
3. Verify UVisBox is installed
4. Run unit tests first to isolate issue
5. Check if UVisBox interface changed (run `--pre-planning`)

### Coverage Gaps
1. Generate HTML report: `python tests/test.py --pre-planning --coverage`
2. Open `htmlcov/index.html`
3. Find red lines (uncovered code)
4. Add tests for those lines
5. Re-run coverage to verify

### LLM Budget / Slow Tests
If LLM-backed tests are slow or unreliable:
1. Use smaller subsets: `--llm-subset=smoke`
2. Use `--iterative` during development (unit + minimal LLM)
3. Save `--acceptance` for final validation only

### v0.3.1 (2025-11-05)
- Added comprehensive integration tests for backward compatibility
- Layer 1: Tool interface tests (21 tests)
- Layer 2: E2E pipeline tests (15 tests)
- Current coverage: 89.29%
- Total: 345 tests (277 unit, 53 integration, 15 e2e)

### v0.3.0 (2025-01-29)
- Added analysis testing (46 tests)
- Statistics tools: 25 tests
- Analyzer tools: 21 tests
- E2E analysis workflows: 12 tests

### v2.0 (2025-01-29)
- Reorganized test structure
- Added 35+ unit tests
- Category-based test runner
- BoxplotStyleConfig testing
