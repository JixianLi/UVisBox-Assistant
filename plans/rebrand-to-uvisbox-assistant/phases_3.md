# Phase 3: Update Test Suite

## Overview

Update all test files to import from `uvisbox_assistant` instead of `chatuvisbox`. This phase covers 22+ test files across unit, integration, e2e, and interactive test directories. We prioritize unit tests for immediate feedback since they have 0 API calls.

## Goals

- Update all test imports: `from chatuvisbox` → `from uvisbox_assistant`
- Update test utilities and conftest.py
- Run unit tests immediately for fast feedback (0 API calls)
- Fix any import errors discovered
- Run integration and E2E tests with rate limit awareness
- Verify all tests pass with new package name

## Prerequisites

- Phase 2 completed successfully
- Package renamed to `uvisbox_assistant`
- All source imports updated and verified
- Version bumped to 0.2.0

## Implementation Plan

### Step 1: Update Test Configuration Files

**Objective**: Update test infrastructure files first.

**1.1 Update `tests/conftest.py`**:

Check if this file has any imports:
```bash
grep -n "chatuvisbox" tests/conftest.py
```

If imports exist, update them:
```python
# OLD
from chatuvisbox import config
# or similar imports

# NEW
from uvisbox_assistant import config
```

**1.2 Update `tests/__init__.py`**:

Check for imports:
```bash
grep -n "chatuvisbox" tests/__init__.py
```

Update any found imports.

**1.3 Verify Test Utilities**:
```bash
grep -n "chatuvisbox" tests/utils/*.py
```

Update `tests/utils/run_all_tests.py` if it has any imports (unlikely, but check).

### Step 2: Update Unit Test Files (Priority 1)

**Objective**: Update unit tests first for immediate feedback (0 API calls).

**2.1 List Unit Test Files with Imports**:
```bash
grep -l "from chatuvisbox" tests/unit/*.py
```

Expected files:
- `test_command_parser.py`
- `test_config.py`
- `test_routing.py`
- `test_tools.py`
- `test_error_tracking.py`
- `test_output_control.py`
- `test_error_interpretation.py`
- `test_command_handlers.py`

**2.2 Update Each Unit Test File**:

**File: `tests/unit/test_command_parser.py`**:
```python
# OLD
from chatuvisbox.command_parser import parse_simple_command, apply_command_to_params

# NEW
from uvisbox_assistant.command_parser import parse_simple_command, apply_command_to_params
```

**File: `tests/unit/test_config.py`**:
```python
# OLD
from chatuvisbox import config

# NEW
from uvisbox_assistant import config
```

**File: `tests/unit/test_routing.py`**:
```python
# OLD
from chatuvisbox.routing import route_after_model, route_after_tool
from chatuvisbox.state import create_initial_state

# NEW
from uvisbox_assistant.routing import route_after_model, route_after_tool
from uvisbox_assistant.state import create_initial_state
```

**File: `tests/unit/test_tools.py`**:
```python
# OLD
from chatuvisbox.data_tools import (
    generate_ensemble_curves,
    generate_scalar_field_ensemble,
    generate_vector_field_ensemble,
)
from chatuvisbox.vis_tools import (
    plot_functional_boxplot,
    plot_curve_boxplot,
    plot_contour_boxplot,
    plot_probabilistic_marching_squares,
    plot_uncertainty_lobes,
    plot_squid_glyph_2D,
)

# NEW
from uvisbox_assistant.data_tools import (
    generate_ensemble_curves,
    generate_scalar_field_ensemble,
    generate_vector_field_ensemble,
)
from uvisbox_assistant.vis_tools import (
    plot_functional_boxplot,
    plot_curve_boxplot,
    plot_contour_boxplot,
    plot_probabilistic_marching_squares,
    plot_uncertainty_lobes,
    plot_squid_glyph_2D,
)
```

