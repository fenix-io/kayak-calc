# Phase 6, Task 6.3 - Interactive Visualization Implementation Plan

## Overview
Implement interactive visualization features using matplotlib widgets to allow users to dynamically explore hull geometry and stability characteristics at different heel angles.

## Objectives
1. Create interactive plots with matplotlib widgets for parameter control
2. Implement real-time visualization of hull at different heel angles
3. Create animation capabilities for heel sequence visualization
4. Provide intuitive user controls for exploring stability characteristics

## Detailed Tasks

### Task 6.3.1: Interactive Heel Angle Explorer
**Purpose:** Allow users to interactively adjust heel angle and see real-time updates

**Implementation:**
- Create `interactive_heel_explorer()` function
- Use matplotlib `Slider` widget for heel angle control
- Display:
  - 3D hull view at current heel angle
  - Current profile view (cross-section)
  - Real-time GZ value and stability metrics
  - Center of buoyancy and center of gravity positions
- Update all views dynamically as slider moves

**Components:**
- Slider for heel angle (0° to 90°)
- Multiple synchronized subplots
- Real-time calculation and display of stability parameters

### Task 6.3.2: Interactive Stability Curve Explorer
**Purpose:** Allow users to explore stability curve with interactive selection

**Implementation:**
- Create `interactive_stability_curve()` function
- Display GZ curve with clickable points
- Use matplotlib event handling for point selection
- Show detailed information for selected heel angle:
  - Hull visualization at that angle
  - Cross-section view
  - Numerical stability values
  - CB and CG positions

**Components:**
- Main stability curve plot
- Click event handler
- Dynamic detail panels
- Hover tooltips for curve points

### Task 6.3.3: Animated Heel Sequence
**Purpose:** Create smooth animation showing hull behavior through heel range

**Implementation:**
- Create `animate_heel_sequence()` function
- Use matplotlib `FuncAnimation` for smooth transitions
- Display:
  - 3D hull view rotating through heel angles
  - Synchronized GZ curve with moving indicator
  - Profile view animation
  - Stability metrics updating in real-time
- Playback controls:
  - Play/Pause button
  - Speed control slider
  - Frame step forward/backward buttons

**Components:**
- Animation controller with `FuncAnimation`
- Play/pause button widget
- Speed slider widget
- Frame navigation buttons

### Task 6.3.4: Interactive Parameter Adjustment
**Purpose:** Allow users to adjust CG position and see impact on stability

**Implementation:**
- Create `interactive_cg_adjustment()` function
- Multiple sliders for CG adjustment:
  - Vertical CG position (VCG)
  - Longitudinal CG position (LCG)
  - Mass/displacement
- Real-time updates to:
  - Stability curve
  - GM value
  - Maximum GZ
  - Range of stability
- Side-by-side comparison of original vs. adjusted

**Components:**
- Multiple parameter sliders
- Dual plot display (before/after)
- Live metric calculations
- Reset button

### Task 6.3.5: Interactive Waterline Explorer
**Purpose:** Visualize hull at different waterline levels (draft variations)

**Implementation:**
- Create `interactive_waterline_explorer()` function
- Slider for waterline Z-coordinate
- Display:
  - 3D hull with variable waterline
  - Displacement volume calculation
  - Submerged profile views
  - CB position updates
- Show how displacement changes with draft

**Components:**
- Waterline slider
- Multiple view synchronization
- Volume/displacement readout
- CB position indicator

## Technical Implementation Details

### Module Structure
All functions will be added to `src/visualization/plots.py`

### Dependencies
- `matplotlib.widgets` - For interactive controls (Slider, Button, RadioButtons)
- `matplotlib.animation` - For animated sequences
- `matplotlib.backend_bases` - For event handling

