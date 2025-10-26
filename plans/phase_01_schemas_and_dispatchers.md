# Phase 1: Schemas & Dispatchers

**Goal**: Define the foundational data and visualization tools with their schemas for Gemini tool-calling.

**Duration**: 1-2 days

## Prerequisites

- Conda environment 'agent' is activated
- UVisBox is installed and verified
- Google Gemini API key is available

## Tasks

### Task 1.1: Environment & Project Setup

**Create project structure:**

```bash
chatuvisbox/
├── main.py                 # Placeholder for now
├── data_tools.py           # This phase
├── viz_tools.py            # This phase
├── config.py               # This phase
├── test_data/              # This phase
│   └── README.md
├── temp/                   # For .npy files
├── .gitignore
└── requirements.txt
```

**Steps:**
1. Create directories:
   ```bash
   mkdir -p test_data temp plans
   ```

2. Create `.gitignore`:
   ```
   temp/
   __pycache__/
   *.pyc
   .DS_Store
   ```

3. Create `requirements.txt`:
   ```txt
   langgraph>=0.0.20
   langchain>=0.1.0
   langchain-google-genai>=0.0.5
   google-generativeai>=0.3.0
   numpy>=1.24.0
   pandas>=2.0.0
   matplotlib>=3.7.0
   ```

4. Verify API key is available:
   ```bash
   echo $GEMINI_API_KEY
   # Should output your API key
   ```

5. Install dependencies:
   ```bash
   conda activate agent
   pip install -r requirements.txt
   ```

### Task 1.2: Configuration Module

**File**: `config.py`

```python
"""Configuration for ChatUVisBox"""
import os
from pathlib import Path

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment. Please set it in your system environment.")

# Model Configuration
MODEL_NAME = "gemini-2.0-flash"

# Paths
PROJECT_ROOT = Path(__file__).parent
TEMP_DIR = PROJECT_ROOT / "temp"
TEST_DATA_DIR = PROJECT_ROOT / "test_data"

# Ensure directories exist
TEMP_DIR.mkdir(exist_ok=True)
TEST_DATA_DIR.mkdir(exist_ok=True)

# File naming
TEMP_FILE_PREFIX = "_temp_"
TEMP_FILE_EXTENSION = ".npy"

# Visualization defaults (Tier-2 parameters)
DEFAULT_VIZ_PARAMS = {
    "figsize": (10, 8),
    "dpi": 100,
    "cmap": "viridis",
    "alpha": 0.5,
    "show_median": True,
    "show_outliers": True,
}
```

**Test:**
```bash
python -c "import config; print(config.MODEL_NAME)"
```

### Task 1.3: Data Tools Implementation

**File**: `data_tools.py`

Implement the following functions with:
- **Tier-1 parameters**: Exposed to Gemini (filepath, dimensions, etc.)
- **Tier-2 parameters**: Hard-coded defaults (data types, validation rules)
- **Return format**: `{"status": "success", "output_path": "...", "message": "..."}` or `{"status": "error", "message": "..."}`

**Functions to implement:**

