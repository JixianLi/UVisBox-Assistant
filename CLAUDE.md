# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ChatUVisBox** is a natural language interface for the UVisBox uncertainty visualization library. It uses LangGraph to orchestrate a conversational AI agent (powered by Google Gemini) that translates natural language requests into data processing and visualization operations.

**Current State**: Phase 2 Complete (2025-10-26). Implementing phases sequentially per `plans/` directory.

**Completed Phases**:
- ✅ **Phase 1**: Tool definitions, schemas, data/viz tools with UVisBox wrappers (2025-10-26)
- ✅ **Phase 2**: LangGraph state management, model setup, core nodes (2025-10-26)

## Architecture

### Core Design Pattern: Hybrid Control Model

The system uses a **two-tier execution model**:

1. **Full LangGraph Workflow** (for complex/ambiguous requests):
   - User Input → Model Node → Tool Dispatcher (data or viz) → Model Node → Response
   - Maintains conversation state across multi-turn interactions
   - Handles data loading, transformation, and visualization in sequence

2. **Hybrid Fast Path** (for simple parameter updates):
   - Direct pattern matching (e.g., "colormap plasma", "percentile 80")
   - Bypasses LangGraph for ~10x speed improvement
   - Updates `last_viz_params` and re-executes visualization directly

### Key Components

```
graph.py          - LangGraph StateGraph definition with conditional routing (TODO: Phase 3)
state.py          - ✅ DONE: GraphState TypedDict: messages, current_data_path, last_viz_params, session_files
nodes.py          - ✅ DONE: Three core nodes: call_model, call_data_tool, call_viz_tool
routing.py        - Conditional logic: route_after_model, route_after_tool (TODO: Phase 3)
model.py          - ✅ DONE: ChatGoogleGenerativeAI setup with tool binding
utils.py          - ✅ DONE: Tool type detection and file management utilities
data_tools.py     - ✅ DONE: Functions: load_csv_to_numpy, generate_ensemble_curves, load_npy, generate_scalar_field_ensemble
viz_tools.py      - ✅ DONE: UVisBox wrappers: plot_functional_boxplot, plot_curve_boxplot, probabilistic_marching_squares, uncertainty_lobes
config.py         - ✅ DONE: Configuration (API key, paths, defaults)
hybrid_control.py - Pattern matching for fast parameter updates (TODO: Phase 7)
conversation.py   - ConversationSession class for multi-turn state management (TODO: Phase 6)
main.py           - Interactive REPL with command handling (/help, /context, /clear, /quit) (TODO: Phase 8)
```

### LangGraph Flow

```
START → call_model → [route_after_model]
                         ├─ data_tool → call_model (loop for multi-step)
                         ├─ viz_tool  → call_model (confirm to user)
                         └─ END (direct response)
```

### State Management

**GraphState fields**:
- `messages`: Full conversation history (List[BaseMessage])
- `current_data_path`: Path to most recent .npy file
- `last_viz_params`: Dict with `_tool_name`, `data_path`, and viz parameters
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

**Milestone 1 (Days 1-5)**: Core Pipeline
- Phase 1: Create data_tools.py, viz_tools.py, config.py with tool schemas
- Phase 2: Create state.py, nodes.py, model.py
- Phase 3: Create graph.py with routing logic
- Phase 4: End-to-end happy path test

**Milestone 2 (Days 6-8)**: Robustness
- Phase 5: Error handling with circuit breaker
- Phase 6: Multi-turn conversation with ConversationSession
- Phase 7: Hybrid control with command_parser.py

**Milestone 3 (Days 9-11)**: Polish
- Phase 8: Session management with clear_session tool
- Phase 9: Comprehensive testing (pytest + manual)
- Phase 10: Documentation and packaging

### Testing Commands

```bash
# Individual phase tests (create as you implement)
python test_data_tools.py
python test_nodes.py
python test_graph.py
python test_happy_path.py
python test_error_handling.py
python test_multiturn.py
python test_hybrid_control.py
python test_session_management.py

# Comprehensive test suite (Phase 9)
python test_comprehensive.py
python run_all_tests.py
```

### Running the Application

```bash
# After implementation is complete
python main.py
```

## Key Design Decisions

### 1. Single LangGraph vs Two-Agent Architecture
**Decision**: Use single LangGraph workflow with two tool registries (data_tools + viz_tools).
**Rationale**: More efficient than agent handoff; simpler state management; achieves same functional goal.

### 2. MVP Visualization Scope
**Include** (matplotlib-based 2D):
- functional_boxplot (1D curve ensembles)
- curve_boxplot (depth-colored curves)
- probabilistic_marching_squares (2D scalar field uncertainty)
- uncertainty_lobes (vector uncertainty)

**Exclude**: All 3D/PyVista visualizations (marching cubes, tetrahedra, 3D squids)

### 3. Matplotlib Non-Blocking
Always use `plt.show(block=False)` + `plt.pause(0.1)` to allow REPL interaction while plots are open.

### 4. Error Handling Pattern
- All tool functions return `{"status": "success"|"error", "message": ..., ...}`
- Tool nodes wrap execution in try-except, always return ToolMessage
- Graph loops back to model on error for clarification
- Circuit breaker: `error_count >= 3` → route to END

