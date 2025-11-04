# Phase 1: Foundation and State Extension

## Overview

Establish the foundation for uncertainty analysis by extending GraphState with new fields, creating the statistics_tools.py module structure, and setting up the UVisBox interface for functional_boxplot_summary_statistics(). This phase ensures minimal disruption to existing code while preparing infrastructure for statistical analysis.

## Goals

- Extend GraphState with four new optional fields for analysis state
- Create statistics_tools.py with initial structure and tool registry
- Define tool schemas for LLM binding
- Set up comprehensive unit tests (0 API calls)
- Verify backward compatibility with existing tests

## Prerequisites

- UVisBox library installed in conda environment
- Access to functional_boxplot_summary_statistics() function
- Existing codebase at v0.2.0

## Implementation Plan

### Step 1: Extend GraphState Schema

**File**: `src/uvisbox_assistant/state.py`

Add new fields to GraphState TypedDict (after existing fields):

```python
class GraphState(TypedDict):
    """
    State for the UVisBox-Assistant conversation graph.

    Attributes:
        messages: List of conversation messages (user, assistant, tool messages)
        current_data_path: Path to the most recently created/loaded .npy data file
        last_vis_params: Parameters used in the last visualization call (for hybrid control)
        session_files: List of temporary files created during this session
        error_count: Number of consecutive errors (for circuit breaking)
        tool_execution_sequence: List of tool execution records for auto-fix detection
        last_error_tool: Name of tool that last failed (for auto-fix detection)
        last_error_id: ID of last error (for auto-fix detection)

        # NEW: Uncertainty analysis fields (v0.3.0)
        raw_statistics: Raw output from functional_boxplot_summary_statistics (numpy arrays)
        processed_statistics: LLM-friendly structured summary from statistics_tool
        analysis_report: Generated text report from analyzer_tool
        analysis_type: Report format - "inline" | "quick" | "detailed" | None
    """
    # Existing fields (unchanged)
    messages: Annotated[List[BaseMessage], operator.add]
    current_data_path: Optional[str]
    last_vis_params: Optional[dict]
    session_files: List[str]
    error_count: int
    tool_execution_sequence: List[Dict]
    last_error_tool: Optional[str]
    last_error_id: Optional[int]

    # NEW: Uncertainty analysis state
    raw_statistics: Optional[dict]
    processed_statistics: Optional[dict]
    analysis_report: Optional[str]
    analysis_type: Optional[str]
```

Update `create_initial_state()` to initialize new fields:

```python
def create_initial_state(user_message: str) -> GraphState:
    """
    Create the initial state for a new conversation turn.

    Args:
        user_message: The user's input message

    Returns:
        Initial GraphState
    """
    from langchain_core.messages import HumanMessage

    return GraphState(
        messages=[HumanMessage(content=user_message)],
        current_data_path=None,
        last_vis_params=None,
        session_files=[],
        error_count=0,
        tool_execution_sequence=[],
        last_error_tool=None,
        last_error_id=None,
        # NEW: Initialize analysis state
        raw_statistics=None,
        processed_statistics=None,
        analysis_report=None,
        analysis_type=None
    )
```

Add new state update helper functions:

```python
def update_state_with_statistics(state: GraphState, raw_stats: dict, processed_stats: dict) -> dict:
    """
    Update state after successful statistics tool execution.

    Args:
        state: Current graph state
        raw_stats: Raw output from functional_boxplot_summary_statistics (numpy arrays)
        processed_stats: Processed LLM-friendly summary

    Returns:
        Dict of updates to merge into state
    """
    return {
        "raw_statistics": raw_stats,
        "processed_statistics": processed_stats,
        "error_count": 0  # Reset error count on success
    }


def update_state_with_analysis(state: GraphState, report: str, analysis_type: str) -> dict:
    """
    Update state after successful analyzer tool execution.

    Args:
        state: Current graph state
        report: Generated text report
        analysis_type: Type of report ("inline" | "quick" | "detailed")

    Returns:
        Dict of updates to merge into state
    """
    return {
        "analysis_report": report,
        "analysis_type": analysis_type,
        "error_count": 0  # Reset error count on success
    }
```

### Step 2: Create statistics_tools.py Module

**File**: `src/uvisbox_assistant/statistics_tools.py`

Create initial module structure with UVisBox imports and tool registry:

