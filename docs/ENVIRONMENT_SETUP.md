# Environment Setup for UVisBox-Assistant

This document explains how to configure the required environment variables and set up your development environment for UVisBox-Assistant.

## Prerequisites

- Python 3.10-3.13
- Conda (recommended) or venv
- Google Gemini API key

## API Key Configuration

UVisBox-Assistant requires the Google Gemini API key to be set in your **system environment** (not in a `.env` file).

### Required Environment Variable

```bash
GEMINI_API_KEY=your_api_key_here
```

### Getting Your API Key

1. Visit [Google AI Studio](https://ai.google.dev/)
2. Sign in with your Google account
3. Navigate to "Get API Key"
4. Create a new API key or use an existing one

### Setting the Environment Variable

The API key must be available to your shell session. Choose the method that works for your setup:

#### Option 1: Temporary (Current Session Only)

```bash
export GEMINI_API_KEY="your_api_key_here"
```

This will only work for the current terminal session.

#### Option 2: Permanent (Recommended)

Add the export command to your shell configuration file:

**For Bash** (~/.bashrc or ~/.bash_profile):
```bash
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

**For Zsh** (~/.zshrc):
```bash
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

**For Fish** (~/.config/fish/config.fish):
```bash
echo 'set -x GEMINI_API_KEY "your_api_key_here"' >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

#### Option 3: System-Wide (macOS/Linux)

Add to `/etc/environment` (requires sudo):
```bash
sudo sh -c 'echo "GEMINI_API_KEY=your_api_key_here" >> /etc/environment'
```

Then log out and log back in.

### Verifying the Setup

Check that the environment variable is set correctly:

```bash
echo $GEMINI_API_KEY
```

You should see your API key printed to the terminal.

## Python Environment Setup

### Using Conda (Recommended)

```bash
# Create environment
conda create -n uvisbox_assistant python=3.13
conda activate uvisbox_assistant

# Install dependencies
pip install -r requirements.txt
pip install uvisbox

# Verify installation
python -c "import uvisbox_assistant; print('UVisBox-Assistant ready!')"
```

### Using venv

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install uvisbox

# Verify installation
python -c "import uvisbox_assistant; print('UVisBox-Assistant ready!')"
```

### Using the Setup Script

UVisBox-Assistant includes an automated setup script:

```bash
# Default: creates/uses 'uvisbox_assistant' environment
./setup_env.sh

# Or specify custom environment name
./setup_env.sh my_env_name
```

The script will:
- ✅ Check for conda installation
- ✅ Verify Python version (3.10-3.13)
- ✅ Check GEMINI_API_KEY is set
- ✅ Install all dependencies
- ✅ Verify UVisBox installation
- ✅ Create necessary directories (test_data/, temp/, logs/)

## Security Notes

1. **Never commit API keys to version control**
2. The key is stored in your shell configuration files, which should have restricted permissions:
   ```bash
   chmod 600 ~/.bashrc  # or ~/.zshrc, etc.
   ```
3. Consider using a secrets manager for production deployments
4. Rotate your API key periodically
5. Monitor your API usage at [Google Cloud Console](https://console.cloud.google.com/)

## Troubleshooting

### Problem: `GEMINI_API_KEY not found in environment`

**Solution**:
1. Verify you set the variable: `echo $GEMINI_API_KEY`
2. Check you're using the correct shell (bash vs zsh)
3. Ensure you sourced your config file after editing
4. Try setting it temporarily first: `export GEMINI_API_KEY="..."`

### Problem: API key works in terminal but not in UVisBox-Assistant

**Solution**:
1. Restart your terminal after adding to config file
2. Make sure conda environment is activated: `conda activate uvisbox_assistant`
3. Check Python can access it:
   ```python
   import os
   print(os.getenv("GEMINI_API_KEY"))
   ```

### Problem: UVisBox import fails

**Solution**:
1. Verify conda environment is activated
2. Install UVisBox: `pip install uvisbox`
3. Check installation: `python -c "import uvisbox; print(uvisbox.__version__)"`

### Problem: Python version incompatible

**Solution**:
1. Check your Python version: `python --version`
2. UVisBox-Assistant requires Python 3.10-3.13
3. Create new environment with correct version:
   ```bash
   conda create -n uvisbox_assistant python=3.13
   ```

## Conda Environment Integration

When using conda environments, environment variables set in your shell profile will be available to the conda environment by default. No additional configuration is needed.

If you want to set environment variables specifically for the conda environment:

```bash
conda activate uvisbox_assistant
conda env config vars set GEMINI_API_KEY="your_api_key_here"
conda deactivate
conda activate uvisbox_assistant  # Reactivate to apply
```

## CI/CD and Production

For automated testing and production deployments:

- **GitHub Actions**: Use repository secrets
- **Docker**: Pass as environment variable with `-e` flag
- **Kubernetes**: Use secrets and configmaps
- **Cloud platforms**: Use platform-specific secrets management

Example for GitHub Actions:
```yaml
env:
  GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

Example for Docker:
```bash
docker run -e GEMINI_API_KEY="$GEMINI_API_KEY" uvisbox_assistant
```

## Quick Start Summary

✅ **Do**:
- Set `GEMINI_API_KEY` in system environment
- Add to shell profile for persistence
- Verify with `echo $GEMINI_API_KEY`
- Keep file permissions restricted
- Use Python 3.10-3.13

❌ **Don't**:
- Store in `.env` files (not used in this project)
- Commit API keys to git
- Share API keys publicly
- Use python-dotenv (not needed)

## Complete Setup Example

```bash
# 1. Set the API key in your shell profile
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc

# 2. Verify it's set
echo $GEMINI_API_KEY

# 3. Create and activate conda environment
conda create -n uvisbox_assistant python=3.13
conda activate uvisbox_assistant

# 4. Install dependencies
pip install -r requirements.txt
pip install uvisbox

# 5. Verify installation
python -c "import uvisbox_assistant; print('Ready!')"

# 6. Run UVisBox-Assistant
python main.py
```

## Automated Setup (Recommended)

For the easiest setup, use the provided script:

```bash
# 1. Set API key (if not already set)
export GEMINI_API_KEY="your_api_key_here"

# 2. Create conda environment
conda create -n uvisbox_assistant python=3.13

# 3. Run setup script
./setup_env.sh

# 4. Start UVisBox-Assistant
python main.py
```

The setup script handles all dependency installation and verification automatically.

## Next Steps

After completing the environment setup:

1. **Read the User Guide**: `docs/USER_GUIDE.md` for usage examples
2. **Check the API Reference**: `docs/API.md` for complete documentation
3. **Run tests**: `python tests/test_simple.py` for quick validation
4. **Start the REPL**: `python main.py` to begin using UVisBox-Assistant

## Additional Resources

- **README.md** - Project overview and features
- **TESTING.md** - Testing strategies and guidelines
- **CONTRIBUTING.md** - Contribution guidelines
- **CLAUDE.md** - Implementation details for AI agents

That's it! No `.env` files needed. Your environment is ready for UVisBox-Assistant v0.1.0.
