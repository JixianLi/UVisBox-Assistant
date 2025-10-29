# Phase 4.5: Codebase Restructure to Python Package

**Goal**: Transform the flat file structure into a professional Python package using Poetry for dependency management and packaging, while maintaining Conda for environment management.

**Duration**: 1-2 days

**Priority**: HIGH - Better to establish proper structure now with ~10 files than later with 20+ files

---

## Prerequisites

- Phase 4 completed (all tests working)
- UVisBox API adjustments completed (if any)
- All tests passing in current structure
- Familiarity with Poetry basics (or willingness to learn)

---

## Rationale

### Why Now?

1. **Natural Milestone Boundary**: Just completed Milestone 1 (core pipeline)
2. **Small Codebase**: Only ~10 Python files to restructure (cheapest time to do it)
3. **Test Coverage**: Full test suite exists to validate restructuring
4. **Before Complexity**: Phase 5-7 will add ~10 more files (error handling, conversation, hybrid control)
5. **Professional Foundation**: Proper imports and package structure for all future development

### Why Poetry + Conda?

**Conda** (`environment.yml`):
- System-level dependencies
- Python version management
- UVisBox installation (scientific computing stack)
- Cross-platform environment reproducibility

**Poetry** (`pyproject.toml`):
- Python package management
- Dependency resolution and locking
- Build system (wheel/sdist creation)
- Development dependencies separation
- Future PyPI publishing

This hybrid approach is **best practice** for scientific Python projects with compiled dependencies.

---

## Target Structure

```
chatuvisbox/                        # Project root
├── pyproject.toml                  # Poetry: package metadata, dependencies
├── poetry.lock                     # Poetry: locked dependencies (generated)
├── environment.yml                 # Conda: environment specification
├── README.md                       # User-facing documentation
├── CLAUDE.md                       # Development guidance
├── .gitignore                      # Git ignore rules
│
├── src/                            # Source code (src layout)
│   └── chatuvisbox/                # Main package
│       ├── __init__.py             # Package initialization, version
│       ├── __main__.py             # Entry point: python -m chatuvisbox
│       ├── graph.py                # LangGraph workflow
│       ├── state.py                # GraphState definition
│       ├── nodes.py                # Graph nodes
│       ├── routing.py              # Routing logic
│       ├── model.py                # LLM setup
│       ├── data_tools.py           # Data tool functions
│       ├── vis_tools.py            # Visualization tool functions
│       ├── config.py               # Configuration
│       └── utils.py                # Utility functions
│
├── tests/                          # Test suite (pytest discovery)
│   ├── __init__.py                 # Test package marker
│   ├── conftest.py                 # Pytest fixtures (NEW)
│   ├── test_phase1.py              # Phase 1 tests
│   ├── test_phase2.py              # Phase 2 tests
│   ├── test_routing.py             # Routing tests
│   ├── test_graph.py               # Graph tests
│   ├── test_graph_quick.py         # Quick integration tests
│   ├── test_graph_integration.py   # Integration tests
│   ├── test_happy_path.py          # Happy path tests
│   ├── test_matplotlib_behavior.py # Matplotlib tests
│   └── interactive_test.py         # Interactive manual test
│
├── test_data/                      # Test data files
│   └── sample_curves.csv
│
├── temp/                           # Temporary files (gitignored)
│   └── .gitkeep
│
├── plans/                          # Implementation plans
│   ├── README.md
│   ├── phase_*.md
│   └── ...
│
└── docs/                           # Documentation (Phase 10)
    └── (future)
```

---

## Tasks

### Task 4.5.1: Create Poetry Project Structure

**Step 1**: Initialize Poetry in project root

```bash
cd /path/to/chatuvisbox

# Initialize Poetry (interactive)
poetry init

# Or create pyproject.toml manually (see below)
```

**Step 2**: Create `pyproject.toml`

```toml
[tool.poetry]
name = "chatuvisbox"
version = "0.1.0"
description = "Natural language interface for UVisBox uncertainty visualization"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"
license = "MIT"  # Or your preferred license
packages = [{include = "chatuvisbox", from = "src"}]

[tool.poetry.dependencies]
python = "^3.10"
langchain-google-genai = "^2.0.4"
langgraph = "^0.2.53"
numpy = "^1.26.0"
matplotlib = "^3.8.0"
pandas = "^2.2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-cov = "^4.1.0"
black = "^24.0.0"
ruff = "^0.3.0"
ipython = "^8.20.0"

[tool.poetry.scripts]
chatuvisbox = "chatuvisbox.__main__:main"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
]

[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
target-version = "py310"
select = ["E", "F", "I", "W"]
ignore = ["E501"]  # Line too long (handled by black)
```

