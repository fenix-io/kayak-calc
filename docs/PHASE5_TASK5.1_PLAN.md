# Phase 5, Task 5.1: Righting Arm Calculation - Implementation Plan

## Date: December 25, 2025

## Objective
Implement GZ (righting arm) calculation functionality for stability analysis.

## Background

### What is GZ (Righting Arm)?
The righting arm (GZ) is the horizontal distance between the center of gravity (CG) and the center of buoyancy (CB) when the vessel is heeled. It represents the moment arm through which the buoyant force acts to restore the vessel to upright position.

### Mathematical Definition
When a vessel is heeled by angle φ:
- GZ = horizontal distance from CG to vertical line through CB
- GZ = (TCB - TCG) × cos(φ) + (VCB - VCG) × sin(φ)

Or more commonly in naval architecture:
- GZ = d × sin(φ) where d is the distance between CG and CB along the normal to the keel

### Physical Interpretation
- **Positive GZ**: Righting moment exists (stable)
- **Zero GZ**: No righting moment (equilibrium or limit)
- **Negative GZ**: Capsizing moment (unstable)

The GZ curve (GZ vs heel angle) is fundamental to stability analysis.

## Key Parameters to Calculate

### 1. GZ at Single Heel Angle
Given:
- Hull geometry
- Waterline position
- CG position (lcg, vcg, tcg)
- Heel angle φ

Calculate:
- CB at heeled condition (lcb, vcb, tcb)
- GZ value

### 2. Range of Positive Stability
- Minimum heel angle where GZ > 0
- Maximum heel angle where GZ > 0 (angle of vanishing stability)

### 3. Maximum GZ
- Maximum value of GZ
- Angle at which maximum GZ occurs

## Implementation Strategy

### Module Structure
Create `src/stability/righting_arm.py` with:

1. **GZ Calculation Function**
   - `calculate_gz(hull, cg, waterline_z, heel_angle)` → GZ value
   - Use existing `calculate_center_of_buoyancy()` function
   - Calculate horizontal distance between CG and CB

2. **GZ Curve Function**
   - `calculate_gz_curve(hull, cg, waterline_z, heel_angles)` → list of GZ values
   - Call `calculate_gz()` for each heel angle
   - Return structured result with angles and GZ values

3. **Stability Metrics Function**
   - `analyze_stability(gz_curve)` → metrics dictionary
   - Find range of positive stability
   - Find maximum GZ and its angle
   - Calculate other derived parameters

4. **Data Classes**
   - `RightingArm`: Single GZ calculation result
   - `StabilityCurve`: Complete GZ curve with all data points
   - `StabilityMetrics`: Derived stability parameters

### Coordinate System Considerations

The challenge is that when the hull is heeled:
1. CB is calculated in the **heeled coordinate system** (by `calculate_center_of_buoyancy` with `heel_angle` parameter)
2. CG remains fixed in the **upright coordinate system**

**Important**: Need to carefully handle coordinate transformations:
- Option A: Transform CG to heeled coordinates, then calculate horizontal distance
- Option B: Transform CB back to upright coordinates, then calculate
- Option C: Use proper transformation formulas accounting for both systems

### Recommended Approach (Option C)
For heel angle φ:

1. Calculate CB in heeled condition: `CB_heeled = calculate_center_of_buoyancy(hull, waterline_z, φ)`
2. The heeled CB gives us (tcb, vcb, lcb) in the heeled coordinate system
3. Transform back to upright system or use direct formula:
   - GZ = TCB_heeled (transverse distance already gives horizontal arm)
   - Since CG doesn't move and CB_heeled.tcb is already the transverse distance in heeled frame

**Actually, simpler approach:**
When heeled by φ degrees:
- The vertical through CB (buoyant force) and vertical through CG (weight) are both vertical in global frame
- The horizontal distance between these two vertical lines is the righting arm
- This is essentially: GZ = (CB_y - CG_y)_in_heeled_frame

Since `calculate_center_of_buoyancy` with `heel_angle=φ` returns CB in heeled coordinates:
- CB.tcb is the transverse position in heeled frame
- CG needs to be transformed to heeled frame
- GZ = CB.tcb - CG_transverse_in_heeled_frame

### GZ Calculation Formula

For a kayak heeled by angle φ:

```
# CG is fixed in upright frame: (lcg, tcg, vcg) = (x_g, y_g, z_g)
# When heeled, CG position in heeled frame:
y_g_heeled = y_g * cos(φ) + z_g * sin(φ)
z_g_heeled = -y_g * sin(φ) + z_g * cos(φ)

# CB in heeled frame (from calculate_center_of_buoyancy with heel_angle=φ):
(lcb, tcb, vcb) = CB position in heeled frame

# Righting arm:
GZ = tcb - y_g_heeled
   = tcb - (tcg * cos(φ) + vcg * sin(φ))
```

This accounts for the fact that as the vessel heels, the CG moves transversely in the heeled coordinate system even though it's fixed in space.

## Implementation Steps

### Step 1: Create righting_arm.py with data classes
```python
@dataclass
class RightingArm:
    gz: float  # Righting arm (m)
    heel_angle: float  # Heel angle (degrees)
    cb: CenterOfBuoyancy  # CB at this heel angle
    cg: CenterOfGravity  # CG position
    waterline_z: float  # Waterline position
```

### Step 2: Implement calculate_gz()
Core calculation function for single heel angle

### Step 3: Implement calculate_gz_curve()
Calculate GZ for range of heel angles

### Step 4: Implement analyze_stability()
Extract key stability metrics from GZ curve

### Step 5: Create comprehensive tests
Test with known cases and validate against theory

### Step 6: Create example scripts
Demonstrate usage with realistic kayak data

## Test Cases

### Test 1: Symmetric Hull Upright
- Hull symmetric about centerline
- CG on centerline (tcg=0)
- Heel angle = 0°
- Expected: GZ = 0 (equilibrium)

### Test 2: Small Heel Angle
- Use metacentric height formula for validation
- GZ ≈ GM × sin(φ) for small φ
- Verify against theoretical value

### Test 3: Large Heel Angle
- Calculate at 45°, 60°, 90°
- Verify CB moves correctly
- Verify GZ values are physically reasonable

### Test 4: GZ Curve
- Generate curve from 0° to 90°
- Verify shape: starts at 0, increases, peaks, decreases
- Find maximum GZ and angle

### Test 5: Vanishing Stability
- High CG case (less stable)
- Find angle where GZ returns to zero

## Dependencies

### Existing Modules Required
- `src/geometry/hull.py`: KayakHull class
- `src/geometry/transformations.py`: Coordinate transformations
- `src/hydrostatics/volume.py`: calculate_center_of_buoyancy()
- `src/hydrostatics/center_of_gravity.py`: CenterOfGravity class

### New Dependencies
- None (use existing NumPy, SciPy)

## Success Criteria

1. ✓ `calculate_gz()` returns correct GZ value for given conditions
2. ✓ `calculate_gz_curve()` generates complete stability curve
3. ✓ `analyze_stability()` extracts correct metrics
4. ✓ All tests pass with reasonable tolerances
5. ✓ Example scripts demonstrate practical usage
6. ✓ Documentation is complete and clear

## Future Enhancements (Not in this task)

- Dynamic stability (area under GZ curve)
- Stability criteria checks (IMO/regulatory standards)
- Trim angle effects on stability
- Added mass effects in dynamic motion

## Notes

- Keep coordinate system consistent with existing code
- Use type hints throughout
- Include comprehensive docstrings with formulas
- Add validation for input parameters
- Handle edge cases (zero volume, extreme heel angles)
