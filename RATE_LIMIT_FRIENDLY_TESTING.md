# Rate-Limit-Friendly Testing Strategy

## Summary

All ChatUVisBox tests have been adapted to respect Gemini's free tier rate limits (30 requests/minute with gemini-2.0-flash-lite). You can now run tests safely without hitting quota limits.

## Quick Reference

### ✅ Safe to Run Anytime (No API Calls)
```bash
python test_routing.py        # Routing logic
python test_phase1.py          # Tool schemas and data generation
```

### ⚠️ Run with 60s Delays (6-15 API Calls)
```bash
python test_graph_quick.py     # Quick integration (RECOMMENDED)
python test_phase2.py          # State and nodes
python test_graph.py           # Graph compilation
```

### 🚀 Automated with Delays (All Tests)
```bash
python run_tests_with_delays.py    # Runs all tests with auto-delays
```

## Recommended Testing Workflow

### During Development (Most Common)
```bash
# 1. Make code changes

# 2. Run quick test (9 API calls, ~5 seconds)
python test_graph_quick.py

# 3. Wait 60 seconds before next test run
```

### Before Committing
```bash
# Run full suite with automatic delays (~5-7 minutes)
python run_tests_with_delays.py
```

### Testing Specific Features
```bash
# Routing changes? (0 API calls - instant)
python test_routing.py

# Data/vis tools changes? (0 API calls - instant)
python test_phase1.py

# Graph/nodes changes? (6-10 API calls - wait 60s between runs)
python test_graph_quick.py
```

## Test File Comparison

| File | API Calls | Duration | Best For |
|------|-----------|----------|----------|
| `test_graph_quick.py` ⭐ | 6-10 | ~5s | Development (new!) |
| `test_routing.py` | 0 | <1s | Routing changes |
| `test_phase1.py` | 0 | ~1s | Tool changes |
| `test_phase2.py` | 10-15 | ~8s | State/node changes |
| `test_graph.py` | 5-8 | ~4s | Graph changes |
| `test_graph_integration.py` | 15-20 | ~15s | ⚠️ Will hit limit |
| `run_tests_with_delays.py` 🚀 | 40-50 | ~5-7min | Pre-commit validation |

⭐ **Recommended** for regular development
🚀 **Recommended** for comprehensive validation

## What Changed?

### New Files Created

1. **test_graph_quick.py** - Streamlined 3-test suite
   - Data generation only (3 API calls)
   - Data + visualization (5 API calls)
   - Conversational response (1 API call)
   - **Total**: ~9 API calls (60% of limit)

2. **run_tests_with_delays.py** - Automated test runner
   - Runs all test suites in sequence
   - Adds 60-second delays between API-heavy tests
   - Shows progress and estimates
   - Stops on first failure

3. **TESTING.md** - Comprehensive testing guide
   - Rate limit explanations
   - Best practices
   - Troubleshooting tips

4. **RATE_LIMIT_FRIENDLY_TESTING.md** - This document

### Modified Approach

**Before**: Run all integration tests sequentially → Hit rate limit ❌

**Now**:
- Use `test_graph_quick.py` for development ✅
- Use `run_tests_with_delays.py` for full validation ✅
- Reserve `test_graph_integration.py` for comprehensive testing (when needed)

## API Call Breakdown

### test_graph_quick.py (9 calls total)
```
Test 1: Data only
  → User message → Model (1)
  → Model decides → Tool call (0, same request)
  → Tool executes → Model (2)
  → Model responds → End (3)
  Total: 3 calls

Test 2: Data + vis
  → User → Model (4)
  → Model → Data tool → Model (5)
  → Model → Vis tool → Model (6)
  → Model responds (7)
  Total: 4 calls (7 cumulative)

Test 3: Conversational
  → User → Model (8)
  → Model responds (9)
  Total: 2 calls (9 cumulative)

Grand Total: ~9 API calls ✅ (30% of 30/min limit)
```

## When You'll See Rate Limit Errors

You'll only hit the limit if you:
1. Run `test_graph_integration.py` (makes 15-20 calls)
2. Run multiple test files without delays
3. Run tests repeatedly within the same minute

**Solution**: Always wait 60 seconds between test runs that make API calls.

## Verification

The quick test was successfully run and completed:
```
✅ ALL TESTS PASSED in 5.2s
API calls made: ~9 (estimated)
Free tier limit: 30 requests/minute
Status: ✅ Well under limit
```

All 3 tests passed:
- ✅ Data generation (10 curves generated)
- ✅ Data + visualization (functional boxplot displayed)
- ✅ Conversational response

## Future Improvements

To further reduce API usage:
1. **Mock mode**: Test with fake LLM responses (Phase 9)
2. **Response caching**: Cache identical queries
3. **Batch testing**: Group tests more intelligently
4. **Local LLM option**: Use local model for development

## Questions?

- See `TESTING.md` for detailed testing guide
- See `CLAUDE.md` for architecture overview
- See `plans/README.md` for implementation phases
