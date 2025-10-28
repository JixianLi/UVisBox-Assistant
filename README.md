# ChatUVisBox

Natural language interface for the [UVisBox](https://github.com/VCCRI/UVisBox) uncertainty visualization library. ChatUVisBox uses LangGraph to orchestrate a conversational AI agent (powered by Google Gemini) that translates natural language requests into data processing and visualization operations.

**Status**: Phase 4 Complete + Enhancements (2025-10-28)

## Features

### Visualization Tools (5 total)
- **Functional Boxplot**: Band depth visualization for 1D curve ensembles
- **Curve Boxplot**: Depth-colored curves with multiple percentile bands
- **Probabilistic Marching Squares**: Uncertainty visualization for 2D scalar fields
- **Contour Boxplot**: Band depth of binary contours from scalar field ensembles
- **Uncertainty Lobes**: Directional uncertainty glyphs for vector ensembles

### Data Generation Tools
- **Curve Ensembles**: Synthetic sinusoidal curves with controlled variation
- **Scalar Field Ensembles**: 2D Gaussian fields with systematic uncertainty
- **Vector Field Ensembles**: 2D vector fields with directional and magnitude variation
- **CSV to NumPy**: Load and convert CSV data to .npy format

## Requirements

- **Python**: 3.10-3.13 (tested on 3.13)
- **Conda**: For environment management (UVisBox requires conda)
- **GEMINI_API_KEY**: Google Gemini API key (set in system environment)

## Installation

### 1. Set up environment variable
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export GEMINI_API_KEY="your-api-key-here"
```

### 2. Create conda environment
```bash
conda env create -f environment.yml
conda activate chatuvisbox
```

### 3. Install dependencies
```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

### 4. Install UVisBox
```bash
# UVisBox must be installed separately in the conda environment
pip install uvisbox
```

## Usage

### Quick Start
```python
from chatuvisbox.graph import create_graph

# Create the LangGraph workflow
graph = create_graph()

# Run a natural language query
result = graph.invoke({
    "messages": [{"role": "user", "content": "Generate 30 curves and show a functional boxplot"}]
})
```

### Example Queries
```python
# Curve visualization
"Generate 50 curves with 100 points each and create a functional boxplot"

# Scalar field uncertainty
"Generate a 50x50 scalar field ensemble and show probabilistic contours at isovalue 0.5"

# Contour boxplot
"Create a contour boxplot from a scalar field with isovalue 0.6"

# Vector field uncertainty
"Generate a 10x10 vector field and plot uncertainty lobes"
```

### Direct Tool Usage
```python
from chatuvisbox.data_tools import generate_ensemble_curves, generate_scalar_field_ensemble
from chatuvisbox.vis_tools import plot_functional_boxplot, plot_contour_boxplot

# Generate data
curves_result = generate_ensemble_curves(n_curves=50, n_points=100)
field_result = generate_scalar_field_ensemble(nx=50, ny=50, n_ensemble=30)

# Create visualizations
plot_functional_boxplot(data_path=curves_result['output_path'], percentiles=[25, 50, 90, 100])
plot_contour_boxplot(data_path=field_result['output_path'], isovalue=0.5)
```

## Testing

```bash
# Quick test (recommended, ~5 seconds, 9 API calls)
python test_graph_quick.py

# No API calls - instant validation
python test_phase1.py
python test_routing.py

# Full test suite with automatic delays (~5-7 minutes)
python run_tests_with_delays.py
```

See `TESTING.md` and `RATE_LIMIT_FRIENDLY_TESTING.md` for details on handling Gemini API rate limits.

## Project Structure

```
chatuvisbox/
├── src/chatuvisbox/       # Main package
│   ├── graph.py          # LangGraph workflow definition
│   ├── state.py          # GraphState schema
│   ├── nodes.py          # Graph nodes (model, tools)
│   ├── routing.py        # Conditional routing logic
│   ├── model.py          # Gemini model setup
│   ├── data_tools.py     # Data generation functions
│   ├── vis_tools.py      # UVisBox visualization wrappers
│   └── config.py         # Configuration
├── test_data/            # Sample datasets
├── temp/                 # Temporary .npy files (gitignored)
├── plans/                # Implementation phase guides
└── tests/                # Test suite
```

## Development

- **Implementation Guide**: See `CLAUDE.md` for detailed development guidelines
- **Phase Plans**: Follow `plans/README.md` for sequential implementation phases
- **API Reference**: UVisBox function signatures documented in `CLAUDE.md`

## Current Limitations

- **Gemini Free Tier**: 30 requests per minute (using gemini-2.0-flash-lite)
- **2D Only**: 3D/PyVista visualizations excluded from MVP
- **No Persistence**: Conversation state not saved between sessions (Phase 6)
- **No Fast Path**: Hybrid control for parameter updates not yet implemented (Phase 7)

## License

MIT

## Citation

If you use UVisBox in your research, please cite:
```
[UVisBox citation - see UVisBox repository]
```
