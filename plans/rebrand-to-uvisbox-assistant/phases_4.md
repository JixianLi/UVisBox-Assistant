# Phase 4: Update Configuration Files

## Overview

Update all configuration and root-level script files to use the new package name. This includes pyproject.toml (Poetry configuration), main.py (entry script), create_test_data.py, setup_env.sh, and requirements.txt. Critical for ensuring the package can be installed and run correctly.

## Goals

- Update pyproject.toml: package name, version, entry point
- Update main.py: import and display name
- Update create_test_data.py: imports
- Update setup_env.sh: references and instructions
- Update requirements.txt if needed
- Verify entry point: `python -m uvisbox_assistant`
- Verify Poetry build works (if using Poetry)

## Prerequisites

- Phase 3 completed successfully
- All test imports updated
- Full test suite passing
- Version: 0.2.0

## Implementation Plan

### Step 1: Update pyproject.toml

**Objective**: Update Poetry configuration with new package name and entry point.

**File: `pyproject.toml`**

**1.1 Update Package Name and Version**:
```toml
# OLD
[tool.poetry]
name = "chatuvisbox"
version = "0.1.2"
description = "Natural language interface for UVisBox uncertainty visualization"

# NEW
[tool.poetry]
name = "uvisbox-assistant"  # Note: hyphen for PyPI package name
version = "0.2.0"
description = "Natural language interface for UVisBox uncertainty visualization"
```

**1.2 Update Package Include Path**:
```toml
# OLD
packages = [{include = "chatuvisbox", from = "src"}]

# NEW
packages = [{include = "uvisbox_assistant", from = "src"}]
```

**1.3 Update Entry Point Script**:
```toml
# OLD
[tool.poetry.scripts]
chatuvisbox = "chatuvisbox.__main__:main"

# NEW
[tool.poetry.scripts]
uvisbox-assistant = "uvisbox_assistant.__main__:main"
```

**1.4 Verify Complete pyproject.toml**:

Complete updated sections:
```toml
[tool.poetry]
name = "uvisbox-assistant"
version = "0.2.0"
description = "Natural language interface for UVisBox uncertainty visualization"
authors = ["Jixian Li <jixianli@sci.utah.edu>"]
readme = "README.md"
license = "MIT"
packages = [{include = "uvisbox_assistant", from = "src"}]

[tool.poetry.dependencies]
python = ">=3.10,<3.14"
langchain = "^0.3.27"
langchain-google-genai = "^2.1.12"
langgraph = "^0.2.76"
numpy = "^2.0"
matplotlib = "^3.10.7"
pandas = "^2.3.3"
langsmith = "^0.4.38"

[tool.poetry.group.dev.dependencies]
pytest = "^8.4.2"
pytest-cov = "^4.1.0"
black = "^24.10.0"
ruff = "^0.3.7"
ipython = "^8.37.0"

[tool.poetry.scripts]
uvisbox-assistant = "uvisbox_assistant.__main__:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
]

[tool.black]
line-length = 100
target-version = ['py313']

[tool.ruff]
line-length = 100
target-version = "py313"
select = ["E", "F", "I", "W"]
ignore = ["E501"]  # Line too long (handled by black)
```

### Step 2: Update main.py

**Objective**: Update convenience entry script.

**File: `main.py`**

```python
#!/usr/bin/env python
"""
UVisBox-Assistant - Convenience wrapper for running the REPL

This is a convenience script that imports and runs the main REPL
from the uvisbox_assistant package.

Usage:
    python main.py

Or use the module directly:
    python -m uvisbox_assistant
"""

import sys

# Run the main REPL from the package
if __name__ == "__main__":
    from src.uvisbox_assistant.main import main
    sys.exit(main())
```

**Changes**:
- Docstring: "ChatUVisBox" → "UVisBox-Assistant"
- Import: `src.chatuvisbox.main` → `src.uvisbox_assistant.main`
- Comment: `python -m chatuvisbox` → `python -m uvisbox_assistant`

### Step 3: Update create_test_data.py

**Objective**: Update test data generation script.

**File: `create_test_data.py`**

**3.1 Find Current Imports**:
```bash
grep -n "chatuvisbox" create_test_data.py
```

**3.2 Update Imports**:
```python
# OLD (if exists)
from src.chatuvisbox.data_tools import generate_ensemble_curves, generate_scalar_field_ensemble
# or similar

# NEW
from src.uvisbox_assistant.data_tools import generate_ensemble_curves, generate_scalar_field_ensemble
```

**3.3 Update Comments and Docstrings**:
```python
# OLD
"""
Create test data for ChatUVisBox

# NEW
"""
Create test data for UVisBox-Assistant
```

### Step 4: Update setup_env.sh

