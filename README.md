# UVisBox-Assistant

Natural language interface for the [UVisBox](https://github.com/ouermijudicael/UVisBox) uncertainty visualization library.

## Overview

UVisBox-Assistant allows you to create uncertainty visualizations using natural language commands. Powered by a local Ollama LLM and LangGraph, it provides an interactive conversational interface for exploring and visualizing uncertainty in scientific data.

## Features

- **Natural Language Interface**: Describe what you want in plain English
- **Conversational**: Multi-turn conversations with context preservation
- **Fast Parameter Updates**: Quick visualization adjustments without reprocessing
- **Fine-Grained Control**: Control all BoxplotStyleConfig styling parameters
- **Multiple Visualization Types**: Functional boxplots, curve boxplots, probabilistic marching squares, contour boxplots, uncertainty lobes, and squid glyphs
- **Session Management**: Clean file management and session control

## Quick Start

### Example: Styling Control

```
You: Generate 30 curves and plot functional boxplot
Assistant: [displays plot]
You: median color blue
Assistant: [updates median to blue]
You: median width 2.5
Assistant: [updates median width]
You: show outliers
Assistant: [shows outliers]
You: outliers color black
Assistant: [updates outliers to black]
You: outliers alpha 1.0
Assistant: [updates outliers transparency]
```

## Available Visualizations

### 1. Functional Boxplot
Visualizes band depth for multiple 1D curves with full styling control.

**Example**: `Generate 40 curves and show functional boxplot with median color blue`

**BoxplotStyleConfig Parameters**:
- **Percentiles**: `percentiles` (list), `percentile_colormap` (str)
- **Median Styling**: `show_median` (bool), `median_color` (str), `median_width` (float), `median_alpha` (float)
- **Outliers Styling**: `show_outliers` (bool), `outliers_color` (str), `outliers_width` (float), `outliers_alpha` (float)

### 2. Curve Boxplot
Ensemble curves with depth-based coloring and parallel band depth computation.

**Example**: `Plot curve boxplot with median color red and 8 workers`

**Parameters**: Same as Functional Boxplot + `workers` (int, default: 12)

### 3. Contour Boxplot
Band depth visualization of binary contours from scalar field ensembles.

**Example**: `Show contour boxplot at isovalue 0.5 with median color blue`

**Parameters**: Same as Functional Boxplot + `isovalue` (float) + `workers` (int)

### 4. Probabilistic Marching Squares
2D scalar field uncertainty visualization.

**Example**: `Generate scalar field 40x40 and show marching squares at isovalue 0.6`

**Parameters**: `isovalue`, `colormap`

### 5. Uncertainty Lobes
Directional uncertainty visualization for vector fields.

**Example**: `Show uncertainty lobes with percentile1 90 and percentile2 50`

**Parameters**: `percentile1` (0-100), `percentile2` (0-100), `scale`

### 6. Squid Glyph 2D
2D vector uncertainty visualization using squid-shaped glyphs with depth-based filtering.

**Example**: `Show squid glyphs with percentile 95 and scale 0.3`

**Parameters**: `percentile` (0-100, default: 95), `scale` (default: 0.2), `workers`

## Quick Commands (Hybrid Control)

For fast parameter updates without full reprocessing:

### Basic Parameters
- `colormap <name>` - Change colormap (e.g., `colormap plasma`)
- `percentile <value>` - Update percentile
- `isovalue <value>` - Update isovalue
- `show median` / `hide median` - Toggle median display
- `show outliers` / `hide outliers` - Toggle outliers

### Median Styling
- `median color <color>` - Set median color (e.g., `median color blue`)
- `median width <number>` - Set median line width (e.g., `median width 2.5`)
- `median alpha <number>` - Set median transparency (e.g., `median alpha 0.8`)

### Outliers Styling
- `outliers color <color>` - Set outliers color (e.g., `outliers color black`)
- `outliers width <number>` - Set outliers line width (e.g., `outliers width 1.5`)
- `outliers alpha <number>` - Set outliers transparency (e.g., `outliers alpha 1.0`)

### Other
- `scale <value>` - Update glyph scale
- `alpha <value>` - Update general transparency

## Installation

### Prerequisites
- Python 3.11-3.13
- Conda environment (recommended for UVisBox)
- A running [Ollama](https://ollama.com/) instance with a tool-capable model pulled (default: `qwen3-vl:8b`)

### Setup

1. **Start Ollama and pull the model** (if not already done):
```bash
ollama pull qwen3-vl:8b
```

2. **Configure connection** (defaults shown — only set these if you need to override):
```bash
export OLLAMA_API_URL="http://localhost:11434"
export OLLAMA_MODEL_NAME="qwen3-vl:8b"
```

3. **Create and activate environment**:
```bash
conda create -n agent python=3.13
conda activate agent
```

4. **Install dependencies**:
```bash
poetry install
pip install uvisbox
```

5. **Run the application**:
```bash
python main.py
# Or: python -m uvisbox_assistant
```

## Project Structure

```
uvisbox-assistant/
├── src/uvisbox_assistant/      # Feature-based architecture
│   ├── __init__.py             # Public API exports
│   ├── config.py               # Configuration
│   ├── main.py                 # Main REPL entry point
│   ├── core/                   # LangGraph workflow orchestration
│   │   ├── graph.py            # StateGraph (model, data_tool, vis_tool)
│   │   ├── nodes.py            # Graph node implementations
│   │   ├── routing.py          # Conditional routing with circuit breaker
│   │   └── state.py            # State definitions
│   ├── tools/                  # Data and visualization tools
│   │   ├── data_tools.py       # Data loading/generation
│   │   └── vis_tools.py        # Visualization wrappers (BoxplotStyleConfig)
│   ├── session/                # User interaction and session management
│   │   ├── conversation.py     # Session management
│   │   ├── hybrid_control.py   # Fast parameter updates
│   │   └── command_parser.py   # Command parsing
│   ├── llm/                    # LLM configuration
│   │   └── model.py            # Ollama model setup
│   ├── errors/                 # Error handling infrastructure
│   │   ├── error_tracking.py   # Error storage and recording
│   │   └── error_interpretation.py  # Context-aware error hints
│   └── utils/                  # Utilities and logging
│       ├── logger.py           # Logging infrastructure
│       ├── output_control.py   # Verbose mode control
│       └── utils.py            # Utility functions
├── test_data/                  # Sample datasets
├── temp/                       # Temporary files (auto-generated)
├── tests/                      # Test suites
├── scripts/                    # Helper scripts
└── pyproject.toml              # Poetry configuration
```

## Requirements

Managed via Poetry (see `pyproject.toml`):

- `langchain>=1.2.15`
- `langchain-ollama>=1.1.0`
- `langgraph>=1.1.10`
- `uvisbox` (installed separately)
- `numpy>=2.0`
- `pandas>=3.0.2`
- `matplotlib>=3.10.7`
- `scikit-learn>=1.7.2`, `scikit-image>=0.26.0`, `scipy>=1.16.3`
- `langsmith>=0.7.37`

## Development

### Testing

```bash
# Quick validation (0 LLM calls, < 30 seconds)
python tests/test.py --pre-planning

# Smoke test (minimal LLM usage, ~3 calls)
python tests/test.py --iterative --llm-subset=smoke

# Full test suite
python tests/test.py --acceptance
```

See [TESTING.md](TESTING.md) for details.

## Documentation

- **User Guide**: `docs/USER_GUIDE.md` - Detailed styling control examples
- **API Reference**: `docs/API.md` - Complete BoxplotStyleConfig documentation
- **Testing Guide**: `TESTING.md` - Comprehensive testing strategies

## License

MIT

## Citation

If you use UVisBox in your research, please cite the original UVisBox paper. See the [UVisBox repository](https://github.com/ouermijudicael/UVisBox) for citation details.

---

Made with ❤️ for uncertainty visualization
