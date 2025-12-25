# Phase 6, Task 6.2: Stability Curve Plotting - Implementation Plan

## Overview
Implement visualization functions for plotting stability curves (GZ vs heel angle) with annotations for key stability metrics. This task builds on the existing stability analysis functionality to provide clear, informative plots for understanding kayak stability characteristics.

## Objectives
1. Create GZ curve plots (heel angle on x-axis, GZ on y-axis)
2. Mark and annotate key points (max GZ, vanishing stability, etc.)
3. Add clear grid, labels, and legends
4. Annotate stability metrics (GM, range of stability, areas)
5. Support multiple curve comparison
6. Export plots to various formats (PNG, PDF, SVG)

## Technical Specifications

### Module Extension
**File:** `src/visualization/plots.py` (extend existing module)

### Core Functions

#### 1. `plot_stability_curve()`
Plot a single GZ curve with key points marked.

**Signature:**
```python
def plot_stability_curve(
    curve: StabilityCurve,
    metrics: Optional[StabilityMetrics] = None,
    mark_key_points: bool = True,
    show_metrics: bool = True,
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
```

**Parameters:**
- `curve`: StabilityCurve object from stability analysis
- `metrics`: Optional StabilityMetrics object (calculated if None)
- `mark_key_points`: Mark max GZ, vanishing stability, etc.
- `show_metrics`: Show text box with stability metrics
- `ax`: Optional matplotlib axes
- `**kwargs`: Customization options (colors, line styles, etc.)

**Features:**
- Plot heel angles vs GZ values as line plot
- Mark maximum GZ point with marker and annotation
- Mark vanishing stability angle (where GZ crosses zero)
- Mark angle of deck immersion (if available)
- Show range of positive stability with shaded region
- Display stability metrics in text box
- Zero line reference (y=0)
- Grid for readability

**Key Points to Mark:**
1. **Maximum GZ**: Point with largest righting arm
2. **Vanishing Stability**: Angle where GZ becomes zero (negative)
3. **Initial GM**: Slope at origin (if metrics provided)
4. **Specific angles**: User-defined angles of interest

**Metrics to Display:**
- Maximum GZ value and angle
- Range of positive stability
- GM (metacentric height estimate)
- Area under curve (dynamic stability)
- Angle of vanishing stability

#### 2. `plot_multiple_stability_curves()`
Compare multiple stability curves on same axes.

**Signature:**
```python
def plot_multiple_stability_curves(
    curves: List[StabilityCurve],
    labels: Optional[List[str]] = None,
    mark_key_points: bool = True,
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
```

**Parameters:**
- `curves`: List of StabilityCurve objects to compare
- `labels`: Labels for each curve (auto-generated if None)
- `mark_key_points`: Mark key points for each curve
- `ax`: Optional matplotlib axes
- `**kwargs`: Customization options

**Features:**
- Plot multiple curves with different colors/styles
- Legend identifying each curve
- Optionally mark key points for each
- Common axes and grid
- Support for up to ~5 curves for clarity

**Use Cases:**
- Compare different loading conditions
- Compare different CG positions
- Compare different waterlines
- Show effect of parameter variations

#### 3. `plot_stability_curve_with_metrics()`
Enhanced plot with detailed metrics annotations.

**Signature:**
```python
def plot_stability_curve_with_metrics(
    curve: StabilityCurve,
    metrics: StabilityMetrics,
    show_areas: bool = True,
    show_slopes: bool = True,
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
```

**Parameters:**
- `curve`: StabilityCurve object
- `metrics`: StabilityMetrics object with calculated values
- `show_areas`: Shade areas under curve (dynamic stability)
- `show_slopes`: Show initial and final slopes
- `ax`: Optional matplotlib axes
- `**kwargs`: Customization options

**Features:**
- All features from `plot_stability_curve()`
- Shade area under curve (represents dynamic stability)
- Show tangent line at origin (represents GM)
- Mark additional critical angles
- More detailed metrics box
- Optional secondary y-axis for moment

#### 4. `plot_gz_at_angles()`
Plot GZ values at specific heel angles as bar chart.

**Signature:**
```python
def plot_gz_at_angles(
    curve: StabilityCurve,
    angles: List[float],
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
```

**Parameters:**
- `curve`: StabilityCurve object
- `angles`: List of heel angles to display
- `ax`: Optional matplotlib axes
- `**kwargs`: Customization options

