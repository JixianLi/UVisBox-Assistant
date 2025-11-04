# Uncertainty Analysis Examples

This guide demonstrates how to use UVisBox-Assistant's uncertainty analysis features to generate both visualizations and natural language reports.

## Quick Start

### Pattern 1: Visualization Only (Existing)

The traditional workflow for creating visualizations without text analysis:

```python
from uvisbox_assistant.conversation import ConversationSession

session = ConversationSession()
session.send("Generate 50 curves and plot functional boxplot")
```

This creates:
- Data generation
- Functional boxplot visualization
- No statistical analysis or text report

### Pattern 2: Text Analysis Only (New)

Generate statistical analysis and text reports without visualization:

```python
session = ConversationSession()
session.send("Generate 50 curves and create a quick uncertainty analysis")
```

This creates:
- Data generation
- Statistical summary (median trends, band characteristics, outliers)
- Natural language analysis report
- No visualization

### Pattern 3: Combined Visualization + Analysis (New)

Create both visualizations and analysis reports in a single workflow:

```python
session = ConversationSession()
session.send("Generate 50 curves, plot boxplot, and create detailed analysis")
```

This creates:
- Data generation
- Functional boxplot visualization
- Statistical summary
- Detailed analysis report

## Analysis Report Formats

UVisBox-Assistant supports three report formats with different levels of detail.

### Inline (1 sentence)

Inline reports provide a single concise sentence summarizing uncertainty level:

```python
session.send("Generate 30 curves and give me an inline uncertainty summary")
```

**Example output:**
> "This ensemble shows moderate uncertainty with 15% band width variation and 2 outliers."

**Characteristics:**
- 1 sentence only
- ~15-30 words
- Mentions overall uncertainty level (low/moderate/high)
- Quick snapshot of key metrics

### Quick (3-5 sentences)

Quick reports provide a brief overview covering main uncertainty characteristics:

```python
session.send("Generate 30 curves and create a quick analysis")
```

**Example output:**
> "The ensemble exhibits moderate uncertainty with 30 curves showing consistent trends. The median curve displays an increasing trend with a slope of 0.05 and smooth behavior. Percentile bands show an average width of 1.2 units with widest regions near indices 45-55. Two outliers were detected with 65% similarity to the median curve."

**Characteristics:**
- 3-5 sentences
- ~50-100 words
- Covers median behavior, band characteristics, and outliers
- Balanced detail for quick understanding

### Detailed (Full report)

Detailed reports provide comprehensive analysis with structured sections:

```python
session.send("Generate 30 curves and create a detailed uncertainty report")
```

**Example structure:**

```
## Median Behavior
The median curve exhibits an increasing trend with an overall slope of 0.048...

## Band Characteristics
The ensemble shows moderate uncertainty with band widths ranging from...

## Outlier Analysis
Three outliers were identified representing 10% of the ensemble...

## Overall Assessment
This ensemble demonstrates moderate to high uncertainty...
```

**Characteristics:**
- 100+ words
- Structured sections (Median Behavior, Band Characteristics, Outlier Analysis, Overall Assessment)
- Comprehensive coverage of all statistical summaries
- Includes specific numbers and metrics

## Multi-Turn Workflows

### Incremental Analysis

Build analysis step-by-step across multiple conversation turns:

```python
session = ConversationSession()

# Step 1: Load data
session.send("Load test_data/sample_curves.npy")

# Step 2: Compute statistics
session.send("Compute statistics for this data")

# Step 3: Generate report
session.send("Create a quick analysis report")

# Step 4: Visualize (optional)
session.send("Now plot it")
```

This allows you to:
- Inspect intermediate results
- Make decisions at each step
- Combine analysis with visualization later

### Refining Analysis

Start with a brief summary, then request more detail:

```python
session = ConversationSession()

# Start with quick overview
session.send("Generate curves and give me a quick summary")

# Request more detail
session.send("That's interesting, give me a detailed report")

# Add visualization
session.send("Now show me the boxplot")
```

### Analysis-First, Visualization-Second

Analyze data first, then visualize based on findings:

```python
session = ConversationSession()

# Analyze first
session.send("Generate 30 curves and create detailed analysis")

# Review analysis, then visualize
session.send("Now plot it as functional boxplot")

# Try different visualization
session.send("Show it as curve boxplot instead")
```

## Checking Analysis State

### Get Context Summary

Check what analysis has been performed:

```python
context = session.get_context_summary()
print(f"Statistics: {context['statistics']}")  # "computed" or None
print(f"Analysis: {context['analysis']}")      # "inline", "quick", "detailed", or None
print(f"Visualization: {context['last_vis']}") # Tool name or None
```

