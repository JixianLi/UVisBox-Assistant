# Phase 5: Multi-Workflow Support and End-to-End Testing

## Overview

Validate and refine all three workflow patterns (vis-only, text-only, combined) with comprehensive end-to-end testing. This phase ensures the system correctly interprets user intent, executes appropriate tool sequences, and maintains state correctly across complex multi-turn conversations.

## Goals

- Validate Pattern 1: Visualization-only workflow (existing, must continue working)
- Validate Pattern 2: Text-only analysis workflow (new)
- Validate Pattern 3: Combined visualization + analysis workflow (new)
- Create comprehensive E2E tests for all patterns
- Refine model system prompt for better tool selection
- Verify multi-turn conversation handling

## Prerequisites

- Phase 4 completed (graph integration functional)
- All unit and integration tests passing
- UVisBox library available for testing

## Implementation Plan

### Step 1: Enhance Model System Prompt

**File**: `src/uvisbox_assistant/model.py`

Update system prompt to guide tool selection for analysis workflows:

```python
SYSTEM_PROMPT = """You are UVisBox-Assistant, a helpful AI for uncertainty visualization and analysis.

Available Tools:
- Data tools: Generate or load ensemble data
- Visualization tools: Create uncertainty visualizations (boxplots, contours, glyphs)
- Statistics tools: Compute numerical summaries of uncertainty characteristics
- Analyzer tools: Generate natural language reports about uncertainty

Workflow Patterns:

1. VISUALIZATION ONLY (existing):
   User: "generate curves and plot them"
   → data_tool → vis_tool

2. TEXT ANALYSIS ONLY (new):
   User: "generate curves and analyze uncertainty"
   User: "create a data summary"
   → data_tool → statistics_tool → analyzer_tool

3. COMBINED VISUALIZATION + ANALYSIS (new):
   User: "generate curves, plot boxplot, and create summary"
   → data_tool → vis_tool → statistics_tool → analyzer_tool

Tool Selection Guidelines:
- Use statistics_tool when user requests: "analyze", "summary", "statistics", "uncertainty characteristics"
- Use analyzer_tool AFTER statistics_tool to generate text reports
- Analysis types: "inline" (1 sentence), "quick" (3-5 sentences), "detailed" (full report)
- If user says "analyze" without specifying format, use "quick"
- You can combine visualization and analysis in the same workflow

Context Awareness:
- Remember current_data_path from previous operations
- If user requests visualization/analysis, use current_data_path unless they specify new data
- For statistics tools, use the data_path from current_data_path
- For analyzer tools, use statistics_summary from state (passed automatically)

Error Recovery:
- If a tool fails, suggest alternatives or ask for clarification
- If data file not found, list available files
- Be helpful and guide users to successful outcomes

Available files in test_data: {file_list}
"""
```

Update prepare_messages_for_model to inject system prompt:

```python
def prepare_messages_for_model(state: GraphState, file_list: List[str]) -> List[BaseMessage]:
    """
    Prepare messages for model invocation with system prompt.

    Args:
        state: Current graph state
        file_list: List of available data files

    Returns:
        List of messages including system prompt
    """
    from langchain_core.messages import SystemMessage

    # Format system prompt with file list
    system_message = SystemMessage(
        content=SYSTEM_PROMPT.format(file_list=", ".join(file_list) if file_list else "None")
    )

    # Combine system message with conversation messages
    messages = [system_message] + state["messages"]

    return messages
```

### Step 2: Add Conversation Context Commands

**File**: `src/uvisbox_assistant/conversation.py`

Add method to display analysis state:

```python
class ConversationSession:
    # ... existing methods ...

    def get_analysis_summary(self) -> Optional[str]:
        """
        Get summary of current analysis state.

        Returns:
            Formatted string with analysis info, or None if no analysis
        """
        if not self.state:
            return None

        has_stats = self.state.get("statistics_summary") is not None
        has_report = self.state.get("analysis_report") is not None

        if not has_stats and not has_report:
            return None

        lines = ["📊 Analysis State:"]

        if has_stats:
            stats = self.state["statistics_summary"]
            data_shape = stats.get("data_shape", {})
            n_curves = data_shape.get("n_curves", "?")
            n_points = data_shape.get("n_points", "?")
            lines.append(f"  ✓ Statistics computed: {n_curves} curves, {n_points} points")

            median = stats.get("median", {})
            lines.append(f"  - Median trend: {median.get('trend', 'unknown')}")

            outliers = stats.get("outliers", {})
            outlier_count = outliers.get("count", 0)
            lines.append(f"  - Outliers: {outlier_count}")

        if has_report:
            report = self.state["analysis_report"]
            analysis_type = self.state.get("analysis_type", "unknown")
            word_count = len(report.split())
            lines.append(f"  ✓ Report generated: {analysis_type} ({word_count} words)")
            lines.append(f"  - Preview: {report[:100]}...")

        return "\n".join(lines)
```

