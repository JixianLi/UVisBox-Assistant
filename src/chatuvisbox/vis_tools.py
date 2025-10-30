"""Visualization tools wrapping UVisBox functions"""
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Optional, List
from chatuvisbox import config

# Import UVisBox modules
try:
    from uvisbox.Modules import (
        functional_boxplot,
        curve_boxplot,
        probabilistic_marching_squares,
        uncertainty_lobes,
        contour_boxplot,
        BoxplotStyleConfig
    )
except ImportError as e:
    print(f"Warning: UVisBox import failed: {e}")
    print("Make sure UVisBox is installed in the 'agent' conda environment")


def plot_functional_boxplot(
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
    method: str = "fdb"
) -> Dict[str, str]:
    """
    Create a functional boxplot from curve data with multiple percentile bands.

    Args:
        data_path: Path to .npy file with shape (n_curves, n_points)
        percentiles: List of percentiles for bands (default: [25, 50, 90, 100])
        percentile_colormap: Colormap for percentile bands (default: "viridis")
        show_median: Whether to show median curve (default: True)
        median_color: Color of median curve (default: "red")
        median_width: Width of median curve (default: 3.0)
        median_alpha: Alpha of median curve (default: 1.0)
        show_outliers: Whether to show outlier curves (default: False)
        outliers_color: Color of outlier curves (default: "gray")
        outliers_width: Width of outlier curves (default: 1.0)
        outliers_alpha: Alpha of outlier curves (default: 0.5)
        method: Band depth method - 'fdb' (functional band depth) or 'mfdb' (modified functional band depth) (default: 'fdb')

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

        # Set defaults if not provided
        if percentiles is None:
            percentiles = [25, 50, 90, 100]

        # Create BoxplotStyleConfig
        style_config = BoxplotStyleConfig(
            percentiles=percentiles,
            percentile_colormap=percentile_colormap,
            show_median=show_median,
            median_color=median_color,
            median_width=median_width,
            median_alpha=median_alpha,
            show_outliers=show_outliers,
            outliers_color=outliers_color,
            outliers_width=outliers_width,
            outliers_alpha=outliers_alpha
        )

        # Create figure with Tier-2 defaults
        fig, ax = plt.subplots(
            figsize=config.DEFAULT_VIS_PARAMS["figsize"],
            dpi=config.DEFAULT_VIS_PARAMS["dpi"]
        )

        # Call UVisBox function
        functional_boxplot(
            data=curves,
            method=method,
            boxplot_style=style_config,
            ax=ax
        )

        ax.set_title("Functional Boxplot")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        # Show non-blocking
        plt.show(block=False)
        plt.pause(0.1)

        return {
            "status": "success",
            "message": f"Displayed functional boxplot for {curves.shape[0]} curves with percentiles {percentiles} using method '{method}'",
            "_vis_params": {
                "_tool_name": "plot_functional_boxplot",
                "data_path": data_path,
                "percentiles": percentiles,
                "percentile_colormap": percentile_colormap,
                "show_median": show_median,
                "median_color": median_color,
                "median_width": median_width,
                "median_alpha": median_alpha,
                "show_outliers": show_outliers,
                "outliers_color": outliers_color,
                "outliers_width": outliers_width,
                "outliers_alpha": outliers_alpha,
                "method": method
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating functional boxplot: {str(e)}"
        }


def plot_curve_boxplot(
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
) -> Dict[str, str]:
    """
    Create a curve boxplot from 3D curve ensemble data with multiple percentile bands.

    Args:
        data_path: Path to .npy with shape (n_curves, n_steps, n_dims)
        percentiles: List of percentiles for bands (default: [25, 50, 90, 100])
        percentile_colormap: Colormap for percentile bands (default: "viridis")
        show_median: Whether to show median curve (default: True)
        median_color: Color of median curve (default: "red")
        median_width: Width of median curve (default: 3.0)
        median_alpha: Alpha of median curve (default: 1.0)
        show_outliers: Whether to show outlier curves (default: False)
        outliers_color: Color of outlier curves (default: "gray")
        outliers_width: Width of outlier curves (default: 1.0)
        outliers_alpha: Alpha of outlier curves (default: 0.5)
        workers: Number of parallel workers for band depth computation (default: 12)

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

        # Set defaults if not provided
        if percentiles is None:
            percentiles = [25, 50, 90, 100]

        # Create BoxplotStyleConfig
        style_config = BoxplotStyleConfig(
            percentiles=percentiles,
            percentile_colormap=percentile_colormap,
            show_median=show_median,
            median_color=median_color,
            median_width=median_width,
            median_alpha=median_alpha,
            show_outliers=show_outliers,
            outliers_color=outliers_color,
            outliers_width=outliers_width,
            outliers_alpha=outliers_alpha
        )

        fig, ax = plt.subplots(
            figsize=config.DEFAULT_VIS_PARAMS["figsize"],
            dpi=config.DEFAULT_VIS_PARAMS["dpi"]
        )

        curve_boxplot(
            curves=curves,
            boxplot_style=style_config,
            ax=ax,
            workers=workers
        )

        ax.set_title("Curve Boxplot")
        plt.show(block=False)
        plt.pause(0.1)

        return {
            "status": "success",
            "message": f"Displayed curve boxplot for {curves.shape[0]} curves with percentiles {percentiles}",
            "_vis_params": {
                "_tool_name": "plot_curve_boxplot",
                "data_path": data_path,
                "percentiles": percentiles,
                "percentile_colormap": percentile_colormap,
                "show_median": show_median,
                "median_color": median_color,
                "median_width": median_width,
                "median_alpha": median_alpha,
                "show_outliers": show_outliers,
                "outliers_color": outliers_color,
                "outliers_width": outliers_width,
                "outliers_alpha": outliers_alpha,
                "workers": workers
            }
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
            figsize=config.DEFAULT_VIS_PARAMS["figsize"],
            dpi=config.DEFAULT_VIS_PARAMS["dpi"]
        )

        probabilistic_marching_squares(
            ensemble_images=field,
            isovalue=isovalue,
            cmap=colormap,
            ax=ax
        )

        ax.set_title(f"Probabilistic Marching Squares (isovalue={isovalue})")
        plt.show(block=False)
        plt.pause(0.1)

        return {
            "status": "success",
            "message": f"Displayed probabilistic marching squares for field shape {field.shape}",
            "_vis_params": {
                "_tool_name": "plot_probabilistic_marching_squares",
                "data_path": data_path,
                "isovalue": isovalue,
                "colormap": colormap
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating probabilistic marching squares: {str(e)}"
        }


def plot_uncertainty_lobes(
    vectors_path: str,
    positions_path: str,
    percentile1: float = 90,
    percentile2: float = 50,
    scale: float = 0.2,
    workers: Optional[int] = None
) -> Dict[str, str]:
    """
    Create uncertainty lobe glyphs.

    Args:
        vectors_path: Path to .npy with shape (n, m, 2) - ensemble vectors
        positions_path: Path to .npy with shape (n, 2) - glyph positions
        percentile1: First percentile for depth filtering, 0-100 (default: 90)
        percentile2: Second percentile for depth filtering, 0-100 (default: 50)
        scale: Scale factor for glyphs
        workers: Number of parallel workers for band depth computation (default: None, optimized for large data only)

    Returns:
        Dict with status and message
    """
    try:
        if not Path(vectors_path).exists():
            return {"status": "error", "message": f"Vectors file not found: {vectors_path}"}

        if not Path(positions_path).exists():
            return {"status": "error", "message": f"Positions file not found: {positions_path}"}

        vectors = np.load(vectors_path)
        positions = np.load(positions_path)

        fig, ax = plt.subplots(
            figsize=config.DEFAULT_VIS_PARAMS["figsize"],
            dpi=config.DEFAULT_VIS_PARAMS["dpi"]
        )

        # Call uncertainty_lobes with positions
        uncertainty_lobes(
            positions=positions,
            ensemble_vectors=vectors,
            percentile1=percentile1,
            percentile2=percentile2,
            scale=scale,
            ax=ax,
            workers=workers
        )

        n_positions = positions.shape[0]

        # Set proper axis limits based on positions
        x_min, x_max = positions[:, 0].min(), positions[:, 0].max()
        y_min, y_max = positions[:, 1].min(), positions[:, 1].max()

        # Add some margin
        x_margin = (x_max - x_min) * 0.1 if x_max > x_min else 0.5
        y_margin = (y_max - y_min) * 0.1 if y_max > y_min else 0.5

        ax.set_xlim(x_min - x_margin, x_max + x_margin)
        ax.set_ylim(y_min - y_margin, y_max + y_margin)

        ax.set_title("Uncertainty Lobes")
        ax.set_aspect('equal')
        plt.show(block=False)
        plt.pause(0.1)

        return {
            "status": "success",
            "message": f"Displayed uncertainty lobes for {n_positions} positions",
            "_vis_params": {
                "_tool_name": "plot_uncertainty_lobes",
                "positions_path": positions_path,
                "vectors_path": vectors_path,
                "percentile1": percentile1,
                "percentile2": percentile2,
                "scale": scale,
                "workers": workers
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating uncertainty lobes: {str(e)}"
        }


def plot_contour_boxplot(
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
) -> Dict[str, str]:
    """
    Create a contour boxplot visualization from ensemble scalar fields.

    Extracts binary contours at isovalue, computes band depths, and visualizes
    uncertainty using band envelopes.

    Args:
        data_path: Path to .npy file with shape (ny, nx, n_ensemble)
        isovalue: Threshold value for creating binary images
        percentiles: List of percentiles (0-100) for band envelopes (default: [25, 50, 75, 90])
        percentile_colormap: Colormap for percentile bands (default: "viridis")
        show_median: Whether to show median contour (default: True)
        median_color: Color of median contour (default: "red")
        median_width: Width of median contour (default: 3.0)
        median_alpha: Alpha of median contour (default: 1.0)
        show_outliers: Whether to show outlier contours (default: False)
        outliers_color: Color of outlier contours (default: "gray")
        outliers_width: Width of outlier contours (default: 1.0)
        outliers_alpha: Alpha of outlier contours (default: 0.5)
        workers: Number of parallel workers for band depth computation (default: 12)

    Returns:
        Dict with status and message
    """
    try:
        if not Path(data_path).exists():
            return {"status": "error", "message": f"Data file not found: {data_path}"}

        data = np.load(data_path)

        # Validate shape (should be 3D)
        if data.ndim != 3:
            return {
                "status": "error",
                "message": f"Expected 3D array, got shape {data.shape}"
            }

        # Rearrange from (ny, nx, n_ensemble) to (n_ensemble, ny, nx)
        ensemble_images = np.transpose(data, (2, 0, 1))

        # Set defaults
        if percentiles is None:
            percentiles = [25, 50, 75, 90]

        # Create BoxplotStyleConfig
        style_config = BoxplotStyleConfig(
            percentiles=percentiles,
            percentile_colormap=percentile_colormap,
            show_median=show_median,
            median_color=median_color,
            median_width=median_width,
            median_alpha=median_alpha,
            show_outliers=show_outliers,
            outliers_color=outliers_color,
            outliers_width=outliers_width,
            outliers_alpha=outliers_alpha
        )

        fig, ax = plt.subplots(
            figsize=config.DEFAULT_VIS_PARAMS["figsize"],
            dpi=config.DEFAULT_VIS_PARAMS["dpi"]
        )

        # Call UVisBox contour_boxplot
        contour_boxplot(
            ensemble_images=ensemble_images,
            isovalue=isovalue,
            boxplot_style=style_config,
            ax=ax,
            workers=workers
        )

        ax.set_title(f"Contour Boxplot (isovalue={isovalue})")
        plt.show(block=False)
        plt.pause(0.1)

        return {
            "status": "success",
            "message": f"Displayed contour boxplot for ensemble with {ensemble_images.shape[0]} members",
            "_vis_params": {
                "_tool_name": "plot_contour_boxplot",
                "data_path": data_path,
                "isovalue": isovalue,
                "percentiles": percentiles,
                "percentile_colormap": percentile_colormap,
                "show_median": show_median,
                "median_color": median_color,
                "median_width": median_width,
                "median_alpha": median_alpha,
                "show_outliers": show_outliers,
                "outliers_color": outliers_color,
                "outliers_width": outliers_width,
                "outliers_alpha": outliers_alpha,
                "workers": workers
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating contour boxplot: {str(e)}"
        }


# Tool registry
VIS_TOOLS = {
    "plot_functional_boxplot": plot_functional_boxplot,
    "plot_curve_boxplot": plot_curve_boxplot,
    "plot_probabilistic_marching_squares": plot_probabilistic_marching_squares,
    "plot_uncertainty_lobes": plot_uncertainty_lobes,
    "plot_contour_boxplot": plot_contour_boxplot,
}


# Tier-1 schemas for Gemini
VIS_TOOL_SCHEMAS = [
    {
        "name": "plot_functional_boxplot",
        "description": "Create a functional boxplot visualization with multiple percentile bands showing band depth of curves",
        "parameters": {
            "type": "object",
            "properties": {
                "data_path": {
                    "type": "string",
                    "description": "Path to .npy file containing 2D array of curves (n_curves, n_points)"
                },
                "percentiles": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "List of percentiles for bands to be plotted (e.g., [25, 50, 90, 100])",
                    "default": [25, 50, 90, 100]
                },
                "percentile_colormap": {
                    "type": "string",
                    "description": "Colormap for percentile bands (e.g., 'viridis', 'plasma', 'inferno')",
                    "default": "viridis"
                },
                "show_median": {
                    "type": "boolean",
                    "description": "Whether to show median curve (default: True)",
                    "default": True
                },
                "median_color": {
                    "type": "string",
                    "description": "Color of median curve (default: 'red')",
                    "default": "red"
                },
                "median_width": {
                    "type": "number",
                    "description": "Width of median curve (default: 3.0)",
                    "default": 3.0
                },
                "median_alpha": {
                    "type": "number",
                    "description": "Alpha transparency of median curve (default: 1.0)",
                    "default": 1.0
                },
                "show_outliers": {
                    "type": "boolean",
                    "description": "Whether to show outlier curves (default: False)",
                    "default": False
                },
                "outliers_color": {
                    "type": "string",
                    "description": "Color of outlier curves (default: 'gray')",
                    "default": "gray"
                },
                "outliers_width": {
                    "type": "number",
                    "description": "Width of outlier curves (default: 1.0)",
                    "default": 1.0
                },
                "outliers_alpha": {
                    "type": "number",
                    "description": "Alpha transparency of outlier curves (default: 0.5)",
                    "default": 0.5
                },
                "method": {
                    "type": "string",
                    "description": "Band depth method - 'fdb' (functional band depth) or 'mfdb' (modified functional band depth) (default: 'fdb')",
                    "default": "fdb",
                    "enum": ["fdb", "mfdb"]
                }
            },
            "required": ["data_path"]
        }
    },
    {
        "name": "plot_curve_boxplot",
        "description": "Create a curve boxplot for ensemble curve data with multiple percentile bands",
        "parameters": {
            "type": "object",
            "properties": {
                "data_path": {
                    "type": "string",
                    "description": "Path to .npy file containing 3D curve ensemble (n_curves, n_steps, n_dims)"
                },
                "percentiles": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "List of percentiles for bands to be plotted (e.g., [25, 50, 90, 100])",
                    "default": [25, 50, 90, 100]
                },
                "percentile_colormap": {
                    "type": "string",
                    "description": "Colormap for percentile bands (e.g., 'viridis', 'plasma', 'inferno')",
                    "default": "viridis"
                },
                "show_median": {
                    "type": "boolean",
                    "description": "Whether to show median curve (default: True)",
                    "default": True
                },
                "median_color": {
                    "type": "string",
                    "description": "Color of median curve (default: 'red')",
                    "default": "red"
                },
                "median_width": {
                    "type": "number",
                    "description": "Width of median curve (default: 3.0)",
                    "default": 3.0
                },
                "median_alpha": {
                    "type": "number",
                    "description": "Alpha transparency of median curve (default: 1.0)",
                    "default": 1.0
                },
                "show_outliers": {
                    "type": "boolean",
                    "description": "Whether to show outlier curves (default: False)",
                    "default": False
                },
                "outliers_color": {
                    "type": "string",
                    "description": "Color of outlier curves (default: 'gray')",
                    "default": "gray"
                },
                "outliers_width": {
                    "type": "number",
                    "description": "Width of outlier curves (default: 1.0)",
                    "default": 1.0
                },
                "outliers_alpha": {
                    "type": "number",
                    "description": "Alpha transparency of outlier curves (default: 0.5)",
                    "default": 0.5
                },
                "workers": {
                    "type": "integer",
                    "description": "Number of parallel workers for band depth computation (default: 12)",
                    "default": 12
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
                "vectors_path": {
                    "type": "string",
                    "description": "Path to .npy file with ensemble vectors (n, m, 2)"
                },
                "positions_path": {
                    "type": "string",
                    "description": "Path to .npy file with glyph positions (n, 2)"
                },
                "percentile1": {
                    "type": "number",
                    "description": "First percentile for depth filtering (0 to 100), should be larger than percentile2",
                    "default": 90
                },
                "percentile2": {
                    "type": "number",
                    "description": "Second percentile for depth filtering (0 to 100), should be smaller than percentile1",
                    "default": 50
                },
                "scale": {
                    "type": "number",
                    "description": "Scale factor for glyph size",
                    "default": 0.2
                },
                "workers": {
                    "type": "integer",
                    "description": "Number of parallel workers for band depth computation (default: None, optimized for large data only)"
                }
            },
            "required": ["vectors_path", "positions_path"]
        }
    },
    {
        "name": "plot_contour_boxplot",
        "description": "Create a contour boxplot showing band depth of binary contours extracted from ensemble scalar fields",
        "parameters": {
            "type": "object",
            "properties": {
                "data_path": {
                    "type": "string",
                    "description": "Path to .npy file containing 3D scalar field ensemble (ny, nx, n_ensemble)"
                },
                "isovalue": {
                    "type": "number",
                    "description": "Threshold value for creating binary contours"
                },
                "percentiles": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "List of percentiles (0-100) for band envelope visualization",
                    "default": [25, 50, 75, 90]
                },
                "percentile_colormap": {
                    "type": "string",
                    "description": "Colormap for percentile bands (e.g., 'viridis', 'plasma', 'inferno')",
                    "default": "viridis"
                },
                "show_median": {
                    "type": "boolean",
                    "description": "Whether to show median contour (default: True)",
                    "default": True
                },
                "median_color": {
                    "type": "string",
                    "description": "Color of median contour (default: 'red')",
                    "default": "red"
                },
                "median_width": {
                    "type": "number",
                    "description": "Width of median contour (default: 3.0)",
                    "default": 3.0
                },
                "median_alpha": {
                    "type": "number",
                    "description": "Alpha transparency of median contour (default: 1.0)",
                    "default": 1.0
                },
                "show_outliers": {
                    "type": "boolean",
                    "description": "Whether to show outlier contours (default: False)",
                    "default": False
                },
                "outliers_color": {
                    "type": "string",
                    "description": "Color of outlier contours (default: 'gray')",
                    "default": "gray"
                },
                "outliers_width": {
                    "type": "number",
                    "description": "Width of outlier contours (default: 1.0)",
                    "default": 1.0
                },
                "outliers_alpha": {
                    "type": "number",
                    "description": "Alpha transparency of outlier contours (default: 0.5)",
                    "default": 0.5
                },
                "workers": {
                    "type": "integer",
                    "description": "Number of parallel workers for band depth computation (default: 12)",
                    "default": 12
                }
            },
            "required": ["data_path", "isovalue"]
        }
    }
]
