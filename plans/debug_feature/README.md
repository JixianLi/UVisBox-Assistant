# Debug & Verbose Mode Feature - Implementation Plan

## Overview

This feature adds comprehensive debugging capabilities to ChatUVisBox with two independent modes:

1. **Debug Mode** (`/debug on/off`) - Verbose error output with full stack traces
2. **Verbose Mode** (`/verbose on/off`) - Show/hide internal state messages

## Problem Statement

**Current Issues:**
- Vague error messages (e.g., "I can't use 'Reds' as a colormap" when Reds IS valid)
- No access to full stack traces for debugging
- Auto-fixed errors are invisible
- Internal state messages clutter normal conversation

**Goals:**
- Detailed stack traces on demand
- Error history tracking
- Clean conversation experience by default
- Powerful debugging capabilities when needed

## Mode Comparison

| Feature | Default (OFF) | Debug Mode | Verbose Mode |
|---------|---------------|------------|--------------|
| Error messages | Concise | Full traceback | Concise |
| Error history | ✅ Recorded | ✅ Recorded | ✅ Recorded |
| Internal messages | ❌ Hidden | ❌ Hidden | ✅ Shown |
| Error hints | ✅ Basic | ✅ Enhanced | ✅ Basic |
| Use case | Normal use | Error investigation | Execution debugging |

**Combinations:**
- **Both OFF** (default): Clean conversation
- **Debug ON, Verbose OFF**: See detailed errors, hide execution flow
- **Debug OFF, Verbose ON**: See execution flow, concise errors
- **Both ON**: Maximum debugging visibility

## Phase Structure

### Phase 1: Core Infrastructure (Priority: HIGH) - Week 1
- ErrorRecord class for tracking errors
- Error history in ConversationSession
- Enhanced tool error handling
- Error recording in nodes

**Files**: `phase_01_core_infrastructure.md`

### Phase 2: Verbose Mode Control (Priority: HIGH) - Week 1
- Output control utility (vprint)
- Update all internal print statements
- Session reference management

**Files**: `phase_02_verbose_mode.md`

### Phase 3: User Commands (Priority: HIGH) - Week 2
- `/debug on/off` commands
- `/verbose on/off` commands
- `/errors` - List error history
- `/trace <id>` - Show full stack trace
- Updated help text

**Files**: `phase_03_user_commands.md`

### Phase 4: Enhanced Error Messages (Priority: MEDIUM) - Week 3
- UVisBox error interpretation
- Context-aware error hints
- Colormap/method/shape error handlers

**Files**: `phase_04_enhanced_errors.md`

### Phase 5: Auto-Fix Detection (Priority: LOW) - Week 4
- Track retry attempts
- Mark auto-fixed errors
- Retroactive error updates

**Files**: `phase_05_auto_fix_detection.md`

### Phase 6: Testing (Priority: HIGH) - Week 3-4
- Unit tests (ErrorRecord, verbose mode)
- Integration tests (commands, error recording)
- Manual testing scenarios

**Files**: `phase_06_testing.md`

### Phase 7: Documentation & Version (Priority: HIGH) - Week 4
- Update all documentation (USER_GUIDE, API, CLAUDE, TESTING)
- Update CHANGELOG with v0.1.2 features
- Increment version numbers (pyproject.toml, __init__.py)
- Create release notes

**Files**: `phase_07_documentation.md`

## Implementation Timeline

```
Week 1: Phase 1 + Phase 2 (Core Infrastructure + Verbose Mode)
Week 2: Phase 3 (User Commands)
Week 3: Phase 4 + Phase 6 (Enhanced Errors + Testing)
Week 4: Phase 5 (Optional) + Phase 6 (Testing) + Phase 7 (Documentation & v0.1.2)
```

**Recommended Path** (Skip Phase 5 for MVP):
```
Week 1: Phase 1 + Phase 2
Week 2: Phase 3
Week 3: Phase 4 + Phase 6 (start)
Week 4: Phase 6 (finish) + Phase 7
```

## Success Criteria

### Debug Features
- ✅ Full stack traces available on demand
- ✅ Error history with searchable IDs
- ✅ Context-aware error hints
- ✅ Auto-fixed errors tracked

### Verbose Mode Features
- ✅ Internal messages hidden by default
- ✅ Clean conversation experience
- ✅ Debug info available on demand
- ✅ Independent from debug mode

### Quality
- ✅ < 5% performance overhead
- ✅ Backward compatible
- ✅ Comprehensive test coverage

## Quick Start

For immediate value, implement **Phase 1 + Phase 2 + Phase 3** (Weeks 1-2):
- Core error tracking
- Verbose mode control
- User-facing commands

This provides 80% of the value with minimal complexity.

For **complete release**, add Phase 6 + Phase 7 (Week 3-4):
- Comprehensive testing
- Documentation updates
- Version 0.1.2 release

## Files

- `phase_01_core_infrastructure.md` - ErrorRecord, error history, tool updates
- `phase_02_verbose_mode.md` - vprint utility, print statement updates
- `phase_03_user_commands.md` - Command handlers, help text
- `phase_04_enhanced_errors.md` - Error interpretation, hints
- `phase_05_auto_fix_detection.md` - Retry tracking, auto-fix marking (OPTIONAL)
- `phase_06_testing.md` - Unit, integration, manual tests
- `phase_07_documentation.md` - Documentation updates, v0.1.2 release

## Related Documents

- Main plan: `../detailed_debug_info_on_demand.md`
- Project instructions: `../../CLAUDE.md`
- Testing guide: `../../TESTING.md`
