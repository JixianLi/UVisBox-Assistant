# Phase 4: Graph Integration and Routing

## Overview

Integrate statistics and analyzer tools into the LangGraph workflow by creating new node functions, updating routing logic to support multi-path workflows, and modifying the graph structure to handle sequential tool execution (data → statistics → analyzer). This is the most critical phase requiring careful attention to backward compatibility.

## Goals

- Create call_statistics_tool and call_analyzer_tool node functions
- Update route_after_model to recognize new tool types
- Extend graph structure to support new nodes
- Maintain backward compatibility with existing workflows
- Implement comprehensive routing tests

## Prerequisites

- Phase 1 completed (GraphState extended)
- Phase 2 completed (statistics_tools.py functional)
- Phase 3 completed (analyzer_tools.py functional)
- Understanding of existing routing logic and graph structure

## Implementation Plan

### Step 1: Create Statistics Tool Node

**File**: `src/uvisbox_assistant/nodes.py`

Add new node function after existing call_vis_tool:

```python
def call_statistics_tool(state: GraphState) -> Dict:
    """
    Node that executes a statistics tool.

    Args:
        state: Current graph state

    Returns:
        Dict with tool result message and state updates
    """
    last_message = state["messages"][-1]

    # Extract tool call
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        raise ValueError("call_statistics_tool invoked but no tool_calls in last message")

    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    tool_call_id = tool_call["id"]

    vprint(f"[STATISTICS TOOL] Calling {tool_name} with args: {tool_args}")
    log_tool_call(tool_name, tool_args)

    # Track execution start
    execution_entry = {
        "tool_name": tool_name,
        "timestamp": datetime.now(),
        "status": None,
        "error_id": None
    }

    # Execute tool with error handling
    try:
        # Import statistics tools
        from uvisbox_assistant.statistics_tools import STATISTICS_TOOLS

        if tool_name not in STATISTICS_TOOLS:
            result = {
                "status": "error",
                "message": f"Unknown statistics tool: {tool_name}"
            }
        else:
            tool_func = STATISTICS_TOOLS[tool_name]
            result = tool_func(**tool_args)

        vprint(f"[STATISTICS TOOL] Result: {result}")
        log_tool_result(tool_name, result)

        # Create tool message
        tool_message = ToolMessage(
            content=str(result),
            tool_call_id=tool_call_id
        )

        # Update state
        state_updates = {"messages": [tool_message]}

        if result.get("status") == "success" and "statistics_summary" in result:
            execution_entry["status"] = "success"

            # Import state update helper
            from uvisbox_assistant.state import update_state_with_statistics

            # Update state with both raw and processed statistics
            raw_stats = result.get("_raw_statistics", {})
            stats_summary = result["statistics_summary"]

            state_updates.update(
                update_state_with_statistics(state, raw_stats, stats_summary)
            )

            # Check for auto-fix pattern
            _check_and_mark_auto_fix(state, tool_name, state_updates)
        else:
            execution_entry["status"] = "error"
            state_updates.update(increment_error_count(state))
            # Store error info for auto-fix detection
            state_updates["last_error_tool"] = tool_name
            state_updates["last_error_id"] = state.get("_pending_error_id")

        # Add execution to sequence
        _add_execution_entry(state, execution_entry, state_updates)

        return state_updates

    except Exception as e:
        vprint(f"[STATISTICS TOOL] Exception: {e}")
        log_error(f"Exception in {tool_name}: {str(e)}")
        error_result = {
            "status": "error",
            "message": f"Exception in {tool_name}: {str(e)}"
        }

        execution_entry["status"] = "error"

        tool_message = ToolMessage(
            content=str(error_result),
            tool_call_id=tool_call_id
        )

        state_updates = {
            "messages": [tool_message],
            **increment_error_count(state),
            "last_error_tool": tool_name,
            "last_error_id": state.get("_pending_error_id")
        }

        # Add execution to sequence
        _add_execution_entry(state, execution_entry, state_updates)

        return state_updates
```

### Step 2: Create Analyzer Tool Node

**File**: `src/uvisbox_assistant/nodes.py`

Add analyzer node function:

