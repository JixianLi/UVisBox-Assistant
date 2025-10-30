# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ChatUVisBox** is a natural language interface for the UVisBox uncertainty visualization library. It uses LangGraph to orchestrate a conversational AI agent (powered by Google Gemini) that translates natural language requests into data processing and visualization operations.

**Current Version**: v0.1.0 (Released 2025-01-29)

**Key Features**:
- ✅ Natural language interface for 5 visualization types
- ✅ BoxplotStyleConfig with 10 styling parameters
- ✅ Hybrid control system (16 commands, 10-15x faster updates)
- ✅ Multi-turn conversation with context preservation
- ✅ Session management with automatic cleanup
- ✅ Error handling with circuit breaker
- ✅ Comprehensive test suite (unit/integration/e2e/interactive)
- ✅ Complete documentation (User Guide, API Reference, Testing Guide)

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
data_tools.py     - ✅ DONE: Data generation and loading functions
vis_tools.py      - ✅ DONE: UVisBox visualization wrappers with BoxplotStyleConfig
config.py         - ✅ DONE: Configuration (API key, paths, DEFAULT_VIS_PARAMS)
logger.py         - ✅ DONE: Logging infrastructure with file and console output
conversation.py   - ✅ DONE: ConversationSession class for multi-turn conversations with hybrid control
command_parser.py - ✅ DONE: Parse simple commands for hybrid control (16 patterns)
hybrid_control.py - ✅ DONE: Execute simple commands directly, 10-15x speedup
main.py           - ✅ DONE: Interactive REPL with command handling (/help, /context, /stats, /clear, /reset, /quit)
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
- See `docs/ENVIRONMENT_SETUP.md` for detailed configuration instructions

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

### Project Status

ChatUVisBox v0.1.0 is **feature complete** with all core functionality implemented:

**Core Features** ✅ COMPLETE
- LangGraph workflow with state management
- 5 visualization types with BoxplotStyleConfig support
- Data generation and loading tools
- Error handling with circuit breaker
- Logging infrastructure

**User Experience** ✅ COMPLETE
- Multi-turn conversation support
- Hybrid control system (16 fast commands)
- Session management with cleanup
- Interactive REPL with full commands

**Quality Assurance** ✅ COMPLETE
- Comprehensive test suite (unit/integration/e2e/interactive)
- 45+ unit tests with 0 API calls
- BoxplotStyleConfig testing coverage
- Documentation complete (User Guide, API Reference, Testing Guide)

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
- See `TESTING.md` for comprehensive testing guide

**Quick Start (Recommended):**
```bash
# Quick sanity check (30 seconds, 1-2 API calls)
python tests/test_simple.py

# Run unit tests only (instant, 0 API calls) ⭐ RECOMMENDED FOR DEVELOPMENT
python tests/utils/run_all_tests.py --unit

# Run all tests with automatic delays (~10 minutes)
python tests/utils/run_all_tests.py
```

**Category-Based Testing:**
```bash
# Unit tests (0 API calls, < 15 seconds)
python tests/utils/run_all_tests.py --unit
python tests/unit/test_command_parser.py  # 17 tests: BoxplotStyleConfig commands
python tests/unit/test_config.py          # 8 tests: Configuration validation
python tests/unit/test_routing.py         # Routing logic tests
python tests/unit/test_tools.py           # 10 tests: Direct tool function calls

# Integration tests (15-25 API calls per file, 2-4 minutes each)
python tests/utils/run_all_tests.py --integration
python tests/integration/test_hybrid_control.py      # Fast parameter updates
python tests/integration/test_error_handling.py      # Error recovery
python tests/integration/test_session_management.py  # Session cleanup

# End-to-end tests (20-30 API calls per file, 3-5 minutes each)
python tests/utils/run_all_tests.py --e2e
python tests/e2e/test_matplotlib_behavior.py

# Interactive testing (user-paced)
python tests/interactive/interactive_test.py
```

**Quick Validation:**
```bash
# Quick validation (unit + sanity check)
python tests/utils/run_all_tests.py --quick
```

