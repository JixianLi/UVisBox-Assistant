"""
Interactive REPL for testing multi-turn conversations.

This is a basic version for Phase 6 testing.
Will be enhanced in Phase 8 with full session management.
"""

from chatuvisbox.conversation import ConversationSession
import matplotlib.pyplot as plt


def print_banner():
    """Display welcome banner and command help."""
    print("\n" + "="*70)
    print("  CHATUVISBOX - Interactive REPL (Phase 6 Preview)")
    print("="*70)
    print("\nCommands:")
    print("  /context - Show current conversation context")
    print("  /reset   - Reset conversation to initial state")
    print("  /quit    - Exit the REPL")
    print("\nTips:")
    print("  - Use pronouns like 'it', 'that', 'them' to refer to previous data")
    print("  - The assistant remembers data and visualizations across turns")
    print("  - Try: 'Generate curves' → 'Plot them' → 'Change percentile to 90'")
    print("="*70 + "\n")


def main():
    """Run interactive REPL for multi-turn conversations."""
    print_banner()

    session = ConversationSession()

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input == "/quit":
                print("\n👋 Goodbye!")
                plt.close('all')
                break

            elif user_input == "/reset":
                session.reset()
                print("🔄 Conversation reset\n")
                continue

            elif user_input == "/context":
                ctx = session.get_context_summary()
                print(f"\n📊 Context:")
                for key, value in ctx.items():
                    if key == "session_files" and len(value) > 3:
                        # Truncate long file lists
                        print(f"  {key}: [{len(value)} files]")
                    else:
                        print(f"  {key}: {value}")
                print()
                continue

            # Send message to agent
            print("🤔 Thinking...")
            session.send(user_input)

            # Get and print response
            response = session.get_last_response()
            print(f"\nAssistant: {response}\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type /quit to exit or continue typing.\n")
            continue

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("The conversation will continue. Type /context to see state.\n")
            continue


if __name__ == "__main__":
    main()
