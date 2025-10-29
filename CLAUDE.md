# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ChatUVisBox** is a natural language interface for the UVisBox uncertainty visualization library. It uses LangGraph to orchestrate a conversational AI agent (powered by Google Gemini) that translates natural language requests into data processing and visualization operations.

**Current State**: Phase 7 Complete (2025-10-28). Implementing phases sequentially per `plans/` directory.

**Completed Phases**:
- ✅ **Phase 1**: Tool definitions, schemas, data/vis tools with UVisBox wrappers (2025-10-26)
- ✅ **Phase 2**: LangGraph state management, model setup, core nodes (2025-10-26)
- ✅ **Phase 3**: Graph wiring, routing logic, end-to-end workflow (2025-10-26)
- ✅ **Phase 4**: End-to-end happy path tests, matplotlib verification, interactive testing (2025-10-27)
- ✅ **Phase 4.5**: Codebase restructure to professional Python package with Poetry (2025-10-27)
- ✅ **Phase 5**: Error handling, circuit breaker, context awareness, logging (2025-10-28)
- ✅ **Phase 6**: Multi-turn conversation with ConversationSession, interactive REPL (2025-10-28)
- ✅ **Phase 7**: Hybrid control for 10-15x faster parameter updates (2025-10-28)
- ✅ **Enhancements**: Vector field generation, API updates, dependency updates (2025-10-28)

## Architecture

### Core Design Pattern: Hybrid Control Model

The system uses a **two-tier execution model**:

1. **Full LangGraph Workflow** (for complex/ambiguous requests):
   - User Input → Model Node → Tool Dispatcher (data or vis) → Model Node → Response
   - Maintains conversation state across multi-turn interactions
   - Handles data loading, transformation, and visualization in sequence

2. **Hybrid Fast Path** (for simple parameter updates):
   - Direct pattern matching (e.g., "colormap plasma", "percentile 80")
   - Bypasses LangGraph for ~10x speed improvement
   - Updates `last_vis_params` and re-executes visualization directly

### Key Components

```
graph.py          - ✅ DONE: LangGraph StateGraph definition with conditional routing
state.py          - ✅ DONE: GraphState TypedDict: messages, current_data_path, last_vis_params, session_files, error_count
nodes.py          - ✅ DONE: Three core nodes with error handling: call_model, call_data_tool, call_vis_tool
routing.py        - ✅ DONE: Conditional logic with circuit breaker: route_after_model, route_after_tool
model.py          - ✅ DONE: ChatGoogleGenerativeAI with error recovery prompt and context awareness
utils.py          - ✅ DONE: Tool type detection and file management utilities
data_tools.py     - ✅ DONE: Functions: load_csv_to_numpy, generate_ensemble_curves, load_npy, generate_scalar_field_ensemble, generate_vector_field_ensemble
vis_tools.py      - ✅ DONE: UVisBox wrappers: plot_functional_boxplot, plot_curve_boxplot, probabilistic_marching_squares, plot_uncertainty_lobes, plot_contour_boxplot
config.py         - ✅ DONE: Configuration (API key, paths, DEFAULT_VIS_PARAMS)
logger.py         - ✅ DONE Phase 5: Logging infrastructure with file and console output
conversation.py   - ✅ DONE Phase 6: ConversationSession class for multi-turn conversations with Phase 7 hybrid control integration
command_parser.py - ✅ DONE Phase 7: Parse simple commands for hybrid control (127 lines)
hybrid_control.py - ✅ DONE Phase 7: Execute simple commands directly, 10-15x speedup (86 lines)
main.py           - Interactive REPL with command handling (/help, /context, /clear, /quit) (TODO: Phase 8)
```

### LangGraph Flow

```
START → call_model → [route_after_model]
                         ├─ data_tool → call_model (loop for multi-step)
                         ├─ vis_tool  → call_model (confirm to user)
                         └─ END (direct response)
```

### State Management

**GraphState fields**:
- `messages`: Full conversation history (List[BaseMessage])
- `current_data_path`: Path to most recent .npy file
- `last_vis_params`: Dict with `_tool_name`, `data_path`, and vis parameters
- `session_files`: List of temp files created (for cleanup)
- `error_count`: Circuit breaker (max 3 consecutive errors → END)

**Intermediate data**: All data transformations saved as `.npy` files in `temp/` directory with `_temp_*` prefix.

