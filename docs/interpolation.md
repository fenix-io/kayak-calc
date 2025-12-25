# Interpolation Functions Documentation

## Overview

The `interpolation.py` module provides comprehensive interpolation functions for kayak hull geometry. These functions enable smooth representation of hull surfaces and facilitate numerical calculations by creating intermediate profiles and points where needed.

## Table of Contents

1. [Transverse Interpolation](#transverse-interpolation)
2. [Longitudinal Interpolation](#longitudinal-interpolation)
3. [Bow/Stern Apex Interpolation](#bowstern-apex-interpolation)
4. [Symmetric Profile Creation](#symmetric-profile-creation)
5. [Profile Resampling](#profile-resampling)
6. [Usage Examples](#usage-examples)

---

## Transverse Interpolation

### Purpose
Transverse interpolation creates intermediate points along a single profile curve (cross-section), generating a smoother representation of the hull shape at a given longitudinal station.

### Functions

#### `interpolate_transverse(points, num_points, method='linear')`

Interpolates points along a transverse profile curve.

**Parameters:**
- `points` (List[Point3D]): List of points defining the profile (must have same x-coordinate)
- `num_points` (int): Number of points to generate in the interpolated result
- `method` (str): Interpolation method
  - `'linear'`: Linear interpolation (default)
  - `'cubic'`: Cubic spline interpolation (requires scipy)

**Returns:**
- List[Point3D]: Interpolated points uniformly distributed along the profile

**Example:**
```python
from src.geometry import Point3D, interpolate_transverse

points = [
    Point3D(0, -0.5, 0.1),
    Point3D(0, 0.0, 0.0),
    Point3D(0, 0.5, 0.1)
]

# Create 20 intermediate points
interpolated = interpolate_transverse(points, 20)
```

#### `interpolate_profile_transverse(profile, num_points, method='linear')`

Convenience wrapper for Profile objects.

**Parameters:**
- `profile` (Profile): Profile object to interpolate
- `num_points` (int): Number of points in the interpolated profile
- `method` (str): Interpolation method ('linear' or 'cubic')

**Returns:**
- Profile: New Profile with interpolated points at the same station

**Example:**
```python
from src.geometry import Profile, interpolate_profile_transverse

profile = Profile(0.0, points)
smooth_profile = interpolate_profile_transverse(profile, 50)
```

### When to Use
- Creating smoother profile representations for visualization
- Ensuring consistent point density across profiles
- Preparing profiles for numerical integration
- Generating intermediate points for waterline calculations

---

## Longitudinal Interpolation

### Purpose
Longitudinal interpolation creates intermediate profiles between two existing profiles at different longitudinal stations, enabling smooth hull representation along the kayak length.

### Functions

#### `interpolate_longitudinal(profile1, profile2, target_station, num_points=None)`

Interpolates a profile between two adjacent profiles.

**Parameters:**
- `profile1` (Profile): First profile (automatically ordered by station)
- `profile2` (Profile): Second profile (automatically ordered by station)
- `target_station` (float): Longitudinal position for the interpolated profile
- `num_points` (int, optional): Number of points in result (default: average of input profiles)

**Returns:**
- Profile: Interpolated profile at target_station

**Key Features:**
- Automatically orders profiles by station
- Handles profiles with different numbers of points
- Uses common y-coordinate range for interpolation
- Linear interpolation in both transverse and vertical dimensions

**Example:**
```python
from src.geometry import Profile, Point3D, interpolate_longitudinal

# Profile at station 0
p1 = Profile(0.0, [Point3D(0, -0.6, 0.2), Point3D(0, 0.6, 0.2)])

# Profile at station 2
p2 = Profile(2.0, [Point3D(2, -0.4, 0.15), Point3D(2, 0.4, 0.15)])

# Interpolate at midpoint
p_mid = interpolate_longitudinal(p1, p2, 1.0)
```

#### `interpolate_multiple_profiles(profiles, target_stations, num_points=None)`

Interpolates multiple profiles at specified target stations.

**Parameters:**
- `profiles` (List[Profile]): List of profiles (automatically sorted by station)
- `target_stations` (List[float]): Longitudinal positions for interpolated profiles
- `num_points` (int, optional): Number of points in each interpolated profile

**Returns:**
- List[Profile]: List of interpolated profiles

**Example:**
```python
from src.geometry import interpolate_multiple_profiles

profiles = [profile_at_0, profile_at_2, profile_at_4]
targets = [0.5, 1.0, 1.5, 2.5, 3.0, 3.5]

interpolated = interpolate_multiple_profiles(profiles, targets)
```

### When to Use
- Densifying profile distribution for smoother hull surface
- Creating intermediate sections for volume integration
- Generating profiles for stability calculations at specific heel angles
- Filling gaps in sparse profile data

### Mathematical Approach

For a target station `x_t` between profiles at `x_1` and `x_2`:

1. Calculate interpolation factor: `t = (x_t - x_1) / (x_2 - x_1)`
2. Create common y-coordinates from both profiles
3. Interpolate z-coordinates: `z_t = (1 - t) * z_1 + t * z_2`
4. Create new profile with interpolated points

---

## Bow/Stern Apex Interpolation

### Purpose
Creates intermediate profiles from an end profile to a bow or stern apex point, handling the tapering geometry where the hull narrows to a point at the ends.

### Function

#### `interpolate_to_apex(profile, apex_point, num_intermediate_stations=5, num_points_per_profile=None)`

Interpolates profiles from an end profile to apex point with progressive tapering.

**Parameters:**
- `profile` (Profile): End profile (bow or stern profile)
- `apex_point` (Point3D): Apex point (bow or stern tip)
- `num_intermediate_stations` (int): Number of profiles to create between profile and apex
- `num_points_per_profile` (int, optional): Number of points in each intermediate profile

**Returns:**
- List[Profile]: Intermediate profiles (excluding original profile and apex point itself)

**Key Features:**
- Automatically detects bow (forward) or stern (aft) direction
- Progressively reduces profile width toward apex
- Maintains shape characteristics during tapering
- Reduces point count as profiles approach apex

**Example:**
```python
from src.geometry import Profile, Point3D, interpolate_to_apex

# Bow profile at x=4.5
bow_profile = Profile(4.5, [
    Point3D(4.5, -0.3, 0.1),
    Point3D(4.5, 0.0, 0.0),
    Point3D(4.5, 0.3, 0.1)
])

# Bow apex at x=5.0
bow_apex = Point3D(5.0, 0.0, 0.15)

# Create 5 intermediate profiles
tapered = interpolate_to_apex(bow_profile, bow_apex, 5)
```

### When to Use
- Defining bow and stern geometry from end profiles
- Creating complete hull representation including tapered ends
- Ensuring smooth transition from hull body to ends
- Volume calculations that include bow/stern regions

### Tapering Algorithm

For each intermediate station between profile and apex:

1. Calculate progress factor: `t = distance_from_profile / total_distance`
2. Scale transverse coordinates: `y_scaled = y * (1 - t)`
3. Interpolate vertical coordinates: `z_scaled = z * (1 - t) + z_apex * t`
4. Reduce point count as approaching apex: `n_points = n_base * (1 - t * 0.5)`

---

## Symmetric Profile Creation

### Purpose
Creates a complete symmetric profile from starboard-side points only, automatically generating port-side mirror points.

### Function

#### `create_symmetric_profile(station, starboard_points, include_centerline=True)`

Creates symmetric profile by mirroring starboard points to port side.

**Parameters:**
- `station` (float): Longitudinal position for the profile
- `starboard_points` (List[Point3D]): Points on starboard side (y ≥ 0)
- `include_centerline` (bool): Whether to include centerline point if not present

**Returns:**
- Profile: Complete symmetric profile with port and starboard points

**Coordinate Convention:**
- Positive y = Starboard (right side when looking forward)
- Negative y = Port (left side when looking forward)
- y = 0 = Centerline

**Example:**
```python
from src.geometry import Point3D, create_symmetric_profile

# Define only starboard side
starboard = [
    Point3D(1.0, 0.0, 0.0),
    Point3D(1.0, 0.25, 0.05),
    Point3D(1.0, 0.5, 0.15)
]

# Create full symmetric profile
profile = create_symmetric_profile(1.0, starboard)
# Result includes mirrored port points + original starboard points
```

### When to Use
- Simplifying input data (only need to define half the hull)
- Ensuring perfect symmetry in profile definitions
- Creating profiles from measurements taken on one side only
- Reducing data entry errors

---

## Profile Resampling

### Purpose
Resamples existing profiles with different point distributions for improved numerical accuracy or visualization.

### Functions

#### `resample_profile_uniform_y(profile, num_points)`

Resamples profile with uniformly spaced y-coordinates.

**Parameters:**
- `profile` (Profile): Profile to resample
- `num_points` (int): Number of points in resampled profile

**Returns:**
- Profile: New profile with uniform y-spacing

**When to Use:**
- Creating consistent transverse spacing across profiles
- Simplifying mesh generation
- Preparing for specific integration methods

#### `resample_profile_uniform_arc(profile, num_points)`

Resamples profile with points uniformly distributed along arc length.

**Parameters:**
- `profile` (Profile): Profile to resample
- `num_points` (int): Number of points in resampled profile

**Returns:**
- Profile: New profile with uniform arc-length spacing

**When to Use:**
- Improving resolution in high-curvature regions
- Creating smoother surface representations
- Better capturing shape details in curved sections

**Example:**
```python
from src.geometry import resample_profile_uniform_arc

# Original profile with uneven point distribution
profile = Profile(2.0, original_points)

# Resample with uniform arc length spacing
smooth_profile = resample_profile_uniform_arc(profile, 30)
```

---

## Usage Examples

### Example 1: Complete Hull with Interpolation

```python
from src.geometry import KayakHull, Profile, Point3D
from src.geometry import interpolate_multiple_profiles

# Create hull with sparse profiles
hull = KayakHull()

# Add a few key profiles
hull.add_profile(Profile(0.0, stern_points))
hull.add_profile(Profile(2.5, midship_points))
hull.add_profile(Profile(5.0, bow_points))

# Densify with interpolation
original_profiles = list(hull.profiles.values())
target_stations = list(range(0.5, 5.0, 0.25))  # Every 25 cm

new_profiles = interpolate_multiple_profiles(
    original_profiles,
    target_stations
)

# Add to hull
for profile in new_profiles:
    hull.update_profile(profile)

print(f"Hull now has {hull.num_profiles} profiles")
```

### Example 2: Complete Bow Definition

```python
from src.geometry import interpolate_to_apex, create_symmetric_profile

# Define bow profile from starboard measurements only
bow_starboard = [
    Point3D(4.5, 0.0, 0.0),
    Point3D(4.5, 0.15, 0.03),
    Point3D(4.5, 0.30, 0.10)
]

# Create symmetric profile
bow_profile = create_symmetric_profile(4.5, bow_starboard)

# Define bow apex
bow_apex = Point3D(5.0, 0.0, 0.12)

# Create tapered profiles to apex
bow_profiles = interpolate_to_apex(bow_profile, bow_apex, 8)

# Add all to hull
hull.add_profile(bow_profile)
for profile in bow_profiles:
    hull.add_profile(profile)
```

### Example 3: Smooth Profile for Integration

```python
from src.geometry import (
    interpolate_profile_transverse,
    resample_profile_uniform_arc
)

# Start with coarse profile (few points)
coarse_profile = Profile(2.0, measurement_points)

# First, increase point count
denser = interpolate_profile_transverse(coarse_profile, 50)

# Then, ensure uniform arc-length spacing for accurate integration
smooth = resample_profile_uniform_arc(denser, 40)

# Use smooth profile for calculations
area = smooth.calculate_area_below_waterline(waterline_z=0.1)
```

---

## Best Practices

### Point Count Selection
- **Transverse interpolation**: 20-50 points typically sufficient
- **Longitudinal spacing**: 0.1-0.5m for typical kayaks
- **Bow/stern tapering**: 5-10 intermediate stations

### Accuracy Considerations
- Use uniform arc-length spacing for better shape fidelity
- Increase point density in high-curvature regions
- Balance accuracy vs. computational cost

### Common Pitfalls
- **Over-interpolation**: Too many points can slow calculations
- **Under-interpolation**: Too few points miss shape details
- **Inconsistent spacing**: Can cause numerical integration errors

### Performance Tips
- Cache interpolated profiles when possible
- Use linear interpolation for most cases (faster)
- Reserve cubic splines for visualization

---

## Mathematical Background

### Linear Interpolation Formula
For a point at parameter `t` between points `P1` and `P2`:
```
P(t) = (1 - t) * P1 + t * P2
where t ∈ [0, 1]
```

### Arc Length Calculation
Arc length between consecutive points:
```
L = Σ √[(x_{i+1} - x_i)² + (y_{i+1} - y_i)² + (z_{i+1} - z_i)²]
```

### Tapering Scale Factor
Linear tapering toward apex:
```
scale(t) = 1 - t
where t = distance_from_base / total_distance
```

---

## Error Handling

All interpolation functions include validation:
- **ValueError**: Invalid input parameters (e.g., insufficient points, out-of-range stations)
- **Automatic handling**: Profiles automatically sorted, ordered correctly

Common errors and solutions:
- **"Need at least 2 points"**: Provide more points in profile
- **"Target station outside range"**: Check station bounds
- **"Inconsistent x-coordinates"**: Ensure all points in profile have same station

---

## Integration with Other Modules

The interpolation functions integrate with:
- **Profile class**: All functions work with Profile objects
- **KayakHull class**: Can use hull.get_profile() with interpolation
- **Hydrostatics**: Provides smooth profiles for area/volume calculations
- **Visualization**: Creates smooth curves for plotting

---

## See Also

- [Profile class documentation](profile.py)
- [KayakHull class documentation](hull.py)
- [Point3D class documentation](point.py)
- [Examples directory](../examples/)

---

## Testing

Comprehensive unit tests available in:
- `tests/test_interpolation.py`: 25 test cases covering all functions

Run tests:
```bash
pytest tests/test_interpolation.py -v
```

---

## Version History

- **v1.0** (2025-12-25): Initial implementation
  - Transverse interpolation with linear and cubic methods
  - Longitudinal interpolation with automatic profile ordering
  - Bow/stern apex interpolation with tapering
  - Symmetric profile creation
  - Profile resampling (uniform y and arc length)
