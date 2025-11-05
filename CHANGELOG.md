# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2025-11-05

### Added

**Comprehensive Test Coverage Infrastructure** - 89.29% overall coverage with 345 total tests

**Test Expansion:**
- **277 unit tests** (0 API calls) - up from 77
  - Added 200+ new unit tests across all core modules
  - Comprehensive coverage for core/, tools/, session/, errors/, utils/
  - Mock-based testing for error paths and edge cases
  - 100% coverage: routing.py, state.py, hybrid_control.py, logger.py, utils.py, error_tracking.py

- **53 integration tests** (~100 API calls)
  - **Layer 1**: Tool interface tests (21 tests) - Direct tool-to-UVisBox interface verification
    - Tests all 6 visualization modules with real UVisBox
    - Tests statistics tool output structure
    - Catches KEY_NOT_FOUND and API changes immediately
  - **Layer 2**: E2E pipeline tests (15 tests) - Complete user workflow verification
    - Tests all 6 visualization types end-to-end
    - Tests full analyzer pipeline (inline, quick, detailed)
    - Tests multi-turn workflows and session management
    - Verifies backward compatibility for users
  - Existing tests: analyzer_tool (3), hybrid_control (4), error_handling (6), session_management (3)

- **15 E2E tests** (~30 API calls)
  - matplotlib_behavior (3 tests)
  - analysis_workflows (12 tests)

**Coverage Achievements:**
```
Overall: 89.29%

Key modules:
- vis_tools.py:        96.69% ✅
- data_tools.py:       92.47% ✅
- statistics_tools.py: 92.92% ✅
- command_parser.py:   94.44% ✅
- routing.py:         100.00% ✅
- state.py:           100.00% ✅
- hybrid_control.py:  100.00% ✅
```

**Coverage Infrastructure:**
- `.coveragerc` configuration file with exclusion rules
- HTML coverage reports (`htmlcov/index.html`)
- Test runner `--coverage` flag for all test categories
- Mock-based testing strategy for error paths
- Documentation in TESTING.md

**Documentation:**
- Simplified TESTING.md from 819 to 438 lines (-47%)
- Clear structure: Quick Start, Test Structure, Test Roles, Code Coverage
- Removed rate limit references (kept 429 error handling)
- Added TDD workflow guidance for adding/modifying/removing features
- Two-layer integration test explanation

### Changed

**Project Restructure** - Feature-based directory architecture for improved code organization

**Directory Structure:**
- Reorganized 21 Python files from flat structure into 6 feature-based subdirectories:
  - `core/` - LangGraph workflow orchestration (graph, nodes, routing, state)
  - `tools/` - Data generation, visualization, statistics, and analysis tools
  - `session/` - User interaction and session management (conversation, hybrid control, command parser)
  - `llm/` - LLM configuration and model setup
  - `errors/` - Error handling infrastructure (tracking, interpretation)
  - `utils/` - Utilities and logging

**Backward Compatibility:**
- Root `__init__.py` re-exports all public APIs for backward compatibility
- Legacy imports (e.g., `from uvisbox_assistant import ConversationSession`) continue working
- New structured imports also supported (e.g., `from uvisbox_assistant.session import ConversationSession`)
- Git history fully preserved using `git mv` for all file moves

**Benefits:**
- Clear feature boundaries and single responsibility per directory
- Improved discoverability for new developers (3-4 files per directory vs 21 in one)
- Better scalability for future feature additions
- Reduced cognitive load
- Zero functional changes (pure structural refactoring)

**Testing:**
- ✅ All 345 tests pass (277 unit, 53 integration, 15 e2e)
- ✅ Backward compatibility verified with Layer 2 integration tests
- ✅ Import updates automated across 25 files (57 imports)

**Migration Tools:**
- `scripts/update_imports.py` - Automated import updater with dry-run mode
- `scripts/verify_compatibility.py` - Backward compatibility verification

### Technical Details

**Test Organization:**
```
tests/
├── unit/          277 tests (0 API calls, < 10 seconds)
├── integration/    53 tests (~100 API calls, 3-5 minutes)
├── e2e/            15 tests (~30 API calls, 2-3 minutes)
└── interactive/    Manual testing (24+ scenarios)
```

**Coverage Configuration:**
- Source: `src/uvisbox_assistant`
- Omit: Entry points, `__init__.py`, test files
- Precision: 2 decimal places
- Exclude lines: Debug code, abstract methods, defensive code