### Tool Schema Pattern (3-Tier Parameters)

- **Tier 1** (LLM-exposed): Simple params in tool schemas (e.g., `percentile`, `colormap`, `isovalue`)
- **Tier 2** (Hard-coded): Defaults in Python functions (e.g., `figsize=(10,8)`, `dpi=100`, `alpha=0.5`)
- **Tier 3** (Reserved): Future user preferences (not in MVP)

## Environment & Dependencies

### Required Environment Variable
- `GEMINI_API_KEY` must be set in system environment (not in `.env` file)
- Check with: `echo $GEMINI_API_KEY`
- See `ENVIRONMENT_SETUP.md` for detailed configuration instructions

### Conda Environment
```bash
conda activate agent  # Must have UVisBox installed here
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Critical Dependencies
- `langchain-google-genai` - Provides `ChatGoogleGenerativeAI` class
- `langgraph` - State graph orchestration
- `uvisbox` - Installed separately in conda env (not in requirements.txt)

## Development Workflow

### Implementation Phases (Sequential)

Follow `plans/README.md` for complete guidance. Phases must be completed in order:

**Milestone 1 (Days 1-5)**: Core Pipeline ✅ COMPLETE
- ✅ Phase 1: Create data_tools.py, vis_tools.py, config.py with tool schemas
- ✅ Phase 2: Create state.py, nodes.py, model.py
- ✅ Phase 3: Create graph.py with routing logic
- ✅ Phase 4: End-to-end happy path test
- ✅ Phase 4.5: Professional package structure with Poetry

**Milestone 2 (Days 6-8)**: Robustness ✅ COMPLETE
- ✅ Phase 5: Error handling with circuit breaker (COMPLETE 2025-10-28)
- ✅ Phase 6: Multi-turn conversation with ConversationSession (COMPLETE 2025-10-28)
- ✅ Phase 7: Hybrid control with command_parser.py (COMPLETE 2025-10-28)

**Milestone 3 (Days 9-11)**: Polish (0/3 complete)
- ⏭️ Phase 8: Session management with clear_session tool
- ⏭️ Phase 9: Comprehensive testing (pytest + manual)
- ⏭️ Phase 10: Documentation and packaging

### Temporary Verification Files

**IMPORTANT**: Completion reports and update summaries are temporary verification files:
- `PHASE_*_COMPLETION_REPORT.md` - Phase verification summaries
- `UPDATE_*.md` - API update documentation
- `*_SUMMARY.md` - Various update summaries

**Workflow**:
1. AI coding agent creates these during development for verification
2. Human developer reviews to verify correctness
3. **DELETE before committing** - these are NOT part of the codebase or documentation
4. Only keep actual code, tests, and permanent documentation (CLAUDE.md, TESTING.md, etc.)

**Purpose**: Provide detailed verification context for human review, then discard.

### Testing Commands

**⚠️ IMPORTANT: Gemini Free Tier Rate Limits**
- 30 requests per minute (using gemini-2.0-flash-lite)
- See `TESTING.md` and `RATE_LIMIT_FRIENDLY_TESTING.md` for details

**Recommended for development (respects rate limits):**
```bash
# Quick test - 9 API calls, ~5 seconds (RECOMMENDED)
python tests/test_graph_quick.py

# No API calls - instant validation
python tests/test_routing.py
python tests/test_phase1.py

# Interactive menu-driven testing - user-paced, 24+ scenarios (BEST FOR DEMOS)
python tests/interactive_test.py

# Full suite with automatic delays - ~5-7 minutes
python tests/run_tests_with_delays.py
```

**Individual phase tests:**
```bash
python tests/test_phase1.py           # Phase 1: 0 API calls
python tests/test_phase2.py           # Phase 2: 10-15 API calls (wait 60s between runs)
python tests/test_routing.py          # Phase 3: 0 API calls
python tests/test_graph.py            # Phase 3: 5-8 API calls (wait 60s between runs)
python tests/test_graph_quick.py      # Phase 3: 6-10 API calls (RECOMMENDED)
python tests/test_graph_integration.py # Phase 3: 15-20 API calls (will hit limit)
python tests/test_error_handling.py   # Phase 5: 15-20 API calls, 6 tests with delays
python tests/test_multiturn.py        # Phase 6: 50-60 API calls, 5 multi-turn tests
python tests/test_hybrid_control.py   # Phase 7: 50-60 API calls, 4 hybrid tests with speedup demo
python validate_phase6.py             # Phase 6: 0 API calls, quick validation
python src/chatuvisbox/command_parser.py  # Phase 7: 0 API calls, command parser test
```

**Interactive testing:**
```bash
python repl.py                        # Phase 6: Interactive multi-turn REPL (user-paced)
```

### Running the Application

```bash
# After Phase 8 implementation (REPL)
python -m chatuvisbox

