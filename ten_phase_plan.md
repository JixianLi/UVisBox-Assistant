# **ChatUVisBox: Project Plan (v5 \- Matplotlib MVP)**

## **1\. Project Goal & MVP Definition**

**Goal:** Create a local, natural language-driven application for the `UVisBox` Python library.

**MVP Scope (10 Phases):** A locally-run Python script that:

1. Accepts a natural language prompt from the user in a CLI.  
2. Uses **`LangGraph`** to manage a stateful, multi-step workflow.  
3. The `LangGraph` orchestrator uses the **Google `Gemini` API** for tool-calling and chat logic.  
4. The orchestrator has access to two distinct toolsets:  
   * **Data Tools:** A curated set of Python functions for loading/transforming **2D data** (e.g., `load_csv_as_2d_array`).  
   * **Vis Tools:** `UVisBox` functions that produce **2D visualizations** (e.g., `plot_2d_contour`).  
5. Executes multi-step tasks (e.g., "load this CSV, then show me its contour plot").  
6. Manages all intermediate data state via the **local file system** (e.g., as `.npy` files).  
7. Renders the final visualization in an **interactive Matplotlib window**.

   ## **2\. Confirmed Tech Stack**

* **Language:** Python  
* **Orchestration:** `LangGraph`  
* **NLI Engine:** **Google `Gemini` API** (via `google-generativeai` library)  
* **Core Libraries:** `UVisBox`  
* **Visualization:** **`matplotlib`**  
* **Data Tools:** `pandas`, `numpy`  
* **Tracing (Recommended):** `LangSmith`

  ---

  ## **3\. Milestone-by-Milestone Timeline**

  ### **Milestone 1: Core Pipeline Implementation (Phases 1-4)**

**Goal:** Build the essential `LangGraph` state machine capable of a single `Data Tool -> Vis Tool` chain.

* **Phase 1: Schemas & Dispatchers**  
  * Define the Python functions for your `data_tools` (file-in, `.npy`\-out) and `vis_tools` (`.npy`\-in, `matplotlib`\-out).  
  * Use the 3-Tier Parameter system from the start: define simple Tier-1 schemas for `Gemini` and hard-code Tier-2 defaults (e.g., `figsize`, `interpolation`) in your Python functions.  
* **Phase 2: LangGraph State & Nodes**  
  * Define your `GraphState` `TypedDict` (e.g., `messages`, `current_file_path`).  
  * Implement the core nodes: `call_model` (contacts `Gemini`), `call_data_tool`, and `call_vis_tool`.  
  * Ensure tool-calling nodes have robust `try...except` blocks that return a JSON-friendly `{"error": ...}` message on failure.  
* **Phase 3: Graph Wiring & Routing**  
  * Implement the conditional router logic that checks the `Gemini` response for tool calls (data or vis) and directs the graph to the correct node or to `END`.  
  * Set the `call_model` node as the entry point and wire the complete graph.  
* **Phase 4: End-to-End "Happy Path" Test**  
  * **Test Case:** `User:` "Load `my_data.csv` as a 2D array, then show me a heatmap."  
  * **Success:** Trace the graph: `call_model` \-\> `call_data_tool` \-\> `call_model` \-\> `call_vis_tool` \-\> `END`. A Matplotlib window appears.

    ---

    ### **Milestone 2: Robustness & Conversation (Phases 5-7)**

**Goal:** Make the agent "smart" by handling errors, context, and follow-up commands.

* **Phase 5: Error Handling & Contextual Awareness**  
  * Test the `try...except` blocks from Phase 2\. Confirm that when a tool returns an error, the graph loops back to `Gemini`, which then formulates a helpful, clarifying question to the user.  
  * Implement file system awareness: Before invoking the graph, scan `os.listdir()` and inject this file list into the *first* system prompt.  
* **Phase 6: Conversational Follow-up Test**  
  * Test a true multi-turn conversation.  
  * `User:` "Load `data.csv`."  
  * *(Graph runs: `model` \-\> `data_tool`. `current_file_path` is updated. Graph responds: "OK, data loaded.")*  
  * `User:` "Great, now show me the contour plot for that."  
  * **Success:** The graph uses its `messages` history and `current_file_path` state to correctly call `viz_tool(file_path="_temp_data.npy")`.  
* **Phase 7: Implement Hybrid Control Model**  
  * Implement the "pre-graph" logic in your main `main.py` REPL.  
  * If a user types a simple command (e.g., "colormap jet"), your script should intercept this, manually update the *last known* vis parameters, and call the `execute_vis_tool` dispatcher directly, bypassing the (slower) `LangGraph` call. This ensures a fast, interactive feel for simple tweaks.

    ---

    ### **Milestone 3: Polish & Finalization (Phases 8-10)**

**Goal:** Finalize the user experience and create a distributable MVP.

* **Phase 8: Session & Interaction Management**  
  * Ensure `plt.show(block=False)` is reliable, allowing the user to keep chatting after a plot appears.  
  * Create a `clear_session` tool and add it to your `data_tools`. This tool should `os.remove()` all `_temp_*.npy` files and reset the `GraphState`'s `current_file_path`.  
* **Phase 9: Final Testing & Bug Bash**  
  * Test with a variety of "failure chain" prompts (bad file paths, malformed CSVs, unknown colormaps). Ensure the `Gemini` response is helpful in every case.  
  * Test all hybrid control commands (Phase 7\) and session commands (Phase 8).  
* **Phase 10: Documentation & Packaging**  
  * Create the final `requirements.txt` file.  
  * Write a `README.md` that explains:  
    1. Installation and setting the **Google AI Studio API Key**.  
    2. A full list of available `data_tools` and `vis_tools`.  
    3. Example prompts (simple, multi-step, and error-correction).