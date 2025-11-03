"""Data loading and transformation tools"""
import numpy as np
import pandas as pd
import traceback
from pathlib import Path
from typing import Dict, Optional
from uvisbox_assistant import config

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
        # Capture full traceback
        tb_str = traceback.format_exc()

        # Create user-friendly message
        user_msg = f"Error loading CSV: {str(e)}"

        # Return error info (will be recorded by conversation.py)
        return {
            "status": "error",
            "message": user_msg,
            "_error_details": {
                "exception": e,
                "traceback": tb_str
            }
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
        # Capture full traceback
        tb_str = traceback.format_exc()

        # Create user-friendly message
        user_msg = f"Error generating curves: {str(e)}"

        # Return error info (will be recorded by conversation.py)
        return {
            "status": "error",
            "message": user_msg,
            "_error_details": {
                "exception": e,
                "traceback": tb_str
            }
        }


def generate_scalar_field_ensemble(
    nx: int = 50,
    ny: int = 50,
    n_ensemble: int = 30,
    output_path: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate synthetic 2D scalar field ensemble.

    Each ensemble member is a Gaussian centered at (nx/2, ny/2) with:
    - Standard deviation: (nx+ensemble_index, ny)
    - Rescaled to [0, 1]
    - Uniform noise added from [0, 0.01)
    - Final rescale to [0, 1]

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

        # Create coordinate grids (0 to nx-1, 0 to ny-1)
        x = np.arange(nx)
        y = np.arange(ny)
        X, Y = np.meshgrid(x, y)

        # Center of the field
        center_x = nx / 2.0
        center_y = ny / 2.0

        # Generate ensemble of 2D Gaussian fields
        ensemble = []
        for ensemble_index in range(n_ensemble):
            # Standard deviation varies with ensemble index
            sigma_x = nx + ensemble_index
            sigma_y = ny

            # Generate 2D Gaussian
            Z = np.exp(-((X - center_x)**2 / (2 * sigma_x**2) +
                         (Y - center_y)**2 / (2 * sigma_y**2)))

            # Rescale to [0, 1]
            Z_min, Z_max = Z.min(), Z.max()
            if Z_max > Z_min:
                Z = (Z - Z_min) / (Z_max - Z_min)
            else:
                Z = np.zeros_like(Z)

            # Add uniform random noise from [0, 0.01)
            noise = np.random.uniform(0, 0.01, Z.shape)
            Z = Z + noise

            # Rescale again to [0, 1]
            Z_min, Z_max = Z.min(), Z.max()
            if Z_max > Z_min:
                Z = (Z - Z_min) / (Z_max - Z_min)
            else:
                Z = np.zeros_like(Z)

            ensemble.append(Z)

        data = np.stack(ensemble, axis=-1)  # Shape: (ny, nx, n_ensemble)

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
        # Capture full traceback
        tb_str = traceback.format_exc()

        # Create user-friendly message
        user_msg = f"Error generating scalar field: {str(e)}"

        # Return error info (will be recorded by conversation.py)
        return {
            "status": "error",
            "message": user_msg,
            "_error_details": {
                "exception": e,
                "traceback": tb_str
            }
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
        # Capture full traceback
        tb_str = traceback.format_exc()

        # Create user-friendly message
        user_msg = f"Error loading .npy file: {str(e)}"

        # Return error info (will be recorded by conversation.py)
        return {
            "status": "error",
            "message": user_msg,
            "_error_details": {
                "exception": e,
                "traceback": tb_str
            }
        }


def generate_vector_field_ensemble(
    x_res: int = 30,
    y_res: int = 30,
    n_instances: int = 30,
    initial_direction: float = 0.0,
    initial_magnitude: float = 1.0,
    direction_variation_factor: float = 0.3,
    magnitude_variation_factor: float = 0.3,
    output_path: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate synthetic 2D vector field ensemble on a regular grid.

    Direction variation increases with x coordinate.
    Magnitude variation increases with y coordinate.

    Args:
        x_res: Grid resolution in x direction (default: 30)
        y_res: Grid resolution in y direction (default: 30)
        n_instances: Number of ensemble members (default: 30)
        initial_direction: Base direction in radians (default: 0.0 = rightward)
        initial_magnitude: Base magnitude (default: 1.0)
        direction_variation_factor: Controls how much direction varies with x (default: 0.3)
        magnitude_variation_factor: Controls how much magnitude varies with y (default: 0.3)
        output_path: Output path for positions and vectors files

    Returns:
        Dict with status, positions_path, vectors_path, message
    """
    try:
        # Convert to int in case LLM passes floats
        x_res = int(x_res)
        y_res = int(y_res)
        n_instances = int(n_instances)

        # Create regular grid positions
        x = np.arange(x_res)
        y = np.arange(y_res)
        X, Y = np.meshgrid(x, y)

        # Flatten to (n_positions, 2) where n_positions = x_res * y_res
        positions = np.stack([X.flatten(), Y.flatten()], axis=1)
        n_positions = positions.shape[0]

        # Generate ensemble vectors with shape (n_positions, n_instances, 2)
        vectors = np.zeros((n_positions, n_instances, 2))

        for instance_idx in range(n_instances):
            for pos_idx in range(n_positions):
                x_coord = positions[pos_idx, 0]
                y_coord = positions[pos_idx, 1]

                # Direction variation increases with x
                # Normalize x to [0, 1] range
                x_normalized = x_coord / max(x_res - 1, 1)
                direction_std = direction_variation_factor * np.pi * x_normalized
                direction = initial_direction + np.random.normal(0, direction_std)

                # Magnitude variation increases with y
                # Normalize y to [0, 1] range
                y_normalized = y_coord / max(y_res - 1, 1)
                magnitude_std = magnitude_variation_factor * initial_magnitude * y_normalized
                magnitude = initial_magnitude + np.random.normal(0, magnitude_std)
                magnitude = max(0, magnitude)  # Ensure non-negative

                # Convert to Cartesian coordinates [vx, vy]
                vectors[pos_idx, instance_idx, 0] = magnitude * np.cos(direction)
                vectors[pos_idx, instance_idx, 1] = magnitude * np.sin(direction)

        # Generate output paths
        if output_path is None:
            positions_path = config.TEMP_DIR / f"{config.TEMP_FILE_PREFIX}vector_positions.npy"
            vectors_path = config.TEMP_DIR / f"{config.TEMP_FILE_PREFIX}vector_ensemble.npy"
        else:
            base_path = Path(output_path)
            positions_path = base_path.parent / f"{base_path.stem}_positions.npy"
            vectors_path = base_path.parent / f"{base_path.stem}_vectors.npy"

        # Save arrays
        np.save(positions_path, positions)
        np.save(vectors_path, vectors)

        return {
            "status": "success",
            "positions_path": str(positions_path),
            "vectors_path": str(vectors_path),
            "message": f"Generated vector field ensemble: {x_res}x{y_res} grid, {n_instances} instances",
            "positions_shape": positions.shape,
            "vectors_shape": vectors.shape
        }

    except Exception as e:
        # Capture full traceback
        tb_str = traceback.format_exc()

        # Create user-friendly message
        user_msg = f"Error generating vector field ensemble: {str(e)}"

        # Return error info (will be recorded by conversation.py)
        return {
            "status": "error",
            "message": user_msg,
            "_error_details": {
                "exception": e,
                "traceback": tb_str
            }
        }


def clear_session() -> Dict[str, str]:
    """
    Clear all temporary session files.

    Removes all .npy files in temp directory with TEMP_FILE_PREFIX.

    Returns:
        Dict with status and count of files removed
    """
    try:
        if not config.TEMP_DIR.exists():
            return {
                "status": "success",
                "message": "No temp directory found",
                "files_removed": 0
            }

        files_removed = []
        pattern = f"{config.TEMP_FILE_PREFIX}*{config.TEMP_FILE_EXTENSION}"

        for file_path in config.TEMP_DIR.glob(pattern):
            try:
                file_path.unlink()
                files_removed.append(str(file_path.name))
            except Exception as e:
                print(f"Warning: Could not remove {file_path}: {e}")

        return {
            "status": "success",
            "message": f"Removed {len(files_removed)} temporary files",
            "files_removed": len(files_removed),
            "files": files_removed
        }

    except Exception as e:
        # Capture full traceback
        tb_str = traceback.format_exc()

        # Create user-friendly message
        user_msg = f"Error clearing session: {str(e)}"

        # Return error info (will be recorded by conversation.py)
        return {
            "status": "error",
            "message": user_msg,
            "_error_details": {
                "exception": e,
                "traceback": tb_str
            }
        }


# Tool registry for LangGraph
DATA_TOOLS = {
    "load_csv_to_numpy": load_csv_to_numpy,
    "generate_ensemble_curves": generate_ensemble_curves,
    "generate_scalar_field_ensemble": generate_scalar_field_ensemble,
    "generate_vector_field_ensemble": generate_vector_field_ensemble,
    "load_npy": load_npy,
    "clear_session": clear_session,
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
        "name": "generate_vector_field_ensemble",
        "description": "Generate synthetic 2D vector field ensemble on a regular grid. Direction variation increases with x, magnitude variation increases with y.",
        "parameters": {
            "type": "object",
            "properties": {
                "x_res": {
                    "type": "integer",
                    "description": "Grid resolution in x direction",
                    "default": 30
                },
                "y_res": {
                    "type": "integer",
                    "description": "Grid resolution in y direction",
                    "default": 30
                },
                "n_instances": {
                    "type": "integer",
                    "description": "Number of ensemble members",
                    "default": 30
                },
                "initial_direction": {
                    "type": "number",
                    "description": "Base direction in radians (0 = rightward)",
                    "default": 0.0
                },
                "initial_magnitude": {
                    "type": "number",
                    "description": "Base magnitude of vectors",
                    "default": 1.0
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
    },
    {
        "name": "clear_session",
        "description": "Clear all temporary session files to start fresh",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]
