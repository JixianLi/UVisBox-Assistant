# UVisBox-Assistant

Natural language interface for the [UVisBox](https://github.com/VCCRI/UVisBox) uncertainty visualization library.

## Overview

UVisBox-Assistant allows you to create uncertainty visualizations using natural language commands. Powered by Google Gemini and LangGraph, it provides an interactive conversational interface for exploring and visualizing uncertainty in scientific data.

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
- Python 3.10-3.13
- Conda environment (recommended for UVisBox)
- Google Gemini API key

### Setup

1. **Set environment variable**:
```bash
export GEMINI_API_KEY="your-api-key-here"
```

2. **Create and activate environment**:
```bash
conda create -n agent python=3.13
conda activate agent
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
pip install uvisbox
```

4. **Run the application**:
```bash
python main.py
# Or: python -m uvisbox_assistant
```

## Project Structure

```
uvisbox-assistant/
├── src/uvisbox_assistant/
│   ├── main.py                 # Main REPL entry point
│   ├── graph.py                # LangGraph workflow
│   ├── state.py                # State definitions
│   ├── nodes.py                # Graph nodes
│   ├── routing.py              # Routing logic
│   ├── model.py                # LLM setup
│   ├── data_tools.py           # Data loading/generation tools
│   ├── vis_tools.py            # Visualization wrappers (BoxplotStyleConfig)
│   ├── hybrid_control.py       # Fast parameter updates
│   ├── command_parser.py       # Command parsing (13 patterns)
│   ├── conversation.py         # Session management
│   ├── config.py               # Configuration
│   └── utils.py                # Utilities
├── test_data/                  # Sample datasets
├── temp/                       # Temporary files (auto-generated)
├── tests/                      # Test suites
├── requirements.txt            # Dependencies
└── pyproject.toml              # Poetry configuration
```

## Requirements

See `requirements.txt`:

- `langgraph>=0.2.76`
- `langchain>=0.3.27`
- `langchain-google-genai>=2.1.12`
- `uvisbox` (installed separately)
- `numpy>=2.0`
- `pandas>=2.3.3`
- `matplotlib>=3.10.7`
- `langsmith>=0.4.38`

## Development

### Running Tests

```bash
# Quick sanity check
python tests/test_simple.py

# Unit tests (0 API calls, fast)
python tests/utils/run_all_tests.py --unit

# Integration tests (includes BoxplotStyleConfig params)
python tests/utils/run_all_tests.py --integration

# E2E tests (full styling coverage)
python tests/utils/run_all_tests.py --e2e

# All tests
python tests/utils/run_all_tests.py
```

See `TESTING.md` for comprehensive testing guide.

## Documentation

- **User Guide**: `docs/USER_GUIDE.md` - Detailed styling control examples
- **API Reference**: `docs/API.md` - Complete BoxplotStyleConfig documentation
- **Developer Guide**: `CLAUDE.md` - Implementation details and architecture
- **Testing Guide**: `TESTING.md` - Comprehensive testing strategies

## License

MIT

## Citation

If you use UVisBox in your research, please cite the original UVisBox paper. See the [UVisBox repository](https://github.com/ouermijudicael/UVisBox) for citation details.

---

Made with ❤️ for uncertainty visualization
