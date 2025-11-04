# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**UVisBox-Assistant** is a natural language interface for the UVisBox uncertainty visualization library. It uses LangGraph to orchestrate a conversational AI agent (powered by Google Gemini) that translates natural language requests into data processing and visualization operations.

**Current Version**: v0.3.1 (Released 2025-11-04)

**Key Features**:
- ✅ Natural language interface for 6 visualization types
- ✅ BoxplotStyleConfig with 10 styling parameters
- ✅ Hybrid control system (16 commands, 10-15x faster updates)
- ✅ **Uncertainty analyzer** with statistics and LLM-powered reports (v0.3.0)
- ✅ **Three report formats**: inline (1 sentence), quick (3-5 sentences), detailed (full report) (v0.3.0)
- ✅ Multi-turn conversation with context preservation
- ✅ Session management with automatic cleanup
- ✅ Error handling with circuit breaker
- ✅ Comprehensive test suite (unit/integration/e2e/interactive)
- ✅ Complete documentation (User Guide, API Reference, Testing Guide, Analysis Examples)

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

### Analysis Workflow Architecture (v0.3.0)

The system supports **three workflow patterns** for uncertainty analysis:

1. **Visualization Only** (existing):
   - User: "generate curves and plot them"
   - Workflow: `data_tool → vis_tool`
   - Result: Visual output only

2. **Text Analysis Only** (new in v0.3.0):
   - User: "generate curves and analyze uncertainty"
   - Workflow: `data_tool → statistics_tool → analyzer_tool`
   - Result: Text report only (inline/quick/detailed)
   - **Critical Sequence**: MUST call statistics tool before analyzer tool

3. **Combined Visualization + Analysis** (new in v0.3.0):
   - User: "generate curves, plot boxplot, and create summary"
   - Workflow: `data_tool → vis_tool → statistics_tool → analyzer_tool`
   - Result: Both visual and text output

**Tool Sequence Rules** (enforced by system prompt):
- Statistics tool (`compute_functional_boxplot_statistics`) computes processed statistics from data
- Analyzer tool (`generate_uncertainty_report`) generates natural language reports from statistics
- Analyzer automatically receives `processed_statistics` from state (state injection pattern)
- Model must NEVER skip statistics tool when analysis is requested

**Report Formats**:
- `inline`: 1 sentence summary (~15-30 words)
- `quick`: 3-5 sentence overview (~50-100 words)
- `detailed`: Full report with sections (~100-300 words)

### Key Components

**Note**: As of v0.3.1, the project uses a feature-based directory structure. Import from the root package (e.g., `from uvisbox_assistant import ConversationSession`) for backward compatibility.

```
core/graph.py             - ✅ LangGraph StateGraph with 5 nodes and conditional routing
core/state.py             - ✅ GraphState with analysis fields (processed_statistics, analysis_report, analysis_type)
core/nodes.py             - ✅ Five core nodes: call_model, call_data_tool, call_vis_tool, call_statistics_tool, call_analyzer_tool
core/routing.py           - ✅ Conditional logic with circuit breaker and analyzer routing
llm/model.py              - ✅ ChatGoogleGenerativeAI with analysis workflow guidance
utils/utils.py            - ✅ Tool type detection (data/vis/statistics/analyzer) and file management
tools/data_tools.py       - ✅ Data generation and loading functions
tools/vis_tools.py        - ✅ UVisBox visualization wrappers with BoxplotStyleConfig
tools/statistics_tools.py - ✅ Statistical analysis with UVisBox functional_boxplot_summary_statistics (v0.3.0)
tools/analyzer_tools.py   - ✅ LLM-powered report generation with three formats (v0.3.0)
config.py                 - ✅ Configuration (API key, paths, DEFAULT_VIS_PARAMS)
utils/logger.py           - ✅ Logging infrastructure with file and console output
session/conversation.py   - ✅ ConversationSession with analysis state tracking (v0.3.0)
session/command_parser.py - ✅ Parse simple commands for hybrid control (16 patterns)
session/hybrid_control.py - ✅ Execute simple commands directly, 10-15x speedup
main.py                   - ✅ Interactive REPL with command handling (/help, /context, /stats, /clear, /reset, /quit)
```

