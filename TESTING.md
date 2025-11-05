# Testing Guide

## Quick Start

```bash
# Run all tests with automatic delays (~10 minutes, ~100 API calls)
python tests/utils/run_all_tests.py

# Run unit tests only (instant, 0 API calls)
python tests/utils/run_all_tests.py --unit

# Quick sanity check (30 seconds, 1-2 API calls)
python tests/test_simple.py

# Run with coverage report
python tests/utils/run_all_tests.py --unit --coverage
```

---

## Test Structure

```
tests/
├── test_simple.py              # Quick sanity check (1-2 API calls)
│
├── unit/                       # 277 tests, 0 API calls
│   ├── test_command_parser.py      # Hybrid command parsing
│   ├── test_command_handlers.py    # Command handler logic
│   ├── test_config.py              # Configuration validation
│   ├── test_routing.py             # Graph routing logic
│   ├── test_state_extensions.py    # State management
│   ├── test_tools.py               # Data/vis tool functions
│   ├── test_statistics_tools.py    # Statistics computation
│   ├── test_analyzer_tools.py      # Report generation
│   ├── test_error_tracking.py      # Error tracking system
│   ├── test_error_interpretation.py # Error message interpretation
│   └── test_output_control.py      # Verbose mode control
│
├── integration/                # 53 tests, ~100 API calls
│   ├── test_tool_interfaces.py     # Layer 1: Tool-to-UVisBox interface (21 tests)
│   ├── test_e2e_pipelines.py       # Layer 2: Complete user workflows (15 tests)
│   ├── test_analyzer_tool.py       # Analyzer with LLM (3 tests)
│   ├── test_hybrid_control.py      # Fast parameter updates (4 tests)
│   ├── test_error_handling.py      # Error recovery (6 tests)
│   └── test_session_management.py  # Session lifecycle (3 tests)
│
├── e2e/                        # 15 tests, ~30 API calls
│   ├── test_matplotlib_behavior.py # Non-blocking visualization (3 tests)
│   └── test_analysis_workflows.py  # Analysis pipelines (12 tests)
│
├── interactive/                # Manual testing
│   └── interactive_test.py         # Menu-driven testing (24+ scenarios)
│
└── utils/
    └── run_all_tests.py        # Test runner with categories
```

### API Call Estimates

| Category | Tests | API Calls | Duration |
|----------|-------|-----------|----------|
| **Unit** | 277 | 0 | < 10 seconds |
| **Integration** | 53 | ~100 | 3-5 minutes |
| **E2E** | 15 | ~30 | 2-3 minutes |
| **Total** | 345 | ~130 | 8-10 minutes |

**Note**: API call estimates are approximate. Actual usage depends on model behavior and may vary by ±20%.

---

## Test Roles

### Unit Tests (0 API Calls)
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

### Integration Tests (~2-3 API Calls per Test)
**Purpose**: Test interactions between components and with external dependencies (UVisBox, LLM).

**Responsibilities**:
- Tool-to-UVisBox interface correctness
- Complete user workflows (data → vis → analysis)
- Multi-turn conversations
- Session state management
- Error recovery across components

**Two-layer structure**:
- **Layer 1** (`test_tool_interfaces.py`): Direct tool functions with real UVisBox
  - Catches UVisBox API changes (e.g., KEY_NOT_FOUND bugs)
  - Verifies exact return structures
- **Layer 2** (`test_e2e_pipelines.py`): Complete workflows through model
  - Verifies backward compatibility for users
  - Tests all 6 visualization types
  - Tests full analyzer pipeline

**When to add integration tests**:
- **New workflow**: Add E2E test for complete user journey
- **New UVisBox module**: Add Layer 1 interface test
- **API change**: Update Layer 1 tests to match new interface
- **Breaking change detection**: Layer 1 fails → update tools → Layer 2 passes = backward compatible

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

### E2E Tests (~2-3 API Calls per Test)
**Purpose**: Test complete user scenarios from natural language input to final output.

**Responsibilities**:
- Complete analysis workflows
- Real LLM report generation
- Matplotlib non-blocking behavior
- Multi-turn analysis conversations
- Report format validation (inline/quick/detailed)

**When to add E2E tests**:
- **New feature**: Add test for complete user-facing workflow
- **New analysis type**: Add test for new report format
- **Before release**: Run full E2E suite to verify everything works

