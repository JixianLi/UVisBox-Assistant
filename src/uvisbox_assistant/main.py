"""
UVisBox-Assistant - Main interactive REPL

This is the primary user interface for UVisBox-Assistant.
"""

from .conversation import ConversationSession
from .output_control import vprint
import matplotlib.pyplot as plt
import sys


def print_welcome():
    """Print welcome banner."""
    print("\n" + "="*70)
    print("  ╔═══════════════════════════════════════════════════════════╗")
    print("  ║         UVisBox-Assistant - Interactive REPL              ║")
    print("  ║         Natural Language Interface for UVisBox            ║")
    print("  ╚═══════════════════════════════════════════════════════════╝")
    print("="*70)
    print("\nType your requests in natural language. Examples:")
    print("  • Generate 30 curves and plot functional boxplot")
    print("  • Generate vector field and show squid glyphs")
    print("  • Load sample_curves.csv and visualize")
    print("  • Change percentile to 85")
    print("  • colormap plasma")
    print("  • median color blue")
    print("\nCommands:")
    print("  /help       - Show help (all 6 visualizations, 16 commands)")
    print("  /context    - Show current context")
    print("  /stats      - Show session statistics")
    print("  /debug on   - Enable debug mode (full error tracebacks)")
    print("  /verbose on - Show internal state messages")
    print("  /errors     - List recent errors")
    print("  /clear      - Clear session and temp files")
    print("  /reset      - Reset conversation (keep files)")
    print("  /quit       - Exit")
    print("="*70 + "\n")