### LangGraph Flow

```
START → call_model → [route_after_model]
                         ├─ data_tool       → call_model (loop for multi-step)
                         ├─ vis_tool        → call_model (confirm to user)
                         ├─ statistics_tool → call_model (v0.3.0)
                         ├─ analyzer_tool   → call_model (v0.3.0)
                         └─ END (direct response)

Typical Analysis Flow:
  data_tool → statistics_tool → analyzer_tool → END
```

### State Management

**GraphState fields**:
- `messages`: Full conversation history (List[BaseMessage])
- `current_data_path`: Path to most recent .npy file
- `last_vis_params`: Dict with `_tool_name`, `data_path`, and vis parameters
- `session_files`: List of temp files created (for cleanup)
- `error_count`: Circuit breaker (max 3 consecutive errors → END)
- **`processed_statistics`** (v0.3.0): Structured dict from statistics tool with numeric summaries
- **`analysis_report`** (v0.3.0): Generated text report from analyzer tool
- **`analysis_type`** (v0.3.0): Report format ("inline" | "quick" | "detailed")
- **`_raw_statistics`** (v0.3.0): Original UVisBox output for debugging

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

UVisBox-Assistant v0.3.1 (latest) is **feature complete** with improved architecture:

**v0.3.1 Changes** (Project Restructure):
- Feature-based directory structure (core/, tools/, session/, llm/, errors/, utils/)
- Backward-compatible imports via root __init__.py
- Improved code organization and discoverability
- Zero functional changes (pure refactoring)

**v0.3.0 Features**:

**Core Features** ✅ COMPLETE
- LangGraph workflow with 5 nodes (data, vis, statistics, analyzer, model)
- 6 visualization types with BoxplotStyleConfig support
- Data generation and loading tools
- **Statistical analysis with UVisBox integration** (v0.3.0)
- **LLM-powered uncertainty report generation** (v0.3.0)
- Error handling with circuit breaker
- Logging infrastructure

**User Experience** ✅ COMPLETE
- Multi-turn conversation support
- Hybrid control system (16 fast commands)
- **Three report formats (inline/quick/detailed)** (v0.3.0)
- **Combined visualization + analysis workflows** (v0.3.0)
- Session management with cleanup
- Interactive REPL with full commands

**Quality Assurance** ✅ COMPLETE
- Comprehensive test suite (unit/integration/e2e/interactive)
- **77+ unit tests with 0 API calls** (v0.3.0)
- **46 analysis-specific tests** (v0.3.0)
- BoxplotStyleConfig testing coverage
- Documentation complete (User Guide, API Reference, Testing Guide, Analysis Examples)

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
python tests/unit/test_command_parser.py       # 17 tests: BoxplotStyleConfig commands
python tests/unit/test_config.py               # 5 tests: Configuration validation
python tests/unit/test_routing.py              # Routing logic tests
python tests/unit/test_tools.py                # 10 tests: Direct tool function calls
python tests/unit/test_statistics_tools.py     # 25 tests: Statistics analysis (v0.3.0)
python tests/unit/test_analyzer_tools.py       # 21 tests: Report generation (v0.3.0)

# Integration tests (15-25 API calls per file, 2-4 minutes each)
python tests/utils/run_all_tests.py --integration
python tests/integration/test_hybrid_control.py      # Fast parameter updates
python tests/integration/test_error_handling.py      # Error recovery
python tests/integration/test_session_management.py  # Session cleanup

# End-to-end tests (20-30 API calls per file, 3-5 minutes each)
python tests/utils/run_all_tests.py --e2e
python tests/e2e/test_matplotlib_behavior.py
python tests/e2e/test_analysis_workflows.py    # Analysis workflows (v0.3.0)

