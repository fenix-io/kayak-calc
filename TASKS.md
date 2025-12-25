# Development Tasks - Kayak Calculation Tool

## Phase 1: Project Setup and Foundation

### 1.1 Project Structure
- [x] Create basic project directory structure
  - `src/` - main package
  - `src/geometry/` - geometry and transformation modules
  - `src/hydrostatics/` - volume and buoyancy calculations
  - `src/stability/` - stability analysis
  - `src/visualization/` - plotting and visualization
  - `src/io/` - input/output handling
  - `tests/` - unit tests
  - `examples/` - example usage scripts
  - `data/` - sample data files

### 1.2 Dependencies and Configuration
- [x] Create `requirements.txt` with core dependencies:
  - numpy
  - scipy
  - matplotlib
  - Optional: pandas (for data handling)
- [x] Create `setup.py` or `pyproject.toml` for package installation
- [x] Set up `.gitignore` for Python projects
- [x] Initialize basic configuration structure

---

## Phase 2: Core Data Structures

### 2.1 Point and Profile Classes
- [x] Create `Point3D` class to represent 3D coordinates
  - Properties: x, y, z coordinates
  - Methods: distance, transformation operations
- [x] Create `Profile` class for transverse cross-sections
  - Store list of points defining the profile
  - Longitudinal station position
  - Methods: interpolate points, calculate area, find waterline intersection

### 2.2 Hull Definition
- [x] Create `KayakHull` class
  - Store collection of profiles (bow, stern, intermediate stations)
  - Store coordinate system reference (origin on centerline)
  - Methods:
    - `add_profile(station, points)` - add profile at longitudinal position
    - `get_profile(station)` - retrieve or interpolate profile at position
    - Validate symmetry and data consistency
- [x] Implement profile storage and retrieval system

---

## Phase 3: Geometry and Interpolation

### 3.1 Linear Interpolation Functions
- [x] Implement transverse interpolation
  - Interpolate between port and starboard points on a single profile
  - Generate intermediate points along profile curve
- [x] Implement longitudinal interpolation
  - Interpolate between adjacent profiles to create intermediate cross-sections
  - Handle varying number of points in different profiles
- [x] Implement bow/stern interpolation
  - Interpolate from end profiles to bow/stern apex points
  - Handle tapering geometry correctly

### 3.2 Coordinate Transformations
- [x] Create transformation functions for heel angles
  - Rotate coordinates about longitudinal axis (roll)
  - Transform from upright to heeled coordinate system
- [x] Implement waterline intersection calculation
  - Find intersection points of profile with water surface
  - Handle both upright and heeled conditions
  - Account for trim angle if needed
  - Handle both upright and heeled conditions
  - Account for trim angle if needed

---

## Phase 4: Hydrostatic Calculations

### 4.1 Cross-Section Properties
- [x] Calculate cross-sectional area below waterline
  - For upright condition
  - For heeled condition
- [x] Calculate centroid of cross-sectional area
  - First moments of area
  - Centroid coordinates

### 4.2 Volume Integration
- [x] Implement numerical integration along length
  - Simpson's rule for volume calculation
  - Trapezoidal rule as alternative
  - Handle irregular station spacing
- [x] Calculate total displacement volume
- [x] Calculate displaced mass (volume × water density)
- [x] Create comprehensive test suite (39 tests)
- [x] Create example scripts demonstrating usage
- [x] Documentation: `docs/PHASE4_TASK4.2_SUMMARY.md`

### 4.3 Center of Buoyancy
- [x] Calculate center of buoyancy (CB) in 3D
  - Longitudinal position (LCB)
  - Vertical position (VCB)
  - Transverse position (TCB) for heeled conditions
- [x] Implement for both upright and heeled conditions
- [x] Create comprehensive test suite (27 tests)
- [x] Create example scripts with visualizations
- [x] Documentation: `docs/PHASE4_TASK4.3_SUMMARY.md`

### 4.4 Center of Gravity
- [x] Create CG input/calculation system
  - [x] Allow manual CG specification
  - [x] Calculate from component masses and positions
  - [x] Validate CG properties
  - [x] Adjust CG for loading changes
  - [x] Mass distribution analysis
- [x] Store CG coordinates relative to reference origin
- [x] Create comprehensive test suite (44 tests)
- [x] Create example scripts with visualizations
- [x] Documentation: `docs/PHASE4_TASK4.4_SUMMARY.md`

---

## Phase 5: Stability Analysis

### 5.1 Righting Arm Calculation
- [x] Implement GZ calculation for given heel angle
  - GZ = horizontal distance between CG and CB when heeled
  - Account for coordinate transformations
- [x] Calculate range of positive stability
- [x] Identify maximum GZ and angle of maximum GZ
- [x] Create comprehensive test suite (31 tests passing)
- [x] Create example scripts with visualizations
- [x] Documentation: `docs/PHASE5_TASK5.1_SUMMARY.md`

### 5.2 Stability Curve Generation ✅
- [x] Create `StabilityAnalyzer` class
  - Initialize with hull geometry and CG position
  - Method to calculate GZ for single heel angle
  - Method to generate full stability curve (0° to 90° or more)
- [x] Calculate stability curve data
  - Array of heel angles
  - Corresponding GZ values
  - Identify key stability parameters
