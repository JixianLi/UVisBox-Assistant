# v0.3.3 Bug Fixes Design

**Date:** 2025-11-05
**Version:** v0.3.3
**Type:** Bug fixes

## Problem Statement

### Bug #1: /errors Command Not Showing Tool Errors

**Issue**: When VIS TOOL (or other tools) encounter errors, the `/errors` command reports "No errors in this session".

**Root Cause**: Tool errors with `_error_details` are lost during ToolMessage serialization. The flow is:
1. Tool returns error dict with `_error_details` containing Exception objects
2. nodes.py creates ToolMessage with `content=str(result)` - stringifies the dict
3. conversation.py's `_process_tool_errors()` tries to parse stringified dict
4. `ast.literal_eval()` fails because Exception objects can't be parsed from strings
5. Exception is caught and silently ignored

**User Impact**: Users can't see error history or use `/trace <id>` to debug issues.

### Bug #2: CSV Files Cannot Be Loaded

**Issue**: Loading CSV files fails with error: "Object arrays cannot be loaded when allow_pickle=False"

**Root Cause**: All data loading code uses `np.load()` which only works for `.npy` binary format. When given a CSV file, numpy tries to read it as binary and fails.

**User Impact**: Users can only use pre-converted .npy files, cannot load common CSV/TXT data formats.

## Design Goals

1. **Fix error recording** - All tool errors should appear in `/errors` command
2. **Support multiple formats** - Load .npy, .csv, and .txt files seamlessly
3. **Maintain backward compatibility** - Existing .npy loading must continue working
4. **Clear error messages** - When loading fails, explain what went wrong

## Detailed Design

### Bug #1 Fix: Recording Errors Before Serialization

**Approach**: Record errors immediately in `nodes.py` after tool execution, before ToolMessage creation.

**Why this works**: Captures error information while it's still in dict form with accessible Exception objects, before stringification loses the structure.

#### Changes to `conversation.py`

**Add global session accessor**:
```python
_current_session = None

def set_session(session):
    """Set the current session for global access."""
    global _current_session
    _current_session = session

def get_current_session():
    """Get the current session for error recording."""
    return _current_session
```

**Remove obsolete code**:
- Remove `_process_tool_errors()` method (lines 123-175)
- Remove call to `_process_tool_errors()` from `send()` method (line 119)

**Note**: `set_session()` already exists at line 45, just need to add `get_current_session()`.

#### Changes to `nodes.py`

Add error recording pattern to all 4 tool-calling nodes:

**Pattern to add after tool execution**:
```python
# After: result = tool_func(**tool_args)

# Check for errors and record immediately
if result.get("status") == "error" and "_error_details" in result:
    from uvisbox_assistant.session.conversation import get_current_session
    session = get_current_session()
    if session:
        error_details = result["_error_details"]
        session.record_error(
            tool_name=tool_name,
            error=error_details["exception"],
            traceback_str=error_details["traceback"],
            user_message=result.get("message", str(error_details["exception"])),
            auto_fixed=False
        )
```

**Locations to apply**:
1. `call_vis_tool()` - After line ~155 (after tool execution)
2. `call_data_tool()` - After line ~245 (after tool execution)
3. `call_statistics_tool()` - After line ~325 (after tool execution)
4. `call_analyzer_tool()` - After line ~445 (after tool execution)

### Bug #2 Fix: Multi-Format Data Loading

**Approach**: Create unified `load_array()` helper that detects file type and uses appropriate loader.

**Supported formats**:
- `.npy` - Binary numpy format (via `np.load()`)
- `.csv` - Comma-separated values (via `np.loadtxt()`)
- `.txt` - Space/tab delimited (via `np.loadtxt()` with auto-detect)

**Error handling**: Strict validation with clear error messages (as chosen in brainstorming).

#### New File: `src/uvisbox_assistant/utils/data_loading.py`

```python
"""Unified data loading utilities for multiple file formats."""

import numpy as np
from pathlib import Path
from typing import Tuple


def load_array(filepath: str) -> Tuple[bool, np.ndarray, str]:
    """
    Load numpy array from various file formats.

    Supports:
    - .npy: Binary numpy format
    - .csv: Comma-separated values
    - .txt: Space/tab delimited text

    Args:
        filepath: Path to data file

    Returns:
        Tuple of (success, array, error_message)
        - success: True if loaded successfully
        - array: Loaded numpy array (None if failed)
        - error_message: Error description (empty string if success)

    Examples:
        >>> success, data, error = load_array("curves.npy")
        >>> if success:
        ...     print(f"Loaded shape: {data.shape}")

        >>> success, data, error = load_array("data.csv")
        >>> if not success:
        ...     print(f"Failed: {error}")
    """
    path = Path(filepath)
    suffix = path.suffix.lower()

    try:
        if suffix == '.npy':
            array = np.load(filepath)
        elif suffix in ['.csv', '.txt']:
            # Auto-detect delimiter (comma, space, or tab)
            # delimiter=None tells numpy to auto-detect
            array = np.loadtxt(filepath, delimiter=None)
        else:
            return False, None, f"Unsupported file format: {suffix}. Supported: .npy, .csv, .txt"

        return True, array, ""

    except Exception as e:
        return False, None, f"Error loading {suffix} file: {str(e)}"
```

