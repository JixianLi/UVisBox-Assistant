# v0.3.3 Bug Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix two critical bugs: (1) /errors command not showing tool errors, (2) CSV files cannot be loaded.

**Architecture:** Bug #1 solved by recording errors in nodes.py before serialization. Bug #2 solved by creating unified load_array() helper that detects file format and uses appropriate numpy loader.

**Tech Stack:** Python 3.13, LangGraph, numpy

---

## Phase 1: Bug #1 - Error Recording Fix

### Task 1.1: Add get_current_session() Helper

**Files:**
- Modify: `src/uvisbox_assistant/session/conversation.py:45-46`

**Step 1: Write the failing test**

File: `tests/unit/test_conversation.py`

```python
def test_get_current_session():
    """Test global session accessor."""
    from uvisbox_assistant.session.conversation import get_current_session, ConversationSession

    # Initially None
    session = get_current_session()
    assert session is None

    # After creating session, should be accessible
    new_session = ConversationSession()
    session = get_current_session()
    assert session is new_session
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest tests/unit/test_conversation.py::test_get_current_session -v`

Expected: `ImportError: cannot import name 'get_current_session'`

**Step 3: Add get_current_session() function**

File: `src/uvisbox_assistant/session/conversation.py`

After line 46 (after `set_session()` function), add:

```python
def get_current_session():
    """Get the current session for error recording."""
    return _current_session
```

**Step 4: Run test to verify it passes**

Run: `poetry run pytest tests/unit/test_conversation.py::test_get_current_session -v`

Expected: PASS (1 passed)

**Step 5: Commit**

```bash
git add src/uvisbox_assistant/session/conversation.py tests/unit/test_conversation.py
git commit -m "feat: add get_current_session() helper for error recording"
```

---

### Task 1.2: Add Error Recording to call_vis_tool()

**Files:**
- Modify: `src/uvisbox_assistant/core/nodes.py:155-160`

**Step 1: Write the failing integration test**

File: `tests/integration/test_error_recording.py` (NEW)

```python
"""Integration tests for error recording in tool nodes."""

import pytest
from uvisbox_assistant.session.conversation import ConversationSession


def test_vis_tool_errors_recorded():
    """Test that VIS TOOL errors are recorded in error history."""
    session = ConversationSession()

    # Trigger VIS TOOL error with nonexistent file
    session.send("plot functional boxplot with data_path='nonexistent.npy'")

    # Check error was recorded
    assert len(session.error_history) > 0, "No errors recorded"

    # Verify error details
    error = session.error_history[-1]
    assert "plot_functional_boxplot" in error.tool_name
    assert "FileNotFoundError" in error.error_type or "not found" in error.error_message.lower()
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest tests/integration/test_error_recording.py::test_vis_tool_errors_recorded -v`

Expected: FAIL with "No errors recorded" assertion

**Step 3: Add error recording to call_vis_tool()**

File: `src/uvisbox_assistant/core/nodes.py`

After line ~155 (after `result = vis_func(**filtered_params)`), add:

```python
        # Check for errors and record immediately (before serialization)
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

**Step 4: Run test to verify it passes**

Run: `poetry run pytest tests/integration/test_error_recording.py::test_vis_tool_errors_recorded -v`

Expected: PASS (1 passed)

**Step 5: Commit**

```bash
git add src/uvisbox_assistant/core/nodes.py tests/integration/test_error_recording.py
git commit -m "feat: record VIS TOOL errors before serialization"
```

---

### Task 1.3: Add Error Recording to call_data_tool()

**Files:**
- Modify: `src/uvisbox_assistant/core/nodes.py:245-250`

**Step 1: Write the failing test**

File: `tests/integration/test_error_recording.py`

Add:

```python
def test_data_tool_errors_recorded():
    """Test that DATA TOOL errors are recorded in error history."""
    session = ConversationSession()

    # Trigger DATA TOOL error with invalid parameters
    session.send("generate 0 curves")  # Invalid: must be > 0

    # Check error was recorded
    assert len(session.error_history) > 0, "No errors recorded"

    # Verify error details
    error = session.error_history[-1]
    assert "generate_ar2_curves" in error.tool_name or "DATA TOOL" in error.tool_name.upper()
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest tests/integration/test_error_recording.py::test_data_tool_errors_recorded -v`

Expected: FAIL with "No errors recorded" assertion

**Step 3: Add error recording to call_data_tool()**

File: `src/uvisbox_assistant/core/nodes.py`

After line ~245 (after `result = tool_func(**tool_args)`), add the same pattern:

```python
        # Check for errors and record immediately (before serialization)
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

