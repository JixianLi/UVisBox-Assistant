# Testing Guide for ChatUVisBox

## Gemini API Rate Limits (Free Tier)

**Important**: The free tier has strict rate limits:
- **30 requests per minute** (using gemini-2.0-flash-lite)
- Daily quota limits also apply

Each graph execution can make **2-6 API calls** depending on the workflow:
- Simple request: 2-3 calls (user → model → response)
- Data generation: 3-4 calls (user → model → data tool → model → response)
- Data + visualization: 4-6 calls (user → model → data → model → viz → model → response)

## Quick Testing (Recommended for Development)

### 1. Quick Integration Test (6-10 API calls)
**Best for**: Quick validation during development

```bash
python test_graph_quick.py
```

This runs 3 essential tests:
- Data generation only
- Data + visualization
- Conversational response

**Time**: ~10-20 seconds
**API calls**: 6-10 (well under limit)

### 2. Individual Module Tests (0 API calls)
**Best for**: Testing specific components without API usage

```bash
# Test routing logic (no API calls)
python test_routing.py

# Test Phase 1 tools and schemas (no API calls - just data generation)
python test_phase1.py
```

### 3. Single Workflow Test (2-6 API calls)
**Best for**: Testing a specific workflow

```python
from graph import run_graph

# Test one workflow at a time
result = run_graph("Generate 10 curves and plot them")
print(f"Success! Data: {result.get('current_data_path')}")
```

## Comprehensive Testing

### Full Test Suite with Delays
**Best for**: Complete validation before commits

```bash
python run_tests_with_delays.py
```

This script:
- Runs all test suites in order
- Adds 60-second delays between API-heavy tests
- Respects rate limits automatically
- Stops on first failure

**Time**: ~5-7 minutes (includes delays)

### Manual Test Suite (with delays)

If you prefer manual control:

```bash
# 1. Quick test
python test_graph_quick.py
# Wait 60s

# 2. Phase 1 (no API calls - safe to run immediately)
python test_phase1.py

# 3. Phase 2 (10-15 API calls)
python test_phase2.py
# Wait 60s

# 4. Routing (no API calls - safe to run immediately)
python test_routing.py

# 5. Graph compilation (5-8 API calls)
python test_graph.py
# Wait 60s

# 6. Full integration (15-20 API calls - will hit limit)
python test_graph_integration.py
```

## Rate Limit Exceeded Error

If you see this error:
```
ResourceExhausted: 429 You exceeded your current quota
Please retry in 17.461429122s
```

**Solution**: Wait 60 seconds and try again.

The error message tells you exactly how long to wait (e.g., "retry in 17s"). Wait that long plus a buffer.

## Test File Overview

| Test File | API Calls | What It Tests | Safe to Run Repeatedly? |
|-----------|-----------|---------------|------------------------|
| `test_routing.py` | 0 | Routing logic | ✅ Yes |
| `test_phase1.py` | 0 | Tool schemas, data generation | ✅ Yes |
| `test_phase2.py` | 10-15 | State, nodes, model | ⚠️ Wait 60s between runs |
| `test_graph.py` | 5-8 | Graph compilation | ⚠️ Wait 60s between runs |
| `test_graph_quick.py` | 6-10 | Quick integration | ⚠️ Wait 60s between runs |
| `test_graph_integration.py` | 15-20 | Full integration (7 tests) | ❌ Will hit limit |
| `run_tests_with_delays.py` | ~40-50 | All tests with delays | ✅ Yes (auto-delays) |

## Development Workflow Recommendations

### During Active Development
1. Run `test_graph_quick.py` after major changes
2. Wait 60s between test runs
3. Use non-API tests (`test_routing.py`, `test_phase1.py`) for quick validation

### Before Committing
1. Run `python run_tests_with_delays.py` for full validation
2. Review test output for any failures
3. Fix issues and re-run failed tests only

### Debugging Specific Issues
1. Use Python REPL for single requests:
   ```python
   from graph import run_graph
   result = run_graph("your query here")
   print(result)
   ```
2. This gives you full control and minimal API usage

## Estimating API Usage

**Rule of thumb**:
- Each test function ≈ 2-6 API calls
- Stay under 12-13 test functions per minute (to account for retries)
- Add 60s delay after every ~10-12 API calls

**Example**:
```python
# This would use ~12-18 API calls (under limit with margin)
test_1()  # 3 calls
test_2()  # 5 calls
test_3()  # 4 calls
# Total: 12 calls ✅ Safe

# Add delay before more tests
time.sleep(60)

test_4()  # ...
```

## Tips for Minimizing API Usage

1. **Use smaller datasets**: "Generate 5 curves" instead of "Generate 100 curves"
2. **Test data tools separately**: They don't call the API (just generate local data)
3. **Mock the model** for unit tests (not yet implemented)
4. **Cache responses** for repeated queries (not yet implemented)

## Future Improvements

Planned features to reduce API usage:
- Mock model mode for testing
- Response caching for identical queries
- Paid tier upgrade guide (higher limits)
- Local LLM option for development

## Questions?

See `CLAUDE.md` for architecture details or `plans/` for implementation guides.
