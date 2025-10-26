# Environment Setup for ChatUVisBox

This document explains how to configure the required environment variables for ChatUVisBox.

## API Key Configuration

ChatUVisBox requires the Google Gemini API key to be set in your **system environment** (not in a `.env` file).

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

### Security Notes

1. **Never commit API keys to version control**
2. The key is stored in your shell configuration files, which should have restricted permissions:
   ```bash
   chmod 600 ~/.bashrc  # or ~/.zshrc, etc.
   ```
3. Consider using a secrets manager for production deployments
4. Rotate your API key periodically
5. Monitor your API usage at [Google Cloud Console](https://console.cloud.google.com/)

### Troubleshooting

**Problem**: `GEMINI_API_KEY not found in environment`

**Solution**:
1. Verify you set the variable: `echo $GEMINI_API_KEY`
2. Check you're using the correct shell (bash vs zsh)
3. Ensure you sourced your config file after editing
4. Try setting it temporarily first: `export GEMINI_API_KEY="..."`

**Problem**: API key works in terminal but not in ChatUVisBox

**Solution**:
1. Restart your terminal after adding to config file
2. Make sure conda environment is activated: `conda activate agent`
3. Check Python can access it:
   ```python
   import os
   print(os.getenv("GEMINI_API_KEY"))
   ```

### Conda Environment Integration

When using conda environments, environment variables set in your shell profile will be available to the conda environment by default. No additional configuration is needed.

If you want to set environment variables specifically for the conda environment:

```bash
conda activate agent
conda env config vars set GEMINI_API_KEY="your_api_key_here"
conda deactivate
conda activate agent  # Reactivate to apply
```

### CI/CD and Production

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

## Summary

✅ **Do**:
- Set `GEMINI_API_KEY` in system environment
- Add to shell profile for persistence
- Verify with `echo $GEMINI_API_KEY`
- Keep file permissions restricted

❌ **Don't**:
- Store in `.env` files (not used in this project)
- Commit API keys to git
- Share API keys publicly
- Use `.env` with python-dotenv (not needed)

## Quick Start

```bash
# 1. Set the API key in your shell profile
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc

# 2. Verify it's set
echo $GEMINI_API_KEY

# 3. Activate conda environment
conda activate agent

# 4. Run ChatUVisBox
python main.py
```

That's it! No `.env` files needed.
