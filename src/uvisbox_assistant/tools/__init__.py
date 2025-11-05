"""Data generation, visualization, statistics, and analysis tools."""

from uvisbox_assistant.tools.data_tools import (
    generate_ensemble_curves,
    generate_scalar_field_ensemble,
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
    plot_contour_boxplot,
    plot_uncertainty_lobes,
    plot_squid_glyph_2D,
    VIS_TOOL_SCHEMAS,
)

from uvisbox_assistant.tools.statistics_tools import (
    compute_functional_boxplot_statistics,
    STATISTICS_TOOL_SCHEMAS,
)

from uvisbox_assistant.tools.analyzer_tools import (
    generate_uncertainty_report,
    ANALYZER_TOOL_SCHEMAS,
)

__all__ = [
    # Data tools
    "generate_ensemble_curves",
    "generate_scalar_field_ensemble",
    "generate_vector_field_ensemble",
    "load_csv_to_numpy",
    "load_npy",
    "clear_session",
    "DATA_TOOL_SCHEMAS",
    # Visualization tools
    "plot_functional_boxplot",
    "plot_curve_boxplot",
    "plot_probabilistic_marching_squares",
    "plot_contour_boxplot",
    "plot_uncertainty_lobes",
    "plot_squid_glyph_2D",
    "VIS_TOOL_SCHEMAS",
    # Statistics tools
    "compute_functional_boxplot_statistics",
    "STATISTICS_TOOL_SCHEMAS",
    # Analyzer tools
    "generate_uncertainty_report",
    "ANALYZER_TOOL_SCHEMAS",
]
