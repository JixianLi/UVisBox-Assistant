# Phase 2: LangGraph State & Nodes

**Goal**: Define the graph state structure and implement the core nodes for the LangGraph workflow.

**Duration**: 1 day

## Prerequisites

- Phase 1 completed (data_tools.py, vis_tools.py, config.py working)
- Understanding of LangGraph concepts: State, Nodes, Edges

## Tasks

### Task 2.1: Define GraphState

**File**: `state.py`

```python
"""State definition for the LangGraph workflow"""
from typing import TypedDict, List, Optional, Annotated
from langchain_core.messages import BaseMessage
import operator


class GraphState(TypedDict):
    """
    State for the ChatUVisBox conversation graph.

    Attributes:
        messages: List of conversation messages (user, assistant, tool messages)
        current_data_path: Path to the most recently created/loaded .npy data file
        last_vis_params: Parameters used in the last visualization call (for hybrid control)
        session_files: List of temporary files created during this session
        error_count: Number of consecutive errors (for circuit breaking)
    """
    # Messages list - appended to over time
    messages: Annotated[List[BaseMessage], operator.add]

    # Single-value state fields (overwritten, not appended)
    current_data_path: Optional[str]
    last_vis_params: Optional[dict]
    session_files: List[str]
    error_count: int


def create_initial_state(user_message: str) -> GraphState:
    """
    Create the initial state for a new conversation turn.

    Args:
        user_message: The user's input message

    Returns:
        Initial GraphState
    """
    from langchain_core.messages import HumanMessage

    return GraphState(
        messages=[HumanMessage(content=user_message)],
        current_data_path=None,
        last_vis_params=None,
        session_files=[],
        error_count=0
    )


def update_state_with_data(state: GraphState, data_path: str) -> dict:
    """
    Update state after successful data tool execution.

    Returns:
        Dict of updates to merge into state
    """
    return {
        "current_data_path": data_path,
        "session_files": state["session_files"] + [data_path],
        "error_count": 0  # Reset error count on success
    }


def update_state_with_vis(state: GraphState, vis_params: dict) -> dict:
    """
    Update state after successful vis tool execution.

    Returns:
        Dict of updates to merge into state
    """
    return {
        "last_vis_params": vis_params,
        "error_count": 0  # Reset error count on success
    }


def increment_error_count(state: GraphState) -> dict:
    """
    Increment error count after tool failure.

    Returns:
        Dict of updates to merge into state
    """
    return {
        "error_count": state.get("error_count", 0) + 1
    }
```

**Test:**
```python
# test_state.py
from state import create_initial_state, update_state_with_data

state = create_initial_state("Load my_data.csv")
print(state)

updates = update_state_with_data(state, "/path/to/temp_data.npy")
print(updates)
```

### Task 2.2: Set Up LangChain Model with Gemini

**File**: `model.py`

```python
"""Language model setup for ChatUVisBox"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
import config
import os


def get_system_prompt(file_list: list = None) -> str:
    """
    Generate the system prompt for the agent.

    Args:
        file_list: List of available files in test_data directory

    Returns:
        System prompt string
    """
    base_prompt = """You are ChatUVisBox, an AI assistant specialized in visualizing uncertainty data using the UVisBox Python library.

Your capabilities:
1. **Data Tools**: Load CSV files, generate synthetic data, manage numpy arrays
2. **Visualization Tools**: Create uncertainty visualizations using UVisBox functions

Available visualization types:
- functional_boxplot: For visualizing multiple 1D curves with band depth
- curve_boxplot: For ensemble curve data with depth-based coloring
- probabilistic_marching_squares: For 2D scalar field ensembles with isocontours
- uncertainty_lobes: For visualizing directional uncertainty in vector fields

Workflow:
1. User requests a visualization
2. Use data tools to load or generate the required data (saves as .npy)
3. Use visualization tools with the .npy file path
4. Confirm success to user

Important:
- Always save intermediate data as .npy files
- Data tools return an "output_path" field - use this for visualization tools
- If a tool returns an error, ask the user for clarification
- Be conversational and helpful
"""

    if file_list:
        file_list_str = "\n".join([f"  - {f}" for f in file_list])
        base_prompt += f"\n\nAvailable files in test_data/:\n{file_list_str}"

    return base_prompt


def create_model_with_tools(tools: list, temperature: float = 0.0):
    """
    Create a ChatGoogleGenerativeAI model with tools bound.

    Args:
        tools: List of tool schemas (from data_tools and vis_tools)
        temperature: Model temperature (0 = deterministic)

    Returns:
        Model instance with tools bound
    """
    model = ChatGoogleGenerativeAI(
        model=config.MODEL_NAME,
        google_api_key=config.GEMINI_API_KEY,
        temperature=temperature,
    )

    # Bind tools using Gemini's function calling
    if tools:
        model_with_tools = model.bind_tools(tools)
        return model_with_tools

    return model


def prepare_messages_for_model(state: dict, file_list: list = None) -> list:
    """
    Prepare the full message list for the model, including system prompt.

    Args:
        state: Current graph state
        file_list: Available files to include in system prompt

    Returns:
        List of messages including system prompt
    """
    system_prompt = get_system_prompt(file_list)
    system_message = SystemMessage(content=system_prompt)

    # Prepend system message to conversation
    return [system_message] + state["messages"]
```

