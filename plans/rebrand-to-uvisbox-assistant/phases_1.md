# Phase 1: Pre-Rebrand Verification and Planning

## Overview

Establish a verified baseline state before any modifications. This phase ensures the current codebase is healthy, documents all files requiring changes, and creates safety backups for recovery if needed.

## Goals

- Verify current codebase health (all tests passing)
- Create comprehensive inventory of all files requiring changes
- Document all current import patterns and references
- Create git backup branch for recovery
- Establish success metrics for rebrand

## Prerequisites

- Git working directory is clean (no uncommitted changes)
- Conda environment `agent` is activated with UVisBox installed
- `GEMINI_API_KEY` environment variable is set

## Implementation Plan

### Step 1: Verify Git Status

**Objective**: Ensure working directory is clean before starting.

```bash
cd /Users/jixianli/projects/chatuvisbox
git status
```

**Expected Output**:
```
On branch main
nothing to commit, working tree clean
```

**Action if dirty**:
- Commit or stash any uncommitted changes
- Ensure no untracked files that should be committed

### Step 2: Create Backup Branch

**Objective**: Create safety net for recovery.

```bash
git checkout -b backup-before-rebrand-0.1.2
git checkout main  # Return to main for actual work
git checkout -b rebrand-to-uvisbox-assistant
```

**Verification**:
```bash
git branch
# Should show:
#   backup-before-rebrand-0.1.2
#   main
# * rebrand-to-uvisbox-assistant
```

### Step 3: Run Baseline Test Suite

**Objective**: Verify all tests pass before any changes.

**3.1 Quick Sanity Check (30 seconds, 1-2 API calls)**:
```bash
python tests/test_simple.py
```

Expected: Test passes, confirms basic functionality.

**3.2 Unit Tests (instant, 0 API calls)**:
```bash
python tests/utils/run_all_tests.py --unit
```

Expected: All 45+ unit tests pass instantly.

**3.3 Integration Tests (2-4 minutes, ~50 API calls total)**:
```bash
python tests/utils/run_all_tests.py --integration
```

Expected: All integration tests pass. Note timing for comparison after rebrand.

**3.4 E2E Tests (3-5 minutes, ~30 API calls)**:
```bash
python tests/utils/run_all_tests.py --e2e
```

Expected: All E2E tests pass.

**Record Baseline**:
- Document test counts: "45 unit, 15 integration, 8 e2e" (example)
- Document timing: "Unit: 10s, Integration: 180s, E2E: 240s" (example)
- Document any warnings or notes

### Step 4: Create Comprehensive File Inventory

**Objective**: Document every file requiring changes.

**4.1 Source Files Inventory**:
```bash
find src/chatuvisbox -type f -name "*.py" | sort > /tmp/source_files.txt
wc -l /tmp/source_files.txt
```

Expected: 19 Python files in `src/chatuvisbox/`.

**4.2 Test Files Inventory**:
```bash
find tests -type f -name "*.py" | sort > /tmp/test_files.txt
wc -l /tmp/test_files.txt
```

Expected: 22+ Python files in `tests/`.

**4.3 Documentation Files Inventory**:
```bash
find . -maxdepth 1 -name "*.md" | sort > /tmp/root_docs.txt
find docs -name "*.md" | sort > /tmp/docs_docs.txt
find test_data -name "*.md" | sort >> /tmp/docs_docs.txt
find tests -name "*.md" | sort >> /tmp/docs_docs.txt
cat /tmp/root_docs.txt /tmp/docs_docs.txt > /tmp/all_docs.txt
wc -l /tmp/all_docs.txt
```

Expected: 10+ markdown files.

**4.4 Configuration Files Inventory**:
```bash
ls -1 pyproject.toml requirements.txt setup_env.sh main.py create_test_data.py > /tmp/config_files.txt
wc -l /tmp/config_files.txt
```

Expected: 5 configuration/script files.

**4.5 Create Master Inventory**:
```bash
cat > /tmp/rebrand_inventory.txt <<EOF
=== ChatUVisBox → UVisBox-Assistant Rebrand Inventory ===
Date: $(date)

SOURCE FILES (19):
$(cat /tmp/source_files.txt)

TEST FILES (22+):
$(cat /tmp/test_files.txt)

DOCUMENTATION FILES (10+):
$(cat /tmp/all_docs.txt)

CONFIGURATION FILES (5):
$(cat /tmp/config_files.txt)

TOTAL FILES: $(cat /tmp/source_files.txt /tmp/test_files.txt /tmp/all_docs.txt /tmp/config_files.txt | wc -l)
EOF

cat /tmp/rebrand_inventory.txt
```

