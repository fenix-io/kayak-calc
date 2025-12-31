# Sample Hull Datasets

This directory contains sample kayak hull geometries for testing, learning, and demonstration purposes.

---

## Available Files

### 1. sample_hull_simple.json
### 2. sample_hull_simple.csv  
### 3. sample_hull_kayak.json
### 4. sample_hull_multipoint_bow_stern.json

---

## File Descriptions

### sample_hull_simple.json / sample_hull_simple.csv

**Type:** Simplified box-like hull  
**Format:** JSON and CSV versions (same geometry)  
**Purpose:** Testing, debugging, validation

**Description:**
A simple rectangular kayak hull with minimal complexity. Designed for:
- Learning the file format
- Testing calculations against hand calculations
- Debugging code
- Validating numerical methods

**Characteristics:**
- **Length:** 5.0 meters
- **Beam:** 0.6 meters (max width)
- **Profiles:** 5 cross-sections
- **Shape:** Near-rectangular with slight taper
- **Symmetry:** Symmetric about centerline
- **Complexity:** Low (simple geometry)

**Expected Results** (at waterline Z = -0.1 m):
```
Volume:        ~0.275 m³
Displacement:  ~282 kg (seawater)
LCB:           ~2.5 m (midship)
VCB:           ~-0.15 m
GM:            ~0.42 m (with CG at z=-0.3)
Max GZ:        ~0.18 m (at ~35° heel)
Vanishing:     ~68°
```

**Usage Example:**
```python
from src.io import load_hull_from_json
from src.hydrostatics import calculate_volume

# Load the hull
hull = load_hull_from_json('data/sample_hull_simple.json')

# Calculate displacement
volume, cb = calculate_volume(hull, waterline_z=-0.1)
print(f"Volume: {volume:.4f} m³")
print(f"Displacement: {volume * 1025:.1f} kg")
```

**When to Use:**
- ✅ First-time users learning the tool
- ✅ Testing code changes
- ✅ Validating calculations
- ✅ Creating tutorials and examples
- ❌ Not for realistic kayak design

---

### sample_hull_kayak.json

**Type:** Realistic sea kayak hull  
**Format:** JSON  
**Purpose:** Real-world analysis, demonstrations

**Description:**
A realistic sea kayak hull with proper features:
- Bow and stern taper
- Rocker (curved keel line)
- Realistic cross-section shapes
- Proper deck curvature

Represents a typical touring/sea kayak suitable for coastal paddling.

**Characteristics:**
- **Length:** 5.2 meters (17 feet)
- **Beam:** 0.55 meters (22 inches)
- **Profiles:** 9 cross-sections
- **Shape:** Realistic taper, rocker, and curvature
- **Symmetry:** Symmetric about centerline
- **Complexity:** Medium (realistic kayak)

**Design Features:**
- Moderate V-hull for tracking
- Soft chines for stability
- Rocker for maneuverability
- Deck crown for shedding water
- Typical sea kayak proportions

**Expected Results** (at waterline Z = -0.1 m, CG at x=2.5, z=-0.3, mass=100kg):
```
Volume:        ~0.285 m³
Displacement:  ~292 kg (seawater)
LCB:           ~2.45-2.55 m
VCB:           ~-0.145 m
GM:            ~0.45 m
Max GZ:        ~0.20 m (at ~33° heel)
Vanishing:     ~72°
```

**Loading Scenarios:**

**Light Load** (paddler + minimal gear):
- Total mass: 100 kg
- CG: (2.5, 0.0, -0.30)
- Waterline: -0.08 to -0.10 m

**Medium Load** (paddler + day gear):
- Total mass: 120 kg
- CG: (2.5, 0.0, -0.32)
- Waterline: -0.10 to -0.12 m

**Heavy Load** (paddler + camping gear):
- Total mass: 150 kg
- CG: (2.5, 0.0, -0.34)
- Waterline: -0.12 to -0.15 m

