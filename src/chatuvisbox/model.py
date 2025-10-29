"""Language model setup for ChatUVisBox"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from chatuvisbox import config
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
- functional_boxplot: For visualizing multiple 1D curves with band depth (supports multiple percentile bands, optional plot_all_curves flag to show raw curves)
- curve_boxplot: For ensemble curve data with depth-based coloring (supports multiple percentile bands)
- probabilistic_marching_squares: For 2D scalar field ensembles with isocontours
- contour_boxplot: For contour band depth from scalar field ensembles
- uncertainty_lobes: For visualizing directional uncertainty in vector fields (requires both positions_path and vectors_path)

Workflow:
1. User requests a visualization
2. Use data tools to load or generate the required data (saves as .npy)
3. IMMEDIATELY use visualization tools with the .npy file paths - do NOT ask for confirmation or additional parameters
4. Confirm success to user after visualization is complete

**Error Handling Guidelines:**
- If a tool returns an error, READ THE ERROR MESSAGE carefully
- Explain the error to the user in simple terms
- Ask clarifying questions if needed (e.g., "Which file did you mean?", "What dimensions?")
- Suggest alternatives if a file doesn't exist
- Don't retry the same failed operation without changes

**Context Awareness:**
- Remember the current_data_path from previous operations
- If user says "plot that" or "visualize it", use the current_data_path
- If user requests a different visualization type (e.g., "now show curve boxplot"), use current_data_path unless they explicitly mention new data
- Track what files have been created this session

Important:
- Always save intermediate data as .npy files
- Data tools return "output_path", "positions_path", and "vectors_path" fields - use these for visualization tools
- For uncertainty_lobes: use BOTH positions_path and vectors_path from generate_vector_field_ensemble output
- When data generation succeeds, IMMEDIATELY proceed to visualization without asking questions
- Use default parameters for visualizations unless user specifically requests different values
- Both functional_boxplot and curve_boxplot now support percentiles (list of floats) for multi-band visualization
- functional_boxplot has plot_all_curves parameter (default False) to optionally show all raw curves alongside the boxplot
- Be conversational and helpful
- Never make up file paths that don't exist
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
