# Contributing to UVisBox-Assistant

Thank you for your interest in contributing to UVisBox-Assistant! This document provides guidelines for contributing to the project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code Standards](#code-standards)
4. [Testing Guidelines](#testing-guidelines)
5. [Pull Request Process](#pull-request-process)
6. [Reporting Issues](#reporting-issues)

## Getting Started

UVisBox-Assistant is a natural language interface for the UVisBox uncertainty visualization library. Before contributing, please:

1. Read the [README.md](README.md) to understand the project
2. Check [existing issues](https://github.com/yourusername/uvisbox_assistant/issues) to avoid duplicates
3. Familiarize yourself with the [testing guide](TESTING.md)

## Development Setup

### Prerequisites

- Python 3.11–3.13
- Conda environment (recommended)
- A running [Ollama](https://ollama.com/) instance with a tool-capable model pulled

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/uvisbox_assistant.git
   cd uvisbox_assistant
   ```

2. **Set up environment**:
   ```bash
   conda create -n uvisbox_assistant python=3.13
   conda activate uvisbox_assistant
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   pip install uvisbox
   ```

4. **Configure Ollama** (defaults shown — only override if needed):
   ```bash
   export OLLAMA_API_URL="http://localhost:11434"
   export OLLAMA_MODEL_NAME="qwen3-vl:8b"
   ```

5. **Run tests**:
   ```bash
   # Pre-planning: unit + uvisbox_interface (0 LLM calls)
   python tests/test.py --pre-planning
   ```

## Code Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) guidelines
- Use type hints where appropriate
- Maximum line length: 100 characters (flexible)
- Use docstrings for all public functions and classes

### File Organization

Feature-based layout:

```
src/uvisbox_assistant/
├── __init__.py             # Public API exports
├── __main__.py             # `python -m uvisbox_assistant` entry point
├── config.py               # Configuration (paths, Ollama settings)
├── main.py                 # Interactive REPL
├── core/                   # LangGraph workflow orchestration
│   ├── graph.py            # StateGraph (model, data_tool, vis_tool)
│   ├── nodes.py            # Graph node implementations
│   ├── routing.py          # Conditional routing with circuit breaker
│   └── state.py            # GraphState + state-update helpers
├── tools/
│   ├── data_tools.py       # Data loading / synthetic generation
│   └── vis_tools.py        # Visualization wrappers (matplotlib + PyVista)
├── session/
│   ├── conversation.py     # ConversationSession + error tracking
│   ├── hybrid_control.py   # Fast parameter updates without LLM
│   └── command_parser.py   # Quick-command pattern parsing
├── llm/
│   └── model.py            # Ollama model setup + system prompt
├── errors/
│   ├── error_tracking.py   # ErrorRecord
│   └── error_interpretation.py  # Context-aware error hints
└── utils/
    ├── data_loading.py     # Path resolution + safe array loading
    ├── logger.py           # File-based tool/error logging
    ├── output_control.py   # Verbose mode + session injection
    └── utils.py            # Tool-type lookup, temp file cleanup
```

### Naming Conventions

- **Functions**: `snake_case` (e.g., `plot_functional_boxplot`)
- **Classes**: `PascalCase` (e.g., `ConversationSession`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_VIS_PARAMS`)
- **Private functions**: Prefix with `_` (e.g., `_internal_helper`)

### Documentation

#### Mandatory file headers (`ABOUTME:`)

Every `.py` file in `src/` and `tests/` (including `__init__.py`) MUST start with two `ABOUTME:` comment lines, **before** the module docstring or any imports. The prefix makes the headers trivially greppable (`grep -rl ABOUTME src/`).

Format:

```python
# ABOUTME: One-line description of file purpose.
# ABOUTME: Second line with key details — main classes/functions, when to use it.
"""Existing module docstring (kept)."""
import ...
```

Rules:
- Exactly two lines. The first names the file's role; the second adds the most useful concrete detail.
- Neither line should narrate history (no "refactored from", "new", "legacy").
- The lines describe the file as it is, not as it once was.
- Empty `__init__.py` files still get the two lines (e.g., "Test package marker."), so the rule applies uniformly.

#### Function and class docstrings

- Use Google-style docstrings with `Args:` / `Returns:` sections:
  ```python
  def my_function(param1: str, param2: int) -> Dict[str, Any]:
      """
      Brief description.

      Args:
          param1: Description of param1
          param2: Description of param2

      Returns:
          Dict with status and results
      """
  ```

## Testing Guidelines

### Test Categories

UVisBox-Assistant uses a 4-category test structure (v0.3.4):

1. **Unit Tests** (`tests/unit/`):
   - 0 LLM calls
   - Fast execution (< 15 seconds)
   - Test individual functions in isolation with mocking
   - Examples: routing logic, command parsing, tool functions

2. **UVisBox Interface Tests** (`tests/uvisbox_interface/`):
   - 0 LLM calls, calls real UVisBox functions
   - Verify tool → UVisBox integration
   - Catch API structure changes and KEY_NOT_FOUND bugs
   - Examples: tool_interfaces.py, csv_loading.py

3. **LLM Integration Tests** (`tests/llm_integration/`):
   - ~40 LLM calls total
   - Test specific LLM-powered features
   - Examples: analyzer, routing, error handling, session management

4. **E2E Tests** (`tests/e2e/`):
   - ~60 LLM calls total
   - Test complete workflows from data generation to visualization
   - One file per visualization type (functional_boxplot, curve_boxplot, etc.)

### Writing Tests

**Example unit test**:
```python
def test_command_parser():
    """Test command parser for median color."""
    from uvisbox_assistant.command_parser import parse_simple_command

    cmd = parse_simple_command("median color blue")
    assert cmd is not None
    assert cmd.median_color == "blue"
```

**Example UVisBox interface test**:
```python
def test_functional_boxplot_interface():
    """Test functional boxplot calls UVisBox correctly."""
    from uvisbox_assistant.tools.vis_tools import plot_functional_boxplot

    result = plot_functional_boxplot(data_path="test_data.npy")
    assert result["status"] == "success"
    assert "figure_path" in result
```

**Example LLM integration test**:
```python
@pytest.mark.llm_subset_session
def test_session_runs_visualization():
    """Test session executes a visualization workflow."""
    from uvisbox_assistant.session.conversation import ConversationSession

    session = ConversationSession()
    session.send("Generate 30 curves and plot functional boxplot")
    stats = session.get_stats()
    assert stats["current_data"] is True
    assert stats["current_vis"] is True
```

### Running Tests

```bash
# Before feature planning - verify UVisBox interface
python tests/test.py --pre-planning

# During development - test specific feature
python tests/test.py --iterative --llm-subset=routing

# Before code review - comprehensive check
python tests/test.py --code-review --llm-subset=hybrid_control,routing

# Before merge - full acceptance
python tests/test.py --acceptance
```

### Test a Specific File

```bash
python tests/test.py tests/unit/test_config.py
python tests/test.py tests/llm_integration/test_analyzer.py::test_specific
```

### With Coverage

```bash
python tests/test.py --pre-planning --coverage
```

See [TESTING.md](TESTING.md) for comprehensive testing guide.

## Pull Request Process

### Before Submitting

1. **Run tests**:
   ```bash
   python tests/test.py --pre-planning
   ```

2. **Update documentation** if needed:
   - README.md for user-facing changes
   - docs/API.md for API changes
   - docs/USER_GUIDE.md for new features

3. **Update CHANGELOG.md**:
   - Add entry under "Unreleased" section
   - Follow [Keep a Changelog](https://keepachangelog.com/) format

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass (at minimum, unit tests)
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts with main branch

### PR Description Template

```markdown
## Description
[Brief description of changes]

## Motivation
[Why is this change needed?]

## Changes
- [Change 1]
- [Change 2]

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass (if applicable)
- [ ] Manually tested

## Documentation
- [ ] Updated README.md
- [ ] Updated docs/
- [ ] Updated CHANGELOG.md

## Breaking Changes
[List any breaking changes, or write "None"]

## Related Issues
Fixes #[issue number]
```

## Reporting Issues

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
[Clear description of the bug]

**To Reproduce**
Steps to reproduce:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected behavior**
[What you expected to happen]

**Actual behavior**
[What actually happened]

**Environment**
- Python version:
- OS:
- UVisBox-Assistant version:
- UVisBox version:

**Additional context**
[Any additional information, logs, screenshots]
```

### Feature Requests

```markdown
**Feature description**
[Clear description of the feature]

**Motivation**
[Why is this feature needed?]

**Proposed solution**
[How should this be implemented?]

**Alternatives considered**
[Other approaches you've thought about]

**Additional context**
[Any additional information]
```

## Code Review Process

1. Maintainers will review PRs within 1 week
2. Feedback will be provided via PR comments
3. Address all review comments before merging
4. At least one approval required
5. All tests must pass

## Development Workflow

### Branching Strategy

- `main` - Stable releases
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `docs/*` - Documentation updates

### Commit Messages

Follow conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding/updating tests
- `refactor`: Code refactoring
- `style`: Code style changes (formatting)
- `chore`: Maintenance tasks

**Examples**:
```
feat(vis_tools): add median styling parameters
fix(hybrid_control): correct colormap parameter routing
docs(api): update BoxplotStyleConfig documentation
test(unit): add command parser tests for outliers styling
```

## Architecture Guidelines

### Adding New Visualization Tools

1. Add function to `vis_tools.py`
2. Create tool schema for LLM
3. Include all parameters in `_vis_params`
4. Add tests (unit, integration, e2e)
5. Update documentation (API.md, USER_GUIDE.md)

### Adding Hybrid Commands

1. Add pattern to `command_parser.py`
2. Update `SimpleCommand` dataclass
3. Handle in `hybrid_control.py`
4. Add test in `tests/unit/test_command_parser.py`
5. Document in USER_GUIDE.md

### Modifying State

- State changes must go through helper functions in `state.py`
- Never modify state directly in nodes
- Preserve all required fields
- Test state updates thoroughly

## Questions?

- Open an issue for questions
- Review [docs/](docs/) for API and user guides
- Check [TESTING.md](TESTING.md) for testing guidelines

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to UVisBox-Assistant!
