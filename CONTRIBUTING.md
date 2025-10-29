# Contributing to ChatUVisBox

Thank you for your interest in contributing to ChatUVisBox! This document provides guidelines for contributing to the project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code Standards](#code-standards)
4. [Testing Guidelines](#testing-guidelines)
5. [Pull Request Process](#pull-request-process)
6. [Reporting Issues](#reporting-issues)

## Getting Started

ChatUVisBox is a natural language interface for the UVisBox uncertainty visualization library. Before contributing, please:

1. Read the [README.md](README.md) to understand the project
2. Review [CLAUDE.md](CLAUDE.md) for implementation details
3. Check [existing issues](https://github.com/yourusername/chatuvisbox/issues) to avoid duplicates
4. Familiarize yourself with the [testing guide](TESTING.md)

## Development Setup

### Prerequisites

- Python 3.10-3.13
- Conda environment (recommended)
- Google Gemini API key (for testing)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/chatuvisbox.git
   cd chatuvisbox
   ```

2. **Set up environment**:
   ```bash
   conda create -n chatuvisbox python=3.13
   conda activate chatuvisbox
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install uvisbox
   ```

4. **Set environment variable**:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

5. **Run tests**:
   ```bash
   # Unit tests (0 API calls, fast)
   python tests/utils/run_all_tests.py --unit
   ```

## Code Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) guidelines
- Use type hints where appropriate
- Maximum line length: 100 characters (flexible)
- Use docstrings for all public functions and classes

### File Organization

```
src/chatuvisbox/
├── graph.py          # LangGraph workflow
├── state.py          # State definitions
├── nodes.py          # Graph nodes
├── routing.py        # Routing logic
├── model.py          # LLM setup
├── data_tools.py     # Data generation/loading
├── vis_tools.py      # Visualization wrappers
├── hybrid_control.py # Fast parameter updates
├── command_parser.py # Command parsing
├── conversation.py   # Session management
├── config.py         # Configuration
└── utils.py          # Utilities
```

### Naming Conventions

- **Functions**: `snake_case` (e.g., `plot_functional_boxplot`)
- **Classes**: `PascalCase` (e.g., `ConversationSession`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_VIS_PARAMS`)
- **Private functions**: Prefix with `_` (e.g., `_internal_helper`)

### Documentation

- Use docstrings with parameter descriptions:
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

ChatUVisBox uses a category-based test structure:

1. **Unit Tests** (`tests/unit/`):
   - 0 API calls
   - Fast execution (< 15 seconds)
   - Test individual functions in isolation
   - No LLM dependencies

2. **Integration Tests** (`tests/integration/`):
   - 15-25 API calls per file
   - Test component interactions
   - Verify workflow execution
   - Include error handling tests

3. **E2E Tests** (`tests/e2e/`):
   - 20-30 API calls per file
   - Test complete scenarios
   - Verify end-to-end functionality

4. **Interactive Tests** (`tests/interactive/`):
   - User-paced testing
   - Manual verification
   - Menu-driven exploration

### Writing Tests

**Example unit test**:
```python
def test_command_parser():
    """Test command parser for median color."""
    from chatuvisbox.command_parser import parse_simple_command

    cmd = parse_simple_command("median color blue")
    assert cmd is not None
    assert cmd.median_color == "blue"
```

**Example integration test**:
```python
def test_hybrid_control():
    """Test hybrid control for fast parameter updates."""
    from chatuvisbox.conversation import ConversationSession

    session = ConversationSession()
    # Generate data
    state = session.send("Generate 30 curves and plot")
    # Update parameter
    state = session.send("median color blue")
    # Verify update
    assert "median_color" in state["last_vis_params"]
    assert state["last_vis_params"]["median_color"] == "blue"
```

### Running Tests

```bash
# Unit tests only (fast, 0 API calls)
python tests/utils/run_all_tests.py --unit

# Integration tests (moderate API usage)
python tests/utils/run_all_tests.py --integration

# E2E tests (higher API usage)
python tests/utils/run_all_tests.py --e2e

# All tests
python tests/utils/run_all_tests.py
```

### Rate Limit Considerations

- Gemini free tier: 30 requests per minute
- Tests include automatic delays
- See [RATE_LIMIT_FRIENDLY_TESTING.md](RATE_LIMIT_FRIENDLY_TESTING.md) for details

## Pull Request Process

### Before Submitting

1. **Run tests**:
   ```bash
   python tests/utils/run_all_tests.py --unit
   ```

2. **Update documentation** if needed:
   - README.md for user-facing changes
   - CLAUDE.md for implementation changes
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
- ChatUVisBox version:
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
- Check [CLAUDE.md](CLAUDE.md) for implementation details
- Review [docs/](docs/) for API and user guides

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to ChatUVisBox!