**Step 3**: Create `environment.yml` for Conda

```yaml
name: chatuvisbox
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy>=1.26.0
  - matplotlib>=3.8.0
  - pandas>=2.2.0
  # UVisBox and its dependencies
  - pip
  - pip:
      - uvisbox>=0.1.0  # Adjust version as needed
      - langchain-google-genai>=2.0.4
      - langgraph>=0.2.53
```

**Alternative**: Keep UVisBox in pip section if not on conda-forge.

---

### Task 4.5.2: Create Directory Structure

**Step 1**: Create directories

```bash
# From project root
mkdir -p src/chatuvisbox
mkdir -p tests
mkdir -p docs
mkdir -p temp
```

**Step 2**: Create package markers

**File**: `src/chatuvisbox/__init__.py`

```python
"""
ChatUVisBox: Natural language interface for UVisBox uncertainty visualization.

A LangGraph-based conversational agent that translates natural language requests
into data processing and visualization operations using the UVisBox library.
"""

__version__ = "0.1.0"

# Expose main API
from .graph import run_graph, stream_graph, graph_app
from .state import GraphState

__all__ = [
    "run_graph",
    "stream_graph",
    "graph_app",
    "GraphState",
    "__version__",
]
```

**File**: `tests/__init__.py`

```python
"""Test suite for ChatUVisBox."""
```

**File**: `tests/conftest.py`

```python
"""Pytest fixtures and configuration for ChatUVisBox tests."""

import pytest
from pathlib import Path
import matplotlib.pyplot as plt


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Return the test data directory."""
    return project_root / "test_data"


@pytest.fixture(autouse=True)
def cleanup_matplotlib():
    """Clean up matplotlib figures after each test."""
    yield
    plt.close("all")


@pytest.fixture
def temp_dir(project_root):
    """Return the temp directory."""
    return project_root / "temp"
```

---

### Task 4.5.3: Move Source Files

**Step 1**: Move core files to `src/chatuvisbox/`

```bash
# From project root
mv graph.py src/chatuvisbox/
mv state.py src/chatuvisbox/
mv nodes.py src/chatuvisbox/
mv routing.py src/chatuvisbox/
mv model.py src/chatuvisbox/
mv data_tools.py src/chatuvisbox/
mv vis_tools.py src/chatuvisbox/
mv config.py src/chatuvisbox/
mv utils.py src/chatuvisbox/
```

**Step 2**: Update imports in moved files

Change all relative imports to package imports:

**Before** (in flat structure):
```python
from state import GraphState
from model import MODEL
from data_tools import DATA_TOOL_FUNCTIONS
```

**After** (in package structure):
```python
from chatuvisbox.state import GraphState
from chatuvisbox.model import MODEL
from chatuvisbox.data_tools import DATA_TOOL_FUNCTIONS
```

**Files to update**:
- `src/chatuvisbox/graph.py` - imports state, nodes, routing
- `src/chatuvisbox/nodes.py` - imports model, data_tools, vis_tools, state, routing
- `src/chatuvisbox/routing.py` - imports state
- `src/chatuvisbox/model.py` - imports config, data_tools, vis_tools
- `src/chatuvisbox/data_tools.py` - imports config
- `src/chatuvisbox/vis_tools.py` - imports config
- `src/chatuvisbox/utils.py` - imports config (if needed)

---

### Task 4.5.4: Move Test Files

**Step 1**: Move test files to `tests/`

```bash
# From project root
mv test_phase1.py tests/
mv test_phase2.py tests/
mv test_routing.py tests/
mv test_graph.py tests/
mv test_graph_quick.py tests/
mv test_graph_integration.py tests/
mv test_happy_path.py tests/
mv test_matplotlib_behavior.py tests/
mv interactive_test.py tests/
mv simple_test.py tests/  # If it exists
mv run_tests_with_delays.py tests/
```

**Step 2**: Update imports in test files

**Before**:
```python
from graph import run_graph, stream_graph
from data_tools import generate_ensemble_curves
from vis_tools import plot_functional_boxplot
```

