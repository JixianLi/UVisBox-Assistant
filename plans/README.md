# ChatUVisBox Implementation Plans

This directory contains detailed implementation plans for all 10 phases of the ChatUVisBox MVP development.

## Overview

These plans provide step-by-step guidance for building a natural language interface to UVisBox using LangGraph and Google Gemini API.

## Quick Navigation

### Milestone 1: Core Pipeline & Structure (Phases 1-4.5) - ~4-7 days ✅ COMPLETE

| Phase | Document | Focus | Duration | Status |
|-------|----------|-------|----------|--------|
| **Phase 1** ✅ | [Schemas & Dispatchers](phase_01_schemas_and_dispatchers.md) | Data/viz tools and function schemas | 1-2 days | Complete (2025-10-26) |
| **Phase 2** ✅ | [LangGraph State & Nodes](phase_02_langgraph_state_and_nodes.md) | State definition and core nodes | 1 day | Complete (2025-10-26) |
| **Phase 3** ✅ | [Graph Wiring & Routing](phase_03_graph_wiring_and_routing.md) | Complete graph assembly | 0.5-1 day | Complete (2025-10-26) |
| **Phase 4** ✅ | [End-to-End Test](phase_04_end_to_end_test.md) | Happy path validation | 0.5 day | Complete (2025-10-27) |
| **Phase 4.5** ✅ | [Codebase Restructure](phase_04.5_codebase_restructure.md) | Professional package structure | 1-2 days | Complete (2025-10-27) |

**Milestone 1 Output**: ✅ Working data → viz pipeline with professional Python package structure

---

### Milestone 2: Robustness & Conversation (Phases 5-7) - ~2-3 days

| Phase | Document | Focus | Duration |
|-------|----------|-------|----------|
| **Phase 5** | [Error Handling](phase_05_error_handling.md) | Error recovery and context awareness | 0.5-1 day |
| **Phase 6** | [Conversational Follow-up](phase_06_conversational_followup.md) | Multi-turn conversations | 0.5 day |
| **Phase 7** | [Hybrid Control](phase_07_hybrid_control.md) | Fast parameter updates | 0.5-1 day |

**Milestone 2 Output**: Robust agent with conversation memory and fast updates

---

### Milestone 3: Polish & Finalization (Phases 8-10) - ~2-3 days

| Phase | Document | Focus | Duration |
|-------|----------|-------|----------|
| **Phase 8** | [Session Management](phase_08_session_management.md) | File cleanup and REPL polish | 0.5 day |
| **Phase 9** | [Final Testing](phase_09_final_testing.md) | Comprehensive test coverage | 1 day |
| **Phase 10** | [Documentation & Packaging](phase_10_documentation_and_packaging.md) | Docs and release prep | 0.5-1 day |

**Milestone 3 Output**: Production-ready MVP with full documentation

---

## Additional Documents

- **[Project Modifications](00_project_modifications.md)** - Review of original plan with recommended changes

## Key Decisions & Recommendations

### 1. Agent Architecture ✅ Recommended

**Use**: Single LangGraph workflow with two tool sets (data_tools + viz_tools)

**Why**:
- More efficient than true two-agent handoff
- Simpler state management
- Achieves same functional goal

### 2. MVP Visualization Scope ✅ Recommended

**Include** (matplotlib-based 2D):
- `functional_boxplot`
- `curve_boxplot`
- `probabilistic_marching_squares`
- `uncertainty_lobes`

**Exclude** (3D/PyVista):
- All marching cubes/tetrahedra
- 3D squid glyphs

### 3. Tech Stack ✅ Confirmed

- Python 3.9+
- LangGraph for orchestration
- Google Gemini API (gemini-2.0-flash)
- matplotlib for rendering
- .npy files for intermediate storage

### 4. Hybrid Control ✅ Critical Feature

Simple commands (e.g., "colormap plasma") bypass full LangGraph for speed.

## Timeline Estimate

- **Fast track**: 7 days (experienced developer, no blockers)
- **Normal pace**: 10-11 days (with learning curve)
- **Thorough approach**: 14 days (with extensive testing)

## Implementation Order

Follow phases sequentially - each builds on the previous:

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 (Core working)
   ↓
Phase 5 → Phase 6 → Phase 7 (Robustness added)
   ↓
