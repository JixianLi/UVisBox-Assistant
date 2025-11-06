# UVisBox-Assistant Development Guide

## Project Overview

UVisBox-Assistant (uva) is a LangGraph-powered conversational agent for uncertainty visualization using UVisBox. This document covers architecture patterns and development conventions not found in other docs.

## Architecture

### LangGraph Workflow

The agent uses a 5-node StateGraph with conditional routing:

```
START -> model -> [conditional routing]
              -> data_tool -> model
              -> vis_tool -> model
              -> statistics_tool -> model
              -> analyzer_tool -> model
              -> END
```

**State Management** (`src/uvisbox_assistant/core/state.py`):
- `messages`: Accumulated with `operator.add`
- Single-value fields (overwritten): `current_data_path`, `last_vis_params`
- Analysis state: `raw_statistics`, `processed_statistics`, `analysis_reports`

**Circuit Breaker**: Stops execution after 3 consecutive tool errors to prevent infinite loops.

### Dual-Mode Execution

1. **Full Graph Mode**: Multi-turn conversations through Gemini (slow, flexible)
2. **Hybrid Control Mode**: Direct parameter updates via `command_parser.py` (fast, no API calls)
   - Handles 16 quick command patterns (e.g., "median color blue", "show outliers")
   - Bypasses full graph for simple parameter changes

### Tool Response Pattern

All tools return consistent dict structure:
```python
{
    "status": "success" | "error",
    "message": str,
    "_vis_params": dict,  # Optional: for parameter tracking
    "_error_details": str  # Optional: for debugging
}
```

## Development Workflow

Feature development follows this pipeline:
1. **Brainstorm** -> Design plan -> Implementation plan
2. **Git worktree + branching** for isolation
3. **Iterative development + code review** (minimal integration tests)
4. **Acceptance test** (all tests)
5. **Feature refinement** -> Merge to main

## Testing Strategy (CRITICAL: API Budget Awareness)

### Test Categories

| Category | Count | LLM Calls | When to Run |
|----------|-------|-----------|-------------|
| Unit | 277 | 0 | Every code review |
| Integration (UVisBox Interface) | 21 | 0 | Every code review |
| Integration (LLM Integration) | 15 | ~40 | Minimal subset during iteration |
| E2E | 15 | ~60 | Acceptance test stage only |

**API Budget Rule**: Run ONLY minimal integration tests during iterative development. Run full test suite only at acceptance stage.

### Test Runner
```bash
# During development (no API calls)
python tests/test.py --pre-planning

# Minimal integration (specific feature)
python tests/test.py --iterative --llm-subset=analyzer

# Acceptance stage (all tests)
python tests/test.py --acceptance
```

### Integration Test Layers

**UVisBox Interface** (`uvisbox_interface/`): Tool -> UVisBox interface validation
- Tests actual UVisBox function calls with real data
- Verifies parameter passing, error handling
- 0 LLM calls

**LLM Integration** (`llm_integration/`): Individual LLM-powered features
- Tests specific components that require LLM calls
- Verifies analyzer, routing, error handling, session management
- ~40 LLM calls total

**E2E** (`e2e/`): Complete workflows through Gemini
- Tests full graph execution with LLM
- Verifies routing, state management, multi-turn conversations
- ~60 LLM calls total

## Code Organization

**Feature-based structure** (since v0.3.1):
```
src/uvisbox_assistant/
    core/          # LangGraph orchestration (graph, state, nodes, routing)
    tools/         # Tool implementations (data, vis, statistics, analyzer)
    session/       # User interaction (conversation, hybrid_control, command_parser)
    llm/           # Gemini configuration
    errors/        # Error tracking and interpretation
  utils/         # Logging, output control, data loading
```

## Key Conventions

1. **All source files start with `ABOUTME:` comments** (2 lines explaining file purpose)
2. **No temporal/implementation names**: Never use "New", "Legacy", "Wrapper", "Improved" in names
3. **Type hints throughout**: All public functions have complete type annotations
4. **100-char line length**: PEP 8 style
5. **Temp file prefix**: All temporary files use `config.TEMP_FILE_PREFIX` ("uva_")

## Error Handling Pattern

All nodes use try-except with error tracking:
```python
try:
    result = tool_function(**params)
    return {"status": "success", ...}
except Exception as e:
    error_id = track_error(tool_name, str(e), context)
    hint = get_error_interpretation(error_id, state)
    return {"status": "error", "message": f"Error: {e}\n\nHint: {hint}"}
```

## External Dependencies

**UVisBox**: Source dependency project (see `.claude-local.md` for local path)
- Interface may change; always run `python tests/test.py --pre-planning` after UVisBox updates
- 6 visualization functions wrapped: functional_boxplot, curve_boxplot, probabilistic_marching_squares, uncertainty_lobes, contour_boxplot, squid_glyph_2D

**Python**: Conda environment `agent` (see `.claude-local.md` for local path)

**Package Management**: Poetry (all dev packages in `[tool.poetry.group.dev.dependencies]`)

## Common Development Tasks

**Add a new visualization tool**:
1. Wrap UVisBox function in `src/uvisbox_assistant/tools/vis_tools.py`
2. Add to tool definitions in `src/uvisbox_assistant/llm/model.py`
3. Add integration test in `tests/uvisbox_interface/test_tool_interfaces.py`
4. Update API.md

**Modify LangGraph workflow**:
1. Update graph structure in `src/uvisbox_assistant/core/graph.py`
2. Modify routing logic in `src/uvisbox_assistant/core/routing.py`
3. Update state in `src/uvisbox_assistant/core/state.py` if needed
4. Add unit tests for routing logic
5. Add integration test for full workflow

**Add quick command**:
1. Add pattern to `src/uvisbox_assistant/session/command_parser.py`
2. Implement in `src/uvisbox_assistant/session/hybrid_control.py`
3. Add unit test in `tests/unit/test_command_parser.py`

## Documentation Files Reference

- **README.md**: Project overview, quick start, installation
- **TESTING.md**: Comprehensive testing guide (structure, roles, coverage)
- **CONTRIBUTING.md**: Dev setup, code standards, naming conventions
- **API.md**: Complete API reference for all tools
- **USER_GUIDE.md**: Styling examples, user commands
- **ANALYSIS_EXAMPLES.md**: Uncertainty analysis workflows
- **ENVIRONMENT_SETUP.md**: Prerequisites, environment setup

See these docs for user-facing information and API details.
