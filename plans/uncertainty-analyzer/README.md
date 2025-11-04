# Feature: Uncertainty Analyzer - Functional Boxplot

## Summary

Add text-based uncertainty analysis capabilities to UVisBox-Assistant by introducing two new LangGraph tool nodes:

1. **statistics_tool**: Processes `functional_boxplot_summary_statistics()` output from UVisBox into LLM-friendly structured summaries using statistical analysis (scipy/numpy/scikit-learn)
2. **analyzer_tool**: LLM-powered agent that generates natural language reports in three formats (inline/quick/detailed)

This feature enables users to request text summaries of uncertainty characteristics alongside or instead of visualizations, expanding the assistant's analytical capabilities while maintaining full backward compatibility with existing visualization workflows.

## Goals

- Enable text-based uncertainty analysis for functional boxplot data
- Support three report formats: inline (1 sentence), quick (3-5 sentences), detailed (full report)
- Integrate seamlessly with existing LangGraph workflow without breaking current functionality
- Provide statistical summaries: median behavior, band characteristics, outlier analysis
- Support three workflow patterns: vis-only (existing), text-only (new), combined text+vis (new)

## Success Criteria

- [ ] statistics_tool successfully processes functional_boxplot_summary_statistics() output
- [ ] analyzer_tool generates all three report formats correctly
- [ ] New workflow patterns work: text-only and combined text+vis
- [ ] All existing tests pass (100% backward compatibility)
- [ ] Unit tests for statistics_tool achieve 0 API calls
- [ ] Integration tests for analyzer_tool work with LLM
- [ ] Documentation updated with new capabilities
- [ ] CLAUDE.md updated with architecture patterns and pitfalls

## Implementation Phases

### Phase 1: Foundation and State Extension
- **File**: `phases_1.md`
- **Goal**: Extend GraphState and create statistics_tools.py foundation
- **Status**: Planned
- **Estimated Effort**: 2-3 hours

### Phase 2: Statistics Tool Implementation
- **File**: `phases_2.md`
- **Goal**: Implement statistical analysis functions with comprehensive testing
- **Status**: Planned
- **Estimated Effort**: 4-5 hours

### Phase 3: Analyzer Tool Implementation
- **File**: `phases_3.md`
- **Goal**: Create LLM-powered analyzer with report generation
- **Status**: Planned
- **Estimated Effort**: 3-4 hours

### Phase 4: Graph Integration and Routing
- **File**: `phases_4.md`
- **Goal**: Integrate new nodes into LangGraph workflow with routing logic
- **Status**: Planned
- **Estimated Effort**: 4-5 hours

### Phase 5: Multi-Workflow Support
- **File**: `phases_5.md`
- **Goal**: Enable all three workflow patterns with comprehensive testing
- **Status**: Planned
- **Estimated Effort**: 3-4 hours

### Phase 6: Documentation and Release
- **File**: `phases_6.md`
- **Goal**: Update all documentation for v0.3.0 release
- **Status**: Planned
- **Estimated Effort**: 2-3 hours

## Dependencies

### External
- UVisBox library with `functional_boxplot_summary_statistics()` function
- scipy (for statistical analysis)
- numpy (for numerical computations)
- scikit-learn (for similarity metrics)
- langchain-google-genai (for analyzer LLM)

### Internal
- Existing GraphState and LangGraph workflow
- Tool registration pattern (DATA_TOOLS, VIS_TOOLS)
- Node implementation pattern (call_data_tool, call_vis_tool)
- Routing logic pattern (route_after_model, route_after_tool)

## Timeline

**Total Estimated Duration**: 18-24 hours of development + testing

**Breakdown**:
- Phase 1 (Foundation): 2-3 hours
- Phase 2 (Statistics): 4-5 hours
- Phase 3 (Analyzer): 3-4 hours
- Phase 4 (Integration): 4-5 hours
- Phase 5 (Multi-Workflow): 3-4 hours
- Phase 6 (Documentation): 2-3 hours

**Suggested Sprint Structure**:
- Week 1: Phases 1-2 (Foundation + Statistics)
- Week 2: Phases 3-4 (Analyzer + Integration)
- Week 3: Phases 5-6 (Multi-Workflow + Documentation)

## Architecture Overview

### New State Fields

```python
class GraphState(TypedDict):
    # Existing fields...
    messages: Annotated[List[BaseMessage], operator.add]
    current_data_path: Optional[str]
    last_vis_params: Optional[dict]
    session_files: List[str]
    error_count: int

    # New fields for uncertainty analysis
    summary_statistics: Optional[dict]      # Raw UVisBox output
    statistics_summary: Optional[dict]      # LLM-friendly structured summary
    analysis_report: Optional[str]          # Generated text report
    analysis_type: Optional[str]            # "inline" | "quick" | "detailed" | None
```

### New Tool Nodes

```
statistics_tool (call_statistics_tool)
├─ Input: current_data_path
├─ Process: functional_boxplot_summary_statistics()
├─ Analyze: median/band/outlier statistics
└─ Output: structured dict → statistics_summary

analyzer_tool (call_analyzer_tool)
├─ Input: statistics_summary + analysis_type
├─ Process: LLM with specialized prompts
├─ Generate: text report
└─ Output: analysis_report
```

### Workflow Patterns

**Pattern 1: Text-Only Analysis**
```
User: "generate curves and analyze uncertainty"
Flow: data_tool → statistics_tool → analyzer_tool → END
```

**Pattern 2: Combined Text + Visualization**
```
User: "generate curves, plot boxplot, and create summary"
Flow: data_tool → vis_tool → statistics_tool → analyzer_tool → END
```

**Pattern 3: Existing (Visualization Only)**
```
User: "generate curves and plot them"
Flow: data_tool → vis_tool → END
```

## Technical Constraints

### Backward Compatibility Requirements
- Existing tool functions unchanged
- Existing tests must pass
- Hybrid control system unchanged
- No breaking changes to GraphState structure (only additions)

### Testing Requirements
- Statistics tool: Unit tests only (0 API calls)
- Analyzer tool: Integration tests (uses LLM, manages API budget)
- Workflow tests: E2E tests for all three patterns
- Regression tests: All existing tests must pass

### Scope Limitations
- v0.3.0: Functional boxplot ONLY
- Future versions: Extend to curve_boxplot, contour_boxplot, etc.
- No recommendations in reports (descriptive only)

## Risk Analysis

### High Risk
- **Graph routing complexity**: Multiple tool paths may require careful edge configuration
  - Mitigation: Detailed routing logic specification in Phase 4

### Medium Risk
- **API rate limits**: Analyzer tool uses LLM calls
  - Mitigation: Use gemini-2.0-flash-lite (30 RPM), test with delays

- **State bloat**: Adding multiple new fields to GraphState
  - Mitigation: Use Optional types, clear documentation

### Low Risk
- **Statistical analysis accuracy**: scipy/numpy/scikit-learn are mature libraries
- **Backward compatibility**: Additive changes only, no modifications to existing code

## Notes

- This feature is the first step toward comprehensive uncertainty analysis
- Future extensions will add support for other visualization types
- The analyzer LLM approach provides flexibility for natural language output
- Statistical analysis is deterministic and fast (unit testable)
- LLM analysis provides interpretability but requires API budget management
