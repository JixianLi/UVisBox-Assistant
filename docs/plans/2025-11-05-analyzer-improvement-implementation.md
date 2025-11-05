# v0.3.2 Analyzer Improvement Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix analyzer regeneration issue by generating all three report types at once and enabling instant report switching via hybrid control.

**Architecture:** Modify state to store reports as dictionary, update analyzer tool to generate all three types in single call, add hybrid control patterns for instant retrieval, update model prompt for smart intent detection.

**Tech Stack:** Python 3.13, LangGraph, LangChain, Poetry, pytest

---

## Phase 1: State Structure Changes

### Task 1.1: Update State Type Definition

**Files:**
- Modify: `src/uvisbox_assistant/core/state.py:7-46`
- Test: Update in later phase (integration tests will verify)

**Step 1: Update GraphState TypedDict**

In `src/uvisbox_assistant/core/state.py`, replace lines 21-25:

```python
# OLD (remove these lines):
        raw_statistics: Raw output from functional_boxplot_summary_statistics (numpy arrays)
        processed_statistics: LLM-friendly structured summary from statistics_tool
        analysis_report: Generated text report from analyzer_tool
        analysis_type: Report format - "inline" | "quick" | "detailed" | None
```

With:

```python
# NEW:
        raw_statistics: Raw output from functional_boxplot_summary_statistics (numpy arrays)
        processed_statistics: LLM-friendly structured summary from statistics_tool
        analysis_reports: Dictionary of all three report types {"inline": "...", "quick": "...", "detailed": "..."}
```

**Step 2: Update state field declarations (lines 42-45)**

Replace:

```python
# OLD:
    raw_statistics: Optional[dict]
    processed_statistics: Optional[dict]
    analysis_report: Optional[str]
    analysis_type: Optional[str]
```

With:

```python
# NEW:
    raw_statistics: Optional[dict]
    processed_statistics: Optional[dict]
    analysis_reports: Optional[Dict[str, str]]
```

**Step 3: Add Dict import at top of file**

At line 2, update the import to include Dict:

```python
from typing import TypedDict, List, Optional, Annotated, Dict
```

**Step 4: Run import check**

Run: `python -c "from uvisbox_assistant.core.state import GraphState; print('Import successful')"`
Expected: "Import successful"

**Step 5: Commit state type changes**

```bash
git add src/uvisbox_assistant/core/state.py
git commit -m "refactor: update GraphState to use analysis_reports dictionary"
```

### Task 1.2: Update create_initial_state Function

**Files:**
- Modify: `src/uvisbox_assistant/core/state.py:48-74`

**Step 1: Update initial state (lines 69-73)**

Replace:

```python
# OLD:
        # NEW: Initialize analysis state (v0.3.0)
        raw_statistics=None,
        processed_statistics=None,
        analysis_report=None,
        analysis_type=None
```

With:

```python
# NEW:
        # NEW: Initialize analysis state (v0.3.2)
        raw_statistics=None,
        processed_statistics=None,
        analysis_reports=None
```

**Step 2: Test state creation**

Run: `python -c "from uvisbox_assistant.core.state import create_initial_state; s = create_initial_state('test'); print('analysis_reports' in s and s['analysis_reports'] is None)"`
Expected: `True`

**Step 3: Commit**

```bash
git add src/uvisbox_assistant/core/state.py
git commit -m "refactor: initialize analysis_reports as None in create_initial_state"
```

### Task 1.3: Update update_state_with_analysis Function

**Files:**
- Modify: `src/uvisbox_assistant/core/state.py:135-151`

**Step 1: Update function signature and docstring (lines 135-143)**

Replace:

```python
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
```

With:

```python
def update_state_with_analysis(state: GraphState, reports: Dict[str, str]) -> dict:
    """
    Update state after successful analyzer tool execution.

    Args:
        state: Current graph state
        reports: Dictionary with all three report types {"inline": "...", "quick": "...", "detailed": "..."}

    Returns:
        Dict of updates to merge into state
    """
```

**Step 2: Update return statement (lines 147-150)**

Replace:

```python
    return {
        "analysis_report": report,
        "analysis_type": analysis_type,
        "error_count": 0  # Reset error count on success
    }
```

With:

```python
    return {
        "analysis_reports": reports,
        "error_count": 0  # Reset error count on success
    }
```

**Step 3: Test function**

