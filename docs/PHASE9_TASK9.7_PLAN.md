# Phase 9 - Task 9.7: Multi-Point Bow and Stern Definition

## Task Overview
Enhance the bow and stern definition from single apex points to arrays of points, providing better control over hull rocker and depth at different vertical positions (keel, chines, gunwale).

## Current Implementation
Currently, bow and stern are defined as single apex points:
```json
"bow": {"x": 0.0, "y": 0.0, "z": 0.45},
"stern": {"x": 5.2, "y": 0.0, "z": 0.45}
```

This creates a simple taper but lacks control over:
- Rocker curve (longitudinal curvature at different heights)
- Depth progression at bow/stern ends
- Independent control of keel, chine, and gunwale end points

## Proposed New Format
Bow and stern will be arrays of points, each matching a corresponding "level" from the station profiles.

### Two Matching Approaches:

**Approach 1: Explicit Level Names (Optional "level" attribute)**
```json
"bow": [
  {"x": 0.0, "y": 0.0, "z": 0.45, "level": "gunwale"},
  {"x": 0.15, "y": 0.0, "z": 0.0, "level": "chine2"},
  {"x": 0.25, "y": 0.0, "z": -0.10, "level": "chine1"},
  {"x": 0.40, "y": 0.0, "z": -0.15, "level": "keel"}
],
"stern": [
  {"x": 5.2, "y": 0.0, "z": 0.45, "level": "gunwale"},
  {"x": 5.05, "y": 0.0, "z": 0.0, "level": "chine2"},
  {"x": 4.95, "y": 0.0, "z": -0.10, "level": "chine1"},
  {"x": 4.80, "y": 0.0, "z": -0.15, "level": "keel"}
]
```
**Requires**: All profile points must also have "level" attribute for consistency.
**Pros**: Clear, self-documenting, order-independent
**Cons**: More verbose

**Approach 2: Implicit Array Position Matching (No "level" attribute)**
```json
"bow": [
  {"x": 0.0, "y": 0.0, "z": 0.45},
  {"x": 0.15, "y": 0.0, "z": 0.0},
  {"x": 0.25, "y": 0.0, "z": -0.10},
  {"x": 0.40, "y": 0.0, "z": -0.15}
],
"stern": [
  {"x": 5.2, "y": 0.0, "z": 0.45},
  {"x": 5.05, "y": 0.0, "z": 0.0},
  {"x": 4.95, "y": 0.0, "z": -0.10},
  {"x": 4.80, "y": 0.0, "z": -0.15}
]
```
**Requires**: Points in profiles grouped by level (centerline, then port/starboard pairs)
**Pros**: Compact, less verbose
**Cons**: Requires consistent ordering convention

## Design Rules

### 1. Point Count and Correspondence
- **Rule**: Number of bow/stern points must match the "levels" in station profiles
- **Example**: If stations have 7 points (keel + 2×chine1 + 2×chine2 + 2×gunwale), bow/stern should have 4 distinct levels (keel, chine1, chine2, gunwale)
- **Rationale**: Each level can have its own longitudinal position, creating complex rocker and shape

### 1a. Level Attribute Usage (Optional but Consistent)
- **Rule**: "level" attribute is **optional** - matching can be done by array position OR explicit level names
- **Consistency Rule**: If "level" is used in bow/stern points, it **must** be used in all profile points too
- **Detection**: System will auto-detect which approach is used by checking for "level" attribute presence
- **Rationale**: Ensures unambiguous matching; prevents mixed approaches that could cause confusion

### 2. Centerline Constraint
- **Rule**: All bow/stern points must have y = 0.0 (on centerline)
- **Example**: `{"x": 0.25, "y": 0.0, "z": -0.10}`
- **Rationale**: Maintains hull symmetry assumption

### 3. Longitudinal Position Variation
- **Rule**: Each level can have different x-coordinate values
- **Example**: Keel extends further forward/aft than gunwale
- **Rationale**: Creates realistic rocker curve and end shape