**Key Test Improvements:**
- Mock-based testing reaches 90%+ coverage (vs 60-70% without)
- All error handling paths tested
- Edge cases covered (empty data, boundary values, malformed inputs)
- UVisBox API changes detected immediately via Layer 1 tests

### Performance

- Unit tests: < 10 seconds (277 tests, 0 API calls)
- Integration tests: 3-5 minutes (53 tests, ~100 API calls)
- E2E tests: 2-3 minutes (15 tests, ~30 API calls)
- Total test suite: 8-10 minutes (345 tests, ~130 API calls)
- Coverage report generation: < 15 seconds

### Backward Compatibility

- ✅ Fully backward compatible
- ✅ No breaking changes to APIs or commands
- ✅ Layer 2 integration tests verify user-facing workflows
- ✅ All existing tests pass after restructure

## [0.3.0] - 2025-11-04

### Added

**Uncertainty Analysis System** - LLM-powered statistical analysis and report generation

**Core Features:**
- **Statistics Tool** (`statistics_tools.py`): Computes numerical summaries from functional boxplot data
  - `compute_functional_boxplot_statistics()` function with UVisBox integration
  - Median analysis: trend, slope, fluctuation, smoothness, value range
  - Band characteristics: widths, variation regions, uncertainty scores
  - Outlier analysis: count, similarity to median, clustering metrics
  - Returns structured JSON-serializable dict (no numpy arrays)

- **Analyzer Tool** (`analyzer_tools.py`): Generates natural language uncertainty reports
  - `generate_uncertainty_report()` function with three report formats
  - **Inline**: 1 sentence summary (~15-30 words)
  - **Quick**: 3-5 sentence overview (~50-100 words) - DEFAULT
  - **Detailed**: Full report with sections (~100-300 words)
  - Uses Gemini Flash Lite (temperature=0.3) for report generation
  - Report validation: word count checks, structure validation

- **Three Workflow Patterns**:
  1. **Visualization Only** (existing): `data_tool → vis_tool`
  2. **Text Analysis Only** (new): `data_tool → statistics_tool → analyzer_tool`
  3. **Combined Visualization + Analysis** (new): `data_tool → vis_tool → statistics_tool → analyzer_tool`

**Architecture Changes:**
- **5-node LangGraph**: Added `call_statistics_tool` and `call_analyzer_tool` nodes
- **State injection pattern**: Statistics automatically passed from state to analyzer
- **GraphState extensions**: Added `processed_statistics`, `analysis_report`, `analysis_type`, `_raw_statistics` fields
- **Enhanced routing**: Tool type detection now includes "statistics" and "analyzer" types
- **System prompt guidance**: Enforces REQUIRED sequence (statistics → analyzer)

**Testing:**
- **46 analysis-specific tests**: 25 statistics + 21 analyzer
- **12 E2E workflow tests**: Three workflow patterns with multi-turn conversations
- **77+ total unit tests** (0 API calls, instant execution)
- **Integration tests**: Real UVisBox and Gemini calls with report validation

**Documentation:**
- **`docs/ANALYSIS_EXAMPLES.md`**: 400+ lines covering all workflows, formats, examples
- **Outlier detection clarification**: Explains depth-based detection vs. percentile bands
- **Updated all docs**: README.md, API.md, TESTING.md with v0.3.0 info

### Changed

**Enhanced Modules:**
- `nodes.py`: Implements state injection in `call_analyzer_tool` node (lines 398-413)
- `model.py`: System prompt updated with workflow guidance and presentation instructions
- `conversation.py`: Added `get_analysis_summary()` method for analysis state tracking
- `state.py`: Added analysis-related state update functions
- `routing.py`: Updated tool type detection for analyzer routing
- `utils.py`: Added `is_statistics_tool()` and `is_analyzer_tool()` functions
- `graph.py`: Added statistics and analyzer nodes with conditional edges

**Tool Schemas:**
- Simplified analyzer schema: removed `statistics_summary` parameter (state injection instead)
- Statistics schema: clear documentation of required sequence
- Model binding: Now includes STATISTICS_TOOL_SCHEMAS + ANALYZER_TOOL_SCHEMAS

### Fixed

**Critical Bug Fixes:**
- **UVisBox API mismatch**: Changed `raw_stats["depth"]` → `raw_stats["depths"]` (plural)
  - Fixed in `statistics_tools.py` lines 298, 335
  - Updated all test mocks to use "depths"

