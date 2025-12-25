# Phase 4, Task 4.1: Cross-Section Properties - Implementation Plan

## Current Status
The Profile class in `src/geometry/profile.py` already implements the core functionality for Task 4.1:
- ✅ `calculate_area_below_waterline()` - calculates cross-sectional area below waterline
- ✅ `calculate_centroid_below_waterline()` - calculates centroid of submerged area
- ✅ Tests exist in `tests/test_geometry.py` for both methods
- ✅ Both upright and heeled conditions supported via `rotate_about_x()` method

## Task 4.1 Requirements (from TASKS.md)
- [ ] Calculate cross-sectional area below waterline
  - For upright condition
  - For heeled condition
- [ ] Calculate centroid of cross-sectional area
  - First moments of area
  - Centroid coordinates

## What Needs to be Done

### 1. Create Hydrostatics Module Structure
Create a dedicated module for cross-section calculations in `src/hydrostatics/cross_section.py`:
- `CrossSectionProperties` class to encapsulate area and centroid data
- High-level functions that wrap Profile methods with clear hydrostatics context
- Support for batch calculations on multiple profiles

### 2. Add Enhanced Documentation
- Add comprehensive docstrings explaining the hydrostatics context
- Document the mathematical formulas used (Shoelace formula, polygon centroid)
- Add references to marine hydrostatics theory
- Document assumptions and limitations

### 3. Create Example Usage Script
Create `examples/cross_section_examples.py` demonstrating:
- Calculating area and centroid for a single profile (upright)
- Calculating area and centroid for heeled profiles
- Comparing results across different heel angles
- Visualizing cross-section with waterline and centroid marked

### 4. Enhanced Testing
Add tests in `tests/test_cross_section.py`:
- Test with analytical cases (rectangle, triangle)
- Test heel angle effects on area and centroid
- Test edge cases (profile entirely above/below waterline)
- Test with realistic kayak profiles

### 5. Update Documentation
- Update TASKS.md to mark Task 4.1 as complete
- Add cross-section calculations to README.md
- Create technical documentation explaining the calculations

## Implementation Details

### CrossSectionProperties Class
```python
class CrossSectionProperties:
    """
    Represents hydrostatic properties of a cross-section.
    
    Attributes:
        area: Submerged cross-sectional area
        centroid_y: Transverse position of centroid
        centroid_z: Vertical position of centroid
        station: Longitudinal position of cross-section
        waterline_z: Z-coordinate of waterline
        heel_angle: Heel angle in degrees (0 = upright)
    """
```

### Key Functions
1. `calculate_section_properties(profile, waterline_z, heel_angle)` - Calculate all properties
2. `calculate_properties_at_heel_angles(profile, waterline_z, heel_angles)` - Batch calculation
3. Helper functions for validation and error checking

### Example Usage
```python
from src.hydrostatics import CrossSectionProperties, calculate_section_properties

# Calculate for upright condition
props = calculate_section_properties(profile, waterline_z=0.0, heel_angle=0.0)
print(f"Area: {props.area:.3f} m²")
print(f"Centroid: ({props.centroid_y:.3f}, {props.centroid_z:.3f})")

# Calculate for heeled condition
props_heeled = calculate_section_properties(profile, waterline_z=0.0, heel_angle=15.0)
```

## Files to Create/Modify

### New Files
1. `/src/hydrostatics/cross_section.py` - Main implementation
2. `/examples/cross_section_examples.py` - Usage examples
3. `/tests/test_cross_section.py` - Additional tests
4. `/docs/PHASE4_TASK4.1_SUMMARY.md` - Technical documentation

### Modified Files
1. `/src/hydrostatics/__init__.py` - Add exports
2. `/TASKS.md` - Mark Task 4.1 as complete
3. `/README.md` - Add documentation for cross-section calculations

## Testing Strategy

### Unit Tests
- Test `CrossSectionProperties` class initialization and properties
- Test `calculate_section_properties()` with known geometries
- Test heel angle effects
- Test edge cases

### Validation Tests
Compare results with analytical solutions:
- **Rectangle**: Area = width × depth, Centroid at geometric center
- **Triangle**: Area = 0.5 × base × height, Centroid at 1/3 height
- **Trapezoid**: Known formulas for area and centroid

### Integration Tests
- Test with realistic kayak profiles from examples
- Verify consistency between upright and heeled calculations
- Test with multiple profiles along hull

## Success Criteria
- [x] Core calculation methods work (already implemented)
- [ ] CrossSectionProperties class created with proper documentation
- [ ] High-level API functions created for ease of use
- [ ] Comprehensive examples demonstrating usage
- [ ] All tests pass with >95% coverage
- [ ] Documentation complete and clear
- [ ] TASKS.md updated to mark Task 4.1 complete

## Timeline Estimate
- Module structure and CrossSectionProperties class: 30 minutes
- Example scripts: 20 minutes
- Additional tests: 30 minutes
- Documentation: 20 minutes
- **Total: ~2 hours**

## Dependencies
- Phase 3 (✅ Complete) - Coordinate transformations and interpolation
- Profile class (✅ Complete) - Area and centroid calculations

## Next Steps After Completion
Task 4.1 completion enables:
- **Task 4.2**: Volume Integration (uses cross-sectional areas)
- **Task 4.3**: Center of Buoyancy (uses cross-sectional centroids)
- **Task 4.4**: Center of Gravity input system