**BoxplotStyleConfig Testing:**
- 17 command parser tests for styling parameters (median/outliers color/width/alpha)
- 8 config tests for BoxplotStyleConfig defaults
- 10 tool tests for direct function calls with full styling
- Total: 45+ unit tests, all 0 API calls, instant execution

### Running the Application

```bash
# Full REPL with commands
python main.py

# Alternative (using package entry point)
python -m chatuvisbox
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

### 4. Error Handling Pattern
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

### 6. Hybrid Control Model
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
- `command_parser.py`: Pattern matching for 16 simple command types (includes BoxplotStyleConfig)
- `hybrid_control.py`: Direct execution with parameter validation
- `conversation.py`: Checks hybrid eligibility before full graph

### 7. Test Organization
**Decision**: Category-based test structure (unit/integration/e2e/interactive) for clear separation by API usage.

**Test Categories**:
- **Unit tests** (`tests/unit/`): 0 API calls, instant execution, 45+ tests
- **Integration tests** (`tests/integration/`): 15-25 API calls per file, workflow testing
- **E2E tests** (`tests/e2e/`): 20-30 API calls per file, complete scenarios
- **Interactive tests** (`tests/interactive/`): User-paced, menu-driven exploration

**BoxplotStyleConfig Testing**:
- 17 command parser tests for styling parameters (median/outliers color/width/alpha)
- 8 config tests for BoxplotStyleConfig defaults
- 10 tool tests for direct function calls with full styling
- All 16 hybrid control commands tested

**Benefits**:
- Clear separation by API usage (unit tests = 0 calls, safe to run repeatedly)
- Test runner with category flags (--unit, --integration, --e2e, --quick)
- Reduced from ~2600 lines (17 files) to ~1600 lines (14 files)
- Deleted ~1444 lines of obsolete phase-based tests

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

ChatUVisBox uses the following matplotlib-based UVisBox functions:

### Boxplot Functions (with BoxplotStyleConfig)

**functional_boxplot**:
```python
functional_boxplot(data, method='fdb', boxplot_style=None, ax=None)
```
- `data`: NumPy array of shape (n_curves, n_points)
- `method`: Band depth method - 'fdb' (functional band depth) or 'mfdb' (modified functional band depth) (default: 'fdb')
- `boxplot_style`: BoxplotStyleConfig instance (optional)
- `ax`: Matplotlib axes (optional)

**curve_boxplot**:
```python
curve_boxplot(curves, boxplot_style=None, ax=None, workers=12)
```
- `curves`: NumPy array of shape (n_curves, n_points)
- `boxplot_style`: BoxplotStyleConfig instance (optional)
- `ax`: Matplotlib axes (optional)
- `workers`: Number of parallel workers for band depth (default: 12)

**contour_boxplot**:
```python
contour_boxplot(ensemble_images, isovalue, boxplot_style=None, ax=None, workers=12)
```
- `ensemble_images`: NumPy array of shape (n_ensemble, ny, nx)
- `isovalue`: Float threshold for binary contour extraction (required)
- `boxplot_style`: BoxplotStyleConfig instance (optional)
- `ax`: Matplotlib axes (optional)
- `workers`: Number of parallel workers (default: 12)

### BoxplotStyleConfig

The `BoxplotStyleConfig` dataclass controls boxplot styling:

```python
from uvisbox.Modules import BoxplotStyleConfig