**Step 4: Run test to verify it passes**

Run: `poetry run pytest tests/integration/test_error_recording.py::test_data_tool_errors_recorded -v`

Expected: PASS (1 passed)

**Step 5: Commit**

```bash
git add src/uvisbox_assistant/core/nodes.py tests/integration/test_error_recording.py
git commit -m "feat: record DATA TOOL errors before serialization"
```

---

### Task 1.4: Add Error Recording to call_statistics_tool()

**Files:**
- Modify: `src/uvisbox_assistant/core/nodes.py:325-330`

**Step 1: Write the failing test**

File: `tests/integration/test_error_recording.py`

Add:

```python
def test_statistics_tool_errors_recorded():
    """Test that STATISTICS TOOL errors are recorded in error history."""
    session = ConversationSession()

    # Trigger STATISTICS TOOL error with nonexistent file
    session.send("compute statistics for nonexistent.npy")

    # Check error was recorded
    assert len(session.error_history) > 0, "No errors recorded"

    # Verify error details
    error = session.error_history[-1]
    assert "compute_functional_boxplot_statistics" in error.tool_name
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest tests/integration/test_error_recording.py::test_statistics_tool_errors_recorded -v`

Expected: FAIL with "No errors recorded" assertion

**Step 3: Add error recording to call_statistics_tool()**

File: `src/uvisbox_assistant/core/nodes.py`

After line ~325 (after `result = tool_func(**tool_args)`), add:

```python
        # Check for errors and record immediately (before serialization)
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

**Step 4: Run test to verify it passes**

Run: `poetry run pytest tests/integration/test_error_recording.py::test_statistics_tool_errors_recorded -v`

Expected: PASS (1 passed)

**Step 5: Commit**

```bash
git add src/uvisbox_assistant/core/nodes.py tests/integration/test_error_recording.py
git commit -m "feat: record STATISTICS TOOL errors before serialization"
```

---

### Task 1.5: Add Error Recording to call_analyzer_tool()

**Files:**
- Modify: `src/uvisbox_assistant/core/nodes.py:445-450`

**Step 1: Write the failing test**

File: `tests/integration/test_error_recording.py`

Add:

```python
def test_analyzer_tool_errors_recorded():
    """Test that ANALYZER TOOL errors are recorded in error history."""
    session = ConversationSession()

    # Trigger ANALYZER TOOL error by calling without statistics
    session.send("generate uncertainty report")

    # Check error was recorded
    assert len(session.error_history) > 0, "No errors recorded"

    # Verify error details
    error = session.error_history[-1]
    assert "generate_uncertainty_report" in error.tool_name
    assert "statistics" in error.error_message.lower()
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest tests/integration/test_error_recording.py::test_analyzer_tool_errors_recorded -v`

Expected: FAIL with "No errors recorded" assertion

**Step 3: Add error recording to call_analyzer_tool()**

File: `src/uvisbox_assistant/core/nodes.py`

After line ~445 (after `result = tool_func(**tool_args)`), add:

```python
        # Check for errors and record immediately (before serialization)
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

**Step 4: Run test to verify it passes**

Run: `poetry run pytest tests/integration/test_error_recording.py::test_analyzer_tool_errors_recorded -v`

Expected: PASS (1 passed)

**Step 5: Commit**

```bash
git add src/uvisbox_assistant/core/nodes.py tests/integration/test_error_recording.py
git commit -m "feat: record ANALYZER TOOL errors before serialization"
```

---

### Task 1.6: Remove Obsolete _process_tool_errors() Method

**Files:**
- Modify: `src/uvisbox_assistant/session/conversation.py:119,123-175`

**Step 1: Verify all tests still pass**

Run: `poetry run pytest tests/integration/test_error_recording.py -v`

Expected: ALL 4 tests pass (error recording now happens in nodes.py)

**Step 2: Remove call to _process_tool_errors()**

File: `src/uvisbox_assistant/session/conversation.py`

Delete line ~119:
```python
# DELETE THIS LINE:
self._process_tool_errors()
```

**Step 3: Remove _process_tool_errors() method**

File: `src/uvisbox_assistant/session/conversation.py`

Delete lines ~123-175 (entire method):
```python
# DELETE THIS ENTIRE METHOD:
def _process_tool_errors(self):
    """Process tool messages to detect and record errors."""
    # ... (delete all content)
```