def print_help():
    """Print detailed help."""
    print("\n" + "="*70)
    print("HELP")
    print("="*70)
    print("\n📚 Available Visualizations (6 types):")
    print("  • functional_boxplot    - Band depth for 1D curves")
    print("  • curve_boxplot         - Depth-colored ensemble curves")
    print("  • contour_boxplot       - Contour band depth from scalar fields")
    print("  • probabilistic_marching_squares - 2D scalar field uncertainty")
    print("  • uncertainty_lobes     - Directional vector uncertainty")
    print("  • squid_glyph_2D        - 2D vector uncertainty glyphs")

    print("\n📊 Data Operations:")
    print("  • Load CSV files: 'Load data.csv'")
    print("  • Generate test data: 'Generate 30 curves'")
    print("  • Generate scalar fields: 'Generate 40x40 scalar field'")
    print("  • Generate vector fields: 'Generate 10x10 vector field'")

    print("\n⚡ Quick Parameter Updates (16 Hybrid Commands):")
    print("\n  Basic:")
    print("    • colormap <name>       - Change colormap (e.g., colormap plasma)")
    print("    • percentile <value>    - Change percentile (e.g., percentile 85)")
    print("    • isovalue <value>      - Change isovalue (e.g., isovalue 0.7)")
    print("    • show/hide median      - Toggle median display")
    print("    • show/hide outliers    - Toggle outliers display")
    print("    • scale <value>         - Change glyph scale (e.g., scale 0.3)")
    print("    • method <fbd|mfbd>     - Change band depth method")

    print("\n  Median Styling:")
    print("    • median color <color>  - Set median color (e.g., median color blue)")
    print("    • median width <value>  - Set median width (e.g., median width 2.5)")
    print("    • median alpha <value>  - Set median alpha (e.g., median alpha 0.8)")

    print("\n  Outliers Styling:")
    print("    • outliers color <color> - Set outliers color (e.g., outliers color black)")
    print("    • outliers width <value> - Set outliers width (e.g., outliers width 1.5)")
    print("    • outliers alpha <value> - Set outliers alpha (e.g., outliers alpha 0.7)")

    print("\n🎮 REPL Commands:")
    print("  • /help         - Show this help message")
    print("  • /context      - Show current conversation context")
    print("  • /stats        - Show session statistics")
    print("  • /clear        - Clear session and temp files")
    print("  • /reset        - Reset conversation (keep files)")
    print("  • /quit         - Exit UVisBox-Assistant")

    print("\n🔍 Debug Commands:")
    print("  • /debug on     - Enable debug mode (full error tracebacks)")
    print("  • /debug off    - Disable debug mode")
    print("  • /verbose on   - Show internal state messages ([HYBRID], [TOOL], etc.)")
    print("  • /verbose off  - Hide internal state messages")
    print("  • /errors       - List recent errors with IDs")
    print("  • /trace <id>   - Show full traceback for error ID")
    print("  • /trace last   - Show traceback for most recent error")

    print("\n💡 Tips:")
    print("  • Use conversational language")
    print("  • Reference previous operations: 'plot that', 'change it'")
    print("  • Chain operations: 'Load X and plot as Y'")
    print("  • Hybrid commands are 10-15x faster than full requests")
    print("  • Enable /debug mode to see detailed error information")
    print("  • Enable /verbose mode to see internal execution flow")

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
                    print(f"\n🔧 Modes:")
                    print(f"  debug_mode: {session.debug_mode}")
                    print(f"  verbose_mode: {session.verbose_mode}")
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

                elif command.startswith("/debug"):
                    parts = user_input.split()
                    if len(parts) == 1 or parts[1].lower() not in ["on", "off"]:
                        print("Usage: /debug on|off")
                        continue

                    if parts[1].lower() == "on":
                        session.debug_mode = True
                        print("🔍 Debug mode: ON (full tracebacks on errors)")
                    else:
                        session.debug_mode = False
                        print("🔍 Debug mode: OFF")
                    continue

                elif command.startswith("/verbose"):
                    parts = user_input.split()
                    if len(parts) == 1 or parts[1].lower() not in ["on", "off"]:
                        print("Usage: /verbose on|off")
                        continue

                    if parts[1].lower() == "on":
                        session.verbose_mode = True
                        print("📢 Verbose mode: ON (show internal messages)")
                        print("   Internal messages like [DATA TOOL], [VIS TOOL], [HYBRID] will now be shown")
                        vprint("[VERBOSE] Test message - if you see this, verbose mode is working!")
                    else:
                        session.verbose_mode = False
                        print("📢 Verbose mode: OFF")
                        print("   Internal messages will be hidden")
                    continue

                elif command == "/errors":
                    if not session.error_history:
                        print("\n✅ No errors in this session\n")
                    else:
                        print(f"\n🚨 Error History ({len(session.error_history)} errors):")
                        for err in session.error_history:
                            # Check if auto-fixed
                            is_auto_fixed = session.is_error_auto_fixed(err.error_id)
                            status = "auto-fixed ✓" if is_auto_fixed else "failed"
                            time_str = err.timestamp.strftime('%H:%M:%S')
                            print(f"  [{err.error_id}] {time_str} - {err.tool_name}: {err.error_type} ({status})")
                        print("\nUse /trace <id> or /trace last to see full details\n")
                    continue

                elif command.startswith("/trace"):
                    parts = user_input.split()
                    if len(parts) != 2:
                        print("Usage: /trace <error_id> or /trace last")
                        print("\nExamples:")
                        print("  /trace 3      - Show full trace for error ID 3")
                        print("  /trace last   - Show trace for most recent error")
                        continue

                    # Handle /trace last
                    if parts[1].lower() == "last":
                        err = session.get_last_error()
                        if err:
                            print(f"\n{err.detailed()}")
                            if session.is_error_auto_fixed(err.error_id):
                                print("\n✓ This error was automatically fixed by the agent\n")
                            else:
                                print()
                        else:
                            print("\n✅ No errors recorded yet\n")
                        continue

                    # Handle /trace <id>
                    try:
                        error_id = int(parts[1])
                        err = session.get_error(error_id)
                        if err:
                            # Show detailed error
                            print(f"\n{err.detailed()}")
                            # Add auto-fix status if it was fixed after recording
                            if session.is_error_auto_fixed(error_id):
                                print("\n✓ This error was automatically fixed by the agent\n")
                            else:
                                print()
                        else:
                            print(f"\n❌ Error ID {error_id} not found")
                            print("Use /errors to see available error IDs\n")
                    except ValueError:
                        print(f"❌ Error ID must be a number or 'last', got: '{parts[1]}'")
                        print("Use /errors to see list of error IDs")
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
