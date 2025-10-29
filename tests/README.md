# ChatUVisBox Test Suite

## Quick Start

```bash
# Quick sanity check (30 seconds, 1-2 API calls)
python tests/test_simple.py

# Run unit tests only (fast, 0 API calls)
python tests/utils/run_all_tests.py --unit

# Run all tests with automatic delays (~10 minutes)
python tests/utils/run_all_tests.py

# Run specific test category
python tests/utils/run_all_tests.py --integration  # 3-4 minutes
python tests/utils/run_all_tests.py --e2e          # 4-5 minutes
```

## Test Structure

### Unit Tests (`tests/unit/`)
**Purpose**: Test individual functions and components in isolation
**API Calls**: 0 (no LLM calls)
**Duration**: < 10 seconds
**When to run**: After modifying individual functions

**Files**:
- `test_command_parser.py` - Test hybrid control command parsing (17 tests)
  - All 13 BoxplotStyleConfig commands
  - Parameter mapping and application
- `test_config.py` - Test configuration loading (8 tests)
  - BoxplotStyleConfig defaults
  - API key configuration
  - Path validation
- `test_routing.py` - Test routing logic
  - Graph routing decisions
  - Tool type detection

### Integration Tests (`tests/integration/`)
**Purpose**: Test component interactions (LangGraph, ConversationSession)
**API Calls**: 15-25 per file
**Duration**: 2-4 minutes per file
**When to run**: After modifying workflows or state management

**Files** (existing, to be moved):
- `test_hybrid_control.py` - Fast parameter updates
- `test_error_handling.py` - Error recovery and circuit breaker
- `test_session_management.py` - Session cleanup and stats

### End-to-End Tests (`tests/e2e/`)
**Purpose**: Test complete user workflows
**API Calls**: 20-30 per file
**Duration**: 3-5 minutes per file
**When to run**: Before releases or major changes

**Files** (existing):
- `test_matplotlib_behavior.py` - Matplotlib non-blocking behavior

### Interactive Tests (`tests/interactive/`)
**Purpose**: Manual testing and exploration
**API Calls**: User-paced
**Duration**: User-controlled
**When to run**: For manual verification

**Files**:
- `interactive_test.py` - Menu-driven testing with 24+ scenarios

## BoxplotStyleConfig Testing

### New Parameters Tested (v2.0)

All unit tests verify the new BoxplotStyleConfig interface:

**Median Styling**:
- `median_color` - Color of median curve
- `median_width` - Line width of median
- `median_alpha` - Transparency of median

**Outliers Styling**:
- `outliers_color` - Color of outlier curves
- `outliers_width` - Line width of outliers
- `outliers_alpha` - Transparency of outliers

**Hybrid Commands**:
- `median color <color>`
- `median width <number>`
- `median alpha <number>`
- `outliers color <color>`
- `outliers width <number>`
- `outliers alpha <number>`

### Test Coverage

| Component | Unit | Integration | E2E |
|-----------|------|-------------|-----|
| Command Parser | ✓ (17 tests) | - | - |
| Config Defaults | ✓ (8 tests) | - | - |
| Routing Logic | ✓ | - | - |
| Hybrid Control | ✓ | ✓ | - |
| BoxplotStyleConfig | ✓ | ✓ | - |

## Running Tests

### Individual Tests

```bash
# Sanity check
python tests/test_simple.py

# Unit tests (fast, no API calls)
python tests/unit/test_command_parser.py
python tests/unit/test_config.py
python tests/unit/test_routing.py

# Integration tests (require API key)
python tests/test_hybrid_control.py
python tests/test_error_handling.py
python tests/test_session_management.py
```

### Test Runner

```bash
# All tests (respects rate limits)
python tests/utils/run_all_tests.py

# Unit tests only (instant)
python tests/utils/run_all_tests.py --unit

# Quick validation (unit + sanity)
python tests/utils/run_all_tests.py --quick

# Integration tests only
python tests/utils/run_all_tests.py --integration

# E2E tests only
python tests/utils/run_all_tests.py --e2e
```

## Rate Limit Guidelines

**Gemini Free Tier**: 30 requests per minute (gemini-2.0-flash-lite)

- **Unit tests**: 0 API calls (safe to run repeatedly)
- **Integration tests**: Wait 60s between runs
- **E2E tests**: Wait 60s between runs
- **Full suite**: Automatic delays built-in (3s between files)

### API Call Estimates:
- `test_simple.py`: 1-2 calls
- `test_hybrid_control.py`: 10-15 calls
- `test_error_handling.py`: 5-10 calls
- `test_session_management.py`: 5-10 calls
- Full suite: ~40-50 calls (with delays, ~10 minutes)

## CI/CD Recommendations

```yaml
# Fast feedback loop (on every commit)
- Unit tests (< 10s, 0 API calls)
- test_simple.py (30s, 1-2 API calls)

# Pull request validation
- Unit tests
- Integration tests (with rate limiting)
- test_simple.py

# Pre-release validation
- All tests (unit + integration + e2e)
```

## Test File Migration Status

### ✅ New Structure Implemented
- `tests/test_simple.py` - Quick sanity check
- `tests/unit/test_command_parser.py` - Command parsing (17 tests)
- `tests/unit/test_config.py` - Configuration (8 tests)
- `tests/unit/test_routing.py` - Routing logic
- `tests/utils/run_all_tests.py` - Test runner with categories
- `tests/README.md` - This file

### 📝 To Be Migrated
- `tests/test_hybrid_control.py` → `integration/`
- `tests/test_error_handling.py` → `integration/`
- `tests/test_session_management.py` → `integration/`
- `tests/test_matplotlib_behavior.py` → `e2e/`
- `tests/interactive_test.py` → `interactive/`

### ❌ To Be Deleted (obsolete phase tests)
- `tests/test_phase1.py`
- `tests/test_phase2.py`
- `tests/test_graph.py`
- `tests/test_graph_quick.py`
- `tests/test_graph_integration.py`
- `tests/test_happy_path.py`
- `tests/test_multiturn.py`
- `tests/simple_test.py` (replaced by test_simple.py)
- `tests/run_tests_with_delays.py` (replaced by utils/run_all_tests.py)

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
1. Check that `GEMINI_API_KEY` is set
2. Verify conda environment `agent` is active with UVisBox installed
3. Check test_data/ directory has sample files
4. Review error messages carefully

## Contributing

When adding new tests:
1. **Unit tests** for individual functions → `unit/`
2. **Integration tests** for workflows → `integration/`
3. **E2E tests** for complete scenarios → `e2e/`
4. Follow existing patterns for imports and assertions
5. Include docstrings explaining what each test verifies
6. Update this README if adding new test categories

## Version History

### v2.0 (2025-01-29) - BoxplotStyleConfig Testing
- Added 17 command parser tests for new styling parameters
- Added 8 config tests for BoxplotStyleConfig defaults
- New test structure: unit/, integration/, e2e/, interactive/, utils/
- Test runner with category support
- Comprehensive BoxplotStyleConfig coverage

### v1.0 (2025-01-26) - Initial Test Suite
- Phase-based test organization
- 17 test files, ~2600 lines
- Basic coverage of all components