**Test:**
```python
# test_model.py
from model import get_system_prompt, create_model_with_tools
from data_tools import DATA_TOOL_SCHEMAS
from vis_tools import VIS_TOOL_SCHEMAS

# Test system prompt
prompt = get_system_prompt(["sample_curves.csv", "sample_scalar_field.npy"])
print(prompt)

# Test model creation
all_tools = DATA_TOOL_SCHEMAS + VIS_TOOL_SCHEMAS
model = create_model_with_tools(all_tools)
print(f"Model created: {model}")

# Test simple invocation (no tool call expected)
from langchain_core.messages import HumanMessage
response = model.invoke([HumanMessage(content="Hello, what can you do?")])
print(response.content)
```

### Task 2.3: Implement Graph Nodes

**File**: `nodes.py`

```python
"""Node implementations for the LangGraph workflow"""
from typing import Dict
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
import os

from state import GraphState, update_state_with_data, update_state_with_vis, increment_error_count
from model import create_model_with_tools, prepare_messages_for_model
from data_tools import DATA_TOOLS, DATA_TOOL_SCHEMAS
from vis_tools import VIS_TOOLS, VIS_TOOL_SCHEMAS
import config


# Create model with all tools
ALL_TOOL_SCHEMAS = DATA_TOOL_SCHEMAS + VIS_TOOL_SCHEMAS
MODEL = create_model_with_tools(ALL_TOOL_SCHEMAS)


def call_model(state: GraphState) -> Dict:
    """
    Node that calls the LLM to decide next action.

    Args:
        state: Current graph state

    Returns:
        Dict with messages to add to state
    """
    # Get list of available files for context
    file_list = []
    if config.TEST_DATA_DIR.exists():
        file_list = [f.name for f in config.TEST_DATA_DIR.iterdir() if f.is_file()]

    # Prepare messages with system prompt
    messages = prepare_messages_for_model(state, file_list)

    # Call model
    response = MODEL.invoke(messages)

    # Return as state update
    return {"messages": [response]}


def call_data_tool(state: GraphState) -> Dict:
    """
    Node that executes a data tool based on the last AI message.

    Args:
        state: Current graph state

    Returns:
        Dict with tool result message and state updates
    """
    last_message = state["messages"][-1]

    # Extract tool call from AI message
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        raise ValueError("call_data_tool invoked but no tool_calls in last message")

    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    tool_call_id = tool_call["id"]

    print(f"[DATA TOOL] Calling {tool_name} with args: {tool_args}")

    # Execute tool with error handling
    try:
        if tool_name not in DATA_TOOLS:
            result = {
                "status": "error",
                "message": f"Unknown data tool: {tool_name}"
            }
        else:
            tool_func = DATA_TOOLS[tool_name]
            result = tool_func(**tool_args)

        print(f"[DATA TOOL] Result: {result}")

        # Create tool message
        tool_message = ToolMessage(
            content=str(result),
            tool_call_id=tool_call_id
        )

        # Update state if successful
        state_updates = {"messages": [tool_message]}

        if result.get("status") == "success" and "output_path" in result:
            state_updates.update(update_state_with_data(state, result["output_path"]))
        else:
            state_updates.update(increment_error_count(state))

        return state_updates

    except Exception as e:
        print(f"[DATA TOOL] Exception: {e}")
        error_result = {
            "status": "error",
            "message": f"Exception in {tool_name}: {str(e)}"
        }

        tool_message = ToolMessage(
            content=str(error_result),
            tool_call_id=tool_call_id
        )

        return {
            "messages": [tool_message],
            **increment_error_count(state)
        }


def call_vis_tool(state: GraphState) -> Dict:
    """
    Node that executes a visualization tool.

    Args:
        state: Current graph state

    Returns:
        Dict with tool result message and state updates
    """
    last_message = state["messages"][-1]

    # Extract tool call
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        raise ValueError("call_vis_tool invoked but no tool_calls in last message")

    tool_call = last_message.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    tool_call_id = tool_call["id"]

    print(f"[VIS TOOL] Calling {tool_name} with args: {tool_args}")

    # Execute tool
    try:
        if tool_name not in VIS_TOOLS:
            result = {
                "status": "error",
                "message": f"Unknown vis tool: {tool_name}"
            }
        else:
            tool_func = VIS_TOOLS[tool_name]
            result = tool_func(**tool_args)

        print(f"[VIS TOOL] Result: {result}")

        # Create tool message
        tool_message = ToolMessage(
            content=str(result),
            tool_call_id=tool_call_id
        )

        # Update state
        state_updates = {"messages": [tool_message]}

        if result.get("status") == "success":
            state_updates.update(update_state_with_vis(state, tool_args))
        else:
            state_updates.update(increment_error_count(state))

        return state_updates

    except Exception as e:
        print(f"[VIS TOOL] Exception: {e}")
        error_result = {
            "status": "error",
            "message": f"Exception in {tool_name}: {str(e)}"
        }

        tool_message = ToolMessage(
            content=str(error_result),
            tool_call_id=tool_call_id
        )

        return {
            "messages": [tool_message],
            **increment_error_count(state)
        }
```