```python
"""Data loading and transformation tools"""
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import config

def load_csv_to_numpy(
    filepath: str,
    output_path: Optional[str] = None
) -> Dict[str, str]:
    """
    Load a CSV file and save as numpy array.

    Args:
        filepath: Path to input CSV file
        output_path: Path for output .npy file (auto-generated if None)

    Returns:
        Dict with status, output_path, message, and shape info
    """
    try:
        # Validate input
        if not Path(filepath).exists():
            return {
                "status": "error",
                "message": f"File not found: {filepath}"
            }

        # Load CSV
        df = pd.read_csv(filepath)
        data = df.to_numpy()

        # Generate output path if needed
        if output_path is None:
            filename = Path(filepath).stem
            output_path = config.TEMP_DIR / f"{config.TEMP_FILE_PREFIX}{filename}.npy"

        # Save as .npy
        np.save(output_path, data)

        return {
            "status": "success",
            "output_path": str(output_path),
            "message": f"Loaded CSV with shape {data.shape}",
            "shape": data.shape,
            "dtype": str(data.dtype)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error loading CSV: {str(e)}"
        }


def generate_ensemble_curves(
    n_curves: int = 50,
    n_points: int = 100,
    n_ensemble: int = 30,
    output_path: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate synthetic ensemble curve data for testing.

    Args:
        n_curves: Number of curves
        n_points: Number of points per curve
        n_ensemble: Number of ensemble members (for 3D output)
        output_path: Output .npy path

    Returns:
        Dict with status, output_path, message, shape
    """
    try:
        # Generate synthetic curves
        x = np.linspace(0, 2*np.pi, n_points)
        curves = []

        for i in range(n_curves):
            # Random sinusoidal curves with noise
            amplitude = np.random.uniform(0.5, 1.5)
            frequency = np.random.uniform(0.8, 1.2)
            phase = np.random.uniform(0, 2*np.pi)
            noise = np.random.normal(0, 0.1, n_points)

            curve = amplitude * np.sin(frequency * x + phase) + noise
            curves.append(curve)

        data = np.array(curves)  # Shape: (n_curves, n_points)

        # Generate output path
        if output_path is None:
            output_path = config.TEMP_DIR / f"{config.TEMP_FILE_PREFIX}ensemble_curves.npy"

        np.save(output_path, data)

        return {
            "status": "success",
            "output_path": str(output_path),
            "message": f"Generated {n_curves} curves with {n_points} points each",
            "shape": data.shape
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating curves: {str(e)}"
        }


def generate_scalar_field_ensemble(
    nx: int = 50,
    ny: int = 50,
    n_ensemble: int = 30,
    output_path: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate synthetic 2D scalar field ensemble.

    Args:
        nx: Grid size in x
        ny: Grid size in y
        n_ensemble: Number of ensemble members
        output_path: Output path

    Returns:
        Dict with status, output_path, message
    """
    try:
        x = np.linspace(-3, 3, nx)
        y = np.linspace(-3, 3, ny)
        X, Y = np.meshgrid(x, y)

        # Generate ensemble of 2D Gaussian-like fields
        ensemble = []
        for i in range(n_ensemble):
            center_x = np.random.uniform(-1, 1)
            center_y = np.random.uniform(-1, 1)
            sigma = np.random.uniform(0.5, 1.5)

            Z = np.exp(-((X - center_x)**2 + (Y - center_y)**2) / (2 * sigma**2))
            Z += np.random.normal(0, 0.05, Z.shape)
            ensemble.append(Z)

        data = np.stack(ensemble, axis=-1)  # Shape: (nx, ny, n_ensemble)

        if output_path is None:
            output_path = config.TEMP_DIR / f"{config.TEMP_FILE_PREFIX}scalar_field.npy"

        np.save(output_path, data)

        return {
            "status": "success",
            "output_path": str(output_path),
            "message": f"Generated scalar field ensemble with shape {data.shape}",
            "shape": data.shape
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating scalar field: {str(e)}"
        }


def load_npy(filepath: str) -> Dict[str, str]:
    """
    Load and validate a .npy file.

    Args:
        filepath: Path to .npy file

    Returns:
        Dict with status, filepath, shape, dtype
    """
    try:
        if not Path(filepath).exists():
            return {
                "status": "error",
                "message": f"File not found: {filepath}"
            }

        data = np.load(filepath)

        return {
            "status": "success",
            "output_path": filepath,
            "message": f"Loaded array with shape {data.shape}",
            "shape": data.shape,
            "dtype": str(data.dtype)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error loading .npy file: {str(e)}"
        }


# Tool registry for LangGraph
DATA_TOOLS = {
    "load_csv_to_numpy": load_csv_to_numpy,
    "generate_ensemble_curves": generate_ensemble_curves,
    "generate_scalar_field_ensemble": generate_scalar_field_ensemble,
    "load_npy": load_npy,
}


# Tier-1 schemas for Gemini (will be used in Phase 2)
DATA_TOOL_SCHEMAS = [
    {
        "name": "load_csv_to_numpy",
        "description": "Load a CSV file and convert it to a numpy array saved as .npy format",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the CSV file to load"
                }
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "generate_ensemble_curves",
        "description": "Generate synthetic ensemble curve data for testing visualizations",
        "parameters": {
            "type": "object",
            "properties": {
                "n_curves": {
                    "type": "integer",
                    "description": "Number of curves to generate",
                    "default": 50
                },
                "n_points": {
                    "type": "integer",
                    "description": "Number of points per curve",
                    "default": 100
                }
            }
        }
    },
    {
        "name": "generate_scalar_field_ensemble",
        "description": "Generate synthetic 2D scalar field ensemble for testing",
        "parameters": {
            "type": "object",
            "properties": {
                "nx": {
                    "type": "integer",
                    "description": "Grid size in x direction",
                    "default": 50
                },
                "ny": {
                    "type": "integer",
                    "description": "Grid size in y direction",
                    "default": 50
                }
            }
        }
    },
    {
        "name": "load_npy",
        "description": "Load an existing .npy numpy array file",
        "parameters": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the .npy file"
                }
            },
            "required": ["filepath"]
        }
    }
]
```

