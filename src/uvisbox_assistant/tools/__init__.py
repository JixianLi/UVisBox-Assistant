"""Data generation and visualization tools."""

from uvisbox_assistant.tools.data_tools import (
    generate_ensemble_curves,
    generate_3d_trajectory_ensemble,
    generate_scalar_field_ensemble,
    generate_3d_scalar_field_ensemble,
    generate_vector_field_ensemble,
    load_csv_to_numpy,
    load_npy,
    clear_session,
    DATA_TOOL_SCHEMAS,
)

from uvisbox_assistant.tools.vis_tools import (
    plot_functional_boxplot,
    plot_curve_boxplot,
    plot_probabilistic_marching_squares,
    plot_probabilistic_marching_cubes,
    plot_uncertainty_tubes,
    plot_contour_boxplot,
    plot_uncertainty_lobes,
    plot_squid_glyph_2D,
    VIS_TOOL_SCHEMAS,
)

__all__ = [
    # Data tools
    "generate_ensemble_curves",
    "generate_3d_trajectory_ensemble",
    "generate_scalar_field_ensemble",
    "generate_3d_scalar_field_ensemble",
    "generate_vector_field_ensemble",
    "load_csv_to_numpy",
    "load_npy",
    "clear_session",
    "DATA_TOOL_SCHEMAS",
    # Visualization tools
    "plot_functional_boxplot",
    "plot_curve_boxplot",
    "plot_probabilistic_marching_squares",
    "plot_probabilistic_marching_cubes",
    "plot_uncertainty_tubes",
    "plot_contour_boxplot",
    "plot_uncertainty_lobes",
    "plot_squid_glyph_2D",
    "VIS_TOOL_SCHEMAS",
]