# Interactive testing (user-paced)
python tests/interactive/interactive_test.py
```

**Quick Validation:**
```bash
# Quick validation (unit + sanity check)
python tests/utils/run_all_tests.py --quick
```

**Testing Coverage Summary:**
- **BoxplotStyleConfig**: 17 command parser tests + 8 config tests + 10 tool tests
- **Analysis Tools** (v0.3.0): 25 statistics tests + 21 analyzer tests + 12 E2E workflow tests
- **Total**: 77+ unit tests (0 API calls, instant execution)
- **Integration**: 46 analysis-specific tests with real UVisBox and Gemini calls

### Running the Application

```bash
# Full REPL with commands
python main.py

# Alternative (using package entry point)
python -m uvisbox_assistant
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
- squid_glyph_2D (2D vector uncertainty with depth-based filtering)

**Exclude**: All 3D/PyVista visualizations (marching cubes, tetrahedra)

### 3. Matplotlib Non-Blocking
Always use `plt.show(block=False)` + `plt.pause(0.1)` to allow REPL interaction while plots are open.

### 4. Error Handling Pattern
- All tool functions return `{"status": "success"|"error", "message": ..., ...}`
- Tool nodes wrap execution in try-except, always return ToolMessage
- Graph loops back to model on error for clarification
- Circuit breaker: `error_count >= 3` → route to END
- Error recovery: error_count resets to 0 on successful tool execution
- Context awareness: file list injected in system prompt for helpful suggestions
- Logging: all tool calls, results, and errors logged to `logs/uvisbox_assistant.log`
- **Error Tracking (v0.1.2)**: Full traceback capture with `_error_details` dict
- **Error Interpretation (v0.1.2)**: Context-aware hints when debug mode enabled
- **Auto-Fix Detection (v0.1.2)**: Tracks error → retry → success patterns

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
- **Unit tests** (`tests/unit/`): 0 API calls, instant execution, 77+ tests (v0.3.0)
- **Integration tests** (`tests/integration/`): 15-25 API calls per file, workflow testing
- **E2E tests** (`tests/e2e/`): 20-30 API calls per file, complete scenarios
- **Interactive tests** (`tests/interactive/`): User-paced, menu-driven exploration

**Testing Coverage**:
- 17 command parser tests for styling parameters (median/outliers color/width/alpha)
- 5 config tests (figsize, dpi, and verification that vis params are NOT duplicated)
- 11 tool tests for direct function calls with full styling (includes squid_glyph_2D)
- **25 statistics tests** (v0.3.0): Analysis, validation, error handling
- **21 analyzer tests** (v0.3.0): Report generation, prompts, validation
- **12 E2E workflow tests** (v0.3.0): Three workflow patterns, multi-turn analysis
- All 16 hybrid control commands tested

**Benefits**:
- Clear separation by API usage (unit tests = 0 calls, safe to run repeatedly)
- Test runner with category flags (--unit, --integration, --e2e, --quick)
- Comprehensive analysis test coverage with 0 API calls for development

### 8. Separating Statistics from Analysis (v0.3.0)
**Decision**: Split uncertainty analysis into two distinct tools: `compute_functional_boxplot_statistics` and `generate_uncertainty_report`.

**Rationale**:
- **Separation of concerns**: Statistics computation (numerical) vs. report generation (language)
- **State injection pattern**: Statistics stored in state, automatically injected into analyzer
- **Cost efficiency**: Statistics computed once, multiple reports can be generated
- **Testing**: Statistics logic testable without LLM calls (0 API cost)

**Implementation**:
- `statistics_tools.py`: Computes median analysis, band characteristics, outlier detection
- `analyzer_tools.py`: Uses Gemini to generate natural language reports from statistics
- `nodes.py`: Implements state injection in `call_analyzer_tool` node
- System prompt: Enforces REQUIRED sequence (statistics → analyzer)