```python
def call_analyzer_tool(state: GraphState) -> Dict:
    """
    Node that executes an analyzer tool.

    Args:
        state: Current graph state

    Returns:
        Dict with tool result message and state updates
    """
    last_message = state["messages"][-1]

    # Extract tool call
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        raise ValueError("call_analyzer_tool invoked but no tool_calls in last message")

    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    tool_call_id = tool_call["id"]

    vprint(f"[ANALYZER TOOL] Calling {tool_name} with args: {tool_args}")
    log_tool_call(tool_name, tool_args)

    # Track execution start
    execution_entry = {
        "tool_name": tool_name,
        "timestamp": datetime.now(),
        "status": None,
        "error_id": None
    }

    # Execute tool
    try:
        # Import analyzer tools
        from uvisbox_assistant.analyzer_tools import ANALYZER_TOOLS

        if tool_name not in ANALYZER_TOOLS:
            result = {
                "status": "error",
                "message": f"Unknown analyzer tool: {tool_name}"
            }
        else:
            tool_func = ANALYZER_TOOLS[tool_name]
            result = tool_func(**tool_args)

        vprint(f"[ANALYZER TOOL] Result: {result}")
        log_tool_result(tool_name, result)

        # Create tool message
        tool_message = ToolMessage(
            content=str(result),
            tool_call_id=tool_call_id
        )

        # Update state
        state_updates = {"messages": [tool_message]}

        if result.get("status") == "success" and "report" in result:
            execution_entry["status"] = "success"

            # Import state update helper
            from uvisbox_assistant.state import update_state_with_analysis

            # Update state with analysis results
            report = result["report"]
            analysis_type = result.get("analysis_type", "quick")

            state_updates.update(
                update_state_with_analysis(state, report, analysis_type)
            )

            # Check for auto-fix pattern
            _check_and_mark_auto_fix(state, tool_name, state_updates)
        else:
            execution_entry["status"] = "error"
            state_updates.update(increment_error_count(state))
            # Store error info for auto-fix detection
            state_updates["last_error_tool"] = tool_name
            state_updates["last_error_id"] = state.get("_pending_error_id")

        # Add execution to sequence
        _add_execution_entry(state, execution_entry, state_updates)

        return state_updates

    except Exception as e:
        vprint(f"[ANALYZER TOOL] Exception: {e}")
        log_error(f"Exception in {tool_name}: {str(e)}")
        error_result = {
            "status": "error",
            "message": f"Exception in {tool_name}: {str(e)}"
        }

        execution_entry["status"] = "error"

        tool_message = ToolMessage(
            content=str(error_result),
            tool_call_id=tool_call_id
        )

        state_updates = {
            "messages": [tool_message],
            **increment_error_count(state),
            "last_error_tool": tool_name,
            "last_error_id": state.get("_pending_error_id")
        }

        # Add execution to sequence
        _add_execution_entry(state, execution_entry, state_updates)

        return state_updates
```

### Step 3: Update Tool Type Detection

**File**: `src/uvisbox_assistant/utils.py`

Update get_tool_type to recognize new tools:

```python
def get_tool_type(tool_name: str) -> str:
    """
    Determine the type of tool based on its name.

    Args:
        tool_name: Name of the tool

    Returns:
        Tool type: "data", "vis", "statistics", "analyzer", or "unknown"
    """
    # Import tool registries
    from uvisbox_assistant.data_tools import DATA_TOOLS
    from uvisbox_assistant.vis_tools import VIS_TOOLS
    from uvisbox_assistant.statistics_tools import STATISTICS_TOOLS
    from uvisbox_assistant.analyzer_tools import ANALYZER_TOOLS

    if tool_name in DATA_TOOLS:
        return "data"
    elif tool_name in VIS_TOOLS:
        return "vis"
    elif tool_name in STATISTICS_TOOLS:
        return "statistics"
    elif tool_name in ANALYZER_TOOLS:
        return "analyzer"
    else:
        return "unknown"
```

### Step 4: Update Routing Logic

**File**: `src/uvisbox_assistant/routing.py`

Update route_after_model to handle new tool types:

```python
def route_after_model(state: GraphState) -> Literal["data_tool", "vis_tool", "statistics_tool", "analyzer_tool", "end"]:
    """
    Determine the next node after the model has responded.

    Logic:
    - If the last message contains tool_calls:
      - Route to "data_tool" if it's a data tool
      - Route to "vis_tool" if it's a vis tool
      - Route to "statistics_tool" if it's a statistics tool
      - Route to "analyzer_tool" if it's an analyzer tool
    - Otherwise, route to "end" (conversation response without tool call)

    Args:
        state: Current graph state

    Returns:
        Next node name: "data_tool", "vis_tool", "statistics_tool", "analyzer_tool", or "end"
    """
    last_message = state["messages"][-1]

    # Check if message has tool calls
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        # No tool call - model is responding directly to user
        return "end"

    # Get the first tool call
    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]

    # Route based on tool type
    tool_type = get_tool_type(tool_name)

    if tool_type == "data":
        return "data_tool"
    elif tool_type == "vis":
        return "vis_tool"
    elif tool_type == "statistics":
        return "statistics_tool"
    elif tool_type == "analyzer":
        return "analyzer_tool"
    else:
        # Unknown tool - end and let user see the error
        print(f"WARNING: Unknown tool type for {tool_name}")
        return "end"
```