**Test:**
```python
# test_nodes.py
from nodes import call_model, call_data_tool
from state import create_initial_state
from langchain_core.messages import AIMessage
from unittest.mock import Mock

# Test call_model
state = create_initial_state("Generate some test curves")
result = call_model(state)
print("Model response:")
print(result["messages"][0])

# Test that model outputs tool calls
if hasattr(result["messages"][0], "tool_calls"):
    print(f"\nTool calls: {result['messages'][0].tool_calls}")
```

### Task 2.4: Create Tool Dispatcher Utilities

**File**: `utils.py`

```python
"""Utility functions for the ChatUVisBox pipeline"""
from typing import Dict, Optional
from pathlib import Path
import config


def is_data_tool(tool_name: str) -> bool:
    """Check if a tool name corresponds to a data tool."""
    from data_tools import DATA_TOOLS
    return tool_name in DATA_TOOLS


def is_vis_tool(tool_name: str) -> bool:
    """Check if a tool name corresponds to a vis tool."""
    from vis_tools import VIS_TOOLS
    return tool_name in VIS_TOOLS


def get_tool_type(tool_name: str) -> Optional[str]:
    """
    Determine the type of tool.

    Returns:
        "data", "vis", or None if unknown
    """
    if is_data_tool(tool_name):
        return "data"
    elif is_vis_tool(tool_name):
        return "vis"
    return None


def cleanup_temp_files():
    """Remove all temporary .npy files from the temp directory."""
    if not config.TEMP_DIR.exists():
        return

    count = 0
    for file in config.TEMP_DIR.glob(f"{config.TEMP_FILE_PREFIX}*{config.TEMP_FILE_EXTENSION}"):
        file.unlink()
        count += 1

    print(f"Cleaned up {count} temporary files")


def get_available_files() -> list:
    """Get list of available files in test_data directory."""
    if not config.TEST_DATA_DIR.exists():
        return []

    return [f.name for f in config.TEST_DATA_DIR.iterdir() if f.is_file()]


def format_file_list(files: list) -> str:
    """Format a file list for display."""
    if not files:
        return "No files available"

    return "\n".join([f"  - {f}" for f in files])
```

**Test:**
```python
# test_utils.py
from utils import is_data_tool, is_vis_tool, get_tool_type, get_available_files

print(is_data_tool("load_csv_to_numpy"))  # True
print(is_vis_tool("plot_functional_boxplot"))  # True
print(get_tool_type("load_csv_to_numpy"))  # "data"
print(get_tool_type("unknown_tool"))  # None

print(get_available_files())
```

## Validation Checklist

- [x] `state.py` defines `GraphState` TypedDict with all required fields
- [x] `state.py` helper functions work correctly
- [x] `model.py` creates ChatGoogleGenerativeAI model successfully
- [x] `model.py` binds tools to model without errors
- [x] System prompt includes file list when provided
- [x] `nodes.py` `call_model` node returns AIMessage with tool_calls
- [x] `nodes.py` `call_data_tool` executes data tools and updates state
- [x] `nodes.py` `call_vis_tool` executes vis tools and updates state
- [x] Error handling in tool nodes catches exceptions and returns error messages
- [x] `utils.py` correctly identifies tool types
- [x] All modules import without errors

**Phase 2 Status**: ✅ COMPLETE (2025-10-26)
- All 4 modules implemented and tested
- Comprehensive test suite passing (test_phase2.py)
- All validation criteria met

## Testing Strategy

Run each test file:
```bash
python test_state.py
python test_model.py
python test_nodes.py
python test_utils.py
```

Expected outcomes:
- State updates correctly after data/vis operations
- Model generates tool calls when prompted for data/vis tasks
- Nodes execute tools and return properly formatted messages
- Errors are caught and formatted as tool messages

## Output

After Phase 2, you should have:
- Complete state management system
- LLM model configured with Gemini and tools bound
- Three core nodes: `call_model`, `call_data_tool`, `call_vis_tool`
- Utility functions for tool dispatching
- All components tested individually

## Next Phase

Phase 3 will wire these nodes together into a complete graph with conditional routing logic.