**Key Benefits**:
- Clear error messages when statistics missing
- Model can't skip statistics step
- Multiple reports from same statistics
- Fast unit testing for statistics logic

## Important Implementation Notes

### config.py Setup
```python
import os
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment. Please set it in your system environment.")

# DEFAULT_VIS_PARAMS only contains figsize and dpi
# All visualization-specific defaults are in function signatures (vis_tools.py)
DEFAULT_VIS_PARAMS = {
    "figsize": (10, 8),
    "dpi": 100,
}
```
**Important Notes:**
- **Do not** use `python-dotenv` or `.env` files - API key is in system environment
- **DEFAULT_VIS_PARAMS only contains figure settings** (figsize, dpi)
- **All visualization defaults are hardcoded in function signatures** - prevents duplication and mismatch
- Function signatures are the single source of truth for visualization parameters

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

UVisBox-Assistant uses the following matplotlib-based UVisBox functions:

### Boxplot Functions (with BoxplotStyleConfig)

**functional_boxplot**:
```python
functional_boxplot(data, method='fbd', boxplot_style=None, ax=None)
```
- `data`: NumPy array of shape (n_curves, n_points)
- `method`: Band depth method - 'fbd' (functional band depth) or 'mfbd' (modified functional band depth) (default: 'fbd')
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

**squid_glyph_2D**:
```python
squid_glyph_2D(positions, ensemble_vectors, percentile=95, scale=0.2, ax=None, workers=None)
```
- `positions`: NumPy array of shape (n_points, 2)
- `ensemble_vectors`: NumPy array of shape (n_points, 2, n_ensemble)
- `percentile`: Percentile of ensemble members to include based on depth ranking (0-100, default: 95). Higher values include more vectors showing more variation.
- `scale`: Glyph scale factor (default: 0.2)
- `ax`: Matplotlib axes (optional)
- `workers`: Number of parallel workers for computation (default: None)

**Note**: All functions expect numpy arrays and return matplotlib axes.

## Common Pitfalls to Avoid

1. **Don't create .env files** - Use system environment variable `GEMINI_API_KEY`
2. **Don't forget langchain-google-genai** - Critical dependency for Gemini integration
3. **Don't block on plt.show()** - Always use `block=False`
4. **Don't hardcode file paths** - Use `config.TEMP_DIR` and `config.TEST_DATA_DIR`
5. **Don't forget _tool_name** - Required in vis params for hybrid control
6. **Don't exceed error threshold** - Circuit breaker at 3 consecutive errors
7. **Don't mix GOOGLE_API_KEY and GEMINI_API_KEY** - Use `GEMINI_API_KEY` consistently
8. **Check logs for debugging** - All tool calls logged to `logs/uvisbox_assistant.log`
9. **Error count resets on success** - Don't manually reset error_count
10. **Use category-based tests** - Run `tests/utils/run_all_tests.py --unit` for fast development
11. **BoxplotStyleConfig parameters** - All 10 styling parameters must be preserved in `_vis_params`
12. **Use vprint for internal messages** (v0.1.2) - All internal state messages must use `vprint()` from `output_control.py`, not regular `print()`
13. **Record errors with full traceback** (v0.1.2) - Always capture `traceback.format_exc()` in tool error handling with `_error_details` dict
14. **Check debug mode for hints** (v0.1.2) - Error interpretation should only show hints when debug mode is enabled
15. **Always call statistics before analyzer** (v0.3.0) - Analyzer tool requires processed_statistics from state
16. **UVisBox returns "depths" not "depth"** (v0.3.0) - Use plural form: `raw_stats["depths"]`
17. **Outliers ≠ Percentile bands** (v0.3.0) - Outliers use depth-based detection (Q1 - 1.5×IQR), not percentile position
18. **Model must present reports** (v0.3.0) - System prompt enforces displaying report content to user, not just confirmation

## Implementation-Specific Notes

### Outlier Detection vs Percentile Bands (v0.3.0)

