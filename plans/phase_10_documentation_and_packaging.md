# Phase 10: Documentation & Packaging

**Goal**: Create comprehensive documentation, package the project, and prepare for distribution.

**Duration**: 0.5-1 day

## Prerequisites

- Phases 1-9 completed
- All tests passing
- MVP fully functional

## Tasks

### Task 10.1: Create README.md

**File**: `README.md`

```markdown
# ChatUVisBox

Natural language interface for the [UVisBox](https://github.com/uvisbox/uvisbox) uncertainty visualization library.

## Overview

ChatUVisBox allows you to create uncertainty visualizations using natural language commands. Powered by Google Gemini and LangGraph, it provides an interactive conversational interface for exploring and visualizing uncertainty in scientific data.

## Features

- 🗣️ **Natural Language Interface**: Describe what you want in plain English
- 🔄 **Conversational**: Multi-turn conversations with context preservation
- ⚡ **Fast Parameter Updates**: Quick visualization adjustments without reprocessing
- 📊 **Multiple Visualization Types**: Functional boxplots, curve boxplots, probabilistic marching squares, contour boxplots, and uncertainty lobes
- 🎨 **Flexible**: Load CSV files or generate synthetic test data
- 💾 **Session Management**: Clean file management and session control

## Installation

### Prerequisites

- Python 3.9+
- Conda (recommended)
- Google Gemini API key set in system environment ([Get one here](https://ai.google.dev/))

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chatuvisbox.git
   cd chatuvisbox
   ```

2. **Create conda environment and install UVisBox**
   ```bash
   conda create -n agent python=3.10
   conda activate agent
   pip install uvisbox
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify API key is set**

   Ensure `GEMINI_API_KEY` is set in your system environment:
   ```bash
   echo $GEMINI_API_KEY
   ```

   If not set, add it to your shell profile (~/.bashrc, ~/.zshrc, etc.):
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

## Quick Start

### Example 1: Generate and Visualize Test Data

```
You: Generate 30 curves with 100 points and plot functional boxplot
Assistant: Generated 30 curves and displayed functional boxplot.
```

### Example 2: Load and Visualize CSV

```
You: Load test_data/sample_curves.csv and visualize
Assistant: Loaded sample_curves.csv. Would you like a functional boxplot?
You: Yes please
Assistant: Created functional boxplot visualization.
```

### Example 3: Quick Parameter Updates

```
You: Generate curves and plot
Assistant: [displays plot]
You: colormap plasma
Assistant: Updated colormap to plasma.
You: percentile 85
Assistant: Updated percentile to 85.
```

## Available Visualizations

### 1. Functional Boxplot
Visualizes band depth for multiple 1D curves.

**Example**: `Generate 40 curves and show functional boxplot`

**Parameters**: `percentile`, `show_median`, `colormap`

### 2. Curve Boxplot
Ensemble curves with depth-based coloring.

**Example**: `Plot curve boxplot with percentile 60`

**Parameters**: `percentile`, `colormap`

### 3. Probabilistic Marching Squares
2D scalar field uncertainty visualization.

**Example**: `Generate scalar field 40x40 and show marching squares at isovalue 0.6`

**Parameters**: `isovalue`, `colormap`

### 4. Uncertainty Lobes
Directional uncertainty visualization for vector fields.

**Example**: `Show uncertainty lobes with percentile 0.8`

**Parameters**: `percentile`, `scale`

## Data Tools

### Load CSV
```
Load mydata.csv
Load test_data/sample_curves.csv as curves
```

### Generate Test Data
```
Generate 50 curves with 100 points
Generate scalar field 40x40 with 25 ensemble members
```

### Session Management
```
/clear    - Clear all temporary files and reset session
/reset    - Reset conversation (keep files)
/stats    - Show session statistics
/context  - Show current state
```

## Quick Commands (Hybrid Control)

For fast parameter updates without full reprocessing:

- `colormap <name>` - Change colormap (e.g., `colormap plasma`, `colormap viridis`)
- `percentile <value>` - Update percentile (e.g., `percentile 90`)
- `isovalue <value>` - Update isovalue (e.g., `isovalue 0.7`)
- `show median` / `hide median` - Toggle median display
- `show outliers` / `hide outliers` - Toggle outliers
- `scale <value>` - Update glyph scale
- `alpha <value>` - Update transparency

## Project Structure

```
chatuvisbox/
├── main.py                 # Main REPL entry point
├── graph.py                # LangGraph workflow
├── state.py                # State definitions
├── nodes.py                # Graph nodes
├── routing.py              # Routing logic
├── model.py                # LLM setup
├── data_tools.py           # Data loading/generation tools
├── vis_tools.py            # Visualization wrappers
├── hybrid_control.py       # Fast parameter updates
├── command_parser.py       # Command parsing
├── conversation.py         # Session management
├── config.py               # Configuration
├── utils.py                # Utilities
├── test_data/              # Sample datasets
├── temp/                   # Temporary files (auto-generated)
├── tests/                  # Test suites
└── requirements.txt
```

## Requirements

See `requirements.txt` for full list:

- `langgraph>=0.0.20`
- `langchain>=0.1.0`
- `langchain-google-genai>=0.0.5`
- `google-generativeai>=0.3.0`
- `uvisbox` (installed separately)
- `numpy>=1.24.0`
- `pandas>=2.0.0`
- `matplotlib>=3.7.0`

## Troubleshooting

### Matplotlib windows don't appear
```bash
export MPLBACKEND=TkAgg
```

### API key errors
- Verify `.env` file exists and contains valid key
- Check quota at https://console.cloud.google.com/

### Import errors
```bash
conda activate agent
pip install --upgrade -r requirements.txt
```

### Slow performance
- Check internet connection (Gemini API calls)
- Use hybrid control commands for parameter updates
- Reduce data size for testing

## Development

### Running Tests

```bash
# Run all tests
python run_all_tests.py