**Test:**
```python
# test_data_tools.py
from data_tools import *

# Test CSV loading (create dummy CSV first)
import pandas as pd
pd.DataFrame({"x": [1,2,3], "y": [4,5,6]}).to_csv("test_data/dummy.csv", index=False)
result = load_csv_to_numpy("test_data/dummy.csv")
print(result)

# Test generation
result = generate_ensemble_curves(n_curves=10, n_points=50)
print(result)

result = generate_scalar_field_ensemble(nx=20, ny=20, n_ensemble=10)
print(result)
```

### Task 1.4: Visualization Tools Implementation

**File**: `viz_tools.py`

Implement wrappers around UVisBox functions:

```python
"""Visualization tools wrapping UVisBox functions"""
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Optional
import config

# Import UVisBox modules
try:
    from uvisbox.Modules import functional_boxplot, curve_boxplot
    from uvisbox.Modules import probabilistic_marching_squares, uncertainty_lobes
except ImportError as e:
    print(f"Warning: UVisBox import failed: {e}")
    print("Make sure UVisBox is installed in the 'agent' conda environment")


def plot_functional_boxplot(
    data_path: str,
    percentile: float = 100.0,
    show_median: bool = True
) -> Dict[str, str]:
    """
    Create a functional boxplot from curve data.

    Args:
        data_path: Path to .npy file with shape (n_curves, n_points)
        percentile: Percentile for band depth (Tier-1)
        show_median: Whether to show median curve (Tier-1)

    Returns:
        Dict with status and message
    """
    try:
        # Load data
        if not Path(data_path).exists():
            return {"status": "error", "message": f"Data file not found: {data_path}"}

        curves = np.load(data_path)

        # Validate shape (should be 2D: n_curves x n_points)
        if curves.ndim != 2:
            return {
                "status": "error",
                "message": f"Expected 2D array, got shape {curves.shape}"
            }

        # Create figure with Tier-2 defaults
        fig, ax = plt.subplots(
            figsize=config.DEFAULT_VIZ_PARAMS["figsize"],
            dpi=config.DEFAULT_VIZ_PARAMS["dpi"]
        )

        # Call UVisBox function
        functional_boxplot(
            curves=curves,
            percentil=percentile,
            ax=ax,
            show_median=show_median,
            band_alpha=config.DEFAULT_VIZ_PARAMS["alpha"]
        )

        ax.set_title("Functional Boxplot")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        # Show non-blocking
        plt.show(block=False)

        return {
            "status": "success",
            "message": f"Displayed functional boxplot for {curves.shape[0]} curves"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating functional boxplot: {str(e)}"
        }


def plot_curve_boxplot(
    data_path: str,
    percentile: float = 50.0,
    colormap: str = "viridis"
) -> Dict[str, str]:
    """
    Create a curve boxplot from 3D curve ensemble data.

    Args:
        data_path: Path to .npy with shape (n_curves, n_steps, n_dims)
        percentile: Percentile for band highlighting
        colormap: Colormap name

    Returns:
        Dict with status and message
    """
    try:
        if not Path(data_path).exists():
            return {"status": "error", "message": f"Data file not found: {data_path}"}

        curves = np.load(data_path)

        # For 2D curves from functional data, reshape if needed
        if curves.ndim == 2:
            # Shape (n_curves, n_points) -> (n_curves, n_points, 1) for viewing as 1D curves
            n_curves, n_points = curves.shape
            x_coords = np.linspace(0, 1, n_points)
            # Stack x and y to make (n_curves, n_points, 2)
            curves_3d = np.stack([
                np.tile(x_coords, (n_curves, 1)),
                curves
            ], axis=-1)
            curves = curves_3d

        if curves.ndim != 3:
            return {
                "status": "error",
                "message": f"Expected 3D array (n_curves, n_steps, n_dims), got shape {curves.shape}"
            }

        fig, ax = plt.subplots(
            figsize=config.DEFAULT_VIZ_PARAMS["figsize"],
            dpi=config.DEFAULT_VIZ_PARAMS["dpi"]
        )

        curve_boxplot(
            curves=curves,
            percentile=percentile,
            ax=ax,
            color_map=colormap,
            alpha=config.DEFAULT_VIZ_PARAMS["alpha"]
        )

        ax.set_title("Curve Boxplot")
        plt.show(block=False)

        return {
            "status": "success",
            "message": f"Displayed curve boxplot for {curves.shape[0]} curves"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating curve boxplot: {str(e)}"
        }


def plot_probabilistic_marching_squares(
    data_path: str,
    isovalue: float = 0.5,
    colormap: str = "viridis"
) -> Dict[str, str]:
    """
    Create probabilistic marching squares visualization.

    Args:
        data_path: Path to .npy with shape (n_x, n_y, n_ensemble)
        isovalue: Isovalue for contour extraction
        colormap: Colormap name

    Returns:
        Dict with status and message
    """
    try:
        if not Path(data_path).exists():
            return {"status": "error", "message": f"Data file not found: {data_path}"}

        field = np.load(data_path)

        if field.ndim != 3:
            return {
                "status": "error",
                "message": f"Expected 3D array (nx, ny, n_ens), got shape {field.shape}"
            }

        fig, ax = plt.subplots(
            figsize=config.DEFAULT_VIZ_PARAMS["figsize"],
            dpi=config.DEFAULT_VIZ_PARAMS["dpi"]
        )

        probabilistic_marching_squares(
            F=field,
            isovalue=isovalue,
            cmap=colormap,
            ax=ax
        )

        ax.set_title(f"Probabilistic Marching Squares (isovalue={isovalue})")
        plt.show(block=False)

        return {
            "status": "success",
            "message": f"Displayed probabilistic marching squares for field shape {field.shape}"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating probabilistic marching squares: {str(e)}"
        }


def plot_uncertainty_lobes(
    positions_path: str,
    vectors_path: str,
    percentile: float = 0.75,
    scale: float = 0.2
) -> Dict[str, str]:
    """
    Create uncertainty lobe glyphs.

    Args:
        positions_path: Path to .npy with shape (n, 2) - glyph positions
        vectors_path: Path to .npy with shape (n, m, 2) - ensemble vectors
        percentile: Percentile for depth filtering
        scale: Scale factor for glyphs

    Returns:
        Dict with status and message
    """
    try:
        if not Path(positions_path).exists():
            return {"status": "error", "message": f"Positions file not found: {positions_path}"}
        if not Path(vectors_path).exists():
            return {"status": "error", "message": f"Vectors file not found: {vectors_path}"}

        positions = np.load(positions_path)
        vectors = np.load(vectors_path)

        fig, ax = plt.subplots(
            figsize=config.DEFAULT_VIZ_PARAMS["figsize"],
            dpi=config.DEFAULT_VIZ_PARAMS["dpi"]
        )

        uncertainty_lobes(
            positions=positions,
            ensemble_vectors=vectors,
            percentil1=percentile,
            scale=scale,
            ax=ax,
            show_median=config.DEFAULT_VIZ_PARAMS["show_median"]
        )

        ax.set_title("Uncertainty Lobes")
        ax.set_aspect('equal')
        plt.show(block=False)

        return {
            "status": "success",
            "message": f"Displayed uncertainty lobes for {positions.shape[0]} positions"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating uncertainty lobes: {str(e)}"
        }


# Tool registry
VIZ_TOOLS = {
    "plot_functional_boxplot": plot_functional_boxplot,
    "plot_curve_boxplot": plot_curve_boxplot,
    "plot_probabilistic_marching_squares": plot_probabilistic_marching_squares,
    "plot_uncertainty_lobes": plot_uncertainty_lobes,
}


# Tier-1 schemas for Gemini
VIZ_TOOL_SCHEMAS = [
    {
        "name": "plot_functional_boxplot",
        "description": "Create a functional boxplot visualization showing the median and band depth of multiple curves",
        "parameters": {
            "type": "object",
            "properties": {
                "data_path": {
                    "type": "string",
                    "description": "Path to .npy file containing 2D array of curves (n_curves, n_points)"
                },
                "percentile": {
                    "type": "number",
                    "description": "Percentile for band depth calculation (0-100)",
                    "default": 100.0
                },
                "show_median": {
                    "type": "boolean",
                    "description": "Whether to show the median curve",
                    "default": True
                }
            },
            "required": ["data_path"]
        }
    },
    {
        "name": "plot_curve_boxplot",
        "description": "Create a curve boxplot for ensemble curve data with depth-based coloring",
        "parameters": {
            "type": "object",
            "properties": {
                "data_path": {
                    "type": "string",
                    "description": "Path to .npy file containing 3D curve ensemble (n_curves, n_steps, n_dims)"
                },
                "percentile": {
                    "type": "number",
                    "description": "Percentile for band highlighting",
                    "default": 50.0
                },
                "colormap": {
                    "type": "string",
                    "description": "Matplotlib colormap name",
                    "default": "viridis"
                }
            },
            "required": ["data_path"]
        }
    },
    {
        "name": "plot_probabilistic_marching_squares",
        "description": "Visualize probabilistic isocontours from 2D scalar field ensemble",
        "parameters": {
            "type": "object",
            "properties": {
                "data_path": {
                    "type": "string",
                    "description": "Path to .npy file containing 3D scalar field (nx, ny, n_ensemble)"
                },
                "isovalue": {
                    "type": "number",
                    "description": "Isovalue for contour extraction",
                    "default": 0.5
                },
                "colormap": {
                    "type": "string",
                    "description": "Matplotlib colormap name",
                    "default": "viridis"
                }
            },
            "required": ["data_path"]
        }
    },
    {
        "name": "plot_uncertainty_lobes",
        "description": "Create uncertainty lobe glyphs showing directional uncertainty of vector ensembles",
        "parameters": {
            "type": "object",
            "properties": {
                "positions_path": {
                    "type": "string",
                    "description": "Path to .npy file with glyph positions (n, 2)"
                },
                "vectors_path": {
                    "type": "string",
                    "description": "Path to .npy file with ensemble vectors (n, m, 2)"
                },
                "percentile": {
                    "type": "number",
                    "description": "Percentile for depth filtering",
                    "default": 0.75
                },
                "scale": {
                    "type": "number",
                    "description": "Scale factor for glyph size",
                    "default": 0.2
                }
            },
            "required": ["positions_path", "vectors_path"]
        }
    }
]
```

