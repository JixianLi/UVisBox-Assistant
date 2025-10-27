"""Create sample test data for ChatUVisBox"""
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

print("\n✅ All test data created successfully!")
