# Phase 6, Task 6.1: Profile Plotting - Implementation Plan

## Overview
Implement visualization functions for plotting individual transverse profiles and 3D hull views. This task adds visual tools for understanding hull geometry, waterline interactions, and submerged portions.

## Objectives
1. Plot individual transverse profiles (cross-sections) in 2D
2. Show waterline and submerged portion visualization
3. Plot complete hull in 3D wireframe/surface view
4. Support both upright and heeled conditions
5. Provide flexible customization options

## Technical Specifications

### Module Structure
**File:** `src/visualization/plots.py`

### Core Functions

#### 1. `plot_profile()`
Plot a single transverse profile (cross-section).

**Signature:**
```python
def plot_profile(
    profile: Profile,
    waterline_z: float = 0.0,
    heel_angle: float = 0.0,
    show_submerged: bool = True,
    show_waterline: bool = True,
    ax: Optional[plt.Axes] = None,
    **kwargs
) -> plt.Axes:
```

**Parameters:**
- `profile`: Profile object to plot
- `waterline_z`: Z-coordinate of waterline
- `heel_angle`: Heel angle in degrees (0 = upright)
- `show_submerged`: Highlight submerged portion
- `show_waterline`: Draw waterline reference
- `ax`: Optional matplotlib axes (creates new if None)
- `**kwargs`: Additional plot customization options

**Features:**
- Plot profile points connected by lines
- Draw waterline as horizontal line at z = waterline_z
- Fill/shade submerged portion below waterline
- Handle heeled conditions (transform profile coordinates)
- Labels and grid
- Aspect ratio equal for accurate geometry

**Visualization:**
- Y-axis: Transverse position (port negative, starboard positive)
- Z-axis: Vertical position
- Profile shown as connected line
- Waterline as horizontal dashed line
- Submerged area filled with blue/translucent color

#### 2. `plot_multiple_profiles()`
Plot multiple profiles side-by-side for comparison.

**Signature:**
```python
def plot_multiple_profiles(
    profiles: List[Profile],
    stations: Optional[List[float]] = None,
    waterline_z: float = 0.0,
    heel_angle: float = 0.0,
    ncols: int = 3,
    figsize: Optional[Tuple[float, float]] = None,
    **kwargs
) -> Tuple[plt.Figure, List[plt.Axes]]:
```

**Parameters:**
- `profiles`: List of Profile objects
- `stations`: Optional station labels (uses profile.station if None)
- `waterline_z`: Waterline height
- `heel_angle`: Heel angle for all profiles
- `ncols`: Number of columns in subplot grid
- `figsize`: Figure size
- `**kwargs`: Passed to plot_profile()

**Features:**
- Creates subplot grid
- Each subplot shows one profile
- Consistent axes limits across subplots
- Station labels as subplot titles

#### 3. `plot_hull_3d()`
Plot hull in 3D wireframe or surface view.

**Signature:**
```python
def plot_hull_3d(
    hull: KayakHull,
    waterline_z: float = 0.0,
    heel_angle: float = 0.0,
    show_waterline_plane: bool = True,
    view_mode: str = 'wireframe',
    ax: Optional[Axes3D] = None,
    **kwargs
) -> Axes3D:
```

**Parameters:**
- `hull`: KayakHull object
- `waterline_z`: Z-coordinate of waterline
- `heel_angle`: Heel angle in degrees
- `show_waterline_plane`: Draw waterline plane
- `view_mode`: 'wireframe' or 'surface'
- `ax`: Optional 3D axes
- `**kwargs`: Plot customization

**Features:**
- Plot all profiles as lines along hull length
- Connect corresponding points between profiles (longitudinal lines)
- Show hull surface mesh
- Draw waterline plane (semi-transparent)
- Set proper 3D view angle
- Equal aspect ratio
- Labels for axes (x=length, y=beam, z=height)

**Wireframe mode:**
- Transverse lines (profiles)
- Longitudinal lines connecting profiles
- Simple line plots

**Surface mode:**
- Create mesh surface using plot_surface()
- Interpolate between profiles for smooth surface
- Color by height or other parameter

#### 4. `plot_profile_with_properties()`
Enhanced profile plot with geometric properties annotated.

**Signature:**
```python
def plot_profile_with_properties(
    profile: Profile,
    waterline_z: float = 0.0,
    show_centroid: bool = True,
    show_area: bool = True,
    show_waterline_intersection: bool = True,
    ax: Optional[plt.Axes] = None,
    **kwargs
) -> plt.Axes:
```

**Features:**
- Plot profile with submerged portion
- Mark centroid of submerged area with 'x'
- Annotate area value
- Mark waterline intersection points
- Show dimensions (beam, draft)

### Utility Functions

#### 5. `configure_plot_style()`
Set consistent plot styling for all visualizations.

```python
def configure_plot_style(
    grid: bool = True,
    style: str = 'seaborn-v0_8-darkgrid'
) -> None:
```

#### 6. `save_figure()`
Save figure to file with standard options.

```python
def save_figure(
    fig: plt.Figure,
    filepath: Path,
    dpi: int = 300,
    bbox_inches: str = 'tight',
    **kwargs
) -> None:
```

## Dependencies

