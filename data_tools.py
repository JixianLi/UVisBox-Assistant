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
        # Convert to int in case LLM passes floats
        n_curves = int(n_curves)
        n_points = int(n_points)
        n_ensemble = int(n_ensemble)

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
        # Convert to int in case LLM passes floats
        nx = int(nx)
        ny = int(ny)
        n_ensemble = int(n_ensemble)

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