```python
"""Statistical analysis tools for uncertainty quantification."""

import numpy as np
import traceback
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from scipy import stats
from sklearn.metrics import pairwise_distances

# UVisBox import
try:
    from uvisbox.Modules import functional_boxplot_summary_statistics
except ImportError as e:
    print(f"Warning: UVisBox statistics function import failed: {e}")
    print("Make sure UVisBox is installed with statistics support")


def compute_functional_boxplot_statistics(
    data_path: str,
    method: str = "fbd"
) -> Dict:
    """
    Compute functional boxplot summary statistics and process into LLM-friendly format.

    This tool:
    1. Calls UVisBox functional_boxplot_summary_statistics()
    2. Analyzes median curve behavior (trend, fluctuation, smoothness, range)
    3. Analyzes percentile band behavior (widths, variation regions, gaps)
    4. Analyzes outlier behavior (count, similarity to median)
    5. Returns structured dict suitable for LLM consumption (no numpy arrays)

    Args:
        data_path: Path to .npy file with shape (n_curves, n_points)
        method: Band depth method - 'fbd' or 'mfbd' (default: 'fbd')

    Returns:
        Dict with:
        - status: "success" or "error"
        - message: User-friendly message
        - statistics_summary: Structured dict with numeric summaries
        - _raw_statistics: Original UVisBox output (for debugging)
    """
    try:
        # Implementation will be in Phase 2
        # Placeholder for Phase 1
        return {
            "status": "error",
            "message": "Statistics tool not yet implemented (Phase 2)"
        }

    except Exception as e:
        tb_str = traceback.format_exc()
        return {
            "status": "error",
            "message": f"Error computing statistics: {str(e)}",
            "_error_details": {
                "exception": e,
                "traceback": tb_str
            }
        }


# Tool registry (similar to DATA_TOOLS and VIS_TOOLS)
STATISTICS_TOOLS = {
    "compute_functional_boxplot_statistics": compute_functional_boxplot_statistics,
}


# Tool schemas for LLM binding
STATISTICS_TOOL_SCHEMAS = [
    {
        "name": "compute_functional_boxplot_statistics",
        "description": (
            "Compute summary statistics for functional boxplot data including "
            "median behavior, percentile band characteristics, and outlier analysis. "
            "Use this when user requests uncertainty analysis or data summary."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "data_path": {
                    "type": "string",
                    "description": "Path to .npy file containing curve ensemble data"
                },
                "method": {
                    "type": "string",
                    "description": "Band depth method: 'fbd' (functional band depth) or 'mfbd' (modified functional band depth)",
                    "enum": ["fbd", "mfbd"],
                    "default": "fbd"
                }
            },
            "required": ["data_path"]
        }
    }
]
```

### Step 3: Create analyzer_tools.py Module

**File**: `src/uvisbox_assistant/analyzer_tools.py`

Create initial module structure with LLM setup:

```python
"""LLM-powered uncertainty analysis and report generation."""

import traceback
from typing import Dict, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from uvisbox_assistant import config
from uvisbox_assistant.model import create_model_with_tools


def generate_uncertainty_report(
    statistics_summary: dict,
    analysis_type: str = "quick"
) -> Dict:
    """
    Generate natural language uncertainty analysis report.

    Uses LLM to interpret statistical summaries and generate reports in three formats:
    - inline: 1 sentence summary of uncertainty level
    - quick: 3-5 sentence overview
    - detailed: Full report with median, band, and outlier analysis

    Args:
        statistics_summary: Structured dict from statistics_tool
        analysis_type: "inline" | "quick" | "detailed" (default: "quick")

    Returns:
        Dict with:
        - status: "success" or "error"
        - message: User-friendly confirmation
        - report: Generated text report
        - analysis_type: Echo of requested type
    """
    try:
        # Implementation will be in Phase 3
        # Placeholder for Phase 1
        return {
            "status": "error",
            "message": "Analyzer tool not yet implemented (Phase 3)"
        }

    except Exception as e:
        tb_str = traceback.format_exc()
        return {
            "status": "error",
            "message": f"Error generating report: {str(e)}",
            "_error_details": {
                "exception": e,
                "traceback": tb_str
            }
        }


# Tool registry
ANALYZER_TOOLS = {
    "generate_uncertainty_report": generate_uncertainty_report,
}


# Tool schemas for LLM binding
ANALYZER_TOOL_SCHEMAS = [
    {
        "name": "generate_uncertainty_report",
        "description": (
            "Generate a natural language uncertainty analysis report from statistical summaries. "
            "Use this after compute_functional_boxplot_statistics to create text-based analysis."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "statistics_summary": {
                    "type": "object",
                    "description": "Structured statistical summary from statistics tool"
                },
                "analysis_type": {
                    "type": "string",
                    "description": "Report format",
                    "enum": ["inline", "quick", "detailed"],
                    "default": "quick"
                }
            },
            "required": ["statistics_summary"]
        }
    }
]
```

### Step 4: Update Package Exports

**File**: `src/uvisbox_assistant/__init__.py`

Add new modules to exports if they're exported (check current pattern):

```python
# Existing exports...

# NEW: Statistics and analyzer tools (v0.3.0)
from uvisbox_assistant.statistics_tools import STATISTICS_TOOLS, STATISTICS_TOOL_SCHEMAS
from uvisbox_assistant.analyzer_tools import ANALYZER_TOOLS, ANALYZER_TOOL_SCHEMAS
```