Update get_context_summary to include analysis state:

```python
def get_context_summary(self) -> dict:
    """
    Return current conversation context.

    Returns:
        Dict with context information
    """
    if not self.state:
        return {
            "turn_count": self.turn_count,
            "message_count": 0,
            "current_data": None,
            "last_vis": None,
            "statistics": None,
            "analysis": None,
            "error_count": 0
        }

    return {
        "turn_count": self.turn_count,
        "message_count": len(self.state.get("messages", [])),
        "current_data": self.state.get("current_data_path"),
        "last_vis": self.state.get("last_vis_params", {}).get("_tool_name") if self.state.get("last_vis_params") else None,
        "statistics": "computed" if self.state.get("statistics_summary") else None,
        "analysis": self.state.get("analysis_type") if self.state.get("analysis_report") else None,
        "error_count": self.state.get("error_count", 0)
    }
```

### Step 3: Create End-to-End Test Suite

**File**: `tests/e2e/test_analysis_workflows.py`

```python
"""End-to-end tests for uncertainty analysis workflows (uses API calls)."""

import pytest
import time
import numpy as np
from pathlib import Path
from unittest.mock import patch
from uvisbox_assistant.conversation import ConversationSession


@pytest.fixture
def test_data_path(tmp_path):
    """Create test data file."""
    n_curves, n_points = 30, 100
    x = np.linspace(0, 2*np.pi, n_points)
    curves = []
    for i in range(n_curves):
        amplitude = np.random.uniform(0.8, 1.2)
        phase = np.random.uniform(0, np.pi)
        noise = np.random.normal(0, 0.1, n_points)
        curve = amplitude * np.sin(x + phase) + noise
        curves.append(curve)
    data = np.array(curves)

    data_path = tmp_path / "e2e_test_curves.npy"
    np.save(data_path, data)
    return str(data_path)


class TestPattern1VisualizationOnly:
    """Test Pattern 1: Visualization-only workflow (existing behavior)."""

    @pytest.mark.e2e
    def test_generate_and_plot_workflow(self):
        """Test existing data → vis workflow still works."""
        time.sleep(2)  # Rate limit

        session = ConversationSession()

        # Request data generation and visualization
        state = session.send("Generate 30 curves and plot functional boxplot")

        # Verify data was created
        assert state.get("current_data_path") is not None

        # Verify visualization was created
        assert state.get("last_vis_params") is not None
        assert state["last_vis_params"]["_tool_name"] == "plot_functional_boxplot"

        # Verify NO analysis was performed (backward compatibility)
        assert state.get("statistics_summary") is None
        assert state.get("analysis_report") is None


class TestPattern2TextAnalysisOnly:
    """Test Pattern 2: Text-only analysis workflow (new)."""

    @pytest.mark.e2e
    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_generate_and_analyze_workflow(self, mock_uvisbox, test_data_path):
        """Test new data → statistics → analyzer workflow."""
        time.sleep(3)  # Rate limit (multiple LLM calls)

        # Mock UVisBox statistics
        mock_uvisbox.return_value = {
            "depth": np.random.rand(30),
            "median": np.random.randn(100),
            "percentile_bands": {
                "50_percentile_band": (np.random.randn(100), np.random.randn(100)),
                "90_percentile_band": (np.random.randn(100), np.random.randn(100))
            },
            "outliers": np.random.randn(2, 100),
            "sorted_curves": np.random.randn(30, 100),
            "sorted_indices": np.arange(30)
        }

        session = ConversationSession()

        # Request data and analysis (no visualization)
        state = session.send(f"Load {test_data_path} and create a quick uncertainty analysis")

        # Verify data was loaded
        assert state.get("current_data_path") is not None

        # Verify statistics were computed
        assert state.get("statistics_summary") is not None
        assert "median" in state["statistics_summary"]
        assert "bands" in state["statistics_summary"]

        # Verify analysis report was generated
        assert state.get("analysis_report") is not None
        assert state.get("analysis_type") == "quick"

        # Verify NO visualization was created
        assert state.get("last_vis_params") is None

    @pytest.mark.e2e
    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_inline_analysis_format(self, mock_uvisbox, test_data_path):
        """Test inline analysis format (1 sentence)."""
        time.sleep(3)

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

        # Request inline analysis
        state = session.send(f"Load {test_data_path} and give me an inline uncertainty summary")

        # Verify inline report
        assert state.get("analysis_report") is not None
        assert state.get("analysis_type") == "inline"

        # Verify report is short
        word_count = len(state["analysis_report"].split())
        assert 10 <= word_count <= 40

    @pytest.mark.e2e
    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_detailed_analysis_format(self, mock_uvisbox, test_data_path):
        """Test detailed analysis format (full report)."""
        time.sleep(3)

        mock_uvisbox.return_value = {
            "depth": np.random.rand(30),
            "median": np.random.randn(100),
            "percentile_bands": {
                "50_percentile_band": (np.random.randn(100), np.random.randn(100)),
                "90_percentile_band": (np.random.randn(100), np.random.randn(100))
            },
            "outliers": np.random.randn(3, 100),
            "sorted_curves": np.random.randn(30, 100),
            "sorted_indices": np.arange(30)
        }

        session = ConversationSession()

        # Request detailed analysis
        state = session.send(f"Load {test_data_path} and create a detailed uncertainty report")

        # Verify detailed report
        assert state.get("analysis_report") is not None
        assert state.get("analysis_type") == "detailed"

        # Verify report is comprehensive
        word_count = len(state["analysis_report"].split())
        assert word_count >= 100

        # Verify mentions key sections
        report_lower = state["analysis_report"].lower()
        assert "median" in report_lower
        assert "band" in report_lower or "percentile" in report_lower
        assert "outlier" in report_lower


class TestPattern3CombinedWorkflow:
    """Test Pattern 3: Combined visualization + analysis workflow (new)."""

    @pytest.mark.e2e
    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_vis_and_analysis_workflow(self, mock_uvisbox, test_data_path):
        """Test data → vis → statistics → analyzer workflow."""
        time.sleep(4)  # Rate limit (multiple LLM calls + tools)

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

        # Request both visualization and analysis
        state = session.send(
            f"Load {test_data_path}, plot functional boxplot, and create quick analysis"
        )

        # Verify data was loaded
        assert state.get("current_data_path") is not None

        # Verify visualization was created
        assert state.get("last_vis_params") is not None
        assert state["last_vis_params"]["_tool_name"] == "plot_functional_boxplot"

        # Verify statistics were computed
        assert state.get("statistics_summary") is not None

        # Verify analysis report was generated
        assert state.get("analysis_report") is not None


class TestMultiTurnAnalysisWorkflow:
    """Test multi-turn conversations with analysis."""

    @pytest.mark.e2e
    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_incremental_analysis_workflow(self, mock_uvisbox, test_data_path):
        """Test building up analysis over multiple turns."""
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

        # Turn 1: Load data
        time.sleep(2)
        state = session.send(f"Load {test_data_path}")
        assert state.get("current_data_path") is not None
        assert state.get("statistics_summary") is None

        # Turn 2: Compute statistics
        time.sleep(2)
        state = session.send("Compute statistics for this data")
        assert state.get("statistics_summary") is not None
        assert state.get("analysis_report") is None

        # Turn 3: Generate report
        time.sleep(2)
        state = session.send("Now generate a quick analysis report")
        assert state.get("analysis_report") is not None
        assert state.get("analysis_type") == "quick"

    @pytest.mark.e2e
    @patch('uvisbox_assistant.statistics_tools.functional_boxplot_summary_statistics')
    def test_analysis_then_visualization(self, mock_uvisbox, test_data_path):
        """Test doing analysis first, then visualization."""
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

        # Turn 1: Load and analyze
        time.sleep(3)
        state = session.send(f"Load {test_data_path} and analyze uncertainty")
        assert state.get("statistics_summary") is not None
        assert state.get("analysis_report") is not None

        # Turn 2: Now visualize
        time.sleep(2)
        state = session.send("Now plot it as functional boxplot")
        assert state.get("last_vis_params") is not None
        # Statistics should still be there
        assert state.get("statistics_summary") is not None
```