### Function Signatures
```python
def interactive_heel_explorer(
    hull: KayakHull,
    cg: Point3D,
    waterline_z: float = 0.0,
    heel_range: Tuple[float, float] = (0.0, 90.0),
    initial_heel: float = 0.0,
    figsize: Tuple[float, float] = (16, 10)
) -> plt.Figure:
    """Interactive heel angle explorer with slider control."""
    pass

def interactive_stability_curve(
    hull: KayakHull,
    cg: Point3D,
    waterline_z: float = 0.0,
    heel_angles: Optional[np.ndarray] = None,
    figsize: Tuple[float, float] = (16, 10)
) -> plt.Figure:
    """Interactive stability curve with clickable point selection."""
    pass

def animate_heel_sequence(
    hull: KayakHull,
    cg: Point3D,
    waterline_z: float = 0.0,
    heel_range: Tuple[float, float] = (0.0, 90.0),
    n_frames: int = 90,
    interval: int = 100,
    figsize: Tuple[float, float] = (16, 10),
    save_path: Optional[Path] = None
) -> Tuple[plt.Figure, Any]:
    """Animate heel sequence with playback controls."""
    pass

def interactive_cg_adjustment(
    hull: KayakHull,
    initial_cg: Point3D,
    waterline_z: float = 0.0,
    vcg_range: Optional[Tuple[float, float]] = None,
    lcg_range: Optional[Tuple[float, float]] = None,
    figsize: Tuple[float, float] = (16, 10)
) -> plt.Figure:
    """Interactive CG position adjustment with stability comparison."""
    pass

def interactive_waterline_explorer(
    hull: KayakHull,
    cg: Point3D,
    waterline_range: Tuple[float, float] = (-0.5, 0.2),
    initial_waterline: float = 0.0,
    heel_angle: float = 0.0,
    figsize: Tuple[float, float] = (16, 10)
) -> plt.Figure:
    """Interactive waterline level explorer."""
    pass
```

## Testing Strategy

### Unit Tests (`tests/test_plots.py`)
1. Test interactive function creation (verify figures are created)
2. Test widget initialization (sliders, buttons)
3. Test callback functions independently
4. Test data update mechanisms
5. Test animation frame generation
6. Mock user interactions for automated testing

### Integration Tests
1. Test interaction between multiple widgets
2. Test synchronization of multiple views
3. Test animation playback functionality
4. Test event handling and callbacks

### Visual/Manual Tests
1. Manual verification of smooth interactions
2. Performance testing with complex hull geometries
3. Widget responsiveness testing
4. Animation smoothness verification

## Example Scripts

Create `examples/interactive_visualization_examples.py` with:
1. Basic heel angle explorer demo
2. Stability curve explorer demo
3. Animated heel sequence demo
4. CG adjustment demo
5. Waterline explorer demo
6. Combined interactive dashboard demo

## Documentation

### Code Documentation
- Comprehensive docstrings for all functions
- Parameter descriptions
- Usage examples
- Return value specifications

### User Documentation
- Create `docs/PHASE6_TASK6.3_SUMMARY.md` with:
  - Overview of interactive features
  - Usage instructions for each interactive tool
  - Screenshots/GIFs of interactions (if possible)
  - Tips for effective use
  - Limitations and known issues

## Success Criteria
- [ ] All 5 interactive visualization functions implemented
- [ ] Smooth, responsive interactions with no lag
- [ ] All widgets functional and intuitive
- [ ] Comprehensive test coverage (aim for 25+ tests)
- [ ] 6+ working examples demonstrating all features
- [ ] Complete documentation with usage guidelines
- [ ] Animations can be saved to file formats (MP4, GIF)

## Timeline Estimate
- Task 6.3.1: 2-3 hours
- Task 6.3.2: 2-3 hours
- Task 6.3.3: 3-4 hours
- Task 6.3.4: 2-3 hours
- Task 6.3.5: 2-3 hours
- Testing: 2-3 hours
- Examples: 1-2 hours
- Documentation: 1 hour
**Total: ~15-22 hours**

## Notes
- Interactive visualization requires matplotlib to be run in interactive mode
- Some features may not work in non-GUI backends (e.g., Agg backend)
- Performance may vary with hull complexity
- Animation export requires `ffmpeg` or `pillow` for video/GIF formats
- Consider adding performance optimization for complex hulls (caching, LOD)