**After**:
```python
from chatuvisbox.graph import run_graph, stream_graph
from chatuvisbox.data_tools import generate_ensemble_curves
from chatuvisbox.vis_tools import plot_functional_boxplot
```

**Files to update**: All test files in `tests/`

**Step 3**: Remove `sys.path.insert()` hacks

Many test files have this at the top:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

**Delete these lines** - no longer needed with proper package structure.

---

### Task 4.5.5: Create Package Entry Point

**File**: `src/chatuvisbox/__main__.py`

```python
"""
Entry point for running ChatUVisBox as a module.

Usage:
    python -m chatuvisbox
"""

import sys


def main():
    """Main entry point for ChatUVisBox."""
    print("ChatUVisBox v0.1.0")
    print("Natural language interface for UVisBox")
    print()
    print("This is a placeholder for the main REPL (Phase 8).")
    print("For now, use the test scripts:")
    print("  - tests/interactive_test.py")
    print("  - tests/test_happy_path.py")
    print()
    print("To run the interactive test:")
    print("  python -m pytest tests/interactive_test.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Note**: Full REPL implementation comes in Phase 8. This is just a placeholder.

---

### Task 4.5.6: Update Configuration

**File**: `src/chatuvisbox/config.py`

Update path references to work from installed package:

```python
"""
Configuration for ChatUVisBox.
"""

import os
from pathlib import Path

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in environment. "
        "Please set it in your system environment:\n"
        "  export GEMINI_API_KEY='your-key-here'"
    )

# Model Configuration
MODEL_NAME = "gemini-2.0-flash-lite"  # 30 RPM (vs flash: 15 RPM)
TEMPERATURE = 0.0

# Directory Configuration
# Use package root (one level up from src/chatuvisbox/)
PACKAGE_ROOT = Path(__file__).parent.parent.parent
PROJECT_ROOT = PACKAGE_ROOT  # For compatibility

TEMP_DIR = PROJECT_ROOT / "temp"
TEST_DATA_DIR = PROJECT_ROOT / "test_data"

# Ensure directories exist
TEMP_DIR.mkdir(exist_ok=True)
TEST_DATA_DIR.mkdir(exist_ok=True)

# File Naming
TEMP_FILE_PREFIX = "_temp_"

# Visualization Defaults
DEFAULT_PERCENTILES = [25, 50, 90, 100]
DEFAULT_COLORS = None  # Let UVisBox choose
DEFAULT_FIGSIZE = (10, 8)
DEFAULT_DPI = 100

# Error Handling (Phase 5)
MAX_ERROR_COUNT = 3
ERROR_RETRY_DELAY = 1.0  # seconds
```

---

### Task 4.5.7: Install Package in Development Mode

**Step 1**: Recreate conda environment (optional but recommended)

```bash
# Deactivate current env
conda deactivate

# Remove old env (optional)
conda env remove -n agent

# Create new env from environment.yml
conda env create -f environment.yml

# Activate
conda activate chatuvisbox
```

**Step 2**: Install Poetry dependencies

```bash
# Install all dependencies including dev
poetry install

# This installs the package in editable mode with all dependencies
```

**Step 3**: Verify installation

```bash
# Check package is installed
poetry run python -c "import chatuvisbox; print(chatuvisbox.__version__)"

# Should output: 0.1.0

# Test import paths
poetry run python -c "from chatuvisbox import run_graph; print('✅ Imports working')"
```

---

### Task 4.5.8: Update .gitignore

Add Poetry and package-specific patterns:

```gitignore
# Existing rules...

# Poetry
poetry.lock
dist/
*.egg-info/
.eggs/
build/