# Or via entry point (if configured)
chatuvisbox

# Current status: Entry point placeholder exists but REPL not yet implemented
```

## Key Design Decisions

### 1. Single LangGraph vs Two-Agent Architecture
**Decision**: Use single LangGraph workflow with two tool registries (data_tools + vis_tools).
**Rationale**: More efficient than agent handoff; simpler state management; achieves same functional goal.

### 2. MVP Visualization Scope
**Include** (matplotlib-based 2D):
- functional_boxplot (1D curve ensembles)
- curve_boxplot (depth-colored curves)
- probabilistic_marching_squares (2D scalar field uncertainty)
- contour_boxplot (contour band depth from scalar field ensembles)
- uncertainty_lobes (vector uncertainty)

**Exclude**: All 3D/PyVista visualizations (marching cubes, tetrahedra, 3D squids)

### 3. Matplotlib Non-Blocking
Always use `plt.show(block=False)` + `plt.pause(0.1)` to allow REPL interaction while plots are open.

### 4. Error Handling Pattern (Phase 5)
- All tool functions return `{"status": "success"|"error", "message": ..., ...}`
- Tool nodes wrap execution in try-except, always return ToolMessage
- Graph loops back to model on error for clarification
- Circuit breaker: `error_count >= 3` → route to END
- Error recovery: error_count resets to 0 on successful tool execution
- Context awareness: file list injected in system prompt for helpful suggestions
- Logging: all tool calls, results, and errors logged to `logs/chatuvisbox.log`

### 5. File Naming Convention
- Test data: `test_data/sample_curves.csv`, `test_data/sample_scalar_field.npy`
- Temp files: `temp/_temp_*.npy` (auto-generated, gitignored)
- Clear on session end with `clear_session()` tool

### 6. Hybrid Control Model (Phase 7)
**Decision**: Two-tier execution - full LangGraph for complex queries, direct execution for simple commands.

**Simple Commands** (Fast Path):
- Pattern: "percentile 80", "isovalue 0.7", "colormap plasma"
- Execution: Direct vis tool call, bypasses LangGraph
- Speed: 10-15x faster (0.12s vs 1.65s)

**Complex Queries** (Full Path):
- Pattern: "Make it look better", "Change colors and percentile"
- Execution: Full LangGraph workflow with LLM interpretation
- Maintains flexibility for ambiguous requests

**Implementation**:
- `command_parser.py`: Pattern matching for 7 simple command types
- `hybrid_control.py`: Direct execution with parameter validation
- `conversation.py`: Checks hybrid eligibility before full graph

## Important Implementation Notes

### config.py Setup
```python
import os
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment. Please set it in your system environment.")
```
**Do not** use `python-dotenv` or `.env` files - API key is in system environment.

### Model Binding Pattern
```python
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",  # Lite version for 30 RPM
    google_api_key=config.GEMINI_API_KEY,
    temperature=0.0
)
model_with_tools = model.bind_tools(DATA_TOOL_SCHEMAS + VIS_TOOL_SCHEMAS)
```

### Visualization Tool Return Pattern
Include `_vis_params` in return dict for hybrid control:
```python
return {
    "status": "success",
    "message": "...",
    "_vis_params": {
        "_tool_name": "plot_functional_boxplot",
        "data_path": data_path,
        "percentile": percentile,
        "show_median": show_median
    }
}
```

### REPL Commands
- `/help` - Show available commands
- `/context` - Display current GraphState
- `/stats` - Session statistics
- `/clear` - Clear temp files and reset state
- `/reset` - Reset conversation only (preserve files)
- `/quit` - Exit application

## UVisBox Interface Reference

Key matplotlib-based functions for MVP:

- `functional_boxplot(data, method='fdb', percentiles=[25, 50, 90, 100], ax=None, colors=None, alpha=0.7, plot_all_curves=False)` ⚠️ **Updated 2025-10-26**
- `curve_boxplot(curves, percentiles=[25, 50, 90, 100], ax=None, colors=None, alpha=0.7)` ⚠️ **Updated 2025-10-26**
- `probabilistic_marching_squares(F, isovalue, cmap='viridis', ax=None)`
- `uncertainty_lobes(positions, ensemble_vectors, percentile1=50, percentile2=90, scale=0.2, ax=None)` ⚠️ **Updated 2025-10-28**
- `contour_boxplot(ensemble_images, isovalue, percentiles=[25, 50, 75, 90], ax=None, colormap='viridis', show_median=True, show_outliers=True, workers=12)` ⚠️ **Added 2025-10-28**

All expect numpy arrays and return matplotlib axes.

### API Changes

**2025-10-28 (Latest)**: Major updates to data generation, visualization tools, and dependencies:

**contour_boxplot** (NEW):
- Added wrapper for UVisBox's `contour_boxplot` function
- Creates band depth visualization of binary contours from scalar field ensembles
- Accepts data with shape (ny, nx, n_ensemble), transposes to (n_ensemble, ny, nx)
- Parameters: `isovalue`, `percentiles`, `colormap`, `show_median`, `show_outliers`
- Automatically extracts binary contours and computes band depths

**generate_vector_field_ensemble** (NEW):
- Added new function for generating 2D vector field ensembles
- Parameters: `x_res`, `y_res`, `n_instances`, `initial_direction`, `initial_magnitude`
- Direction variation increases with x, magnitude variation increases with y
- Returns both `positions_path` and `vectors_path`

**generate_scalar_field_ensemble** (UPDATED):
- Changed from random Gaussian centers to fixed center at (nx/2, ny/2)
- Standard deviation now varies systematically: σx = nx + ensemble_index, σy = ny
- Rescales to [0,1], adds uniform noise [0, 0.1), then rescales again
- More predictable variation for testing

**uncertainty_lobes** (UPDATED):
- Parameter `percentil1` → `percentile1` (fixed typo, added 'e')
- Parameter `percentil2` → `percentile2` (fixed typo, added 'e')
- Parameter `positions` is now **required** (was optional in brief experimental version)
- Default values: `percentile1=90`, `percentile2=50` (note: percentile1 should be > percentile2)
- Range changed from [0,1] to [0,100] for percentiles

**File Naming Convention**:
- All `vis_tools.py` → `vis_tools.py`
- All `VIS_TOOLS` → `VIS_TOOLS`
- All `VIS_TOOL_SCHEMAS` → `VIS_TOOL_SCHEMAS`
- All `DEFAULT_VIS_PARAMS` → `DEFAULT_VIS_PARAMS`

**Model Prompt** (UPDATED):
- More directive: "IMMEDIATELY use visualization tools" without asking for confirmation
- Emphasizes automatic progression from data generation to visualization

**Python Version** (UPDATED):
- Minimum: Python 3.10
- Maximum: Python 3.13 (excludes 3.14+)
- Default: Python 3.13 in conda environment
- Linting tools (black, ruff) target Python 3.13

**Dependencies** (UPDATED):
- langchain: 0.1.0 → 0.3.27
- langchain-google-genai: 2.0.4 → 2.1.12
- langgraph: 0.2.53 → 0.2.76
- **google-generativeai: REMOVED** (was causing dependency conflict, not directly used)
- numpy: 1.26.0 → 1.26.4
- pandas: 2.2.0 → 2.3.3
- matplotlib: 3.8.0 → 3.10.7
- langsmith: 0.1.0 → 0.4.38
- Poetry lock file now generated successfully with caret (^) version notation

**2025-10-26**: `functional_boxplot` added `plot_all_curves` parameter:
- Added `plot_all_curves` parameter (boolean, default False)
- When True, plots all individual curves in addition to the boxplot bands
- Useful for showing raw data alongside statistical summary

**2025-10-26 (Earlier)**: Both `functional_boxplot` and `curve_boxplot` updated to support multiple percentile bands:

**functional_boxplot**:
- Parameter `curves` → `data`
- Parameter `percentil` (float) → `percentiles` (list of floats)
- Parameter `band_alpha` (float) → `alpha` (float)
- Added `method` parameter ('fdb' or 'mfdb', default 'fdb')
- Added `colors` parameter (list of strings, optional)
- Removed `show_median` parameter (always shows median)
- Removed `curves_depths` parameter (auto-computed)
- Default `alpha` changed from 0.5 → 0.7
- Now supports multiple percentile bands instead of single band

**curve_boxplot**:
- Parameter `percentile` (float) → `percentiles` (list of floats)
- Parameter `color_map` (str) → `colors` (list of strings, optional)
- Default `alpha` changed from 1.0 → 0.7
- Now supports multiple percentile bands instead of single band

## Common Pitfalls to Avoid

1. **Don't create .env files** - Use system environment variable `GEMINI_API_KEY`
2. **Don't forget langchain-google-genai** - Critical missing dependency in original plan
3. **Don't block on plt.show()** - Always use `block=False`
4. **Don't skip phase validation** - Each phase has a checklist; complete before moving on
5. **Don't hardcode file paths** - Use `config.TEMP_DIR` and `config.TEST_DATA_DIR`
6. **Don't forget _tool_name** - Required in vis params for hybrid control
7. **Don't exceed error threshold** - Circuit breaker at 3 consecutive errors (Phase 5)
8. **Don't mix GOOGLE_API_KEY and GEMINI_API_KEY** - Use `GEMINI_API_KEY` consistently
9. **Check logs for debugging** - All tool calls logged to `logs/chatuvisbox.log` (Phase 5)
10. **Error count resets on success** - Don't manually reset error_count (Phase 5)

## Implementation-Specific Notes (From Phase 1)

### UVisBox Import Path Issue
The correct import path for UVisBox functions is:
```python
from uvisbox.Modules import functional_boxplot
from uvisbox.Modules import curve_boxplot  
from uvisbox.Modules import probabilistic_marching_squares
from uvisbox.Modules import uncertainty_lobes
```

### Visualization Return Format
All vis tools MUST include `_vis_params` for hybrid control (Phase 7):
```python
return {
    "status": "success",
    "message": "Displayed functional boxplot for 30 curves",
    "_vis_params": {
        "_tool_name": "plot_functional_boxplot",
        "data_path": data_path,
        "percentile": percentile,
        "show_median": show_median
    }
}
```

## Implementation-Specific Notes (From Phase 5)

### Error Handling Architecture

**Circuit Breaker** (`src/chatuvisbox/routing.py:64-71`):
```python
def route_after_tool(state: GraphState) -> Literal["model", "end"]:
    MAX_ERRORS = 3
    if state.get("error_count", 0) >= MAX_ERRORS:
        print(f"ERROR: Exceeded {MAX_ERRORS} consecutive errors. Ending.")
        return "end"
    return "model"
