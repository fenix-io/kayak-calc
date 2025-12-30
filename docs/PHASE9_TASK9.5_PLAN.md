# Phase 9, Task 9.5: Hull CG Automation - Implementation Plan

## Task Overview
Automate hull center of gravity calculation by deriving it from hydrostatic geometry rather than requiring users to manually specify hull mass and CG position.

## Current Situation
Currently, users must manually specify the hull as a `MassComponent` with:
- Mass: Hull weight in kg (must be estimated or known)
- Position (x, y, z): Hull CG coordinates (must be guessed/estimated)

Example from code:
```python
components = [
    MassComponent("Hull", mass=28.0, x=2.3, y=0.0, z=-0.05),  # Manual!
    MassComponent("Paddler", mass=80.0, x=2.0, y=0.0, z=0.3),
    MassComponent("Gear", mass=15.0, x=1.5, y=0.0, z=0.1)
]
```

## Problems
1. **No guidance**: Users don't know what hull mass or CG to use
2. **Error-prone**: Manual estimation can be wildly inaccurate
3. **Inconsistent**: Hull geometry exists in the model but isn't used for CG
4. **Confusing**: New users struggle with this requirement

## Solution Design

### 1. New Function: `calculate_hull_cg_mass_component()`
Create a function that automatically calculates hull CG from hydrostatic geometry:

**Inputs:**
- `hull`: KayakHull object (the geometry)
- `hull_mass`: Total hull mass in kg (user provides or we estimate)
- `waterline_z`: Reference waterline (default 0.0)
- `method`: 'volume' (volumetric centroid) or 'surface' (surface area centroid)

**Algorithm for 'volume' method:**
1. Divide hull into longitudinal slices (stations)
2. For each slice:
   - Calculate volume element
   - Calculate centroid of volume element (x, y, z)
3. Compute weighted average of centroids weighted by volume
4. This gives the volumetric center (approximates CG for uniform density)

**Algorithm for 'surface' method:**
- Calculate centroid of hull surface area
- Assumes mass is concentrated in shell

**Default behavior:**
- Use 'volume' method as default
- Provides better approximation for solid materials
- For hollow shells, 'surface' method may be more accurate

**Output:**
- Returns `MassComponent` object representing the hull
- Can be directly combined with other components

### 2. Integration with `calculate_cg_from_components()`
No changes needed! The function already accepts a list of `MassComponent` objects.
The hull component from `calculate_hull_cg_mass_component()` can be included in that list.

**New workflow:**
```python
# Step 1: Calculate hull CG automatically
hull_component = calculate_hull_cg_mass_component(
    hull, 
    hull_mass=28.0,  # Only mass needed!
    method='volume'
)

# Step 2: Add other components as before
components = [
    hull_component,  # Automatic!
    MassComponent("Paddler", mass=80.0, x=2.0, y=0.0, z=0.3),
    MassComponent("Gear", mass=15.0, x=1.5, y=0.0, z=0.1)
]

# Step 3: Calculate total CG (unchanged)
cg = calculate_cg_from_components(components)
```

### 3. Implementation Details

#### Location
Add to: `src/hydrostatics/center_of_gravity.py`

#### Function Signature
```python
def calculate_hull_cg_mass_component(
    hull: KayakHull,
    hull_mass: float,
    waterline_z: float = 0.0,
    method: str = "volume",
    num_stations: Optional[int] = None,
    name: str = "Hull",
    description: str = "Hull structure (calculated CG)"
) -> MassComponent:
    """
    Calculate hull CG from hydrostatic geometry.
    
    Automatically derives the center of gravity of the hull structure
    from the hull geometry, eliminating the need for manual estimation.
    
    Args:
        hull: KayakHull object with defined geometry
        hull_mass: Total hull mass (kg) - must be known or measured
        waterline_z: Reference waterline position (m), default 0.0
        method: Calculation method ('volume' or 'surface'), default 'volume'
        num_stations: Number of stations for integration (None = use hull stations)
        name: Component name (default "Hull")
        description: Component description
        
    Returns:
        MassComponent representing the hull with calculated CG position
        
    Example:
        >>> hull = load_kayak_hull("kayak.json")
        >>> hull_component = calculate_hull_cg_mass_component(hull, hull_mass=28.0)
        >>> print(f"Hull CG: ({hull_component.x:.3f}, {hull_component.z:.3f})")
    """
```

#### Algorithm Details (Volume Method)
1. Get station positions along hull
2. For each station:
   - Get profile at that station
   - Calculate full hull cross-section properties (not just submerged)
   - Get area, centroid_y, centroid_z
3. Integrate to find volumetric centroid:
   - volume = ∫ A(x) dx
   - lcg = ∫ x·A(x) dx / volume
   - vcg = ∫ z_c(x)·A(x) dx / volume
   - tcg = ∫ y_c(x)·A(x) dx / volume (should be ~0 for symmetric hull)
4. Create and return MassComponent with hull_mass and calculated position

**Key consideration**: We need FULL hull cross-section, not just submerged portion.
- Existing `calculate_section_properties()` uses waterline to find submerged area
- Need a variant that calculates full hull cross-section area and centroid

#### Algorithm Details (Surface Method)
Similar but integrate over surface area rather than volume:
1. For each profile section (between stations i and i+1):
   - Calculate surface area of that section
   - Calculate centroid of that section
2. Weight centroids by surface area

