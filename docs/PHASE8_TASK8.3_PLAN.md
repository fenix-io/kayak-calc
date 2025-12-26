# Phase 8, Task 8.3: Validation Cases - Implementation Plan

**Date:** December 26, 2024  
**Task:** Create validation test cases with analytical solutions and symmetry checks

## Objective

Create comprehensive validation test cases that verify the correctness of calculations using:
1. Simple geometries with known analytical solutions (rectangular hulls)
2. Symmetry preservation tests for symmetric hulls
3. Edge case validation for extreme configurations

## Requirements from TASKS.md

### 1. Simple Validation Cases
- **Rectangular hull:** Use analytical solutions for volume, CB, and stability
- **Symmetric hulls:** Verify symmetry is preserved in calculations

### 2. Edge Cases
- **Extreme heel angles:** Test at angles approaching 90°
- **Very narrow or wide hulls:** Test aspect ratio extremes
- **Unusual profile shapes:** Test with non-standard geometries

## Implementation Strategy

### Test File Organization
Create `tests/test_validation_cases.py` with the following test classes:

1. **TestRectangularHullValidation**
   - Analytical solutions for rectangular box hulls
   - Compare calculated vs. theoretical values for:
     - Volume
     - Center of buoyancy (CB)
     - Waterplane area
     - Metacentric height (GM) approximation
   - Test at multiple waterlines and heel angles

2. **TestSymmetryPreservation**
   - Create perfectly symmetric hulls
   - Verify symmetry properties:
     - TCG = 0 (transverse CG on centerline)
     - TCB = 0 at 0° heel (transverse CB on centerline)
     - GZ(φ) = -GZ(-φ) (GZ curve antisymmetric)
     - Volume same for port/starboard heel
   - Test with various symmetric geometries

3. **TestExtremeHeelAngles**
   - Test heel angles from 0° to 89°
   - Verify calculations remain stable
   - Check for numerical issues near 90°
   - Verify physical reasonableness

4. **TestExtremeAspectRatios**
   - Very narrow hulls (high length/beam ratio)
   - Very wide hulls (low length/beam ratio)
   - Verify calculations handle extremes
   - Check for numerical stability

5. **TestUnusualProfileShapes**
   - Triangular profiles
   - Multi-chine profiles
   - Asymmetric profiles
   - Profiles with discontinuities

## Analytical Solutions

### Rectangular Hull (Box)
For a rectangular box hull with:
- Length: L
- Beam: B
- Draft: T (submerged depth)
- Heel angle: φ

**Volume (upright):**
```
V = L × B × T
```

**Center of Buoyancy (upright):**
```
LCB = L/2 (at midship)
VCB = -T/2 (half draft below waterline)
TCB = 0 (on centerline)
```

**Waterplane Area (upright):**
```
Awp = L × B
```

**Metacentric Height (small angles):**
```
BM = I/V
where I = (L × B³)/12 (second moment of waterplane)
GM = KB + BM - KG
where KB = T/2 (center of buoyancy above keel)
```

**Volume (heeled):**
For small heel angles, volume remains constant.
For large angles, need to calculate submerged portion geometrically.

### Symmetry Properties

For a symmetric hull (symmetric about centerline):
1. **At zero heel:**
   - TCB = 0 (CB on centerline)
   - All transverse forces balanced

2. **GZ Curve Antisymmetry:**
   - GZ(φ) = -GZ(-φ)
   - Port heel should mirror starboard heel

3. **Volume Conservation:**
   - Volume at +φ heel = Volume at -φ heel

## Test Data

### Rectangular Hulls
Create test cases with:
- Small box: 2m × 0.5m × 0.3m draft
- Medium box: 5m × 1.0m × 0.5m draft
- Large box: 10m × 2.0m × 1.0m draft

### Symmetric Hulls
Use existing test utilities:
- Box profiles (already have analytical solutions)
- Wedge profiles
- Multi-chine symmetric profiles

### Edge Cases
- Narrow hull: Length/Beam = 20:1
- Wide hull: Length/Beam = 2:1
- Extreme heel: 85°, 88°, 89°
- Unusual shapes: Triangle, trapezoid, multi-chine

## Success Criteria

1. ✅ **Analytical Validation:** Calculated values match analytical solutions within tolerance
   - Volume: < 1% error
   - CB position: < 1% error
   - GM approximation: < 5% error (depends on assumptions)

2. ✅ **Symmetry Preservation:** Symmetric hulls maintain symmetry in calculations
   - TCB at 0° heel: < 0.001m from centerline
   - GZ antisymmetry: |GZ(φ) + GZ(-φ)| < 0.001m
   - Volume symmetry: < 0.1% difference

3. ✅ **Edge Case Stability:** Calculations remain stable at extremes
   - No NaN or Inf values
   - Physically reasonable results
   - Graceful handling of numerical issues

4. ✅ **Comprehensive Coverage:** Test various configurations
   - Multiple hull sizes
   - Multiple waterlines
   - Multiple heel angles
   - Multiple aspect ratios

## Implementation Steps

1. **Create test file structure** (test classes and fixtures)
2. **Implement rectangular hull analytical formulas** (utility functions)
3. **Create rectangular hull test cases** (volume, CB, GM)
4. **Implement symmetry tests** (TCB, GZ antisymmetry, volume)
5. **Create extreme heel angle tests** (up to 89°)
6. **Create extreme aspect ratio tests** (narrow/wide hulls)
7. **Create unusual profile tests** (various shapes)
8. **Run tests and fix issues**
9. **Document results**
10. **Update TASKS.md**

## Expected Outcomes

- **New test file:** `tests/test_validation_cases.py` (~500-700 lines)
- **Test count:** ~30-40 validation tests
- **Documentation:** Summary document with validation results
- **All tests passing:** 100% pass rate
- **Enhanced confidence:** Analytical validation proves correctness

## Notes

- Use existing `tests/utils/analytical_solutions.py` where applicable
- May need to add more analytical formulas for complex cases
- Focus on physically meaningful validation (not just code coverage)
- Document any limitations or assumptions in analytical solutions

---

**Ready for implementation upon approval.**