### 5. File Naming Convention
- Test data: `test_data/sample_curves.csv`, `test_data/sample_scalar_field.npy`
- Temp files: `temp/_temp_*.npy` (auto-generated, gitignored)
- Clear on session end with `clear_session()` tool

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
    model="gemini-2.0-flash",
    google_api_key=config.GEMINI_API_KEY,
    temperature=0.0
)
model_with_tools = model.bind_tools(DATA_TOOL_SCHEMAS + VIZ_TOOL_SCHEMAS)
```

### Viz Tool Return Pattern
Include `_viz_params` in return dict for hybrid control:
```python
return {
    "status": "success",
    "message": "...",
    "_viz_params": {
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

See `interface.md` for complete function signatures. Key matplotlib-based functions for MVP:

- `functional_boxplot(data, method='fdb', percentiles=[25, 50, 90, 100], ax=None, colors=None, alpha=0.7)` ⚠️ **Updated 2025-10-26**
- `curve_boxplot(curves, percentiles=[25, 50, 90, 100], ax=None, colors=None, alpha=0.7)` ⚠️ **Updated 2025-10-26**
- `probabilistic_marching_squares(F, isovalue, cmap='viridis', ax=None)`
- `uncertainty_lobes(positions, ensemble_vectors, percentil1, percentil2=None, scale=0.2, ax=None)`

All expect numpy arrays and return matplotlib axes.

### API Changes

**2025-10-26**: Both `functional_boxplot` and `curve_boxplot` updated to support multiple percentile bands:

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
6. **Don't forget _tool_name** - Required in viz params for hybrid control
7. **Don't exceed error threshold** - Circuit breaker at 3 consecutive errors
8. **Don't mix GOOGLE_API_KEY and GEMINI_API_KEY** - Use `GEMINI_API_KEY` consistently

## Implementation-Specific Notes (From Phase 1)

### UVisBox Import Path Issue
The correct import path for UVisBox functions is:
```python
# ❌ WRONG - Does not work
from uvisbox.Modules import functional_boxplot

# ✅ CORRECT - Use full module path
from uvisbox.Modules.FunctionalBoxplot.functional_boxplot import functional_boxplot
from uvisbox.Modules import curve_boxplot  # These work at top level
from uvisbox.Modules import probabilistic_marching_squares
from uvisbox.Modules import uncertainty_lobes
```

### Visualization Return Format
All viz tools MUST include `_viz_params` for hybrid control (Phase 7):
```python
return {
    "status": "success",
    "message": "Displayed functional boxplot for 30 curves",
    "_viz_params": {
        "_tool_name": "plot_functional_boxplot",
        "data_path": data_path,
        "percentile": percentile,
        "show_median": show_median
    }
}
```

## File Structure (Current Implementation Status)

```
chatuvisbox/
├── main.py                  # TODO Phase 8: REPL entry point
├── graph.py                 # TODO Phase 3: LangGraph workflow
├── state.py                 # ✅ DONE Phase 2: GraphState definition (85 lines)
├── nodes.py                 # ✅ DONE Phase 2: call_model, call_data_tool, call_viz_tool (182 lines)
├── routing.py               # TODO Phase 3: Conditional routing logic
├── model.py                 # ✅ DONE Phase 2: ChatGoogleGenerativeAI setup (95 lines)
├── utils.py                 # ✅ DONE Phase 2: Utility functions (60 lines)
├── data_tools.py            # ✅ DONE Phase 1: Data loading/generation tools (278 lines)
├── viz_tools.py             # ✅ DONE Phase 1: UVisBox wrappers (401 lines)
├── config.py                # ✅ DONE Phase 1: Configuration (34 lines)
├── hybrid_control.py        # TODO Phase 7: Fast path for simple commands
├── command_parser.py        # TODO Phase 7: Pattern matching for hybrid control
├── conversation.py          # TODO Phase 6: ConversationSession class
├── logger.py                # TODO Phase 5: Logging setup (optional)
├── viz_manager.py           # TODO Phase 8: Matplotlib window tracking (optional)
├── test_data/               # ✅ DONE Phase 1: Sample CSV/NPY files
│   ├── sample_curves.csv
│   ├── sample_scalar_field.npy
│   └── README.md
├── temp/                    # ✅ DONE Phase 1: Generated .npy files (gitignored)
├── plans/                   # ✅ DONE: Implementation phase guides
│   ├── phase_01_*.md        # ✅ Phase 1 complete
│   └── phase_02_*.md        # ✅ Phase 2 complete
├── requirements.txt         # ✅ DONE: Python dependencies
├── ENVIRONMENT_SETUP.md     # ✅ DONE: API key configuration guide
├── .gitignore               # ✅ DONE Phase 1
├── test_phase1.py           # ✅ DONE Phase 1: Validation test suite
├── test_phase2.py           # ✅ DONE Phase 2: Comprehensive test suite
├── PHASE_1_COMPLETION_REPORT.md  # ✅ Phase 1 summary
├── PHASE_2_COMPLETION_REPORT.md  # ✅ Phase 2 summary
└── create_test_data.py      # ✅ DONE Phase 1: Test data generator
```

## Reference Documentation

- **Implementation Plans**: `plans/README.md` - Start here for step-by-step guidance
- **Project Modifications**: `plans/00_project_modifications.md` - Key decisions and rationale
- **UVisBox Functions**: `interface.md` - Complete function signatures
- **Environment Setup**: `ENVIRONMENT_SETUP.md` - API key configuration
- **Original Plan**: `ten_phase_plan.md` - High-level overview