### 4. Update Examples
Update these example files to use the new function:
- `examples/center_of_gravity_examples.py`
- `examples/complete_stability_analysis.py`
- `examples/basic_displacement_workflow.py`
- `examples/parametric_study_workflow.py`
- Any other examples that create hull MassComponents

**Pattern to follow:**
```python
# OLD (manual):
components = [
    MassComponent("Hull", mass=28.0, x=2.3, y=0.0, z=-0.05),
    ...
]

# NEW (automatic):
hull_component = calculate_hull_cg_mass_component(hull, hull_mass=28.0)
components = [
    hull_component,
    ...
]

# Optionally display calculated values
print(f"Calculated hull CG: ({hull_component.x:.4f}, "
      f"{hull_component.y:.4f}, {hull_component.z:.4f})")
```

### 5. Documentation Updates
Update the following documents:
- `USER_GUIDE.md`: Add section on automatic hull CG calculation
- `QUICKREF.md`: Update CG examples to show new method
- `docs/getting_started.rst`: Update tutorial
- `examples/README.md`: Document the new function

### 6. Testing Strategy

#### Unit Tests (in `tests/test_center_of_gravity.py`)
1. **Test basic calculation**
   - Simple rectangular hull → verify CG at geometric center
   - Symmetric hull → verify TCG ≈ 0
   
2. **Test with known shapes**
   - Box hull → LCG at length/2, VCG at height/2
   - Triangular profile → verify analytical centroid formulas
   
3. **Test both methods**
   - Volume method
   - Surface method
   - Compare results (should be similar for uniform shells)
   
4. **Test parameter validation**
   - Negative mass → raise ValueError
   - Empty hull → raise ValueError
   - Invalid method → raise ValueError
   
5. **Test integration with calculate_cg_from_components**
   - Calculate hull component
   - Add to other components
   - Verify total CG calculation

#### Integration Tests
1. **Complete workflow test**
   - Load hull from file
   - Calculate hull CG component
   - Add paddler and gear
   - Calculate total CG
   - Verify reasonable results
   
2. **Comparison test**
   - Calculate using automatic method
   - Calculate using manual specification (with same values)
   - Results should be identical

### 7. Additional Considerations

#### Hull Mass Estimation
While we automate CG calculation, we still need hull mass.
Consider adding a helper function for mass estimation:

```python
def estimate_hull_mass(
    hull: KayakHull,
    material: str = "fiberglass",
    shell_thickness: float = 0.004  # 4mm default
) -> float:
    """
    Estimate hull mass from geometry and material properties.
    
    Uses surface area and typical material density to estimate mass.
    This is approximate but useful for initial analysis.
    """
```

Materials database:
- Fiberglass: ~1.5-2.0 g/cm³, typical thickness 4-6mm
- Carbon fiber: ~1.4-1.6 g/cm³, typical thickness 3-5mm
- Polyethylene: ~0.94-0.96 g/cm³, typical thickness 5-8mm
- Wood: ~0.5-0.7 g/cm³ for typical marine plywood

**Decision**: Keep this as a separate optional feature. For Phase 9, Task 9.5, 
focus on CG calculation assuming mass is known.

#### Coordinate System
Ensure consistency with existing conventions:
- Origin at reference point (typically midship or bow)
- x: longitudinal (+ forward)
- y: transverse (+ starboard)
- z: vertical (+ up)

### 8. Implementation Steps

1. **Add helper function for full hull cross-section**
   - Create `calculate_full_section_properties()` in `cross_section.py`
   - Similar to existing function but calculates entire hull section
   - No waterline intersection needed

2. **Implement `calculate_hull_cg_mass_component()`**
   - Add to `center_of_gravity.py`
   - Volume method first (primary)
   - Surface method second (optional/future)
   - Full docstring with examples

3. **Write unit tests**
   - Add to `tests/test_center_of_gravity.py`
   - Test all scenarios listed above
   - Aim for >95% code coverage

4. **Update examples**
   - Modify 3-5 representative examples
   - Show calculated CG coordinates in output
   - Keep some examples with manual specification for comparison

5. **Update documentation**
   - Add section to USER_GUIDE.md
   - Update QUICKREF.md examples
   - Update API documentation

6. **Run quality checks**
   - `make format` - format code
   - `make lint` - check style
   - `make test` - run all tests
   - Verify all tests pass

## Success Criteria
- [ ] New function `calculate_hull_cg_mass_component()` implemented and working
- [ ] Full hull cross-section calculation helper added
- [ ] All unit tests pass (target: 10+ new tests)
- [ ] At least 3 examples updated to use new function
- [ ] Examples display calculated hull CG for verification
- [ ] Documentation updated (USER_GUIDE, QUICKREF, docstrings)
- [ ] Code formatted and linted (no errors)
- [ ] All existing tests still pass
- [ ] Manual verification: calculated CG matches expected values for known geometries

## Timeline Estimate
- Helper function (cross-section): 30 minutes
- Main function implementation: 1 hour
- Unit tests: 1 hour
- Update examples: 45 minutes
- Update documentation: 45 minutes
- Testing and refinement: 30 minutes
- **Total: ~4.5 hours**

## Notes
- This is a quality-of-life improvement for users
- Doesn't change fundamental calculations, just automates data preparation
- Maintains backward compatibility (old manual method still works)
- Provides verification capability (users can compare calculated vs. manual)