**Usage Example:**
```python
from src.io import load_hull_from_json
from src.hydrostatics import CenterOfGravity
from src.stability import StabilityAnalyzer
from src.visualization import plot_stability_curve

# Load realistic kayak
hull = load_hull_from_json('data/sample_hull_kayak.json')

# Define typical loading (paddler + gear)
cg = CenterOfGravity.from_components([
    {'mass': 22.0, 'x': 2.0, 'y': 0.0, 'z': -0.15, 'name': 'hull'},
    {'mass': 75.0, 'x': 2.5, 'y': 0.0, 'z': -0.35, 'name': 'paddler'},
    {'mass': 8.0, 'x': 2.2, 'y': 0.0, 'z': -0.25, 'name': 'gear'},
])

# Analyze stability
analyzer = StabilityAnalyzer(hull, cg)
results = analyzer.calculate_stability_curve(waterline_z=-0.1)

# Report results
print(f"Total mass: {cg.mass:.1f} kg")
print(f"GM: {results.initial_gm:.3f} m")
print(f"Max GZ: {results.max_gz:.3f} m at {results.max_gz_angle:.0f}°")
print(f"Vanishing: {results.vanishing_angle:.0f}°")

# Visualize
plot_stability_curve(results, save_path='kayak_stability.png', show=True)
```

**When to Use:**
- ✅ Realistic kayak analysis
- ✅ Demonstration of tool capabilities
- ✅ Learning stability characteristics
- ✅ Comparing design variations
- ✅ Example for documentation

---

## File Format Notes

### JSON Format Features
- Complete metadata (name, description, units)
- Structured profile organization
- Easy to read and edit
- Validation-friendly
- Recommended for new files

### CSV Format Features
- Simpler for spreadsheet workflows
- Smaller file size
- Metadata in comments
- Good for simple hulls
- Easy export from CAD

**Conversion:** Both formats represent identical geometry and can be converted:
```python
from src.io import load_hull_from_json, export_hull_to_csv

hull = load_hull_from_json('sample_hull_simple.json')
export_hull_to_csv(hull, 'sample_hull_simple.csv')
```

---

## Creating Your Own Hull Files

### Data Collection

**From Physical Kayak:**
1. Measure transverse profiles at 5-10 stations along length
2. Use calipers or template for accurate profiles
3. Record bow and stern apex points
4. Note waterline marks for reference

**From Plans/CAD:**
1. Extract profile coordinates at key stations
2. Export as CSV or create JSON manually
3. Verify coordinate system matches (centerline origin)

**From Digital Model:**
1. Section model at regular intervals
2. Extract profile point coordinates
3. Convert to JSON/CSV format
4. Validate with visualization

### Recommended Profile Spacing

- **Minimum:** 3 profiles (bow, mid, stern)
- **Good:** 5-7 profiles
- **Optimal:** 9-11 profiles
- **Maximum:** 15+ profiles (diminishing returns)

Place more profiles where curvature is high (near bow/stern).

### Points Per Profile

- **Minimum:** 5 points
- **Good:** 7-9 points  
- **Optimal:** 11-15 points
- **Maximum:** 20+ points (overkill)

Include points at:
- Centerline (Y=0)
- Waterline area
- Chines (sharp curves)
- Deck edges
- Keel area

**Point Ordering:** List points in consistent order for all profiles:
- Recommended: Port side (y < 0) → Keel (y = 0) → Starboard side (y > 0)
- Walk each profile from port deck/waterline, down through port side, across keel, up through starboard side, to starboard deck/waterline
- **Critical:** Use the same traversal direction for every profile

**Bow/Stern:** No explicit bow or stern entries needed in hull files. The software automatically derives bow and stern positions from the first and last profiles.

### Validation Checklist

Before using a new hull file:

1. **Load and visualize:**
   ```python
   from src.visualization import plot_hull_3d
   hull = load_hull_from_json('my_hull.json')
   plot_hull_3d(hull, view='isometric')
   ```

2. **Check displacement:**
   ```python
   from src.hydrostatics import calculate_volume
   volume, cb = calculate_volume(hull, waterline_z=-0.1)
   print(f"Volume: {volume:.4f} m³")
   # Should be reasonable for hull size
   ```

3. **Verify symmetry:**
   ```python
   # CB should be on centerline (TCB ≈ 0)
   print(f"TCB: {cb.y:.6f}")  # Should be near 0.0
   ```

4. **Test stability:**
   ```python
   from src.stability import StabilityAnalyzer
   from src.hydrostatics import CenterOfGravity
   
   cg = CenterOfGravity(x=2.5, y=0.0, z=-0.3, mass=100.0)
   analyzer = StabilityAnalyzer(hull, cg)
   results = analyzer.calculate_stability_curve(waterline_z=-0.1)
   
   # Check for reasonable values
   print(f"GM: {results.initial_gm:.3f} m")  # Should be 0.2-0.8 m
   print(f"Max GZ: {results.max_gz:.3f} m")  # Should be 0.1-0.3 m
   ```