Phase 8 → Phase 9 → Phase 10 (Polish & release)
```

## Before You Start

### Prerequisites Checklist

- [ ] Conda environment created (`conda create -n agent python=3.10`)
- [ ] UVisBox installed (`pip install uvisbox`)
- [ ] `GEMINI_API_KEY` set in system environment
- [ ] Git repository initialized
- [ ] Project directory structure created

### Environment Setup

```bash
# Create and activate environment
conda create -n agent python=3.10
conda activate agent

# Install UVisBox
pip install uvisbox

# Verify installation
python -c "import uvisbox; print(uvisbox.__version__)"

# Verify API key is available (should already be in system environment)
echo $GEMINI_API_KEY

# If not set, add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
# export GEMINI_API_KEY="your_key_here"
```

## Using These Plans

Each phase document includes:

1. **Goal & Duration** - What you'll build and how long
2. **Prerequisites** - What must be completed first
3. **Tasks** - Step-by-step implementation tasks
4. **Code Examples** - Copy-paste ready code
5. **Tests** - Validation tests for each feature
6. **Validation Checklist** - Completion criteria
7. **Troubleshooting** - Common issues and solutions
8. **Output** - What you should have after completion

### Recommended Workflow

For each phase:

1. ✅ Read entire phase document first
2. ✅ Ensure prerequisites are met
3. ✅ Follow tasks sequentially
4. ✅ Test after each task
5. ✅ Complete validation checklist
6. ✅ Fix any issues before next phase

## Testing Strategy

Each phase includes tests. Run them frequently:

```bash
# Individual phase tests
python test_data_tools.py      # Phase 1
python test_nodes.py            # Phase 2
python test_graph.py            # Phase 3
python test_happy_path.py       # Phase 4
python test_error_handling.py   # Phase 5
python test_multiturn.py        # Phase 6
python test_hybrid_control.py   # Phase 7
python test_session_management.py # Phase 8

# Final comprehensive tests
python run_all_tests.py         # Phase 9
```

## Key Files Created

By the end of Phase 10, you'll have:

```
chatuvisbox/
├── main.py                    # Main REPL (Phase 8)
├── graph.py                   # LangGraph workflow (Phase 3)
├── state.py                   # State definitions (Phase 2)
├── nodes.py                   # Graph nodes (Phase 2)
├── routing.py                 # Routing logic (Phase 3)
├── model.py                   # LLM setup (Phase 2)
├── data_tools.py              # Data tools (Phase 1)
├── viz_tools.py               # Viz tools (Phase 1)
├── hybrid_control.py          # Hybrid control (Phase 7)
├── command_parser.py          # Command parsing (Phase 7)
├── conversation.py            # Session management (Phase 6)
├── config.py                  # Configuration (Phase 1)
├── utils.py                   # Utilities (Phase 2)
├── logger.py                  # Logging (Phase 5)
├── viz_manager.py             # Window management (Phase 8)
├── test_data/                 # Sample data (Phase 1)
├── temp/                      # Temp files (Phase 1)
├── tests/                     # All test files (Phases 4-9)
├── docs/                      # Documentation (Phase 10)
├── requirements.txt           # Dependencies (Phase 1, finalized Phase 10)
└── README.md                  # Main docs (Phase 10)
```

## Success Criteria

Your MVP is complete when:

- ✅ All tests in Phase 9 pass
- ✅ User can install following README.md only
- ✅ All 4 visualization types work
- ✅ Conversational follow-up works
- ✅ Hybrid control speeds up parameter updates
- ✅ Error handling is graceful
- ✅ Documentation is comprehensive

## Getting Help

If you encounter issues:

1. Check the **Troubleshooting** section in each phase
2. Verify **Prerequisites** are met
3. Review **Validation Checklist** for missed steps
4. Check code examples match your implementation
5. Run relevant tests to isolate issues

## Next Steps

1. Review [Project Modifications](00_project_modifications.md) and confirm decisions
2. Set up your environment (see checklist above)
3. Start with [Phase 1: Schemas & Dispatchers](phase_01_schemas_and_dispatchers.md)

---

**Good luck building ChatUVisBox!** 🚀

Each phase is designed to be self-contained with clear inputs and outputs. Follow them sequentially, test thoroughly, and you'll have a working MVP in ~1-2 weeks.