### 4. Coordinate System Handling
When `bow_origin` coordinate system is used:
- **Rule**: Reverse the order of bow/stern points
- **Rule**: Negate x-coordinates for bow points
- **Rule**: Convert stern x-coordinates to bow-origin reference
- **Implementation**: Ensure consistency when converting between coordinate systems

### 5. Interpolation Between Last Station and Bow/Stern Points
For each bow/stern level point:
- **Input**: 
  - Last station point at that level: e.g., `{0.65, 0.22, 0.20}` (gunwale, starboard)
  - Bow/stern point at that level: e.g., `{0.0, 0.0, 0.45}` (gunwale, centerline)
- **Output**: Intermediate profiles at interpolated stations between last station and bow point
- **Method**: Linear interpolation along the line connecting these two points
- **Example Calculation**:
  ```
  Last station gunwale (starboard): P1 = (0.65, 0.22, 0.20)
  Bow gunwale: P2 = (0.0, 0.0, 0.45)
  
  For intermediate station at x = 0.30:
  t = (0.30 - 0.0) / (0.65 - 0.0) = 0.46
  
  Interpolated point:
  x = 0.30
  y = 0.0 + 0.46 * (0.22 - 0.0) = 0.10
  z = 0.45 + 0.46 * (0.20 - 0.45) = 0.34
  ```

### 6. Final Volume (Pyramid/Cone)
- **Rule**: Between the closest interpolated station and the actual bow/stern point, create a closing volume
- **Approach**: Treat as a pyramid/cone with apex at the bow/stern point
- **Volume Calculation**: Use tetrahedral decomposition or equivalent
- **Rationale**: Ensures hull is properly closed at ends

## Implementation Plan

### Step 1: Remove Current Unrealistic Interpolation (src/io/loaders.py) ✅
- [x] **CRITICAL FIRST STEP**: Remove existing bow/stern interpolation code
- [x] Locate and remove the automatic profile generation logic:
  - Lines creating intermediate stations between last profile and bow/stern apex
  - Beam scaling logic (15% beam_scale)
  - Profile interpolation loops
- [x] Keep only the bow_apex/stern_apex data extraction
- [x] This removes the unrealistic interpolation that will be replaced with proper multi-point approach
- [x] Run tests to confirm system still loads hull data (just without interpolated profiles)
- **Completed**: ~170 lines removed, all 579 tests pass

### Step 2: Update Data Structures (src/geometry/hull.py) ✅
- [x] Understanding: Review current `bow_apex` and `stern_apex` implementation
- [x] Modify `KayakHull` class:
  - Change `bow_apex: Optional[Point3D]` to `bow_points: Optional[List[Point3D]]`
  - Change `stern_apex: Optional[Point3D]` to `stern_points: Optional[List[Point3D]]`
  - Add validation method to ensure all bow/stern points have y = 0.0
  - Add method to verify point count matches station structure
  - Keep backward compatibility: if single point format detected, store as single-element list
- [x] Added legacy properties for `bow_apex` and `stern_apex` (return first point)
- [x] Updated all transformation methods: rotate_about_x, translate, convert_coordinate_system
- **Completed**: Full backward compatibility maintained, all 579 tests pass

### Step 3: Update Input Format Schema (src/io/formats.py) ✅

**Status**: COMPLETED

- [x] Extend `KAYAK_JSON_SCHEMA` to support arrays for bow/stern
- [x] Maintain backward compatibility with single-point format (pyramid volume approach)
- [x] Add "level" as optional attribute for points (both bow/stern and profiles)
- [x] Add validation rules for:
  - y = 0.0 constraint
  - Point count correspondence
  - x-coordinate ordering (monotonic or unique)
  - Level consistency: if any bow/stern point has "level", all profile points must have it too

### Step 4: Update Loader Functions (src/io/loaders.py) ✅

**Status**: COMPLETED

