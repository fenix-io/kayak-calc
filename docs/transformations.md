# Coordinate Transformations Documentation

## Overview

The `transformations.py` module provides comprehensive coordinate transformation functions for analyzing kayak hull geometry in different orientations. These transformations are essential for:
- **Stability analysis** - Calculating righting moments at various heel angles
- **Displacement calculations** - Finding volume at different attitudes
- **Hydrostatic properties** - Computing waterplane area and centers
- **Motion simulation** - Modeling kayak behavior in waves

## Table of Contents

1. [Heel Transformations](#heel-transformations)
2. [Trim Transformations](#trim-transformations)
3. [Combined Transformations](#combined-transformations)
4. [Waterline Class](#waterline-class)
5. [Waterline Intersections](#waterline-intersections)
6. [Submerged Calculations](#submerged-calculations)
7. [Coordinate System Conversions](#coordinate-system-conversions)
8. [Usage Examples](#usage-examples)

---

## Heel Transformations

Heel angle represents rotation about the X-axis (longitudinal axis). Positive heel means **starboard side down** (roll to starboard).

### Functions

#### `apply_heel(point, heel_angle, reference_point=None)`

Apply heel angle to a single point.

**Parameters:**
- `point` (Point3D): Point to transform
- `heel_angle` (float): Heel angle in degrees (+ = starboard down)
- `reference_point` (Point3D, optional): Center of rotation (default: origin)

**Returns:**
- Point3D: Transformed point

**Example:**
```python
from src.geometry import Point3D, apply_heel

point = Point3D(2.0, 0.5, 0.1)
heeled = apply_heel(point, 15.0)  # 15° to starboard
```

#### `apply_heel_to_profile(profile, heel_angle, reference_point=None)`

Apply heel to an entire profile.

**Example:**
```python
from src.geometry import Profile, apply_heel_to_profile

profile = Profile(2.0, points)
heeled_profile = apply_heel_to_profile(profile, 20.0)
```

#### `apply_heel_to_hull(hull, heel_angle, reference_point=None)`

Apply heel to entire hull.

**Example:**
```python
from src.geometry import KayakHull, apply_heel_to_hull

hull = KayakHull()
# ... add profiles ...
heeled_hull = apply_heel_to_hull(hull, 30.0)
```

### Sign Convention

- **Positive** heel angle: Starboard side down (right side when looking forward)
- **Negative** heel angle: Port side down (left side when looking forward)
- **0°**: Upright (level)

### Rotation Matrix

Heel rotation about X-axis:
```
[1    0       0   ]
[0  cos(θ) -sin(θ)]
[0  sin(θ)  cos(θ)]
```

---

## Trim Transformations

Trim angle represents rotation about the Y-axis (transverse axis). Positive trim means **bow up** (pitch bow up/stern down).

### Functions

#### `apply_trim(point, trim_angle, reference_point=None)`

Apply trim angle to a single point.

**Parameters:**
- `point` (Point3D): Point to transform
- `trim_angle` (float): Trim angle in degrees (+ = bow up)
- `reference_point` (Point3D, optional): Center of rotation (default: origin)

**Example:**
```python
from src.geometry import Point3D, apply_trim

point = Point3D(3.0, 0.0, 0.1)
trimmed = apply_trim(point, 5.0)  # 5° bow up
```

#### `apply_trim_to_profile(profile, trim_angle, reference_point=None)`

Apply trim to a profile.

**Note:** When trimmed, profile points' x-coordinates change. The function automatically adjusts them to maintain profile integrity.

#### `apply_trim_to_hull(hull, trim_angle, reference_point=None)`

Apply trim to entire hull.

### Sign Convention

- **Positive** trim: Bow up, stern down
- **Negative** trim: Bow down, stern up
- **0°**: Level trim

### Rotation Matrix

Trim rotation about Y-axis:
```
[ cos(θ)  0  sin(θ)]
[   0     1    0   ]
[-sin(θ)  0  cos(θ)]
```

---

## Combined Transformations

### `apply_heel_and_trim(point, heel_angle, trim_angle, reference_point=None, order='heel_first')`

Apply both heel and trim to a point.

**Parameters:**
- `point` (Point3D): Point to transform
- `heel_angle` (float): Heel angle in degrees
- `trim_angle` (float): Trim angle in degrees
- `reference_point` (Point3D, optional): Center of rotation
- `order` (str): Rotation order ('heel_first' or 'trim_first')

**Important:** Order matters! Rotations are non-commutative.

**Example:**
```python
from src.geometry import apply_heel_and_trim

point = Point3D(2.0, 0.5, 0.1)
transformed = apply_heel_and_trim(point, 20.0, 5.0, order='heel_first')
```

### Rotation Order

**'heel_first'** (typical for ships):
1. Apply heel (roll)
2. Apply trim (pitch)

**'trim_first'**:
1. Apply trim (pitch)
2. Apply heel (roll)

---

## Waterline Class

The `Waterline` class represents a water plane that can be horizontal or inclined due to heel/trim.

### Constructor

```python
Waterline(z_reference=0.0, heel_angle=0.0, trim_angle=0.0)
```

**Parameters:**
- `z_reference` (float): Reference z-coordinate for level waterline
- `heel_angle` (float): Heel angle in degrees (inclines waterline)
- `trim_angle` (float): Trim angle in degrees (inclines waterline)

**Example:**
```python
from src.geometry import Waterline

# Horizontal waterline at z=0.1m
wl_level = Waterline(z_reference=0.1)

# Inclined waterline (15° heel)
wl_heeled = Waterline(z_reference=0.1, heel_angle=15.0)

# Waterline with both heel and trim
wl_combined = Waterline(z_reference=0.1, heel_angle=20.0, trim_angle=5.0)
```

### Methods

#### `z_at_point(x, y)`

Calculate z-coordinate of waterline at given (x, y) position.

```python
z = waterline.z_at_point(2.0, 0.5)
```

#### `is_below_waterline(point)`

Check if a point is submerged.

```python
submerged = waterline.is_below_waterline(Point3D(1.0, 0.0, -0.2))
```

#### `signed_distance(point)`

Calculate signed distance from point to waterline (negative = below).

```python
dist = waterline.signed_distance(point)
```

### Plane Equation

The waterline is represented as a 3D plane:
```
ax + by + cz + d = 0
```

Where (a, b, c) is the normalized normal vector, determined by heel and trim angles.

---

## Waterline Intersections

### `find_waterline_intersection_segment(p1, p2, waterline)`

Find intersection of a line segment with waterline plane.

**Parameters:**
- `p1` (Point3D): First endpoint
- `p2` (Point3D): Second endpoint
- `waterline` (Waterline): Waterline plane

**Returns:**
- Point3D or None: Intersection point if exists

**Example:**
```python
from src.geometry import find_waterline_intersection_segment, Waterline

p1 = Point3D(1.0, 0.0, -0.1)  # Below waterline
p2 = Point3D(1.0, 0.0, 0.2)   # Above waterline
wl = Waterline(z_reference=0.0)

intersection = find_waterline_intersection_segment(p1, p2, wl)
```

### `find_profile_waterline_intersection(profile, waterline)`

Find all intersection points of a profile with waterline.

**Returns:**
- List[Point3D]: Intersection points (typically 0 or 2 for closed profiles)

**Example:**
```python
from src.geometry import find_profile_waterline_intersection

intersections = find_profile_waterline_intersection(profile, waterline)
print(f"Found {len(intersections)} waterline intersections")
```

---

## Submerged Calculations

### `get_submerged_points(profile, waterline, include_intersections=True)`

Get points of profile that are submerged.

**Returns:**
- List[Point3D]: Ordered list of points forming submerged portion

### `calculate_submerged_area(profile, waterline)`

Calculate submerged cross-sectional area using Shoelace formula.

**Example:**
```python
from src.geometry import calculate_submerged_area, Waterline

wl = Waterline(z_reference=0.1)
area = calculate_submerged_area(profile, wl)
print(f"Submerged area: {area:.4f} m²")
```

### `calculate_waterplane_area(hull, waterline, num_stations=50)`

Calculate waterplane area (area of hull at waterline).

This integrates half-breadths along the hull length.

**Example:**
```python
from src.geometry import calculate_waterplane_area

wl = Waterline(z_reference=0.1, heel_angle=15.0)
wp_area = calculate_waterplane_area(hull, wl, num_stations=50)
print(f"Waterplane area: {wp_area:.4f} m²")
```

---

## Coordinate System Conversions

### Body-Fixed vs Earth-Fixed Coordinates

**Body-fixed**: Coordinate system fixed to the kayak (moves with it)
**Earth-fixed**: Stationary coordinate system (fixed to Earth)

### `transform_to_earth_coordinates(point, hull_orientation)`

Transform from body-fixed to earth-fixed coordinates.

**Parameters:**
- `point` (Point3D): Point in body-fixed coordinates
- `hull_orientation` (tuple): (heel, trim, yaw) in degrees

**Example:**
```python
from src.geometry import transform_to_earth_coordinates

point_body = Point3D(2.0, 0.5, 0.1)
orientation = (15.0, 5.0, 0.0)  # 15° heel, 5° trim, 0° yaw

point_earth = transform_to_earth_coordinates(point_body, orientation)
```

### `transform_to_body_coordinates(point, hull_orientation)`

Transform from earth-fixed to body-fixed coordinates (inverse transformation).

---

## Usage Examples

### Example 1: Stability Analysis Setup

```python
from src.geometry import (
    KayakHull, apply_heel_to_hull, Waterline,
    calculate_submerged_area, calculate_waterplane_area
)

# Create hull geometry
hull = KayakHull()
# ... add profiles ...

# Analyze at different heel angles
for heel_angle in range(0, 46, 5):
    # Transform hull
    heeled_hull = apply_heel_to_hull(hull, heel_angle)
    
    # Create waterline
    waterline = Waterline(z_reference=0.1, heel_angle=heel_angle)
    
    # Calculate properties
    wp_area = calculate_waterplane_area(heeled_hull, waterline)
    
    # Get midship section for detailed analysis
    midship = heeled_hull.get_profile(2.5)
    submerged_area = calculate_submerged_area(midship, waterline)
    
    print(f"Heel {heel_angle}°: WP Area = {wp_area:.3f} m², "
          f"Midship Submerged = {submerged_area:.3f} m²")
```

### Example 2: Waterline Visualization

```python
import numpy as np
import matplotlib.pyplot as plt

# Get profile at heel
profile = hull.get_profile(2.5)
heeled_profile = apply_heel_to_profile(profile, 20.0)

# Create waterline
waterline = Waterline(z_reference=0.1, heel_angle=20.0)

# Find intersections
intersections = find_profile_waterline_intersection(heeled_profile, waterline)

# Plot
y = heeled_profile.get_y_coordinates()
z = heeled_profile.get_z_coordinates()

plt.figure(figsize=(10, 6))
plt.plot(y, z, 'b-o', label='Profile')

# Plot waterline
y_range = np.linspace(y.min(), y.max(), 100)
z_wl = [waterline.z_at_point(2.5, yi) for yi in y_range]
plt.plot(y_range, z_wl, 'c--', label='Waterline', linewidth=2)

# Mark intersections
if intersections:
    int_y = [p.y for p in intersections]
    int_z = [p.z for p in intersections]
    plt.plot(int_y, int_z, 'r*', markersize=15, label='Intersections')

plt.xlabel('Y (Transverse) [m]')
plt.ylabel('Z (Vertical) [m]')
plt.title('Profile at 20° Heel with Waterline')
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.gca().invert_yaxis()
plt.show()
```

### Example 3: Time-Domain Simulation

```python
# Simulate kayak motion over time
import numpy as np

# Define motion (simplified)
time = np.linspace(0, 10, 100)  # 10 seconds
heel_motion = 15 * np.sin(2 * np.pi * 0.2 * time)  # 0.2 Hz oscillation
trim_motion = 5 * np.cos(2 * np.pi * 0.3 * time)   # 0.3 Hz oscillation

properties_history = []

for t, heel, trim in zip(time, heel_motion, trim_motion):
    # Transform hull
    transformed_hull = apply_heel_and_trim_to_hull(hull, heel, trim)
    
    # Calculate waterline properties
    wl = Waterline(z_reference=0.1, heel_angle=heel, trim_angle=trim)
    wp_area = calculate_waterplane_area(transformed_hull, wl)
    
    properties_history.append({
        'time': t,
        'heel': heel,
        'trim': trim,
        'waterplane_area': wp_area
    })

# Analyze results
# ... plotting, statistics, etc.
```

---

## Mathematical Background

### Rotation Matrices

**Heel (Roll about X-axis):**
```
Rx(θ) = [1    0       0   ]
        [0  cos(θ) -sin(θ)]
        [0  sin(θ)  cos(θ)]
```

**Trim (Pitch about Y-axis):**
```
Ry(θ) = [ cos(θ)  0  sin(θ)]
        [   0     1    0   ]
        [-sin(θ)  0  cos(θ)]
```

**Yaw (about Z-axis):**
```
Rz(θ) = [cos(θ) -sin(θ)  0]
        [sin(θ)  cos(θ)  0]
        [  0       0     1]
```

### Plane-Line Intersection

For line segment from P1 to P2 and plane ax + by + cz + d = 0:

1. Calculate signed distances: d1 = a·P1.x + b·P1.y + c·P1.z + d
2. If d1 and d2 have opposite signs, intersection exists
3. Intersection parameter: t = -d1 / (d2 - d1)
4. Intersection point: P = P1 + t(P2 - P1)

### Shoelace Formula (Area)

For polygon with vertices (y1, z1), ..., (yn, zn):
```
A = 0.5 * |Σ(yi * (z[i+1] - z[i-1]))|
```

---

## Performance Considerations

### Optimization Tips

1. **Cache transformations**: If analyzing at multiple heel angles, cache intermediate results
2. **Station count**: Balance accuracy vs. speed in `calculate_waterplane_area`
   - 20 stations: Fast, moderate accuracy
   - 50 stations: Good balance (default)
   - 100+ stations: High accuracy, slower

3. **Profile reuse**: Reuse interpolated profiles when possible

### Example: Efficient Multi-Angle Analysis

```python
# Pre-calculate properties at all angles
heel_angles = range(0, 46, 5)
results = {}

# Reuse waterline calculations
for heel in heel_angles:
    heeled_hull = apply_heel_to_hull(hull, heel)
    wl = Waterline(z_reference=0.1, heel_angle=heel)
    results[heel] = calculate_waterplane_area(heeled_hull, wl)
```

---

## Validation and Testing

### Unit Tests

Comprehensive test suite in `tests/test_transformations.py`:
- 33 unit tests covering all transformation functions
- Tests for edge cases (0°, 90°, 360°, negative angles)
- Waterline intersection validation
- Coordinate conversion round-trip tests

Run tests:
```bash
pytest tests/test_transformations.py -v
```

### Validation Cases

1. **90° heel**: Point at (x, 0, 1) → (x, -1, 0)
2. **360° rotation**: Returns to original position
3. **Symmetric waterline**: Port and starboard intersections equidistant from centerline

---

## Common Issues and Solutions

### Issue 1: Profile Validation Error After Trim

**Problem:** "Point has x=... but profile station is..."

**Solution:** This is handled automatically in `apply_trim_to_profile`. The function adjusts points to have consistent x-coordinates after rotation.

### Issue 2: No Waterline Intersections Found

**Possible causes:**
- Profile entirely above waterline (increase z_reference)
- Profile entirely below waterline (decrease z_reference)
- Waterline plane nearly perpendicular to profile

**Solution:** Check waterline z-coordinate relative to profile z-range.

### Issue 3: Unexpected Waterplane Area

**Check:**
- Sufficient station count (increase `num_stations`)
- Waterline z_reference appropriate for draft
- Hull profiles properly defined and ordered

---

## Integration with Other Modules

The transformations module works with:

- **Interpolation**: Can interpolate transformed hulls for finer analysis
- **Hydrostatics** (future): Uses submerged area calculations
- **Stability** (future): Primary module for stability analysis
- **Visualization**: Creates data for plotting heeled/trimmed configurations

---

## API Reference Summary

### Transformation Functions
- `apply_heel(point, angle, ref)` - Heel single point
- `apply_heel_to_profile(profile, angle, ref)` - Heel profile
- `apply_heel_to_hull(hull, angle, ref)` - Heel hull
- `apply_trim(point, angle, ref)` - Trim single point
- `apply_trim_to_profile(profile, angle, ref)` - Trim profile
- `apply_trim_to_hull(hull, angle, ref)` - Trim hull
- `apply_heel_and_trim(point, heel, trim, ref, order)` - Combined
- `apply_heel_and_trim_to_hull(hull, heel, trim, ref, order)` - Combined hull

### Waterline Class
- `Waterline(z_ref, heel, trim)` - Constructor
- `z_at_point(x, y)` - Z-coordinate at position
- `is_below_waterline(point)` - Check if submerged
- `signed_distance(point)` - Distance to waterline

### Intersection Functions
- `find_waterline_intersection_segment(p1, p2, wl)` - Segment intersection
- `find_profile_waterline_intersection(profile, wl)` - Profile intersections
- `get_submerged_points(profile, wl, include_ints)` - Submerged points

### Area Calculations
- `calculate_submerged_area(profile, wl)` - Cross-section area
- `calculate_waterplane_area(hull, wl, n_stations)` - Waterplane area

### Coordinate Conversions
- `transform_to_earth_coordinates(point, orientation)` - Body → Earth
- `transform_to_body_coordinates(point, orientation)` - Earth → Body

---

## Version History

- **v1.0** (2025-12-25): Initial implementation
  - Heel, trim, and combined transformations
  - Waterline class with plane equation
  - Waterline intersection calculations
  - Submerged area calculations
  - Waterplane area integration
  - Coordinate system conversions
  - Comprehensive test suite (33 tests)
  - Example visualizations

---

## See Also

- [Interpolation documentation](interpolation.md)
- [Profile class documentation](../src/geometry/profile.py)
- [Hull class documentation](../src/geometry/hull.py)
- [Examples directory](../examples/)
