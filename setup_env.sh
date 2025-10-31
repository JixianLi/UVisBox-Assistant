#!/bin/bash

# UVisBox-Assistant Environment Setup Script
# This script sets up the development environment for UVisBox-Assistant

set -e  # Exit on error

echo "=========================================="
echo "UVisBox-Assistant Environment Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if conda is available
if ! command -v conda &> /dev/null; then
    print_error "Conda not found. Please install conda first."
    exit 1
fi

print_success "Conda is available"

# Default environment name
ENV_NAME="${1:-agent}"

# Check if environment exists
if conda env list | grep -q "^${ENV_NAME} "; then
    print_success "Conda '${ENV_NAME}' environment exists"
else
    print_warning "Conda '${ENV_NAME}' environment not found"
    echo "Create it with: conda create -n ${ENV_NAME} python=3.13"
    echo "Or specify existing environment: ./setup_env.sh your_env_name"
    exit 1
fi

# Activate environment
echo ""
echo "Activating '${ENV_NAME}' environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "${ENV_NAME}"

if [ "$CONDA_DEFAULT_ENV" = "${ENV_NAME}" ]; then
    print_success "Activated '${ENV_NAME}' environment"
else
    print_error "Failed to activate '${ENV_NAME}' environment"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python version: $PYTHON_VERSION"

# Verify Python version is 3.10+
PYTHON_MAJOR=$(python -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 10 ] && [ "$PYTHON_MINOR" -lt 14 ]; then
    print_success "Python version compatible (3.10-3.13)"
else
    print_warning "Python $PYTHON_VERSION may not be compatible"
    echo "  Recommended: Python 3.10-3.13"
fi

# Check GEMINI_API_KEY
if [ -z "$GEMINI_API_KEY" ]; then
    print_warning "GEMINI_API_KEY not set in environment"
    echo "  Set it with: export GEMINI_API_KEY='your_key_here'"
    echo "  Add to ~/.bashrc or ~/.zshrc for persistence"
    echo "  See docs/ENVIRONMENT_SETUP.md for details"
else
    print_success "GEMINI_API_KEY is set"
fi

# Check UVisBox
echo ""
echo "Checking UVisBox installation..."
if python -c "import uvisbox" 2>/dev/null; then
    UVISBOX_VERSION=$(python -c "import uvisbox; print(uvisbox.__version__)" 2>/dev/null || echo "unknown")
    print_success "UVisBox ${UVISBOX_VERSION} is installed"
else
    print_error "UVisBox not found"
    echo "Install with: pip install uvisbox"
    exit 1
fi

# Install dependencies
echo ""
echo "Installing dependencies from requirements.txt..."
if pip install -r requirements.txt; then
    print_success "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Verify installation
echo ""
echo "Verifying installation..."

VERIFICATION=$(python -c "
import sys
try:
    import langgraph
    import langchain
    import langchain_google_genai
    import numpy
    import pandas
    import matplotlib
    import uvisbox
    import langsmith
    print('SUCCESS')
except ImportError as e:
    print(f'FAILED: {e}')
    sys.exit(1)
" 2>&1)

if [ "$VERIFICATION" = "SUCCESS" ]; then
    print_success "All dependencies verified"
else
    print_error "Verification failed: $VERIFICATION"
    exit 1
fi

# Print package versions
echo ""
echo "Installed package versions:"
python -c "
import importlib.metadata

packages = [
    'langgraph',
    'langchain',
    'langchain-google-genai',
    'langsmith',
    'numpy',
    'pandas',
    'matplotlib',
    'uvisbox',
]

for pkg_name in packages:
    try:
        version = importlib.metadata.version(pkg_name)
    except:
        version = 'unknown'
    print(f'  {pkg_name:25} {version}')
"

# Create directories
echo ""
echo "Creating project directories..."
mkdir -p test_data temp logs
print_success "Directories created: test_data/, temp/, logs/"

# Summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "UVisBox-Assistant v0.2.0 environment is ready."
echo ""
echo "Next steps:"
echo "  1. Review README.md for project overview"
echo "  2. Check docs/USER_GUIDE.md for usage examples"
echo "  3. Run quick test: python tests/test_simple.py"
echo "  4. Start the REPL: python main.py"
echo ""
echo "Documentation:"
echo "  - User Guide: docs/USER_GUIDE.md"
echo "  - API Reference: docs/API.md"
echo "  - Testing Guide: TESTING.md"
echo "  - Contributing: CONTRIBUTING.md"
echo ""
echo "Run 'conda activate ${ENV_NAME}' in new terminals to use this environment."
echo ""