Run:
```bash
python -c "
from uvisbox_assistant.core.state import update_state_with_analysis, create_initial_state
state = create_initial_state('test')
reports = {'inline': 'a', 'quick': 'b', 'detailed': 'c'}
update = update_state_with_analysis(state, reports)
print('analysis_reports' in update and len(update['analysis_reports']) == 3)
"
```
Expected: `True`

**Step 4: Commit**

```bash
git add src/uvisbox_assistant/core/state.py
git commit -m "refactor: update update_state_with_analysis to accept reports dict"
```

---

## Phase 2: Analyzer Tool Changes

### Task 2.1: Write Test for Multi-Report Generation

**Files:**
- Modify: `tests/integration/test_analyzer_tool.py`

**Step 1: Add new test class for multi-report generation**

At the end of `tests/integration/test_analyzer_tool.py` (after existing test classes), add:

```python
class TestMultiReportGeneration:
    """Test that analyzer generates all three report types at once (v0.3.2)"""

    def test_all_three_reports_generated(self):
        """Verify analyzer returns inline, quick, and detailed reports in single call"""
        # Arrange
        processed_stats = {
            "data_shape": {"n_curves": 100, "n_points": 50},
            "median": {
                "trend": "increasing",
                "overall_slope": 0.5,
                "fluctuation_level": "low",
                "smoothness_score": 0.95,
                "value_range": {"min": 0.0, "max": 10.0}
            },
            "bands": {
                "band_widths": [0.5, 1.0, 1.5],
                "overall_uncertainty": 0.3
            },
            "outliers": {
                "count": 2,
                "similarity_to_median": 0.7
            },
            "method": "modified_band_depth"
        }

        # Act
        from uvisbox_assistant.tools.analyzer_tools import generate_uncertainty_report
        result = generate_uncertainty_report(processed_stats)

        # Assert
        assert result["status"] == "success", f"Expected success, got: {result.get('message')}"
        assert "reports" in result, "Result should contain 'reports' key"
        assert isinstance(result["reports"], dict), "Reports should be a dictionary"

        # Verify all three types present
        assert "inline" in result["reports"], "Missing inline report"
        assert "quick" in result["reports"], "Missing quick report"
        assert "detailed" in result["reports"], "Missing detailed report"

        # Verify each is non-empty string
        for report_type in ["inline", "quick", "detailed"]:
            report = result["reports"][report_type]
            assert isinstance(report, str), f"{report_type} report should be string"
            assert len(report) > 0, f"{report_type} report should not be empty"
            assert len(report.split()) > 5, f"{report_type} report should have multiple words"

    def test_multi_report_word_counts(self):
        """Verify different report types have appropriate lengths"""
        # Arrange
        processed_stats = {
            "data_shape": {"n_curves": 100, "n_points": 50},
            "median": {
                "trend": "increasing",
                "overall_slope": 0.5,
                "fluctuation_level": "low",
                "smoothness_score": 0.95,
                "value_range": {"min": 0.0, "max": 10.0}
            },
            "bands": {
                "band_widths": [0.5, 1.0, 1.5],
                "overall_uncertainty": 0.3
            },
            "outliers": {
                "count": 2,
                "similarity_to_median": 0.7
            },
            "method": "modified_band_depth"
        }

        # Act
        from uvisbox_assistant.tools.analyzer_tools import generate_uncertainty_report
        result = generate_uncertainty_report(processed_stats)

        # Assert - verify appropriate lengths
        reports = result["reports"]
        inline_words = len(reports["inline"].split())
        quick_words = len(reports["quick"].split())
        detailed_words = len(reports["detailed"].split())

        # Inline should be shortest (1 sentence, ~15-30 words)
        assert 10 <= inline_words <= 40, f"Inline should be 10-40 words, got {inline_words}"

        # Quick should be medium (3-5 sentences, ~50-100 words)
        assert 40 <= quick_words <= 150, f"Quick should be 40-150 words, got {quick_words}"

        # Detailed should be longest (>100 words)
        assert detailed_words >= 80, f"Detailed should be >=80 words, got {detailed_words}"

        # Verify ordering: inline < quick < detailed
        assert inline_words < quick_words, "Inline should be shorter than quick"
        assert quick_words < detailed_words, "Quick should be shorter than detailed"
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest tests/integration/test_analyzer_tool.py::TestMultiReportGeneration -v`
Expected: FAIL with "TypeError: generate_uncertainty_report() missing 1 required positional argument: 'analysis_type'" or similar

**Step 3: Commit failing test**

```bash
git add tests/integration/test_analyzer_tool.py
git commit -m "test: add test for multi-report generation (RED)"
```

### Task 2.2: Implement Multi-Report Generation