- [x] Modify `load_kayak_from_json()`:
  - Detect if bow/stern are single points or arrays
  - Parse array format and create list of Point3D objects (with optional level attribute)
  - For backward compatibility with single apex point: **do NOT convert to array**
  - Single apex will be handled by pyramid volume calculation (Step 6)
  - Detect matching approach: check if "level" attribute exists in bow/stern points
  - Validate consistency: if levels used in bow/stern, verify all profile points have levels
- [x] Update `_create_profile_from_dict()` to parse optional "level" attribute
- [x] Add optional "level" parameter to Point3D class
- [x] Update Point3D transformation methods to preserve level attribute

### Step 5: Implement Multi-Point Interpolation Logic ✅

**Status**: COMPLETED

- [x] Create new function `interpolate_to_bow_stern_multipoint()` in `src/geometry/interpolation.py`:
  - Input: hull with bow_points/stern_points arrays, last station profile
  - Output: Modified hull with intermediate profiles added
  - Algorithm:
    1. **Detect matching approach**:
       - If "level" attributes present: Use level name matching
       - If no "level" attributes: Use array position matching
    2. **Group station profile points**:
       - With levels: Group by level name
       - Without levels: Group by position (assume ordered: centerline, port/starboard pairs)
    3. For each level/position in bow_points:
       a. Find corresponding points in last station (port, centerline, starboard)
       b. Create intermediate stations between last station and bow point
       c. For each intermediate station, interpolate all three points (port, center, starboard)
    4. Add interpolated profiles to hull
    5. Create final closing profile at bow point location
- [x] Implemented level-based matching via `_interpolate_multipoint_by_level()`
- [x] Implemented position-based matching via `_interpolate_multipoint_by_position()`
- [x] Handles tapering of port/starboard points toward centerline
- [x] Supports single-point mode (backward compatibility with apex approach)

### Step 6: Handle Pyramid/Cone Volume for End Closure ✅

**Status**: COMPLETED

- [x] Create function `calculate_end_pyramid_volume()` in `src/hydrostatics/volume.py`:
  - **For multi-point arrays**: Calculate volume between last interpolated profile and bow/stern points
  - **For single apex (backward compatibility)**: Calculate pyramid volume from last data station to apex
  - Use tetrahedral decomposition: divide cross-section into triangles, create tetrahedra to apex
  - Alternative: Use cone approximation for circular-like cross-sections
  - Integrate into overall displacement calculation
- [x] Update `calculate_displacement()` to add pyramid volumes at both ends
- [x] Implemented `_calculate_pyramid_to_single_apex()` for single apex case
- [x] Implemented `_calculate_pyramid_multipoint()` for multi-point arrays
- [x] Added `include_end_volumes` parameter to `calculate_displacement()`
- [x] Handles waterline intersection and heel angle correctly

### Step 7: Update Coordinate System Conversion (src/geometry/hull.py)
- [ ] Modify `convert_coordinate_system()` method:
  - Handle bow_points and stern_points arrays
  - Properly reverse order and negate x-coordinates when converting between bow_origin and stern_origin
  - Ensure consistency for all points in arrays
  - Handle single apex points for backward compatibility

### Step 8: Update Visualization (src/visualization/)
- [ ] Modify plotting functions to show multi-point bow/stern:
  - `plot_profile_view()`: Show multiple bow/stern end points
  - `plot_plan_view()`: Display rocker lines for each level
  - `plot_3d_hull()`: Render improved end geometry
  - Show pyramid closure volumes in visualizations

### Step 9: Update Documentation
- [ ] Update INPUT_DATA_FORMATS.md:
  - Document new array format for bow/stern
  - Provide examples with different point counts
  - Explain level correspondence rules
- [ ] Update GLOSSARY.md if new terms are introduced
- [ ] Update examples in `data/` folder with multi-point bow/stern

### Step 10: Create Migration Examples
- [ ] Create example script `create_multipoint_bow_stern_example.py`:
  - Show how to design hulls with multi-point bow/stern
  - Generate example JSON files with realistic multi-point arrays
  - Demonstrate different rocker configurations
- [ ] **Note**: Old single-point files continue to work via pyramid volume calculation (no migration needed)
- [ ] Provide design guide in documentation for creating multi-point definitions

