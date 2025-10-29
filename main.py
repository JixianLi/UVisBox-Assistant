#!/usr/bin/env python
"""
ChatUVisBox - Convenience wrapper for running the REPL

This is a convenience script that imports and runs the main REPL
from the chatuvisbox package.

Usage:
    python main.py

Or use the module directly:
    python -m chatuvisbox
"""

import sys

# Run the main REPL from the package
if __name__ == "__main__":
    from src.chatuvisbox.main import main
    sys.exit(main())