**File: `tests/unit/test_error_tracking.py`**:
```python
# OLD
from chatuvisbox.error_tracking import ErrorRecord
from chatuvisbox.conversation import ConversationSession

# NEW
from uvisbox_assistant.error_tracking import ErrorRecord
from uvisbox_assistant.conversation import ConversationSession
```

**File: `tests/unit/test_output_control.py`**:
```python
# OLD
from chatuvisbox.output_control import vprint, is_verbose, set_session
from chatuvisbox.conversation import ConversationSession

# NEW
from uvisbox_assistant.output_control import vprint, is_verbose, set_session
from uvisbox_assistant.conversation import ConversationSession
```

**File: `tests/unit/test_error_interpretation.py`**:
```python
# OLD
from chatuvisbox.error_interpretation import (
    detect_error_pattern,
    interpret_uvisbox_error,
    format_error_with_hint,
)

# NEW
from uvisbox_assistant.error_interpretation import (
    detect_error_pattern,
    interpret_uvisbox_error,
    format_error_with_hint,
)
```

**File: `tests/unit/test_command_handlers.py`**:
```python
# OLD
from chatuvisbox.conversation import ConversationSession

# NEW
from uvisbox_assistant.conversation import ConversationSession
```

**2.3 Verify No Old Imports in Unit Tests**:
```bash
grep -r "from chatuvisbox" tests/unit/ || echo "✓ No old imports in unit tests"
```

### Step 3: Run Unit Tests for Immediate Feedback

**Objective**: Verify unit tests pass with new imports (0 API calls, instant).

**3.1 Run All Unit Tests**:
```bash
python tests/utils/run_all_tests.py --unit
```

**Expected Output**:
- All 45+ unit tests pass
- Execution time: < 15 seconds
- 0 API calls
- No import errors

**3.2 If Failures Occur**:

Check error messages for:
- `ModuleNotFoundError`: Import path incorrect
- `ImportError`: Circular import or missing dependency
- `AttributeError`: Function/class name typo

**Fix pattern**:
1. Identify failing test file
2. Check imports in that file
3. Verify import matches source file structure
4. Re-run: `python tests/unit/test_<name>.py`

### Step 4: Update Integration Test Files

**Objective**: Update integration tests (15-25 API calls per file).

**4.1 List Integration Test Files**:
```bash
grep -l "from chatuvisbox" tests/integration/*.py
```

Expected files:
- `test_hybrid_control.py`
- `test_error_handling.py`
- `test_session_management.py`

**4.2 Update Each Integration Test File**:

**File: `tests/integration/test_hybrid_control.py`**:
```python
# OLD
from chatuvisbox.conversation import ConversationSession

# NEW
from uvisbox_assistant.conversation import ConversationSession
```

**File: `tests/integration/test_error_handling.py`**:
```python
# OLD
from chatuvisbox.graph import run_graph, graph_app
from chatuvisbox.routing import route_after_tool
from chatuvisbox.state import create_initial_state

# NEW
from uvisbox_assistant.graph import run_graph, graph_app
from uvisbox_assistant.routing import route_after_tool
from uvisbox_assistant.state import create_initial_state
```

**File: `tests/integration/test_session_management.py`**:
```python
# OLD
from chatuvisbox.conversation import ConversationSession
from chatuvisbox import config

# NEW
from uvisbox_assistant.conversation import ConversationSession
from uvisbox_assistant import config
```

**4.3 Verify Integration Test Imports**:
```bash
grep -r "from chatuvisbox" tests/integration/ || echo "✓ No old imports in integration tests"
```

### Step 5: Update E2E Test Files

**Objective**: Update E2E tests (20-30 API calls per file).

**5.1 List E2E Test Files**:
```bash
grep -l "from chatuvisbox" tests/e2e/*.py
```

Expected file:
- `test_matplotlib_behavior.py`

**5.2 Update E2E Test File**:

