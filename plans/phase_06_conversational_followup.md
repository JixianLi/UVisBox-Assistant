# Phase 6: Conversational Follow-up Test

**Goal**: Verify multi-turn conversations work correctly with proper context maintenance.

**Duration**: 0.5 day

## Prerequisites

- Phase 5 completed (error handling working)
- Understanding of stateful conversations in LangGraph

## Tasks

### Task 6.1: Implement Conversation Manager

**File**: `conversation.py`

```python
"""Conversation management for multi-turn interactions."""

from typing import Optional
from state import GraphState, create_initial_state
from graph import graph_app
from langchain_core.messages import HumanMessage


class ConversationSession:
    """
    Manages a multi-turn conversation session.

    Maintains state across multiple user inputs.
    """

    def __init__(self):
        """Initialize a new conversation session."""
        self.state: Optional[GraphState] = None
        self.turn_count = 0

    def send(self, user_message: str) -> GraphState:
        """
        Send a user message and get response.

        Args:
            user_message: User's input

        Returns:
            Updated state after graph execution
        """
        self.turn_count += 1

        if self.state is None:
            # First turn - create initial state
            self.state = create_initial_state(user_message)
        else:
            # Subsequent turn - add to existing state
            self.state["messages"].append(HumanMessage(content=user_message))

        # Run graph with current state
        self.state = graph_app.invoke(self.state)

        return self.state

    def get_last_response(self) -> str:
        """Get the last assistant response."""
        if not self.state:
            return ""

        for msg in reversed(self.state["messages"]):
            if hasattr(msg, "content") and msg.content:
                if "AI" in msg.__class__.__name__:
                    return msg.content

        return ""

    def get_context_summary(self) -> dict:
        """Get a summary of current context."""
        if not self.state:
            return {}

        return {
            "turn_count": self.turn_count,
            "current_data": self.state.get("current_data_path"),
            "last_viz": self.state.get("last_viz_params"),
            "session_files": self.state.get("session_files", []),
            "error_count": self.state.get("error_count"),
            "message_count": len(self.state["messages"])
        }

    def reset(self):
        """Reset the conversation session."""
        self.state = None
        self.turn_count = 0
```

**Test:**
```python
# test_conversation.py
from conversation import ConversationSession

session = ConversationSession()

# Turn 1
result1 = session.send("Generate 20 test curves")
print(f"Turn 1 response: {session.get_last_response()[:100]}")
print(f"Context: {session.get_context_summary()}")

# Turn 2
result2 = session.send("Now plot them as a functional boxplot")
print(f"\nTurn 2 response: {session.get_last_response()[:100]}")
print(f"Context: {session.get_context_summary()}")
```

### Task 6.2: Multi-Turn Test Suite

**File**: `test_multiturn.py`