**Files:**
- Modify: `src/uvisbox_assistant/tools/analyzer_tools.py:148-240`

**Step 1: Update function signature (line 148-151)**

Replace:

```python
def generate_uncertainty_report(
    processed_statistics: dict,
    analysis_type: str = "quick"
) -> Dict:
```

With:

```python
def generate_uncertainty_report(
    processed_statistics: dict
) -> Dict:
```

**Step 2: Replace function body (lines 152-240)**

Replace entire function body with:

```python
    """
    Generate natural language uncertainty analysis reports for all three formats.

    Uses LLM to interpret statistical summaries and generate reports in three formats:
    - inline: 1 sentence summary of uncertainty level
    - quick: 3-5 sentence overview
    - detailed: Full report with median, band, and outlier analysis

    Args:
        processed_statistics: Structured dict from compute_functional_boxplot_statistics

    Returns:
        Dict with:
        - status: "success" or "error"
        - message: User-friendly confirmation
        - reports: Dictionary with all three report types {"inline": "...", "quick": "...", "detailed": "..."}
    """
    try:
        # Validate input structure
        is_valid, error_msg = validate_processed_statistics(processed_statistics)
        if not is_valid:
            return {
                "status": "error",
                "message": f"Invalid processed_statistics: {error_msg}"
            }

        # Convert statistics summary to JSON string for prompts
        statistics_json = json.dumps(processed_statistics, indent=2)

        # Create Gemini model (no tools needed for text generation)
        from langchain_google_genai import ChatGoogleGenerativeAI

        model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.3  # Slight creativity for natural language
        )

        # Generate all three report types
        reports = {}
        word_counts = {}

        for analysis_type in ["inline", "quick", "detailed"]:
            # Get appropriate prompt template
            prompt_template = _get_prompt_for_analysis_type(analysis_type)
            prompt = prompt_template.format(statistics_json=statistics_json)

            # Generate report
            response = model.invoke([HumanMessage(content=prompt)])
            report_text = response.content.strip()

            # Validate output length
            word_count = len(report_text.split())

            if analysis_type == "inline" and word_count > 40:
                return {
                    "status": "error",
                    "message": f"Inline report too long ({word_count} words). Expected ~15-30 words."
                }
            elif analysis_type == "quick" and word_count > 150:
                return {
                    "status": "error",
                    "message": f"Quick report too long ({word_count} words). Expected 50-100 words."
                }

            reports[analysis_type] = report_text
            word_counts[analysis_type] = word_count

        # Format summary message
        summary = f"inline: {word_counts['inline']} words, quick: {word_counts['quick']} words, detailed: {word_counts['detailed']} words"

        return {
            "status": "success",
            "message": f"Generated all uncertainty reports ({summary})",
            "reports": reports
        }

    except Exception as e:
        tb_str = traceback.format_exc()
        return {
            "status": "error",
            "message": f"Error generating reports: {str(e)}",
            "_error_details": {
                "exception": e,
                "traceback": tb_str
            }
        }
```

**Step 3: Run test to verify it passes**

Run: `poetry run pytest tests/integration/test_analyzer_tool.py::TestMultiReportGeneration -v`
Expected: PASS (both tests pass)

**Step 4: Commit implementation**

```bash
git add src/uvisbox_assistant/tools/analyzer_tools.py
git commit -m "feat: generate all three report types in single analyzer call (GREEN)"
```

### Task 2.3: Update Analyzer Tool Schema

**Files:**
- Modify: `src/uvisbox_assistant/tools/analyzer_tools.py:250-272`

**Step 1: Update tool schema**

Replace lines 250-272:

```python
ANALYZER_TOOL_SCHEMAS = [
    {
        "name": "generate_uncertainty_report",
        "description": (
            "Generate a natural language uncertainty analysis report from statistical summaries. "
            "IMPORTANT: You must call compute_functional_boxplot_statistics FIRST to compute statistics. "
            "This tool will automatically use the statistics from that computation. "
            "Do NOT try to pass statistics manually - just specify the analysis_type."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "analysis_type": {
                    "type": "string",
                    "description": "Report format: 'inline' (1 sentence), 'quick' (3-5 sentences), or 'detailed' (full report)",
                    "enum": ["inline", "quick", "detailed"],
                    "default": "quick"
                }
            },
            "required": []
        }
    }
]
```

With:

