# Testing Guide for UVisBox-Assistant

## Quick Start

```bash
# Quick sanity check (30 seconds, 1-2 API calls)
python tests/test_simple.py

# Run unit tests only (instant, 0 API calls)
python tests/utils/run_all_tests.py --unit

# Run all tests with automatic delays (~10 minutes)
python tests/utils/run_all_tests.py
```

## Test Structure (Phase 9 - v2.0)

UVisBox-Assistant uses a reorganized test structure with clear categories:

```
tests/
├── test_simple.py              # Quick sanity check
├── unit/                       # Unit tests (0 API calls, 77+ tests)
│   ├── test_command_parser.py       # 17 tests: Styling commands
│   ├── test_config.py               # 8 tests: Configuration
│   ├── test_routing.py              # Routing logic
│   ├── test_tools.py                # 10 tests: Data/vis tools
│   ├── test_statistics_tools.py     # 25 tests: Statistics (v0.3.0)
│   └── test_analyzer_tools.py       # 21 tests: Analyzer (v0.3.0)
├── integration/                # Integration tests (15-25 API calls)
│   ├── test_hybrid_control.py
│   ├── test_error_handling.py
│   └── test_session_management.py
├── e2e/                        # End-to-end tests (20-30 API calls)
│   ├── test_matplotlib_behavior.py
│   └── test_analysis_workflows.py   # 12 tests: Analysis workflows (v0.3.0)
├── interactive/                # Manual tests (user-paced)
│   └── interactive_test.py
└── utils/
    └── run_all_tests.py        # Test runner with categories
```

## Test Categories

### Unit Tests (0 API Calls)
**When to run**: After modifying individual functions
**Duration**: < 15 seconds
**API calls**: 0

**Run all unit tests**:
```bash
python tests/utils/run_all_tests.py --unit
```

**Individual unit tests**:
```bash
python tests/unit/test_command_parser.py       # 17 tests: BoxplotStyleConfig commands
python tests/unit/test_config.py               # 8 tests: Configuration
python tests/unit/test_routing.py              # Routing logic tests
python tests/unit/test_tools.py                # 10 tests: Data/vis tools
python tests/unit/test_statistics_tools.py     # 25 tests: Statistics analysis (v0.3.0)
python tests/unit/test_analyzer_tools.py       # 21 tests: Report generation (v0.3.0)
```

**What's tested**:
- All 16 BoxplotStyleConfig hybrid commands
- Parameter mapping and application
- Configuration defaults and validation
- Graph routing logic (includes statistics/analyzer routing)
- Direct tool function calls with styling parameters
- **Statistics computation** (v0.3.0): Median analysis, band characteristics, outlier detection
- **Analyzer tools** (v0.3.0): Report generation, prompt templates, validation

### Integration Tests (15-25 API Calls)
**When to run**: After modifying workflows or state management
**Duration**: 2-4 minutes per file
**API calls**: 15-25 per file

**Run all integration tests**:
```bash
python tests/utils/run_all_tests.py --integration
```

**Individual integration tests**:
```bash
python tests/integration/test_hybrid_control.py      # Fast parameter updates
python tests/integration/test_error_handling.py      # Error recovery
python tests/integration/test_session_management.py  # Session cleanup
```

⚠️ **Wait 60 seconds between runs** to respect rate limits

### End-to-End Tests (20-30 API Calls)
**When to run**: Before releases or major changes
**Duration**: 3-5 minutes per file
**API calls**: 20-30 per file

```bash
python tests/utils/run_all_tests.py --e2e
python tests/e2e/test_matplotlib_behavior.py
python tests/e2e/test_analysis_workflows.py     # Analysis workflows (v0.3.0)
```

**What's tested**:
- Complete matplotlib non-blocking behavior
- **Three analysis workflow patterns** (v0.3.0):
  1. Visualization only (existing)
  2. Text analysis only (new)
  3. Combined visualization + analysis (new)
- Multi-turn analysis conversations
- Report format validation (inline/quick/detailed)

### Interactive Tests (User-Paced)
**When to run**: For manual verification
**Duration**: User-controlled

```bash
python tests/interactive/interactive_test.py
```

Menu-driven testing with 24+ pre-defined scenarios.

## BoxplotStyleConfig Testing (v2.0)

### New Parameters Tested

All unit tests verify the new BoxplotStyleConfig interface:

**Median Styling** (3 parameters):
- `median_color` - Color of median curve
- `median_width` - Line width of median
- `median_alpha` - Transparency of median

**Outliers Styling** (3 parameters):
- `outliers_color` - Color of outlier curves
- `outliers_width` - Line width of outliers
- `outliers_alpha` - Transparency of outliers

**Hybrid Commands** (6 commands):
- `median color <color>`
- `median width <number>`
- `median alpha <number>`
- `outliers color <color>`
- `outliers width <number>`
- `outliers alpha <number>`

### Test Coverage Summary

| Component | Tests | API Calls | Category |
|-----------|-------|-----------|----------|
| Command Parser | 17 | 0 | Unit |
| Configuration | 8 | 0 | Unit |
| Routing Logic | ~10 | 0 | Unit |
| Tool Functions | 10 | 0 | Unit |
| **Statistics Tools (v0.3.0)** | **25** | **0** | **Unit** |
| **Analyzer Tools (v0.3.0)** | **21** | **0** | **Unit** |
| **Total Unit** | **77+** | **0** | **Unit** |
| Hybrid Control | ~10 | 15-20 | Integration |
| Error Handling | ~8 | 10-15 | Integration |
| Session Management | ~6 | 5-10 | Integration |
| Matplotlib | ~5 | 0 | E2E |
| **Analysis Workflows (v0.3.0)** | **12** | **~20** | **E2E** |

## Analysis Testing (v0.3.0)

### Overview

The v0.3.0 release adds comprehensive testing for uncertainty analysis features:
- **46 analysis-specific tests**: 25 statistics + 21 analyzer
- **12 E2E workflow tests**: Three workflow patterns
- **77+ total unit tests** (0 API calls)
- **All statistics logic testable without LLM calls**

### Statistics Tool Tests (25 tests, 0 API calls)

**`tests/unit/test_statistics_tools.py`**

**Registry and Schema Tests** (6 tests):
- Tool registry structure
- Schema validation for LLM binding
- Required sequence documentation

**Median Analysis Tests** (5 tests):
- Trend detection (increasing/decreasing/stationary)
- Slope calculation
- Fluctuation and smoothness metrics
- Value range analysis

**Band Analysis Tests** (4 tests):
- Band width computation (mean/max/min/std)
- Widest region detection
- Uncertainty score calculation

**Outlier Analysis Tests** (4 tests):
- Outlier count and percentage
- Similarity to median (Pearson correlation)
- Intra-outlier clustering

**Integration Tests** (6 tests):
- Full end-to-end statistics computation
- UVisBox API integration (`functional_boxplot_summary_statistics`)
- Error handling for missing files and invalid data shapes

**Key Insight**: All statistics computation testable with 0 API calls due to separation of concerns (statistics vs. report generation).

### Analyzer Tool Tests (21 tests, 0 API calls)

**`tests/unit/test_analyzer_tools.py`**

**Registry and Schema Tests** (4 tests):
- Tool registry structure
- Schema validation
- Sequential workflow documentation
- No required parameters (state injection pattern)

**Prompt Template Tests** (7 tests):
- Three prompt templates exist (inline/quick/detailed)
- Prompt selection logic
- Statistics JSON formatting in prompts
- Invalid analysis type error handling

**Validation Tests** (6 tests):
- Processed statistics structure validation
- Missing top-level keys detection
- Incomplete data_shape/median/bands/outliers detection

**Error Handling Tests** (4 tests):
- Invalid analysis_type error
- Invalid summary structure error
- Word count validation

**Note**: These tests don't invoke the LLM. Report generation tests are in E2E suite.

### E2E Analysis Workflow Tests (12 tests, ~20 API calls)

**`tests/e2e/test_analysis_workflows.py`**

**Three Workflow Patterns** (6 tests):
1. **Visualization Only** (existing):
   - Test data → vis workflow without analysis
   - Verify no statistics/reports in state

2. **Text Analysis Only** (new):
   - Test data → statistics → analyzer workflow
   - Verify report generation
   - Validate inline/quick/detailed formats

3. **Combined Visualization + Analysis** (new):
   - Test data → vis → statistics → analyzer
   - Verify both visual and text output

**Multi-Turn Analysis** (3 tests):
- Incremental analysis (step-by-step)
- Report refinement (quick → detailed)
- Analysis-first, visualization-second

