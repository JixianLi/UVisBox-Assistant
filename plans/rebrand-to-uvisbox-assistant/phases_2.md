# Phase 2: Core Directory and Package Rename

## Overview

Rename the core package directory from `src/chatuvisbox/` to `src/uvisbox_assistant/` using git mv to preserve file history. Update all internal imports within the package to use the new name. This is the most critical phase as it establishes the new package structure.

## Goals

- Rename directory: `src/chatuvisbox/` → `src/uvisbox_assistant/`
- Preserve git history for all files
- Update all imports within `src/uvisbox_assistant/` to use new package name
- Update `__version__` to "0.2.0"
- Verify package structure integrity
- Verify imports work with new package name

## Prerequisites

- Phase 1 completed successfully
- All baseline tests passed
- Working on `rebrand-to-uvisbox-assistant` branch
- File inventory from Phase 1 available

## Implementation Plan

### Step 1: Rename Package Directory with Git

**Objective**: Rename directory while preserving git history.

**1.1 Perform Git Move**:
```bash
cd /Users/jixianli/projects/chatuvisbox
git mv src/chatuvisbox src/uvisbox_assistant
```

**1.2 Verify Directory Rename**:
```bash
ls -la src/
# Should show: uvisbox_assistant/ (not chatuvisbox/)

ls -la src/uvisbox_assistant/
# Should show all 19 Python files
```

**1.3 Verify Git History Preservation**:
```bash
git log --follow src/uvisbox_assistant/__init__.py | head -20
# Should show full commit history including pre-rename commits
```

**1.4 Check Git Status**:
```bash
git status
# Should show: renamed: src/chatuvisbox -> src/uvisbox_assistant
```

### Step 2: Update Package Version

**Objective**: Bump version from 0.1.2 to 0.2.0.

**2.1 Update `__init__.py`**:

File: `src/uvisbox_assistant/__init__.py`

Find and replace:
```python
# OLD
__version__ = "0.1.2"

# NEW
__version__ = "0.2.0"
```

Also update imports in `__init__.py`:
```python
# OLD
from chatuvisbox.graph import run_graph, stream_graph, graph_app
from chatuvisbox.state import GraphState
from chatuvisbox.conversation import ConversationSession

# NEW
from uvisbox_assistant.graph import run_graph, stream_graph, graph_app
from uvisbox_assistant.state import GraphState
from uvisbox_assistant.conversation import ConversationSession
```

**2.2 Verify Version**:
```bash
python -c "import sys; sys.path.insert(0, 'src'); import uvisbox_assistant; print(uvisbox_assistant.__version__)"
# Expected: 0.2.0
```

### Step 3: Update All Internal Imports in Source Files

**Objective**: Update every `from chatuvisbox` import to `from uvisbox_assistant`.

**3.1 List All Files with Imports**:
```bash
grep -l "from chatuvisbox" src/uvisbox_assistant/*.py
```

Expected files (19 total):
- `__init__.py` ✓ (done in Step 2)
- `conversation.py`
- `graph.py`
- `model.py`
- `nodes.py`
- `routing.py`
- `utils.py`
- `vis_tools.py`
- `data_tools.py`
- `hybrid_control.py`
- `logger.py`

**3.2 Update Each File Systematically**:

For each file, use find-replace pattern:
- Find: `from chatuvisbox`
- Replace: `from uvisbox_assistant`

**File: `src/uvisbox_assistant/conversation.py`** (10 imports):
```python
# OLD
from chatuvisbox.state import GraphState, create_initial_state
from chatuvisbox.graph import graph_app
from chatuvisbox.hybrid_control import execute_simple_command, is_hybrid_eligible
from chatuvisbox.error_tracking import ErrorRecord
from chatuvisbox.output_control import set_session, vprint
from chatuvisbox.error_interpretation import interpret_uvisbox_error, format_error_with_hint

# NEW
from uvisbox_assistant.state import GraphState, create_initial_state
from uvisbox_assistant.graph import graph_app
from uvisbox_assistant.hybrid_control import execute_simple_command, is_hybrid_eligible
from uvisbox_assistant.error_tracking import ErrorRecord
from uvisbox_assistant.output_control import set_session, vprint
from uvisbox_assistant.error_interpretation import interpret_uvisbox_error, format_error_with_hint
```

