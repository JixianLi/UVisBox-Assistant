"""
Interactive test script for manual testing.

This allows you to test the graph interactively and verify the flow.
Uses gemini-2.0-flash-lite (30 requests/minute rate limit).
"""

from chatuvisbox.graph import run_graph, stream_graph
import matplotlib.pyplot as plt


def print_banner():
    print("\n" + "="*70)
    print("  CHATUVISBOX - Interactive Test")
    print("="*70)
    print("\nModel: gemini-2.0-flash-lite (30 requests/minute)")
    print("\nAvailable test prompts:")
    print("  1. Generate 30 curves and plot functional boxplot")
    print("  2. Generate scalar field and show marching squares")
    print("  3. Load sample_curves.csv and visualize")
    print("  4. Generate curves with all curves visible")
    print("  5. Custom prompt")
    print("  s. Stream mode (show execution steps)")
    print("  q. Quit")
    print()


def run_test(prompt: str, stream: bool = False):
    """Run a test with the given prompt."""
    print(f"\n🔹 Running: {prompt}")
    print("-" * 70)

    if stream:
        # Stream execution
        print("Streaming execution:")
        for update in stream_graph(prompt):
            node_name = list(update.keys())[0]
            print(f"  [{node_name}] executing...")
        print("  [complete]")
    else:
        # Regular execution
        result = run_graph(prompt)

        # Print result
        print(f"\n✅ Complete")
        print(f"  Data path: {result.get('current_data_path')}")

        viz_params = result.get('last_viz_params')
        if viz_params:
            print(f"  Viz tool: {viz_params.get('_tool_name', 'N/A')}")

        print(f"  Errors: {result.get('error_count')}")
        print(f"  Total messages: {len(result.get('messages', []))}")

        # Print final message
        for msg in reversed(result["messages"]):
            if hasattr(msg, "content") and msg.content:
                if "AI" in msg.__class__.__name__:
                    content = msg.content[:300]
                    if len(msg.content) > 300:
                        content += "..."
                    print(f"\n💬 Assistant: {content}")
                    break


def main():
    """Main interactive loop."""
    test_prompts = {
        "1": "Generate 30 ensemble curves with 100 points, then show me a functional boxplot",
        "2": "Generate a 2D scalar field ensemble with 40x40 grid, then visualize with probabilistic marching squares at isovalue 0.6",
        "3": "Load test_data/sample_curves.csv and plot it as a functional boxplot",
        "4": "Generate 20 curves and show functional boxplot with all individual curves visible",
    }

    stream_mode = False

    while True:
        print_banner()

        if stream_mode:
            print("⚡ STREAM MODE ENABLED")

        choice = input("Enter choice: ").strip()

        if choice.lower() == 'q':
            print("\nClosing all windows...")
            plt.close('all')
            print("👋 Goodbye!")
            break

        if choice.lower() == 's':
            stream_mode = not stream_mode
            print(f"Stream mode: {'ON' if stream_mode else 'OFF'}")
            input("\nPress Enter to continue...")
            continue

        if choice in test_prompts:
            prompt = test_prompts[choice]
        elif choice == "5":
            prompt = input("Enter custom prompt: ").strip()
            if not prompt:
                print("Empty prompt, skipping...")
                continue
        else:
            print("Invalid choice")
            input("\nPress Enter to continue...")
            continue

        try:
            run_test(prompt, stream=stream_mode)
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            plt.close('all')
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            input("\nPress Enter to continue...")

    print("\nExiting...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        plt.close('all')
        sys.exit(0)