```

**Error Recovery** (`src/chatuvisbox/state.py`):
- `increment_error_count()`: Called on tool failure
- `update_state_with_data()`: Resets error_count to 0 on success
- `update_state_with_vis()`: Resets error_count to 0 on success

**Context Awareness** (`src/chatuvisbox/nodes.py:29-32` and `model.py:44-48`):
```python
# In nodes.py: Get list of available files for context
file_list = []
if config.TEST_DATA_DIR.exists():
    file_list = [f.name for f in config.TEST_DATA_DIR.iterdir() if f.is_file()]

# In model.py: System prompt guidance
"Remember the current_data_path from previous operations"
"If user requests a different visualization type, use current_data_path
 unless they explicitly mention new data"
```

**Logging System** (`src/chatuvisbox/logger.py`):
- Dual output: file (`logs/chatuvisbox.log`) + console
- Functions: `log_tool_call()`, `log_tool_result()`, `log_error()`, `log_state_update()`
- Integrated in `nodes.py` for all tool executions

### Phase 5 Error Handling Patterns

**Pattern 1: File Not Found**
- Tool returns `{"status": "error", "message": "File not found: <path>"}`
- Agent receives error and file list in context
- Agent suggests available files or alternatives

**Pattern 2: Data Shape Mismatch**
- UVisBox raises exception on incompatible data
- try-except in tool node catches and wraps error
- Agent explains incompatibility and suggests alternatives

**Pattern 3: Circuit Breaker**
- After 3 consecutive errors, routing goes to END
- Prevents infinite error loops
- Error count resets on any successful tool execution

**Pattern 4: Multi-turn Error Recovery**
- User can correct errors in follow-up messages
- Conversation state maintained across turns
- Error count persists but resets on success

## Implementation-Specific Notes (From Phase 6)

### Multi-Turn Conversation Architecture

**ConversationSession Class** (`src/chatuvisbox/conversation.py`):
```python
class ConversationSession:
    """Manages a multi-turn conversation session."""

    def send(self, user_message: str) -> GraphState:
        """Send message and get response."""
        # First turn: create_initial_state()
        # Subsequent turns: append HumanMessage
        # Always: invoke graph_app with current state

    def get_last_response(self) -> str:
        """Get most recent assistant message."""

    def get_context_summary(self) -> dict:
        """Return turn_count, current_data, last_vis, etc."""

    def reset(self):
        """Clear state and start fresh."""
