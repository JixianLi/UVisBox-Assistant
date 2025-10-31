"""
Interactive testing script for ChatUVisBox with pre-defined options.

This script provides a menu-driven interface for testing various
visualization and data generation scenarios.
"""
import sys
sys.path.insert(0, '/Users/jixianli/projects/chatuvisbox/src')

from uvisbox_assistant.graph import run_graph
from uvisbox_assistant.state import GraphState
from pathlib import Path


def print_menu():
    """Display the interactive test menu."""
    print("\n" + "="*70)
    print("CHATUVISBOX INTERACTIVE TEST")
    print("="*70)
    print("\n📊 VISUALIZATION OPTIONS:")
    print("  1. Functional Boxplot (generate 30 curves)")
    print("  2. Functional Boxplot (generate 50 curves)")
    print("  3. Functional Boxplot with all curves shown")
    print("  4. Curve Boxplot")
    print("  5. Probabilistic Marching Squares (isovalue 0.5)")
    print("  6. Probabilistic Marching Squares (isovalue 0.3)")
    print("  7. Contour Boxplot (isovalue 0.5)")
    print("  8. Contour Boxplot (isovalue 0.7)")
    print("  9. Uncertainty Lobes (10x10 grid)")
    print(" 10. Uncertainty Lobes (8x8 grid)")
    
    print("\n🔬 DATA GENERATION OPTIONS:")
    print(" 11. Generate 100 curves with 200 points")
    print(" 12. Generate scalar field 100x100 with 50 ensemble members")
    print(" 13. Generate vector field 20x20 with 40 instances")
    print(" 14. Load CSV file (specify path)")
    
    print("\n🎨 PARAMETER VARIATION OPTIONS:")
    print(" 15. Functional boxplot with percentiles [10, 50, 90, 100]")
    print(" 16. Functional boxplot with percentiles [25, 75, 100]")
    print(" 17. Contour boxplot with percentiles [10, 30, 70, 90]")
    print(" 18. Uncertainty lobes with percentile1=95, percentile2=60")
    
    print("\n🔄 MULTI-STEP WORKFLOWS:")
    print(" 19. Generate curves → Functional boxplot → Curve boxplot")
    print(" 20. Generate scalar field → Probabilistic MS → Contour boxplot")
    print(" 21. Generate vector field → Uncertainty lobes (2 different scales)")
    
    print("\n💡 CUSTOM & ADVANCED:")
    print(" 22. Custom: Enter your own prompt")
    print(" 23. Show current state info")
    print(" 24. Clear all temp files")
    print("  0. Exit")
    print("\n" + "="*70)


