# Testing Guide for ChatUVisBox

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

ChatUVisBox uses a reorganized test structure with clear categories:

```
tests/
├── test_simple.py              # Quick sanity check
├── unit/                       # Unit tests (0 API calls)
│   ├── test_command_parser.py  # 17 tests
│   ├── test_config.py          # 8 tests
│   ├── test_routing.py         # Routing logic
│   └── test_tools.py           # 10 tests
├── integration/                # Integration tests (15-25 API calls)
│   ├── test_hybrid_control.py
│   ├── test_error_handling.py
│   └── test_session_management.py
├── e2e/                        # End-to-end tests (20-30 API calls)
│   └── test_matplotlib_behavior.py
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
python tests/unit/test_command_parser.py  # 17 tests for BoxplotStyleConfig commands
python tests/unit/test_config.py          # 8 tests for configuration
python tests/unit/test_routing.py         # Routing logic tests
python tests/unit/test_tools.py           # 10 tests for data/vis tools
```

**What's tested**:
- All 13 BoxplotStyleConfig hybrid commands
- Parameter mapping and application
- Configuration defaults and validation
- Graph routing logic
- Direct tool function calls with styling parameters

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
```

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
| **Total Unit** | **45+** | **0** | **Unit** |
| Hybrid Control | ~10 | 15-20 | Integration |
| Error Handling | ~8 | 10-15 | Integration |
| Session Management | ~6 | 5-10 | Integration |
| Matplotlib | ~5 | 0 | E2E |

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
   from chatuvisbox.graph import create_graph
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

### ImportError: No module named 'chatuvisbox'
Make sure you're running from the project root:
```bash
cd /path/to/chatuvisbox
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