**File: `src/uvisbox_assistant/graph.py`** (3 imports):
```python
# OLD
from chatuvisbox.state import GraphState
from chatuvisbox.nodes import call_model, call_data_tool, call_vis_tool
from chatuvisbox.routing import route_after_model, route_after_tool

# NEW
from uvisbox_assistant.state import GraphState
from uvisbox_assistant.nodes import call_model, call_data_tool, call_vis_tool
from uvisbox_assistant.routing import route_after_model, route_after_tool
```

**File: `src/uvisbox_assistant/model.py`** (1 import):
```python
# OLD
from chatuvisbox import config

# NEW
from uvisbox_assistant import config
```

**File: `src/uvisbox_assistant/nodes.py`** (7 imports):
```python
# OLD
from chatuvisbox.state import GraphState, update_state_with_data, update_state_with_vis, increment_error_count
from chatuvisbox.model import create_model_with_tools, prepare_messages_for_model
from chatuvisbox.data_tools import DATA_TOOLS, DATA_TOOL_SCHEMAS
from chatuvisbox.vis_tools import VIS_TOOLS, VIS_TOOL_SCHEMAS
from chatuvisbox import config
from chatuvisbox.logger import log_tool_call, log_tool_result, log_error
from chatuvisbox.output_control import vprint

# NEW
from uvisbox_assistant.state import GraphState, update_state_with_data, update_state_with_vis, increment_error_count
from uvisbox_assistant.model import create_model_with_tools, prepare_messages_for_model
from uvisbox_assistant.data_tools import DATA_TOOLS, DATA_TOOL_SCHEMAS
from uvisbox_assistant.vis_tools import VIS_TOOLS, VIS_TOOL_SCHEMAS
from uvisbox_assistant import config
from uvisbox_assistant.logger import log_tool_call, log_tool_result, log_error
from uvisbox_assistant.output_control import vprint
```

**File: `src/uvisbox_assistant/routing.py`** (2 imports):
```python
# OLD
from chatuvisbox.state import GraphState
from chatuvisbox.utils import get_tool_type

# NEW
from uvisbox_assistant.state import GraphState
from uvisbox_assistant.utils import get_tool_type
```

**File: `src/uvisbox_assistant/utils.py`** (1 import):
```python
# OLD
from chatuvisbox import config

# NEW
from uvisbox_assistant import config
```

**File: `src/uvisbox_assistant/vis_tools.py`** (1 import):
```python
# OLD
from chatuvisbox import config

# NEW
from uvisbox_assistant import config
```

**File: `src/uvisbox_assistant/data_tools.py`** (1 import):
```python
# OLD
from chatuvisbox import config

# NEW
from uvisbox_assistant import config
```

**File: `src/uvisbox_assistant/hybrid_control.py`** (3 imports):
```python
# OLD
from chatuvisbox.command_parser import parse_simple_command, apply_command_to_params
from chatuvisbox.vis_tools import VIS_TOOLS
from chatuvisbox.output_control import vprint

# NEW
from uvisbox_assistant.command_parser import parse_simple_command, apply_command_to_params
from uvisbox_assistant.vis_tools import VIS_TOOLS
from uvisbox_assistant.output_control import vprint
```

**File: `src/uvisbox_assistant/logger.py`** (1 import):
```python
# OLD
from chatuvisbox import config

# NEW
from uvisbox_assistant import config
```

**3.3 Verify All Imports Updated**:
```bash
# This should return ZERO results:
grep -n "from chatuvisbox" src/uvisbox_assistant/*.py

# If any results appear, update those files manually
```

### Step 4: Update Log File Path in Logger