```python
"""Test multi-turn conversations."""

from conversation import ConversationSession
import matplotlib.pyplot as plt


def test_sequential_operations():
    """Test: User does operations in sequence."""
    print("\n" + "="*70)
    print("TEST: Sequential Operations")
    print("="*70)

    session = ConversationSession()

    # Turn 1: Generate data
    print("\n🔹 Turn 1: Generate data")
    session.send("Generate 30 curves with 100 points")
    response1 = session.get_last_response()
    print(f"   Response: {response1[:150]}")

    ctx = session.get_context_summary()
    assert ctx["current_data"] is not None, "Should have data path"
    print(f"   ✓ Data generated: {ctx['current_data']}")

    # Turn 2: Visualize using implicit reference
    print("\n🔹 Turn 2: Visualize (implicit reference)")
    session.send("Show me a functional boxplot of that")
    response2 = session.get_last_response()
    print(f"   Response: {response2[:150]}")

    ctx = session.get_context_summary()
    assert ctx["last_viz"] is not None, "Should have viz params"
    print(f"   ✓ Visualization created")

    # Turn 3: Modify viz
    print("\n🔹 Turn 3: Modify visualization")
    session.send("Change the percentile to 80")
    response3 = session.get_last_response()
    print(f"   Response: {response3[:150]}")

    print("\n✅ Sequential operations test passed")
    return session


def test_context_preservation():
    """Test: Context is preserved across turns."""
    print("\n" + "="*70)
    print("TEST: Context Preservation")
    print("="*70)

    session = ConversationSession()

    # Turn 1
    session.send("Generate 25 curves")
    ctx1 = session.get_context_summary()
    data_path_1 = ctx1["current_data"]

    # Turn 2: Should remember data from turn 1
    session.send("Plot it as functional boxplot")
    ctx2 = session.get_context_summary()

    assert ctx2["current_data"] == data_path_1, "Data path should be preserved"
    assert ctx2["turn_count"] == 2, "Should track turns"

    print(f"✓ Context preserved across {ctx2['turn_count']} turns")
    print(f"✓ Data path: {ctx2['current_data']}")

    # Turn 3: Generate new data
    session.send("Now generate a scalar field ensemble with 30x30 grid")
    ctx3 = session.get_context_summary()

    assert ctx3["current_data"] != data_path_1, "Should have new data path"
    print(f"✓ New data path: {ctx3['current_data']}")

    # Turn 4: Visualize new data
    session.send("Show probabilistic marching squares at isovalue 0.6")
    ctx4 = session.get_context_summary()

    assert ctx4["last_viz"] is not None, "Should have new viz"
    print(f"✓ New visualization created")

    print("\n✅ Context preservation test passed")
    return session


def test_pronoun_reference():
    """Test: Agent understands pronouns and references."""
    print("\n" + "="*70)
    print("TEST: Pronoun Reference")
    print("="*70)

    session = ConversationSession()

    # Generate data
    session.send("Generate some test curves")
    ctx1 = session.get_context_summary()
    data_path = ctx1["current_data"]

    # Use pronoun reference
    session.send("Plot it")  # "it" should refer to the generated data
    ctx2 = session.get_context_summary()

    assert ctx2["last_viz"] is not None, "Should have created viz"
    print(f"✓ Agent understood 'it' refers to {data_path}")

    # Another reference
    session.send("Make it prettier")  # Should modify last viz
    response = session.get_last_response()

    print(f"   Response: {response[:150]}")
    print("\n✅ Pronoun reference test passed")

    return session


def test_error_and_recovery_in_conversation():
    """Test: Error in middle of conversation doesn't break context."""
    print("\n" + "="*70)
    print("TEST: Error and Recovery in Conversation")
    print("="*70)

    session = ConversationSession()

    # Turn 1: Success
    session.send("Generate 20 curves")
    ctx1 = session.get_context_summary()
    assert ctx1["error_count"] == 0

    # Turn 2: Error
    session.send("Load nonexistent_file.csv")
    ctx2 = session.get_context_summary()
    print(f"   Error count after bad load: {ctx2['error_count']}")

    # Turn 3: Recovery - use previous data
    session.send("Actually, just plot the curves I generated earlier")
    ctx3 = session.get_context_summary()

    # Should have reset error count and created viz
    assert ctx3["error_count"] == 0, "Error count should reset after success"
    print(f"   ✓ Recovered: error_count = {ctx3['error_count']}")

    print("\n✅ Error and recovery test passed")
    return session


def test_multi_viz_same_data():
    """Test: Multiple visualizations from same data."""
    print("\n" + "="*70)
    print("TEST: Multiple Visualizations from Same Data")
    print("="*70)

    session = ConversationSession()

    # Generate data
    session.send("Generate 40 curves")
    ctx1 = session.get_context_summary()
    data_path = ctx1["current_data"]

    # Viz 1
    session.send("Show functional boxplot")
    ctx2 = session.get_context_summary()
    viz1 = ctx2["last_viz"]

    # Viz 2 from same data
    session.send("Now show curve boxplot with percentile 60")
    ctx3 = session.get_context_summary()
    viz2 = ctx3["last_viz"]

    assert ctx3["current_data"] == data_path, "Should still use same data"
    assert viz1 != viz2, "Should have different viz params"

    print(f"   ✓ Created 2 visualizations from {data_path}")
    print("\n✅ Multiple viz test passed")

    return session


def run_all_multiturn_tests():
    """Run all multi-turn conversation tests."""
    print("\n" + "💬"*35)
    print("CHATUVISBOX: MULTI-TURN CONVERSATION TESTS")
    print("💬"*35)

    tests = [
        test_sequential_operations,
        test_context_preservation,
        test_pronoun_reference,
        test_error_and_recovery_in_conversation,
        test_multi_viz_same_data,
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
    print("MULTI-TURN TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")

    input("\nPress Enter to close matplotlib windows...")
    plt.close('all')

    return passed, failed


if __name__ == "__main__":
    passed, failed = run_all_multiturn_tests()
    exit(0 if failed == 0 else 1)
```