### Step 4: Add Example Usage Documentation

**File**: `docs/ANALYSIS_EXAMPLES.md`

```markdown
# Uncertainty Analysis Examples

## Quick Start

### Pattern 1: Visualization Only (Existing)

```python
from uvisbox_assistant.conversation import ConversationSession

session = ConversationSession()
session.send("Generate 50 curves and plot functional boxplot")
```

### Pattern 2: Text Analysis Only (New)

```python
session = ConversationSession()
session.send("Generate 50 curves and create a quick uncertainty analysis")
```

### Pattern 3: Combined Visualization + Analysis (New)

```python
session = ConversationSession()
session.send("Generate 50 curves, plot boxplot, and create detailed analysis")
```

## Analysis Report Formats

### Inline (1 sentence)

```python
session.send("Give me an inline uncertainty summary")
# Output: "This ensemble shows moderate uncertainty with 15% band width variation and 2 outliers."
```

### Quick (3-5 sentences)

```python
session.send("Create a quick analysis")
# Output: Multi-sentence overview covering median, bands, outliers
```

### Detailed (Full report)

```python
session.send("Generate a detailed uncertainty report")
# Output: Structured report with sections for median, bands, outliers, overall assessment
```

## Multi-Turn Workflows

### Incremental Analysis

```python
session = ConversationSession()

