# Feature: Rebrand ChatUVisBox to UVisBox-Assistant

## Summary

Comprehensive rebrand of the ChatUVisBox project to UVisBox-Assistant v0.2.0. This rebrand involves updating all package names, display names, imports, documentation, and configuration files while preserving git history and maintaining full functionality.

**Naming Convention**:
- Display name: **UVisBox-Assistant** (with hyphen for branding)
- Package name: **uvisbox_assistant** (with underscore for Python imports)
- Repository name: **uvisbox-assistant** (with hyphen for GitHub)
- Log file: `logs/uvisbox_assistant.log`
- Entry point: `python -m uvisbox_assistant`

**Version**: Bump from 0.1.2 → 0.2.0 (minor version for branding change)

**Scope**:
- 19 source files in `src/chatuvisbox/`
- 22 test files across unit/integration/e2e/interactive
- 10+ documentation files (README.md, CLAUDE.md, USER_GUIDE.md, API.md, TESTING.md, CHANGELOG.md, etc.)
- 5 configuration files (pyproject.toml, requirements.txt, setup_env.sh, main.py, create_test_data.py)
- 1 directory rename: `src/chatuvisbox/` → `src/uvisbox_assistant/`
- All import statements: `from chatuvisbox` → `from uvisbox_assistant`

**Key Design Decisions**:
1. **Clean break approach**: No backward compatibility layer (0.1.x → 0.2.0 is a major change)
2. **Git mv for directory rename**: Preserve file history during rename
3. **Systematic verification**: Run tests after each phase to catch errors early
4. **Documentation-first**: Update CHANGELOG.md with migration guide for users

## Goals

- Rename all package references from `chatuvisbox` to `uvisbox_assistant`
- Update all display names from "ChatUVisBox" to "UVisBox-Assistant"
- Maintain 100% test coverage and functionality
- Preserve git history for all renamed files
- Bump version to 0.2.0 across all files
- Create comprehensive migration documentation

## Success Criteria

- [ ] All 41 Python files updated with new package name
- [ ] All 10+ documentation files updated with new branding
- [ ] All 5 configuration files updated
- [ ] Directory renamed: `src/chatuvisbox/` → `src/uvisbox_assistant/`
- [ ] All imports working: `from uvisbox_assistant` imports succeed
- [ ] All 45+ unit tests pass (0 API calls)
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] Entry point works: `python -m uvisbox_assistant`
- [ ] Log file created at correct path: `logs/uvisbox_assistant.log`
- [ ] Version bumped to 0.2.0 in all files
- [ ] CHANGELOG.md updated with 0.2.0 migration guide
- [ ] No references to "ChatUVisBox" or "chatuvisbox" remain (except in CHANGELOG history)

## Implementation Phases

### Phase 1: Pre-Rebrand Verification and Planning
- **File**: `phases_1.md`
- **Goal**: Establish baseline, verify current state, prepare detailed change inventory
- **Status**: Planned
- **Key Activities**:
  - Run full test suite to establish baseline
  - Create comprehensive file inventory
  - Document all import patterns
  - Verify git status is clean
  - Create backup branch

### Phase 2: Core Directory and Package Rename
- **File**: `phases_2.md`
- **Goal**: Rename `src/chatuvisbox/` → `src/uvisbox_assistant/` with git history preservation
- **Status**: Planned
- **Key Activities**:
  - Use `git mv` to rename directory
  - Update all internal imports within `src/uvisbox_assistant/`
  - Update `__init__.py` and `__version__`
  - Verify package structure integrity
  - Run import validation tests

### Phase 3: Update Test Suite
- **File**: `phases_3.md`
- **Goal**: Update all test imports and references
- **Status**: Planned
- **Key Activities**:
  - Update 22 test files with new imports
  - Update test utilities and conftest.py
  - Run unit tests (0 API calls, fast feedback)
  - Fix any import errors
  - Run integration and E2E tests

### Phase 4: Update Configuration Files
- **File**: `phases_4.md`
- **Goal**: Update pyproject.toml, requirements.txt, and root scripts
- **Status**: Planned
- **Key Activities**:
  - Update pyproject.toml (name, version, scripts)
  - Update main.py and create_test_data.py
  - Update setup_env.sh
  - Verify entry point: `python -m uvisbox_assistant`
  - Test log file path