def execute_option(option: int, state: GraphState = None) -> GraphState:
    """
    Execute the selected menu option.
    
    Args:
        option: Menu option number
        state: Current state (for multi-turn)
    
    Returns:
        Updated state after execution
    """
    prompts = {
        # Visualization options
        1: "Generate 30 curves and create a functional boxplot",
        2: "Generate 50 curves with 100 points each and show functional boxplot",
        3: "Generate 30 curves and plot functional boxplot with all curves shown",
        4: "Generate 50 curves and display curve boxplot",
        5: "Generate a 50x50 scalar field ensemble and show probabilistic marching squares at isovalue 0.5",
        6: "Generate scalar field 60x60 and visualize probabilistic marching squares at isovalue 0.3",
        7: "Generate 50x50 scalar field and create contour boxplot with isovalue 0.5",
        8: "Generate scalar field and show contour boxplot at isovalue 0.7",
        9: "Generate 10x10 vector field and plot uncertainty lobes",
        10: "Generate 8x8 vector field with 30 instances and show uncertainty lobes with scale 0.3",
        
        # Data generation options
        11: "Generate 100 curves with 200 points each",
        12: "Generate scalar field ensemble with nx=100, ny=100, n_ensemble=50",
        13: "Generate vector field ensemble 20x20 with 40 instances",
        
        # Parameter variations
        15: "Generate 30 curves and plot functional boxplot with percentiles [10, 50, 90, 100]",
        16: "Generate 40 curves and show functional boxplot with percentiles [25, 75, 100]",
        17: "Generate 50x50 scalar field and create contour boxplot at isovalue 0.6 with percentiles [10, 30, 70, 90]",
        18: "Generate 10x10 vector field and plot uncertainty lobes with percentile1=95 and percentile2=60",
        
        # Multi-step workflows
        19: "Generate 30 curves",  # Will be followed by additional prompts
        20: "Generate 50x50 scalar field ensemble",  # Will be followed by additional prompts
        21: "Generate 15x15 vector field",  # Will be followed by additional prompts
    }
    
    if option == 0:
        print("\n👋 Exiting interactive test. Goodbye!")
        return None
    
    elif option == 14:
        # Load CSV - custom path
        csv_path = input("\nEnter CSV file path: ").strip()
        prompt = f"Load {csv_path} and convert to numpy array"
    
    elif option == 22:
        # Custom prompt
        prompt = input("\nEnter your custom prompt: ").strip()
        if not prompt:
            print("⚠️  Empty prompt, skipping.")
            return state
    
    elif option == 23:
        # Show state info
        if state:
            print("\n" + "="*70)
            print("CURRENT STATE INFO")
            print("="*70)
            print(f"Messages count: {len(state.get('messages', []))}")
            print(f"Current data path: {state.get('current_data_path', 'None')}")
            print(f"Last vis params: {state.get('last_vis_params', 'None')}")
            print(f"Session files: {len(state.get('session_files', []))} files")
            print(f"Error count: {state.get('error_count', 0)}")
            print("="*70)
        else:
            print("\n⚠️  No active state yet.")
        return state
    
    elif option == 24:
        # Clear temp files
        from uvisbox_assistant.utils import cleanup_temp_files
        print("\n🧹 Clearing temporary files...")
        cleanup_temp_files()
        return None
    
    elif option in prompts:
        prompt = prompts[option]
    
    else:
        print(f"\n⚠️  Invalid option: {option}")
        return state
    
    # Execute the prompt
    print(f"\n🚀 Executing: {prompt}")
    print("-" * 70)
    
    try:
        result_state = run_graph(prompt, initial_state=state)
        
        # Print last assistant response
        for msg in reversed(result_state["messages"]):
            if hasattr(msg, "content") and msg.content:
                if "AI" in msg.__class__.__name__:
                    print(f"\n💬 Assistant: {msg.content}")
                    break
        
        # Handle multi-step workflows
        if option == 19:
            print("\n🔄 Continuing workflow: Functional boxplot...")
            result_state = run_graph("Show functional boxplot", initial_state=result_state)
            for msg in reversed(result_state["messages"]):
                if hasattr(msg, "content") and msg.content and "AI" in msg.__class__.__name__:
                    print(f"\n💬 Assistant: {msg.content}")
                    break
            
            print("\n🔄 Continuing workflow: Curve boxplot...")
            result_state = run_graph("Now show curve boxplot", initial_state=result_state)
            for msg in reversed(result_state["messages"]):
                if hasattr(msg, "content") and msg.content and "AI" in msg.__class__.__name__:
                    print(f"\n💬 Assistant: {msg.content}")
                    break
        
        elif option == 20:
            print("\n🔄 Continuing workflow: Probabilistic marching squares...")
            result_state = run_graph("Show probabilistic marching squares at isovalue 0.5", initial_state=result_state)
            for msg in reversed(result_state["messages"]):
                if hasattr(msg, "content") and msg.content and "AI" in msg.__class__.__name__:
                    print(f"\n💬 Assistant: {msg.content}")
                    break
            
            print("\n🔄 Continuing workflow: Contour boxplot...")
            result_state = run_graph("Now show contour boxplot at isovalue 0.6", initial_state=result_state)
            for msg in reversed(result_state["messages"]):
                if hasattr(msg, "content") and msg.content and "AI" in msg.__class__.__name__:
                    print(f"\n💬 Assistant: {msg.content}")
                    break
        
        elif option == 21:
            print("\n🔄 Continuing workflow: Uncertainty lobes (scale 0.2)...")
            result_state = run_graph("Plot uncertainty lobes with scale 0.2", initial_state=result_state)
            for msg in reversed(result_state["messages"]):
                if hasattr(msg, "content") and msg.content and "AI" in msg.__class__.__name__:
                    print(f"\n💬 Assistant: {msg.content}")
                    break
            
            print("\n🔄 Continuing workflow: Uncertainty lobes (scale 0.5)...")
            result_state = run_graph("Show uncertainty lobes again with scale 0.5", initial_state=result_state)
            for msg in reversed(result_state["messages"]):
                if hasattr(msg, "content") and msg.content and "AI" in msg.__class__.__name__:
                    print(f"\n💬 Assistant: {msg.content}")
                    break
        
        print("\n" + "-" * 70)
        print("✅ Execution completed successfully")
        
        return result_state
    
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        return state


def main():
    """Main interactive loop."""
    print("\n🎨 ChatUVisBox Interactive Testing Interface")
    print("This tool helps you test various visualization scenarios quickly.\n")
    
    state = None
    
    while True:
        print_menu()
        
        try:
            choice = input("\nSelect option (0-24): ").strip()
            
            if not choice:
                continue
            
            option = int(choice)
            
            if option == 0:
                execute_option(0)
                break
            
            state = execute_option(option, state)
            
            # Pause for user to see results
            input("\nPress Enter to continue...")
        
        except ValueError:
            print("\n⚠️  Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