BoxplotStyleConfig(
    percentiles=[25, 50, 90, 100],      # List of percentile values
    percentile_colormap='viridis',       # Colormap for bands
    show_median=True,                    # Show median curve
    median_color='red',                  # Median color
    median_width=3.0,                    # Median line width
    median_alpha=1.0,                    # Median transparency (0.0-1.0)
    show_outliers=False,                 # Show outlier curves
    outliers_color='gray',               # Outliers color
    outliers_width=1.0,                  # Outliers line width
    outliers_alpha=0.5                   # Outliers transparency (0.0-1.0)
)
```

### Other Visualization Functions

**probabilistic_marching_squares**:
```python
probabilistic_marching_squares(F, isovalue, cmap='viridis', ax=None)
```
- `F`: NumPy array of shape (ny, nx, n_ensemble)
- `isovalue`: Float threshold for contour extraction (required)
- `cmap`: Matplotlib colormap name (default: 'viridis')
- `ax`: Matplotlib axes (optional)

**uncertainty_lobes**:
```python
uncertainty_lobes(positions, ensemble_vectors, percentile1=90, percentile2=50, scale=0.2, ax=None, workers=None)
```
- `positions`: NumPy array of shape (n_points, 2)
- `ensemble_vectors`: NumPy array of shape (n_points, 2, n_ensemble)
- `percentile1`: Outer percentile (0-100, default: 90)
- `percentile2`: Inner percentile (0-100, default: 50)
- `scale`: Glyph scale factor (default: 0.2)
- `ax`: Matplotlib axes (optional)
- `workers`: Number of parallel workers for band depth computation (default: None, optimized for large data only)

**Note**: All functions expect numpy arrays and return matplotlib axes.

## Common Pitfalls to Avoid

1. **Don't create .env files** - Use system environment variable `GEMINI_API_KEY`
2. **Don't forget langchain-google-genai** - Critical dependency for Gemini integration
3. **Don't block on plt.show()** - Always use `block=False`
4. **Don't hardcode file paths** - Use `config.TEMP_DIR` and `config.TEST_DATA_DIR`
5. **Don't forget _tool_name** - Required in vis params for hybrid control
6. **Don't exceed error threshold** - Circuit breaker at 3 consecutive errors
7. **Don't mix GOOGLE_API_KEY and GEMINI_API_KEY** - Use `GEMINI_API_KEY` consistently
8. **Check logs for debugging** - All tool calls logged to `logs/chatuvisbox.log`
9. **Error count resets on success** - Don't manually reset error_count
10. **Use category-based tests** - Run `tests/utils/run_all_tests.py --unit` for fast development
11. **BoxplotStyleConfig parameters** - All 10 styling parameters must be preserved in `_vis_params`

## Implementation-Specific Notes

### UVisBox BoxplotStyleConfig Interface

The UVisBox library now uses a `BoxplotStyleConfig` dataclass for boxplot styling:

**Correct import path**:
```python
from uvisbox.Modules import (
    functional_boxplot,
    curve_boxplot,
    contour_boxplot,
    probabilistic_marching_squares,
    uncertainty_lobes,
    BoxplotStyleConfig  # NEW
)
```

**Function signatures**:
```python
functional_boxplot(data, method='fdb', boxplot_style=None, ax=None)
curve_boxplot(curves, boxplot_style=None, ax=None, workers=12)
contour_boxplot(ensemble_images, isovalue, boxplot_style=None, ax=None, workers=12)
```

**BoxplotStyleConfig fields** (all have defaults):
- percentiles: List[float]
- percentile_colormap: str
- show_median: bool
- median_color: str
- median_width: float
- median_alpha: float
- show_outliers: bool
- outliers_color: str
- outliers_width: float
- outliers_alpha: float

**Important Notes**:
- Parameter name is `boxplot_style` (not `style_config`)
- Use `show_outliers` to control outlier curve display
- `workers` parameter enables parallel band depth computation

### Visualization Return Format

All vis tools MUST include all BoxplotStyleConfig parameters in `_vis_params`:

```python
return {
    "status": "success",
    "message": "Displayed functional boxplot",
    "_vis_params": {
        "_tool_name": "plot_functional_boxplot",
        "data_path": data_path,
        "percentiles": percentiles,
        "percentile_colormap": percentile_colormap,
        "show_median": show_median,
        "median_color": median_color,
        "median_width": median_width,
        "median_alpha": median_alpha,
        "show_outliers": show_outliers,
        "outliers_color": outliers_color,
        "outliers_width": outliers_width,
        "outliers_alpha": outliers_alpha
    }
}
```

### Command Parser Patterns

The command parser supports 16 patterns including BoxplotStyleConfig styling:

```python
# Basic
"colormap <name>" → colormap/percentile_colormap
"percentile <number>" → percentiles
"show median" → show_median=True
"hide outliers" → show_outliers=False
"method <fdb|mfdb>" → method (functional band depth method)

# Median styling
"median color <color>" → median_color
"median width <number>" → median_width
"median alpha <number>" → median_alpha

