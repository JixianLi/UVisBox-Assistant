# Phase 8: Session & Interaction Management

**Goal**: Implement session cleanup, file management, and polish the interactive experience.

**Duration**: 0.5 day

## Prerequisites

- Phase 7 completed (hybrid control working)
- Understanding of temp file management

## Tasks

### Task 8.1: Implement Session Cleanup Tool

**File**: Update `src/chatuvisbox/data_tools.py`

```python
# Add to data_tools.py

def clear_session() -> Dict[str, str]:
    """
    Clear all temporary session files.

    Removes all .npy files in temp directory with TEMP_FILE_PREFIX.

    Returns:
        Dict with status and count of files removed
    """
    try:
        if not config.TEMP_DIR.exists():
            return {
                "status": "success",
                "message": "No temp directory found",
                "files_removed": 0
            }

        files_removed = []
        pattern = f"{config.TEMP_FILE_PREFIX}*{config.TEMP_FILE_EXTENSION}"

        for file_path in config.TEMP_DIR.glob(pattern):
            try:
                file_path.unlink()
                files_removed.append(str(file_path.name))
            except Exception as e:
                print(f"Warning: Could not remove {file_path}: {e}")

        return {
            "status": "success",
            "message": f"Removed {len(files_removed)} temporary files",
            "files_removed": len(files_removed),
            "files": files_removed
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error clearing session: {str(e)}"
        }


# Add to DATA_TOOLS registry
DATA_TOOLS["clear_session"] = clear_session

# Add to DATA_TOOL_SCHEMAS
DATA_TOOL_SCHEMAS.append({
    "name": "clear_session",
    "description": "Clear all temporary session files to start fresh",
    "parameters": {
        "type": "object",
        "properties": {}
    }
})
```

**Test:**
```python
# test_clear_session.py
from data_tools import generate_ensemble_curves, clear_session
import config

# Generate some files
result1 = generate_ensemble_curves(n_curves=10)
result2 = generate_ensemble_curves(n_curves=20)

print("Files before clear:")
print(list(config.TEMP_DIR.glob("_temp_*")))

# Clear
result = clear_session()
print(f"\n{result}")

print("\nFiles after clear:")
print(list(config.TEMP_DIR.glob("_temp_*")))
```

### Task 8.2: Enhance Conversation Session Management

**File**: Update `src/chatuvisbox/conversation.py`

```python
# Add to ConversationSession class:

class ConversationSession:
    # ... existing code ...

    def clear(self):
        """Clear session data and temporary files."""
        from data_tools import clear_session

        # Clear temp files
        result = clear_session()
        print(f"🧹 {result['message']}")

        # Reset state
        self.reset()

    def get_session_files(self) -> list:
        """Get list of session files."""
        if not self.state:
            return []
        return self.state.get("session_files", [])

    def get_stats(self) -> dict:
        """Get session statistics."""
        ctx = self.get_context_summary()
        return {
            "turns": ctx["turn_count"],
            "messages": ctx["message_count"],
            "files_created": len(ctx.get("session_files", [])),
            "current_data": ctx.get("current_data") is not None,
            "current_vis": ctx.get("last_vis") is not None,
        }
```

### Task 8.3: Enhanced REPL with Full Features

**File**: `main.py` (final version)

