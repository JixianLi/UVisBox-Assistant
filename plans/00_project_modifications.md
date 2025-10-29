# Project Plan Modifications & Recommendations

## Overview
This document outlines recommended modifications to the original 10-phase plan based on review and the two-agent architecture requirement.

## Key Modifications

### 1. Agent Architecture
**Current Plan**: Single LangGraph workflow with tool-calling nodes
**Your Request**: Two-agent system (data agent + vis agent)

**Recommendation**: Keep the current plan's architecture (single graph with two tool sets) because:
- More efficient for MVP - single conversation context
- Easier state management - one graph state
- Natural tool-calling flow: User → Model → Data Tool → Model → Vis Tool → End
- The "two agents" concept is effectively implemented as two specialized tool dispatchers

**If you prefer true two-agent architecture**, we would need:
- Separate `DataAgent` graph and `VisAgent` graph
- Handoff mechanism between agents
- Duplicated model calls (less efficient)
- More complex state synchronization

### 2. MVP Visualization Scope

**Limit to matplotlib-based 2D visualizations only:**

| Function | Include? | Reason |
|----------|----------|--------|
| `functional_boxplot` | ✅ Yes | 2D, matplotlib, good starter |
| `curve_boxplot` | ✅ Yes | 2D, matplotlib, core use case |
| `probabilistic_marching_squares` | ✅ Yes | 2D, matplotlib, uncertainty vis |
| `squid_glyph_2D` | ✅ Yes | 2D, matplotlib, vector uncertainty |
| `uncertainty_lobes` | ✅ Yes | 2D, matplotlib, vector uncertainty |
| `uncertainty_tubes_2D` | ✅ Yes | 2D, matplotlib, trajectory uncertainty |
| `contour_boxplot` | ✅ Yes | 2D, matplotlib, contour band depth (added 2025-10-28) |
| `squid_glyph_3D` | ❌ No | PyVista, not matplotlib |
| `probabilistic_marching_cubes` | ❌ No | PyVista, 3D, too complex for MVP |
| `probabilistic_marching_tetrahedra` | ❌ No | PyVista, 3D, too complex for MVP |
| `probabilistic_marching_triangles` | ❌ No | 2D but complex triangulation |

**Implemented (5 functions)**: `functional_boxplot`, `curve_boxplot`, `probabilistic_marching_squares`, `uncertainty_lobes`, `contour_boxplot`

### 3. Data Tools Specification

Define concrete data tools for MVP:

```python
# data_tools.py

def load_csv_to_numpy(filepath: str, output_path: str) -> dict:
    """Load CSV file and save as .npy"""

def load_npy(filepath: str) -> dict:
    """Load existing .npy file"""

def generate_ensemble_curves(n_curves: int, n_points: int, output_path: str) -> dict:
    """Generate synthetic ensemble curve data for testing"""

def generate_scalar_field_ensemble(nx: int, ny: int, n_ens: int, output_path: str) -> dict:
    """Generate synthetic 2D scalar field ensemble"""

def compute_curve_statistics(input_path: str, output_path: str) -> dict:
    """Compute statistics (mean, median, std) on curve ensembles"""

def clear_session() -> dict:
    """Remove all temporary .npy files"""
```

### 4. Additional Phase Modifications

#### Phase 1 Additions:
- Create `test_data/` directory with sample CSV files
- Create `temp/` directory for .npy intermediate files
- Add dependency verification step

#### Phase 2 Additions:
- Define GraphState with fields:
  - `messages: List[BaseMessage]`
  - `current_data_path: Optional[str]`
  - `last_vis_params: Optional[dict]`
  - `session_files: List[str]`

#### Phase 4 Additions:
- Test with all 3-4 selected vis functions
- Verify matplotlib window doesn't block execution

#### Phase 7 Clarification:
- Hybrid control commands: `"colormap viridis"`, `"percentile 90"`, `"show median"`
- These bypass LangGraph and directly update vis params

#### Phase 9 Additions:
- Test prompts for each vis function
- Test error cases: missing files, wrong data shapes, invalid parameters

### 5. Project Structure

```
chatuvisbox/
├── main.py                 # CLI entry point with REPL
├── graph.py                # LangGraph workflow definition
├── state.py                # GraphState definition
├── data_tools.py           # Data loading/transformation tools
├── vis_tools.py            # UVisBox visualization wrappers
├── utils.py                # Helper functions
├── config.py               # Configuration (reads GEMINI_API_KEY from env)
├── test_data/              # Sample datasets
│   ├── sample_curves.csv
│   ├── sample_scalar_field.csv
│   └── README.md
├── temp/                   # Temporary .npy files (gitignored)
├── plans/                  # Implementation plans (this directory)
├── requirements.txt
└── README.md
```

### 6. Dependencies to Verify

```txt
langgraph>=0.0.20
langchain>=0.1.0
google-generativeai>=0.3.0
uvisbox                     # Your package in conda 'agent' env
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.7.0
langsmith (optional)        # For tracing
```

**Note**: `GEMINI_API_KEY` must be set in your system environment (no .env file needed).

### 7. Testing Strategy

Each phase should include:
- **Unit tests**: Individual tool functions
- **Integration tests**: Graph execution paths
- **Example prompts**: Real user scenarios

**Sample test prompts**:
- Simple: `"Load test_data/curves.csv and plot it as a functional boxplot"`
- Multi-step: `"Load curves.csv, compute statistics, then show me the curve boxplot with 75th percentile"`
- Error handling: `"Load nonexistent.csv"`
- Follow-up: `"Load curves.csv"` → `"Now plot it"` → `"Change colormap to plasma"`

### 8. Environment Setup

Before Phase 1:
```bash
# Activate conda environment
conda activate agent

# Verify UVisBox is installed
python -c "import uvisbox; print(uvisbox.__version__)"

# Install dependencies
pip install langgraph langchain google-generativeai

# Verify API key is available (already in system environment)
echo $GEMINI_API_KEY
```

## Decision Points

Please confirm:
1. **Agent Architecture**: Stick with single-graph + two-tool-sets approach? (Recommended)
2. **Vis Functions**: Start with which 3-4 functions for MVP?
3. **LLM Provider**: Confirm Google Gemini API (gemini-2.0-flash)
4. **Data Format**: Stick with .npy for intermediate storage? (Could also use pickle or JSON for metadata)

## Timeline Estimate

- **Milestone 1** (Phases 1-4): 3-5 days
- **Milestone 2** (Phases 5-7): 2-3 days
- **Milestone 3** (Phases 8-10): 2-3 days

**Total**: ~7-11 days for full MVP

## Next Steps

1. Review these modifications
2. Confirm decisions above
3. Proceed with Phase 1 implementation using detailed plan
