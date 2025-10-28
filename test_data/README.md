# Test Data

This directory contains sample datasets for testing ChatUVisBox visualization tools.

## Files

- `sample_curves.csv`: 50 sinusoidal curves with 100 points each
  - Used for: `plot_functional_boxplot`, `plot_curve_boxplot`
  - Shape: (50, 100) - 50 curves with 100 points each

- `sample_scalar_field.npy`: 2D scalar field ensemble
  - Used for: `plot_probabilistic_marching_squares`, `plot_contour_boxplot`
  - Shape: (30, 30, 20) - 30x30 grid with 20 ensemble members
  - Value range: [0, 1]

## Generating New Data

Use the data generation tools from `chatuvisbox.data_tools`:

### Curve Ensembles
```python
from chatuvisbox.data_tools import generate_ensemble_curves

result = generate_ensemble_curves(
    n_curves=50,      # Number of curves
    n_points=100,     # Points per curve
    n_ensemble=30     # Ensemble members (currently unused, reserved)
)
# Output: .npy file with shape (n_curves, n_points)
```

### Scalar Field Ensembles
```python
from chatuvisbox.data_tools import generate_scalar_field_ensemble

result = generate_scalar_field_ensemble(
    nx=50,            # Grid size in x
    ny=50,            # Grid size in y
    n_ensemble=30     # Number of ensemble members
)
# Output: .npy file with shape (ny, nx, n_ensemble)
# Algorithm: Fixed Gaussian center at (nx/2, ny/2), varying σ
```

### Vector Field Ensembles
```python
from chatuvisbox.data_tools import generate_vector_field_ensemble

result = generate_vector_field_ensemble(
    x_res=30,                        # Grid resolution in x
    y_res=30,                        # Grid resolution in y
    n_instances=30,                  # Number of ensemble members
    initial_direction=0.0,           # Base direction in radians
    initial_magnitude=1.0,           # Base magnitude
    direction_variation_factor=0.3,  # Direction uncertainty (increases with x)
    magnitude_variation_factor=0.3   # Magnitude uncertainty (increases with y)
)
# Output: Two .npy files
#   - positions: shape (n, 2) where n = x_res * y_res
#   - vectors: shape (n, n_instances, 2)
```

### CSV to NumPy
```python
from chatuvisbox.data_tools import load_csv_to_numpy

result = load_csv_to_numpy(
    filepath="path/to/data.csv",
    output_path="path/to/output.npy"  # Optional
)
# Output: .npy file with same shape as CSV data
```

## Data Shapes Reference

| Tool | Expected Input Shape | Description |
|------|---------------------|-------------|
| `plot_functional_boxplot` | `(n_curves, n_points)` | 2D array of curves |
| `plot_curve_boxplot` | `(n_curves, n_steps, n_dims)` | 3D array of trajectories |
| `plot_probabilistic_marching_squares` | `(ny, nx, n_ensemble)` | 3D scalar field ensemble |
| `plot_contour_boxplot` | `(ny, nx, n_ensemble)` | 3D scalar field ensemble |
| `plot_uncertainty_lobes` | positions: `(n, 2)`, vectors: `(n, m, 2)` | Positions and vector ensemble |

## Temporary Files

Generated data is saved to `temp/` directory with prefix `_temp_*`. These files are:
- Automatically created during LangGraph workflows
- Gitignored (not tracked)
- Cleaned up with `/clear` command in REPL (Phase 8)

## Regenerating Sample Data

```python
# Run the test data generation script
python create_test_data.py
```

This will regenerate all sample datasets in this directory.