```python
"""
ChatUVisBox - Main interactive REPL

This is the primary user interface for the MVP.
"""

from conversation import ConversationSession
import matplotlib.pyplot as plt
from pathlib import Path
import sys


def print_welcome():
    """Print welcome banner."""
    print("\n" + "="*70)
    print("  ╔═══════════════════════════════════════════════════════════╗")
    print("  ║              ChatUVisBox - Interactive REPL                ║")
    print("  ║         Natural Language Interface for UVisBox             ║")
    print("  ╚═══════════════════════════════════════════════════════════╝")
    print("="*70)
    print("\nType your requests in natural language. Examples:")
    print("  • Generate 30 curves and plot functional boxplot")
    print("  • Load sample_curves.csv and visualize")
    print("  • Change percentile to 85")
    print("  • colormap plasma")
    print("\nCommands:")
    print("  /help     - Show help")
    print("  /context  - Show current context")
    print("  /stats    - Show session statistics")
    print("  /clear    - Clear session and temp files")
    print("  /reset    - Reset conversation (keep files)")
    print("  /quit     - Exit")
    print("="*70 + "\n")


def print_help():
    """Print detailed help."""
    print("\n" + "="*70)
    print("HELP")
    print("="*70)
    print("\n📚 Available Visualizations:")
    print("  • functional_boxplot    - Band depth for 1D curves")
    print("  • curve_boxplot         - Depth-colored ensemble curves")
    print("  • probabilistic_marching_squares - 2D scalar field uncertainty")
    print("  • contour_boxplot       - Contour band depth from scalar fields")
    print("  • uncertainty_lobes     - Directional vector uncertainty")

    print("\n📊 Data Operations:")
    print("  • Load CSV files: 'Load data.csv'")
    print("  • Generate test data: 'Generate 30 curves'")
    print("  • Generate scalar fields: 'Generate 40x40 scalar field'")

    print("\n⚡ Quick Parameter Updates (Hybrid Control):")
    print("  • colormap <name>       - Change colormap")
    print("  • percentile <value>    - Change percentile")
    print("  • isovalue <value>      - Change isovalue")
    print("  • show/hide median      - Toggle median display")
    print("  • show/hide outliers    - Toggle outliers display")

    print("\n💡 Tips:")
    print("  • Use conversational language")
    print("  • Reference previous operations: 'plot that', 'change it'")
    print("  • Chain operations: 'Load X and plot as Y'")

    print("="*70 + "\n")


def main():
    """Run the main REPL."""
    print_welcome()

    session = ConversationSession()

    while True:
        try:
            # Get user input
            try:
                user_input = input("You: ").strip()
            except EOFError:
                print("\n👋 Goodbye!")
                break

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower()

                if command == "/quit" or command == "/exit":
                    print("\n👋 Goodbye!")
                    plt.close('all')
                    break

                elif command == "/reset":
                    session.reset()
                    print("🔄 Conversation reset (files preserved)")
                    continue

                elif command == "/clear":
                    session.clear()
                    print("🧹 Session cleared (conversation and files)")
                    continue

                elif command == "/context":
                    ctx = session.get_context_summary()
                    print(f"\n📊 Context:")
                    for key, value in ctx.items():
                        print(f"  {key}: {value}")
                    print()
                    continue

                elif command == "/stats":
                    stats = session.get_stats()
                    print(f"\n📈 Session Statistics:")
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
                    print()
                    continue

                elif command == "/help":
                    print_help()
                    continue

                else:
                    print(f"❓ Unknown command: {command}")
                    print("   Type /help for available commands")
                    continue

            # Send message to agent
            print("🤔 Processing...")

            try:
                session.send(user_input)
                response = session.get_last_response()
                print(f"\nAssistant: {response}\n")

            except Exception as e:
                print(f"\n❌ Error processing request: {e}")
                print("   Type /reset to reset the conversation\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type /quit to exit.\n")
            continue

        except Exception as e:
            print(f"\n❌ Unexpected error: {e}\n")
            continue


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        plt.close('all')
        sys.exit(1)
```

### Task 8.4: Matplotlib Window Management

**File**: `src/chatuvisbox/vis_manager.py`

```python
"""Matplotlib window management utilities."""

import matplotlib.pyplot as plt
from typing import List


class VisManager:
    """Manage matplotlib visualization windows."""

    def __init__(self):
        self.figure_count = 0
        self.active_figures: List[int] = []

    def show_plot(self, fig) -> int:
        """
        Show a plot and track it.

        Args:
            fig: Matplotlib figure

        Returns:
            Figure number
        """
        self.figure_count += 1
        self.active_figures.append(fig.number)

        plt.show(block=False)
        plt.pause(0.1)  # Brief pause to ensure window appears

        return fig.number

    def close_all(self):
        """Close all tracked figures."""
        plt.close('all')
        self.active_figures = []
        self.figure_count = 0

    def close_last(self):
        """Close the most recent figure."""
        if self.active_figures:
            last_fig = self.active_figures.pop()
            plt.close(last_fig)

    def get_active_count(self) -> int:
        """Get number of active figure windows."""
        return len(self.active_figures)


# Global instance
vis_manager = VisManager()
```

Update vis_tools.py to use VisManager:

```python
from vis_manager import vis_manager

# In each vis tool, after plt.show(block=False):
vis_manager.show_plot(fig)
```

### Task 8.5: Add Progress Indicators

**File**: Update `main.py`

```python
# Add visual feedback for long operations

import sys

def show_thinking():
    """Show thinking animation."""
    sys.stdout.write("🤔 Processing")
    sys.stdout.flush()

def hide_thinking():
    """Clear thinking animation."""
    sys.stdout.write("\r" + " "*50 + "\r")
    sys.stdout.flush()

# In main loop:
show_thinking()
try:
    session.send(user_input)
    hide_thinking()
    # ...
```