```python
ANALYZER_TOOL_SCHEMAS = [
    {
        "name": "generate_uncertainty_report",
        "description": (
            "Generate all three types of natural language uncertainty analysis reports "
            "(inline, quick, detailed) from statistical summaries in a single call. "
            "IMPORTANT: You must call compute_functional_boxplot_statistics FIRST to compute statistics. "
            "This tool will automatically use the statistics from that computation and generate all three report formats. "
            "Do NOT call this tool multiple times - it generates all formats at once. "
            "After this call succeeds, all three reports are available in state for instant retrieval."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]
```

**Step 2: Test schema is valid JSON**

Run:
```bash
python -c "
from uvisbox_assistant.tools.analyzer_tools import ANALYZER_TOOL_SCHEMAS
import json
print('Schema valid:', len(ANALYZER_TOOL_SCHEMAS[0]['parameters']['properties']) == 0)
"
```
Expected: `Schema valid: True`

**Step 3: Commit schema changes**

```bash
git add src/uvisbox_assistant/tools/analyzer_tools.py
git commit -m "refactor: update analyzer tool schema to remove analysis_type parameter"
```

---

## Phase 3: Node Execution Changes

### Task 3.1: Update call_analyzer_tool Node

**Files:**
- Modify: `src/uvisbox_assistant/core/nodes.py:427-432`

**Step 1: Update result handling in call_analyzer_tool**

Replace lines 427-432:

```python
        if result.get("status") == "success" and "report" in result:
            execution_entry["status"] = "success"
            # Extract report and analysis type from result
            report = result["report"]
            analysis_type = result.get("analysis_type", "quick")
            state_updates.update(update_state_with_analysis(state, report, analysis_type))
```

With:

```python
        if result.get("status") == "success" and "reports" in result:
            execution_entry["status"] = "success"
            # Extract all three reports from result
            reports = result["reports"]  # {"inline": "...", "quick": "...", "detailed": "..."}
            state_updates.update(update_state_with_analysis(state, reports))
```

**Step 2: Test node execution (manual verification)**

Run:
```bash
python -c "
from uvisbox_assistant.core.state import GraphState, create_initial_state
print('Import successful')
"
```
Expected: `Import successful`

**Step 3: Commit node changes**

```bash
git add src/uvisbox_assistant/core/nodes.py
git commit -m "refactor: update call_analyzer_tool to handle reports dictionary"
```

---

## Phase 4: Model Prompt Changes

### Task 4.1: Update System Prompt - Analysis Report Access

**Files:**
- Modify: `src/uvisbox_assistant/llm/model.py:17-106`

**Step 1: Add new "Analysis Report Access" section after line 58**

After the existing "Critical Tool Sequence Rules" section (around line 58), add this new section:

```python
Analysis Report Access:
- When analyzer tool succeeds, all three report types are stored in state
- Available types: "inline" (1 sentence), "quick" (3-5 sentences), "detailed" (full report)
- To show a report, simply present the appropriate type from stored reports
- NO need to call analyzer again - reports are already available

Smart Intent Detection for Analysis Requests:
- "show summary" / "show the analysis" → Present existing report (default to "quick")
- "show short/brief summary" / "inline summary" → Present "inline" report
- "show detailed analysis" / "detailed summary" → Present "detailed" report
- "generate new summary" / "regenerate analysis" → Call statistics + analyzer tools again
- If no reports exist yet → Call statistics + analyzer tools in sequence

IMPORTANT: If analysis_reports exists in state, NEVER call analyzer tool again
unless user explicitly requests "new" or "regenerate". Just retrieve and present.
```

This should be inserted between the "Critical Tool Sequence Rules" section and the "IMPORTANT - Presenting Analysis Results" section.

**Step 2: Update "Critical Tool Sequence Rules" section (around lines 50-58)**

Replace the existing "Critical Tool Sequence Rules" text with:

```python
Critical Tool Sequence Rules:
- To generate analysis reports, you MUST follow this sequence:
  1. FIRST: Call compute_functional_boxplot_statistics with the data_path
  2. THEN: Call generate_uncertainty_report (no parameters needed)
  3. All three report types are now stored - present the requested type
- The analyzer tool generates all three types at once (inline, quick, detailed)
- NEVER call analyzer multiple times - it's expensive and unnecessary
- If user requests different format, retrieve from stored analysis_reports
- Only regenerate if user explicitly says "new" or "regenerate"
```

**Step 3: Update "IMPORTANT - Presenting Analysis Results" section (around lines 60-67)**

Replace with:

```python
IMPORTANT - Presenting Analysis Results:
- After generate_uncertainty_report succeeds, THREE reports are stored in analysis_reports
- Choose which report to present based on user request:
  * Default: "quick" (if not specified)
  * "inline" for brief one-sentence summary
  * "detailed" for comprehensive analysis
- Present it clearly with appropriate context:
  "Here is the [inline/quick/detailed] uncertainty analysis:

  [report text]"
- Do NOT just say "I generated a report" - actually show the report content
```

**Step 4: Test prompt generation**

Run:
```bash
python -c "
from uvisbox_assistant.llm.model import get_system_prompt
prompt = get_system_prompt()
assert 'analysis_reports' in prompt, 'Should mention analysis_reports'
assert 'all three report types' in prompt, 'Should mention all three types'
print('Prompt updated successfully')
"
```
Expected: `Prompt updated successfully`

**Step 5: Commit prompt changes**

```bash
git add src/uvisbox_assistant/llm/model.py
git commit -m "refactor: update system prompt for multi-report workflow and smart intent detection"
```

---

## Phase 5: Hybrid Control for Report Switching

### Task 5.1: Add Report Retrieval Patterns to Command Parser

**Files:**
- Modify: `src/uvisbox_assistant/session/command_parser.py:64-116`

**Step 1: Add report retrieval patterns**

After line 115 (after the "method" pattern), add these new patterns:

```python
    # Pattern 15: "inline summary" / "show inline summary"
    if text in ['show inline summary', 'inline summary']:
        return SimpleCommand('report_type', 'inline')

    # Pattern 16: "quick summary" / "show quick summary"
    if text in ['show quick summary', 'quick summary']:
        return SimpleCommand('report_type', 'quick')

    # Pattern 17: "detailed summary" / "show detailed summary"
    if text in ['show detailed summary', 'detailed summary']:
        return SimpleCommand('report_type', 'detailed')
```

**Step 2: Test pattern matching**

Run:
```bash
python -c "
from uvisbox_assistant.session.command_parser import parse_simple_command

cmd1 = parse_simple_command('inline summary')
assert cmd1 is not None and cmd1.param_name == 'report_type' and cmd1.value == 'inline'

cmd2 = parse_simple_command('show quick summary')
assert cmd2 is not None and cmd2.param_name == 'report_type' and cmd2.value == 'quick'

cmd3 = parse_simple_command('detailed summary')
assert cmd3 is not None and cmd3.param_name == 'report_type' and cmd3.value == 'detailed'

print('Pattern matching works correctly')
"
```
Expected: `Pattern matching works correctly`

**Step 3: Commit parser changes**

```bash
git add src/uvisbox_assistant/session/command_parser.py
git commit -m "feat: add report retrieval patterns to command parser"
```

### Task 5.2: Implement Report Retrieval in Hybrid Control

**Files:**
- Modify: `src/uvisbox_assistant/session/hybrid_control.py`

**Step 1: Add execute_report_retrieval function**

After the `execute_simple_command` function (around line 80), add this new function:

```python
def execute_report_retrieval(
    command: SimpleCommand,
    current_state: dict
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Retrieve a specific report type from state.

    Args:
        command: Parsed simple command with param_name='report_type'
        current_state: Current conversation state

    Returns:
        Tuple of (success, report_text, message)
        - success: True if report retrieved, False if not available
        - report_text: The report content (str)
        - message: Status message
    """
    if command.param_name != 'report_type':
        return False, None, "Not a report retrieval command"

    analysis_reports = current_state.get("analysis_reports")

    if not analysis_reports:
        return False, None, "No analysis reports available yet"

    report_type = command.value
    report_text = analysis_reports.get(report_type)

    if not report_text:
        return False, None, f"Report type '{report_type}' not found"

    return True, report_text, f"Retrieved {report_type} report"
```

**Step 2: Update execute_simple_command to route to report retrieval**

Replace the beginning of `execute_simple_command` function (lines 9-30) with:

```python
def execute_simple_command(
    command_str: str,
    current_state: dict
) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Try to execute a command as a simple parameter update or report retrieval.

    Args:
        command_str: User's command string
        current_state: Current conversation state with last_vis_params and analysis_reports

    Returns:
        Tuple of (success, result, message)
        - success: True if command was handled, False if needs full graph
        - result: Result from operation (updated_params dict OR report_text str)
        - message: Status message
    """
    # Try to parse as simple command
    command = parse_simple_command(command_str)

    if command is None:
        return False, None, "Not a simple command"

    # Route to appropriate handler
    if command.param_name == 'report_type':
        return execute_report_retrieval(command, current_state)

    # Existing visualization parameter update logic continues below...
    # Need existing vis params to update
    last_vis_params = current_state.get("last_vis_params")
```