### Step 5: Document All "chatuvisbox" References

**Objective**: Find every occurrence requiring changes.

**5.1 Python Import Statements**:
```bash
grep -rn "from chatuvisbox" . --include="*.py" > /tmp/python_imports.txt
grep -rn "import chatuvisbox" . --include="*.py" >> /tmp/python_imports.txt
wc -l /tmp/python_imports.txt
```

Expected: 50+ import statements.

**5.2 Documentation References**:
```bash
grep -rn "chatuvisbox" . --include="*.md" > /tmp/doc_references.txt
wc -l /tmp/doc_references.txt
```

Expected: 100+ references in documentation.

**5.3 Configuration References**:
```bash
grep -rn "chatuvisbox" pyproject.toml requirements.txt setup_env.sh main.py create_test_data.py > /tmp/config_references.txt
wc -l /tmp/config_references.txt
```

Expected: 10+ references in configuration.

**5.4 Case-Insensitive Search (for "ChatUVisBox" display name)**:
```bash
grep -rin "ChatUVisBox" . --include="*.py" --include="*.md" > /tmp/display_name_references.txt
wc -l /tmp/display_name_references.txt
```

Expected: 50+ display name references.

**5.5 Create Reference Summary**:
```bash
cat > /tmp/reference_summary.txt <<EOF
=== Reference Summary ===

Python Imports: $(wc -l < /tmp/python_imports.txt) occurrences
Documentation: $(wc -l < /tmp/doc_references.txt) occurrences
Configuration: $(wc -l < /tmp/config_references.txt) occurrences
Display Name: $(wc -l < /tmp/display_name_references.txt) occurrences

Total Estimated Changes: $(cat /tmp/python_imports.txt /tmp/doc_references.txt /tmp/config_references.txt /tmp/display_name_references.txt | wc -l)
EOF

cat /tmp/reference_summary.txt
```

### Step 6: Document Current Package Structure

**Objective**: Verify package imports work correctly before changes.

**6.1 Test Current Import**:
```bash
python -c "import chatuvisbox; print(f'Package: {chatuvisbox.__name__}'); print(f'Version: {chatuvisbox.__version__}')"
```

Expected Output:
```
Package: chatuvisbox
Version: 0.1.2
```

**6.2 Test Current Entry Point**:
```bash
python -c "from chatuvisbox.__main__ import main; print('Entry point import: OK')"
```

Expected: "Entry point import: OK"

**6.3 List Package Exports**:
```bash
python -c "import chatuvisbox; print('Exports:', ', '.join(chatuvisbox.__all__))"
```

Expected Output:
```
Exports: run_graph, stream_graph, graph_app, GraphState, ConversationSession, __version__
```

### Step 7: Verify Log File Path

**Objective**: Document current log file location for comparison.

```bash
grep -n "chatuvisbox.log" src/chatuvisbox/logger.py
```

Expected: Line showing `logs/chatuvisbox.log` path.

**Check if log file exists**:
```bash
ls -lh logs/chatuvisbox.log 2>/dev/null || echo "Log file not yet created"
```

### Step 8: Create Phase 1 Completion Report

**Objective**: Document baseline state and verification results.

```bash
cat > /tmp/phase1_completion_report.txt <<EOF
=== Phase 1 Completion Report ===
Date: $(date)
Branch: $(git branch --show-current)

BASELINE TEST RESULTS:
- Quick sanity: PASS
- Unit tests (45+): PASS (0 API calls)
- Integration tests: PASS (~50 API calls)
- E2E tests: PASS (~30 API calls)

FILE INVENTORY:
- Source files: 19
- Test files: 22+
- Documentation files: 10+
- Configuration files: 5
- Total files to modify: 56+

REFERENCE COUNTS:
- Python imports: 50+
- Documentation references: 100+
- Configuration references: 10+
- Display name references: 50+
- Estimated total changes: 200+

CURRENT STATE:
- Package name: chatuvisbox
- Version: 0.1.2
- Entry point: python -m chatuvisbox
- Log file: logs/chatuvisbox.log

GIT STATUS:
- Backup branch created: backup-before-rebrand-0.1.2
- Work branch created: rebrand-to-uvisbox-assistant
- Working directory: CLEAN

TARGET STATE:
- Package name: uvisbox_assistant
- Display name: UVisBox-Assistant
- Version: 0.2.0
- Entry point: python -m uvisbox_assistant
- Log file: logs/uvisbox_assistant.log

NEXT STEPS:
- Proceed to Phase 2: Core Directory and Package Rename
- Use 'git mv' to preserve file history
- Update all internal imports in src/uvisbox_assistant/

STATUS: ✅ READY FOR PHASE 2
EOF

cat /tmp/phase1_completion_report.txt
```