### Task 8.6: Test Session Management

**File**: `tests/test_session_management.py`

```python
"""Test session management features."""

from conversation import ConversationSession
import matplotlib.pyplot as plt
from pathlib import Path
import config


def test_clear_session():
    """Test: Clear session removes temp files."""
    print("\n" + "="*70)
    print("TEST: Clear Session")
    print("="*70)

    session = ConversationSession()

    # Generate some data
    session.send("Generate 20 curves")
    session.send("Generate scalar field 30x30")

    files_before = list(config.TEMP_DIR.glob("_temp_*"))
    print(f"\n📁 Files before clear: {len(files_before)}")

    # Clear session
    session.clear()

    files_after = list(config.TEMP_DIR.glob("_temp_*"))
    print(f"📁 Files after clear: {len(files_after)}")

    assert len(files_after) == 0, "Should have removed all temp files"
    assert session.state is None, "Should have reset state"

    print("\n✅ Clear session test passed")


def test_reset_vs_clear():
    """Test: Reset preserves files, clear removes them."""
    print("\n" + "="*70)
    print("TEST: Reset vs Clear")
    print("="*70)

    session = ConversationSession()

    # Generate data
    session.send("Generate 15 curves")
    ctx1 = session.get_context_summary()
    data_path = ctx1["current_data"]

    print(f"\n📁 Data path: {data_path}")
    assert Path(data_path).exists(), "Data file should exist"

    # Reset (preserves files)
    session.reset()
    assert session.state is None, "State should be reset"
    assert Path(data_path).exists(), "Data file should still exist after reset"
    print("✓ Reset preserved files")

    # Clear (removes files)
    session2 = ConversationSession()
    session2.send("Generate 15 curves")
    ctx2 = session2.get_context_summary()
    data_path2 = ctx2["current_data"]

    session2.clear()
    assert not Path(data_path2).exists(), "Data file should be removed after clear"
    print("✓ Clear removed files")

    print("\n✅ Reset vs Clear test passed")


def test_session_stats():
    """Test: Session statistics are tracked correctly."""
    print("\n" + "="*70)
    print("TEST: Session Statistics")
    print("="*70)

    session = ConversationSession()

    # Initial stats
    stats0 = session.get_stats()
    print(f"\nInitial stats: {stats0}")
    assert stats0["turns"] == 0

    # After some operations
    session.send("Generate curves")
    session.send("Plot them")
    session.send("colormap plasma")

    stats = session.get_stats()
    print(f"\nFinal stats: {stats}")

    assert stats["turns"] == 3
    assert stats["current_data"] is True
    assert stats["current_vis"] is True

    print("\n✅ Session stats test passed")


def run_all_session_tests():
    """Run all session management tests."""
    print("\n" + "🗂️ "*35)
    print("CHATUVISBOX: SESSION MANAGEMENT TESTS")
    print("🗂️ "*35)

    tests = [
        test_clear_session,
        test_reset_vs_clear,
        test_session_stats,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "="*70)
    print("SESSION MANAGEMENT TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")

    plt.close('all')
    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_session_tests()
    exit(0 if failed == 0 else 1)
```

Run:
```bash
python test_session_management.py
```

## Validation Checklist

- [ ] `/clear` command removes all temp files
- [ ] `/reset` command preserves files but resets conversation
- [ ] `/context` shows current state
- [ ] `/stats` shows accurate statistics
- [ ] `/help` displays comprehensive help
- [ ] Matplotlib windows don't block interaction
- [ ] Progress indicators appear during processing
- [ ] Session file tracking works correctly
- [ ] Error recovery maintains usable state
- [ ] Clean exit with `/quit` closes all windows

## Enhanced REPL Features

### Commands
- `/help` - Comprehensive help
- `/context` - Show current state
- `/stats` - Session statistics
- `/clear` - Clear files and reset
- `/reset` - Reset conversation only
- `/quit` - Exit cleanly

### User Experience
- Welcome banner
- Clear command reference
- Progress indicators
- Helpful error messages
- Clean window management

## Output

After Phase 8, you should have:
- Complete session management system
- Polished interactive REPL
- Temp file cleanup functionality
- Session statistics tracking
- Enhanced user experience with commands and help
- Comprehensive session management tests

## Next Phase

Phase 9 will perform final end-to-end testing with various failure scenarios and edge cases.