# Outliers styling
"outliers color <color>" → outliers_color
"outliers width <number>" → outliers_width
"outliers alpha <number>" → outliers_alpha
```

## Error Handling Architecture

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

### Error Handling Patterns

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

## Multi-Turn Conversation Architecture

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

### Conversation Patterns

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

## File Structure

```
chatuvisbox/
├── pyproject.toml           # Poetry configuration
├── requirements.txt         # Python dependencies
├── README.md                # Package documentation
├── CLAUDE.md                # AI agent guidance (this file)
├── TESTING.md               # Comprehensive testing guide
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # Contribution guidelines
├── LICENSE                  # MIT License
├── .gitignore               # Git ignore patterns
│
├── src/chatuvisbox/         # Package source (src layout)
│   ├── __init__.py          # Package exports
│   ├── __main__.py          # Entry point for python -m chatuvisbox
│   ├── graph.py             # LangGraph workflow
│   ├── state.py             # GraphState with error tracking
│   ├── nodes.py             # Graph nodes with error handling
│   ├── routing.py           # Routing with circuit breaker
│   ├── model.py             # Gemini model with error recovery
│   ├── logger.py            # Logging infrastructure
│   ├── conversation.py      # ConversationSession with hybrid control
│   ├── command_parser.py    # Command parsing (16 patterns)
│   ├── hybrid_control.py    # Fast path execution
│   ├── utils.py             # Utility functions
│   ├── data_tools.py        # Data generation and loading
│   ├── vis_tools.py         # Visualization wrappers with BoxplotStyleConfig
│   └── config.py            # Configuration and defaults
│
├── tests/                   # Comprehensive test suite
│   ├── __init__.py          # Test package marker
│   ├── conftest.py          # Pytest fixtures
│   ├── README.md            # Test structure documentation
│   ├── test_simple.py       # Quick sanity check (30s, 1-2 API calls)
│   │
│   ├── unit/                # Unit tests (0 API calls, instant)
│   │   ├── test_command_parser.py  # 17 tests: BoxplotStyleConfig commands
│   │   ├── test_config.py          # 8 tests: Configuration validation
│   │   ├── test_routing.py         # Routing logic tests
│   │   └── test_tools.py           # 10 tests: Direct tool function calls
│   │
│   ├── integration/         # Integration tests (15-25 API calls per file)
│   │   ├── test_hybrid_control.py      # Fast parameter updates
│   │   ├── test_error_handling.py      # Error recovery & circuit breaker
│   │   └── test_session_management.py  # Session cleanup & stats
│   │
│   ├── e2e/                 # End-to-end tests (20-30 API calls per file)
│   │   └── test_matplotlib_behavior.py # Matplotlib non-blocking
│   │
│   ├── interactive/         # Interactive tests (user-paced)
│   │   └── interactive_test.py         # Menu-driven testing (24+ scenarios)
│   │
│   └── utils/               # Test utilities
│       └── run_all_tests.py            # Category-based test runner
│
├── test_data/               # Sample data files
│   ├── sample_curves.csv
│   ├── sample_scalar_field.npy
│   └── README.md
│
├── temp/                    # Generated files (gitignored)
├── logs/                    # Log files (gitignored)
│   └── chatuvisbox.log
│
├── docs/                    # Documentation
│   ├── USER_GUIDE.md        # Detailed user guide with examples
│   ├── API.md               # Complete API reference
│   └── ENVIRONMENT_SETUP.md # Environment setup guide
│
├── main.py                  # Production REPL with full commands
├── setup_env.sh             # Environment setup script
└── create_test_data.py      # Test data generation script
```

## Reference Documentation

- **User Guide**: `docs/USER_GUIDE.md` - Detailed usage examples and workflows
- **API Reference**: `docs/API.md` - Complete API documentation
- **Environment Setup**: `docs/ENVIRONMENT_SETUP.md` - API key configuration and setup
- **Testing Guide**: `TESTING.md` - Comprehensive testing strategies
- **Contributing**: `CONTRIBUTING.md` - Contribution guidelines
- **Changelog**: `CHANGELOG.md` - Version history