Add conditional edges from new tool nodes:

```python
# No changes needed to route_after_tool - it already handles all tool nodes generically
# by checking error_count and routing back to model or end
```

### Step 5: Update Graph Structure

**File**: `src/uvisbox_assistant/graph.py`

Update graph definition to include new nodes and edges:

```python
def create_graph():
    """
    Create and compile the UVisBox-Assistant LangGraph workflow.

    Graph structure:
        START -> model -> [conditional]
                            ├─> data_tool -> model (loop)
                            ├─> vis_tool -> model (loop)
                            ├─> statistics_tool -> model (loop)  # NEW
                            ├─> analyzer_tool -> model (loop)    # NEW
                            └─> END (if no tool call)

    Returns:
        Compiled StateGraph
    """
    # Import new nodes
    from uvisbox_assistant.nodes import (
        call_model,
        call_data_tool,
        call_vis_tool,
        call_statistics_tool,  # NEW
        call_analyzer_tool     # NEW
    )

    # Initialize graph
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("model", call_model)
    workflow.add_node("data_tool", call_data_tool)
    workflow.add_node("vis_tool", call_vis_tool)
    workflow.add_node("statistics_tool", call_statistics_tool)  # NEW
    workflow.add_node("analyzer_tool", call_analyzer_tool)      # NEW

    # Set entry point
    workflow.set_entry_point("model")

    # Add conditional edges from model
    workflow.add_conditional_edges(
        "model",
        route_after_model,
        {
            "data_tool": "data_tool",
            "vis_tool": "vis_tool",
            "statistics_tool": "statistics_tool",  # NEW
            "analyzer_tool": "analyzer_tool",      # NEW
            "end": END
        }
    )

    # Add edges back to model after tool execution
    workflow.add_conditional_edges(
        "data_tool",
        route_after_tool,
        {
            "model": "model",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        "vis_tool",
        route_after_tool,
        {
            "model": "model",
            "end": END
        }
    )

    # NEW: Add edges for statistics_tool
    workflow.add_conditional_edges(
        "statistics_tool",
        route_after_tool,
        {
            "model": "model",
            "end": END
        }
    )

    # NEW: Add edges for analyzer_tool
    workflow.add_conditional_edges(
        "analyzer_tool",
        route_after_tool,
        {
            "model": "model",
            "end": END
        }
    )

    # Compile the graph
    app = workflow.compile()

    return app


# Create singleton graph instance
graph_app = create_graph()
```

### Step 6: Update Model Tool Binding

**File**: `src/uvisbox_assistant/model.py`

Update model to include new tool schemas:

```python
def create_model_with_tools(tool_schemas: Optional[List[Dict]] = None):
    """
    Create Gemini model with tool bindings.

    Args:
        tool_schemas: Optional list of tool schemas. If None, binds all tools.

    Returns:
        ChatGoogleGenerativeAI model with tools bound
    """
    from langchain_google_genai import ChatGoogleGenerativeAI
    from uvisbox_assistant import config
    from uvisbox_assistant.data_tools import DATA_TOOL_SCHEMAS
    from uvisbox_assistant.vis_tools import VIS_TOOL_SCHEMAS
    from uvisbox_assistant.statistics_tools import STATISTICS_TOOL_SCHEMAS  # NEW
    from uvisbox_assistant.analyzer_tools import ANALYZER_TOOL_SCHEMAS      # NEW

    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=config.GEMINI_API_KEY,
        temperature=0.0
    )

    # Use provided schemas or all schemas
    if tool_schemas is None:
        tool_schemas = (
            DATA_TOOL_SCHEMAS +
            VIS_TOOL_SCHEMAS +
            STATISTICS_TOOL_SCHEMAS +  # NEW
            ANALYZER_TOOL_SCHEMAS      # NEW
        )

    if tool_schemas:
        model = model.bind_tools(tool_schemas)

    return model
```

Update nodes.py to rebuild model with all schemas:

