# ChatUVisBox API Documentation

## Table of Contents

1. [Visualization Tools](#visualization-tools)
2. [Data Generation Tools](#data-generation-tools)
3. [Command Parser](#command-parser)
4. [Configuration](#configuration)

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
    outliers_alpha: float = 0.5
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

**Returns**: Dict with:
- `status` (str): "success" or "error"
- `message` (str): Human-readable message
- `_vis_params` (dict): All visualization parameters for hybrid control

**Example**:
```python
from chatuvisbox.vis_tools import plot_functional_boxplot
from chatuvisbox.data_tools import generate_ensemble_curves

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
from chatuvisbox.vis_tools import probabilistic_marching_squares
from chatuvisbox.data_tools import generate_scalar_field_ensemble

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
    scale: float = 0.2
) -> Dict[str, Any]
```

**Parameters**:
- `positions_path` (str): Path to .npy file with positions array (shape: (n_points, 2))
- `vectors_path` (str): Path to .npy file with vectors array (shape: (n_points, 2, n_ensemble))
- `percentile1` (int): Outer percentile for lobe extent (default: 90, range: 0-100)
- `percentile2` (int): Inner percentile for lobe extent (default: 50, range: 0-100)
- `scale` (float): Scaling factor for glyph size (default: 0.2)

**Note**: percentile1 should be > percentile2 for meaningful visualization

**Example**:
```python
from chatuvisbox.vis_tools import plot_uncertainty_lobes
from chatuvisbox.data_tools import generate_vector_field_ensemble

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

## Command Parser

### Supported Hybrid Commands

The command parser recognizes 13+ fast-path commands for instant parameter updates:

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

### Usage

```python
from chatuvisbox.command_parser import parse_simple_command

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

## Complete Function Reference

### Visualization Functions
- `plot_functional_boxplot()` - Band depth for 1D curves
- `plot_curve_boxplot()` - Depth-colored curves (+ workers)
- `plot_contour_boxplot()` - Contour band depth (+ isovalue, workers)
- `probabilistic_marching_squares()` - 2D scalar uncertainty
- `plot_uncertainty_lobes()` - Vector field uncertainty

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
- **Developer Guide**: See `CLAUDE.md` for implementation details
- **Testing**: See `TESTING.md` for testing strategies