```

**State Persistence Across Turns**:
- Messages accumulate in `state["messages"]`
- `current_data_path` preserved until new data generated
- `last_vis_params` updated with each visualization
- `error_count` tracked and reset on success
- `session_files` accumulates all created files

**Turn Flow**:
```
Turn 1: user input → create_initial_state() → graph_app.invoke() → state
Turn 2: user input → append to state["messages"] → graph_app.invoke() → updated state
Turn N: user input → append to state["messages"] → graph_app.invoke() → updated state
```

### Phase 6 Conversation Patterns

**Pattern 1: Sequential Workflow**
```
User: "Generate 30 curves"
Agent: [creates data, saves to .npy]

User: "Plot them"  ← Implicit reference to turn 1 data
Agent: [creates functional boxplot from current_data_path]

User: "Change percentile to 90"  ← Implicit reference to last vis
Agent: [re-creates plot with new percentile]
```

**Pattern 2: Pronoun Resolution**
```
User: "Generate some curves"
Agent: [creates data]

User: "Plot it"  ← "it" = current_data_path
Agent: [creates visualization]

User: "Make it prettier"  ← "it" = last_vis_params
Agent: [adjusts visualization]
```

**Pattern 3: Multi-Visualization**
```
User: "Generate 40 curves"
Agent: [creates data]