- **Status:** Complete - `src/stability/analyzer.py` with comprehensive OOP interface
- **Tests:** 28 tests passing in `tests/test_analyzer.py`
- **Examples:** 8 examples in `examples/stability_analyzer_examples.py`
- **Documentation:** Complete in `docs/PHASE5_TASK5.2_SUMMARY.md`

### 5.3 Stability Metrics ✅
- [x] Calculate metacentric height (GM) for small angles
- [x] Calculate angle of vanishing stability
- [x] Calculate area under GZ curve (dynamic stability)
- [x] Implement stability criteria checks (if applicable)
- **Status:** Complete - `src/stability/criteria.py` with comprehensive criteria assessment system
- **Tests:** 39 tests passing in `tests/test_criteria.py`
- **Examples:** 7 examples in `examples/stability_criteria_examples.py`
- **Documentation:** Complete in `docs/PHASE5_TASK5.3_SUMMARY.md`
- **Note:** GM, vanishing angle, and area calculations were already implemented in Tasks 5.1 & 5.2

---

## Phase 6: Visualization

### 6.1 Profile Plotting
- [ ] Plot individual transverse profiles
  - Show profile shape with waterline
  - Indicate submerged portion
- [ ] Plot hull in 3D view
  - Wireframe or surface plot of hull
  - Show waterline plane

### 6.2 Stability Curve Plotting
- [ ] Create GZ curve plot
  - Heel angle (x-axis) vs. GZ (y-axis)
  - Mark key points (max GZ, vanishing stability)
  - Add grid and labels
- [ ] Add annotations for stability metrics
- [ ] Export plots to various formats (PNG, PDF, SVG)

### 6.3 Interactive Visualization (Optional)
- [ ] Create interactive plots with matplotlib widgets
- [ ] Show hull at different heel angles
- [ ] Animate heel sequence

---

## Phase 7: Input/Output

### 7.1 Data Input
- [ ] Define standard input data format
  - JSON format for hull geometry
  - CSV format for profile points
  - Include metadata (units, coordinate system)
- [ ] Implement data loading functions
  - Parse JSON/CSV files
  - Validate input data
  - Handle errors gracefully

### 7.2 Data Output
- [ ] Export calculation results
  - Hydrostatic properties report
  - Stability curve data (CSV)
  - Summary statistics
- [ ] Generate calculation report
  - Text or markdown format
  - Include key parameters and plots

---

## Phase 8: Validation and Testing

### 8.1 Unit Tests
- [ ] Test interpolation functions
  - Known input/output pairs
  - Edge cases (end points, single profile)
- [ ] Test volume calculations
  - Simple geometric shapes (box, cylinder, cone)
  - Compare with analytical solutions
- [ ] Test coordinate transformations
  - Rotation matrices
  - Waterline intersections

### 8.2 Integration Tests
- [ ] Test complete calculation workflow
  - Load data → calculate → visualize
- [ ] Test with known kayak geometry
  - Compare with published data if available
  - Verify reasonable results

### 8.3 Validation Cases
- [ ] Create simple validation cases
  - Rectangular hull (analytical solution exists)
  - Symmetric hulls (check symmetry preservation)
- [ ] Test edge cases
  - Extreme heel angles
  - Very narrow or wide hulls
  - Unusual profile shapes

---

## Phase 9: Documentation and Examples

### 9.1 Code Documentation
- [ ] Add docstrings to all classes and functions
  - Parameters, return values, types
  - Example usage where helpful
  - Mathematical formulas and references
- [ ] Generate API documentation (Sphinx or similar)

### 9.2 User Guide
- [ ] Write user guide with examples
  - Basic usage tutorial
  - Input data format explanation
  - Interpretation of results
- [ ] Create example datasets
  - Simple hull geometries
  - Realistic kayak examples

### 9.3 Example Scripts
- [ ] Create example calculation scripts
  - Basic displacement calculation
  - Full stability analysis
  - Visualization examples
- [ ] Add comments and explanations

---

## Phase 10: Optimization and Enhancement

### 10.1 Performance Optimization
- [ ] Profile code for bottlenecks
- [ ] Optimize numerical integration routines
- [ ] Vectorize calculations where possible
- [ ] Cache intermediate results when appropriate

### 10.2 Additional Features (Future)
- [ ] Support for asymmetric hulls
- [ ] Trim angle calculations
- [ ] Wave resistance estimation
- [ ] Added mass calculations
- [ ] Export to CAD formats

---

## Dependencies Between Phases

- Phase 2 must complete before Phase 3 (need data structures for interpolation)
- Phase 3 must complete before Phase 4 (need geometry functions for calculations)
- Phase 4 must complete before Phase 5 (need hydrostatics for stability)
- Phase 5 should complete before Phase 6 (need results to visualize)
- Phase 7 can be developed in parallel with Phases 4-6
- Phase 8 should be ongoing throughout development
- Phase 9 can be done incrementally as features are completed

---

## Notes

- Start with simple cases and gradually add complexity
- Test each component thoroughly before moving to the next phase
- Keep the coordinate system and sign conventions consistent throughout
- Document assumptions and limitations clearly
- Consider numerical precision and stability in all calculations
