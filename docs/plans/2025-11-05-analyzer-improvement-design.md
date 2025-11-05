# v0.3.2 Feature Design: Analyzer Improvement

**Date:** 2025-11-05
**Author:** Brainstorming session with user
**Version:** v0.3.2

## Problem Statement

**Issue:** When a user requests a different type of summary after already receiving one (e.g., "show short summary" after getting a detailed report), the assistant incorrectly responds: "I am sorry, I cannot fulfill this request. I have already generated a detailed report. I am unable to generate a short summary based on the previous analysis."

**Root Cause:**
1. The analyzer tool currently generates only one report type at a time
2. The system prompt emphasizes the sequence "statistics FIRST, then analyzer", making the model think it can't regenerate
3. No mechanism exists to distinguish between "retrieve existing report" vs "regenerate new report"

**User Impact:** Users cannot flexibly switch between report formats without regenerating statistics, creating a poor conversational experience.

## Design Goals

1. **Eliminate regeneration errors** - Users should be able to request any summary type at any time
2. **Efficient report generation** - Generate all three types once, retrieve instantly on subsequent requests
3. **Smart intent detection** - Model determines whether to retrieve existing or regenerate based on user phrasing
4. **Hybrid control support** - Fast report type switching without LLM calls for explicit commands
5. **Backward compatibility** - Clean break on new branch (v0.3.2)

## Architecture Overview

### Current Flow
```
User: "show detailed summary"
  ↓
statistics_tool (compute stats) → processed_statistics stored
  ↓
analyzer_tool(analysis_type="detailed") → single report stored
  ↓
User: "show short summary"
  ↓
Model: "ERROR: Cannot regenerate"
```

### New Flow
```
User: "show detailed summary"
  ↓
statistics_tool (compute stats) → processed_statistics stored
  ↓
analyzer_tool() → ALL THREE reports generated at once
  ↓
analysis_reports = {"inline": "...", "quick": "...", "detailed": "..."}
  ↓
Model: presents "detailed" report
  ↓
User: "show inline summary"
  ↓
HYBRID CONTROL: instant retrieval from analysis_reports["inline"]
  ↓
Model: presents "inline" report (no tool calls)
```

## Detailed Design

### 1. State Structure Changes

**File:** `/src/uvisbox_assistant/core/state.py`

**Current structure:**
```python
analysis_report: Optional[str]
analysis_type: Optional[str]
```

**New structure:**
```python
analysis_reports: Optional[Dict[str, str]]  # {"inline": "...", "quick": "...", "detailed": "..."}
```

**Changes:**
- Remove `analysis_type` field
- Rename and retype `analysis_report` → `analysis_reports` (str → Dict[str, str])
- Initialize to `None` in `create_initial_state()`

**State lifecycle:**
1. Initial: `analysis_reports = None`
2. After first analysis: `analysis_reports = {"inline": "...", "quick": "...", "detailed": "..."}`
3. Persists until statistics regenerated

**Update function signature:**
```python
def update_state_with_analysis(state: GraphState, reports: Dict[str, str]) -> dict:
    """
    Update state after successful analyzer tool execution.

    Args:
        state: Current graph state
        reports: Dictionary with all three report types

    Returns:
        Dict of updates to merge into state
    """
    return {
        "analysis_reports": reports,
        "error_count": 0
    }
```

### 2. Analyzer Tool Changes

**File:** `/src/uvisbox_assistant/tools/analyzer_tools.py`

**Current signature:**
```python
def generate_uncertainty_report(
    processed_statistics: dict,
    analysis_type: str = "quick"
) -> Dict
```

**New signature:**
```python
def generate_uncertainty_report(
    processed_statistics: dict
) -> Dict
```