## Testing Plan

### Unit Tests

**File**: `tests/unit/test_statistics_tools.py`

```python
"""Unit tests for statistics_tools module (0 API calls)."""

import pytest
import numpy as np
from pathlib import Path
from uvisbox_assistant.statistics_tools import (
    STATISTICS_TOOLS,
    STATISTICS_TOOL_SCHEMAS,
    compute_functional_boxplot_statistics
)


class TestStatisticsToolRegistry:
    """Test tool registry structure."""

    def test_statistics_tools_registry_exists(self):
        """Verify STATISTICS_TOOLS dict exists."""
        assert isinstance(STATISTICS_TOOLS, dict)
        assert len(STATISTICS_TOOLS) > 0

    def test_compute_statistics_in_registry(self):
        """Verify compute_functional_boxplot_statistics is registered."""
        assert "compute_functional_boxplot_statistics" in STATISTICS_TOOLS
        assert callable(STATISTICS_TOOLS["compute_functional_boxplot_statistics"])


class TestStatisticsToolSchemas:
    """Test tool schemas for LLM binding."""

    def test_schemas_list_exists(self):
        """Verify STATISTICS_TOOL_SCHEMAS is a list."""
        assert isinstance(STATISTICS_TOOL_SCHEMAS, list)
        assert len(STATISTICS_TOOL_SCHEMAS) > 0

    def test_compute_statistics_schema(self):
        """Verify compute_functional_boxplot_statistics schema."""
        schema = STATISTICS_TOOL_SCHEMAS[0]
        assert schema["name"] == "compute_functional_boxplot_statistics"
        assert "description" in schema
        assert "parameters" in schema

        params = schema["parameters"]["properties"]
        assert "data_path" in params
        assert "method" in params

        # Verify required fields
        assert "data_path" in schema["parameters"]["required"]


class TestComputeStatisticsPlaceholder:
    """Test placeholder implementation (Phase 1)."""

    def test_returns_not_implemented_error(self, tmp_path):
        """Verify placeholder returns error message."""
        # Create dummy data file
        data = np.random.randn(30, 100)
        data_path = tmp_path / "test_curves.npy"
        np.save(data_path, data)

        result = compute_functional_boxplot_statistics(str(data_path))

        assert result["status"] == "error"
        assert "not yet implemented" in result["message"].lower()
```

**File**: `tests/unit/test_analyzer_tools.py`

```python
"""Unit tests for analyzer_tools module (0 API calls)."""

import pytest
from uvisbox_assistant.analyzer_tools import (
    ANALYZER_TOOLS,
    ANALYZER_TOOL_SCHEMAS,
    generate_uncertainty_report
)


class TestAnalyzerToolRegistry:
    """Test tool registry structure."""

    def test_analyzer_tools_registry_exists(self):
        """Verify ANALYZER_TOOLS dict exists."""
        assert isinstance(ANALYZER_TOOLS, dict)
        assert len(ANALYZER_TOOLS) > 0

    def test_generate_report_in_registry(self):
        """Verify generate_uncertainty_report is registered."""
        assert "generate_uncertainty_report" in ANALYZER_TOOLS
        assert callable(ANALYZER_TOOLS["generate_uncertainty_report"])


class TestAnalyzerToolSchemas:
    """Test tool schemas for LLM binding."""

    def test_schemas_list_exists(self):
        """Verify ANALYZER_TOOL_SCHEMAS is a list."""
        assert isinstance(ANALYZER_TOOL_SCHEMAS, list)
        assert len(ANALYZER_TOOL_SCHEMAS) > 0

    def test_generate_report_schema(self):
        """Verify generate_uncertainty_report schema."""
        schema = ANALYZER_TOOL_SCHEMAS[0]
        assert schema["name"] == "generate_uncertainty_report"
        assert "description" in schema
        assert "parameters" in schema

        params = schema["parameters"]["properties"]
        assert "statistics_summary" in params
        assert "analysis_type" in params

        # Verify enum values
        assert "inline" in params["analysis_type"]["enum"]
        assert "quick" in params["analysis_type"]["enum"]
        assert "detailed" in params["analysis_type"]["enum"]


class TestGenerateReportPlaceholder:
    """Test placeholder implementation (Phase 1)."""

    def test_returns_not_implemented_error(self):
        """Verify placeholder returns error message."""
        dummy_summary = {
            "median": {"trend": "increasing"},
            "bands": {},
            "outliers": {"count": 0}
        }

        result = generate_uncertainty_report(dummy_summary, "quick")

        assert result["status"] == "error"
        assert "not yet implemented" in result["message"].lower()
```

**File**: `tests/unit/test_state_extensions.py`

