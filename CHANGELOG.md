# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-01-30

### Added

**Debug Mode** - Comprehensive error debugging capabilities
- `/debug on/off` command to toggle verbose error output
- Full stack trace capture for all tool errors
- Error history tracking (up to 20 recent errors)
- `/errors` command to list error history with IDs
- `/trace <id>` command to view full stack trace for specific error
- `ErrorRecord` class for structured error storage (`src/chatuvisbox/error_tracking.py`)
- `ConversationSession.record_error()`, `get_error()`, and `get_last_error()` methods

**Verbose Mode** - Internal execution visibility
- `/verbose on/off` command to toggle internal state messages
- `vprint()` utility function for conditional output
- Output control module (`src/chatuvisbox/output_control.py`)
- Shows `[HYBRID]`, `[DATA TOOL]`, and `[VIS TOOL]` messages when enabled
- Independent from debug mode (can enable/disable separately)
- Clean conversation output by default (verbose OFF)

**Error Interpretation** - Context-aware error hints
- Automatic error pattern detection (colormap, method, shape, file, import errors)
- Debug hints for common UVisBox integration issues
- Colormap error detection with matplotlib compatibility notes
- Method validation error detection with valid options
- Shape mismatch error detection with dimension information
- Error interpretation module (`src/chatuvisbox/error_interpretation.py`)

**Auto-Fix Detection** - Track agent self-correction
- Tool execution sequence tracking in GraphState
- Automatic detection of error → retry → success patterns
- Auto-fix status shown in error history (`auto-fixed ✓`)
- `/errors` and `/trace` commands show auto-fix status

**Enhanced Commands**
- `/context` now shows debug and verbose mode states
- `/help` updated with debug and verbose command documentation
- Error count and error history summary in `/context` output

### Changed

- All internal debug print statements converted to `vprint()` for verbose control
- Error handling in all tool functions enhanced to capture full tracebacks
- Tool return format includes optional `_error_details` dict for error tracking
- `ConversationSession` now has `debug_mode` and `verbose_mode` flags
- Logger now only writes to file (`logs/chatuvisbox.log`), console controlled by verbose mode
- GraphState expanded with `tool_execution_sequence`, `last_error_tool`, `last_error_id` fields

### Technical Details

**New Modules:**
- `src/chatuvisbox/error_tracking.py` - ErrorRecord dataclass and error storage
- `src/chatuvisbox/output_control.py` - Verbose mode output control
- `src/chatuvisbox/error_interpretation.py` - Error pattern detection and hints

**Updated Modules:**
- `src/chatuvisbox/conversation.py` - Error tracking, auto-fix detection, mode flags
- `src/chatuvisbox/state.py` - Auto-fix tracking fields
- `src/chatuvisbox/nodes.py` - Tool execution tracking, auto-fix detection
- `src/chatuvisbox/hybrid_control.py` - vprint() integration
- `src/chatuvisbox/main.py` - Debug/verbose/error tracking command handlers
- `src/chatuvisbox/logger.py` - File-only logging (no console output)
- `src/chatuvisbox/vis_tools.py` - Enhanced error handling with traceback capture
- `src/chatuvisbox/data_tools.py` - Enhanced error handling with traceback capture

**New Tests:**
- `tests/unit/test_error_tracking.py` - 12 unit tests (0 API calls)
- `tests/unit/test_output_control.py` - 5 unit tests (0 API calls)
- `tests/unit/test_error_interpretation.py` - 11 unit tests (0 API calls)
- `tests/unit/test_command_handlers.py` - 21 unit tests (0 API calls)

**Total: 49 new unit tests, all with 0 API calls**

### Performance

- vprint overhead < 5% when verbose mode OFF
- Error recording < 1ms per error
- No noticeable conversation slowdown
- Minimal memory overhead (max 20 errors stored)

### Backward Compatibility

- ✅ Fully backward compatible
- ✅ Both modes OFF by default (existing behavior preserved)
- ✅ No breaking changes to existing commands or APIs
- ✅ Optional `_error_details` in tool returns (backward compatible)

## [0.1.1] - 2025-01-29

### Added
- **Squid Glyph 2D visualization**: 2D vector uncertainty visualization using squid-shaped glyphs with depth-based filtering
  - `plot_squid_glyph_2D()` function with parameters: `percentile` (0-100, default: 95), `scale`, `workers`
  - Single percentile parameter for depth-based filtering (vs. dual percentiles in uncertainty_lobes)
  - Configuration defaults: `squid_percentile`, `squid_scale`, `squid_workers`
  - Hybrid control support for `percentile` and `scale` parameters
  - Now supports **6 visualization types** (up from 5)

### Changed
- Updated `functional_boxplot` to include `method` parameter ('fbd' or 'mfbd')
- Updated `uncertainty_lobes` to include `workers` parameter for parallel computation
- Hybrid control system now handles both `percentiles` (list) and `percentile` (single value)
- Command parser updated to support 16 patterns (includes new `method` command)

### Fixed
- `/help` command now displays all 6 visualizations (was missing squid_glyph_2D)
- `/help` command now shows all 16 hybrid control commands (was only showing 5)
- Improved help formatting with organized sections: Basic, Median Styling, Outliers Styling
- Welcome banner updated with squid glyph example
- **Removed parameter duplication** - `DEFAULT_VIS_PARAMS` now only contains `figsize` and `dpi`
  - All visualization-specific defaults are now in function signatures only (single source of truth)
  - Prevents config/API mismatch and reduces maintenance burden
  - Config tests updated to verify this architectural decision (5 tests, down from 9)

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
