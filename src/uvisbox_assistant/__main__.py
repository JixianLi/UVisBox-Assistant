"""
Entry point for running UVisBox-Assistant as a module.

Usage:
    python -m uvisbox_assistant
"""

import sys


def main():
    """Main entry point for UVisBox-Assistant."""
    try:
        from .main import main as run_repl
        return run_repl()

    except Exception as e:
        print(f"Error starting UVisBox-Assistant: {e}")
        print()
        print("Make sure you have:")
        print("  1. A running Ollama server reachable at OLLAMA_API_URL with a tool-capable model")
        print("  2. Installed all dependencies: poetry install")
        print("  3. Installed UVisBox: pip install uvisbox")
        print()
        print("For setup help, see docs/ENVIRONMENT_SETUP.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