```python
# At top of nodes.py, update MODEL creation:

from uvisbox_assistant.data_tools import DATA_TOOL_SCHEMAS
from uvisbox_assistant.vis_tools import VIS_TOOL_SCHEMAS
from uvisbox_assistant.statistics_tools import STATISTICS_TOOL_SCHEMAS  # NEW
from uvisbox_assistant.analyzer_tools import ANALYZER_TOOL_SCHEMAS      # NEW

# Create model with all tools
ALL_TOOL_SCHEMAS = (
    DATA_TOOL_SCHEMAS +
    VIS_TOOL_SCHEMAS +
    STATISTICS_TOOL_SCHEMAS +  # NEW
    ANALYZER_TOOL_SCHEMAS      # NEW
)
MODEL = create_model_with_tools(ALL_TOOL_SCHEMAS)
```

## Testing Plan

### Unit Tests for Routing

**File**: `tests/unit/test_routing.py`

Add tests for new routing paths:

```python
"""Unit tests for routing logic with new tool nodes."""

import pytest
from langchain_core.messages import AIMessage
from uvisbox_assistant.routing import route_after_model, route_after_tool
from uvisbox_assistant.state import create_initial_state


class TestRouteAfterModelNewTools:
    """Test routing to new tool nodes."""

    def test_route_to_statistics_tool(self):
        """Test routing to statistics_tool."""
        state = create_initial_state("test")

        # Simulate model calling statistics tool
        ai_message = AIMessage(
            content="",
            tool_calls=[{
                "name": "compute_functional_boxplot_statistics",
                "args": {"data_path": "/path/to/data.npy"},
                "id": "call_123"
            }]
        )
        state["messages"].append(ai_message)

        result = route_after_model(state)
        assert result == "statistics_tool"

    def test_route_to_analyzer_tool(self):
        """Test routing to analyzer_tool."""
        state = create_initial_state("test")

        ai_message = AIMessage(
            content="",
            tool_calls=[{
                "name": "generate_uncertainty_report",
                "args": {"statistics_summary": {}, "analysis_type": "quick"},
                "id": "call_456"
            }]
        )
        state["messages"].append(ai_message)

        result = route_after_model(state)
        assert result == "analyzer_tool"

    def test_backward_compatibility_data_tool(self):
        """Verify existing data tool routing still works."""
        state = create_initial_state("test")

        ai_message = AIMessage(
            content="",
            tool_calls=[{
                "name": "generate_ensemble_curves",
                "args": {"n_curves": 30},
                "id": "call_789"
            }]
        )
        state["messages"].append(ai_message)

        result = route_after_model(state)
        assert result == "data_tool"

    def test_backward_compatibility_vis_tool(self):
        """Verify existing vis tool routing still works."""
        state = create_initial_state("test")

        ai_message = AIMessage(
            content="",
            tool_calls=[{
                "name": "plot_functional_boxplot",
                "args": {"data_path": "/path/to/data.npy"},
                "id": "call_abc"
            }]
        )
        state["messages"].append(ai_message)

        result = route_after_model(state)
        assert result == "vis_tool"


class TestRouteAfterToolWithNewNodes:
    """Test route_after_tool works with new nodes."""

    def test_statistics_tool_success_routes_to_model(self):
        """Test successful statistics tool routes back to model."""
        state = create_initial_state("test")
        state["error_count"] = 0

        result = route_after_tool(state)
        assert result == "model"

    def test_analyzer_tool_success_routes_to_model(self):
        """Test successful analyzer tool routes back to model."""
        state = create_initial_state("test")
        state["error_count"] = 0

        result = route_after_tool(state)
        assert result == "model"

    def test_circuit_breaker_works_for_new_tools(self):
        """Test circuit breaker triggers for new tools."""
        state = create_initial_state("test")
        state["error_count"] = 3

        result = route_after_tool(state)
        assert result == "end"
```

### Integration Tests for Multi-Step Workflows

**File**: `tests/integration/test_multi_tool_workflows.py`

