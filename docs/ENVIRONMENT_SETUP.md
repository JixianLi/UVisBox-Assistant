# Environment Setup for UVisBox-Assistant

This document explains how to configure the local LLM and set up your development environment for UVisBox-Assistant.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (manages the Python interpreter and the virtual environment)
- A running [Ollama](https://ollama.com/) instance with a tool-capable model pulled

uv reads the pinned interpreter from `.python-version` (3.13) and installs it automatically if it is missing — you do not need a separate Python install or Conda.

## LLM Configuration

UVisBox-Assistant talks to a local Ollama server. Connection settings are read from environment variables — defaults are provided so most users don't need to set anything.

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `OLLAMA_API_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL_NAME` | `qwen3-vl:8b` | Model identifier (must support tool calling) |

### Pulling a Model

```bash
ollama pull qwen3-vl:8b
```

You can substitute any tool-capable Ollama model. If you do, set `OLLAMA_MODEL_NAME` accordingly.

### Setting the Environment Variables

Only set these if you need to override the defaults (e.g. when Ollama runs on another host or you want a different model).

#### Temporary (current session)

```bash
export OLLAMA_API_URL="http://my-ollama-host:11434"
export OLLAMA_MODEL_NAME="qwen3-vl:30b-a3b-instruct-q8_0"
```

#### Permanent

Add the same `export` lines to your shell config (`~/.bashrc`, `~/.zshrc`, `~/.config/fish/config.fish`, etc.) and reload the shell.

### Verifying the Setup

```bash
# Confirm Ollama responds
curl "$OLLAMA_API_URL/api/tags" | head

# Confirm the configured model is available
ollama list | grep "$OLLAMA_MODEL_NAME"
```

## Python Environment Setup

Dependencies are managed with [uv](https://docs.astral.sh/uv/). UVisBox is consumed
from the `external/UVisBox` git submodule as an editable path dependency (see
`[tool.uv.sources]` in `pyproject.toml`), so make sure the submodules are checked out
before syncing.

```bash
# Fetch submodules (UVisBox + webuvisbox) if you haven't already
git submodule update --init --recursive

# Create the virtual environment and install everything (incl. editable UVisBox)
uv sync

# Verify installation
uv run python -c "import uvisbox_assistant; print('UVisBox-Assistant ready!')"
```

`uv sync` creates `.venv/` and installs the locked dependency set from `uv.lock`.
Run project commands with `uv run <cmd>` (no manual activation needed), or activate the
environment once with `source .venv/bin/activate` if you prefer bare `python`.

## Troubleshooting

### Problem: Connection refused / cannot reach Ollama

**Solution**:
1. Verify Ollama is running: `ollama list`
2. Check `OLLAMA_API_URL` points at the right host/port
3. If running on another machine, ensure that host is reachable from this one

### Problem: Model not found

**Solution**:
1. Pull the model: `ollama pull <model-name>`
2. Confirm `OLLAMA_MODEL_NAME` matches an entry in `ollama list`
3. Make sure the model supports tool calling — non-tool models will fail to bind tools

### Problem: UVisBox import fails

**Solution**:
1. Confirm the submodule is checked out: `ls external/UVisBox/uvisbox`
   (if empty, run `git submodule update --init --recursive`)
2. Re-sync the environment: `uv sync`
3. Check installation: `uv run python -c "import uvisbox; print(uvisbox.__version__)"`

### Problem: Python version incompatible

**Solution**:
1. The interpreter is pinned to 3.13 in `.python-version`; uv installs it on `uv sync`
2. Check the environment's Python: `uv run python --version`
3. If it is wrong, recreate the environment: `rm -rf .venv && uv sync`

## Complete Setup Example

```bash
# 1. Pull a tool-capable Ollama model
ollama pull qwen3-vl:8b

# 2. Fetch submodules
git submodule update --init --recursive

# 3. Create the environment and install dependencies
uv sync

# 4. Verify installation
uv run python -c "import uvisbox_assistant; print('Ready!')"

# 5. Run UVisBox-Assistant
uv run python main.py
```

## Next Steps

After completing the environment setup:

1. **Read the User Guide**: `docs/USER_GUIDE.md` for usage examples
2. **Check the API Reference**: `docs/API.md` for complete documentation
3. **Run tests**: `uv run python tests/test.py --pre-planning` for quick validation
4. **Start the REPL**: `uv run python main.py` to begin using UVisBox-Assistant

## Additional Resources

- **README.md** - Project overview and features
- **TESTING.md** - Testing strategies and guidelines
- **CONTRIBUTING.md** - Contribution guidelines and development setup