**Step 4: Run tests to verify nothing broke**

Run: `poetry run pytest tests/integration/test_error_recording.py -v`

Expected: ALL 4 tests still pass

Run: `poetry run pytest tests/unit/test_conversation.py -v`

Expected: All conversation tests pass

**Step 5: Commit**

```bash
git add src/uvisbox_assistant/session/conversation.py
git commit -m "refactor: remove obsolete _process_tool_errors() method

Error recording now happens in nodes.py before serialization,
making post-hoc parsing unnecessary."
```

---

## Phase 2: Bug #2 - Multi-Format Loading

### Task 2.1: Create load_array() Helper with Tests

**Files:**
- Create: `src/uvisbox_assistant/utils/data_loading.py`
- Create: `tests/unit/test_data_loading.py`

**Step 1: Write the failing tests**

File: `tests/unit/test_data_loading.py` (NEW)

```python
"""Unit tests for data loading utilities."""

import numpy as np
import pytest
from pathlib import Path
from uvisbox_assistant.utils.data_loading import load_array


def test_load_npy_file(tmp_path):
    """Test loading .npy binary file."""
    # Create test .npy file
    test_data = np.array([[1, 2, 3], [4, 5, 6]])
    npy_file = tmp_path / "test.npy"
    np.save(npy_file, test_data)

    # Load it
    success, array, error = load_array(str(npy_file))

    # Verify
    assert success is True
    assert error == ""
    assert np.array_equal(array, test_data)


def test_load_csv_file(tmp_path):
    """Test loading .csv file with comma delimiter."""
    # Create test .csv file
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("1,2,3\n4,5,6\n")

    # Load it
    success, array, error = load_array(str(csv_file))

    # Verify
    assert success is True
    assert error == ""
    expected = np.array([[1, 2, 3], [4, 5, 6]])
    assert np.array_equal(array, expected)


def test_load_txt_file_space_delimited(tmp_path):
    """Test loading .txt file with space delimiter."""
    # Create test .txt file
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("1 2 3\n4 5 6\n")

    # Load it
    success, array, error = load_array(str(txt_file))

    # Verify
    assert success is True
    assert error == ""
    expected = np.array([[1, 2, 3], [4, 5, 6]])
    assert np.array_equal(array, expected)


def test_unsupported_format(tmp_path):
    """Test error for unsupported file format."""
    # Create .json file
    json_file = tmp_path / "test.json"
    json_file.write_text('{"data": [1, 2, 3]}')

    # Try to load it
    success, array, error = load_array(str(json_file))

    # Verify error
    assert success is False
    assert array is None
    assert "Unsupported file format" in error
    assert ".json" in error


def test_malformed_csv(tmp_path):
    """Test error for malformed CSV file."""
    # Create malformed .csv file
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text("1,2,3\ninvalid,data\n")

    # Try to load it
    success, array, error = load_array(str(csv_file))

    # Verify error
    assert success is False
    assert array is None
    assert "Error loading" in error
```

**Step 2: Run tests to verify they fail**

Run: `poetry run pytest tests/unit/test_data_loading.py -v`

Expected: `ImportError: cannot import name 'load_array'`

**Step 3: Create load_array() implementation**

File: `src/uvisbox_assistant/utils/data_loading.py` (NEW)

```python
"""Unified data loading utilities for multiple file formats."""

import numpy as np
from pathlib import Path
from typing import Tuple, Optional


def load_array(filepath: str) -> Tuple[bool, Optional[np.ndarray], str]:
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

**Step 4: Run tests to verify they pass**

Run: `poetry run pytest tests/unit/test_data_loading.py -v`

Expected: PASS (5 passed)

**Step 5: Commit**

```bash
git add src/uvisbox_assistant/utils/data_loading.py tests/unit/test_data_loading.py
git commit -m "feat: add load_array() helper for multi-format data loading

Supports .npy, .csv, and .txt files with automatic delimiter detection.
Includes comprehensive unit tests."
```

---

### Task 2.2: Update vis_tools.py - plot_functional_boxplot()

**Files:**
- Modify: `src/uvisbox_assistant/tools/vis_tools.py:64`

**Step 1: Write the failing integration test**

File: `tests/integration/test_csv_loading.py` (NEW)

```python
"""Integration tests for CSV file loading."""

import pytest
import numpy as np
from pathlib import Path
from uvisbox_assistant.session.conversation import ConversationSession