# Run specific test suite
python test_happy_path.py
python test_error_handling.py
python test_comprehensive.py
```

### Adding New Visualization Types

1. Add wrapper function to `vis_tools.py`
2. Add schema to `VIS_TOOL_SCHEMAS`
3. Register in `VIS_TOOLS` dict
4. Add tests
5. Update documentation

## Architecture

ChatUVisBox uses a **hybrid control architecture**:

- **Complex queries** (ambiguous, multi-step) → Full LangGraph workflow
- **Simple commands** (parameter updates) → Direct function call (fast path)

**LangGraph Workflow**:
```
User Input → Model → [Data Tool / Viz Tool] → Model → Response
              ↑                                       ↓
              └───────── Loop for multi-step ────────┘
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## Citation

If you use ChatUVisBox in your research, please cite:

```bibtex
@software{chatuvisbox2024,
  title={ChatUVisBox: Natural Language Interface for Uncertainty Visualization},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/chatuvisbox}
}
```

## License

MIT License - see LICENSE file

## Acknowledgments

- [UVisBox](https://github.com/uvisbox/uvisbox) - Core visualization library
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
- [Google Gemini](https://ai.google.dev/) - Natural language processing

## Contact

- Issues: https://github.com/yourusername/chatuvisbox/issues
- Email: your.email@example.com

---

Made with ❤️ for uncertainty visualization
```

### Task 10.2: Create CONTRIBUTING.md

**File**: `CONTRIBUTING.md`

```markdown
# Contributing to ChatUVisBox

Thank you for your interest in contributing!

## Development Setup

1. Fork and clone the repository
2. Set up development environment:
   ```bash
   conda create -n chatuvisbox-dev python=3.10
   conda activate chatuvisbox-dev
   pip install uvisbox
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If exists
   ```
3. Create `.env` file with your Google API key

## Making Changes

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Add tests for new functionality
4. Run test suite: `python run_all_tests.py`
5. Commit with clear messages
6. Push and create pull request

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings for public functions
- Keep functions focused and small

## Testing

All new features must include tests:

- Unit tests for individual functions
- Integration tests for workflows
- Add test cases to appropriate test file

## Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features

## Pull Request Process

1. Ensure all tests pass
2. Update documentation
3. Describe changes clearly in PR
4. Link related issues
5. Request review

## Questions?

Open an issue or reach out to maintainers.
```

### Task 10.3: Create LICENSE

**File**: `LICENSE`

```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Task 10.4: Create User Guide

**File**: `docs/USER_GUIDE.md`

```markdown
# ChatUVisBox User Guide

Complete guide to using ChatUVisBox for uncertainty visualization.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Concepts](#basic-concepts)
3. [Visualization Types](#visualization-types)
4. [Advanced Features](#advanced-features)
5. [Tips and Tricks](#tips-and-tricks)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### First Launch

1. Start ChatUVisBox:
   ```bash
   python main.py
   ```

2. You'll see the welcome screen with available commands

3. Try your first visualization:
   ```
   You: Generate 30 curves and plot functional boxplot
   ```

### Basic Commands

- `/help` - Show help
- `/context` - Show current state
- `/stats` - Show session statistics
- `/clear` - Clear session
- `/quit` - Exit

## Basic Concepts

### Conversation Flow

ChatUVisBox maintains conversation context:

```
You: Generate curves
Assistant: Generated 30 curves
You: Plot them           # "them" refers to the curves
Assistant: [shows plot]
You: Change colormap     # Updates the current plot
```

### Data State

The system tracks:
- **current_data_path**: Most recent data file
- **last_vis_params**: Last visualization parameters
- **session_files**: All files created this session

### Hybrid Control

Simple commands bypass full AI processing for speed:

- `colormap plasma` - Instant update
- `percentile 80` - Instant update
- Complex requests use full AI pipeline

## Visualization Types

### Functional Boxplot

**Purpose**: Visualize ensemble of 1D curves with band depth

**Data**: 2D array (n_curves, n_points)

**Examples**:
```
Generate 40 curves and plot functional boxplot
Show functional boxplot with percentile 95
Plot with percentile 90 and hide median
```

**Parameters**:
- `percentile`: Band depth percentile (0-100)
- `show_median`: Show/hide median curve
- `colormap`: Color scheme

### Curve Boxplot

**Purpose**: Depth-colored ensemble curves

**Data**: 3D array (n_curves, n_steps, n_dims)

**Examples**:
```
Generate curves and show curve boxplot
Plot curve boxplot with percentile 60
Use colormap plasma
```

### Probabilistic Marching Squares

**Purpose**: Uncertainty in 2D scalar field isocontours

**Data**: 3D array (nx, ny, n_ensemble)

**Examples**:
```
Generate scalar field 40x40 and show marching squares
Visualize with isovalue 0.6
Use colormap inferno
```

### Uncertainty Lobes

**Purpose**: Directional uncertainty in vector fields

**Data**: Positions (n, 2) and vectors (n, m, 2)

**Examples**:
```
Show uncertainty lobes with percentile 0.8
Use scale 0.3
```

## Advanced Features

### Multi-Step Workflows

Chain operations:
```
You: Generate scalar field 50x50
Assistant: [generates]
You: Now visualize with marching squares at isovalue 0.5
Assistant: [displays]
You: Try isovalue 0.7 instead
Assistant: [updates]
```

### Parameter Experimentation

Quick iteration:
```
You: Generate curves and plot
Assistant: [shows plot]
You: percentile 70
You: percentile 80
You: percentile 90
You: colormap plasma
```

### Loading External Data

```
You: Load mydata.csv and visualize
Assistant: Loaded data with shape (100, 50). This looks like 100 curves.
          Would you like a functional boxplot?
You: Yes please with percentile 95
```

### Session Management

Keep organized:
```
You: /stats                    # Check what you've done
You: /context                  # See current state
You: /clear                    # Start fresh when needed
```

## Tips and Tricks

### Tip 1: Use Descriptive Names

```
Good: "Load wind_ensemble.csv"
Okay: "Load data.csv"
```

### Tip 2: Be Specific When Needed

```
Specific: "Plot functional boxplot with percentile 90"
Vague: "Make it nice"
```

### Tip 3: Use Hybrid Commands for Speed

```
Fast:    "colormap plasma"
Slower:  "Change the colormap to plasma please"
```

### Tip 4: Reference Previous Operations

```
"Plot that"
"Change it to percentile 80"
"Use the same data"
```

### Tip 5: Start Simple, Then Refine

```
1. "Generate curves and plot"
2. [See result]
3. "percentile 85"
4. "colormap viridis"
5. "hide outliers"
```

## Common Workflows

### Workflow 1: Quick Exploration

```
Generate test data → Visualize → Adjust parameters → Done
```

### Workflow 2: Data Analysis

```
Load CSV → Inspect shape → Visualize → Adjust → Export/save
```

### Workflow 3: Comparison

```
Load data → Viz 1 (functional) → Viz 2 (curve) → Compare windows
```

## Troubleshooting

### Problem: Matplotlib window doesn't appear

**Solutions**:
1. Check backend: `export MPLBACKEND=TkAgg`
2. Verify not in headless environment
3. Try: `python -c "import matplotlib.pyplot as plt; plt.plot([1,2]); plt.show()"`

### Problem: "File not found" errors

**Solutions**:
1. Use `/context` to see available files
2. Check file path is correct
3. Use tab completion if in terminal

### Problem: Slow response times

**Causes**:
- Network latency to Gemini API
- Large data processing

**Solutions**:
- Use hybrid commands for param updates
- Generate smaller test data
- Check internet connection

### Problem: Agent doesn't understand request

**Solutions**:
- Be more specific
- Break into steps
- Use simpler language
- Check examples in `/help`

### Problem: Visualization looks wrong

**Solutions**:
- Check data shape with "What shape is the data?"
- Verify data range is reasonable
- Try different percentile values
- Check colormap is appropriate

## Getting Help

1. `/help` - In-app help
2. README.md - Quick reference
3. GitHub Issues - Report bugs
4. Email - Direct support

## Best Practices

✅ **Do**:
- Start sessions with `/help` if unsure
- Use `/clear` when switching tasks
- Reference previous operations naturally
- Experiment with parameters

❌ **Don't**:
- Don't create hundreds of files without `/clear`
- Don't use very vague requests
- Don't ignore error messages
- Don't forget to check `/stats`

---

Happy visualizing! 🎨📊
```

### Task 10.5: Create API Documentation

**File**: `docs/API.md`

```markdown
# ChatUVisBox API Documentation

## Data Tools

### load_csv_to_numpy(filepath, output_path=None)

Load CSV file and convert to numpy array.

**Parameters**:
- `filepath` (str): Path to CSV file
- `output_path` (str, optional): Output .npy path

**Returns**: Dict with status, output_path, shape

### generate_ensemble_curves(n_curves=50, n_points=100, output_path=None)

Generate synthetic ensemble curves.

**Parameters**:
- `n_curves` (int): Number of curves
- `n_points` (int): Points per curve
- `output_path` (str, optional): Output path

**Returns**: Dict with status, output_path, shape

[Continue for all tools...]

## Visualization Tools

### plot_functional_boxplot(data_path, percentiles=None, colors=None, plot_all_curves=False)

Create functional boxplot visualization with multiple percentile bands.

**Parameters**:
- `data_path` (str): Path to 2D curve data (n_curves, n_points)
- `percentiles` (list): List of percentiles for bands (default: [25, 50, 90, 100])
- `colors` (list): Colors for each band (optional)
- `plot_all_curves` (bool): Plot all individual curves (default: False)

**Returns**: Dict with status, message, _viz_params

### plot_curve_boxplot(data_path, percentiles=None, colors=None)

Create curve boxplot for ensemble curves.

**Parameters**:
- `data_path` (str): Path to 3D curve data (n_curves, n_steps, n_dims)
- `percentiles` (list): List of percentiles for bands (default: [25, 50, 90, 100])
- `colors` (list): Colors for each band (optional)

**Returns**: Dict with status, message, _viz_params

### plot_probabilistic_marching_squares(data_path, isovalue=0.5, colormap="viridis")

Visualize probabilistic isocontours from scalar field ensemble.

**Parameters**:
- `data_path` (str): Path to 3D scalar field (ny, nx, n_ensemble)
- `isovalue` (float): Isovalue for contour extraction
- `colormap` (str): Matplotlib colormap name

**Returns**: Dict with status, message, _viz_params

### plot_contour_boxplot(data_path, isovalue, percentiles=None, colormap="viridis", show_median=True, show_outliers=True)

Create contour boxplot from scalar field ensemble.

**Parameters**:
- `data_path` (str): Path to 3D scalar field (ny, nx, n_ensemble)
- `isovalue` (float): Threshold for binary contour extraction
- `percentiles` (list): List of percentiles for band envelopes (default: [25, 50, 75, 90])
- `colormap` (str): Matplotlib colormap name
- `show_median` (bool): Show median contour in red
- `show_outliers` (bool): Show outlier contours in gray

**Returns**: Dict with status, message, _viz_params

### plot_uncertainty_lobes(vectors_path, positions_path, percentile1=90, percentile2=50, scale=0.2)

Create uncertainty lobe glyphs for vector ensembles.

**Parameters**:
- `vectors_path` (str): Path to ensemble vectors (n, m, 2)
- `positions_path` (str): Path to glyph positions (n, 2)
- `percentile1` (float): First percentile (0-100), should be > percentile2
- `percentile2` (float): Second percentile (0-100), should be < percentile1
- `scale` (float): Scale factor for glyph size

**Returns**: Dict with status, message, _viz_params

## State Management

### GraphState

**Fields**:
- `messages`: Conversation history
- `current_data_path`: Most recent data file
- `last_vis_params`: Last visualization parameters
- `session_files`: List of session files
- `error_count`: Consecutive errors

## Classes

### ConversationSession

Manages multi-turn conversations.

**Methods**:
- `send(user_message)`: Send message and get response
- `get_last_response()`: Get last assistant message
- `get_context_summary()`: Get state summary
- `clear()`: Clear session and files
- `reset()`: Reset conversation only

[Continue...]
```

### Task 10.6: Finalize requirements.txt

**File**: `requirements.txt`

```txt
# LLM and Orchestration
langgraph>=0.0.20
langchain>=0.1.0
langchain-google-genai>=0.0.5
google-generativeai>=0.3.0

# Data Processing
numpy>=1.24.0
pandas>=2.0.0

# Visualization
matplotlib>=3.7.0

# Note: UVisBox should be installed separately via:
# pip install uvisbox
# Note: GEMINI_API_KEY must be set in system environment
```

### Task 10.7: Create Release Checklist

**File**: `RELEASE_CHECKLIST.md`

```markdown
# Release Checklist

## Pre-Release

- [ ] All tests passing (`python run_all_tests.py`)
- [ ] Documentation complete and accurate
- [ ] README.md examples tested
- [ ] User guide reviewed
- [ ] API documentation up to date
- [ ] requirements.txt verified
- [ ] Version number updated
- [ ] CHANGELOG.md updated
- [ ] License file present

## Code Quality

- [ ] No TODO comments in main code
- [ ] All functions have docstrings
- [ ] Type hints added
- [ ] Logging configured
- [ ] Error messages are helpful
- [ ] No hardcoded paths
- [ ] API key usage documented

## Testing

- [ ] Happy path tests pass
- [ ] Error handling tests pass
- [ ] Edge cases covered
- [ ] Performance benchmarks met
- [ ] Manual user acceptance tests complete

## Documentation

- [ ] README.md complete
- [ ] USER_GUIDE.md complete
- [ ] API.md complete
- [ ] CONTRIBUTING.md present
- [ ] Examples tested
- [ ] Screenshots/GIFs added

## Distribution

- [ ] GitHub repository created
- [ ] .gitignore configured
- [ ] README displayed correctly
- [ ] Issues template created
- [ ] PR template created

## Post-Release

- [ ] Tag release version
- [ ] Create release notes
- [ ] Announce to community
- [ ] Monitor issues
- [ ] Gather feedback
```

## Validation Checklist

- [ ] README.md is comprehensive and accurate
- [ ] All code examples in docs work
- [ ] LICENSE file present
- [ ] CONTRIBUTING.md explains process
- [ ] USER_GUIDE.md is beginner-friendly
- [ ] API.md documents all public functions
- [ ] requirements.txt is complete
- [ ] Project structure documented
- [ ] Screenshots/demos included
- [ ] Contact information provided

## Deliverables

After Phase 10, you should have:

1. **README.md** - Complete project documentation
2. **USER_GUIDE.md** - Detailed user guide
3. **API.md** - API reference
4. **CONTRIBUTING.md** - Contribution guidelines
5. **LICENSE** - MIT License
6. **requirements.txt** - Finalized dependencies
7. **RELEASE_CHECKLIST.md** - Release validation
8. **CHANGELOG.md** - Version history (if applicable)

## Final Steps

1. **Review all documentation**
   - Read through as if you're a new user
   - Test all code examples
   - Fix any errors or unclear sections

2. **Document environment setup**
   - Ensure README clearly explains `GEMINI_API_KEY` requirement
   - Provide instructions for different shells (bash, zsh, fish)
   - Note that API key must be in system environment

3. **Test fresh installation**
   - Follow README.md on clean system
   - Verify all steps work
   - Note any missing information

4. **Create demo materials**
   - Record demo video
   - Create screenshots
   - Write blog post (optional)

5. **Prepare repository**
   - Create GitHub repo
   - Push code
   - Configure settings
   - Create first release

## Success Criteria

- [ ] New user can install and run following README only
- [ ] All documentation is accurate
- [ ] Examples are copy-paste ready
- [ ] Troubleshooting covers common issues
- [ ] Project is ready for public use

## Congratulations!

You've completed all 10 phases of ChatUVisBox development! 🎉

Your MVP is now ready for:
- Public release
- User testing
- Community feedback
- Future enhancements
