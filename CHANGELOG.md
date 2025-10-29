# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-29

### Added
- **Natural language interface** for UVisBox uncertainty visualization library
- **5 Visualization types**:
  - Functional boxplot (1D curve ensembles with band depth)
  - Curve boxplot (depth-colored curves with parallel processing)
  - Contour boxplot (contour band depth from scalar field ensembles)
  - Probabilistic marching squares (2D scalar field uncertainty)
  - Uncertainty lobes (directional uncertainty for vector fields)
- **BoxplotStyleConfig Interface**: Full control over median and outliers styling
  - Percentile bands: `percentiles` (list), `percentile_colormap` (str)
  - Median styling: `show_median`, `median_color`, `median_width`, `median_alpha`
  - Outliers styling: `show_outliers`, `outliers_color`, `outliers_width`, `outliers_alpha`
  - Parallel processing: `workers` parameter for curve_boxplot and contour_boxplot (default: 12)
- **Hybrid control system** for fast parameter updates:
  - 13+ command patterns for instant visualization adjustments
  - 10-15x faster than full LLM workflow (~0.12s vs ~1.65s)
  - Basic commands: `colormap <name>`, `percentile <number>`, `isovalue <number>`
  - Toggle commands: `show median`, `hide median`, `show outliers`, `hide outliers`
  - Median styling: `median color <color>`, `median width <number>`, `median alpha <number>`
  - Outliers styling: `outliers color <color>`, `outliers width <number>`, `outliers alpha <number>`
  - Other: `scale <number>`, `alpha <number>`
- **LangGraph workflow orchestration**:
  - StateGraph with 3 nodes: call_model, call_data_tool, call_vis_tool
  - Conditional routing based on tool calls
  - Multi-turn conversation support with context preservation
- **Data generation tools**:
  - `generate_ensemble_curves()` - Synthetic 1D curve ensembles
  - `generate_scalar_field_ensemble()` - 2D Gaussian fields with systematic uncertainty
  - `generate_vector_field_ensemble()` - 2D vector fields with directional variation
  - `load_csv_to_numpy()` - CSV to NumPy conversion
  - `load_npy()` - Load existing NumPy arrays
- **Session management**:
  - `ConversationSession` class for multi-turn interactions
  - `clear_session()` tool for automatic temp file cleanup
  - Session statistics tracking (files created, API calls, etc.)
  - REPL commands: `/help`, `/context`, `/stats`, `/clear`, `/reset`, `/quit`
- **Error handling and recovery**:
  - Circuit breaker (max 3 consecutive errors)
  - Error recovery with LLM suggestions
  - Context-aware file suggestions on errors
  - Comprehensive logging to `logs/chatuvisbox.log`
- **Comprehensive test suite**:
  - Category-based organization: unit/integration/e2e/interactive
  - 45+ unit tests (0 API calls, instant execution)
  - Integration tests for workflows
  - E2E tests for complete scenarios
  - Interactive testing menu for exploration
  - Test runner with category flags: `--unit`, `--integration`, `--e2e`, `--quick`
- **Complete documentation**:
  - `README.md` - Project overview and quick start
  - `docs/USER_GUIDE.md` - Detailed styling examples and workflows
  - `docs/API.md` - Complete API reference
  - `CLAUDE.md` - Implementation details for AI agents
  - `TESTING.md` - Comprehensive testing strategies
  - `CONTRIBUTING.md` - Contribution guidelines
  - `LICENSE` - MIT License

### Technical Details
- **Python**: 3.10-3.13 support
- **LLM**: Google Gemini (gemini-2.0-flash-lite)
- **Framework**: LangGraph + LangChain
- **Visualization**: UVisBox + Matplotlib
- **Package**: Poetry-based project structure with src layout
- **Dependencies**:
  - `langgraph>=0.2.76`
  - `langchain>=0.3.27`
  - `langchain-google-genai>=2.1.12`
  - `langsmith>=0.4.38`
  - `numpy>=2.0`
  - `pandas>=2.3.3`
  - `matplotlib>=3.10.7`
  - `uvisbox` (installed separately)

---

## Links

- Repository: TBD
- Documentation: `docs/`
- Issue Tracker: TBD
- UVisBox: https://github.com/VCCRI/UVisBox

[0.1.0]: https://github.com/yourusername/chatuvisbox/releases/tag/v0.1.0