**Behavior changes:**
- Remove `analysis_type` parameter
- Call LLM three times (once for each type: inline, quick, detailed)
- Return all three reports in single result:
  ```python
  {
      "status": "success",
      "message": "Generated all uncertainty reports (inline: X words, quick: Y words, detailed: Z words)",
      "reports": {
          "inline": "...",
          "quick": "...",
          "detailed": "..."
      }
  }
  ```

**Tool schema update:**
```python
{
    "name": "generate_uncertainty_report",
    "description": (
        "Generate all three types of natural language uncertainty analysis reports "
        "(inline, quick, detailed) from statistical summaries. "
        "IMPORTANT: You must call compute_functional_boxplot_statistics FIRST. "
        "This tool will automatically use the statistics from that computation. "
        "Do NOT call this tool multiple times - it generates all formats at once."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": []
    }
}
```

**Implementation notes:**
- Use existing `INLINE_REPORT_PROMPT`, `QUICK_REPORT_PROMPT`, `DETAILED_REPORT_PROMPT`
- Generate reports sequentially (inline → quick → detailed)
- Validate each output before proceeding
- If any generation fails, return error with partial results

### 3. Model Prompt Changes

**File:** `/src/uvisbox_assistant/llm/model.py`

**Updates to system prompt:**

1. **Update workflow patterns (lines 34-58):**
   - Remove mentions of `analysis_type` parameter
   - Update tool sequence description

2. **Add new section: "Analysis Report Access"** (insert after line 58):
   ```
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

3. **Update "Critical Tool Sequence Rules" (lines 50-58):**
   ```
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

4. **Update "IMPORTANT - Presenting Analysis Results" (lines 60-67):**
   ```
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

### 4. Node Execution Changes

**File:** `/src/uvisbox_assistant/core/nodes.py`

**Update `call_analyzer_tool()` function:**

**Current behavior (lines 427-432):**
```python
if result.get("status") == "success" and "report" in result:
    execution_entry["status"] = "success"
    report = result["report"]
    analysis_type = result.get("analysis_type", "quick")
    state_updates.update(update_state_with_analysis(state, report, analysis_type))
```

**New behavior:**
```python
if result.get("status") == "success" and "reports" in result:
    execution_entry["status"] = "success"
    # Extract all three reports from result
    reports = result["reports"]  # {"inline": "...", "quick": "...", "detailed": "..."}
    state_updates.update(update_state_with_analysis(state, reports))
```

### 5. Hybrid Control for Report Switching

**File:** `/src/uvisbox_assistant/session/command_parser.py`

**Add new patterns to `parse_simple_command()`:**
```python
# Pattern: "inline summary" / "show inline summary"
if text in ['show inline summary', 'inline summary']:
    return SimpleCommand('report_type', 'inline')

# Pattern: "quick summary" / "show quick summary"
if text in ['show quick summary', 'quick summary']:
    return SimpleCommand('report_type', 'quick')

# Pattern: "detailed summary" / "show detailed summary"
if text in ['show detailed summary', 'detailed summary']:
    return SimpleCommand('report_type', 'detailed')