#### Changes to Tool Files

Replace all `np.load(data_path)` calls with `load_array()` pattern:

**Old code**:
```python
curves = np.load(data_path)
```

**New code**:
```python
from uvisbox_assistant.utils.data_loading import load_array

success, curves, error_msg = load_array(data_path)
if not success:
    return {"status": "error", "message": error_msg}
```

**Files to update**:

1. **`src/uvisbox_assistant/tools/vis_tools.py`** (6 locations):
   - `plot_functional_boxplot()` - line 64
   - `plot_uncertainty_lobes()` - line 193
   - `plot_contour_boxplot()` - line 306
   - `plot_uncertainty_treemap()` - line 388 (vectors)
   - `plot_uncertainty_treemap()` - line 389 (positions)
   - `plot_squid_glyph()` - line 484 (vectors)
   - `plot_squid_glyph()` - line 485 (positions)
   - `plot_contour_boxplot()` - line 594

2. **`src/uvisbox_assistant/tools/statistics_tools.py`** (1 location):
   - `compute_functional_boxplot_statistics()` - line 283

3. **`src/uvisbox_assistant/tools/data_tools.py`** (1 location):
   - `load_data()` - line 262

## Implementation Plan

### Phase 1: Bug #1 - Error Recording Fix

1. Add `get_current_session()` to conversation.py
2. Add error recording to `call_vis_tool()` in nodes.py
3. Add error recording to `call_data_tool()` in nodes.py
4. Add error recording to `call_statistics_tool()` in nodes.py
5. Add error recording to `call_analyzer_tool()` in nodes.py
6. Remove `_process_tool_errors()` method and its call
7. Test `/errors` command shows tool errors

### Phase 2: Bug #2 - Multi-Format Loading

1. Create `src/uvisbox_assistant/utils/data_loading.py` with `load_array()`
2. Update `vis_tools.py` - replace all 8 `np.load()` calls
3. Update `statistics_tools.py` - replace 1 `np.load()` call
4. Update `data_tools.py` - replace 1 `np.load()` call
5. Test CSV loading with user's ar2_harmonic_timeseries.csv file
6. Test existing .npy files still work

### Phase 3: Testing

1. Write unit tests for `load_array()` (.npy, .csv, .txt)
2. Write integration test for `/errors` command
3. Write integration test for CSV loading workflow
4. Run full test suite to ensure no regressions

### Phase 4: Documentation

1. Update CHANGELOG.md for v0.3.3
2. Update version in pyproject.toml
3. Commit and tag release

## Testing Strategy

### Unit Tests

**New test file: `tests/unit/test_data_loading.py`**
- Test `load_array()` with .npy file (existing behavior)
- Test `load_array()` with .csv file (comma-delimited)
- Test `load_array()` with .txt file (space-delimited)
- Test `load_array()` with unsupported format (.json)
- Test `load_array()` with malformed file

### Integration Tests

**Error recording test**:
```python
def test_errors_command_shows_tool_errors():
    """Test that /errors command shows VIS TOOL errors."""
    session = ConversationSession()

    # Trigger a VIS TOOL error
    session.send("plot functional boxplot with data_path='nonexistent.npy'")

    # Check error was recorded
    assert len(session.error_history) > 0
    assert session.error_history[-1].tool_name == "plot_functional_boxplot"
```

**CSV loading test**:
```python
def test_load_csv_and_plot():
    """Test loading CSV file and creating visualization."""
    session = ConversationSession()

    # Load CSV file
    csv_path = "test_data/ar2_harmonic_timeseries.csv"
    session.send(f"Load {csv_path} and plot functional boxplot")

    # Should succeed
    assert session.state["current_data_path"] is not None
    assert ".npy" in session.state["current_data_path"]  # Should be converted
```

### Regression Tests

- Run full test suite: `poetry run pytest tests/ --ignore=tests/e2e/`
- Verify all existing .npy loading still works
- Verify no new test failures introduced

## Success Criteria

1. ✅ `/errors` command shows VIS TOOL errors with full details
2. ✅ `/trace <id>` works for tool errors
3. ✅ CSV files can be loaded via "load X.csv" commands
4. ✅ TXT files with space/tab delimiters work
5. ✅ Existing .npy files continue to work
6. ✅ Clear error messages for unsupported formats
7. ✅ All existing tests pass
8. ✅ New tests cover both bug fixes

## Breaking Changes

None - these are pure bug fixes that restore expected behavior.

## Future Enhancements

- Support .npz (compressed numpy arrays)
- Support pandas-compatible formats (.parquet, .hdf5)
- Auto-conversion caching (don't regenerate .npy from same CSV)
- Progress indication for large CSV files
