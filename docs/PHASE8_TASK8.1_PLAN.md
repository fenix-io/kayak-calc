# Phase 8: Task 8.1 - Unit Tests - Implementation Plan

## Overview
Phase 8: Task 8.1 focuses on creating comprehensive unit tests for core functionality including interpolation functions, volume calculations, and coordinate transformations. This task will validate individual components work correctly in isolation with known inputs/outputs.

## Current Status
Looking at the existing test suite, we already have substantial test coverage:
- `tests/test_interpolation.py` - Tests for interpolation functionality
- `tests/test_volume.py` - Tests for volume calculations
- `tests/test_transformations.py` - Tests for coordinate transformations
- `tests/test_cross_section.py` - Tests for cross-section calculations
- `tests/test_geometry.py` - Tests for Point3D and Profile classes
- `tests/test_hull.py` - Tests for KayakHull class

## Task Requirements

### 8.1.1 Test Interpolation Functions
**Goal:** Verify all interpolation functions work correctly with known input/output pairs and edge cases.

#### Tests to Verify/Add:
1. **Linear Interpolation**
   - Basic 1D interpolation with known values
   - 2D/3D point interpolation
   - Edge case: interpolation at endpoints (t=0, t=1)
   - Edge case: single point

2. **Profile Interpolation**
   - Transverse interpolation (across a single profile)
   - Longitudinal interpolation (between profiles)
   - Varying number of points in profiles
   - Edge cases: bow/stern profiles, single profile

3. **Point Distribution**
   - Uniform point distribution on profiles
   - Non-uniform point distributions
   - Handling of symmetry

### 8.1.2 Test Volume Calculations
**Goal:** Validate volume calculations against analytical solutions for simple geometric shapes.

#### Tests to Verify/Add:
1. **Simple Geometric Shapes**
   - **Rectangular Hull (Box):**
     - Known dimensions (e.g., 5m × 1m × 0.5m)
     - Expected volume: length × width × height
     - Compare numerical integration vs. analytical result
   
   - **Cylindrical Hull:**
     - Circular cross-sections
     - Expected volume: π × r² × length
     - Test both full and partially submerged
   
   - **Conical Hull (Tapered):**
     - Linear taper from one end to other
     - Expected volume: (1/3) × π × r² × length (or variations)
     - Test bow and stern tapers

2. **Submerged Volume**
   - Full submersion (waterline above hull)
   - Partial submersion at various waterline heights
   - Zero submersion (waterline below hull)

3. **Integration Methods**
   - Compare Simpson's rule vs. trapezoidal rule
   - Test with varying numbers of stations
   - Verify convergence with increasing resolution

### 8.1.3 Test Coordinate Transformations
**Goal:** Verify transformation operations preserve geometric properties and produce correct results.

#### Tests to Verify/Add:
1. **Rotation Matrices**
   - Heel (roll) transformations
   - 90° rotation should swap coordinates predictably
   - 360° rotation should return to original position
   - Verify rotation matrix properties (orthogonality)

2. **Waterline Intersections**
   - **Upright Condition:**
     - Horizontal waterline (z = constant)
     - Intersection with various profile shapes
     - Edge cases: waterline at keel, at deck
   
   - **Heeled Condition:**
     - Tilted waterline plane
     - Correct intersection calculation
     - Verify port/starboard asymmetry when heeled

3. **Transformation Consistency**
   - Forward and inverse transformations
   - Chaining transformations
   - Preservation of distances and volumes

## Implementation Strategy

### Step 1: Audit Existing Tests
- Review all existing test files
- Identify gaps in coverage
- Document what's already tested vs. what's missing

### Step 2: Create Validation Test Cases
For each geometric shape (box, cylinder, cone):
- Create helper functions to generate exact geometry
- Implement analytical solution calculators
- Create parametrized tests with various dimensions

### Step 3: Enhance Interpolation Tests
- Add edge case tests (endpoints, single points)
- Add tests for degenerate cases
- Verify interpolation accuracy with known intermediate values

### Step 4: Enhance Transformation Tests
- Add rotation property tests (orthogonality, determinant)
- Add inverse transformation tests
- Add waterline intersection edge cases

### Step 5: Documentation
- Add detailed docstrings to test functions
- Document expected vs. actual values
- Add references to analytical formulas used

## Expected Deliverables

1. **Enhanced Test Files:**
   - `tests/test_interpolation.py` - Comprehensive interpolation tests
   - `tests/test_volume.py` - Geometric shape validation tests
   - `tests/test_transformations.py` - Transformation property tests
   - `tests/test_cross_section.py` - Cross-section calculation tests

2. **Test Utilities:**
   - `tests/test_utils.py` or similar - Helper functions for:
     - Generating simple geometric shapes
     - Analytical solution calculators
     - Comparison functions with tolerance

3. **Documentation:**
   - This plan document
   - Summary document after completion
   - Inline test documentation

## Success Criteria

1. All existing tests continue to pass
2. New tests added for all items in sections 8.1.1, 8.1.2, 8.1.3
3. At least 95% code coverage for core modules:
   - `src/geometry/interpolation.py`
   - `src/hydrostatics/volume.py`
   - `src/geometry/transformations.py`
4. All tests pass with clear assertions
5. Test execution time remains reasonable (< 60 seconds for full suite)

## Test Organization

```
tests/
├── test_interpolation.py       # Interpolation function tests
├── test_volume.py               # Volume calculation tests
├── test_transformations.py      # Transformation tests
├── test_cross_section.py        # Cross-section tests
├── test_geometry.py             # Point3D, Profile tests
├── test_hull.py                 # KayakHull tests
├── test_validation.py           # NEW: Geometric validation tests
└── utils/                       # NEW: Test utilities
    ├── __init__.py
    ├── geometric_shapes.py      # Simple shape generators
    └── analytical_solutions.py  # Analytical calculators
```

## Technical Considerations

1. **Numerical Tolerance:**
   - Use appropriate tolerances for floating-point comparisons
   - Stricter tolerance for simple shapes (1e-6)
   - Relaxed tolerance for complex integration (1e-3)

2. **Test Independence:**
   - Each test should be independent
   - Use fixtures for common setup
   - Clean up any temporary data

3. **Parametrization:**
   - Use pytest parametrize for testing multiple scenarios
   - Test boundary conditions systematically

4. **Performance:**
   - Keep individual tests fast (< 1 second each)
   - Mark slow tests appropriately
   - Use fixtures to avoid repeated expensive operations

## Timeline Estimate

- Step 1 (Audit): 30 minutes
- Step 2 (Validation tests): 2-3 hours
- Step 3 (Interpolation tests): 1-2 hours
- Step 4 (Transformation tests): 1-2 hours
- Step 5 (Documentation): 30 minutes
- **Total: ~5-8 hours**

## Next Steps

1. Review and approve this plan
2. Begin implementation with Step 1 (audit)
3. Implement tests incrementally
4. Run tests continuously during development
5. Create summary document after completion