```python
"""Integration tests for multi-tool workflows (uses API calls)."""

import pytest
import time
import numpy as np
from pathlib import Path
from unittest.mock import patch
from uvisbox_assistant.conversation import ConversationSession


@pytest.fixture
def temp_data_file(tmp_path):
    """Create temporary data file for testing."""
    curves = np.random.randn(30, 100)
    data_path = tmp_path / "test_curves.npy"
    np.save(data_path, curves)
    return str(data_path)


class TestDataToStatisticsWorkflow:
    """Test data → statistics workflow."""

    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_data_then_statistics(self, mock_uvisbox, temp_data_file):
        """Test sequential data tool → statistics tool execution."""
        time.sleep(2)  # Rate limit

        # Mock UVisBox statistics
        mock_uvisbox.return_value = {
            "depth": np.random.rand(30),
            "median": np.random.randn(100),
            "percentile_bands": {
                "50_percentile_band": (np.random.randn(100), np.random.randn(100))
            },
            "outliers": np.array([]),
            "sorted_curves": np.random.randn(30, 100),
            "sorted_indices": np.arange(30)
        }

        session = ConversationSession()

        # User requests data generation and statistics
        state = session.send(f"Load {temp_data_file} and compute statistics")

        # Verify statistics were computed
        assert state.get("statistics_summary") is not None
        assert "median" in state["statistics_summary"]
        assert "bands" in state["statistics_summary"]


class TestStatisticsToAnalyzerWorkflow:
    """Test statistics → analyzer workflow."""

    def test_statistics_then_analyzer(self):
        """Test sequential statistics → analyzer execution."""
        time.sleep(2)  # Rate limit

        session = ConversationSession()

        # Simulate state with statistics already computed
        # (In real scenario, would come from previous data → statistics)
        mock_stats_summary = {
            "data_shape": {"n_curves": 30, "n_points": 100},
            "median": {
                "trend": "increasing",
                "overall_slope": 0.05,
                "fluctuation_level": 0.15,
                "smoothness_score": 0.85,
                "value_range": (0.5, 5.5)
            },
            "bands": {"band_widths": {}, "overall_uncertainty_score": 0.3},
            "outliers": {"count": 2, "outlier_percentage": 6.7},
            "method": "fbd"
        }

        # Manually set state for testing (in real use, would come from graph)
        session.state = create_initial_state("generate report")
        session.state["statistics_summary"] = mock_stats_summary

        # Request analysis report
        state = session.send("Generate quick analysis report")

        # Verify report was generated
        assert state.get("analysis_report") is not None
        assert state.get("analysis_type") in ["inline", "quick", "detailed"]
```

## Success Conditions

- [ ] call_statistics_tool() node function created and tested
- [ ] call_analyzer_tool() node function created and tested
- [ ] get_tool_type() recognizes "statistics" and "analyzer" types
- [ ] route_after_model() routes to new tool nodes correctly
- [ ] Graph structure includes statistics_tool and analyzer_tool nodes
- [ ] Conditional edges configured for new nodes
- [ ] Model bound with STATISTICS_TOOL_SCHEMAS and ANALYZER_TOOL_SCHEMAS
- [ ] 8+ routing unit tests pass (including backward compatibility)
- [ ] All existing unit tests still pass (backward compatibility verified)
- [ ] 2+ integration tests for multi-tool workflows pass

## Integration Notes

### Graph Execution Flow

**New workflow example**:
```
User: "Generate curves, compute statistics, and create quick report"

Flow:
1. START → call_model (decides: generate_ensemble_curves)
2. call_model → route_after_model → data_tool
3. data_tool → route_after_tool → model
4. call_model (decides: compute_functional_boxplot_statistics)
5. call_model → route_after_model → statistics_tool
6. statistics_tool → route_after_tool → model
7. call_model (decides: generate_uncertainty_report)
8. call_model → route_after_model → analyzer_tool
9. analyzer_tool → route_after_tool → model
10. call_model (responds to user with confirmation)
11. call_model → route_after_model → END
```

### State Preservation

Each tool node:
- Receives current state
- Executes tool function
- Updates specific state fields (statistics_summary, analysis_report, etc.)
- Preserves all other state fields
- Resets error_count on success
- Returns to model for next decision

### Error Handling Continuity

Circuit breaker works identically for new tools:
- Each tool failure increments error_count
- After 3 consecutive failures, route_after_tool goes to END
- Successful tool execution resets error_count to 0
- Auto-fix detection works for new tools

### Backward Compatibility Verification

Critical tests:
1. Existing data → vis workflow still works
2. Existing hybrid control still works
3. Existing error handling still works
4. No changes to existing tool function signatures

## Estimated Effort

**Development**: 3 hours
- Node functions: 1.5 hours
- Routing updates: 45 minutes
- Graph structure updates: 45 minutes

**Testing**: 1.5 hours
- Unit tests: 45 minutes
- Integration tests: 45 minutes (with API delays)

**Total**: 4-5 hours (including careful backward compatibility verification)
