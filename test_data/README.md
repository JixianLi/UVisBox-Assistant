# Test Data

This directory contains sample datasets for testing ChatUVisBox.

## Files

- `sample_curves.csv`: 50 sinusoidal curves with 100 points each (for functional_boxplot)
- `sample_scalar_field.npy`: 2D scalar field ensemble (30x30 grid, 20 members) for probabilistic_marching_squares

## Generating New Data

Use the data tools:
- `generate_ensemble_curves()`: Create synthetic curve ensembles
- `generate_scalar_field_ensemble()`: Create synthetic scalar field ensembles