@pytest.fixture
def csv_file(tmp_path):
    """Create a test CSV file."""
    csv_path = tmp_path / "test_curves.csv"
    # Create 5 curves with 10 points each
    data = np.random.randn(5, 10)
    np.savetxt(csv_path, data, delimiter=',')
    return csv_path


def test_load_csv_and_plot_functional_boxplot(csv_file):
    """Test loading CSV file and plotting functional boxplot."""
    session = ConversationSession()

    # Send command to plot CSV file
    response = session.send(f"plot functional boxplot with data_path='{csv_file}'")

    # Should succeed (no errors)
    assert len(session.error_history) == 0, f"Errors occurred: {session.error_history}"

    # Check that visualization was created
    assert session.state.get("last_vis_params") is not None
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest tests/integration/test_csv_loading.py::test_load_csv_and_plot_functional_boxplot -v`

Expected: FAIL with pickle error or assertion failure

**Step 3: Update plot_functional_boxplot() to use load_array()**

File: `src/uvisbox_assistant/tools/vis_tools.py`

Replace line ~64:
```python
# OLD:
curves = np.load(data_path)

# NEW:
from uvisbox_assistant.utils.data_loading import load_array

success, curves, error_msg = load_array(data_path)
if not success:
    return {"status": "error", "message": error_msg}
```

**Step 4: Run test to verify it passes**

Run: `poetry run pytest tests/integration/test_csv_loading.py::test_load_csv_and_plot_functional_boxplot -v`

Expected: PASS (1 passed)

**Step 5: Commit**

```bash
git add src/uvisbox_assistant/tools/vis_tools.py tests/integration/test_csv_loading.py
git commit -m "feat: support CSV/TXT loading in plot_functional_boxplot"
```

---

### Task 2.3: Update vis_tools.py - plot_uncertainty_lobes()

**Files:**
- Modify: `src/uvisbox_assistant/tools/vis_tools.py:193`

**Step 1: Update plot_uncertainty_lobes() to use load_array()**

File: `src/uvisbox_assistant/tools/vis_tools.py`

Replace line ~193:
```python
# OLD:
curves = np.load(data_path)

# NEW:
from uvisbox_assistant.utils.data_loading import load_array

success, curves, error_msg = load_array(data_path)
if not success:
    return {"status": "error", "message": error_msg}
```

**Step 2: Test with existing tests**

Run: `poetry run pytest tests/integration/test_tool_interfaces.py::TestUncertaintyLobesInterface -v`

Expected: All tests pass

**Step 3: Commit**

```bash
git add src/uvisbox_assistant/tools/vis_tools.py
git commit -m "feat: support CSV/TXT loading in plot_uncertainty_lobes"
```

---

### Task 2.4: Update vis_tools.py - plot_contour_boxplot() (line 306)

**Files:**
- Modify: `src/uvisbox_assistant/tools/vis_tools.py:306`

**Step 1: Update plot_contour_boxplot() to use load_array()**

File: `src/uvisbox_assistant/tools/vis_tools.py`

Replace line ~306:
```python
# OLD:
field = np.load(data_path)

# NEW:
from uvisbox_assistant.utils.data_loading import load_array

success, field, error_msg = load_array(data_path)
if not success:
    return {"status": "error", "message": error_msg}
```

**Step 2: Test with existing tests**

Run: `poetry run pytest tests/integration/test_tool_interfaces.py::TestContourBoxplotInterface -v`

Expected: All tests pass

**Step 3: Commit**

```bash
git add src/uvisbox_assistant/tools/vis_tools.py
git commit -m "feat: support CSV/TXT loading in plot_contour_boxplot (line 306)"
```

---

### Task 2.5: Update vis_tools.py - plot_uncertainty_treemap()

**Files:**
- Modify: `src/uvisbox_assistant/tools/vis_tools.py:388-389`

**Step 1: Update plot_uncertainty_treemap() to use load_array()**

File: `src/uvisbox_assistant/tools/vis_tools.py`

Replace lines ~388-389:
```python
# OLD:
vectors = np.load(vectors_path)
positions = np.load(positions_path)

# NEW:
from uvisbox_assistant.utils.data_loading import load_array

success, vectors, error_msg = load_array(vectors_path)
if not success:
    return {"status": "error", "message": f"Vectors: {error_msg}"}

success, positions, error_msg = load_array(positions_path)
if not success:
    return {"status": "error", "message": f"Positions: {error_msg}"}
