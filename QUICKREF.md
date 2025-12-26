# Quick Reference Guide

**Kayak Calculation Tool - Code Snippets and Common Patterns**

Fast reference for users already familiar with the basics. For detailed tutorials, see [USER_GUIDE.md](USER_GUIDE.md).

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Code Snippets](#quick-code-snippets)
3. [File Format Templates](#file-format-templates)
4. [Common Workflows](#common-workflows)
5. [API Quick Reference](#api-quick-reference)
6. [Tips and Best Practices](#tips-and-best-practices)

---

## Installation

```bash
# Install from source
git clone <repository-url>
cd kyk-calc
pip install -e .

# Or with requirements only
pip install -r requirements.txt
```

**Dependencies:** Python 3.8+, NumPy, SciPy, Matplotlib

---

## Quick Code Snippets

### Load Hull Geometry

```python
from src.io import load_hull_from_json, load_hull_from_csv

# From JSON
hull = load_hull_from_json('data/sample_hull_kayak.json')

# From CSV
hull = load_hull_from_csv('data/sample_hull_simple.csv')
```

### Calculate Displacement

```python
from src.hydrostatics import calculate_volume

volume, cb = calculate_volume(hull, waterline_z=-0.1, num_sections=20)
displacement_kg = volume * 1025  # seawater density
print(f"Volume: {volume:.3f} m³, Displacement: {displacement_kg:.1f} kg")
```

### Define Center of Gravity

```python
from src.hydrostatics import CenterOfGravity

# Simple CG definition
cg = CenterOfGravity(x=2.5, y=0.0, z=-0.3, mass=100.0)

# CG from component masses
cg = CenterOfGravity.from_components([
    {'mass': 20.0, 'x': 2.0, 'y': 0.0, 'z': -0.2, 'name': 'hull'},
    {'mass': 80.0, 'x': 2.5, 'y': 0.0, 'z': -0.35, 'name': 'paddler'}
])
```

### Calculate Stability Curve

```python
from src.stability import StabilityAnalyzer

analyzer = StabilityAnalyzer(hull, cg)
results = analyzer.calculate_stability_curve(
    waterline_z=-0.1,
    heel_angles=range(0, 91, 5),
    num_sections=20
)

print(f"Initial GM: {results.initial_gm:.3f} m")
print(f"Max GZ: {results.max_gz:.3f} m at {results.max_gz_angle:.1f}°")
print(f"Vanishing angle: {results.vanishing_angle:.1f}°")
```

### Visualize Results

```python
from src.visualization import (
    plot_stability_curve, plot_hull_3d, plot_profile,
    plot_stability_comparison, interactive_heel_explorer
)

# Stability curve
plot_stability_curve(results, save_path='stability.png')

# 3D hull with waterline
plot_hull_3d(hull, waterline_z=-0.1, heel_angle=0, view='isometric')

# Profile at station
plot_profile(hull, station=2.5, waterline_z=-0.1, heel_angle=0)

# Compare multiple CG positions
plot_stability_comparison([results1, results2], labels=['CG Low', 'CG High'])

# Interactive heel explorer
interactive_heel_explorer(hull, cg, waterline_z=-0.1)
```

### Export Results

```python
from src.io import (
    export_stability_curve, export_hydrostatic_properties,
    generate_stability_report
)

# Export stability curve to CSV
export_stability_curve(results, 'output/stability.csv')

# Export hydrostatic properties
export_hydrostatic_properties(
    volume, cb, waterline_z=-0.1, 
    filename='output/hydrostatics.csv'
)

# Generate complete report
generate_stability_report(
    hull, cg, results,
    output_path='output/report.md',
    include_plots=True
)
```

---

## File Format Templates

### JSON Hull Format

```json
{
  "metadata": {
    "name": "My Kayak",
    "description": "Custom kayak design",
    "units": "m",
    "coordinate_system": "centerline_origin",
    "water_density": 1025.0
  },
  "profiles": [
    {
      "station": 0.0,
      "points": [
        {"x": 0.0, "y": -0.3, "z": -0.2},
        {"x": 0.0, "y": -0.3, "z": 0.0},
        {"x": 0.0, "y": 0.0, "z": 0.05},
        {"x": 0.0, "y": 0.3, "z": 0.0},
        {"x": 0.0, "y": 0.3, "z": -0.2}
      ]
    },
    {
      "station": 2.5,
      "points": [
        {"x": 2.5, "y": -0.35, "z": -0.25},
        {"x": 2.5, "y": -0.35, "z": 0.0},
        {"x": 2.5, "y": 0.0, "z": 0.1},
        {"x": 2.5, "y": 0.35, "z": 0.0},
        {"x": 2.5, "y": 0.35, "z": -0.25}
      ]
    }
  ],
  "bow": {"x": 5.0, "y": 0.0, "z": 0.15},
  "stern": {"x": -5.0, "y": 0.0, "z": 0.15}
}
```

### CSV Hull Format

```csv
# Kayak Hull Data
# units: m
# coordinate_system: centerline_origin
# water_density: 1025.0
x,y,z,station,point_type
0.0,-0.3,-0.2,0.0,profile
0.0,-0.3,0.0,0.0,profile
0.0,0.0,0.05,0.0,profile
0.0,0.3,0.0,0.0,profile
0.0,0.3,-0.2,0.0,profile
2.5,-0.35,-0.25,2.5,profile
2.5,-0.35,0.0,2.5,profile
2.5,0.0,0.1,2.5,profile
2.5,0.35,0.0,2.5,profile
2.5,0.35,-0.25,2.5,profile
5.0,0.0,0.15,5.0,bow
-5.0,0.0,0.15,-5.0,stern
```

---

## Common Workflows

### Workflow 1: Quick Displacement Check

```python
from src.io import load_hull_from_json
from src.hydrostatics import calculate_volume

# Load hull and calculate displacement
hull = load_hull_from_json('my_hull.json')
volume, cb = calculate_volume(hull, waterline_z=-0.15)
displacement = volume * 1025

print(f"Displacement: {displacement:.1f} kg")
print(f"Center of Buoyancy: ({cb.x:.2f}, {cb.y:.2f}, {cb.z:.2f})")
```

### Workflow 2: Complete Stability Analysis

```python
from src.io import load_hull_from_json, generate_stability_report
from src.hydrostatics import CenterOfGravity
from src.stability import StabilityAnalyzer
from src.visualization import plot_stability_curve

# 1. Load hull
hull = load_hull_from_json('my_hull.json')

# 2. Define CG
cg = CenterOfGravity(x=2.5, y=0.0, z=-0.3, mass=100.0)

# 3. Analyze stability
analyzer = StabilityAnalyzer(hull, cg)
results = analyzer.calculate_stability_curve(waterline_z=-0.1)

# 4. Plot and export
plot_stability_curve(results, save_path='stability.png', show=True)
generate_stability_report(hull, cg, results, 'report.md')

# 5. Check criteria
print(f"GM: {results.initial_gm:.3f} m {'✓ PASS' if results.initial_gm > 0.35 else '✗ FAIL'}")
print(f"Max GZ: {results.max_gz:.3f} m at {results.max_gz_angle:.0f}°")
print(f"Vanishing: {results.vanishing_angle:.0f}°")
```

### Workflow 3: Compare Design Variations

```python
from src.stability import StabilityAnalyzer
from src.hydrostatics import CenterOfGravity
from src.visualization import plot_stability_comparison

# Analyze multiple CG positions
cg_positions = [
    CenterOfGravity(x=2.5, y=0.0, z=-0.25, mass=100.0),  # High CG
    CenterOfGravity(x=2.5, y=0.0, z=-0.30, mass=100.0),  # Mid CG
    CenterOfGravity(x=2.5, y=0.0, z=-0.35, mass=100.0),  # Low CG
]

results_list = []
for cg in cg_positions:
    analyzer = StabilityAnalyzer(hull, cg)
    results = analyzer.calculate_stability_curve(waterline_z=-0.1)
    results_list.append(results)

plot_stability_comparison(
    results_list, 
    labels=['High CG', 'Mid CG', 'Low CG'],
    save_path='comparison.png'
)
```

### Workflow 4: Interactive Exploration

```python
from src.visualization import interactive_heel_explorer, interactive_cg_adjustment

# Explore heel behavior interactively
interactive_heel_explorer(hull, cg, waterline_z=-0.1)

# Adjust CG and see effects in real-time
interactive_cg_adjustment(hull, initial_cg=cg, waterline_z=-0.1)
```

---

## API Quick Reference

### Core Classes

| Class | Module | Purpose |
|-------|--------|---------|
| `KayakHull` | `src.geometry.hull` | Hull geometry container |
| `Profile` | `src.geometry.hull` | Transverse cross-section |
| `Point3D` | `src.geometry.hull` | 3D coordinate point |
| `CenterOfGravity` | `src.hydrostatics.center_of_gravity` | CG definition and management |
| `StabilityAnalyzer` | `src.stability.analyzer` | Main stability analysis engine |
| `StabilityResults` | `src.stability.analyzer` | Container for analysis results |

### Key Functions

**Hydrostatics:**
- `calculate_volume(hull, waterline_z, num_sections)` → `(volume, cb)`
- `calculate_center_of_buoyancy(hull, waterline_z, heel_angle)` → `Point3D`
- `calculate_cross_section_area(profile, waterline_z, heel_angle)` → `float`

**Stability:**
- `calculate_gz(hull, cg, waterline_z, heel_angle)` → `float`
- `calculate_gm(hull, cg, waterline_z)` → `float`

**Transformations:**
- `heel_transform(points, angle)` → `List[Point3D]`
- `trim_transform(points, angle)` → `List[Point3D]`
- `waterline_intersection(profile, waterline_z, heel_angle)` → `List[Point3D]`

**Interpolation:**
- `interpolate_longitudinal(profiles, num_sections)` → `List[Profile]`
- `interpolate_transverse(points, num_points)` → `List[Point3D]`

**I/O:**
- `load_hull_from_json(filepath)` → `KayakHull`
- `load_hull_from_csv(filepath)` → `KayakHull`
- `export_stability_curve(results, filepath)`
- `generate_stability_report(hull, cg, results, filepath)`

**Visualization:**
- `plot_stability_curve(results, **kwargs)`
- `plot_hull_3d(hull, **kwargs)`
- `plot_profile(hull, station, **kwargs)`
- `interactive_heel_explorer(hull, cg, waterline_z)`

---

## Tips and Best Practices

### Data Preparation
- Use 5-10 profiles for most kayaks
- Space profiles more densely where curvature is high
- Ensure profiles have consistent point ordering (e.g., port to starboard from bottom)
- Include at least 5-7 points per profile for accuracy

### Calculation Performance
- Use `num_sections=20` for fast calculations
- Use `num_sections=50-100` for publication-quality results
- Cache hull geometry if repeating calculations

### Stability Analysis
- Always check GM > 0.35 m for adequate stability
- Vanishing angle should be > 50° for safety
- Max GZ typically occurs at 25-40° for kayaks
- Compare with known good designs

### Visualization
- Use `save_path` parameter to avoid blocking show()
- Set `dpi=150` or higher for publication plots
- Use interactive tools for exploration, static plots for reports
- Export animations as MP4 for presentations

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -e .` from project root |
| Negative volume | Check profile point ordering (should go around perimeter) |
| No stability plot shows | Use `show=True` or save with `save_path='file.png'` |
| "Invalid waterline" error | Ensure waterline_z intersects hull geometry |
| Large GM values (>2m) | Check CG z-coordinate (should be negative for below waterline) |
| StabilityAnalyzer errors | Verify hull has at least 2 profiles and CG is defined |

---

## Next Steps

- Read the complete [USER_GUIDE.md](USER_GUIDE.md) for detailed tutorials
- Browse [examples/](examples/) directory for comprehensive examples
- Check [API documentation](docs/_build/html/index.html) for detailed reference
- Review [INPUT_DATA_FORMATS.md](INPUT_DATA_FORMATS.md) for file format details
- See [OUTPUT_DATA_FORMATS.md](OUTPUT_DATA_FORMATS.md) for export options

---

**Need Help?**
- Check the [USER_GUIDE.md](USER_GUIDE.md) troubleshooting section
- Review [examples/README.md](examples/README.md) for working examples
- Read the [theory documentation](docs/theory.rst) for background
- See API documentation for detailed function signatures