**Report Format Validation** (3 tests):
- Inline: 1 sentence, ~15-30 words
- Quick: 3-5 sentences, ~50-100 words
- Detailed: Structured sections, ~100-300 words

### Analysis Test Strategy

**Unit Tests (0 API calls)**:
- All statistics computation logic
- All analyzer validation and schema logic
- Prompt template selection
- Error handling

**Integration Tests** (if needed):
- Real UVisBox calls with statistics computation
- State injection pattern verification

**E2E Tests** (~2-3 API calls per test):
- Complete analysis workflows
- Real LLM report generation
- Multi-turn conversations
- Format validation

### Running Analysis Tests

**Unit tests only** (instant, 0 API calls):
```bash
# All unit tests including analysis
python tests/utils/run_all_tests.py --unit

# Statistics tests only
python tests/unit/test_statistics_tools.py

# Analyzer tests only
python tests/unit/test_analyzer_tools.py
```

**E2E analysis workflows** (~20 API calls, 2-3 minutes):
```bash
# All E2E tests including analysis
python tests/utils/run_all_tests.py --e2e

# Analysis workflows only
python tests/e2e/test_analysis_workflows.py
```

### Outlier Detection Testing

**Important**: Tests verify that outlier detection uses depth-based fencing (Q1 - 1.5×IQR), NOT percentile position.

**Test Scenarios**:
- **Similar curves** (100 curves): IQR small → low fence → 0 outliers (correct)
- **Heterogeneous curves**: IQR large → high fence → multiple outliers detected
- **Edge cases**: Empty data, single curve, all identical curves