**File: `tests/e2e/test_matplotlib_behavior.py`**:
```python
# OLD
from chatuvisbox.conversation import ConversationSession
# (check actual imports)

# NEW
from uvisbox_assistant.conversation import ConversationSession
```

**5.3 Verify E2E Test Imports**:
```bash
grep -r "from chatuvisbox" tests/e2e/ || echo "✓ No old imports in e2e tests"
```

### Step 6: Update Interactive Test Files

**Objective**: Update interactive test files (user-paced).

**6.1 List Interactive Test Files**:
```bash
grep -l "from chatuvisbox" tests/interactive/*.py
```

Expected file:
- `interactive_test.py`

**6.2 Update Interactive Test File**:

**File: `tests/interactive/interactive_test.py`**:
```python
# OLD
from chatuvisbox.graph import run_graph
from chatuvisbox.state import GraphState

# NEW
from uvisbox_assistant.graph import run_graph
from uvisbox_assistant.state import GraphState
```

**6.3 Verify Interactive Test Imports**:
```bash
grep -r "from chatuvisbox" tests/interactive/ || echo "✓ No old imports in interactive tests"
```

### Step 7: Update Simple Test File

**Objective**: Update `tests/test_simple.py` (quick sanity check).

**File: `tests/test_simple.py`**:
```python
# OLD
from chatuvisbox.graph import create_graph
from chatuvisbox.state import create_initial_state

# NEW
from uvisbox_assistant.graph import create_graph
from uvisbox_assistant.state import create_initial_state
```

### Step 8: Comprehensive Import Verification

**Objective**: Ensure NO old imports remain in tests.

```bash
# This should return ZERO results:
grep -r "from chatuvisbox\|import chatuvisbox" tests/ --include="*.py"

# If any results, fix those files
```

### Step 9: Run Integration Tests (Rate Limit Aware)

**Objective**: Verify integration tests pass (15-25 API calls per file).

**9.1 Run Integration Tests with Delays**:
```bash
python tests/utils/run_all_tests.py --integration
```

**Expected**:
- All integration tests pass
- Automatic rate limit handling
- Total time: 2-4 minutes
- ~50 API calls total

**9.2 If Rate Limits Hit**:
- Wait 60 seconds
- Re-run failed test individually

### Step 10: Run E2E Tests (Rate Limit Aware)

**Objective**: Verify E2E tests pass (20-30 API calls per file).

**10.1 Run E2E Tests**:
```bash
python tests/utils/run_all_tests.py --e2e
```

**Expected**:
- All E2E tests pass
- Total time: 3-5 minutes
- ~30 API calls total

### Step 11: Run Complete Test Suite

**Objective**: Full verification pass.

**11.1 Run All Tests**:
```bash
python tests/utils/run_all_tests.py
```

**Expected**:
- Unit: 45+ tests pass (instant)
- Integration: All pass (2-4 minutes)
- E2E: All pass (3-5 minutes)
- Total: ~80 API calls
- Total time: ~10 minutes

**11.2 Document Test Results**:
```bash
cat > /tmp/phase3_test_results.txt <<EOF
=== Phase 3 Test Results ===
Date: $(date)

UNIT TESTS:
- Status: PASS
- Count: 45+
- Time: <15 seconds
- API calls: 0

INTEGRATION TESTS:
- Status: PASS
- Count: 15
- Time: ~3 minutes
- API calls: ~50

E2E TESTS:
- Status: PASS
- Count: 8
- Time: ~4 minutes
- API calls: ~30

TOTAL:
- Tests: 68+
- Time: ~10 minutes
- API calls: ~80
- Success rate: 100%
EOF

cat /tmp/phase3_test_results.txt
```

### Step 12: Commit Phase 3 Changes

**Objective**: Save test suite updates.

**12.1 Review Changes**:
```bash
git status
git diff tests/
```

**12.2 Stage Changes**:
```bash
git add tests/
```

