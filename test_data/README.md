# Test Data

This directory contains sample datasets for testing ChatUVisBox.

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