**Features:**
- Bar chart showing GZ at specified angles
- Color bars by stability (green=positive, red=negative)
- Value labels on bars
- Comparison of discrete angles

#### 5. `plot_righting_moment_curve()`
Plot righting moment (GZ × displacement × g) vs heel angle.

**Signature:**
```python
def plot_righting_moment_curve(
    curve: StabilityCurve,
    displacement_mass: float,
    g: float = 9.81,
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
```

**Parameters:**
- `curve`: StabilityCurve object
- `displacement_mass`: Displacement in kg
- `g`: Gravitational acceleration (default: 9.81 m/s²)
- `ax`: Optional matplotlib axes
- `**kwargs`: Customization options

**Features:**
- Plot righting moment in N⋅m
- Similar annotations as GZ curve
- Useful for direct moment comparison

#### 6. `create_stability_report_plot()`
Create comprehensive multi-panel stability report.

**Signature:**
```python
def create_stability_report_plot(
    curve: StabilityCurve,
    metrics: StabilityMetrics,
    hull: Optional[KayakHull] = None,
    figsize: Tuple[float, float] = (14, 10),
    **kwargs
) -> Tuple[plt.Figure, Dict[str, Axes]]:
```

**Parameters:**
- `curve`: StabilityCurve object
- `metrics`: StabilityMetrics object
- `hull`: Optional hull for profile plot
- `figsize`: Figure size
- `**kwargs`: Customization options

**Features:**
- Multi-panel layout with:
  1. GZ curve with annotations
  2. Profile at key heel angles
  3. Metrics summary table
  4. CB trajectory plot (optional)
- Comprehensive stability summary
- Publication-ready format

## Implementation Details

### Visualization Style

**Color Scheme:**
- GZ curve: Navy blue (default)
- Positive stability region: Light green fill
- Negative stability region: Light red fill
- Maximum GZ marker: Red star
- Vanishing stability: Orange triangle
- Zero line: Black dashed

**Annotations:**
- Maximum GZ: "Max GZ = X.XXX m at YY.Y°"
- Vanishing stability: "Vanishing at ZZ.Z°"
- GM estimate: "GM ≈ X.XXX m"
- Range: "Stable: 0° to ZZ.Z°"

**Metrics Box:**
```
Stability Metrics:
━━━━━━━━━━━━━━━━
Max GZ:    0.234 m @ 35.0°
GM:        0.145 m
Vanishing: 75.5°
Range:     0° - 75.5°
Area:      0.156 m⋅rad
```

### Key Point Detection

**Maximum GZ:**
```python
max_idx = np.argmax(curve.gz_values)
max_gz = curve.gz_values[max_idx]
max_angle = curve.heel_angles[max_idx]
```

**Vanishing Stability:**
```python
# Find where GZ crosses zero (from positive to negative)
positive_mask = curve.gz_values > 0
if np.any(positive_mask):
    last_positive_idx = np.where(positive_mask)[0][-1]
    # Interpolate zero crossing
```

**Range of Stability:**
```python
# Continuous range where GZ > threshold (e.g., 0.0)
positive_range = curve.heel_angles[curve.gz_values > 0]
range_start = positive_range[0]
range_end = positive_range[-1]
```

### Area Under Curve (Dynamic Stability)

```python
from scipy import integrate

# Area from 0° to vanishing angle
area = integrate.trapz(
    curve.gz_values[mask],
    np.radians(curve.heel_angles[mask])
)
```

## Testing Strategy

### Test File: `tests/test_plots.py` (extend existing file)

#### New Test Cases
1. **test_plot_stability_curve_basic()** - Basic GZ curve plot
2. **test_plot_stability_curve_with_markers()** - Key points marked
3. **test_plot_stability_curve_with_metrics()** - Metrics display
4. **test_plot_multiple_stability_curves()** - Multiple curve comparison
5. **test_plot_stability_curve_custom_axes()** - Using existing axes
6. **test_plot_stability_curve_no_metrics()** - Without metrics object
7. **test_plot_gz_at_angles()** - Bar chart at specific angles
8. **test_plot_righting_moment_curve()** - Moment curve plot
9. **test_create_stability_report_plot()** - Comprehensive report
10. **test_stability_plot_customization()** - Custom colors/styles
11. **test_stability_plot_edge_cases()** - Edge case handling