## Testing Plan

### Verification Tests

**Test 1: Git Safety Net**
- Command: `git branch | grep backup-before-rebrand-0.1.2`
- Expected: Branch exists
- Purpose: Verify recovery option available

**Test 2: Baseline Functionality**
- Command: `python tests/utils/run_all_tests.py --unit`
- Expected: All tests pass
- Purpose: Confirm starting point is healthy

**Test 3: Import Verification**
- Command: `python -c "import chatuvisbox; print(chatuvisbox.__version__)"`
- Expected: "0.1.2"
- Purpose: Verify current package structure

**Test 4: Inventory Completeness**
- Command: `wc -l /tmp/rebrand_inventory.txt`
- Expected: 50+ lines
- Purpose: Verify comprehensive file list

## Success Conditions

- [ ] Git working directory is clean
- [ ] Backup branch created: `backup-before-rebrand-0.1.2`
- [ ] Work branch created: `rebrand-to-uvisbox-assistant`
- [ ] All baseline tests pass (unit/integration/e2e)
- [ ] File inventory complete (56+ files documented)
- [ ] Reference counts documented (200+ changes estimated)
- [ ] Current package imports working correctly
- [ ] Phase 1 completion report generated
- [ ] No blockers identified for Phase 2

## Integration Notes

**Inputs**:
- Current codebase at v0.1.2
- Clean git working directory
- All tests passing

**Outputs**:
- Backup branch for recovery
- Comprehensive file inventory
- Reference count documentation
- Baseline test results
- Phase 1 completion report

**Dependencies for Next Phase**:
- File inventory will guide Phase 2 directory rename
- Import patterns will guide Phase 2 internal updates
- Baseline tests will be re-run for verification

## Estimated Effort

**Time Estimate**: 30 minutes

**Breakdown**:
- Git operations: 2 minutes
- Test suite execution: 10 minutes (including rate limit delays)
- File inventory creation: 5 minutes
- Reference documentation: 8 minutes
- Verification and reporting: 5 minutes

**Complexity**: Low (documentation and verification only, no code changes)

**API Usage**: ~80 API calls (for baseline test suite)

## Recovery Notes

If issues are discovered in Phase 1:

**Issue: Tests Failing**
- Resolution: Fix tests before proceeding
- Do not start rebrand with failing tests

**Issue: Git Working Directory Dirty**
- Resolution: Commit or stash changes
- Ensure clean slate for rebrand

**Issue: Missing Dependencies**
- Resolution: Run `pip install -r requirements.txt`
- Verify UVisBox installed in conda env

**Issue: GEMINI_API_KEY Not Set**
- Resolution: Export API key in environment
- Verify with `echo $GEMINI_API_KEY`

## Phase 1 Checklist

**Pre-Phase**:
- [ ] Conda environment activated
- [ ] API key set in environment
- [ ] Current directory: `/Users/jixianli/projects/chatuvisbox`

**Git Operations**:
- [ ] Git status clean
- [ ] Backup branch created
- [ ] Work branch created

**Baseline Testing**:
- [ ] Quick sanity test passed
- [ ] Unit tests passed
- [ ] Integration tests passed
- [ ] E2E tests passed

**Inventory Creation**:
- [ ] Source files inventoried (19 files)
- [ ] Test files inventoried (22+ files)
- [ ] Documentation inventoried (10+ files)
- [ ] Configuration inventoried (5 files)

**Reference Documentation**:
- [ ] Python imports documented (50+ occurrences)
- [ ] Documentation references documented (100+ occurrences)
- [ ] Configuration references documented (10+ occurrences)
- [ ] Display name references documented (50+ occurrences)

**Verification**:
- [ ] Current imports tested
- [ ] Entry point tested
- [ ] Package exports verified
- [ ] Log file path documented

**Completion**:
- [ ] Phase 1 report generated
- [ ] No blockers identified
- [ ] Ready to proceed to Phase 2

---

**Phase 1 Status**: 📋 Ready to Execute
**Next Phase**: Phase 2 - Core Directory and Package Rename