Run:
```bash
python test_multiturn.py
```

### Task 6.3: Interactive Multi-Turn REPL

**File**: `repl.py` (preliminary version)

```python
"""
Interactive REPL for testing multi-turn conversations.

This is a basic version for Phase 6 testing.
Will be enhanced in Phase 8.
"""

from conversation import ConversationSession
import matplotlib.pyplot as plt


def print_banner():
    print("\n" + "="*70)
    print("  CHATUVISBOX - Interactive REPL")
    print("="*70)
    print("\nCommands:")
    print("  /context - Show current context")
    print("  /reset   - Reset conversation")
    print("  /quit    - Exit")
    print("="*70 + "\n")


def main():
    """Run interactive REPL."""
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
                print("🔄 Conversation reset")
                continue

            elif user_input == "/context":
                ctx = session.get_context_summary()
                print(f"\n📊 Context:")
                for key, value in ctx.items():
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
            print("\n\nInterrupted. Type /quit to exit.\n")
            continue

        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            continue


if __name__ == "__main__":
    main()
```

Run:
```bash
python repl.py
```

Test conversation:
```
You: Generate 30 curves
Assistant: [response]

You: Plot them
Assistant: [creates functional boxplot]

You: Change percentile to 90
Assistant: [recreates plot with new percentile]
```

## Validation Checklist

- [ ] Sequential operations work (generate → plot → modify)
- [ ] Context is preserved across turns (data_path, viz_params)
- [ ] Pronoun references work ("plot it", "change that")
- [ ] Error in middle of conversation doesn't break context
- [ ] Multiple visualizations can be created from same data
- [ ] Turn count is tracked correctly
- [ ] Session files are accumulated
- [ ] Interactive REPL allows continuous conversation
- [ ] `/context` command shows current state
- [ ] `/reset` command clears conversation

## Expected Conversation Patterns

### Pattern 1: Sequential Workflow
```
User: "Generate 30 curves"
Agent: "Generated 30 curves and saved to temp_ensemble_curves.npy"

User: "Plot them as functional boxplot"
Agent: "Created functional boxplot. The plot is now displayed."

User: "Use percentile 90 instead"
Agent: "Updated functional boxplot with percentile 90."
```

### Pattern 2: Implicit References
```
User: "Load sample_curves.csv"
Agent: "Loaded sample_curves.csv as numpy array."

User: "What shape is it?"
Agent: "The data has shape (50, 100) - 50 curves with 100 points each."

User: "Perfect, visualize it"
Agent: "Created functional boxplot visualization."
```

### Pattern 3: Multi-Viz Workflow
```
User: "Generate scalar field 40x40"
Agent: "Generated 40x40 scalar field ensemble."

User: "Show marching squares at 0.5"
Agent: "Created probabilistic marching squares visualization."

User: "Now try isovalue 0.7"
Agent: "Created new visualization with isovalue 0.7."
```

## Troubleshooting

**Context not preserved:**
- Check that state is passed correctly in ConversationSession
- Verify messages are appended, not replaced
- Print state between turns to debug

**Pronoun references don't work:**
- Improve system prompt with examples
- Ensure current_data_path is emphasized in prompt
- Check that model has enough context window

**REPL crashes:**
- Add try-except around session.send()
- Handle empty inputs
- Catch keyboard interrupts

## Output

After Phase 6, you should have:
- Working multi-turn conversation system
- Context preservation across turns
- Pronoun and implicit reference resolution
- Interactive REPL for testing
- Comprehensive multi-turn test suite

## Next Phase

Phase 7 will implement the hybrid control model for fast, direct parameter updates without going through the full LangGraph workflow.