### Phase 5: Update Documentation
- **File**: `phases_5.md`
- **Goal**: Update all documentation files with new branding
- **Status**: Planned
- **Key Activities**:
  - Update CHANGELOG.md with 0.2.0 entry and migration guide
  - Update README.md (all branding and examples)
  - Update CLAUDE.md (all references and architecture notes)
  - Update USER_GUIDE.md, API.md, TESTING.md
  - Update CONTRIBUTING.md, test_data/README.md, tests/README.md

### Phase 6: Final Verification and Release Preparation
- **File**: `phases_6.md`
- **Goal**: Comprehensive testing, cleanup, and release readiness
- **Status**: Planned
- **Key Activities**:
  - Run complete test suite (unit/integration/e2e)
  - Manual smoke testing checklist
  - Search for any remaining "chatuvisbox" references
  - Verify all success criteria
  - Prepare git commit with descriptive message

## Dependencies

**Pre-requisites**:
- Clean git working directory (no uncommitted changes)
- All tests passing on current version (0.1.2)
- Backup branch created before starting

**External Dependencies**:
- None (self-contained rebrand)

**Testing Dependencies**:
- Gemini API key for integration/e2e tests
- Rate limit awareness: 30 RPM for gemini-2.0-flash-lite

## Timeline

**Estimated Total Time**: 4-6 hours

- Phase 1: Pre-Rebrand Verification - 30 minutes
- Phase 2: Core Directory Rename - 1 hour
- Phase 3: Update Test Suite - 1 hour
- Phase 4: Update Configuration - 45 minutes
- Phase 5: Update Documentation - 1.5 hours
- Phase 6: Final Verification - 1 hour

**Parallelization Opportunities**:
- Phases 3, 4, 5 can be partially parallelized after Phase 2 completes
- However, sequential execution is safer for catching cascading issues

## Risk Analysis

### High-Risk Areas

1. **Import Errors**
   - Risk: Circular imports, missing imports
   - Mitigation: Test imports immediately after Phase 2
   - Recovery: Git revert to backup branch

2. **Directory Rename**
   - Risk: Losing git history, broken paths
   - Mitigation: Use `git mv`, verify with `git log --follow`
   - Recovery: Git reset, retry with correct commands

3. **Configuration Errors**
   - Risk: Entry point not working, Poetry build failures
   - Mitigation: Test `python -m uvisbox_assistant` immediately
   - Recovery: Revert pyproject.toml, verify syntax

4. **Hidden References**
   - Risk: Hardcoded strings in unexpected places
   - Mitigation: Comprehensive grep search before/after
   - Recovery: Manual fix with targeted search

### Medium-Risk Areas

1. **Test Suite Failures**
   - Risk: Tests fail due to import or path issues
   - Mitigation: Fix unit tests first (fast feedback)
   - Recovery: Systematic debugging with verbose output

2. **Documentation Inconsistency**
   - Risk: Missed references creating confusion
   - Mitigation: Multi-pass review, grep verification
   - Recovery: Quick fixes in Phase 6

### Low-Risk Areas

1. **Log File Path**
   - Risk: Logs going to wrong location
   - Mitigation: Explicit path verification test
   - Recovery: Simple config change

2. **Version Bump**
   - Risk: Inconsistent version numbers
   - Mitigation: Grep search for "0.1.2", verify all updated
   - Recovery: Find-replace fix

## Mitigation Strategies

### Strategy 1: Incremental Verification
- Run tests after each phase completion
- Don't proceed to next phase until current phase verified
- Maintain test pass/fail log

### Strategy 2: Git Safety Net
- Create backup branch: `git checkout -b backup-before-rebrand-0.1.2`
- Make all changes in feature branch: `git checkout -b rebrand-to-uvisbox-assistant`
- Commit after each phase: enables granular rollback

### Strategy 3: Comprehensive Search
- Before starting: `grep -r "chatuvisbox" .` (document all occurrences)
- After Phase 5: `grep -r "chatuvisbox" .` (verify only CHANGELOG history remains)
- Use case-insensitive search: `grep -ri "chatuvisbox" .`

### Strategy 4: Test-Driven Verification
- Unit tests first (0 API calls, instant feedback)
- Integration tests next (verify workflows)
- E2E tests last (full system verification)
- Manual smoke test checklist for edge cases