**12.3 Commit**:
```bash
git commit -m "Phase 3: Update test suite imports

- Updated all test imports: chatuvisbox → uvisbox_assistant
- Updated 22+ test files across unit/integration/e2e/interactive
- Updated test utilities and configuration
- All tests passing: 68+ tests, 0 failures

Test results:
- Unit tests (45+): ✓ PASS (0 API calls)
- Integration tests (15): ✓ PASS (~50 API calls)
- E2E tests (8): ✓ PASS (~30 API calls)"
```

**12.4 Verify Commit**:
```bash
git log -1 --stat
```

### Step 13: Create Phase 3 Completion Report

```bash
cat > /tmp/phase3_completion_report.txt <<EOF
=== Phase 3 Completion Report ===
Date: $(date)
Branch: $(git branch --show-current)

TEST FILES UPDATED:
- Unit tests: 8 files
- Integration tests: 3 files
- E2E tests: 1 file
- Interactive tests: 1 file
- Simple test: 1 file
- Test utilities: verified
- Total: 22+ files

IMPORT UPDATES:
- Old imports removed: ~30 statements
- New imports added: ~30 statements
- Remaining "from chatuvisbox" in tests/: 0 (verified)

TEST EXECUTION RESULTS:
- Unit tests: ✅ PASS (45+ tests, 0 API calls, <15s)
- Integration tests: ✅ PASS (15 tests, ~50 API calls, ~3min)
- E2E tests: ✅ PASS (8 tests, ~30 API calls, ~4min)
- Total tests: 68+ tests, 100% pass rate
- Total API calls: ~80
- Total time: ~10 minutes

VERIFICATION:
- No old imports in tests/: ✅ VERIFIED
- All unit tests pass: ✅ VERIFIED
- All integration tests pass: ✅ VERIFIED
- All E2E tests pass: ✅ VERIFIED
- No import errors: ✅ VERIFIED

COMMIT:
- Commit created: YES
- Commit message: "Phase 3: Update test suite imports"

NEXT STEPS:
- Proceed to Phase 4: Update Configuration Files
- Update pyproject.toml, main.py, setup_env.sh
- Verify entry point: python -m uvisbox_assistant

STATUS: ✅ PHASE 3 COMPLETE
EOF

cat /tmp/phase3_completion_report.txt
```

## Testing Plan

### Unit Test Verification (Priority 1)

**Test 1: Command Parser Tests**
```bash
python tests/unit/test_command_parser.py
```
- Expected: 17 tests pass
- Purpose: Verify BoxplotStyleConfig command parsing

**Test 2: Config Tests**
```bash
python tests/unit/test_config.py
```
- Expected: 5 tests pass
- Purpose: Verify configuration loading

**Test 3: All Unit Tests**
```bash
python tests/utils/run_all_tests.py --unit
```
- Expected: 45+ tests pass, 0 API calls
- Purpose: Comprehensive unit test verification

### Integration Test Verification

**Test 4: Hybrid Control Tests**
```bash
python tests/integration/test_hybrid_control.py
```
- Expected: Tests pass (~20 API calls)
- Purpose: Verify fast path parameter updates

**Test 5: Error Handling Tests**
```bash
python tests/integration/test_error_handling.py
```
- Expected: Tests pass (~15 API calls)
- Purpose: Verify circuit breaker and recovery

### E2E Test Verification

**Test 6: Matplotlib Behavior Tests**
```bash
python tests/e2e/test_matplotlib_behavior.py
```
- Expected: Tests pass (~30 API calls)
- Purpose: Verify non-blocking plot behavior

### Complete Suite Verification

**Test 7: Full Test Suite**
```bash
python tests/utils/run_all_tests.py
```
- Expected: All tests pass (~80 API calls, ~10 minutes)
- Purpose: Comprehensive system verification

## Success Conditions