**Objective**: Change log file path from `chatuvisbox.log` to `uvisbox_assistant.log`.

**File: `src/uvisbox_assistant/logger.py`**

Find and update log filename:
```python
# OLD (approximate, verify actual code)
LOG_FILE = config.BASE_DIR / "logs" / "chatuvisbox.log"

# NEW
LOG_FILE = config.BASE_DIR / "logs" / "uvisbox_assistant.log"
```

**Verify**:
```bash
grep -n "uvisbox_assistant.log" src/uvisbox_assistant/logger.py
# Should show the updated log path
```

### Step 5: Update Docstrings and Comments

**Objective**: Update any "ChatUVisBox" or "chatuvisbox" in docstrings.

**5.1 Find Docstring References**:
```bash
grep -n "ChatUVisBox\|chatuvisbox" src/uvisbox_assistant/*.py
```

**5.2 Update Package Docstring in `__init__.py`**:
```python
# OLD
"""
ChatUVisBox: Natural language interface for UVisBox uncertainty visualization.

A LangGraph-based conversational agent that translates natural language requests
into data processing and visualization operations using the UVisBox library.
"""

# NEW
"""
UVisBox-Assistant: Natural language interface for UVisBox uncertainty visualization.

A LangGraph-based conversational agent that translates natural language requests
into data processing and visualization operations using the UVisBox library.
"""
```

**5.3 Update Any Other Docstrings**:
Review all files for docstring updates. Common locations:
- Module-level docstrings
- Class docstrings
- Function docstrings with package references

### Step 6: Verify Package Structure

**Objective**: Ensure new package structure is valid.

**6.1 Test Import**:
```bash
python -c "import sys; sys.path.insert(0, 'src'); import uvisbox_assistant; print('Import: OK'); print(f'Version: {uvisbox_assistant.__version__}')"
```

Expected Output:
```
Import: OK
Version: 0.2.0
```

**6.2 Test Package Exports**:
```bash
python -c "import sys; sys.path.insert(0, 'src'); import uvisbox_assistant; print('Exports:', ', '.join(uvisbox_assistant.__all__))"
```

Expected Output:
```
Exports: run_graph, stream_graph, graph_app, GraphState, ConversationSession, __version__
```

**6.3 Test Individual Module Imports**:
```bash
python -c "import sys; sys.path.insert(0, 'src'); from uvisbox_assistant.conversation import ConversationSession; print('ConversationSession: OK')"
python -c "import sys; sys.path.insert(0, 'src'); from uvisbox_assistant.graph import graph_app; print('graph_app: OK')"
python -c "import sys; sys.path.insert(0, 'src'); from uvisbox_assistant.vis_tools import VIS_TOOLS; print('VIS_TOOLS: OK')"
python -c "import sys; sys.path.insert(0, 'src'); from uvisbox_assistant.data_tools import DATA_TOOLS; print('DATA_TOOLS: OK')"
```

Expected: All print "OK".

### Step 7: Check for Circular Imports

**Objective**: Ensure no circular import issues introduced.

```bash
python -c "import sys; sys.path.insert(0, 'src'); import uvisbox_assistant; from uvisbox_assistant import *; print('No circular imports detected')"
```

Expected: No ImportError exceptions.

### Step 8: Commit Phase 2 Changes

**Objective**: Save progress with descriptive commit.

**8.1 Review Changes**:
```bash
git status
git diff src/uvisbox_assistant/
```

**8.2 Stage Changes**:
```bash
git add src/
```

**8.3 Commit with Message**:
```bash
git commit -m "Phase 2: Rename package chatuvisbox → uvisbox_assistant

- Renamed directory: src/chatuvisbox/ → src/uvisbox_assistant/
- Updated all internal imports to use uvisbox_assistant
- Bumped version: 0.1.2 → 0.2.0
- Updated log file path: logs/uvisbox_assistant.log
- Updated package docstring: ChatUVisBox → UVisBox-Assistant
- Preserved git history with 'git mv'

Files modified: 19 source files in src/uvisbox_assistant/"
```