**Test:**
```python
# test_viz_tools.py
from data_tools import generate_ensemble_curves
from viz_tools import plot_functional_boxplot

# Generate test data
result = generate_ensemble_curves(n_curves=30, n_points=100)
print(result)

# Visualize
viz_result = plot_functional_boxplot(result["output_path"])
print(viz_result)

# Check if matplotlib window appears
input("Press Enter to close...")
```

### Task 1.5: Create Test Data

Create sample CSV files in `test_data/`:

```python
# create_test_data.py
import numpy as np
import pandas as pd
from pathlib import Path

test_data_dir = Path("test_data")

# 1. Simple 2D curves (for functional boxplot)
n_curves = 50
n_points = 100
x = np.linspace(0, 10, n_points)
curves = []
for i in range(n_curves):
    amplitude = np.random.uniform(0.8, 1.2)
    phase = np.random.uniform(0, np.pi)
    noise = np.random.normal(0, 0.1, n_points)
    y = amplitude * np.sin(x + phase) + noise
    curves.append(y)

curves_df = pd.DataFrame(np.array(curves).T)
curves_df.to_csv(test_data_dir / "sample_curves.csv", index=False)
print(f"Created sample_curves.csv with shape {curves_df.shape}")

# 2. Scalar field (for marching squares) - save as .npy since CSV is awkward for 3D
nx, ny, n_ens = 30, 30, 20
x = np.linspace(-2, 2, nx)
y = np.linspace(-2, 2, ny)
X, Y = np.meshgrid(x, y)

ensemble = []
for i in range(n_ens):
    Z = np.exp(-(X**2 + Y**2) / 2)
    Z += np.random.normal(0, 0.1, Z.shape)
    ensemble.append(Z)

field = np.stack(ensemble, axis=-1)
np.save(test_data_dir / "sample_scalar_field.npy", field)
print(f"Created sample_scalar_field.npy with shape {field.shape}")

# 3. README
readme = """# Test Data

This directory contains sample datasets for testing ChatUVisBox.

## Files

- `sample_curves.csv`: 50 sinusoidal curves with 100 points each (for functional_boxplot)
- `sample_scalar_field.npy`: 2D scalar field ensemble (30x30 grid, 20 members) for probabilistic_marching_squares

## Generating New Data

Use the data tools:
- `generate_ensemble_curves()`: Create synthetic curve ensembles
- `generate_scalar_field_ensemble()`: Create synthetic scalar field ensembles
"""

(test_data_dir / "README.md").write_text(readme)
print("Created README.md")
```

Run:
```bash
python create_test_data.py
```

## Validation Checklist

- [ ] Project structure created
- [ ] `.env` file with `GOOGLE_API_KEY` configured
- [ ] `requirements.txt` installed successfully
- [ ] `config.py` imports without errors
- [ ] All data tools return proper JSON-formatted responses
- [ ] All data tools have corresponding schemas in `DATA_TOOL_SCHEMAS`
- [ ] All viz tools accept .npy file paths and show matplotlib windows
- [ ] All viz tools have corresponding schemas in `VIZ_TOOL_SCHEMAS`
- [ ] Test data created in `test_data/`
- [ ] Manual test: generate curves → plot functional boxplot (window appears)

## Output

After Phase 1, you should have:
- Working data tools that save to `.npy` files
- Working viz tools that read `.npy` and display matplotlib figures
- Tool schemas ready for Gemini function calling
- Test data for development
- Configuration system in place

## Next Phase

Phase 2 will define the `GraphState` and create the LangGraph nodes that call these tools.