**Example**:
```python
def test_full_analyzer_pipeline():
    """Test data → vis → analyze workflow."""
    session = ConversationSession()
    session.send("Generate curves, plot boxplot, detailed report")

    response = session.get_last_response()
    assert len(response) > 100  # Substantial report
    assert "median" in response.lower()
    assert "outlier" in response.lower()
```

### Interactive Tests (Manual)
**Purpose**: Menu-driven manual testing for exploratory verification.

**Responsibilities**:
- Visual verification of plots
- User experience testing
- Edge case exploration
- Debugging specific scenarios

**When to use**:
- Visual verification needed
- Testing new UI features
- Debugging specific user reports
- Pre-release exploratory testing

---

## Code Coverage

### Current Coverage (v0.3.1)

```
Overall: 89.29%

Key modules:
- vis_tools.py:        96.69% ✅
- statistics_tools.py: 92.92% ✅
- data_tools.py:       92.47% ✅
- command_parser.py:   94.44% ✅
- routing.py:         100.00% ✅
- state.py:           100.00% ✅
- hybrid_control.py:  100.00% ✅
```

**Run coverage report**:
```bash
# Generate coverage report
python tests/utils/run_all_tests.py --unit --coverage

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
- LLM calls in analyzer_tools.py (tested in E2E)
- Interactive REPL in main.py (manual testing)
- Entry points __main__.py
- Debug code marked with `# pragma: no cover`

### Coverage Best Practices

**When adding new features**:
1. Write unit tests first (TDD)
2. Aim for 90%+ coverage on new code
3. Run `--unit --coverage` to verify
4. Add mock-based tests for error paths

**When modifying existing code**:
1. Check current coverage: `python tests/utils/run_all_tests.py --unit --coverage`
2. Add tests for new branches
3. Maintain or improve coverage percentage
4. Don't remove tests without replacement

**Finding coverage gaps**:
```bash
# Generate report
python tests/utils/run_all_tests.py --unit --coverage

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
- Use `python tests/utils/run_all_tests.py` (automatic delays)
- Run unit tests first (0 API calls)
- Add 60s delay between heavy test runs

---

## Test Runner Usage

### Categories

```bash
# All tests (automatic delays)
python tests/utils/run_all_tests.py

# Unit tests only (instant)
python tests/utils/run_all_tests.py --unit

# Integration tests only
python tests/utils/run_all_tests.py --integration

# E2E tests only
python tests/utils/run_all_tests.py --e2e

# Quick validation (unit + sanity check)
python tests/utils/run_all_tests.py --quick
```

### With Coverage

```bash
# Unit tests with coverage (recommended)
python tests/utils/run_all_tests.py --unit --coverage

# All tests with coverage
python tests/utils/run_all_tests.py --coverage

# Integration tests with coverage
python tests/utils/run_all_tests.py --integration --coverage
```

### Individual Test Files

```bash
# Unit tests
python -m pytest tests/unit/test_tools.py -v
python tests/unit/test_statistics_tools.py

# Integration tests
python -m pytest tests/integration/test_tool_interfaces.py -v
python tests/integration/test_e2e_pipelines.py

# E2E tests
python tests/e2e/test_analysis_workflows.py
```

---

## Development Workflow

### During Active Development
1. **Run unit tests** after code changes (instant feedback):
   ```bash
   python tests/utils/run_all_tests.py --unit
   ```

2. **Run coverage** to verify new code is tested:
   ```bash
   python tests/utils/run_all_tests.py --unit --coverage
   ```

### Before Committing
1. **Run quick sanity check**:
   ```bash
   python tests/test_simple.py
   ```

2. **Run full test suite** (if time permits):
   ```bash
   python tests/utils/run_all_tests.py
   ```

### Before Release
1. **Run all tests with coverage**:
   ```bash
   python tests/utils/run_all_tests.py --coverage
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
python tests/test_simple.py
```

### Test Failures
1. Verify `GEMINI_API_KEY` is set
2. Verify conda environment `agent` is active
3. Verify UVisBox is installed
4. Run unit tests first to isolate issue

### Coverage Gaps
1. Generate HTML report: `python tests/utils/run_all_tests.py --unit --coverage`
2. Open `htmlcov/index.html`
3. Find red lines (uncovered code)
4. Add tests for those lines
5. Re-run coverage to verify

---

## Version History

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