### Required Imports
```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path

from src.geometry import Point3D, Profile, KayakHull
from src.geometry.transformations import rotate_point_about_x_axis
from src.hydrostatics.cross_section import calculate_cross_section_area, calculate_cross_section_centroid
```

### New Dependencies
None - all required libraries already in requirements.txt

## Implementation Strategy

### Step 1: Core 2D Profile Plotting
1. Implement `plot_profile()` for basic profile visualization
2. Extract profile points (y, z coordinates)
3. Plot connected line
4. Add waterline and submerged fill
5. Handle heeled conditions using transformations

### Step 2: Multiple Profiles
1. Implement `plot_multiple_profiles()`
2. Create subplot grid
3. Call plot_profile() for each
4. Ensure consistent axes limits

### Step 3: 3D Hull Visualization
1. Implement `plot_hull_3d()` wireframe mode
2. Plot each profile as 3D line
3. Connect corresponding points longitudinally
4. Add waterline plane
5. Set 3D view parameters

### Step 4: Enhanced Annotations
1. Implement `plot_profile_with_properties()`
2. Calculate geometric properties
3. Add centroid markers
4. Add dimension annotations
5. Format area/dimension text

### Step 5: Utility Functions
1. Implement `configure_plot_style()`
2. Implement `save_figure()`
3. Add helper functions as needed

## Testing Strategy

### Test File: `tests/test_plots.py`

#### Test Cases
1. **test_plot_profile_basic()** - Basic profile plotting
2. **test_plot_profile_with_waterline()** - Waterline display
3. **test_plot_profile_submerged()** - Submerged area highlighting
4. **test_plot_profile_heeled()** - Heeled profile visualization
5. **test_plot_multiple_profiles()** - Multi-profile subplot grid
6. **test_plot_hull_3d_wireframe()** - 3D wireframe view
7. **test_plot_hull_3d_surface()** - 3D surface view (if implemented)
8. **test_plot_profile_with_properties()** - Annotated profile plot
9. **test_custom_axes()** - Using existing axes objects
10. **test_save_figure()** - Figure saving functionality

#### Testing Approach
- Most tests will verify function execution without errors
- Check that axes objects are created/returned correctly
- Verify basic plot elements exist (lines, patches, etc.)
- Visual inspection through example scripts
- Save outputs to `examples/output/` for manual review

## Example Scripts

### File: `examples/profile_plotting_examples.py`

#### Examples to Include
1. **Example 1:** Plot single profile - upright condition
2. **Example 2:** Plot single profile - heeled condition
3. **Example 3:** Plot multiple profiles along hull
4. **Example 4:** Plot hull in 3D wireframe
5. **Example 5:** Plot profile with geometric properties
6. **Example 6:** Compare profiles at different heel angles
7. **Example 7:** Custom styling and colors
8. **Example 8:** Export plots to files

## Documentation

### Code Documentation
- Comprehensive docstrings for all functions
- Parameter descriptions with types
- Return value specifications
- Usage examples in docstrings
- Type hints throughout

### Summary Document
**File:** `docs/PHASE6_TASK6.1_SUMMARY.md`
- Overview of implementation
- Function descriptions
- Usage examples
- Test results
- Example outputs (images)
- Known limitations
- Future enhancements

## Design Considerations

### Coordinate System Consistency
- Maintain consistent axes labels and orientation
- Y-axis: transverse (port negative, starboard positive)
- Z-axis: vertical (down negative, up positive)
- X-axis: longitudinal

### Visual Clarity
- Use distinct colors for different elements
- Waterline: dashed line, gray or blue
- Submerged area: light blue fill with transparency
- Profile outline: solid dark line
- Grid for reference

### Performance
- Efficient for typical kayak hulls (5-20 profiles)
- Consider downsampling for very dense point data
- Lazy evaluation where appropriate

### Flexibility
- Support custom axes for integration with existing figures
- Pass-through kwargs for matplotlib customization
- Sensible defaults for all optional parameters

### Error Handling
- Validate input types
- Handle empty profiles gracefully
- Check for valid heel angles and waterline positions
- Informative error messages

## Deliverables

1. **src/visualization/plots.py** - Core implementation
2. **src/visualization/__init__.py** - Updated exports
3. **tests/test_plots.py** - Test suite
4. **examples/profile_plotting_examples.py** - Usage examples
5. **examples/output/** - Example output images
6. **docs/PHASE6_TASK6.1_SUMMARY.md** - Implementation summary
7. **TASKS.md** - Updated with completion status

## Success Criteria
- [ ] All plotting functions implemented and working
- [ ] Comprehensive test suite with >90% coverage
- [ ] At least 8 example scripts demonstrating usage
- [ ] Clear documentation with usage examples
- [ ] Visual outputs saved to examples/output/
- [ ] No breaking changes to existing code
- [ ] Code follows project style and conventions

## Timeline Estimate
- Implementation: 3-4 hours
- Testing: 1-2 hours
- Documentation & Examples: 1-2 hours
- **Total: 5-8 hours**

## Future Enhancements (Out of Scope)
- Interactive 3D rotation and zoom
- Animation of heel sequence
- Colormap by depth or pressure
- Integration with web-based plotting (plotly)
- Real-time updates with matplotlib widgets
