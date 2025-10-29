"""
ChatUVisBox - Main interactive REPL

This is the primary user interface for ChatUVisBox.
"""

from .conversation import ConversationSession
import matplotlib.pyplot as plt
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
