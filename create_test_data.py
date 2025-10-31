"""Create sample test data for UVisBox-Assistant"""
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

# 3. Vector field (for uncertainty lobes)
x_res, y_res, n_instances = 10, 10, 20
n_positions = x_res * y_res

# Create grid positions
x = np.linspace(0, 1, x_res)
y = np.linspace(0, 1, y_res)
xv, yv = np.meshgrid(x, y)
positions = np.column_stack([xv.ravel(), yv.ravel()])

# Create ensemble of vector fields
vectors_ensemble = []
for i in range(n_instances):
    # Base direction: [1, 0] (pointing right)
    # Direction variation increases with x
    # Magnitude variation increases with y
    vectors = []
    for j, (px, py) in enumerate(positions):
        # Direction varies by x position
        direction_variation = px * np.random.normal(0, 0.2, 2)
        # Magnitude varies by y position
        magnitude_variation = py * np.random.normal(0, 0.1)

        base_vector = np.array([1.0, 0.0])
        vector = base_vector + direction_variation
        vector = vector * (1.0 + magnitude_variation)
        vectors.append(vector)

    vectors_ensemble.append(np.array(vectors))

# Stack into (n_positions, n_instances, 2)
vectors = np.stack(vectors_ensemble, axis=1)

# Save both positions and vectors
np.save(test_data_dir / "sample_vector_positions.npy", positions)
np.save(test_data_dir / "sample_vector_field.npy", vectors)
print(f"Created sample_vector_positions.npy with shape {positions.shape}")
print(f"Created sample_vector_field.npy with shape {vectors.shape}")

# 4. README
readme = """# Test Data

This directory contains sample datasets for testing UVisBox-Assistant.

## Files

- `sample_curves.csv`: 50 sinusoidal curves with 100 points each (for functional_boxplot, curve_boxplot)
- `sample_scalar_field.npy`: 2D scalar field ensemble (30x30 grid, 20 members) for probabilistic_marching_squares and contour_boxplot
- `sample_vector_positions.npy`: Grid positions (100, 2) for uncertainty_lobes
- `sample_vector_field.npy`: Vector field ensemble (100, 20, 2) for uncertainty_lobes

## Generating New Data

Use the data tools:
- `generate_ensemble_curves()`: Create synthetic curve ensembles
- `generate_scalar_field_ensemble()`: Create synthetic scalar field ensembles
- `generate_vector_field_ensemble()`: Create synthetic vector field ensembles
- `load_csv_to_numpy()`: Load CSV files for visualization

## Data Formats

### Curves (2D)
- Shape: (n_points, n_curves) for CSV
- Shape: (n_curves, n_points) for numpy arrays
- Used by: functional_boxplot, curve_boxplot

### Scalar Fields (3D)
- Shape: (nx, ny, n_ensemble) or (ny, nx, n_ensemble)
- Values: Float arrays typically in [0, 1]
- Used by: probabilistic_marching_squares, contour_boxplot

### Vector Fields
- Positions: (n_positions, 2) - [x, y] coordinates
- Vectors: (n_positions, n_ensemble, 2) - [vx, vy] components
- Used by: uncertainty_lobes
"""

(test_data_dir / "README.md").write_text(readme)
print("Created README.md")

print("\n✅ All test data created successfully!")