### Step 11: Comprehensive Testing
- [ ] Unit tests for new data structures
- [ ] Unit tests for multi-point interpolation
- [ ] Integration tests with sample hulls
- [ ] Validation tests for constraint enforcement (y = 0.0, point count, etc.)
- [ ] Backward compatibility tests (single-point format still works)
- [ ] Visual inspection tests (generate plots of new hull shapes)

### Step 12: Performance Considerations
- [ ] Profile interpolation performance with more intermediate stations
- [ ] Optimize level matching algorithm
- [ ] Cache interpolated profiles if needed

## Technical Challenges

### Challenge 1: Level Identification
**Problem**: How to automatically match bow/stern points to station profile levels?

**Solutions** (User chooses one approach per hull definition):
1. **Explicit level attribute** (Optional, adds clarity, more verbose)
   ```json
   {"x": 0.0, "y": 0.0, "z": 0.45, "level": "gunwale"}
   ```
   - Pro: Clear, self-documenting, order-independent
   - Con: More verbose, must add to ALL points (bow/stern AND profiles)
   - Consistency: If any bow/stern point has "level", ALL profile points must have it

2. **Array position matching** (No level attribute, more compact)
   - Pro: Compact, less verbose
   - Con: Requires strict ordering convention
   - Convention: Points grouped by level, ordered consistently (e.g., centerline first, then port/starboard pairs)
   - Example order: [centerline_gunwale, port_gunwale, stbd_gunwale, port_chine2, stbd_chine2, ...]

**Recommendation**: Support both approaches; detect based on "level" attribute presence; enforce consistency

### Challenge 2: Asymmetric Point Counts
**Problem**: What if different stations have different numbers of chines?

**Solutions**:
1. **Require consistency**: Enforce all stations have same structure
2. **Flexible matching**: Use z-coordinate proximity for matching
3. **Level naming**: Use standardized level names (keel, chine_lower, chine_upper, gunwale)

**Recommendation**: Start with consistency requirement, add flexibility later

### Challenge 3: Backward Compatibility
**Problem**: Existing JSON files use single bow/stern points

**Solutions**:
1. **Auto-detect format**: Check if bow/stern are objects or arrays
2. **Pyramid volume approach**: For single apex, calculate pyramid volume from last data station to apex
3. **No interpolation**: Don't create intermediate profiles for single apex
4. **No conversion**: Keep single apex as-is, handle via pyramid volume calculation

**Recommendation**: Implement pyramid volume calculation for single apex - simpler and more accurate than interpolation

### Challenge 4: Interpolation Complexity
**Problem**: More points mean more intermediate profiles and computation

**Solutions**:
1. **Adaptive station spacing**: Use smaller spacing near rapid geometry changes
2. **Parallel processing**: Vectorize interpolation operations
3. **Caching**: Store interpolated profiles for reuse

**Recommendation**: Start simple, optimize if performance issues arise

## Success Criteria
- [ ] Hull can be loaded with multi-point bow/stern definition
- [ ] Interpolation creates smooth transitions from stations to bow/stern
- [ ] All constraint rules are validated and enforced
- [ ] Backward compatibility maintained with single-point format
- [ ] Visualization shows improved end geometry
- [ ] Displacement and buoyancy calculations remain accurate
- [ ] All existing tests pass
- [ ] New tests cover multi-point functionality
- [ ] Documentation is complete and clear

## Example Use Case

### Realistic Sea Kayak with Pronounced Rocker