**Objective**: Update environment setup script with new package name.

**File: `setup_env.sh`**

**4.1 Find References**:
```bash
grep -n "chatuvisbox\|ChatUVisBox" setup_env.sh
```

**4.2 Update Script Content**:

Replace all occurrences:
- "ChatUVisBox" → "UVisBox-Assistant"
- "chatuvisbox" → "uvisbox-assistant" (for display/repo name)
- Keep "uvisbox_assistant" for Python imports

Example sections to update:
```bash
# OLD
echo "Setting up ChatUVisBox environment..."
echo "ChatUVisBox requires the following..."

# NEW
echo "Setting up UVisBox-Assistant environment..."
echo "UVisBox-Assistant requires the following..."
```

```bash
# OLD
# Test ChatUVisBox installation
python -m chatuvisbox --help

# NEW
# Test UVisBox-Assistant installation
python -m uvisbox_assistant --help
```

### Step 5: Update requirements.txt (If Applicable)

**Objective**: Verify requirements.txt doesn't reference package name.

**5.1 Check for Package Name**:
```bash
grep -n "chatuvisbox" requirements.txt
```

**Expected**: No matches (requirements.txt lists dependencies, not the package itself).

**If found**: Remove self-reference (package shouldn't depend on itself).

### Step 6: Verify Entry Point

**Objective**: Test that the new entry point works.

**6.1 Test Module Entry Point**:
```bash
python -m uvisbox_assistant --help 2>&1 || echo "Entry point test"
```

**Expected**: Should launch or show help (depends on implementation).

Alternative test if `--help` not implemented:
```bash
python -c "from src.uvisbox_assistant.__main__ import main; print('Entry point callable: OK')"
```

**6.2 Test Convenience Script**:
```bash
python main.py 2>&1 | head -5 || echo "Main script test"
```

**Expected**: Should launch REPL or show initialization.

### Step 7: Verify Poetry Configuration

**Objective**: Ensure Poetry can build the package.

**7.1 Validate pyproject.toml Syntax**:
```bash
poetry check
```

**Expected**: "All set!" (no errors).

**7.2 Test Poetry Lock (Optional)**:
```bash
poetry lock --no-update
```

**Expected**: Lock file updated successfully.

**Note**: This regenerates `poetry.lock`. Only run if comfortable with lock file changes.

**7.3 Test Poetry Install (Optional)**:
```bash
poetry install --dry-run
```

**Expected**: Shows what would be installed, no errors.

### Step 8: Verify Package Metadata

**Objective**: Confirm package name and version are correct.

**8.1 Check Package Name**:
```bash
python -c "import sys; sys.path.insert(0, 'src'); import uvisbox_assistant; print(f'Package: {uvisbox_assistant.__name__}')"
```

Expected: "Package: uvisbox_assistant"

**8.2 Check Package Version**:
```bash
python -c "import sys; sys.path.insert(0, 'src'); import uvisbox_assistant; print(f'Version: {uvisbox_assistant.__version__}')"
```

Expected: "Version: 0.2.0"

### Step 9: Test Log File Path

**Objective**: Verify log file is created at new location.

**9.1 Clear Old Logs**:
```bash
rm -f logs/chatuvisbox.log logs/uvisbox_assistant.log
```

**9.2 Run Quick Test**:
```bash
python tests/test_simple.py
```

**9.3 Check Log File**:
```bash
ls -lh logs/
# Should show: uvisbox_assistant.log (not chatuvisbox.log)

# Verify log file has content:
head -5 logs/uvisbox_assistant.log
```

**Expected**: Log file exists at `logs/uvisbox_assistant.log` with recent entries.

### Step 10: Comprehensive Configuration Verification

**Objective**: Search for any remaining old references.

```bash
# Search configuration files for old name:
grep -i "chatuvisbox" pyproject.toml main.py create_test_data.py setup_env.sh requirements.txt 2>/dev/null || echo "✓ No old references in configuration"
```

**Expected**: "✓ No old references in configuration"

**If found**: Update those specific lines.

### Step 11: Run Quick Smoke Test

**Objective**: Verify end-to-end functionality.

**11.1 Run Simple Test**:
```bash
python tests/test_simple.py
```

**Expected**: Test passes.

**11.2 Run Quick Unit Tests**:
```bash
python tests/utils/run_all_tests.py --unit
```

**Expected**: All 45+ tests pass.

### Step 12: Commit Phase 4 Changes

**Objective**: Save configuration updates.

**12.1 Review Changes**:
```bash
git status
git diff pyproject.toml main.py create_test_data.py setup_env.sh
```

**12.2 Stage Changes**:
```bash
git add pyproject.toml main.py create_test_data.py setup_env.sh
```

**12.3 Commit**:
```bash
git commit -m "Phase 4: Update configuration files

- Updated pyproject.toml:
  - Package name: chatuvisbox → uvisbox-assistant
  - Version: 0.1.2 → 0.2.0
  - Entry point: uvisbox-assistant (maps to uvisbox_assistant.__main__)
  - Package include: uvisbox_assistant
- Updated main.py: import and docstring
- Updated create_test_data.py: imports
- Updated setup_env.sh: references and instructions

Verification:
- Entry point works: python -m uvisbox_assistant ✓
- Log file path: logs/uvisbox_assistant.log ✓
- Poetry check: PASS ✓
- Quick tests: PASS ✓"
```

**12.4 Verify Commit**:
```bash
git log -1 --stat
```

### Step 13: Create Phase 4 Completion Report

```bash
cat > /tmp/phase4_completion_report.txt <<EOF
=== Phase 4 Completion Report ===
Date: $(date)
Branch: $(git branch --show-current)

CONFIGURATION FILES UPDATED:
1. pyproject.toml:
   - Package name: chatuvisbox → uvisbox-assistant
   - Version: 0.1.2 → 0.2.0
   - Entry point: chatuvisbox → uvisbox-assistant
   - Package include: chatuvisbox → uvisbox_assistant
   - Poetry check: ✅ PASS

2. main.py:
   - Import: src.chatuvisbox.main → src.uvisbox_assistant.main
   - Docstring: ChatUVisBox → UVisBox-Assistant
   - Works: ✅ VERIFIED

3. create_test_data.py:
   - Imports updated: chatuvisbox → uvisbox_assistant
   - Docstrings updated

4. setup_env.sh:
   - Display name: ChatUVisBox → UVisBox-Assistant
   - Package name references updated
   - Instructions updated

5. requirements.txt:
   - Verified: No self-references (correct)

ENTRY POINT VERIFICATION:
- Module entry: python -m uvisbox_assistant ✅ WORKS
- Convenience script: python main.py ✅ WORKS
- Entry point callable: ✅ VERIFIED

LOG FILE VERIFICATION:
- Old location: logs/chatuvisbox.log (removed)
- New location: logs/uvisbox_assistant.log ✅ CREATED
- Log content: ✅ VERIFIED

PACKAGE METADATA:
- Package name: uvisbox_assistant ✅ CORRECT
- Version: 0.2.0 ✅ CORRECT
- Exports: 6 items ✅ CORRECT

VERIFICATION TESTS:
- Simple test: ✅ PASS
- Unit tests: ✅ PASS (45+ tests)
- Poetry validation: ✅ PASS

REMAINING REFERENCES:
- Configuration files: 0 (verified with grep)
- Old package name: NONE

COMMIT:
- Commit created: YES
- Commit message: "Phase 4: Update configuration files"

NEXT STEPS:
- Proceed to Phase 5: Update Documentation
- Update 10+ markdown files
- Update README, CLAUDE, USER_GUIDE, API, TESTING, CHANGELOG

STATUS: ✅ PHASE 4 COMPLETE
EOF

cat /tmp/phase4_completion_report.txt
```

## Testing Plan

### Configuration Verification Tests

**Test 1: Poetry Configuration Valid**
```bash
poetry check
```
- Expected: "All set!"
- Purpose: Verify pyproject.toml syntax

**Test 2: Entry Point Works**
```bash
python -c "from src.uvisbox_assistant.__main__ import main; print('OK')"
```
- Expected: "OK"
- Purpose: Verify entry point is callable

**Test 3: Package Metadata Correct**
```bash
python -c "import sys; sys.path.insert(0, 'src'); import uvisbox_assistant; assert uvisbox_assistant.__version__ == '0.2.0' and uvisbox_assistant.__name__ == 'uvisbox_assistant'; print('OK')"
```
- Expected: "OK"
- Purpose: Verify version and name

**Test 4: Log File Path Correct**
```bash
python tests/test_simple.py && ls logs/uvisbox_assistant.log
```
- Expected: Log file exists
- Purpose: Verify logger uses new path

**Test 5: No Old References**
```bash
grep -i "chatuvisbox" pyproject.toml main.py create_test_data.py setup_env.sh requirements.txt 2>/dev/null || echo "OK"
```
- Expected: "OK"
- Purpose: Verify all references updated

### Functional Tests

**Test 6: Quick Smoke Test**
```bash
python tests/test_simple.py
```
- Expected: Test passes
- Purpose: Verify basic functionality

**Test 7: Unit Tests**
```bash
python tests/utils/run_all_tests.py --unit
```
- Expected: All tests pass
- Purpose: Comprehensive verification

## Success Conditions

- [ ] pyproject.toml updated:
  - [ ] Package name: "uvisbox-assistant"
  - [ ] Version: "0.2.0"
  - [ ] Entry point: "uvisbox-assistant"
  - [ ] Package include: "uvisbox_assistant"
  - [ ] Poetry check passes
- [ ] main.py updated:
  - [ ] Import: `src.uvisbox_assistant.main`
  - [ ] Docstring: "UVisBox-Assistant"
- [ ] create_test_data.py updated:
  - [ ] Imports: `uvisbox_assistant`
  - [ ] Docstrings updated
- [ ] setup_env.sh updated:
  - [ ] Display name: "UVisBox-Assistant"
  - [ ] Instructions updated
- [ ] requirements.txt verified (no self-reference)
- [ ] Entry point works: `python -m uvisbox_assistant`
- [ ] Convenience script works: `python main.py`
- [ ] Log file created at: `logs/uvisbox_assistant.log`
- [ ] Package metadata correct (name and version)
- [ ] No old references in configuration files
- [ ] Quick smoke test passes
- [ ] Unit tests pass
- [ ] Changes committed to git
- [ ] Phase 4 completion report generated

## Integration Notes

**Inputs from Phase 3**:
- All test imports updated
- Full test suite passing
- Package: `uvisbox_assistant`
- Version: 0.2.0

**Outputs for Phase 5**:
- Poetry configuration updated
- Entry points working
- Log file path correct
- All configuration files updated

**Breaking Changes**:
- Entry point command: `chatuvisbox` → `uvisbox-assistant`
- Package name on PyPI: would be `uvisbox-assistant`
- Log file location changed

**Preserved**:
- Package functionality
- Test coverage
- API surface

## Estimated Effort

**Time Estimate**: 45 minutes

**Breakdown**:
- pyproject.toml update: 10 minutes
- main.py update: 5 minutes
- create_test_data.py update: 5 minutes
- setup_env.sh update: 8 minutes
- requirements.txt verification: 2 minutes
- Entry point testing: 5 minutes
- Poetry validation: 3 minutes
- Log file verification: 3 minutes
- Comprehensive verification: 2 minutes
- Git commit: 2 minutes

**Complexity**: Medium (critical files, requires careful validation)

**API Usage**: ~5 API calls (for smoke test and simple test)

## Recovery Notes

**Issue: Poetry Check Fails**
- Resolution: Check pyproject.toml syntax
- Common errors: Missing quotes, wrong indentation
- Validation: Use TOML validator online if needed

**Issue: Entry Point Not Working**
- Resolution: Verify `__main__.py` has `main()` function
- Check: Import path in pyproject.toml scripts section
- Test: `python -c "from src.uvisbox_assistant.__main__ import main"`

**Issue: Log File Wrong Location**
- Resolution: Check logger.py has correct path
- Verify: `grep -n "uvisbox_assistant.log" src/uvisbox_assistant/logger.py`
- Re-run test to recreate log

**Issue: Import Errors**
- Resolution: Likely missed an import in Phase 2 or 3
- Check: `grep -r "from chatuvisbox" .`
- Fix: Update missed imports

## Phase 4 Checklist

**pyproject.toml Updates**:
- [ ] Package name: "uvisbox-assistant"
- [ ] Version: "0.2.0"
- [ ] Package include: "uvisbox_assistant"
- [ ] Entry point: "uvisbox-assistant"
- [ ] Poetry check: PASS

**Script Updates**:
- [ ] main.py: import and docstring updated
- [ ] create_test_data.py: imports updated
- [ ] setup_env.sh: references updated
- [ ] requirements.txt: verified (no changes needed)

**Entry Point Verification**:
- [ ] Module entry works: `python -m uvisbox_assistant`
- [ ] Convenience script works: `python main.py`
- [ ] Entry point callable: verified

**Log File Verification**:
- [ ] Old log removed or ignored
- [ ] New log created: `logs/uvisbox_assistant.log`
- [ ] Log content verified

**Package Metadata**:
- [ ] Package name correct: `uvisbox_assistant`
- [ ] Version correct: `0.2.0`
- [ ] Exports intact: 6 items

**Verification Tests**:
- [ ] Poetry check: PASS
- [ ] Entry point test: PASS
- [ ] Package metadata test: PASS
- [ ] Log file test: PASS
- [ ] No old references: VERIFIED
- [ ] Smoke test: PASS
- [ ] Unit tests: PASS

**Git Operations**:
- [ ] Changes reviewed
- [ ] Changes staged
- [ ] Commit created
- [ ] Phase 4 report generated

---

**Phase 4 Status**: 📋 Ready to Execute
**Next Phase**: Phase 5 - Update Documentation