**IMPORTANT CLARIFICATION**: Outliers and percentile bands are computed differently and serve different purposes.

**Percentile Bands** (Visual Representation):
- Based on depth ranking of curves
- Example: 90th percentile = deepest 90% of curves form the outer band
- With 100 curves, the 10 curves outside 90th percentile are the **outer envelope**, NOT outliers
- These bands show the data distribution and variation
- Controlled by `percentiles` parameter (e.g., `[25, 50, 90, 100]`)

**Outliers** (Statistical Definition):
- Based on traditional boxplot fence: curves with `depth < Q1 - 1.5×IQR`
- Uses interquartile range (IQR) of depth values
- With 100 similar curves, IQR of depths is typically small (e.g., ≈2.0)
- Lower fence = Q1 - 1.5×IQR ≈ 96.0 (example)
- No curves fall below fence → 0 outliers detected
- This is **correct behavior** per UVisBox's functional boxplot definition

**Example Scenario**:
```
Data: 100 curves with percentiles [25, 50, 75, 90]
Percentile bands: Show distribution of deepest 25%, 50%, 75%, 90%
Outer 10 curves: Outside 90th percentile band (part of envelope)
Outliers: 0 (no curves below depth fence)

Why? All curves are similar → small IQR → low fence → no outliers
```

**Key Insight**:
- **Percentiles describe distribution** (relative position in ranking)
- **Outliers describe anomalies** (statistical deviation from main cluster)
- A curve can be in the outer percentile band WITHOUT being an outlier

**UVisBox API**: `functional_boxplot_summary_statistics` returns:
- `depths`: Array of depth values for all curves (note: plural!)
- `outliers`: Array of curves classified as outliers (depth < Q1 - 1.5×IQR)
- `percentile_bands`: Dict of (bottom, top) curves for each percentile

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
functional_boxplot(data, method='fbd', boxplot_style=None, ax=None)
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
"method <fbd|mfbd>" → method (functional band depth method)

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

**Circuit Breaker** (`src/uvisbox_assistant/routing.py:64-71`):
```python
def route_after_tool(state: GraphState) -> Literal["model", "end"]:
    MAX_ERRORS = 3
    if state.get("error_count", 0) >= MAX_ERRORS:
        print(f"ERROR: Exceeded {MAX_ERRORS} consecutive errors. Ending.")
        return "end"
    return "model"
```

**Error Recovery** (`src/uvisbox_assistant/state.py`):
- `increment_error_count()`: Called on tool failure
- `update_state_with_data()`: Resets error_count to 0 on success
- `update_state_with_vis()`: Resets error_count to 0 on success

**Context Awareness** (`src/uvisbox_assistant/nodes.py:29-32` and `model.py:44-48`):
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

**Logging System** (`src/uvisbox_assistant/logger.py`):
- Dual output: file (`logs/uvisbox_assistant.log`) + console
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

**ConversationSession Class** (`src/uvisbox_assistant/conversation.py`):
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

## Debug and Verbose Mode (v0.1.2)

UVisBox-Assistant provides two independent debugging modes for enhanced troubleshooting.

### Debug Mode (`/debug on/off`)

**Purpose**: Verbose error output with full stack traces and helpful hints

**Implementation Pattern**:
```python
# In tools - capture full traceback
import traceback

except Exception as e:
    tb_str = traceback.format_exc()
    return {
        "status": "error",
        "message": "User-friendly message",
        "_error_details": {
            "exception": e,
            "traceback": tb_str
        }
    }

# In conversation.py - interpret with debug mode context
from uvisbox_assistant.error_interpretation import interpret_uvisbox_error, format_error_with_hint

user_msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=self.debug_mode)
enhanced_msg = format_error_with_hint(user_msg, hint)
```

**Key Points**:
- Full tracebacks stored in ErrorRecord
- Debug hints only shown when debug mode is ON
- Error history persists across conversation (max 20)
- Auto-fix detection tracks error → retry → success patterns