**Step 3: Test report retrieval function**

Run:
```bash
python -c "
from uvisbox_assistant.session.hybrid_control import execute_report_retrieval
from uvisbox_assistant.session.command_parser import SimpleCommand

# Test with reports available
state = {
    'analysis_reports': {
        'inline': 'Low uncertainty',
        'quick': 'The data shows low uncertainty...',
        'detailed': 'Full detailed analysis...'
    }
}
cmd = SimpleCommand('report_type', 'inline')
success, report, msg = execute_report_retrieval(cmd, state)
assert success == True
assert report == 'Low uncertainty'
assert 'inline' in msg

# Test with no reports
empty_state = {}
success2, report2, msg2 = execute_report_retrieval(cmd, empty_state)
assert success2 == False
assert report2 is None

print('Report retrieval works correctly')
"
```
Expected: `Report retrieval works correctly`

**Step 4: Commit hybrid control changes**

```bash
git add src/uvisbox_assistant/session/hybrid_control.py
git commit -m "feat: add report retrieval to hybrid control system"
```

### Task 5.3: Update Conversation Handler for Report Retrieval

**Files:**
- Modify: `src/uvisbox_assistant/session/conversation.py:63-80`

**Step 1: Update hybrid control handling in send_message**

Replace lines 63-80 (the hybrid control section) with:

```python
        # Try hybrid control first (only if we have existing state)
        if self.state and is_hybrid_eligible(user_message):
            success, result, message = execute_simple_command(
                user_message,
                self.state
            )

            if success:
                vprint(f"[HYBRID] {message}")

                # Check if result is a report (string) or vis params (dict)
                if isinstance(result, str):
                    # Report retrieval - format and return as AI message
                    # Extract report type from message (e.g., "Retrieved inline report")
                    report_type = message.split()[1]  # Gets "inline", "quick", or "detailed"
                    response_text = f"Here is the {report_type} uncertainty analysis:\n\n{result}"

                    # Create AI message and update state
                    ai_message = AIMessage(content=response_text)
                    self.state["messages"].append(HumanMessage(content=user_message))
                    self.state["messages"].append(ai_message)

                    return response_text
                else:
                    # Visualization parameter update - existing logic
                    self.state["last_vis_params"] = result

                    # Create user message
                    user_msg = HumanMessage(content=user_message)
                    self.state["messages"].append(user_msg)

                    # Create AI message
                    ai_response = AIMessage(content=message)
                    self.state["messages"].append(ai_response)

                    self.turn_count += 1
                    return message
```

**Step 2: Test import**

Run:
```bash
python -c "
from uvisbox_assistant.session.conversation import ConversationSession
print('Import successful')
"
```
Expected: `Import successful`

**Step 3: Commit conversation changes**

```bash
git add src/uvisbox_assistant/session/conversation.py
git commit -m "feat: handle report retrieval in conversation hybrid control"
```

---

## Phase 6: Integration Testing

### Task 6.1: Write Integration Test for Report Switching

**Files:**
- Create: `tests/integration/test_report_switching.py`

**Step 1: Create test file**

Create `tests/integration/test_report_switching.py` with:

```python
"""Integration tests for report switching via hybrid control (v0.3.2)"""

import pytest
from uvisbox_assistant.session.conversation import ConversationSession


class TestReportSwitchingWorkflow:
    """Test users can switch between report types after initial generation"""

    def test_generate_and_switch_report_types(self):
        """
        Test complete workflow:
        1. Generate data and statistics
        2. Generate all three reports
        3. Switch between report types via hybrid control
        """
        session = ConversationSession()

        # Step 1: Generate curves and request detailed analysis
        response1 = session.send_message(
            "generate 100 curves with 50 points each, "
            "compute statistics, and show detailed summary"
        )
        assert "detailed" in response1.lower() or len(response1.split()) > 80
        assert session.state.get("analysis_reports") is not None
        assert "inline" in session.state["analysis_reports"]
        assert "quick" in session.state["analysis_reports"]
        assert "detailed" in session.state["analysis_reports"]

        # Step 2: Switch to inline summary (should be instant via hybrid control)
        response2 = session.send_message("inline summary")
        assert len(response2.split()) < 50  # Inline is short
        assert "inline" in response2.lower()
        # Should not regenerate - reports still in state
        assert session.state["analysis_reports"] is not None

        # Step 3: Switch to quick summary
        response3 = session.send_message("show quick summary")
        assert 40 < len(response3.split()) < 150  # Quick is medium
        assert "quick" in response3.lower()

        # Step 4: Switch back to detailed
        response4 = session.send_message("detailed summary")
        assert len(response4.split()) > 80  # Detailed is long
        assert "detailed" in response4.lower()

    def test_report_switching_without_regeneration(self):
        """Verify switching doesn't call analyzer tool again"""
        session = ConversationSession()

        # Generate initial reports
        session.send_message(
            "generate 50 curves, compute statistics, show quick summary"
        )
        initial_reports = session.state["analysis_reports"].copy()

        # Switch to different type
        session.send_message("inline summary")

        # Verify reports are unchanged (not regenerated)
        assert session.state["analysis_reports"] == initial_reports

    def test_hybrid_control_for_report_retrieval(self):
        """Verify report switching uses hybrid control (fast path)"""
        session = ConversationSession()

        # Generate reports
        session.send_message(
            "generate 30 curves, compute statistics, show detailed summary"
        )

        # Track message count before switching
        message_count_before = len(session.state["messages"])

        # Switch report type
        response = session.send_message("inline summary")

        # Hybrid control should add exactly 2 messages (HumanMessage, AIMessage)
        # No tool calls, so should be fast
        message_count_after = len(session.state["messages"])
        assert message_count_after == message_count_before + 2

        # Verify response is correct
        assert "inline" in response.lower()
        assert len(response.split()) < 50


class TestReportRegenerationDetection:
    """Test smart detection of regenerate vs retrieve intent"""

    def test_explicit_regeneration_request(self):
        """User explicitly asks for 'new' or 'regenerate' - should call analyzer again"""
        session = ConversationSession()

        # Generate initial reports
        session.send_message(
            "generate 50 curves, compute statistics, show quick summary"
        )
        initial_inline = session.state["analysis_reports"]["inline"]

        # Request regeneration (note: this will actually regenerate via full graph)
        response = session.send_message("generate new summary")

        # Should have called analyzer again (reports might differ due to LLM variance)
        # At minimum, state should still have all three types
        assert session.state["analysis_reports"] is not None
        assert "inline" in session.state["analysis_reports"]
        assert "quick" in session.state["analysis_reports"]
        assert "detailed" in session.state["analysis_reports"]

    def test_retrieve_existing_summary(self):
        """User says 'show summary' - should retrieve existing, not regenerate"""
        session = ConversationSession()

        # Generate reports
        session.send_message(
            "generate 50 curves, compute statistics, show detailed summary"
        )
        initial_reports = session.state["analysis_reports"].copy()

        # Request to show summary (not regenerate)
        response = session.send_message("show summary")

        # Should retrieve existing (default to quick)
        assert session.state["analysis_reports"] == initial_reports
        assert "quick" in response.lower() or len(response.split()) < 150


class TestNoReportsAvailable:
    """Test behavior when user requests report before generating"""

    def test_report_request_before_generation(self):
        """User requests report before any analysis - should fail gracefully"""
        session = ConversationSession()

        # Request report without generating data
        response = session.send_message("show inline summary")

        # Should explain no reports available yet
        assert "no" in response.lower() or "not" in response.lower() or "yet" in response.lower()
```

**Step 2: Run tests to verify they pass**

Run: `poetry run pytest tests/integration/test_report_switching.py -v`
Expected: All tests pass (may take time due to LLM calls)

**Step 3: Commit integration tests**

```bash
git add tests/integration/test_report_switching.py
git commit -m "test: add integration tests for report switching workflow"
```

### Task 6.2: Update Existing Analyzer Tests

**Files:**
- Modify: `tests/integration/test_analyzer_tool.py`

**Step 1: Update existing tests to expect reports dict**

Find and update any existing tests that check for `"report"` in result to check for `"reports"` instead.

Look for patterns like:
```python
assert "report" in result
```

Replace with:
```python
assert "reports" in result
assert isinstance(result["reports"], dict)
```

**Step 2: Run all analyzer tests**

Run: `poetry run pytest tests/integration/test_analyzer_tool.py -v`
Expected: All tests pass

**Step 3: Commit test updates**

```bash
git add tests/integration/test_analyzer_tool.py
git commit -m "test: update analyzer tests to expect reports dictionary"
```

---

## Phase 7: Update Version and Documentation

### Task 7.1: Update Version Number

**Files:**
- Modify: `pyproject.toml`

**Step 1: Update version in pyproject.toml**

Find the line with `version = "0.3.1"` and change to:

```toml
version = "0.3.2"
```

**Step 2: Commit version change**

```bash
git add pyproject.toml
git commit -m "chore: bump version to 0.3.2"
```

### Task 7.2: Update CHANGELOG

**Files:**
- Modify: `CHANGELOG.md`

**Step 1: Add v0.3.2 entry to CHANGELOG**

At the top of CHANGELOG.md (after the header), add:

```markdown
## [0.3.2] - 2025-11-05

### Added
- Multi-report generation: Analyzer now generates all three report types (inline, quick, detailed) in a single call
- Hybrid control for instant report switching: Users can switch between report types with commands like "inline summary", "quick summary", "detailed summary"
- Smart intent detection: Model distinguishes between "show summary" (retrieve existing) and "generate new summary" (regenerate)

### Changed
- State structure: `analysis_report` (str) + `analysis_type` (str) → `analysis_reports` (Dict[str, str])
- Analyzer tool signature: Removed `analysis_type` parameter (always generates all three)
- System prompt: Updated workflow descriptions and tool usage instructions for multi-report system

### Fixed
- **Issue #1**: Users can now request different summary types after initial generation without "cannot regenerate" errors
- Report regeneration: Users couldn't switch between inline/quick/detailed summaries after first request

### Technical Details
- `generate_uncertainty_report()` now returns `{"reports": {"inline": "...", "quick": "...", "detailed": "..."}}`
- Hybrid control patterns: "inline summary", "show quick summary", "detailed summary" for instant retrieval
- State field `analysis_reports` persists across conversation turns until statistics regenerated
```

**Step 2: Commit CHANGELOG**

```bash
git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for v0.3.2 release"
```

---

## Phase 8: Final Verification

### Task 8.1: Run Full Test Suite

**Files:**
- None (verification only)

**Step 1: Run all tests**

Run: `poetry run pytest tests/ --ignore=tests/e2e/ -v`
Expected: All tests pass (may have some expected failures from baseline)

**Step 2: Run specific v0.3.2 tests**

Run:
```bash
poetry run pytest tests/integration/test_analyzer_tool.py::TestMultiReportGeneration -v
poetry run pytest tests/integration/test_report_switching.py -v
```
Expected: All v0.3.2 tests pass

**Step 3: Verify no regressions**

Compare test results to baseline (before changes). New failures = regressions to fix.

### Task 8.2: Manual Smoke Test

**Files:**
- None (manual testing)

**Step 1: Test basic workflow**

```bash
poetry run python -m uvisbox_assistant
```

Then test these commands:
1. "generate 50 curves with 30 points, compute statistics, show detailed summary"
2. "inline summary"
3. "show quick summary"
4. "detailed summary"

Expected: All commands work, switching is instant, reports are appropriate lengths

**Step 2: Test regeneration**

Continue in same session:
1. "generate new summary"

Expected: Should regenerate statistics and reports

**Step 3: Test error case**

New session:
1. "show inline summary"

Expected: Should explain no reports available yet

---

## Completion Checklist

- [ ] Phase 1: State structure updated (3 tasks)
- [ ] Phase 2: Analyzer tool updated (3 tasks)
- [ ] Phase 3: Node execution updated (1 task)
- [ ] Phase 4: Model prompt updated (1 task)
- [ ] Phase 5: Hybrid control added (3 tasks)
- [ ] Phase 6: Integration tests added (2 tasks)
- [ ] Phase 7: Version and docs updated (2 tasks)
- [ ] Phase 8: Final verification (2 tasks)

**Total: 17 tasks across 8 phases**

---

## Troubleshooting

### Issue: Tests fail with "analysis_type not found"
**Solution:** Ensure all references to `analysis_type` state field are removed

### Issue: Hybrid control not detecting report commands
**Solution:** Check command_parser.py patterns match exactly (case-sensitive)

### Issue: Reports not stored in state
**Solution:** Verify update_state_with_analysis receives dict, not individual strings

### Issue: LLM still calls analyzer multiple times
**Solution:** Check system prompt emphasizes "NEVER call analyzer again if reports exist"

---

## Post-Implementation

After completing this plan:

1. **Merge to main:**
   - Create PR from `v0.3.2-analyzer-improvement` branch
   - Review all changes
   - Run full test suite
   - Merge to main

2. **Tag release:**
   ```bash
   git tag v0.3.2
   git push origin v0.3.2
   ```

3. **Clean up worktree:**
   Use @superpowers:finishing-a-development-branch skill

4. **User documentation:**
   Update user-facing docs with examples of report switching
