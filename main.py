#!/usr/bin/env python
"""
UVisBox-Assistant - Convenience wrapper for running the REPL

This is a convenience script that imports and runs the main REPL
from the uvisbox_assistant package.

Usage:
    python main.py

Or use the module directly:
    python -m uvisbox_assistant
"""

import sys

# Run the main REPL from the package
if __name__ == "__main__":
    from src.uvisbox_assistant.main import main
    sys.exit(main())