### Verbose Mode (`/verbose on/off`)

**Purpose**: Show/hide internal state messages

**Implementation Pattern**:
```python
from uvisbox_assistant.output_control import vprint, set_session

# In ConversationSession.__init__
set_session(self)  # Register for verbose checks

# In nodes.py, hybrid_control.py, etc.
vprint("[DATA TOOL] Calling generate_curves")  # Hidden by default
vprint("[HYBRID] Fast path executed")         # Hidden by default

# User-facing messages always shown
print("Generated 30 curves")  # Always shown
```

**Internal Messages** (controlled by verbose mode):
- `[DATA TOOL]` - Data tool execution
- `[VIS TOOL]` - Visualization tool execution
- `[HYBRID]` - Hybrid fast path execution
- `[AUTO-FIX]` - Auto-fix detection

**User-Facing Messages** (always shown):
- Success confirmations
- File cleanup notifications
- Error messages (concise or detailed based on debug mode)

### Error Tracking Architecture

**ErrorRecord** (`src/uvisbox_assistant/error_tracking.py`):
- Stores full error details with traceback
- Provides `summary()` and `detailed()` methods
- Immutable dataclass

**ConversationSession** fields:
- `debug_mode: bool` (default: False)
- `verbose_mode: bool` (default: False)
- `error_history: List[ErrorRecord]` (max 20)
- `auto_fixed_errors: set` - IDs of auto-fixed errors

**Error Recording Flow**:
1. Tool catches exception
2. Tool returns error with `_error_details`
3. `conversation.py` records error via `record_error()`
4. Error interpretation applied if debug mode ON
5. Error stored in `error_history`
6. User can retrieve via `/errors` or `/trace`

**Auto-Fix Detection Flow**:
1. Tool fails → Error recorded (ID=1)
2. State stores: `last_error_tool`, `last_error_id`
3. Model retries with corrections
4. Same tool succeeds → Auto-fix detected!
5. `nodes.py` sets `_auto_fixed_error_id` in state
6. `conversation.py` marks error as auto-fixed
7. `/errors` shows `(auto-fixed ✓)` status

### Output Control Pattern

**DO**:
```python
from uvisbox_assistant.output_control import vprint

# Internal messages
vprint("[DATA TOOL] Calling function")
vprint("[HYBRID] Executing fast path")

# User-facing messages
print("Generated 30 curves")
print("✅ Success!")
```

**DON'T**:
```python
# Don't use print for internal messages
print("[DATA TOOL] Calling function")  # ❌ Wrong

# Don't use vprint for user messages
vprint("Generated 30 curves")  # ❌ Wrong
```

### Testing Notes

**Unit Tests** (0 API calls):
- `tests/unit/test_error_tracking.py` - 17 tests
- `tests/unit/test_output_control.py` - 5 tests
- `tests/unit/test_error_interpretation.py` - 14 tests

**Total: 36+ debug feature tests, all 0 API calls**

**Performance Requirements**:
- vprint overhead < 5% when verbose mode OFF
- Error recording < 1ms per error
- No noticeable conversation slowdown

## File Structure