- [ ] All test configuration files updated
- [ ] All 8 unit test files updated
- [ ] All 3 integration test files updated
- [ ] All 1 E2E test file updated
- [ ] All 1 interactive test file updated
- [ ] Simple test file updated
- [ ] No old imports in tests: `grep -r "from chatuvisbox" tests/` returns empty
- [ ] Unit tests pass: 45+ tests, 0 API calls, <15 seconds
- [ ] Integration tests pass: 15 tests, ~50 API calls, ~3 minutes
- [ ] E2E tests pass: 8 tests, ~30 API calls, ~4 minutes
- [ ] Full test suite passes: 68+ tests, 100% success rate
- [ ] No import errors detected
- [ ] Changes committed to git
- [ ] Phase 3 completion report generated

## Integration Notes

**Inputs from Phase 2**:
- Renamed package: `uvisbox_assistant`
- Updated source imports
- Version: 0.2.0

**Outputs for Phase 4**:
- All test imports updated
- Full test suite passing
- Verified package functionality

**Key Achievements**:
- 22+ test files updated
- ~30 import statements updated
- 100% test pass rate maintained
- 0 functionality regressions

## Estimated Effort

**Time Estimate**: 1 hour

**Breakdown**:
- Test config updates: 5 minutes
- Unit test updates (8 files): 15 minutes
- Unit test execution: 1 minute
- Integration test updates (3 files): 10 minutes
- E2E test updates (2 files): 5 minutes
- Interactive test updates (1 file): 3 minutes
- Complete test suite run: 10 minutes
- Verification and debugging: 8 minutes
- Git commit: 2 minutes
- Reporting: 1 minute

**Complexity**: Medium (systematic updates, rate limit awareness needed)

**API Usage**: ~80 API calls (for full test suite)

## Recovery Notes

**Issue: Import Errors in Unit Tests**
- Resolution: Check import statements for typos
- Verify: Source file exists at expected path
- Recovery: Fix import, re-run test file individually

**Issue: Rate Limit Exceeded**
- Resolution: Wait 60 seconds between test runs
- Use: `python tests/utils/run_all_tests.py` (has automatic delays)
- Recovery: Re-run failed tests after delay

**Issue: Test Failures (Not Import Related)**
- Resolution: May indicate functional regression
- Investigation: Compare error with Phase 1 baseline
- Recovery: Check if test itself needs update (unlikely)

**Issue: Circular Import in Tests**
- Resolution: Review import order in test file
- Check: Test dependencies on source modules
- Recovery: Use lazy imports or restructure test

## Phase 3 Checklist

**Test Configuration**:
- [ ] `tests/conftest.py` updated
- [ ] `tests/__init__.py` verified
- [ ] Test utilities verified

**Unit Tests** (8 files):
- [ ] `test_command_parser.py` updated
- [ ] `test_config.py` updated
- [ ] `test_routing.py` updated
- [ ] `test_tools.py` updated
- [ ] `test_error_tracking.py` updated
- [ ] `test_output_control.py` updated
- [ ] `test_error_interpretation.py` updated
- [ ] `test_command_handlers.py` updated

**Integration Tests** (3 files):
- [ ] `test_hybrid_control.py` updated
- [ ] `test_error_handling.py` updated
- [ ] `test_session_management.py` updated

**E2E Tests** (1 file):
- [ ] `test_matplotlib_behavior.py` updated

**Interactive Tests** (1 file):
- [ ] `interactive_test.py` updated

**Other Tests**:
- [ ] `test_simple.py` updated

**Verification**:
- [ ] No old imports in tests/
- [ ] Unit tests pass (45+, 0 API calls)
- [ ] Integration tests pass (15, ~50 API calls)
- [ ] E2E tests pass (8, ~30 API calls)
- [ ] Full suite passes (68+, ~80 API calls)

**Git Operations**:
- [ ] Changes reviewed
- [ ] Changes staged
- [ ] Commit created
- [ ] Phase 3 report generated

---

**Phase 3 Status**: 📋 Ready to Execute
**Next Phase**: Phase 4 - Update Configuration Files