### Get Analysis Details

View detailed information about current analysis:

```python
analysis_summary = session.get_analysis_summary()
if analysis_summary:
    print(analysis_summary)
```

**Example output:**
```
📊 Analysis State:
  ✓ Statistics computed: 30 curves, 100 points
  - Median trend: increasing
  - Outliers: 2
  ✓ Report generated: quick (87 words)
  - Preview: This ensemble shows moderate uncertainty with consistent trends. The median curve...
```

## Workflow Examples

### Example 1: Quick Data Exploration

Quickly understand uncertainty in a dataset:

```python
session = ConversationSession()
session.send("Load test_data/sample_curves.npy and give me an inline summary")
```

**Output:** One-sentence summary in seconds.

### Example 2: Comprehensive Analysis

Thorough analysis for publication or reporting:

```python
session = ConversationSession()
session.send("""
Generate 50 curves, plot functional boxplot with 90th percentile,
and create detailed uncertainty report
""")
```

**Output:** Visualization + full analysis report.

### Example 3: Comparative Analysis

Analyze multiple datasets:

```python
session = ConversationSession()

# Dataset 1
session.send("Load dataset1.npy and create quick analysis")
report1 = session.state["analysis_report"]

# Dataset 2
session.send("Load dataset2.npy and create quick analysis")
report2 = session.state["analysis_report"]

# Compare reports
print("Dataset 1:", report1)
print("Dataset 2:", report2)
```

### Example 4: Interactive Refinement

Refine analysis interactively:

```python
session = ConversationSession()

# Start broad
session.send("Generate curves and analyze")

# Get specific
session.send("Tell me more about the outliers")

# Visualize problem areas
session.send("Plot the outliers separately")
```

## Natural Language Keywords

The system recognizes these keywords for analysis requests:

**For text analysis:**
- "analyze"
- "summary"
- "statistics"
- "uncertainty characteristics"
- "report"

**For report formats:**
- "inline" → 1-sentence summary
- "quick" → 3-5 sentence overview
- "detailed" → Full report with sections

**For combined workflows:**
- "plot and analyze" → Visualization + analysis
- "visualize and summarize" → Visualization + analysis
- "show me and tell me about" → Visualization + analysis

## Tips and Best Practices

1. **Start small**: Begin with inline or quick reports to get a feel for the data

2. **Combine when needed**: Use combined workflows when you need both visual and textual understanding

3. **Multi-turn flexibility**: Break complex analyses into multiple turns for better control

4. **Check context**: Use `get_context_summary()` to verify what analysis has been performed

5. **Format selection**: Choose format based on audience:
   - Inline: Quick checks, dashboards
   - Quick: Team communications, slack messages
   - Detailed: Reports, documentation, publications

6. **Reuse data**: Once data is loaded, you can request multiple analyses without reloading

7. **Visualization independence**: Analysis and visualization are independent - you can do either without the other

## Error Handling

If analysis fails, the system will provide helpful error messages:

```python
session.send("Analyze nonexistent.npy")
# Error: File not found. Available files: sample_curves.npy, sample_scalar_field.npy
```

The system will:
- Explain what went wrong
- Suggest available alternatives
- Maintain conversation state for retry

## Performance Notes

**Timing estimates:**
- Data generation: ~0.5-1s
- Statistics computation: ~1-2s
- Report generation (inline): ~2-3s
- Report generation (quick/detailed): ~3-5s
- Visualization: ~1-2s

**Rate limits:**
- Gemini API: 30 requests per minute (free tier)
- Use delays between rapid-fire requests
- Tests include automatic rate limiting

## Advanced Usage

### Programmatic Access to Results

Access analysis results directly from state:

```python
# Get processed statistics
stats = session.state["processed_statistics"]
n_curves = stats["data_shape"]["n_curves"]
median_trend = stats["median"]["trend"]
outlier_count = stats["outliers"]["count"]

# Get analysis report
report = session.state["analysis_report"]
analysis_type = session.state["analysis_type"]
```

### Custom Workflows

Combine with other tools:

```python
# Generate report and save to file
session.send("Generate curves and create detailed report")
report = session.state["analysis_report"]

with open("uncertainty_report.txt", "w") as f:
    f.write(report)
```

## See Also

- [User Guide](USER_GUIDE.md) - Complete usage documentation
- [API Reference](API.md) - Full API documentation
- [Testing Guide](../TESTING.md) - Testing strategies and examples
- [CLAUDE.md](../CLAUDE.md) - Development guidelines
