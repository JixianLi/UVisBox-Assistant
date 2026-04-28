# Environment Setup for UVisBox-Assistant

This document explains how to configure the local LLM and set up your development environment for UVisBox-Assistant.

## Prerequisites

- Python 3.11–3.13
- Conda (recommended) or venv
- A running [Ollama](https://ollama.com/) instance with a tool-capable model pulled

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

### Using Conda (Recommended)

```bash
# Create environment
conda create -n uvisbox_assistant python=3.13
conda activate uvisbox_assistant

# Install dependencies
poetry install
pip install uvisbox

# Verify installation
python -c "import uvisbox_assistant; print('UVisBox-Assistant ready!')"
```

### Using venv

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

poetry install
pip install uvisbox

python -c "import uvisbox_assistant; print('UVisBox-Assistant ready!')"
```

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
1. Verify the Python environment is activated
2. Install UVisBox: `pip install uvisbox`
3. Check installation: `python -c "import uvisbox; print(uvisbox.__version__)"`

### Problem: Python version incompatible

**Solution**:
1. Check your Python version: `python --version`
2. UVisBox-Assistant requires Python 3.11–3.13
3. Create a new environment with the correct version:
   ```bash
   conda create -n uvisbox_assistant python=3.13
   ```

## Complete Setup Example

```bash
# 1. Pull a tool-capable Ollama model
ollama pull qwen3-vl:8b

# 2. Create and activate the Python environment
conda create -n uvisbox_assistant python=3.13
conda activate uvisbox_assistant

# 3. Install dependencies
poetry install
pip install uvisbox

# 4. Verify installation
python -c "import uvisbox_assistant; print('Ready!')"

# 5. Run UVisBox-Assistant
python main.py
```

## Next Steps

After completing the environment setup:

1. **Read the User Guide**: `docs/USER_GUIDE.md` for usage examples
2. **Check the API Reference**: `docs/API.md` for complete documentation
3. **Run tests**: `python tests/test.py --pre-planning` for quick validation
4. **Start the REPL**: `python main.py` to begin using UVisBox-Assistant

## Additional Resources

- **README.md** - Project overview and features
- **TESTING.md** - Testing strategies and guidelines
- **CONTRIBUTING.md** - Contribution guidelines and development setup