```
uvisbox-assistant/
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
├── src/uvisbox_assistant/         # Package source (feature-based structure, v0.3.1)
│   ├── __init__.py          # Package exports (backward-compatible re-exports)
│   ├── __main__.py          # Entry point for python -m uvisbox_assistant
│   ├── config.py            # Configuration and defaults
│   ├── main.py              # Interactive REPL
│   │
│   ├── core/                # LangGraph workflow orchestration
│   │   ├── __init__.py      # Core exports
│   │   ├── graph.py         # StateGraph with 5 nodes
│   │   ├── nodes.py         # Five graph nodes (data, vis, statistics, analyzer, model)
│   │   ├── routing.py       # Conditional routing with circuit breaker
│   │   └── state.py         # GraphState with analysis fields
│   │
│   ├── tools/               # Data and visualization tools
│   │   ├── __init__.py      # Tools exports
│   │   ├── data_tools.py    # Data generation and loading
│   │   ├── vis_tools.py     # Visualization wrappers with BoxplotStyleConfig
│   │   ├── statistics_tools.py  # Statistical analysis (v0.3.0)
│   │   └── analyzer_tools.py    # LLM-powered report generation (v0.3.0)
│   │
│   ├── session/             # User interaction and session management
│   │   ├── __init__.py      # Session exports
│   │   ├── conversation.py  # ConversationSession with analysis tracking
│   │   ├── hybrid_control.py  # Fast path execution
│   │   └── command_parser.py  # Command parsing (16 patterns)
│   │
│   ├── llm/                 # LLM configuration
│   │   ├── __init__.py      # LLM exports
│   │   └── model.py         # Gemini model setup
│   │
│   ├── errors/              # Error handling infrastructure
│   │   ├── __init__.py      # Error exports
│   │   ├── error_tracking.py  # ErrorRecord and error storage
│   │   └── error_interpretation.py  # Context-aware error hints
│   │
│   └── utils/               # Utilities and logging
│       ├── __init__.py      # Utils exports
│       ├── logger.py        # Logging infrastructure
│       ├── output_control.py  # Verbose mode control
│       └── utils.py         # Utility functions
│
├── tests/                   # Comprehensive test suite
│   ├── __init__.py          # Test package marker
│   ├── conftest.py          # Pytest fixtures
│   ├── README.md            # Test structure documentation
│   ├── test_simple.py       # Quick sanity check (30s, 1-2 API calls)
│   │
│   ├── unit/                # Unit tests (0 API calls, instant)
│   │   ├── test_command_parser.py       # 17 tests: BoxplotStyleConfig commands
│   │   ├── test_config.py               # 5 tests: Configuration validation
│   │   ├── test_routing.py              # Routing logic tests
│   │   ├── test_tools.py                # 10 tests: Direct tool function calls
│   │   ├── test_statistics_tools.py     # 25 tests: Statistics analysis (v0.3.0)
│   │   └── test_analyzer_tools.py       # 21 tests: Report generation (v0.3.0)
│   │
│   ├── integration/         # Integration tests (15-25 API calls per file)
│   │   ├── test_hybrid_control.py      # Fast parameter updates
│   │   ├── test_error_handling.py      # Error recovery & circuit breaker
│   │   └── test_session_management.py  # Session cleanup & stats
│   │
│   ├── e2e/                 # End-to-end tests (20-30 API calls per file)
│   │   ├── test_matplotlib_behavior.py # Matplotlib non-blocking
│   │   └── test_analysis_workflows.py  # Analysis workflows (v0.3.0)
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
│   └── uvisbox_assistant.log
│
├── docs/                    # Documentation
│   ├── USER_GUIDE.md        # Detailed user guide with examples
│   ├── API.md               # Complete API reference
│   ├── ENVIRONMENT_SETUP.md # Environment setup guide
│   └── ANALYSIS_EXAMPLES.md # Uncertainty analysis workflows (v0.3.0)
│
├── main.py                  # Production REPL with full commands
├── setup_env.sh             # Environment setup script
└── create_test_data.py      # Test data generation script
```

## Reference Documentation

- **User Guide**: `docs/USER_GUIDE.md` - Detailed usage examples and workflows
- **API Reference**: `docs/API.md` - Complete API documentation
- **Environment Setup**: `docs/ENVIRONMENT_SETUP.md` - API key configuration and setup
- **Analysis Examples**: `docs/ANALYSIS_EXAMPLES.md` - Uncertainty analysis workflows and report formats (v0.3.0)
- **Testing Guide**: `TESTING.md` - Comprehensive testing strategies
- **Contributing**: `CONTRIBUTING.md` - Contribution guidelines
- **Changelog**: `CHANGELOG.md` - Version history