```python
"""Unit tests for GraphState extensions (0 API calls)."""

import pytest
from uvisbox_assistant.state import (
    GraphState,
    create_initial_state,
    update_state_with_statistics,
    update_state_with_analysis
)


class TestGraphStateExtensions:
    """Test new GraphState fields."""

    def test_initial_state_has_analysis_fields(self):
        """Verify initial state includes analysis fields."""
        state = create_initial_state("test message")

        # Check new fields exist and are None
        assert "raw_statistics" in state
        assert state["raw_statistics"] is None

        assert "processed_statistics" in state
        assert state["processed_statistics"] is None

        assert "analysis_report" in state
        assert state["analysis_report"] is None

        assert "analysis_type" in state
        assert state["analysis_type"] is None

    def test_initial_state_preserves_existing_fields(self):
        """Verify existing fields still present."""
        state = create_initial_state("test message")

        # Existing fields
        assert "messages" in state
        assert "current_data_path" in state
        assert "last_vis_params" in state
        assert "session_files" in state
        assert "error_count" in state


class TestStatisticsStateUpdate:
    """Test update_state_with_statistics helper."""

    def test_updates_statistics_fields(self):
        """Verify statistics state update."""
        state = create_initial_state("test")

        raw_stats = {"depth": [0.1, 0.2], "median": [1.0, 2.0]}
        processed_stats = {"median_trend": "increasing"}

        updates = update_state_with_statistics(state, raw_stats, processed_stats)

        assert updates["raw_statistics"] == raw_stats
        assert updates["processed_statistics"] == processed_stats
        assert updates["error_count"] == 0

    def test_resets_error_count(self):
        """Verify error count reset."""
        state = create_initial_state("test")
        state["error_count"] = 3

        updates = update_state_with_statistics(state, {}, {})
        assert updates["error_count"] == 0


class TestAnalysisStateUpdate:
    """Test update_state_with_analysis helper."""

    def test_updates_analysis_fields(self):
        """Verify analysis state update."""
        state = create_initial_state("test")

        report = "This ensemble shows moderate uncertainty."
        analysis_type = "quick"

        updates = update_state_with_analysis(state, report, analysis_type)

        assert updates["analysis_report"] == report
        assert updates["analysis_type"] == analysis_type
        assert updates["error_count"] == 0

    def test_resets_error_count(self):
        """Verify error count reset."""
        state = create_initial_state("test")
        state["error_count"] = 2

        updates = update_state_with_analysis(state, "report", "inline")
        assert updates["error_count"] == 0
```

### Backward Compatibility Tests

Run existing test suite to verify no regressions:

```bash
# All existing unit tests should pass
python tests/utils/run_all_tests.py --unit

# Verify no import errors
python -c "from uvisbox_assistant import state, statistics_tools, analyzer_tools"
```

## Success Conditions

- [ ] GraphState extended with 4 new optional fields
- [ ] create_initial_state() initializes all new fields to None
- [ ] update_state_with_statistics() helper function created and tested
- [ ] update_state_with_analysis() helper function created and tested
- [ ] statistics_tools.py created with placeholder implementation
- [ ] analyzer_tools.py created with placeholder implementation
- [ ] STATISTICS_TOOLS and STATISTICS_TOOL_SCHEMAS defined
- [ ] ANALYZER_TOOLS and ANALYZER_TOOL_SCHEMAS defined
- [ ] 15+ new unit tests pass (0 API calls)
- [ ] All existing unit tests still pass
- [ ] No breaking changes to existing code

## Integration Notes

### State Field Usage

**raw_statistics**: Stores raw numpy arrays and data from UVisBox function. Used for internal processing, not passed to LLM.

**processed_statistics**: LLM-friendly structured dict with numeric summaries. No numpy arrays. Passed to analyzer_tool.

**analysis_report**: Final text output from analyzer_tool. Shown to user.

**analysis_type**: Tracks which report format was requested. Used for logging and context.

### Error Handling Pattern

Both new tools follow existing error handling pattern:
- Return dict with `{"status": "error"|"success", "message": "...", ...}`
- Include `_error_details` dict with exception and traceback
- Node wrappers (Phase 4) will handle error recovery

### Tool Schema Pattern

Follows existing pattern from data_tools.py and vis_tools.py:
- `name`: Tool function name (matches registry key)
- `description`: Clear description for LLM to understand when to use
- `parameters`: JSON Schema with type, description, defaults, enums
- `required`: List of required parameter names

## Estimated Effort

**Development**: 1.5 hours
- State extension: 30 minutes
- Module creation: 45 minutes
- Tool schemas: 15 minutes

**Testing**: 1 hour
- Unit test writing: 45 minutes
- Backward compatibility verification: 15 minutes

**Total**: 2-3 hours (including buffer for debugging)
