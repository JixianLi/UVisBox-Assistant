#!/bin/bash

# ChatUVisBox Environment Setup Script
# This script sets up the development environment for ChatUVisBox

set -e  # Exit on error

echo "=========================================="
echo "ChatUVisBox Environment Setup"
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

# Check if agent environment exists
if conda env list | grep -q "^agent "; then
    print_success "Conda 'agent' environment exists"
else
    print_error "Conda 'agent' environment not found"
    echo "Create it with: conda create -n agent python=3.10"
    exit 1
fi

# Activate agent environment
echo ""
echo "Activating 'agent' environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate agent

if [ "$CONDA_DEFAULT_ENV" = "agent" ]; then
    print_success "Activated 'agent' environment"
else
    print_error "Failed to activate 'agent' environment"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python version: $PYTHON_VERSION"

# Check GEMINI_API_KEY
if [ -z "$GEMINI_API_KEY" ]; then
    print_warning "GEMINI_API_KEY not set in environment"
    echo "  Set it with: export GEMINI_API_KEY='your_key_here'"
    echo "  Add to ~/.bashrc or ~/.zshrc for persistence"
else
    print_success "GEMINI_API_KEY is set"
fi

# Check UVisBox
echo ""
echo "Checking UVisBox installation..."
if python -c "import uvisbox" 2>/dev/null; then
    UVISBOX_VERSION=$(python -c "import uvisbox; print(uvisbox.__version__)")
    print_success "UVisBox $UVISBOX_VERSION is installed"
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
    import google.generativeai
    import numpy
    import pandas
    import matplotlib
    import uvisbox
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
import langgraph, langchain, numpy, pandas, matplotlib, uvisbox
import importlib.metadata

packages = [
    ('langgraph', langgraph),
    ('langchain', langchain),
    ('numpy', numpy),
    ('pandas', pandas),
    ('matplotlib', matplotlib),
    ('uvisbox', uvisbox),
]

for pkg_name, module in packages:
    try:
        version = module.__version__
    except:
        try:
            version = importlib.metadata.version(pkg_name)
        except:
            version = 'unknown'
    print(f'  {pkg_name:25} {version}')
"

# Create directories
echo ""
echo "Creating project directories..."
mkdir -p test_data temp
print_success "Directories created: test_data/, temp/"

# Summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Environment is ready for Phase 1 implementation."
echo ""
echo "Next steps:"
echo "  1. Review plans/README.md"
echo "  2. Read plans/phase_01_schemas_and_dispatchers.md"
echo "  3. Start implementing Phase 1"
echo ""
echo "Run 'conda activate agent' in new terminals to use this environment."
echo ""
