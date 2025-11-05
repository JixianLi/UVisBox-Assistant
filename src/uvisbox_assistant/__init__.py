"""
UVisBox-Assistant - Natural language interface for UVisBox uncertainty visualization.

This package uses a feature-based architecture with backward-compatible imports.

Public API Structure:
- Core workflow: graph_app, create_graph
- Session management: ConversationSession
- Tools: All data and visualization tools
- Error handling: ErrorRecord
"""

# Core workflow (from core/)
from uvisbox_assistant.core.graph import graph_app, create_graph

# Session management (from session/)
from uvisbox_assistant.session.conversation import ConversationSession

# Data tools (from tools/)
from uvisbox_assistant.tools.data_tools import (
    generate_ensemble_curves,
    generate_scalar_field_ensemble,
    generate_vector_field_ensemble,
    load_csv_to_numpy,
    load_npy,
    clear_session,
)

# Visualization tools (from tools/)
from uvisbox_assistant.tools.vis_tools import (
    plot_functional_boxplot,
    plot_curve_boxplot,
    plot_probabilistic_marching_squares,
    plot_contour_boxplot,
    plot_uncertainty_lobes,
    plot_squid_glyph_2D,
)

# Statistics tools (from tools/, v0.3.0)
from uvisbox_assistant.tools.statistics_tools import (
    compute_functional_boxplot_statistics,
)

# Analyzer tools (from tools/, v0.3.0)
from uvisbox_assistant.tools.analyzer_tools import (
    generate_uncertainty_report,
)

# Error tracking (from errors/, v0.1.2)
from uvisbox_assistant.errors.error_tracking import ErrorRecord

# Configuration (root)
from uvisbox_assistant.config import (
    GEMINI_API_KEY,
    TEMP_DIR,
    TEST_DATA_DIR,
    LOG_DIR,
    DEFAULT_VIS_PARAMS,
)

__all__ = [
    # Core
    "graph_app",
    "create_graph",
    # Session
    "ConversationSession",
    # Data Tools
    "generate_ensemble_curves",
    "generate_scalar_field_ensemble",
    "generate_vector_field_ensemble",
    "load_csv_to_numpy",
    "load_npy",
    "clear_session",
    # Visualization Tools
    "plot_functional_boxplot",
    "plot_curve_boxplot",
    "plot_probabilistic_marching_squares",
    "plot_contour_boxplot",
    "plot_uncertainty_lobes",
    "plot_squid_glyph_2D",
    # Statistics Tools
    "compute_functional_boxplot_statistics",
    # Analyzer Tools
    "generate_uncertainty_report",
    # Error Tracking
    "ErrorRecord",
    # Config
    "GEMINI_API_KEY",
    "TEMP_DIR",
    "TEST_DATA_DIR",
    "LOG_DIR",
    "DEFAULT_VIS_PARAMS",
]

__version__ = "0.3.1"