```

**Step 2: Test with existing tests**

Run: `poetry run pytest tests/integration/test_tool_interfaces.py::TestUncertaintyTreemapInterface -v`

Expected: All tests pass

**Step 3: Commit**

```bash
git add src/uvisbox_assistant/tools/vis_tools.py
git commit -m "feat: support CSV/TXT loading in plot_uncertainty_treemap"
```

---

### Task 2.6: Update vis_tools.py - plot_squid_glyph()

**Files:**
- Modify: `src/uvisbox_assistant/tools/vis_tools.py:484-485`

**Step 1: Update plot_squid_glyph() to use load_array()**

File: `src/uvisbox_assistant/tools/vis_tools.py`

Replace lines ~484-485:
```python
# OLD:
vectors = np.load(vectors_path)
positions = np.load(positions_path)

# NEW:
from uvisbox_assistant.utils.data_loading import load_array

success, vectors, error_msg = load_array(vectors_path)
if not success:
    return {"status": "error", "message": f"Vectors: {error_msg}"}

success, positions, error_msg = load_array(positions_path)
if not success:
    return {"status": "error", "message": f"Positions: {error_msg}"}
```

**Step 2: Test with existing tests**

Run: `poetry run pytest tests/integration/test_tool_interfaces.py::TestSquidGlyphInterface -v`

Expected: All tests pass

**Step 3: Commit**

```bash
git add src/uvisbox_assistant/tools/vis_tools.py
git commit -m "feat: support CSV/TXT loading in plot_squid_glyph"
```

---

### Task 2.7: Update vis_tools.py - plot_contour_boxplot() (line 594)

**Files:**
- Modify: `src/uvisbox_assistant/tools/vis_tools.py:594`

**Step 1: Update second plot_contour_boxplot() occurrence**

File: `src/uvisbox_assistant/tools/vis_tools.py`

Replace line ~594:
```python
# OLD:
data = np.load(data_path)

# NEW:
from uvisbox_assistant.utils.data_loading import load_array

success, data, error_msg = load_array(data_path)
if not success:
    return {"status": "error", "message": error_msg}
```

**Step 2: Test with existing tests**

Run: `poetry run pytest tests/integration/test_tool_interfaces.py::TestContourBoxplotInterface -v`

Expected: All tests pass

**Step 3: Commit**

```bash
git add src/uvisbox_assistant/tools/vis_tools.py
git commit -m "feat: support CSV/TXT loading in plot_contour_boxplot (line 594)"
```

---

### Task 2.8: Update statistics_tools.py

**Files:**
- Modify: `src/uvisbox_assistant/tools/statistics_tools.py:283`

**Step 1: Update compute_functional_boxplot_statistics() to use load_array()**

File: `src/uvisbox_assistant/tools/statistics_tools.py`

Replace line ~283:
```python
# OLD:
curves = np.load(data_path)

# NEW:
from uvisbox_assistant.utils.data_loading import load_array

success, curves, error_msg = load_array(data_path)
if not success:
    return {"status": "error", "message": error_msg}
```

**Step 2: Test with existing tests**

Run: `poetry run pytest tests/unit/test_statistics_tools.py -v`

Expected: All tests pass

**Step 3: Commit**

```bash
git add src/uvisbox_assistant/tools/statistics_tools.py
git commit -m "feat: support CSV/TXT loading in compute_functional_boxplot_statistics"
```

---

### Task 2.9: Update data_tools.py

**Files:**
- Modify: `src/uvisbox_assistant/tools/data_tools.py:262`

**Step 1: Update load_data() to use load_array()**

File: `src/uvisbox_assistant/tools/data_tools.py`

Replace line ~262:
```python
# OLD:
data = np.load(filepath)

# NEW:
from uvisbox_assistant.utils.data_loading import load_array

success, data, error_msg = load_array(filepath)
if not success:
    return {"status": "error", "message": error_msg}
