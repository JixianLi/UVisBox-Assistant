# UVisBox-Assistant API Documentation

## Table of Contents

1. [Visualization Tools](#visualization-tools)
2. [Data Generation Tools](#data-generation-tools)
3. [Statistics Tools](#statistics-tools) **(v0.3.0)**
4. [Analyzer Tools](#analyzer-tools) **(v0.3.0)**
5. [Command Parser](#command-parser)
6. [Configuration](#configuration)

## Visualization Tools

### plot_functional_boxplot

Create a functional boxplot visualization with BoxplotStyleConfig styling.

**Signature**:
```python
plot_functional_boxplot(
    data_path: str,
    percentiles: Optional[List[float]] = None,
    percentile_colormap: str = "viridis",
    show_median: bool = True,
    median_color: str = "red",
    median_width: float = 3.0,
    median_alpha: float = 1.0,
    show_outliers: bool = False,
    outliers_color: str = "gray",
    outliers_width: float = 1.0,
    outliers_alpha: float = 0.5,
    method: str = "fbd"
) -> Dict[str, Any]
```

**Parameters**:
- `data_path` (str): Path to .npy file with shape (n_curves, n_points)
- `percentiles` (List[float], optional): Percentiles for bands (default: [25, 50, 90, 100])
- `percentile_colormap` (str): Colormap for percentile bands (default: "viridis")
- `show_median` (bool): Whether to show median curve (default: True)
- `median_color` (str): Color of median curve (default: "red")
- `median_width` (float): Width of median curve line (default: 3.0)
- `median_alpha` (float): Alpha transparency of median (default: 1.0, range: 0.0-1.0)
- `show_outliers` (bool): Whether to show outlier curves (default: False)
- `outliers_color` (str): Color of outlier curves (default: "gray")
- `outliers_width` (float): Width of outlier curves (default: 1.0)
- `outliers_alpha` (float): Alpha transparency of outliers (default: 0.5, range: 0.0-1.0)
- `method` (str): Band depth method - 'fbd' (functional band depth) or 'mfbd' (modified functional band depth) (default: 'fbd')

**Returns**: Dict with:
- `status` (str): "success" or "error"
- `message` (str): Human-readable message
- `_vis_params` (dict): All visualization parameters for hybrid control

**Example**:
```python
from uvisbox_assistant.vis_tools import plot_functional_boxplot
from uvisbox_assistant.data_tools import generate_ensemble_curves

# Generate data
result = generate_ensemble_curves(n_curves=30, n_points=100)

# Create customized visualization
plot_functional_boxplot(
    data_path=result['output_path'],
    percentiles=[25, 50, 75, 90],
    percentile_colormap='plasma',
    show_median=True,
    median_color='blue',
    median_width=2.5,
    median_alpha=0.9,
    show_outliers=True,
    outliers_color='black',
    outliers_width=1.5,
    outliers_alpha=0.7
)
```

---

### plot_curve_boxplot

Create a curve boxplot with BoxplotStyleConfig and parallel processing.

**Signature**:
```python
plot_curve_boxplot(
    data_path: str,
    percentiles: Optional[List[float]] = None,
    percentile_colormap: str = "viridis",
    show_median: bool = True,
    median_color: str = "red",
    median_width: float = 3.0,
    median_alpha: float = 1.0,
    show_outliers: bool = False,
    outliers_color: str = "gray",
    outliers_width: float = 1.0,
    outliers_alpha: float = 0.5,
    workers: int = 12
) -> Dict[str, Any]
```

**Additional Parameters**:
- `workers` (int): Number of parallel workers for band depth computation (default: 12)

**Performance Notes**:
- Band depth computation is CPU-intensive
- Adjust `workers` based on available CPU cores
- Typical values: 4-16 workers
- More workers = faster for large ensembles (>50 members)

**Example**:
```python
# Fast processing on multi-core system
plot_curve_boxplot(
    data_path=curves_path,
    percentiles=[50, 90],
    workers=16,  # Use 16 threads
    show_outliers=True
)
```

---

### plot_contour_boxplot

Create contour boxplot from scalar field ensemble.

**Signature**:
```python
plot_contour_boxplot(
    data_path: str,
    isovalue: float,
    percentiles: Optional[List[float]] = None,
    percentile_colormap: str = "viridis",
    show_median: bool = True,
    median_color: str = "red",
    median_width: float = 3.0,
    median_alpha: float = 1.0,
    show_outliers: bool = False,
    outliers_color: str = "gray",
    outliers_width: float = 1.0,
    outliers_alpha: float = 0.5,
    workers: int = 12
) -> Dict[str, Any]
```

**Additional Parameters**:
- `isovalue` (float): **Required**. Threshold for binary contour extraction
- `workers` (int): Number of parallel workers (default: 12)

**Example**:
```python
plot_contour_boxplot(
    data_path=field_path,
    isovalue=0.5,
    percentiles=[25, 50, 75],
    median_color='blue',
    show_outliers=True,
    outliers_color='gray',
    workers=8
)
```

---

### probabilistic_marching_squares

Visualize 2D scalar field uncertainty using probabilistic marching squares.

**Signature**:
```python
probabilistic_marching_squares(
    data_path: str,
    isovalue: float,
    colormap: str = "viridis"
) -> Dict[str, Any]
```

**Parameters**:
- `data_path` (str): Path to .npy file with shape (ny, nx, n_ensemble)
- `isovalue` (float): **Required**. Threshold for contour extraction
- `colormap` (str): Matplotlib colormap name (default: "viridis")

**Returns**: Dict with status, message, and _vis_params

**Example**:
```python
from uvisbox_assistant.vis_tools import probabilistic_marching_squares
from uvisbox_assistant.data_tools import generate_scalar_field_ensemble

# Generate 2D scalar field
result = generate_scalar_field_ensemble(nx=50, ny=50, n_ensemble=30)

# Visualize uncertainty
probabilistic_marching_squares(
    data_path=result['output_path'],
    isovalue=0.5,
    colormap='plasma'
)
```

---

### plot_uncertainty_lobes

Visualize directional uncertainty for vector field ensembles.

**Signature**:
```python
plot_uncertainty_lobes(
    positions_path: str,
    vectors_path: str,
    percentile1: int = 90,
    percentile2: int = 50,
    scale: float = 0.2,
    workers: Optional[int] = None
) -> Dict[str, Any]
```

**Parameters**:
- `positions_path` (str): Path to .npy file with positions array (shape: (n_points, 2))
- `vectors_path` (str): Path to .npy file with vectors array (shape: (n_points, 2, n_ensemble))
- `percentile1` (int): Outer percentile for lobe extent (default: 90, range: 0-100)
- `percentile2` (int): Inner percentile for lobe extent (default: 50, range: 0-100)
- `scale` (float): Scaling factor for glyph size (default: 0.2)
- `workers` (Optional[int]): Number of parallel workers for band depth computation (default: None, optimized for large data only)

**Note**: percentile1 should be > percentile2 for meaningful visualization

**Example**:
```python
from uvisbox_assistant.vis_tools import plot_uncertainty_lobes
from uvisbox_assistant.data_tools import generate_vector_field_ensemble

# Generate vector field
result = generate_vector_field_ensemble(x_res=10, y_res=10, n_instances=30)

# Visualize directional uncertainty
plot_uncertainty_lobes(
    positions_path=result['positions_path'],
    vectors_path=result['vectors_path'],
    percentile1=95,
    percentile2=50,
    scale=0.3
)
```

---

### plot_squid_glyph_2D

Visualize 2D vector field uncertainty using squid-shaped glyphs with depth-based filtering.

**Signature**:
```python
plot_squid_glyph_2D(
    vectors_path: str,
    positions_path: str,
    percentile: float = 95,
    scale: float = 0.2,
    workers: Optional[int] = None
) -> Dict[str, Any]
```

**Parameters**:
- `vectors_path` (str): Path to .npy file with ensemble vectors (shape: (n_points, 2, n_ensemble))
- `positions_path` (str): Path to .npy file with glyph positions (shape: (n_points, 2))
- `percentile` (float): Percentile of ensemble members to include based on depth ranking (0-100, default: 95). Higher values include more vectors showing more variation.
- `scale` (float): Scale factor for glyph size (default: 0.2)
- `workers` (Optional[int]): Number of parallel workers for computation (default: None)

**Returns**: Dict with status, message, and _vis_params

**Example**:
```python
from uvisbox_assistant.vis_tools import plot_squid_glyph_2D
from uvisbox_assistant.data_tools import generate_vector_field_ensemble

# Generate vector field
result = generate_vector_field_ensemble(x_res=10, y_res=10, n_instances=30)

# Visualize with squid glyphs
plot_squid_glyph_2D(
    vectors_path=result['vectors_path'],
    positions_path=result['positions_path'],
    percentile=95,
    scale=0.3
)
```

**Note**: Squid glyphs use depth-based filtering with a single percentile parameter, unlike uncertainty_lobes which uses two percentiles for inner/outer bands.

---

## Data Generation Tools

### generate_ensemble_curves

Generate synthetic 1D curve ensembles with controlled variation.

**Signature**:
```python
generate_ensemble_curves(
    n_curves: int = 30,
    n_points: int = 100
) -> Dict[str, Any]
```

**Parameters**:
- `n_curves` (int): Number of curves in ensemble (default: 30)
- `n_points` (int): Number of points per curve (default: 100)

**Returns**: Dict with:
- `status` (str): "success" or "error"
- `message` (str): Human-readable message
- `output_path` (str): Path to saved .npy file
- `shape` (tuple): Data shape (n_curves, n_points)

**Example**:
```python
result = generate_ensemble_curves(n_curves=50, n_points=200)
print(f"Generated data: {result['shape']}")
print(f"Saved to: {result['output_path']}")
```

---

### generate_scalar_field_ensemble

Generate 2D scalar field ensembles with systematic uncertainty.

**Signature**:
```python
generate_scalar_field_ensemble(
    nx: int = 50,
    ny: int = 50,
    n_ensemble: int = 30
) -> Dict[str, Any]
```

**Parameters**:
- `nx` (int): Grid resolution in x direction (default: 50)
- `ny` (int): Grid resolution in y direction (default: 50)
- `n_ensemble` (int): Number of ensemble members (default: 30)

**Returns**: Dict with:
- `status`, `message`, `output_path`
- `shape` (tuple): Data shape (ny, nx, n_ensemble)

**Example**:
```python
result = generate_scalar_field_ensemble(nx=100, ny=100, n_ensemble=50)
```

---

### generate_vector_field_ensemble

Generate 2D vector field ensembles with directional and magnitude variation.

**Signature**:
```python
generate_vector_field_ensemble(
    x_res: int = 10,
    y_res: int = 10,
    n_instances: int = 30,
    initial_direction: float = 0.0,
    initial_magnitude: float = 1.0
) -> Dict[str, Any]
```

**Parameters**:
- `x_res` (int): Grid resolution in x direction (default: 10)
- `y_res` (int): Grid resolution in y direction (default: 10)
- `n_instances` (int): Number of ensemble members (default: 30)
- `initial_direction` (float): Base direction in radians (default: 0.0)
- `initial_magnitude` (float): Base magnitude (default: 1.0)

**Returns**: Dict with:
- `status`, `message`
- `positions_path` (str): Path to positions array
- `vectors_path` (str): Path to vectors array
- `positions_shape`, `vectors_shape`

**Example**:
```python
result = generate_vector_field_ensemble(
    x_res=15,
    y_res=15,
    n_instances=50,
    initial_direction=np.pi/4  # 45 degrees
)
```

---

### load_csv_to_numpy

Load CSV data and convert to NumPy array.

**Signature**:
```python
load_csv_to_numpy(
    file_path: str
) -> Dict[str, Any]
```

**Parameters**:
- `file_path` (str): Path to CSV file

**Returns**: Dict with status, message, output_path, and shape

**Example**:
```python
result = load_csv_to_numpy("test_data/sample_curves.csv")
```

---

### load_npy

Load existing .npy file.

**Signature**:
```python
load_npy(
    file_path: str
) -> Dict[str, Any]
```

**Parameters**:
- `file_path` (str): Path to .npy file

**Returns**: Dict with status, message, output_path, and shape

**Example**:
```python
result = load_npy("temp/my_data.npy")
```

---

## Statistics Tools

**(v0.3.0)** Statistical analysis module for uncertainty quantification.

### compute_functional_boxplot_statistics

Compute comprehensive statistical summaries from functional boxplot data using UVisBox integration.

**Signature**:
```python
compute_functional_boxplot_statistics(
    data_path: str,
    method: str = "fbd"
) -> Dict[str, Any]
```

**Parameters**:
- `data_path` (str): Path to .npy file with shape (n_curves, n_points)
- `method` (str): Band depth method - 'fbd' (functional band depth) or 'mfbd' (modified functional band depth) (default: 'fbd')

**Returns**: Dict with:
- `status` (str): "success" or "error"
- `message` (str): Human-readable message
- `processed_statistics` (dict): Structured numerical summaries (JSON-serializable, no numpy arrays)
  - `data_shape`: Dict with n_curves and n_points
  - `median`: Dict with trend, slope, fluctuation, smoothness, value_range, mean_value, std_value
  - `bands`: Dict with band_widths, widest_regions, overall_uncertainty_score, num_bands
  - `outliers`: Dict with count, median_similarity_mean, median_similarity_std, intra_outlier_similarity, outlier_percentage
  - `method`: Band depth method used
- `_raw_statistics` (dict): Original UVisBox output for debugging (lists, not numpy arrays)

**Median Analysis Metrics**:
- **trend**: Overall direction ("increasing" | "decreasing" | "stationary")
- **overall_slope**: Linear regression slope (positive/negative/~0)
- **fluctuation_level**: Standard deviation normalized by range
- **smoothness_score**: Inverse of gradient variability (0-1, higher = smoother)
- **value_range**: Tuple (min, max) of median values
- **mean_value**: Mean of median curve
- **std_value**: Standard deviation of median curve

**Band Analysis Metrics**:
- **band_widths**: Dict with mean/max/min/std widths per band
- **widest_regions**: List of (start, end) index tuples for top 10% widths
- **overall_uncertainty_score**: Mean normalized band width (0-1, higher = more uncertain)
- **num_bands**: Number of percentile bands

**Outlier Analysis Metrics**:
- **count**: Number of outliers (depth < Q1 - 1.5×IQR)
- **median_similarity_mean**: Mean Pearson correlation with median
- **median_similarity_std**: Standard deviation of correlations
- **intra_outlier_similarity**: Mean pairwise correlation among outliers
- **outlier_percentage**: Outliers as percentage of total curves

**Important**: Outliers use depth-based detection (Q1 - 1.5×IQR), NOT percentile position. See [ANALYSIS_EXAMPLES.md](ANALYSIS_EXAMPLES.md#understanding-outlier-detection) for clarification.

**Example**:
```python
from uvisbox_assistant.statistics_tools import compute_functional_boxplot_statistics
from uvisbox_assistant.data_tools import generate_ensemble_curves

# Generate data
result = generate_ensemble_curves(n_curves=50, n_points=100)

# Compute statistics
stats_result = compute_functional_boxplot_statistics(
    data_path=result['output_path'],
    method='fbd'
)

# Access processed statistics
stats = stats_result['processed_statistics']
print(f"Median trend: {stats['median']['trend']}")
print(f"Overall uncertainty: {stats['bands']['overall_uncertainty_score']:.2f}")
print(f"Outliers: {stats['outliers']['count']}")
```

**Sequential Workflow**:
This function must be called **before** `generate_uncertainty_report()`. Statistics are stored in GraphState and automatically injected into the analyzer tool.

---

## Analyzer Tools

**(v0.3.0)** LLM-powered report generation module for natural language uncertainty analysis.

### generate_uncertainty_report

Generate natural language uncertainty analysis reports from statistical summaries.

**Signature**:
```python
generate_uncertainty_report(
    processed_statistics: dict,
    analysis_type: str = "quick"
) -> Dict[str, Any]
```

**Parameters**:
- `processed_statistics` (dict): Structured statistics from `compute_functional_boxplot_statistics`
  - **Note**: In agent workflow, this is automatically injected from GraphState. Users don't pass this manually.
- `analysis_type` (str): Report format - "inline" | "quick" | "detailed" (default: "quick")

**Report Formats**:

**1. Inline** (1 sentence, ~15-30 words):
- Concise summary of overall uncertainty level
- Mentions key metrics (low/moderate/high uncertainty)
- Example: "This ensemble shows moderate uncertainty with 15% band width variation and 2 outliers."

**2. Quick** (3-5 sentences, ~50-100 words):
- Brief overview covering main characteristics
- Structure: overall assessment, median behavior, band characteristics, outliers
- Example:
  > "The ensemble exhibits moderate uncertainty with 30 curves showing consistent trends. The median curve displays an increasing trend with a slope of 0.05 and smooth behavior. Percentile bands show an average width of 1.2 units with widest regions near indices 45-55. Two outliers were detected with 65% similarity to the median curve."

**3. Detailed** (Full report, ~100-300 words):
- Comprehensive analysis with structured sections
- Sections: Median Behavior, Band Characteristics, Outlier Analysis, Overall Assessment
- Includes specific numbers and metrics from all summaries

**Returns**: Dict with:
- `status` (str): "success" or "error"
- `message` (str): Confirmation message with word count
- `report` (str): Generated natural language report
- `analysis_type` (str): Echo of requested format

**LLM Configuration**:
- Model: `gemini-2.0-flash-lite` (cost-effective)
- Temperature: 0.3 (mostly deterministic, slight creativity for natural language)
- Validation: Word count checks per format
- Constraint: Descriptive only, no recommendations or prescriptions

**Example (Direct Call)**:
```python
from uvisbox_assistant.analyzer_tools import generate_uncertainty_report
from uvisbox_assistant.statistics_tools import compute_functional_boxplot_statistics

# Compute statistics first
stats_result = compute_functional_boxplot_statistics(data_path)
stats = stats_result['processed_statistics']

# Generate report
report_result = generate_uncertainty_report(
    processed_statistics=stats,
    analysis_type='detailed'
)

print(report_result['report'])
```

**Example (Agent Workflow)**:
```python
from uvisbox_assistant.conversation import ConversationSession

session = ConversationSession()

# Statistics are computed and stored automatically
session.send("Generate 50 curves and compute statistics")

# Analyzer automatically uses statistics from state
session.send("Create a detailed uncertainty report")
# Report is generated and presented to user
```

**Tool Sequence (REQUIRED)**:
1. FIRST: Call `compute_functional_boxplot_statistics` with data_path
2. THEN: Call `generate_uncertainty_report` with analysis_type
3. FINALLY: Model presents report to user

The system prompt enforces this sequence. Skipping statistics will result in an error: "No statistics available. Please run compute_functional_boxplot_statistics first."

**State Injection Pattern**:
In the LangGraph workflow, the `call_analyzer_tool` node automatically injects `processed_statistics` from GraphState into the tool arguments. This pattern:
- Separates concerns (statistics computation vs. report generation)
- Enables cost efficiency (statistics computed once, multiple reports generated)
- Provides clear error messages when statistics missing
- Prevents model from attempting to construct statistics manually

---

## Command Parser

### Supported Hybrid Commands

The command parser recognizes 16 fast-path commands for instant parameter updates:

#### Basic Parameters
1. `colormap <name>` → Updates colormap/percentile_colormap
2. `percentile <number>` → Updates percentiles
3. `isovalue <number>` → Updates isovalue
4. `show median` → Sets show_median=True
5. `hide median` → Sets show_median=False
6. `show outliers` → Sets show_outliers=True
7. `hide outliers` → Sets show_outliers=False

#### Median Styling
8. `median color <color>` → Updates median_color
9. `median width <number>` → Updates median_width
10. `median alpha <number>` → Updates median_alpha

#### Outliers Styling
11. `outliers color <color>` → Updates outliers_color
12. `outliers width <number>` → Updates outliers_width
13. `outliers alpha <number>` → Updates outliers_alpha

#### Other
14. `scale <number>` → Updates scale (for uncertainty_lobes)
15. `alpha <number>` → Updates general alpha
16. `method <fbd|mfbd>` → Updates method (for functional_boxplot: 'fbd' = functional band depth, 'mfbd' = modified functional band depth)

### Usage

```python
from uvisbox_assistant.command_parser import parse_simple_command

cmd = parse_simple_command("median color blue")
# Returns: SimpleCommand(median_color='blue')

cmd = parse_simple_command("outliers alpha 0.8")
# Returns: SimpleCommand(outliers_alpha=0.8)

cmd = parse_simple_command("make it look better")
# Returns: None (not a simple command, needs LLM)
```

### SimpleCommand Dataclass

```python
@dataclass
class SimpleCommand:
    """Represents a parsed simple command."""

    # Basic parameters
    percentile: Optional[float] = None
    isovalue: Optional[float] = None
    colormap: Optional[str] = None

    # Median styling
    show_median: Optional[bool] = None
    median_color: Optional[str] = None
    median_width: Optional[float] = None
    median_alpha: Optional[float] = None

    # Outliers styling
    show_outliers: Optional[bool] = None
    outliers_color: Optional[str] = None
    outliers_width: Optional[float] = None
    outliers_alpha: Optional[float] = None

    # Other
    scale: Optional[float] = None
    alpha: Optional[float] = None
```

---

## Configuration

### DEFAULT_VIS_PARAMS

Default visualization parameters in `config.py`:

```python
DEFAULT_VIS_PARAMS = {
    # General figure settings
    "figsize": (10, 8),
    "dpi": 100,

    # BoxplotStyleConfig defaults
    "percentiles": [25, 50, 90, 100],
    "percentile_colormap": "viridis",
    "show_median": True,
    "median_color": "red",
    "median_width": 3.0,
    "median_alpha": 1.0,
    "show_outliers": False,
    "outliers_color": "gray",
    "outliers_width": 1.0,
    "outliers_alpha": 0.5,

    # Parallel computation
    "workers": 12,

    # Probabilistic marching squares
    "isovalue": 0.5,
    "colormap": "viridis",

    # Uncertainty lobes
    "percentile1": 90,
    "percentile2": 50,
    "scale": 0.2,
}
```

### Environment Variables

```python
# Required
GEMINI_API_KEY  # Google Gemini API key for LLM

# Optional (set in config.py)
TEMP_DIR        # Directory for temporary files (default: "temp/")
TEST_DATA_DIR   # Directory for test data (default: "test_data/")
LOGS_DIR        # Directory for log files (default: "logs/")
```

---

## Error Tracking Module

### ErrorRecord

**File**: `src/uvisbox_assistant/error_tracking.py`

Dataclass for storing error information with full traceback.

**Class Definition:**
```python
@dataclass
class ErrorRecord:
    error_id: int
    timestamp: datetime
    tool_name: str
    error_type: str
    error_message: str
    full_traceback: str
    user_facing_message: str
    auto_fixed: bool
    context: Optional[Dict] = None
```

**Methods:**

- **`summary() -> str`**

  Returns a one-line summary suitable for error list display.

  **Example Output:**
  ```
  [3] 10:23:45 - plot_functional_boxplot: ValueError (failed)
  ```

- **`detailed() -> str`**

  Returns a detailed multi-line description with full traceback.

  **Example Output:**
  ```
  Error ID: 3
  Timestamp: 2025-01-30T10:23:45.123456
  Tool: plot_functional_boxplot
  Type: ValueError
  Message: Invalid colormap name 'Reds'
  ...
  Full Traceback:
  [full traceback here]
  ```

### ConversationSession - Error Tracking Methods

**File**: `src/uvisbox_assistant/conversation.py`

**New Attributes:**

- **`debug_mode: bool`** - Whether debug mode is enabled (default: False)
- **`verbose_mode: bool`** - Whether verbose mode is enabled (default: False)
- **`error_history: List[ErrorRecord]`** - List of recorded errors (max 20)
- **`max_error_history: int`** - Maximum errors to keep (default: 20)

**New Methods:**

- **`record_error(tool_name: str, error: Exception, traceback_str: str, user_message: str, auto_fixed: bool = False, context: Optional[Dict] = None) -> ErrorRecord`**

  Record an error in the error history.

  **Parameters:**
  - `tool_name`: Name of the tool that failed
  - `error`: The exception object
  - `traceback_str`: Full traceback from `traceback.format_exc()`
  - `user_message`: User-friendly error message
  - `auto_fixed`: Whether error was automatically fixed
  - `context`: Optional context dictionary

  **Returns:** ErrorRecord object

  **Example:**
  ```python
  record = session.record_error(
      tool_name="plot_functional_boxplot",
      error=ValueError("Invalid colormap"),
      traceback_str=traceback.format_exc(),
      user_message="Colormap error: Invalid colormap 'Reds'"
  )
  ```

- **`get_error(error_id: int) -> Optional[ErrorRecord]`**

  Retrieve error by ID.

  **Parameters:**
  - `error_id`: ID of error to retrieve

  **Returns:** ErrorRecord or None if not found

- **`get_last_error() -> Optional[ErrorRecord]`**

  Get the most recent error.

  **Returns:** ErrorRecord or None if no errors

- **`mark_error_auto_fixed(error_id: int) -> None`**

  Mark an error as automatically fixed by the agent.

  **Parameters:**
  - `error_id`: ID of error to mark as auto-fixed

- **`is_error_auto_fixed(error_id: int) -> bool`**

  Check if an error was automatically fixed.

  **Parameters:**
  - `error_id`: ID of error to check

  **Returns:** True if error was auto-fixed, False otherwise

## Output Control Module

### Output Control Functions

**File**: `src/uvisbox_assistant/output_control.py`

Functions for controlling verbose output based on session settings.

**Functions:**

- **`set_session(session: ConversationSession) -> None`**

  Register the current session for verbose mode checks.

  **Note:** Automatically called by ConversationSession.__init__()

- **`vprint(message: str, force: bool = False) -> None`**

  Print message only if verbose mode is enabled.

  **Parameters:**
  - `message`: Message to print
  - `force`: If True, always print regardless of verbose mode

  **Example:**
  ```python
  vprint("[DATA TOOL] Calling generate_curves")  # Only if verbose
  vprint("✅ Success!", force=True)  # Always print
  ```

- **`is_verbose() -> bool`**

  Check if verbose mode is enabled.

  **Returns:** True if verbose mode is on, False otherwise

## Error Interpretation Module

### Error Interpretation Functions

**File**: `src/uvisbox_assistant/error_interpretation.py`

Functions for interpreting and enhancing error messages.

**Functions:**

- **`interpret_uvisbox_error(error: Exception, traceback_str: str, debug_mode: bool = False) -> Tuple[str, Optional[str]]`**

  Interpret UVisBox errors and provide helpful context.

  **Parameters:**
  - `error`: The exception object
  - `traceback_str`: Full traceback string
  - `debug_mode`: Whether debug mode is enabled

  **Returns:** Tuple of (user_message, debug_hint)
  - `debug_hint` is None if debug mode is OFF

  **Supported Error Patterns:**
  - Colormap errors (e.g., "Invalid colormap 'Reds'")
  - Method validation errors (e.g., "Unknown method 'fbd'")
  - Shape mismatch errors
  - File not found errors
  - Import errors (UVisBox not installed)

  **Example:**
  ```python
  error = ValueError("Invalid colormap name 'Reds'")
  traceback = "...matplotlib..."

  msg, hint = interpret_uvisbox_error(error, traceback, debug_mode=True)
  # msg: "Colormap error: Invalid colormap name 'Reds'"
  # hint: "The colormap 'Reds' may be valid in matplotlib..."
  ```

- **`format_error_with_hint(user_message: str, hint: Optional[str]) -> str`**

  Format error message with optional debug hint.

  **Parameters:**
  - `user_message`: Main error message
  - `hint`: Optional debug hint

  **Returns:** Formatted error message

  **Example:**
  ```python
  formatted = format_error_with_hint("Error occurred", "This is a hint")
  # Returns: "Error occurred\n💡 Debug hint: This is a hint"
  ```

## Command Reference

### Debug and Verbose Commands

**New commands added in v0.1.2:**

| Command | Description | Default State |
|---------|-------------|---------------|
| `/debug on` | Enable verbose error output with full tracebacks | OFF |
| `/debug off` | Disable verbose error output | OFF |
| `/verbose on` | Show internal state messages ([HYBRID], [TOOL]) | OFF |
| `/verbose off` | Hide internal state messages | OFF |
| `/errors` | List recent errors with IDs | N/A |
| `/trace <id>` | Show full stack trace for specific error ID | N/A |
| `/trace last` | Show stack trace for most recent error | N/A |

**Updated commands:**

- **`/context`** - Now shows debug and verbose mode states
- **`/help`** - Updated with debug/verbose command documentation

---

## Complete Function Reference

### Visualization Functions
- `plot_functional_boxplot()` - Band depth for 1D curves (+ method)
- `plot_curve_boxplot()` - Depth-colored curves (+ workers)
- `plot_contour_boxplot()` - Contour band depth (+ isovalue, workers)
- `plot_probabilistic_marching_squares()` - 2D scalar uncertainty
- `plot_uncertainty_lobes()` - Vector field uncertainty (dual percentiles)
- `plot_squid_glyph_2D()` - 2D vector uncertainty glyphs (depth-filtered)

### Data Functions
- `generate_ensemble_curves()` - 1D curve ensembles
- `generate_scalar_field_ensemble()` - 2D scalar fields
- `generate_vector_field_ensemble()` - 2D vector fields
- `load_csv_to_numpy()` - CSV to NumPy conversion
- `load_npy()` - Load existing .npy files

### Utility Functions
- `parse_simple_command()` - Parse hybrid control commands
- `execute_simple_command()` - Execute parsed commands
- `clear_session()` - Clean up temporary files

---

For more information:
- **User Guide**: See `USER_GUIDE.md` for styling examples and workflows
- **Testing**: See `TESTING.md` for testing strategies
- **Contributing**: See `CONTRIBUTING.md` for development guidelines