```

**File:** `/src/uvisbox_assistant/session/hybrid_control.py`

**Add new function:**
```python
def execute_report_retrieval(
    command: SimpleCommand,
    current_state: dict
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Retrieve a specific report type from state.

    Args:
        command: Parsed simple command
        current_state: Current conversation state

    Returns:
        Tuple of (success, report_text, message)
        - success: True if report retrieved, False if not available
        - report_text: The report content
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

**Update `execute_simple_command()` to delegate:**
```python
def execute_simple_command(
    command_str: str,
    current_state: dict
) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Try to execute a command as a simple parameter update or report retrieval.

    Returns:
        Tuple of (success, result, message)
        - For vis updates: result is updated_params dict
        - For report retrieval: result is report_text string
    """
    command = parse_simple_command(command_str)

    if command is None:
        return False, None, "Not a simple command"

    # Route to appropriate handler
    if command.param_name == 'report_type':
        return execute_report_retrieval(command, current_state)

    # Existing visualization parameter update logic
    last_vis_params = current_state.get("last_vis_params")

    if not last_vis_params:
        return False, None, "No previous visualization to update"

    # ... rest of existing code ...
```

**File:** `/src/uvisbox_assistant/session/conversation.py`

**Update `send_message()` to handle report retrieval:**
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
            response_text = f"Here is the {message.split()[1]} report:\n\n{result}"

            # Create AI message and update state
            ai_message = AIMessage(content=response_text)
            self.state["messages"].append(HumanMessage(content=user_message))
            self.state["messages"].append(ai_message)

            return response_text
        else:
            # Visualization parameter update - existing logic
            self.state["last_vis_params"] = result
            # ... existing code ...
```

## Implementation Plan

### Phase 1: State and Core Changes
1. Update `GraphState` in `state.py`
2. Update `create_initial_state()` and `update_state_with_analysis()`
3. Update `call_analyzer_tool()` in `nodes.py`

### Phase 2: Analyzer Tool Changes
1. Modify `generate_uncertainty_report()` to generate all three types
2. Update tool schema to remove `analysis_type` parameter
3. Update validation and error handling

### Phase 3: Model Prompt Changes
1. Update system prompt with new workflow descriptions
2. Add "Analysis Report Access" section
3. Update tool sequence rules and presentation guidelines

### Phase 4: Hybrid Control Extension
1. Add report retrieval patterns to `command_parser.py`
2. Implement `execute_report_retrieval()` in `hybrid_control.py`
3. Update `execute_simple_command()` to route correctly
4. Update `conversation.py` to handle report retrieval results

### Phase 5: Testing and Validation
1. Test report generation (all three types)
2. Test report retrieval via hybrid control
3. Test smart intent detection via model
4. Test regeneration on explicit request
5. Integration tests for full workflows

## Testing Strategy

### Unit Tests
- `test_state.py`: Verify state structure changes
- `test_analyzer_tools.py`: Verify all three reports generated
- `test_command_parser.py`: Verify report retrieval patterns
- `test_hybrid_control.py`: Verify report retrieval logic

### Integration Tests
- Test workflow: statistics → analyzer → all reports stored
- Test retrieval: "inline summary", "quick summary", "detailed summary"
- Test smart detection: "show summary" vs "generate new summary"
- Test persistence: reports available across conversation turns

### User Acceptance Tests
1. "Generate curves and plot functional boxplot, show detailed description"
   → Should generate all three reports, present detailed
2. "Show inline summary"
   → Should instantly retrieve inline report (no tool calls)
3. "Quick summary"
   → Should instantly retrieve quick report
4. "Generate a new summary"
   → Should regenerate statistics and analyzer

## Breaking Changes

1. **State field changes:**
   - `analysis_report` (str) → `analysis_reports` (Dict[str, str])
   - `analysis_type` (str) → removed

2. **Tool signature changes:**
   - `generate_uncertainty_report(processed_statistics, analysis_type)` → `generate_uncertainty_report(processed_statistics)`

3. **Tool result format:**
   - Old: `{"report": "...", "analysis_type": "quick"}`
   - New: `{"reports": {"inline": "...", "quick": "...", "detailed": "..."}}`

## Migration Notes

- Create new feature branch for v0.3.2
- No backward compatibility needed (clean break)
- Update all tests to use new structure
- Update documentation to reflect new behavior

## Success Criteria

1. ✅ User can request any summary type after initial generation
2. ✅ Hybrid control provides instant report switching
3. ✅ Model correctly detects retrieve vs regenerate intent
4. ✅ No "cannot regenerate" errors
5. ✅ All three report types generated in single analyzer call
6. ✅ Tests pass with new structure

## Future Enhancements

- Cache analyzer LLM calls to reduce latency
- Support custom report formats beyond inline/quick/detailed
- Add report comparison: "compare inline and detailed summaries"
- Add report history: track changes across regenerations