**Example 1: Using Explicit Level Names (Verbose but Clear)**
```json
{
  "metadata": {
    "coordinate_system": "bow_origin",
    "length": 5.2,
    "beam": 0.55
  },
  "bow": [
    {"x": 0.0, "y": 0.0, "z": 0.50, "level": "gunwale"},
    {"x": 0.15, "y": 0.0, "z": 0.10, "level": "chine_upper"},
    {"x": 0.25, "y": 0.0, "z": -0.05, "level": "chine_lower"},
    {"x": 0.45, "y": 0.0, "z": -0.18, "level": "keel"}
  ],
  "stern": [
    {"x": 5.2, "y": 0.0, "z": 0.48, "level": "gunwale"},
    {"x": 5.05, "y": 0.0, "z": 0.08, "level": "chine_upper"},
    {"x": 4.90, "y": 0.0, "z": -0.08, "level": "chine_lower"},
    {"x": 4.70, "y": 0.0, "z": -0.20, "level": "keel"}
  ],
  "profiles": [
    {
      "station": 0.65,
      "points": [
        {"x": 0.65, "y": 0.0, "z": 0.40, "level": "gunwale"},
        {"x": 0.65, "y": -0.22, "z": 0.20, "level": "chine_upper"},
        {"x": 0.65, "y": 0.22, "z": 0.20, "level": "chine_upper"},
        {"x": 0.65, "y": -0.24, "z": 0.0, "level": "chine_lower"},
        {"x": 0.65, "y": 0.24, "z": 0.0, "level": "chine_lower"},
        {"x": 0.65, "y": -0.20, "z": -0.18, "level": "keel"},
        {"x": 0.65, "y": 0.20, "z": -0.18, "level": "keel"}
      ]
    }
  ]
}
```

**Example 2: Using Array Position Matching (Compact)**
```json
{
  "metadata": {
    "coordinate_system": "bow_origin",
    "length": 5.2,
    "beam": 0.55
  },
  "bow": [
    {"x": 0.0, "y": 0.0, "z": 0.50},
    {"x": 0.15, "y": 0.0, "z": 0.10},
    {"x": 0.25, "y": 0.0, "z": -0.05},
    {"x": 0.45, "y": 0.0, "z": -0.18}
  ],
  "stern": [
    {"x": 5.2, "y": 0.0, "z": 0.48},
    {"x": 5.05, "y": 0.0, "z": 0.08},
    {"x": 4.90, "y": 0.0, "z": -0.08},
    {"x": 4.70, "y": 0.0, "z": -0.20}
  ],
  "profiles": [
    {
      "station": 0.65,
      "points": [
        {"x": 0.65, "y": 0.0, "z": 0.40},
        {"x": 0.65, "y": -0.22, "z": 0.20},
        {"x": 0.65, "y": 0.22, "z": 0.20},
        {"x": 0.65, "y": -0.24, "z": 0.0},
        {"x": 0.65, "y": 0.24, "z": 0.0},
        {"x": 0.65, "y": -0.20, "z": -0.18},
        {"x": 0.65, "y": 0.20, "z": -0.18}
      ]
    }
  ]
}
```
Note: Array position approach requires consistent point ordering across all profiles.

**Both examples create**:
- Gunwale rocker: Rises from 0.40m at station 0.65 to 0.50m at bow
- Keel rocker: Extends further forward (0.45m) than gunwale (0.0m)
- Smooth transitions with multiple intermediate profiles
- Better control over bow shape and volume distribution

## Dependencies
- Depends on: Current geometry, interpolation, and I/O modules
- Blocks: Task 9.8 (testing and docs review)
- Related to: Profile interpolation (Phase 3), visualization (Phase 6)

## Estimated Effort
- Data structure updates: 4 hours
- Interpolation logic: 8 hours
- Coordinate system handling: 3 hours
- Visualization updates: 4 hours
- Testing: 6 hours
- Documentation: 3 hours
- **Total: ~28 hours** (approximately 4 working days)

## Risk Assessment
- **Low Risk**: Data structure changes (well-defined)
- **Medium Risk**: Interpolation complexity (manageable with proper algorithm)
- **Low Risk**: Backward compatibility (auto-detection handles this)
- **Medium Risk**: Testing coverage (need comprehensive test cases)

## Notes
- Consider adding visual validation tools during development
- Test with multiple realistic hull shapes
- May want to add UI/CLI tool for converting old format to new format
- Consider adding validation warnings if rocker curves seem unrealistic (e.g., keel point is aft of gunwale point at bow)