```

**Step 2: Test with existing tests**

Run: `poetry run pytest tests/unit/test_tools.py::test_load_data -v`

Expected: Test passes

**Step 3: Commit**

```bash
git add src/uvisbox_assistant/tools/data_tools.py
git commit -m "feat: support CSV/TXT loading in load_data tool"
```

---

## Phase 3: End-to-End Testing

### Task 3.1: Test User's CSV File

**Files:**
- None (manual testing)

**Step 1: Test loading user's ar2_harmonic_timeseries.csv**

Run the main application and test:

```bash
cd /Users/jixianli/projects/uvisbox-assistant/.worktrees/v0.3.3-bug-fixes
poetry run python -m uvisbox_assistant.main
```

Commands to test:
1. `load /Users/jixianli/projects/uvisbox-assistant/test_data/ar2_harmonic_timeseries.csv`
2. `plot functional boxplot`
3. `/errors` (should show no errors)

Expected: CSV loads successfully, boxplot is created, no errors

**Step 2: Test error recording**

Commands to test:
1. `plot functional boxplot with data_path='nonexistent.npy'`
2. `/errors` (should show the error)
3. `/trace last` (should show full traceback)

Expected: Error is recorded and visible in `/errors` command

**Step 3: Document results**

Create file: `docs/testing/v0.3.3-manual-test-results.md`

```markdown
# v0.3.3 Manual Testing Results

**Date:** 2025-11-05
**Tester:** [Name]

## Bug #1: Error Recording

**Test**: Trigger VIS TOOL error and check `/errors`
- Command: `plot functional boxplot with data_path='nonexistent.npy'`
- Result: ✅/❌ Error shown in `/errors`
- Details: [Any notes]

## Bug #2: CSV Loading

**Test**: Load user's CSV file
- File: `/Users/jixianli/projects/uvisbox-assistant/test_data/ar2_harmonic_timeseries.csv`
- Command: `load [path] and plot functional boxplot`
- Result: ✅/❌ CSV loaded and plotted
- Details: [Any notes]
```

**Step 4: Commit test results**

```bash
git add docs/testing/v0.3.3-manual-test-results.md
git commit -m "test: document v0.3.3 manual testing results"
```

---

### Task 3.2: Run Full Test Suite

**Files:**
- None (verification)

**Step 1: Run all unit tests**

Run: `poetry run pytest tests/unit/ -v`

Expected: All unit tests pass (including new tests)

**Step 2: Run all integration tests**

Run: `poetry run pytest tests/integration/ -v`

Expected: All integration tests pass

**Step 3: Run full suite**

Run: `poetry run pytest tests/ --ignore=tests/e2e/ -v`

Expected: All tests pass (or same 4 pre-existing failures as baseline)

**Step 4: Document any failures**

If any NEW failures occur, document in:
`docs/testing/v0.3.3-test-failures.md`

---

## Phase 4: Documentation and Release

### Task 4.1: Update CHANGELOG

**Files:**
- Modify: `CHANGELOG.md`

**Step 1: Add v0.3.3 entry**

File: `CHANGELOG.md`

Add at the top:

```markdown
## [0.3.3] - 2025-11-05

### Fixed
- **Bug #1**: `/errors` command now correctly shows tool errors that occur during execution
  - Error recording happens before ToolMessage serialization to preserve Exception objects
  - Affects all tool types: VIS, DATA, STATISTICS, ANALYZER
- **Bug #2**: CSV and TXT files can now be loaded for visualization and analysis
  - New `load_array()` helper supports .npy, .csv, and .txt formats
  - Automatic delimiter detection for CSV/TXT files
  - Clear error messages for unsupported formats

### Technical Details
- Added `get_current_session()` helper for global session access in nodes
- Error recording moved from `conversation.py` to `nodes.py` (before serialization)
- Created `src/uvisbox_assistant/utils/data_loading.py` module
- Updated 8 tool functions to use unified `load_array()` helper
```

**Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for v0.3.3"
```

---

### Task 4.2: Update Version

**Files:**
- Modify: `pyproject.toml:3`

**Step 1: Bump version**

File: `pyproject.toml`

Change line 3:
```toml
# OLD:
version = "0.3.2"

# NEW:
version = "0.3.3"
```

**Step 2: Commit**

```bash
git add pyproject.toml
git commit -m "chore: bump version to 0.3.3"
```

---

## Summary

**Total tasks:** 16 tasks across 4 phases

**Time estimate:** 2-3 hours total
- Phase 1 (Bug #1): 45 minutes (6 tasks)
- Phase 2 (Bug #2): 60 minutes (9 tasks)
- Phase 3 (Testing): 20 minutes (2 tasks)
- Phase 4 (Docs): 10 minutes (2 tasks)

**Key commits:** 17 commits (one per task + final version bump)

**Success criteria:**
- ✅ All 4 error recording tests pass
- ✅ All 5 load_array() tests pass
- ✅ CSV integration test passes
- ✅ User's ar2_harmonic_timeseries.csv loads successfully
- ✅ `/errors` command shows tool errors
- ✅ No new test failures
- ✅ Version bumped to 0.3.3