**8.4 Verify Commit**:
```bash
git log -1 --stat
```

### Step 9: Create Phase 2 Completion Report

**Objective**: Document Phase 2 results for verification.

```bash
cat > /tmp/phase2_completion_report.txt <<EOF
=== Phase 2 Completion Report ===
Date: $(date)
Branch: $(git branch --show-current)

DIRECTORY RENAME:
- Old path: src/chatuvisbox/
- New path: src/uvisbox_assistant/
- Git history: PRESERVED (verified with 'git log --follow')
- Files renamed: 19

VERSION UPDATE:
- Old version: 0.1.2
- New version: 0.2.0
- Location: src/uvisbox_assistant/__init__.py

IMPORT UPDATES:
- Files updated: 11 (with internal imports)
- Total import statements updated: ~30
- Remaining "from chatuvisbox" in src/: 0 (verified with grep)

LOG FILE PATH:
- Old path: logs/chatuvisbox.log
- New path: logs/uvisbox_assistant.log
- Location: src/uvisbox_assistant/logger.py

DOCSTRING UPDATES:
- Package docstring updated: ChatUVisBox → UVisBox-Assistant
- Module-level docstrings reviewed and updated

VERIFICATION:
- Package import: ✅ PASS
- Version check: ✅ 0.2.0
- Export verification: ✅ PASS (all 6 exports)
- Module imports: ✅ PASS (ConversationSession, graph_app, tools)
- Circular imports: ✅ PASS (none detected)
- Git history: ✅ PRESERVED

COMMIT:
- Commit created: YES
- Commit message: "Phase 2: Rename package chatuvisbox → uvisbox_assistant"

NEXT STEPS:
- Proceed to Phase 3: Update Test Suite
- Update 22+ test files with new imports
- Run unit tests for immediate feedback

STATUS: ✅ PHASE 2 COMPLETE
EOF

cat /tmp/phase2_completion_report.txt
```

## Testing Plan

### Import Verification Tests

**Test 1: Basic Package Import**
```bash
python -c "import sys; sys.path.insert(0, 'src'); import uvisbox_assistant; print(uvisbox_assistant.__version__)"
```
- Expected: "0.2.0"
- Purpose: Verify package imports under new name

**Test 2: Version Verification**
```bash
python -c "import sys; sys.path.insert(0, 'src'); import uvisbox_assistant; assert uvisbox_assistant.__version__ == '0.2.0', 'Version mismatch'"
```
- Expected: No assertion error
- Purpose: Confirm version bump

**Test 3: Export Completeness**
```bash
python -c "import sys; sys.path.insert(0, 'src'); import uvisbox_assistant; expected = {'run_graph', 'stream_graph', 'graph_app', 'GraphState', 'ConversationSession', '__version__'}; actual = set(uvisbox_assistant.__all__); assert expected == actual, f'Export mismatch: {actual}'"
```
- Expected: No assertion error
- Purpose: Verify __all__ exports unchanged

**Test 4: No Old Imports Remain**
```bash
grep -r "from chatuvisbox" src/uvisbox_assistant/ || echo "✓ No old imports found"
```
- Expected: "✓ No old imports found"
- Purpose: Verify all imports updated

**Test 5: Git History Preserved**
```bash
git log --follow --oneline src/uvisbox_assistant/__init__.py | wc -l
```
- Expected: Multiple commits (5+)
- Purpose: Verify git history intact

## Success Conditions