See [ANALYSIS_EXAMPLES.md](docs/ANALYSIS_EXAMPLES.md#understanding-outlier-detection) for detailed explanation.

---

## Code Coverage

### Overview

UVisBox-Assistant maintains comprehensive code coverage with specific targets for critical modules:

**Coverage Targets**:
- **Overall codebase**: 80% minimum
- **Tools modules** (data_tools, vis_tools, statistics_tools, analyzer_tools): **90% minimum**

**Current Coverage** (as of v0.3.1):
- `data_tools.py`: 92.47% ✅
- `vis_tools.py`: 96.69% ✅
- `statistics_tools.py`: 92.92% ✅
- `analyzer_tools.py`: 70.91% (LLM code excluded from unit tests)
- **Overall tools**: 91.40% ✅

### Running Tests with Coverage

**Quick Start**:
```bash
# Run unit tests with coverage (instant, 0 API calls)
python tests/utils/run_all_tests.py --unit --coverage

# Run all tests with coverage (~10 minutes)
python tests/utils/run_all_tests.py --coverage
```

**Coverage Commands**:
```bash
# Unit tests with coverage (recommended for development)
python tests/utils/run_all_tests.py --unit --coverage

# Integration tests with coverage
python tests/utils/run_all_tests.py --integration --coverage

# E2E tests with coverage
python tests/utils/run_all_tests.py --e2e --coverage

# All tests with coverage
python tests/utils/run_all_tests.py --coverage
```

**Direct pytest usage**:
```bash
# Run specific test file with coverage
pytest tests/unit/test_tools.py --cov=src/uvisbox_assistant --cov-report=html

# Run entire unit suite with coverage
pytest tests/unit/ --cov=src/uvisbox_assistant --cov-report=term --cov-report=html
```

### Understanding Coverage Reports

**Terminal Output**:
After running tests with `--coverage`, you'll see:
```
Name                                           Stmts   Miss  Cover
------------------------------------------------------------------
src/uvisbox_assistant/tools/data_tools.py        73      5  93.15%
src/uvisbox_assistant/tools/vis_tools.py        149      5  96.64%
src/uvisbox_assistant/tools/statistics_tools.py  113     8  92.92%
------------------------------------------------------------------
TOTAL                                           2023    174  91.40%
```

**HTML Coverage Report**:
```bash
# Open HTML report in browser
open htmlcov/index.html

# Or manually navigate to:
# file:///path/to/uvisbox-assistant/htmlcov/index.html
```

**HTML Report Features**:
- **Green lines**: Covered by tests
- **Red lines**: Not covered (need tests)
- **Yellow lines**: Partially covered (branches not fully tested)
- **Click files**: See line-by-line coverage details
- **Coverage percentage**: Per-file and overall metrics

### Coverage Configuration

Coverage is configured in `.coveragerc`:

```ini
[run]
source = src/uvisbox_assistant
omit =
    */tests/*
    */test_*
    */__pycache__/*
    */site-packages/*
    */__init__.py
    */main.py
    */__main__.py

[report]
show_missing = True
precision = 2
exclude_lines =
    pragma: no cover
    def __repr__
    if self\.debug
    raise AssertionError
    raise NotImplementedError
    if 0:
    if False:
    if __name__ == .__main__.:
    @(abc\.)?abstractmethod
```

**Key Configuration Points**:
- **Omit**: Entry points, `__init__.py`, and test files excluded
- **Exclude lines**: Defensive code and debug statements marked with `# pragma: no cover`
- **Precision**: 2 decimal places (92.47% vs 92%)
- **Show missing**: Terminal output shows line numbers of uncovered code

### Mock-Based Testing Strategy

To reach 90%+ coverage, especially for error handling paths, we use **mock-based testing**:

**Why Mocking?**
- Trigger exception handlers without real errors
- Test error paths (file not found, invalid data, UVisBox exceptions)
- Test edge cases (disk full, permission denied, malformed data)
- 0 API calls, instant execution

**Example: Testing Error Handlers**
```python
from unittest.mock import patch

@patch('uvisbox_assistant.tools.vis_tools.functional_boxplot')
def test_plot_functional_boxplot_uvisbox_exception(mock_uvisbox, tmp_path):
    """Test functional boxplot with UVisBox exception to trigger error handler."""
    # Create valid data
    data = tmp_path / "data.npy"
    np.save(data, np.random.randn(10, 50))

    # Force UVisBox to raise exception
    mock_uvisbox.side_effect = RuntimeError("UVisBox internal error")

    # Call function - should catch exception and return error dict
    result = plot_functional_boxplot(str(data))

    # Verify error handling
    assert result['status'] == 'error'
    assert '_error_details' in result
```

**Example: Testing File System Errors**
```python
@patch('numpy.save')
def test_generate_ensemble_curves_save_exception(mock_save):
    """Test generate_ensemble_curves with save exception."""
    # Force np.save to fail (simulates disk full)
    mock_save.side_effect = OSError("Disk full")

    # Call function - should catch exception
    result = generate_ensemble_curves(n_curves=5, n_points=20)

    # Verify error handling
    assert result['status'] == 'error'
    assert '_error_details' in result
```

**Coverage Impact**:
- Without mocks: ~60-70% coverage (only happy paths tested)
- With mocks: 90%+ coverage (error paths and edge cases covered)

### Coverage Maintenance Guidelines

**When Adding New Features**:
1. Write unit tests FIRST (test-driven development)
2. Aim for 90%+ coverage on new code
3. Run `--unit --coverage` to verify
4. Add mock-based tests for error paths

**When Modifying Existing Code**:
1. Run coverage to see current state
2. Add tests for any new branches
3. Maintain or improve coverage percentage
4. Don't remove tests without replacement

**Coverage Best Practices**:
- **Unit tests with 0 API calls**: Primary coverage source
- **Mock external dependencies**: UVisBox, file I/O, LLM calls
- **Test error paths**: File not found, invalid data, exceptions
- **Test edge cases**: Empty data, single element, boundary values
- **Don't test LLM output**: analyzer_tools.py excludes LLM code from coverage

**Reviewing Coverage Gaps**:
```bash
# Generate HTML report
python tests/utils/run_all_tests.py --unit --coverage

# Open in browser
open htmlcov/index.html

# Look for red lines (uncovered code)
# Add tests for those lines
# Re-run coverage to verify
```

**Coverage Anti-Patterns** (Avoid These):
- ❌ Don't write tests just to hit coverage numbers (write meaningful tests)
- ❌ Don't use `# pragma: no cover` to hide untested code (add tests instead)
- ❌ Don't test implementation details (test behavior and interfaces)
- ❌ Don't skip error path testing (critical for robustness)

### Coverage Integration in CI/CD

**Recommended CI/CD workflow**:
```yaml
# Run on every commit
- name: Unit tests with coverage
  run: |
    python tests/utils/run_all_tests.py --unit --coverage

# Generate coverage badge
- name: Coverage badge
  run: |
    coverage-badge -o coverage.svg -f

# Fail if coverage drops below threshold
- name: Coverage check
  run: |
    coverage report --fail-under=80
```

**Local Pre-Commit Check**:
```bash
# Before committing, verify coverage
python tests/utils/run_all_tests.py --unit --coverage

# Check if you've maintained coverage
# If coverage dropped, add tests before committing
```

### Interpreting Coverage Results

**90%+ Coverage** (Excellent):
- All happy paths covered
- Most error paths tested
- Edge cases handled
- Mock-based exception testing

**80-90% Coverage** (Good):
- Core functionality covered
- Some error paths untested
- Add mock-based tests for gaps

**70-80% Coverage** (Needs Work):
- Basic paths covered
- Missing error handling tests
- Review HTML report for gaps

**Below 70% Coverage** (Critical):
- Significant gaps in testing
- High risk of undetected bugs
- Add comprehensive tests immediately

**What's NOT Covered** (By Design):
- LLM calls in `analyzer_tools.py` (tested in E2E)
- Interactive REPL code in `main.py` (excluded)
- Entry points `__main__.py` (excluded)
- Debug-only code marked with `# pragma: no cover`

---

## Gemini API Rate Limits (Free Tier)

**Important**: The free tier has strict rate limits:
- **30 requests per minute** (using gemini-2.0-flash-lite)
- Daily quota limits also apply

Each graph execution can make **2-6 API calls** depending on the workflow:
- Simple request: 2-3 calls (user → model → response)
- Data generation: 3-4 calls (user → model → data tool → model → response)
- Data + visualization: 4-6 calls (user → model → data → model → viz → model → response)

## Test Runner Usage

### Basic Usage

```bash
# All tests (respects rate limits automatically)
python tests/utils/run_all_tests.py

# Unit tests only (instant, 0 API calls)
python tests/utils/run_all_tests.py --unit

# Quick validation (unit + sanity check)
python tests/utils/run_all_tests.py --quick

# Integration tests only
python tests/utils/run_all_tests.py --integration

# E2E tests only
python tests/utils/run_all_tests.py --e2e
```

### Rate Limit Management

The test runner automatically:
- Adds appropriate delays between test files
- Groups tests by API usage
- Shows progress and timing

**Manual delays**:
- Unit tests: 0s delay (no API calls)
- Integration tests: 5s delay between files
- E2E tests: 5s delay between files
- Full suite: 3s delay between files

## Development Workflow Recommendations

### During Active Development
1. **Run unit tests** after code changes (instant feedback)
   ```bash
   python tests/utils/run_all_tests.py --unit
   ```

2. **Run quick sanity check** before committing
   ```bash
   python tests/test_simple.py
   ```

3. **Wait 60s** before running API-heavy tests again

### Before Committing
1. **Run full test suite** with automatic delays
   ```bash
   python tests/utils/run_all_tests.py
   ```

2. **Review test output** for any failures

3. **Fix issues** and re-run failed tests only

### Debugging Specific Issues
1. **Use Python REPL** for single requests:
   ```python
   from uvisbox_assistant.graph import create_graph
   graph = create_graph()
   result = graph.invoke({
       "messages": [{"role": "user", "content": "your query here"}]
   })
   print(result)
   ```

2. **Run specific test files** for targeted debugging:
   ```bash
   python tests/unit/test_command_parser.py
   python tests/integration/test_hybrid_control.py
   ```

## Rate Limit Exceeded Error

If you see this error:
```
ResourceExhausted: 429 You exceeded your current quota
Please retry in 17.461429122s
```

**Solution**: Wait 60 seconds and try again.

The error message tells you exactly how long to wait (e.g., "retry in 17s"). Wait that long plus a buffer.

## CI/CD Recommendations

```yaml
# Fast feedback loop (on every commit)
- Unit tests (< 15s, 0 API calls)
- test_simple.py (30s, 1-2 API calls)

# Pull request validation
- Unit tests
- Integration tests (with rate limiting)
- test_simple.py

# Pre-release validation
- All tests (unit + integration + e2e)
```

## Tips for Minimizing API Usage

1. **Use smaller datasets**: "Generate 5 curves" instead of "Generate 100 curves"
2. **Test data tools separately**: They don't call the API (just generate local data)
3. **Run unit tests first**: 0 API calls, instant feedback
4. **Use test runner categories**: `--unit`, `--integration`, `--e2e`
5. **Wait 60s between heavy test runs**

## Estimating API Usage

**Rule of thumb**:
- Each test function ≈ 2-6 API calls
- Stay under 12-13 test functions per minute (to account for retries)
- Add 60s delay after every ~10-12 API calls

**API Call Estimates**:
- `test_simple.py`: 1-2 calls
- `test_hybrid_control.py`: 15-20 calls
- `test_error_handling.py`: 10-15 calls
- `test_session_management.py`: 5-10 calls
- Full integration suite: ~40-50 calls (with delays, ~10 minutes)

## Migration from Old Tests

### ❌ Deleted (Obsolete Phase Tests)
These test files have been removed:
- `test_phase1.py`
- `test_phase2.py`
- `test_graph.py`
- `test_graph_quick.py`
- `test_graph_integration.py`
- `test_happy_path.py`
- `test_multiturn.py`
- `simple_test.py` (replaced by `test_simple.py`)
- `run_tests_with_delays.py` (replaced by `utils/run_all_tests.py`)

### ✅ Migrated to New Structure
Old tests have been reorganized:
- `test_routing.py` → `unit/test_routing.py`
- `test_hybrid_control.py` → `integration/test_hybrid_control.py`
- `test_error_handling.py` → `integration/test_error_handling.py`
- `test_session_management.py` → `integration/test_session_management.py`
- `test_matplotlib_behavior.py` → `e2e/test_matplotlib_behavior.py`
- `interactive_test.py` → `interactive/interactive_test.py`

### 🆕 New Tests (v2.0)
- `test_simple.py` - Quick sanity check
- `unit/test_command_parser.py` - BoxplotStyleConfig commands (17 tests)
- `unit/test_config.py` - Configuration validation (8 tests)
- `unit/test_tools.py` - Direct tool testing (10 tests)
- `utils/run_all_tests.py` - Category-based test runner

## Troubleshooting

### ImportError: No module named 'uvisbox_assistant'
Make sure you're running from the project root:
```bash
cd /path/to/uvisbox_assistant
python tests/test_simple.py
```

### Rate Limit Errors
If you hit rate limits:
1. Wait 60 seconds
2. Use `--unit` flag for instant tests: `python tests/utils/run_all_tests.py --unit`
3. Run tests in smaller batches

### Test Failures
1. Check that `GEMINI_API_KEY` is set in system environment
2. Verify conda environment `agent` is active with UVisBox installed
3. Check `test_data/` directory has sample files
4. Run unit tests first to verify basic functionality

## Future Improvements

Planned features to reduce API usage:
- Mock model mode for testing
- Response caching for identical queries
- Paid tier upgrade guide (higher limits)
- Local LLM option for development

## Documentation

- **Test Structure**: See `tests/README.md` for detailed test organization
- **Architecture**: See `CLAUDE.md` for system architecture
- **Implementation**: See `plans/` for phase-by-phase guides
- **BoxplotStyleConfig**: See updated plans for v2.0 interface details

## Version History

### v0.3.1 (2025-11-05) - Coverage Infrastructure
- Added comprehensive code coverage reporting with pytest-cov
- Created `.coveragerc` configuration file
- Updated test runner with `--coverage` flag
- Added 26 new unit tests for tools modules (28 total new tests)
- Achieved 90%+ coverage targets:
  - data_tools.py: 61.64% → 92.47% (+30.83%)
  - vis_tools.py: 72.85% → 96.69% (+23.84%)
  - statistics_tools.py: 76.11% → 92.92% (+16.81%)
  - Overall tools modules: 91.40% ✅
- Implemented mock-based testing strategy for error paths
- Fixed 2 failing tests in test_statistics_tools.py (mock import paths)
- Fixed vector field test parameter names
- Added comprehensive coverage documentation in TESTING.md
- Total: 166 unit tests, all 0 API calls

### v2.0 (2025-01-29) - Phase 9 Complete
- Reorganized test structure: unit/, integration/, e2e/, interactive/
- Added 35+ unit tests (17 command parser, 8 config, 10 tools)
- Full BoxplotStyleConfig testing coverage
- Category-based test runner
- Deleted 1444+ lines of obsolete phase tests

### v1.0 (2025-01-26) - Initial Test Suite
- Phase-based test organization
- 17 test files, ~2600 lines
- Basic coverage of all components