- **Workflow routing issue**: Analyzer tool wasn't being called correctly
  - Root cause: Schema required manual statistics parameter
  - Solution: State injection + simplified schema

- **Report display issue**: Reports generated but not shown to user
  - Root cause: System prompt didn't instruct model to present reports
  - Solution: Added explicit presentation instructions in prompt

### Technical Details

**New Modules:**
- `src/uvisbox_assistant/statistics_tools.py` - Statistical analysis with UVisBox integration
- `src/uvisbox_assistant/analyzer_tools.py` - LLM-powered report generation

**Key Implementation Patterns:**
1. **Separation of Concerns**: Statistics (numerical) separate from analysis (language)
2. **State Injection**: Automatic parameter passing via GraphState
3. **Cost Efficiency**: Statistics computed once, multiple reports generated
4. **Zero-API Testing**: All statistics logic testable without LLM calls

**Outlier Detection (Important Clarification):**
- **Percentile bands** ≠ **Outliers**
- Percentiles show distribution (e.g., 90th percentile = deepest 90% of curves)
- Outliers use statistical fence: `depth < Q1 - 1.5×IQR`
- With similar curves → small IQR → low fence → fewer outliers
- Example: 100 curves with [25,50,75,90] percentiles may have 0 outliers (correct behavior)

**Prompt Engineering:**
- Three specialized templates (inline, quick, detailed)
- "No recommendations" constraint for descriptive-only reports
- Specific structure guidance for each format
- Word count validation to ensure format adherence

### Performance

- Statistics computation: < 1 second for 100 curves
- Report generation: ~1-2 seconds (Gemini Flash Lite call)
- Unit tests: 77+ tests in < 15 seconds (0 API calls)
- No impact on existing visualization workflows

### Backward Compatibility

- ✅ Fully backward compatible
- ✅ No breaking changes to existing commands or APIs
- ✅ Existing visualization workflows unchanged
- ✅ New analysis features are additive (opt-in)

---

## [0.2.0] - 2025-10-30

### Changed

**Rebrand: ChatUVisBox → UVisBox-Assistant**

This is a complete rebrand of the project. All functionality remains the same, but the package name and branding have changed.

**Breaking Changes:**
- Package name: `chatuvisbox` → `uvisbox_assistant`
- Entry point: `python -m chatuvisbox` → `python -m uvisbox_assistant`
- CLI command: `chatuvisbox` → `uvisbox-assistant`
- Log file location: `logs/chatuvisbox.log` → `logs/uvisbox_assistant.log`

**Migration Guide:**

For existing users upgrading from 0.1.x:

1. **Update imports** in your code:
   ```python
   # OLD
   from chatuvisbox import ConversationSession
   from chatuvisbox.graph import graph_app

   # NEW
   from uvisbox_assistant import ConversationSession
   from uvisbox_assistant.graph import graph_app
   ```

2. **Update entry point** usage:
   ```bash
   # OLD
   python -m chatuvisbox

   # NEW
   python -m uvisbox_assistant
   ```

3. **Update log file** references:
   ```python
   # OLD
   log_path = "logs/chatuvisbox.log"

   # NEW
   log_path = "logs/uvisbox_assistant.log"
   ```

4. **Reinstall** the package:
   ```bash
   pip uninstall chatuvisbox
   pip install uvisbox-assistant  # Or from source
   ```

**Why the rebrand?**
- Clearer naming: "UVisBox-Assistant" better describes the project as an assistant for UVisBox
- Consistency: Aligns with UVisBox naming convention
- Professionalism: Hyphenated name follows common assistant naming patterns

**No functional changes** - All features, APIs, and behavior remain identical to 0.1.2.

---

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
- UVisBox: https://github.com/ouermijudicael/UVisBox

[0.3.0]: https://github.com/yourusername/uvisbox-assistant/releases/tag/v0.3.0
[0.2.0]: https://github.com/yourusername/uvisbox-assistant/releases/tag/v0.2.0
[0.1.2]: https://github.com/yourusername/uvisbox-assistant/releases/tag/v0.1.2
[0.1.1]: https://github.com/yourusername/uvisbox-assistant/releases/tag/v0.1.1
[0.1.0]: https://github.com/yourusername/uvisbox-assistant/releases/tag/v0.1.0