# Package build artifacts
src/*.egg-info/
*.whl

# Virtual environments (if not using conda)
.venv/
venv/

# Pytest cache
.pytest_cache/
.coverage
htmlcov/
*.cover

# Ruff cache
.ruff_cache/
```

**Note**: Some developers commit `poetry.lock` for reproducibility. Your choice.

---

### Task 4.5.9: Validate with Tests

**Step 1**: Run pytest with proper discovery

```bash
# Run all tests with pytest
poetry run pytest tests/ -v

# Or specific test files
poetry run pytest tests/test_phase1.py -v
poetry run pytest tests/test_graph_quick.py -v
```

**Step 2**: Run quick integration test

```bash
# This should work with new package structure
poetry run python tests/test_graph_quick.py
```

**Step 3**: Run matplotlib behavior test (0 API calls)

```bash
poetry run python tests/test_matplotlib_behavior.py
```

**Step 4**: (Optional) Run full happy path test

```bash
# 25-35 API calls - only if you have quota
poetry run python tests/test_happy_path.py
```

---

### Task 4.5.10: Update Documentation

**Update**: `CLAUDE.md`

Add section on package structure and installation:

```markdown
## Installation

### For Development

1. **Clone repository**
   ```bash
   git clone <repo-url>
   cd chatuvisbox
   ```

2. **Create conda environment**
   ```bash
   conda env create -f environment.yml
   conda activate chatuvisbox
   ```

3. **Install with Poetry**
   ```bash
   poetry install
   ```

4. **Verify installation**
   ```bash
   poetry run python -c "import chatuvisbox; print(chatuvisbox.__version__)"
   ```

### For Users (Future)

```bash
pip install chatuvisbox
```

## Package Structure

The project follows the `src` layout pattern:

```
src/chatuvisbox/     # Main package code
tests/               # Test suite
test_data/           # Sample data files
temp/                # Generated files (gitignored)
plans/               # Implementation guides
```

All imports should use absolute paths:
```python
from chatuvisbox.graph import run_graph
from chatuvisbox.state import GraphState
```

## Running Tests

```bash
# All tests
poetry run pytest tests/ -v

# Specific test
poetry run pytest tests/test_graph_quick.py -v

# Interactive test
poetry run python tests/interactive_test.py
```
```

**Update**: `plans/README.md`

Add Phase 4.5 to the milestone table:

```markdown
### Milestone 1: Core Pipeline (Phases 1-4.5) ✅ COMPLETE

| Phase | Document | Focus | Duration | Status |
|-------|----------|-------|----------|--------|
| **Phase 1** ✅ | [Schemas & Dispatchers](phase_01_schemas_and_dispatchers.md) | Data/vis tools | 1-2 days | Complete |
| **Phase 2** ✅ | [State & Nodes](phase_02_langgraph_state_and_nodes.md) | State and nodes | 1 day | Complete |
| **Phase 3** ✅ | [Graph Wiring](phase_03_graph_wiring_and_routing.md) | Graph assembly | 0.5-1 day | Complete |
| **Phase 4** ✅ | [End-to-End Test](phase_04_end_to_end_test.md) | Happy path | 0.5 day | Complete |
| **Phase 4.5** ✅ | [Codebase Restructure](phase_04.5_codebase_restructure.md) | Package structure | 1-2 days | Complete |
```

---

## Validation Checklist

### Structure
- [ ] `src/chatuvisbox/` directory exists with all source files
- [ ] `tests/` directory exists with all test files
- [ ] `pyproject.toml` created with correct dependencies
- [ ] `environment.yml` created for conda
- [ ] `src/chatuvisbox/__init__.py` exists with version and exports
- [ ] `src/chatuvisbox/__main__.py` exists as entry point
- [ ] `tests/conftest.py` exists with pytest fixtures

### Imports
- [ ] All source files use `from chatuvisbox.X import Y` syntax
- [ ] All test files use `from chatuvisbox.X import Y` syntax
- [ ] No `sys.path.insert()` hacks remain in test files
- [ ] Circular imports resolved (if any)

### Installation
- [ ] `poetry install` completes without errors
- [ ] `poetry run python -c "import chatuvisbox"` works
- [ ] Package version accessible: `chatuvisbox.__version__`
- [ ] Entry point works: `poetry run python -m chatuvisbox`

### Tests
- [ ] `pytest tests/` runs and discovers all tests
- [ ] `test_phase1.py` passes
- [ ] `test_phase2.py` passes
- [ ] `test_routing.py` passes
- [ ] `test_graph.py` passes
- [ ] `test_graph_quick.py` passes (6-10 API calls)
- [ ] `test_matplotlib_behavior.py` passes (0 API calls)
- [ ] All imports resolve correctly in tests

### Configuration
- [ ] `TEMP_DIR` and `TEST_DATA_DIR` paths work from package
- [ ] Temp files still generated in correct location
- [ ] Test data files accessible

### Documentation
- [ ] `CLAUDE.md` updated with package structure
- [ ] `plans/README.md` updated with Phase 4.5
- [ ] `.gitignore` updated for Poetry artifacts
- [ ] Import examples in docs updated

---

## Common Issues & Solutions

### Issue 1: Import Errors After Restructuring

**Symptom**: `ModuleNotFoundError: No module named 'chatuvisbox'`

**Solution**:
```bash
# Ensure package is installed in editable mode
poetry install

# Verify PYTHONPATH
poetry run python -c "import sys; print(sys.path)"
```

### Issue 2: Tests Can't Find Test Data

**Symptom**: `FileNotFoundError: test_data/sample_curves.csv`

**Solution**: Update `config.py` to use proper path resolution:
```python
PROJECT_ROOT = Path(__file__).parent.parent.parent
TEST_DATA_DIR = PROJECT_ROOT / "test_data"
```

Or use pytest fixtures from `conftest.py`:
```python
def test_something(test_data_dir):
    data_file = test_data_dir / "sample_curves.csv"
```

### Issue 3: Circular Import

**Symptom**: `ImportError: cannot import name 'X' from partially initialized module`

**Solution**: Review import order. Common circular import:
```python
# Bad: nodes.py imports graph.py, graph.py imports nodes.py
# Fix: Use TYPE_CHECKING for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chatuvisbox.graph import GraphApp
```

### Issue 4: Poetry vs Conda Conflicts

**Symptom**: Dependency resolution conflicts between Poetry and Conda

**Solution**:
- Install scientific/compiled deps with Conda (numpy, matplotlib, UVisBox)
- Install pure Python deps with Poetry (langchain, langgraph)
- Run `poetry install --sync` to synchronize

### Issue 5: Temp Files in Wrong Location

**Symptom**: Files created in `src/chatuvisbox/temp/` instead of `temp/`

**Solution**: Fix `config.py` path calculation:
```python
# Correct: Go up to project root
PACKAGE_ROOT = Path(__file__).parent.parent.parent
TEMP_DIR = PACKAGE_ROOT / "temp"
```

---

## Expected Behavior After Restructuring

### Imports Work Everywhere

```python
# From any test file
from chatuvisbox.graph import run_graph
from chatuvisbox.state import GraphState
from chatuvisbox import __version__

# ✅ All work regardless of where you run from
```

### Tests Run with Pytest

```bash
# Auto-discovery works
pytest

# Specific tests
pytest tests/test_phase1.py -v

# Pattern matching
pytest -k "test_functional_boxplot"
```

### Package is Installable

```bash
# Build distribution
poetry build

# Creates dist/chatuvisbox-0.1.0-py3-none-any.whl
# Ready for: pip install dist/chatuvisbox-0.1.0-py3-none-any.whl
```

### Development Workflow

```bash
# Edit code in src/chatuvisbox/
vim src/chatuvisbox/graph.py

# Run tests (changes reflected immediately - editable install)
poetry run pytest tests/test_graph.py

# No need to reinstall after code changes
```

---

## Output

After Phase 4.5, you should have:

- ✅ Professional Python package structure (`src` layout)
- ✅ Poetry for dependency management and locking
- ✅ Conda for environment + scientific dependencies
- ✅ Pytest-based test discovery and execution
- ✅ All imports using absolute package paths
- ✅ Clean separation: source, tests, data, docs
- ✅ Installable package (`poetry install`)
- ✅ Entry point (`python -m chatuvisbox`)
- ✅ All Phase 1-4 tests still passing

---

## Next Phase

**Phase 5**: Error Handling and Circuit Breaker

With proper package structure in place, you can now build error handling on a solid foundation with clean imports and professional organization.

---

## Time Estimate

- **Task 4.5.1-4.5.2** (Setup): 30 min
- **Task 4.5.3-4.5.4** (Move files): 1 hour
- **Task 4.5.5-4.5.6** (Entry point, config): 30 min
- **Task 4.5.7** (Install): 15 min
- **Task 4.5.8-4.5.9** (Validate): 1-2 hours
- **Task 4.5.10** (Documentation): 30 min

**Total**: 4-5 hours of focused work, spread across 1-2 days with testing breaks.

---

## Tips

1. **Commit before restructuring** - Easy rollback if needed
2. **Test incrementally** - Don't move everything at once
3. **Use git mv** - Preserves file history: `git mv graph.py src/chatuvisbox/graph.py`
4. **Verify imports** - Use IDE's "find usages" to catch all import references
5. **Keep test_data and temp at root** - Easier to manage, clear purpose
6. **Document the change** - Update CLAUDE.md as you go
7. **Run tests frequently** - Catch issues early

---

**This restructuring sets the foundation for professional, maintainable code through Phase 10 and beyond.**