---

## Common Issues

### Negative Volume
**Symptom:** Volume calculation returns negative value  
**Cause:** Profile points ordered incorrectly or profiles out of sequence  
**Fix:** Ensure consistent point ordering (e.g., port→centerline→starboard, bottom→top)

### Unrealistic CB Position
**Symptom:** CB far from expected location  
**Cause:** Profile station values incorrect or hull asymmetric  
**Fix:** Check station X-coordinates match profile point X-coordinates

### Very High/Low GM
**Symptom:** GM > 1.0 m or GM < 0.1 m  
**Cause:** Hull geometry error or CG position wrong  
**Fix:** Visualize hull, check profile shapes, verify CG location

### Validation Errors
**Symptom:** File fails to load with validation error  
**Cause:** Missing required fields or invalid values  
**Fix:** Check INPUT_DATA_FORMATS.md for requirements

---

## Additional Resources

- **[INPUT_DATA_FORMATS.md](../INPUT_DATA_FORMATS.md)** - Complete file format specification
- **[USER_GUIDE.md](../USER_GUIDE.md)** - How to use hull files in calculations
- **[examples/data_input_examples.py](../examples/data_input_examples.py)** - Loading examples
- **[docs/getting_started.rst](../docs/getting_started.rst)** - Getting started tutorial

---

## File History

- `sample_hull_simple.*` - Created for Phase 2 (basic testing)
- `sample_hull_kayak.json` - Created for Phase 5 (realistic analysis)
- `sample_hull_multipoint_bow_stern.json` - Created for Phase 9 (multi-point bow/stern demonstration)

---

### 4. sample_hull_multipoint_bow_stern.json

**Type:** Realistic sea kayak with multi-point bow/stern  
**Format:** JSON  
**Purpose:** Demonstrating multi-point bow/stern arrays with rocker control

**Description:**
A sea kayak hull using the new multi-point bow/stern format. Instead of single apex points, the bow and stern are defined by arrays of points at different vertical levels (gunwale, chines, keel).

**Characteristics:**
- **Length:** 5.2 meters
- **Beam:** 0.55 meters
- **Profiles:** 5 cross-sections with explicit level attributes
- **Bow Points:** 4 levels (gunwale at x=0.0, keel at x=0.45)
- **Stern Points:** 4 levels (gunwale at x=5.2, keel at x=4.70)
- **Shape:** Traditional sea kayak with pronounced rocker
- **Levels:** "gunwale", "chine_upper", "chine_lower", "keel"

**Key Features:**
1. **Independent rocker curves** - Each level (keel, chines, gunwale) has its own longitudinal position at bow/stern
2. **Realistic end shape** - Keel extends further forward (x=0.45) than gunwale (x=0.0), creating proper bow shape
3. **Explicit level matching** - All points have "level" attribute for clear correspondence
4. **Smooth interpolation** - System generates intermediate profiles between last station and bow/stern points

**Rocker Configuration:**
- **Bow:** Gunwale rises to z=0.50, keel extends to x=0.45 at z=-0.18
- **Stern:** Gunwale at z=0.48, keel ends at x=4.70 at z=-0.20
- **Effect:** More maneuverable than flat keel, good tracking with moderate rocker

**Usage Example:**
```python
from src.io import load_kayak_from_json

# Load hull with multi-point bow/stern
hull = load_kayak_from_json("data/sample_hull_multipoint_bow_stern.json")

# System automatically interpolates between profiles and bow/stern points
print(f"Number of profiles after interpolation: {hull.num_profiles}")
print(f"Bow points: {len(hull.bow_points)}")
print(f"Stern points: {len(hull.stern_points)}")

# Visualize to see rocker lines
from src.visualization import plot_profile_view, plot_plan_view, plot_hull_3d
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
plot_profile_view(hull, ax=axes[0])  # Side view showing rocker
plot_plan_view(hull, ax=axes[1])     # Top view showing beam
plt.show()
```

**Learning Points:**
- How to define multi-point bow/stern arrays
- Using level attributes for explicit matching
- Creating realistic rocker curves
- Visualizing rocker lines at different levels

---

## Contributing

Have a good example hull? Consider contributing:
1. Ensure it's your own design or properly licensed
2. Validate it loads and produces reasonable results
3. Document key characteristics and expected values
4. Submit as pull request with description

---

**Questions?** See [USER_GUIDE.md](../USER_GUIDE.md) or [examples/README.md](../examples/README.md)