## Notes

### Important Considerations

1. **Backward Compatibility**: This is a BREAKING change. Users on 0.1.x must migrate to 0.2.0.
2. **Repository Rename**: GitHub repo should also be renamed (separate from this plan).
3. **PyPI Package**: If published, new package name requires new PyPI registration.
4. **Import Migration**: Users must update: `from chatuvisbox` → `from uvisbox_assistant`

### Post-Rebrand Actions (Outside This Plan)

1. **GitHub Repository Rename**:
   - Rename repo: `chatuvisbox` → `uvisbox-assistant`
   - Update GitHub description and topics
   - GitHub auto-redirects old URLs

2. **PyPI Publication** (if applicable):
   - Register new package: `uvisbox-assistant`
   - Consider yanking old `chatuvisbox` versions with migration notice

3. **User Communication**:
   - GitHub release notes with migration guide
   - Update project README with prominent migration notice
   - Consider deprecation notice in 0.1.x

### Files Excluded from Rebrand

- `.git/` directory (git internals)
- `.pytest_cache/` (test cache)
- `__pycache__/` (Python bytecode)
- `temp/` (temporary runtime files)
- `logs/` (log files)
- `.vscode/` (editor settings)
- `.claude/` (Claude Code settings)
- `poetry.lock` (no manual edits, regenerate with `poetry lock`)

### Verification Commands Reference

```bash
# Find all Python imports
grep -r "from chatuvisbox" . --include="*.py"
grep -r "import chatuvisbox" . --include="*.py"

# Find all documentation references
grep -ri "chatuvisbox" . --include="*.md"

# Find all configuration references
grep -r "chatuvisbox" . --include="*.toml" --include="*.txt" --include="*.sh"

# Verify package structure
python -c "import uvisbox_assistant; print(uvisbox_assistant.__version__)"

# Verify entry point
python -m uvisbox_assistant --help

# Run test suite
python tests/utils/run_all_tests.py --unit
python tests/utils/run_all_tests.py --integration
python tests/utils/run_all_tests.py --e2e
```

## Change Statistics

**Files to Modify**:
- Source files: 19 (all in `src/chatuvisbox/`)
- Test files: 22 (across unit/integration/e2e/interactive/utils)
- Documentation: 10 (README, CLAUDE, USER_GUIDE, API, TESTING, CHANGELOG, CONTRIBUTING, etc.)
- Configuration: 5 (pyproject.toml, requirements.txt, setup_env.sh, main.py, create_test_data.py)
- **Total: 56 files**

**Directories to Rename**:
- `src/chatuvisbox/` → `src/uvisbox_assistant/` (1 directory)

**Import Statements to Update**:
- Estimated 50+ import statements across all files

**String Replacements**:
- "ChatUVisBox" → "UVisBox-Assistant" (display name)
- "chatuvisbox" → "uvisbox_assistant" (package name)
- "0.1.2" → "0.2.0" (version bump)

## Success Verification Checklist

After completing all phases, verify:

- [ ] `python -m uvisbox_assistant` launches successfully
- [ ] `python -c "import uvisbox_assistant; print(uvisbox_assistant.__version__)"` returns "0.2.0"
- [ ] Unit tests: `python tests/utils/run_all_tests.py --unit` passes
- [ ] Integration tests: `python tests/utils/run_all_tests.py --integration` passes
- [ ] E2E tests: `python tests/utils/run_all_tests.py --e2e` passes
- [ ] Log file created at: `logs/uvisbox_assistant.log`
- [ ] No "chatuvisbox" in source: `grep -r "chatuvisbox" src/ tests/` (empty or minimal)
- [ ] Git history preserved: `git log --follow src/uvisbox_assistant/__init__.py` shows history
- [ ] Documentation consistent: No "ChatUVisBox" in docs except CHANGELOG history
- [ ] Configuration working: `poetry install` succeeds (if using Poetry)
- [ ] Entry script working: `python main.py` launches REPL

## Reference Documentation

- **Python Package Naming**: PEP 8, PEP 423
- **Git mv Documentation**: `git help mv`
- **Poetry Project Structure**: https://python-poetry.org/docs/basic-usage/
- **Semantic Versioning**: https://semver.org/ (0.1.2 → 0.2.0 is minor version bump)