#### Testing Approach
- Use StabilityAnalyzer to generate test curves
- Verify plot elements exist (lines, markers, annotations)
- Check that key points are correctly identified
- Test with various curve shapes
- Save outputs for visual inspection

## Example Scripts

### File: `examples/stability_curve_plotting_examples.py`

#### Examples to Include
1. **Example 1:** Basic stability curve plot
2. **Example 2:** Stability curve with detailed metrics
3. **Example 3:** Compare multiple loading conditions
4. **Example 4:** Compare different CG heights
5. **Example 5:** GZ values at specific angles (bar chart)
6. **Example 6:** Righting moment curve
7. **Example 7:** Comprehensive stability report
8. **Example 8:** Custom styling and colors
9. **Example 9:** Sensitivity analysis (vary parameter)
10. **Example 10:** Export to multiple formats (PNG, PDF, SVG)

## Dependencies

### Required Imports
```python
# Extend existing imports in plots.py
from ..stability import StabilityCurve, StabilityMetrics, RightingArm
from scipy import integrate  # For area calculations
```

### No New Dependencies
All required libraries already in requirements.txt

## Integration with Existing Code

### Seamless Integration
- Extends existing `plots.py` module
- Uses existing StabilityCurve and StabilityMetrics classes
- Compatible with StabilityAnalyzer workflow
- Consistent styling with profile plots

### Typical Workflow
```python
from src.stability import StabilityAnalyzer
from src.visualization import plot_stability_curve

# Create analyzer
analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.2)

# Generate curve
curve = analyzer.generate_stability_curve()
metrics = analyzer.analyze_stability(curve)

# Plot
ax = plot_stability_curve(curve, metrics)
plt.show()
```

## Deliverables

1. **Extended `src/visualization/plots.py`** - New stability plotting functions
2. **Updated `src/visualization/__init__.py`** - Export new functions
3. **Extended `tests/test_plots.py`** - Additional tests (aim for 10+ new tests)
4. **`examples/stability_curve_plotting_examples.py`** - Usage examples
5. **`examples/output/`** - Example output images
6. **`docs/PHASE6_TASK6.2_PLAN.md`** - This plan document
7. **`docs/PHASE6_TASK6.2_SUMMARY.md`** - Implementation summary
8. **Updated `TASKS.md`** - Mark task complete

## Success Criteria
- [ ] All stability plotting functions implemented
- [ ] Curves plotted accurately with correct annotations
- [ ] Key points (max GZ, vanishing angle) correctly identified and marked
- [ ] Metrics displayed clearly and accurately
- [ ] At least 10 new tests, all passing
- [ ] At least 10 example scripts with visual outputs
- [ ] Documentation complete and thorough
- [ ] Integration with existing stability analysis seamless
- [ ] Publication-quality plot outputs

## Visual Design Guidelines

### Layout
- Standard figure size: 10×6 inches for single curve
- Larger for multi-panel reports: 14×10 inches
- Sufficient margins for annotations
- Clear, readable fonts (10-12pt)

### Axes
- X-axis: "Heel Angle (degrees)" or "Heel Angle (°)"
- Y-axis: "Righting Arm GZ (m)" or "GZ (m)"
- Grid: Major grid visible, minor grid optional
- Aspect ratio: Auto (not equal)

### Lines and Markers
- Curve line width: 2-3pt
- Marker size: 8-12pt for key points
- Annotation arrows: Clear, not cluttering
- Text size: 9-10pt for annotations

### Professional Appearance
- Clean, uncluttered layout
- Consistent color scheme
- Publication-ready quality
- Suitable for reports and presentations

## Timeline Estimate
- Planning: Complete (this document)
- Implementation: 2-3 hours
- Testing: 1 hour
- Examples & Documentation: 1-2 hours
- **Total: 4-6 hours**

## Notes

### Mathematical Background
- GZ curve is fundamental to stability analysis
- Area under GZ curve represents dynamic stability
- Slope at origin relates to metacentric height (GM)
- Vanishing stability angle indicates capsize risk

### Physical Interpretation
- Positive GZ: Boat will right itself
- Maximum GZ: Greatest restoring capability
- Vanishing angle: Beyond this, boat will capsize
- Area under curve: Energy available to resist capsizing

### Best Practices
- Always show zero line for reference
- Mark key points clearly
- Include metrics for quantitative assessment
- Use consistent units (degrees, meters)
- Provide context with annotations