- [ ] Directory renamed: `src/uvisbox_assistant/` exists
- [ ] Old directory gone: `src/chatuvisbox/` does not exist
- [ ] Git history preserved: `git log --follow` shows full history
- [ ] Version updated to "0.2.0" in `__init__.py`
- [ ] All internal imports updated (0 "from chatuvisbox" in src/)
- [ ] Log file path updated to `logs/uvisbox_assistant.log`
- [ ] Package docstring updated to "UVisBox-Assistant"
- [ ] Package imports successfully: `import uvisbox_assistant` works
- [ ] Version check passes: `uvisbox_assistant.__version__ == "0.2.0"`
- [ ] All exports intact: 6 items in `__all__`
- [ ] Module imports work: ConversationSession, graph_app, tools
- [ ] No circular imports detected
- [ ] Changes committed to git
- [ ] Phase 2 completion report generated

## Integration Notes

**Inputs from Phase 1**:
- File inventory (19 source files)
- Import patterns documentation
- Baseline test results

**Outputs for Phase 3**:
- Renamed package directory
- Updated internal imports
- New version 0.2.0
- Verified package structure

**Breaking Changes**:
- Package name changed (cannot import `chatuvisbox` anymore)
- Log file location changed
- Version bumped to 0.2.0

**Preserved**:
- Git commit history
- File contents (except imports and version)
- Package functionality
- API surface (exports unchanged)

## Estimated Effort

**Time Estimate**: 1 hour

**Breakdown**:
- Git mv operation: 2 minutes
- Version update: 3 minutes
- Import updates (11 files): 25 minutes
- Log path update: 5 minutes
- Docstring updates: 10 minutes
- Verification tests: 10 minutes
- Git commit: 3 minutes
- Reporting: 2 minutes

**Complexity**: Medium (systematic but requires careful verification)

**API Usage**: 0 API calls (no integration tests run yet)

## Recovery Notes

If issues are discovered in Phase 2:

**Issue: Import Errors**
- Resolution: Check for typos in import statements
- Verify: `grep -r "from uvisbox_assistant" src/`
- Recovery: Fix imports, re-test

**Issue: Circular Imports**
- Resolution: Review import order in modules
- Check: dependency graph (who imports whom)
- Recovery: Reorder imports, use lazy imports if needed

**Issue: Git History Lost**
- Resolution: Should NOT happen with `git mv`
- Verification: `git log --follow <file>`
- Recovery: `git reset --hard HEAD~1`, retry with correct `git mv`

**Issue: Version Not Updated**
- Resolution: Edit `__init__.py`, update `__version__`
- Verify: `python -c "import sys; sys.path.insert(0, 'src'); import uvisbox_assistant; print(uvisbox_assistant.__version__)"`

## Phase 2 Checklist

**Directory Operations**:
- [ ] `git mv src/chatuvisbox src/uvisbox_assistant` executed
- [ ] Directory rename verified with `ls`
- [ ] Git history verified with `git log --follow`

**Version Update**:
- [ ] `__version__` changed to "0.2.0"
- [ ] Version verified with import test

**Import Updates** (11 files):
- [ ] `__init__.py` (3 imports + version)
- [ ] `conversation.py` (6 imports)
- [ ] `graph.py` (3 imports)
- [ ] `model.py` (1 import)
- [ ] `nodes.py` (7 imports)
- [ ] `routing.py` (2 imports)
- [ ] `utils.py` (1 import)
- [ ] `vis_tools.py` (1 import)
- [ ] `data_tools.py` (1 import)
- [ ] `hybrid_control.py` (3 imports)
- [ ] `logger.py` (1 import + log path)

**Docstring Updates**:
- [ ] Package docstring in `__init__.py`
- [ ] Other docstrings reviewed

**Verification Tests**:
- [ ] Basic import test passed
- [ ] Version verification passed
- [ ] Export completeness passed
- [ ] No old imports remain
- [ ] Git history preserved
- [ ] Module imports work
- [ ] No circular imports

**Git Operations**:
- [ ] Changes staged
- [ ] Commit created with descriptive message
- [ ] Commit verified with `git log -1 --stat`

**Reporting**:
- [ ] Phase 2 completion report generated
- [ ] No blockers identified for Phase 3

---

**Phase 2 Status**: 📋 Ready to Execute
**Next Phase**: Phase 3 - Update Test Suite