# Step 1: Load data
session.send("Load test_data/sample_curves.npy")

# Step 2: Compute statistics
session.send("Compute statistics for this data")

# Step 3: Generate report
session.send("Create a quick analysis report")

# Step 4: Visualize
session.send("Now plot it")
```

### Refining Analysis

```python
# Start with inline
session.send("Give me an inline summary")

# Ask for more detail
session.send("That's interesting, give me a detailed report")
```

## Checking Analysis State

```python
# Get context
context = session.get_context_summary()
print(f"Statistics: {context['statistics']}")
print(f"Analysis: {context['analysis']}")

# Get analysis details
analysis_summary = session.get_analysis_summary()
print(analysis_summary)
```
```

## Testing Plan

### E2E Test Execution

```bash
# Run all E2E tests (slow, ~10-15 minutes)
pytest tests/e2e/test_analysis_workflows.py -v

# Run specific pattern
pytest tests/e2e/test_analysis_workflows.py::TestPattern2TextAnalysisOnly -v

# Run with rate limit consideration
pytest tests/e2e/test_analysis_workflows.py -v --tb=short
```

### Manual Testing Scenarios

**Scenario 1: Text-only analysis**
```
User: Generate 30 curves and analyze uncertainty
Expected: Data generation → Statistics → Quick report (no visualization)
```

**Scenario 2: Combined workflow**
```
User: Generate curves, plot boxplot, and create summary
Expected: Data generation → Visualization → Statistics → Report
```

**Scenario 3: Multi-turn refinement**
```
Turn 1: Generate and analyze data (inline)
Turn 2: Give me more detail (detailed report)
Turn 3: Now plot it (visualization added)
```

## Success Conditions

- [ ] Pattern 1 (vis-only) still works (backward compatibility)
- [ ] Pattern 2 (text-only) works correctly
- [ ] Pattern 3 (combined) works correctly
- [ ] Model system prompt guides tool selection appropriately
- [ ] Inline reports are 1 sentence (~15-30 words)
- [ ] Quick reports are 3-5 sentences (~50-100 words)
- [ ] Detailed reports are comprehensive (100+ words)
- [ ] Multi-turn conversations maintain state correctly
- [ ] get_analysis_summary() provides useful analysis state info
- [ ] 12+ E2E tests pass (covering all patterns)
- [ ] All existing E2E tests still pass

## Integration Notes

### Model Behavior

The enhanced system prompt guides the model to:
1. Recognize analysis requests ("analyze", "summary", "statistics")
2. Choose appropriate analysis format (inline/quick/detailed)
3. Execute correct tool sequence (data → stats → analyzer)
4. Maintain context across multi-turn conversations

### State Consistency

State fields are preserved across workflow:
- `current_data_path`: Set by data tool, used by statistics tool
- `statistics_summary`: Set by statistics tool, used by analyzer tool
- `analysis_report`: Set by analyzer tool, displayed to user
- `last_vis_params`: Independent, can coexist with analysis state

### User Intent Parsing

Natural language indicators:
- "analyze" → statistics + analyzer workflow
- "summary" → statistics + analyzer workflow
- "quick/detailed/inline" → specific analysis format
- "plot" + "analyze" → combined workflow
- "plot" alone → vis-only workflow

## Estimated Effort

**Development**: 2 hours
- System prompt enhancement: 30 minutes
- Analysis context methods: 30 minutes
- Documentation: 1 hour

**Testing**: 1.5 hours
- E2E test writing: 1 hour
- Manual testing: 30 minutes

**Total**: 3-4 hours (including comprehensive validation)
