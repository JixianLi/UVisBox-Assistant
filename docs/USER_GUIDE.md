# ChatUVisBox User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Advanced Styling Control](#advanced-styling-control)
3. [Quick Styling Examples](#quick-styling-examples)
4. [Hybrid Control vs Full Commands](#hybrid-control-vs-full-commands)
5. [Performance Tuning](#performance-tuning)
6. [Tips for Styling](#tips-for-styling)
7. [Common Workflows](#common-workflows)
8. [Troubleshooting](#troubleshooting)

## Getting Started

ChatUVisBox provides a natural language interface for creating uncertainty visualizations. You can describe what you want in plain English, and the system will translate your request into appropriate data processing and visualization operations.

### Basic Usage Pattern

```
You: Generate 30 curves and plot functional boxplot
Assistant: [creates data and displays visualization]

You: median color blue
Assistant: [updates median to blue instantly]

You: show outliers
Assistant: [adds outliers to the plot]
```

## Advanced Styling Control

### BoxplotStyleConfig Parameters

ChatUVisBox provides fine-grained control over boxplot visualizations through 10 styling parameters:

#### Percentile Bands
- **percentiles**: List of percentile values (e.g., [25, 50, 75, 90])
- **percentile_colormap**: Colormap for bands ('viridis', 'plasma', 'inferno', etc.)

#### Median Curve Styling
- **show_median**: Show/hide median curve (default: True)
- **median_color**: Color of median curve (default: 'red')
- **median_width**: Line width of median (default: 3.0)
- **median_alpha**: Transparency of median (default: 1.0)

#### Outliers Styling
- **show_outliers**: Show/hide outlier curves (default: False)
- **outliers_color**: Color of outlier curves (default: 'gray')
- **outliers_width**: Line width of outliers (default: 1.0)
- **outliers_alpha**: Transparency of outliers (default: 0.5)

#### Performance
- **workers**: Number of parallel workers for band depth (default: 12)

## Quick Styling Examples

### Example 1: Customize Median Appearance

```
You: Generate curves and plot
Assistant: [shows plot with red median]

You: median color blue
Assistant: [updates median to blue]

You: median width 4.0
Assistant: [makes median thicker]

You: median alpha 0.7
Assistant: [makes median semi-transparent]
```

### Example 2: Show and Style Outliers

```
You: show outliers
Assistant: [displays outliers in gray]

You: outliers color darkred
Assistant: [changes outliers to dark red]

You: outliers width 2.0
Assistant: [makes outliers thicker]

You: outliers alpha 1.0
Assistant: [makes outliers fully opaque]
```

### Example 3: Full Customization

```
You: Generate 30 curves and plot functional boxplot with percentiles 10, 50, 90, percentile colormap plasma, median color blue, median width 2.5, show outliers, outliers color black, outliers alpha 0.8
Assistant: [creates fully customized visualization]
```

## Hybrid Control vs Full Commands

### Fast (Hybrid Control)

**Single parameter updates** - processed instantly without LLM:
- `median color blue` - Instant update
- `outliers alpha 1.0` - Instant update
- `colormap plasma` - Instant update
- Single parameter at a time
- **Speed**: ~0.12 seconds (10-15x faster)

### Full Command

**Complex natural language** - processed through LLM:
- "Plot with median color blue and outliers color black" - Uses LLM
- "Make it look better" - Uses LLM interpretation
- Multiple parameters in natural language
- More flexible but slightly slower
- **Speed**: ~1.65 seconds

### When to Use Each

**Use Hybrid Control when:**
- You know exactly what parameter to change
- You want instant feedback
- You're fine-tuning a visualization iteratively

**Use Full Commands when:**
- You're describing what you want conceptually
- You want to change multiple things at once
- You're not sure of the exact parameter names

## Performance Tuning

### Parallel Processing for Large Datasets

For large datasets (>100 ensemble members), you can adjust the number of workers used for band depth computation:

```
You: Plot curve boxplot with 4 workers
Assistant: [uses 4 threads for band depth]

You: Try with 16 workers
Assistant: [uses 16 threads, faster on multi-core systems]
```

**Guidelines:**
- Default: 12 workers
- For small datasets (<50 members): 4-8 workers
- For large datasets (>100 members): 12-16 workers
- Optimal value depends on your CPU cores
- Diminishing returns beyond 16 workers

## Tips for Styling

### Tip 1: Start with Defaults, Then Refine

The iterative approach works best:

```
1. Generate and visualize (uses defaults)
2. Evaluate what you want to change
3. Apply specific styling commands one at a time
4. Iterate until satisfied
```

### Tip 2: Use Contrasting Colors

Good color combinations for visibility:

```
Good: median color blue + outliers color red
Good: median color white + outliers color black (on dark plots)
Good: median color red + outliers color gray (default)
```

Avoid similar colors that blend together:
```
Avoid: median color blue + outliers color cyan
Avoid: median color red + outliers color orange
```

### Tip 3: Adjust Transparency for Overlays

When showing both median and outliers:

```
Strategy 1: Emphasize median
- median alpha 1.0 (fully opaque)
- outliers alpha 0.3 (semi-transparent)

Strategy 2: Equal importance
- median alpha 0.8
- outliers alpha 0.8

Strategy 3: Show data density
- median alpha 0.9
- outliers alpha 0.5 (can see through overlaps)
```

### Tip 4: Match Line Widths to Importance

```
Emphasize median:
- median width 4.0
- outliers width 1.0

Equal importance:
- median width 2.0
- outliers width 2.0

Subtle median:
- median width 2.0
- outliers width 1.5
```

## Common Workflows

### Workflow: Publication-Ready Plots

Creating polished visualizations for papers:

```
1. Generate data and visualize
   You: Generate 50 curves and plot functional boxplot

2. Set colormap for accessibility
   You: colormap viridis

3. Customize median for visibility
   You: median color black
   You: median width 3.0

4. Show outliers for completeness
   You: show outliers

5. Style outliers to be subtle
   You: outliers color gray
   You: outliers alpha 0.3

6. Adjust percentiles if needed
   You: percentile 10
   (or use full command for multiple percentiles)
```

### Workflow: Exploratory Analysis

Quick iteration to understand your data:

```
1. Quick generation
   You: Generate curves and plot

2. Toggle outliers to see extremes
   You: show outliers
   You: hide outliers

3. Try different colormaps for patterns
   You: colormap plasma
   You: colormap viridis
   You: colormap inferno

4. Adjust percentiles to focus on specific ranges
   You: percentile 95
   You: percentile 75
```

### Workflow: Comparing Multiple Configurations

Systematically testing different styles:

```
1. Create baseline
   You: Generate 40 curves and plot

2. Save mental snapshot, then try variant 1
   You: median color blue
   You: median width 2.0

3. Reset and try variant 2
   You: median color red
   You: median width 4.0
   You: show outliers

4. Choose best configuration for your needs
```

## Troubleshooting

### Issue: Styling commands not working

**Symptom**: Command seems ignored or error occurs

**Checklist**:
1. ✅ Verify you have a current visualization displayed
   - You must have created a plot first
2. ✅ Check spelling: `outliers color` not `outlier color`
   - "outliers" is plural
3. ✅ For colors, use valid matplotlib names
   - Valid: 'red', 'blue', 'black', 'gray', 'darkred'
   - Invalid: 'redd', 'light-blue' (use 'lightblue')
4. ✅ For numeric values, use decimals
   - Valid: 1.0, 2.5, 0.8
   - Avoid: 1 (but usually works), "2.5" (don't quote)

### Issue: Visualization not updating

**Symptom**: Command accepted but plot doesn't change

**Possible causes**:
1. **Matplotlib window closed**: Close and regenerate
2. **Wrong parameter for visualization type**: Some params only work with certain viz types
3. **Value out of range**: Check parameter constraints (e.g., alpha must be 0.0-1.0)

**Solution**:
```
# Regenerate if needed
You: plot functional boxplot

# Try command again
You: median color blue
```

### Issue: "No visualization to update"

**Symptom**: Error when trying to use hybrid commands

**Cause**: No visualization has been created yet in this session

**Solution**: Create a visualization first:
```
You: Generate 30 curves and plot functional boxplot
# Now you can use hybrid commands
You: median color blue
```

### Issue: Workers parameter not improving speed

**Symptom**: Changing workers count doesn't affect performance

**Possible causes**:
1. Dataset too small to benefit from parallelization
2. System has fewer cores than workers specified
3. Using functional_boxplot (doesn't support workers parameter)

**Solution**:
- Workers parameter only affects: `curve_boxplot`, `contour_boxplot`
- Does NOT affect: `functional_boxplot`, `probabilistic_marching_squares`, `uncertainty_lobes`
- Check your CPU core count: optimal workers ≈ number of cores

### Issue: Colors look different than expected

**Symptom**: Color names produce unexpected results

**Tip**: Use matplotlib's standard color names:
- **Basic**: 'red', 'blue', 'green', 'yellow', 'black', 'white', 'gray'
- **Extended**: 'darkred', 'darkblue', 'lightgray', 'darkgray'
- **Hex codes**: '#FF0000' (red), '#0000FF' (blue)

See [matplotlib colors documentation](https://matplotlib.org/stable/gallery/color/named_colors.html) for full list.

## Advanced Tips

### Combining Multiple Visualizations

Create and compare different views of the same data:

```
You: Generate 50 curves

You: Plot functional boxplot
[view first visualization]

You: Plot curve boxplot
[view second visualization - same data, different representation]
```

### Session Management

Control your working environment:

```
# View session statistics
You: /stats

# Clear temporary files
You: /clear

# Reset conversation but keep files
You: /reset

# Exit
You: /quit
```

### Context Awareness

The system remembers previous operations:

```
You: Generate 30 curves
You: Plot them         # "them" refers to the curves just generated
You: Make it blue      # "it" refers to the current plot
You: Show outliers     # implicitly updates current plot
```

---

Happy visualizing! 🎨📊

For more details:
- **API Reference**: See `API.md` for complete parameter documentation
- **Developer Guide**: See `CLAUDE.md` for implementation details
- **Testing**: See `TESTING.md` for testing strategies
