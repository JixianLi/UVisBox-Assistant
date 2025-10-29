"""
Entry point for running ChatUVisBox as a module.

Usage:
    python -m chatuvisbox
"""

import sys


def main():
    """Main entry point for ChatUVisBox."""
    try:
        from .main import main as run_repl
        return run_repl()

    except Exception as e:
        print(f"Error starting ChatUVisBox: {e}")
        print()
        print("Make sure you have:")
        print("  1. Set GEMINI_API_KEY environment variable")
        print("  2. Installed all dependencies: pip install -r requirements.txt")
        print("  3. Installed UVisBox: pip install uvisbox")
        print()
        print("For setup help, see docs/ENVIRONMENT_SETUP.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