User: "Show functional boxplot"
Agent: [creates vis 1]

User: "Now show curve boxplot"  ← Same data, different vis
Agent: [creates vis 2, current_data_path unchanged]
```

**Pattern 4: Error Recovery**
```
User: "Generate curves"
Agent: [success, error_count = 0]

User: "Load bad_file.csv"
Agent: [error, error_count = 1]

User: "Plot the curves I generated"  ← Uses context to recover
Agent: [success, error_count = 0]
```

### Interactive REPL Commands

**File**: `repl.py`

**Commands**:
- `/quit` - Exit REPL and close matplotlib windows
- `/reset` - Reset conversation (clear state, start fresh)
- `/context` - Display current conversation context

**Usage**:
```bash
$ python repl.py

You: Generate 30 curves
Assistant: Generated 30 curves...

You: Plot them
Assistant: Created functional boxplot...

You: /context
📊 Context:
  turn_count: 2
  current_data: temp/_temp_ensemble_curves.npy
  last_vis: {'_tool_name': 'plot_functional_boxplot', ...}
  error_count: 0
  message_count: 4

You: /quit
👋 Goodbye!
```

## File Structure (Current Implementation Status)

```
chatuvisbox/
├── pyproject.toml           # ✅ DONE Phase 4.5: Poetry configuration
├── environment.yml          # ✅ DONE Phase 4.5: Conda environment
├── requirements.txt         # ✅ DONE: Python dependencies (legacy)
├── README.md                # ✅ DONE Phase 4.5: Package documentation
├── CLAUDE.md                # ✅ DONE: AI agent guidance (this file)
├── ENVIRONMENT_SETUP.md     # ✅ DONE: API key configuration guide
├── TESTING.md               # ✅ DONE: Comprehensive testing guide
├── RATE_LIMIT_FRIENDLY_TESTING.md # ✅ DONE: Rate limit strategy
├── .gitignore               # ✅ DONE Phase 1
│
├── src/chatuvisbox/         # ✅ DONE Phase 4.5: Package source (src layout)
│   ├── __init__.py          # ✅ Package exports (updated Phase 6: ConversationSession)
│   ├── __main__.py          # ✅ Entry point (placeholder for Phase 8)
│   ├── graph.py             # ✅ DONE Phase 3: LangGraph workflow
│   ├── state.py             # ✅ DONE Phase 2: GraphState with error_count
│   ├── nodes.py             # ✅ DONE Phase 5: Nodes with error handling (189 lines)
│   ├── routing.py           # ✅ DONE Phase 5: Routing with circuit breaker (86 lines)
│   ├── model.py             # ✅ DONE Phase 5: Model with error recovery prompt (109 lines)
│   ├── logger.py            # ✅ DONE Phase 5: Logging infrastructure (42 lines)
│   ├── conversation.py      # ✅ DONE Phase 6+7: ConversationSession with hybrid control (145 lines)
│   ├── command_parser.py    # ✅ DONE Phase 7: Parse simple commands (127 lines)
│   ├── hybrid_control.py    # ✅ DONE Phase 7: Fast path execution (86 lines)
│   ├── utils.py             # ✅ DONE Phase 2: Utility functions
│   ├── data_tools.py        # ✅ DONE Phase 1: Data tools (~420 lines)
│   ├── vis_tools.py         # ✅ DONE Phase 1: Visualization tools (570 lines)
│   └── config.py            # ✅ DONE Phase 1: Configuration
│
├── tests/                   # ✅ DONE Phase 4.5: Test suite
│   ├── __init__.py          # ✅ Test package marker
│   ├── conftest.py          # ✅ Pytest fixtures
│   ├── test_phase1.py       # ✅ Phase 1: 0 API calls
│   ├── test_phase2.py       # ✅ Phase 2: 10-15 API calls
│   ├── test_routing.py      # ✅ Phase 3: 0 API calls
│   ├── test_graph.py        # ✅ Phase 3: 5-8 API calls
│   ├── test_graph_quick.py  # ✅ Phase 3: 6-10 API calls ⭐ RECOMMENDED
│   ├── test_graph_integration.py # ✅ Phase 3: 15-20 API calls
│   ├── test_happy_path.py   # ✅ Phase 4: 25-35 API calls
│   ├── test_matplotlib_behavior.py # ✅ Phase 4: 0 API calls
│   ├── test_error_handling.py # ✅ Phase 5: 6 tests (15-20 API calls)
│   ├── test_multiturn.py    # ✅ Phase 6: 5 multi-turn tests (50-60 API calls)
│   ├── test_hybrid_control.py # ✅ Phase 7: 4 hybrid tests (50-60 API calls, speedup demo)
│   ├── interactive_test.py  # ✅ Phase 4: Interactive menu testing
│   ├── run_tests_with_delays.py # ✅ Automated test runner
│   └── simple_test.py       # ✅ Simple validation
│
├── test_data/               # ✅ DONE Phase 1: Sample data files
│   ├── sample_curves.csv
│   ├── sample_scalar_field.npy
│   └── README.md
│
├── temp/                    # ✅ DONE Phase 1: Generated files (gitignored)
├── logs/                    # ✅ DONE Phase 5: Log files (gitignored)
│   └── chatuvisbox.log
│
├── repl.py                  # ✅ DONE Phase 6: Interactive REPL for multi-turn testing (79 lines)
├── validate_phase6.py       # ✅ DONE Phase 6: Validation script (117 lines)
│
├── reports/                 # Temporary: Phase completion reports (gitignored)
│   ├── PHASE_2_COMPLETION_REPORT.md
│   ├── PHASE_3_COMPLETION_REPORT.md
│   ├── PHASE_4_COMPLETION_REPORT.md
│   ├── PHASE_4.5_COMPLETION_REPORT.md
│   ├── PHASE_5_COMPLETION_REPORT.md
│   ├── PHASE_6_COMPLETION_REPORT.md
│   ├── PHASE_7_COMPLETION_REPORT.md  # ✅ NEW
│   ├── VIZ_TO_VIS_MIGRATION_SUMMARY.md
│   └── UPDATE_*.md
│
└── plans/                   # ✅ DONE: Implementation phase guides
    ├── README.md
    ├── phase_01_*.md        # ✅ Phase 1 complete
    ├── phase_02_*.md        # ✅ Phase 2 complete
    ├── phase_03_*.md        # ✅ Phase 3 complete
    ├── phase_04_*.md        # ✅ Phase 4 complete
    ├── phase_05_*.md        # ✅ Phase 5 complete
    └── phase_06_*.md        # ✅ Phase 6 complete
```

## Reference Documentation

- **Implementation Plans**: `plans/README.md` - Start here for step-by-step guidance
- **Project Modifications**: `plans/00_project_modifications.md` - Key decisions and rationale
- **Environment Setup**: `ENVIRONMENT_SETUP.md` - API key configuration
- **Original Plan**: `ten_phase_plan.md` - High-level overview
