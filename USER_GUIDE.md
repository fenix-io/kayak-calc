# User Guide

**Kayak Calculation Tool - Complete Usage Guide**

Welcome to the Kayak Calculation Tool! This guide will teach you everything you need to know to analyze kayak hulls for hydrostatic properties and stability characteristics.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation and Setup](#installation-and-setup)
3. [Basic Concepts](#basic-concepts)
4. [Loading Hull Geometry](#loading-hull-geometry)
5. [Hydrostatic Calculations](#hydrostatic-calculations)
6. [Stability Analysis](#stability-analysis)
7. [Visualization](#visualization)
8. [Exporting Results](#exporting-results)
9. [Working with Examples](#working-with-examples)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)
12. [Advanced Topics](#advanced-topics)

---

## Introduction

### What Does This Tool Do?

The Kayak Calculation Tool performs naval architecture calculations specifically for kayak hulls. It calculates:

- **Displacement**: The volume of water displaced and the corresponding weight
- **Center of Buoyancy (CB)**: The 3D centroid of the submerged volume
- **Center of Gravity (CG)**: The 3D centroid of the kayak's mass distribution
- **Stability Curves**: Graphs showing how the kayak behaves when heeled
- **Stability Metrics**: Key indicators like metacentric height (GM) and vanishing angle

### Who Is This For?

- Kayak designers creating new hulls
- Builders wanting to verify hull stability
- Engineers analyzing kayak performance
- Researchers studying small craft hydrostatics
- Students learning naval architecture

### What You Need to Know

**Prerequisites:**
- Basic Python programming
- Understanding of 3D coordinates
- Basic physics concepts (mass, volume, buoyancy)

**No prerequisites:**
- No naval architecture background needed (we'll explain concepts)
- No advanced mathematics needed (tool handles calculations)

---

## Installation and Setup

### Step 1: Check Prerequisites

You need Python 3.8 or later:

```bash
python --version
# Should show: Python 3.8.x or higher
```

If you don't have Python installed, download it from [python.org](https://www.python.org/).

### Step 2: Get the Code

Clone the repository (or download and extract the ZIP):

```bash
git clone <repository-url>
cd kyk-calc
```

### Step 3: Create Virtual Environment (Recommended)

It's best practice to use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it (Linux/Mac)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

### Step 4: Install Dependencies

Two options:

**Option A: Install as package (recommended)**
```bash
pip install -e .
```

This installs the tool and all dependencies.

**Option B: Install dependencies only**
```bash
pip install -r requirements.txt
```

This installs NumPy, SciPy, and Matplotlib but doesn't install the package.

### Step 5: Verify Installation

Test that everything works:

```bash
python -c "from src.io import load_hull_from_json; print('Success!')"
```

If you see "Success!" you're ready to go!

### Troubleshooting Installation

**Problem:** `ModuleNotFoundError: No module named 'numpy'`  
**Solution:** Run `pip install -r requirements.txt`

**Problem:** `ModuleNotFoundError: No module named 'src'`  
**Solution:** Run `pip install -e .` from the project root directory

**Problem:** Permission denied  
**Solution:** Add `--user` flag: `pip install --user -e .`

---

## Basic Concepts

### Coordinate System

The tool uses a **right-handed 3D coordinate system**:

```
      Z (up)
      |
      |_____ Y (starboard)
     /
    /
   X (forward)
```

- **X-axis**: Longitudinal (along kayak length, forward is positive)
- **Y-axis**: Transverse (across kayak width, starboard is positive, port is negative)
- **Z-axis**: Vertical (up is positive, down is negative)

The **origin** is usually placed:
- On the **centerline** (Y = 0)
- At **midship** (middle of the kayak length)
- At the **waterline** or **baseline**

### Hull Geometry Representation

A kayak hull is defined by **transverse profiles** at various **stations**:

```
Bow                                                   Stern
 *------Profile1--------Profile2--------Profile3------*
 0m                    2.5m            5.0m         7.5m
        Station 0       Station 2.5    Station 5.0
```

Each **profile** is a cross-section with multiple **points**:

```
      Profile at Station 2.5
           (deck)
            . . .
          .       .
        .           .
       .             .
      ._______________. (waterline)
     /                 \
    (                   ) (submerged)
     \                 /
       '----.   .----'
             '-'
          (bottom)
```

### Waterline

The **waterline** is the Z-coordinate where the water surface intersects the hull. Common conventions:

- **Positive Z**: waterline above origin (water level is high)
- **Negative Z**: waterline below origin (kayak sits deep)
- **Z = 0**: waterline at origin

Example: `waterline_z = -0.1` means the water surface is 0.1 meters below the origin.

### Center of Buoyancy (CB)

The **center of buoyancy** is the 3D centroid of the submerged volume. Think of it as the "center" of the underwater portion of the kayak.

- Calculated from hull geometry and waterline
- Changes when kayak heels or changes draft
- Always located in the submerged volume

### Center of Gravity (CG)

The **center of gravity** is the 3D centroid of the kayak's mass. Think of it as the "balance point" where all weight acts.

- Includes hull weight + paddler + gear
- Usually below the waterline for stability
- Fixed relative to the kayak (doesn't move when heeling)

### Stability and GZ Curve

**Stability** is the kayak's ability to return to upright when heeled.

The **righting arm (GZ)** measures this:
- **GZ > 0**: Kayak wants to return to upright (stable)
- **GZ < 0**: Kayak wants to capsize (unstable)
- **GZ = 0**: Neutral (at upright or at capsize point)

A **stability curve** plots GZ versus heel angle:

```
GZ (m)
  ^
0.2|     ___---
0.1|  __/       \
  0|_/___________\___
   0  15  30  45  60  75  90  (heel angle °)
```

Good features:
- Positive GZ for most angles (area under curve)
- Maximum GZ around 30-40° 
- Positive GZ extends beyond 50°

### Key Stability Metrics

**Initial Metacentric Height (GM)**
- Measure of stability for small heel angles
- GM > 0.35m is considered adequate for kayaks
- Higher GM = stiffer (more stable but less comfortable)
- Lower GM = tender (less stable but easier to roll)

**Maximum GZ**
- The peak value of the righting arm
- Usually occurs at 25-45° for kayaks
- Higher values indicate stronger righting ability

**Vanishing Angle**
- The heel angle where GZ becomes zero (starts to capsize)
- Should be > 50° for safety
- Higher angles indicate better ultimate stability

---

## Loading Hull Geometry

### Input File Formats

The tool supports two formats:

1. **JSON** - Complete format with metadata (recommended)
2. **CSV** - Simpler format, good for spreadsheet workflows

See [INPUT_DATA_FORMATS.md](INPUT_DATA_FORMATS.md) for detailed specifications.

### JSON Format Example

Create a file `my_kayak.json`:

```json
{
  "metadata": {
    "name": "My Custom Kayak",
    "units": "m",
    "coordinate_system": "centerline_origin",
    "water_density": 1025.0
  },
  "profiles": [
    {
      "station": 0.0,
      "points": [
        {"x": 0.0, "y": -0.3, "z": -0.2},
        {"x": 0.0, "y": 0.0, "z": 0.0},
        {"x": 0.0, "y": 0.3, "z": -0.2}
      ]
    },
    {
      "station": 2.5,
      "points": [
        {"x": 2.5, "y": -0.35, "z": -0.25},
        {"x": 2.5, "y": 0.0, "z": 0.05},
        {"x": 2.5, "y": 0.35, "z": -0.25}
      ]
    },
    {
      "station": 5.0,
      "points": [
        {"x": 5.0, "y": -0.25, "z": -0.15},
        {"x": 5.0, "y": 0.0, "z": 0.0},
        {"x": 5.0, "y": 0.25, "z": -0.15}
      ]
    }
  ],
  "bow": {"x": 6.0, "y": 0.0, "z": 0.1},
  "stern": {"x": -1.0, "y": 0.0, "z": 0.1}
}
```

### Loading the Hull

```python
from src.io import load_hull_from_json

# Load the hull
hull = load_hull_from_json('my_kayak.json')

# Inspect what we loaded
print(f"Number of profiles: {len(hull.profiles)}")
print(f"Profile stations: {[p.station for p in hull.profiles]}")
print(f"Bow at: {hull.bow}")
print(f"Stern at: {hull.stern}")
```

### CSV Format Example

Create a file `my_kayak.csv`:

```csv
# units: m
# water_density: 1025.0
x,y,z,station,point_type
0.0,-0.3,-0.2,0.0,profile
0.0,0.0,0.0,0.0,profile
0.0,0.3,-0.2,0.0,profile
2.5,-0.35,-0.25,2.5,profile
2.5,0.0,0.05,2.5,profile
2.5,0.35,-0.25,2.5,profile
5.0,-0.25,-0.15,5.0,profile
5.0,0.0,0.0,5.0,profile
5.0,0.25,-0.15,5.0,profile
6.0,0.0,0.1,6.0,bow
-1.0,0.0,0.1,-1.0,stern
```

Load it the same way:

```python
from src.io import load_hull_from_csv

hull = load_hull_from_csv('my_kayak.csv')
```

### Tips for Creating Hull Geometry

1. **Profile Spacing**
   - Use 5-10 profiles for typical kayaks
   - Place more profiles where curvature is high (near bow/stern)
   - Can be unequally spaced

2. **Points Per Profile**
   - Use 5-10 points per profile minimum
   - More points for accuracy in curved sections
   - Points should go around the perimeter consistently

3. **Point Ordering**
   - Keep consistent order (e.g., port-to-starboard, bottom-to-top)
   - Tool doesn't require specific order but consistency helps debugging

4. **Symmetry**
   - Most kayaks are symmetric about centerline
   - Include both port and starboard points
   - Centerline points (Y=0) highly recommended

5. **Units**
   - Meters recommended (most common in naval architecture)
   - Be consistent throughout the file
   - Specify in metadata

### Using Sample Data

The tool includes sample hulls:

```python
from src.io import load_hull_from_json

# Simple rectangular hull (for testing)
hull_simple = load_hull_from_json('data/sample_hull_simple.json')

# Realistic kayak hull
hull_kayak = load_hull_from_json('data/sample_hull_kayak.json')
```

See [data/README.md](data/README.md) for descriptions of each sample file.

---

## Hydrostatic Calculations

### Calculate Displacement

Displacement is the volume of water displaced by the hull:

```python
from src.io import load_hull_from_json
from src.hydrostatics import calculate_volume

# Load hull
hull = load_hull_from_json('data/sample_hull_kayak.json')

# Calculate volume at specific waterline
volume, cb = calculate_volume(
    hull,
    waterline_z=-0.1,  # 0.1m below origin
    num_sections=20     # number of integration points
)

# Calculate mass (displacement)
water_density = 1025  # kg/m³ (seawater)
displacement_kg = volume * water_density

print(f"Volume: {volume:.4f} m³")
print(f"Displacement: {displacement_kg:.2f} kg")
print(f"Center of Buoyancy: ({cb.x:.3f}, {cb.y:.3f}, {cb.z:.3f})")
```

**Output:**
```
Volume: 0.2750 m³
Displacement: 281.88 kg
Center of Buoyancy: (2.500, 0.000, -0.150)
```

### Understanding the Results

- **Volume** (m³): The underwater volume
- **Displacement** (kg): The weight of water displaced = weight the kayak can support
- **CB coordinates**:
  - X: longitudinal position of buoyancy center
  - Y: transverse position (0 for symmetric upright kayak)
  - Z: vertical position (usually negative = below waterline)

### Calculate Center of Buoyancy Only

If you just need CB without volume:

```python
from src.hydrostatics import calculate_center_of_buoyancy

cb = calculate_center_of_buoyancy(
    hull,
    waterline_z=-0.1,
    heel_angle=0  # degrees (0 = upright)
)

print(f"CB at: ({cb.x:.3f}, {cb.y:.3f}, {cb.z:.3f})")
```

### Effect of Waterline

Try different waterlines to see how displacement changes:

```python
waterlines = [-0.05, -0.10, -0.15, -0.20]  # meters

for wl in waterlines:
    volume, cb = calculate_volume(hull, waterline_z=wl)
    displacement = volume * 1025
    print(f"WL={wl:+.2f}m: Disp={displacement:6.1f}kg, VCB={cb.z:.3f}m")
```

**Output:**
```
WL=-0.05m: Disp= 141.0kg, VCB=-0.075m
WL=-0.10m: Disp= 281.9kg, VCB=-0.150m
WL=-0.15m: Disp= 422.7kg, VCB=-0.225m
WL=-0.20m: Disp= 563.6kg, VCB=-0.300m
```

Notice: Deeper waterline (more negative) → more displacement → CB moves down.

### Calculate Cross-Section Properties

You can analyze individual cross-sections:

```python
from src.hydrostatics import calculate_cross_section_area

# Get a profile
profile = hull.profiles[1]  # middle profile

# Calculate area below waterline
area = calculate_cross_section_area(
    profile,
    waterline_z=-0.1,
    heel_angle=0
)

print(f"Cross-section area at station {profile.station}: {area:.4f} m²")
```

---

## Stability Analysis

### Define Center of Gravity

Before stability analysis, you need to define the kayak's CG:

**Method 1: Direct Specification**

```python
from src.hydrostatics import CenterOfGravity

cg = CenterOfGravity(
    x=2.5,      # 2.5m from origin (longitudinal)
    y=0.0,      # on centerline
    z=-0.3,     # 0.3m below origin (vertical)
    mass=100.0  # 100kg total
)
```

**Method 2: From Components**

More realistic - calculate CG from individual masses:

```python
cg = CenterOfGravity.from_components([
    {'mass': 20.0, 'x': 2.0, 'y': 0.0, 'z': -0.15, 'name': 'hull'},
    {'mass': 10.0, 'x': 1.5, 'y': 0.0, 'z': -0.10, 'name': 'seat'},
    {'mass': 70.0, 'x': 2.5, 'y': 0.0, 'z': -0.35, 'name': 'paddler'},
])

print(f"Total mass: {cg.mass:.1f} kg")
print(f"CG position: ({cg.x:.2f}, {cg.y:.2f}, {cg.z:.2f})")
```

### Perform Stability Analysis

Use `StabilityAnalyzer` for complete analysis:

```python
from src.stability import StabilityAnalyzer

# Create analyzer
analyzer = StabilityAnalyzer(hull, cg)

# Calculate stability curve
results = analyzer.calculate_stability_curve(
    waterline_z=-0.1,             # waterline position
    heel_angles=range(0, 91, 5),  # 0° to 90° in 5° steps
    num_sections=20               # integration resolution
)

# Print key metrics
print(f"Initial GM: {results.initial_gm:.3f} m")
print(f"Maximum GZ: {results.max_gz:.3f} m at {results.max_gz_angle:.0f}°")
print(f"Vanishing angle: {results.vanishing_angle:.0f}°")
print(f"Range of positive stability: 0° to {results.vanishing_angle:.0f}°")
```

**Output:**
```
Initial GM: 0.425 m
Maximum GZ: 0.185 m at 35°
Vanishing angle: 68°
Range of positive stability: 0° to 68°
```

### Understanding Stability Results

**Initial GM (Metacentric Height)**
- Indicates initial stability (small angles)
- **Good**: GM > 0.35m (kayaks)
- **Tender**: GM = 0.2-0.35m
- **Unstable**: GM < 0.2m

**Maximum GZ**
- Peak righting ability
- **Good**: Max GZ > 0.15m (kayaks)
- Typically at 25-45° heel

**Vanishing Angle**
- Angle where kayak starts to capsize
- **Good**: > 60° (kayaks)
- **Minimum**: > 50°

### Calculate Single-Angle GZ

For specific heel angle:

```python
from src.stability import calculate_gz

gz_at_30 = calculate_gz(
    hull,
    cg,
    waterline_z=-0.1,
    heel_angle=30  # degrees
)

print(f"GZ at 30°: {gz_at_30:.4f} m")
```

### Compare Different CG Positions

See how CG height affects stability:

```python
cg_heights = [-0.25, -0.30, -0.35]  # meters (negative = below origin)

for z in cg_heights:
    cg = CenterOfGravity(x=2.5, y=0.0, z=z, mass=100.0)
    analyzer = StabilityAnalyzer(hull, cg)
    results = analyzer.calculate_stability_curve(waterline_z=-0.1)
    
    print(f"CG height {z:+.2f}m: GM={results.initial_gm:.3f}m, "
          f"MaxGZ={results.max_gz:.3f}m@{results.max_gz_angle:.0f}°")
```

**Output:**
```
CG height -0.25m: GM=0.325m, MaxGZ=0.145m@32°
CG height -0.30m: GM=0.425m, MaxGZ=0.185m@35°
CG height -0.35m: GM=0.525m, MaxGZ=0.225m@38°
```

**Interpretation:** Lower CG (more negative) → better stability.

---

## Visualization

### Plot Stability Curve

The most important visualization:

```python
from src.visualization import plot_stability_curve

# Calculate stability
analyzer = StabilityAnalyzer(hull, cg)
results = analyzer.calculate_stability_curve(waterline_z=-0.1)

# Plot
plot_stability_curve(
    results,
    save_path='my_stability_curve.png',
    show=True,
    figsize=(10, 6),
    dpi=150
)
```

This creates a professional GZ curve with annotations showing GM, max GZ, and vanishing angle.

### Plot 3D Hull

Visualize the hull geometry:

```python
from src.visualization import plot_hull_3d

plot_hull_3d(
    hull,
    waterline_z=-0.1,
    heel_angle=0,
    show_waterline=True,
    view='isometric',  # or 'top', 'side', 'front'
    save_path='hull_3d.png'
)
```

### Plot Specific Profile

View a single cross-section:

```python
from src.visualization import plot_profile

plot_profile(
    hull,
    station=2.5,       # longitudinal position
    waterline_z=-0.1,
    heel_angle=0,
    show_submerged=True,
    save_path='profile_at_2.5m.png'
)
```

### Compare Multiple Designs

Plot multiple stability curves together:

```python
from src.visualization import plot_stability_comparison

# Analyze multiple designs
cg1 = CenterOfGravity(x=2.5, y=0.0, z=-0.25, mass=100.0)
cg2 = CenterOfGravity(x=2.5, y=0.0, z=-0.35, mass=100.0)

results1 = StabilityAnalyzer(hull, cg1).calculate_stability_curve(waterline_z=-0.1)
results2 = StabilityAnalyzer(hull, cg2).calculate_stability_curve(waterline_z=-0.1)

# Compare
plot_stability_comparison(
    [results1, results2],
    labels=['High CG', 'Low CG'],
    save_path='comparison.png'
)
```

### Interactive Heel Explorer

Explore heel behavior interactively:

```python
from src.visualization import interactive_heel_explorer

interactive_heel_explorer(
    hull,
    cg,
    waterline_z=-0.1
)
```

This opens an interactive window where you can use a slider to change heel angle and see the hull and GZ value update in real-time.

### Interactive CG Adjustment

Adjust CG position interactively:

```python
from src.visualization import interactive_cg_adjustment

interactive_cg_adjustment(
    hull,
    initial_cg=cg,
    waterline_z=-0.1
)
```

Use sliders to adjust CG X, Y, Z and see the stability curve update immediately.

---

## Exporting Results

### Export Stability Curve Data

Save GZ data to CSV:

```python
from src.io import export_stability_curve

export_stability_curve(
    results,
    filename='output/stability_curve.csv',
    include_cb_data=True  # include center of buoyancy for each angle
)
```

**Output file format:**
```csv
# Stability Curve Export
# Waterline Z: -0.100000 m
# CG Position: (2.500, 0.000, -0.300) m
Heel_Angle_deg,GZ_m,LCB_m,VCB_m,TCB_m
0.000000,0.000000,2.500000,-0.150000,0.000000
5.000000,0.012500,2.500100,-0.149900,0.010100
10.000000,0.024800,2.500400,-0.149600,0.020200
...
```

### Export Hydrostatic Properties

Save displacement and CB data:

```python
from src.io import export_hydrostatic_properties

volume, cb = calculate_volume(hull, waterline_z=-0.1)

export_hydrostatic_properties(
    volume=volume,
    cb=cb,
    waterline_z=-0.1,
    filename='output/hydrostatics.csv'
)
```

### Generate Complete Report

Create a markdown report with all results:

```python
from src.io import generate_stability_report

generate_stability_report(
    hull,
    cg,
    results,
    output_path='output/stability_report.md',
    include_plots=True  # embed plots in report
)
```

This generates a comprehensive report including:
- Hull specifications
- CG definition
- Displacement calculations
- Stability metrics
- GZ curve plot
- Recommendations

### Export Plots

All plotting functions support saving:

```python
# Save as PNG
plot_stability_curve(results, save_path='curve.png', dpi=300)

# Save as PDF (vector graphics)
plot_stability_curve(results, save_path='curve.pdf')

# Save as SVG (vector graphics)
plot_stability_curve(results, save_path='curve.svg')
```

---

## Working with Examples

The `examples/` directory contains ready-to-run scripts demonstrating all features.

### List of Example Scripts

- `data_input_examples.py` - Loading hull data
- `volume_examples.py` - Displacement calculations
- `center_of_buoyancy_examples.py` - CB calculations
- `center_of_gravity_examples.py` - CG definition
- `stability_analyzer_examples.py` - Stability analysis
- `stability_curve_plotting_examples.py` - Visualization
- `interactive_visualization_examples.py` - Interactive tools

### Running Examples

```bash
# Run all examples in a script
python examples/stability_analyzer_examples.py

# Run specific example
python -c "
from examples.stability_analyzer_examples import example_1_basic_analysis
example_1_basic_analysis()
"
```

### Example Output

Examples generate output in `examples/output/`:
- PNG plots
- CSV data files
- Markdown reports

### Learning from Examples

1. **Start with `data_input_examples.py`** - Learn how to load data
2. **Try `volume_examples.py`** - Understand hydrostatics
3. **Explore `stability_analyzer_examples.py`** - See complete workflows
4. **Experiment with `interactive_visualization_examples.py`** - Interactive exploration

Each example is heavily commented and explains what it's doing.

---

## Troubleshooting

### Common Errors and Solutions

#### ModuleNotFoundError

**Error:**
```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
```bash
# Install package in development mode
pip install -e .
```

#### Negative Volume

**Error:**
```
ValueError: Calculated volume is negative
```

**Causes:**
- Profile points are not ordered consistently
- Profiles are in wrong order (bow/stern reversed)

**Solution:**
- Check point ordering in each profile
- Ensure all profiles go around perimeter the same way
- Verify profile stations are in increasing order

#### Invalid Waterline

**Error:**
```
ValueError: Waterline does not intersect hull
```

**Cause:** Waterline Z is above or below all hull geometry

**Solution:**
- Check the Z-range of your hull
- Adjust `waterline_z` to be within hull bounds
- For `waterline_z=-0.1`, hull should extend from approximately Z=-0.3 to Z=+0.2

#### No Plot Appears

**Problem:** Code runs but no plot shows

**Solutions:**
```python
# Option 1: Add show=True
plot_stability_curve(results, show=True)

# Option 2: Save to file
plot_stability_curve(results, save_path='curve.png')

# Option 3: Use matplotlib explicitly
import matplotlib.pyplot as plt
plot_stability_curve(results)
plt.show()
```

#### Unrealistic GM Values

**Problem:** GM is very large (>2m) or negative

**Causes:**
- CG z-coordinate has wrong sign
- CG is far from CB
- Hull geometry error

**Solution:**
- Check CG z is negative (below waterline typically)
- Verify CG is reasonable relative to hull size
- Check hull loads correctly

#### Stability Analyzer Errors

**Error:**
```
ValueError: Hull must have at least 2 profiles
```

**Solution:** Ensure hull JSON/CSV has at least 2 profiles defined

**Error:**
```
TypeError: cg must be a CenterOfGravity object
```

**Solution:**
```python
# Wrong:
analyzer = StabilityAnalyzer(hull, (2.5, 0, -0.3))

# Correct:
from src.hydrostatics import CenterOfGravity
cg = CenterOfGravity(x=2.5, y=0.0, z=-0.3, mass=100.0)
analyzer = StabilityAnalyzer(hull, cg)
```

### Getting Help

1. **Check Examples** - See `examples/` directory
2. **Read API Docs** - See `docs/_build/html/index.html`
3. **Search Issues** - Check GitHub issues
4. **Review Input Formats** - See INPUT_DATA_FORMATS.md
5. **Check Theory** - See docs/theory.rst

---

## Best Practices

### Data Preparation

1. **Profile Spacing**
   - 5-7 profiles minimum for accurate kayak
   - Place more profiles where hull curvature is high
   - Don't need perfectly even spacing

2. **Points Per Profile**
   - 7-10 points per profile recommended
   - More points in curved regions
   - Include centerline point (Y=0) for symmetry

3. **Measurement Strategy**
   - Measure from physical kayak or from plans
   - Digital calipers for precision
   - Take photos from multiple angles for reference

4. **Validation**
   - Plot hull in 3D to check shape looks correct
   - Calculate displacement and compare to known values
   - Check CB position is reasonable

### Stability Analysis

1. **Waterline Selection**
   - Use realistic loaded waterline
   - Try multiple waterlines to see effect of loading
   - Record which waterline corresponds to design condition

2. **CG Determination**
   - Measure component weights accurately
   - Include all gear (paddler, equipment, hull)
   - Consider different loading scenarios

3. **Interpretation**
   - Compare to similar known-good kayaks
   - Don't rely on a single metric (check GM, max GZ, vanishing angle)
   - Consider intended use (touring vs. racing vs. whitewater)

4. **Safety Margins**
   - GM > 0.35m for adequate stability
   - Max GZ > 0.15m
   - Vanishing angle > 50°
   - Don't design right at the limits

### Workflow Efficiency

1. **Use Virtual Environments**
   - Keeps project dependencies isolated
   - Prevents version conflicts

2. **Cache Hull Geometry**
   - Load once, reuse for multiple analyses
   - Saves file I/O time

3. **Batch Calculations**
   - Analyze multiple CG positions in a loop
   - Generate comparison plots
   - Export all results together

4. **Document Your Work**
   - Use meaningful filenames
   - Add comments to analysis scripts
   - Export reports with metadata

### Code Organization

Good script structure:

```python
# Standard imports
from src.io import load_hull_from_json
from src.hydrostatics import CenterOfGravity
from src.stability import StabilityAnalyzer
from src.visualization import plot_stability_curve

# Configuration
HULL_FILE = 'my_kayak.json'
WATERLINE_Z = -0.1
OUTPUT_DIR = 'output'

# Load hull
hull = load_hull_from_json(HULL_FILE)

# Define CG
cg = CenterOfGravity(x=2.5, y=0.0, z=-0.3, mass=100.0)

# Analyze
analyzer = StabilityAnalyzer(hull, cg)
results = analyzer.calculate_stability_curve(waterline_z=WATERLINE_Z)

# Report key metrics
print(f"GM: {results.initial_gm:.3f} m")
print(f"Max GZ: {results.max_gz:.3f} m at {results.max_gz_angle:.0f}°")

# Visualize
plot_stability_curve(results, save_path=f'{OUTPUT_DIR}/stability.png')
```

---

## Advanced Topics

### Custom Interpolation Density

Control interpolation resolution:

```python
from src.geometry.interpolation import interpolate_longitudinal

# Generate more intermediate profiles
fine_profiles = interpolate_longitudinal(
    hull.profiles,
    num_sections=50  # creates 50 sections (high resolution)
)
```

### Heel and Trim Combined

Analyze heeled AND trimmed condition:

```python
from src.geometry.transformations import heel_transform, trim_transform

# Apply both transformations
points_heeled = heel_transform(profile.points, heel_angle=20)
points_trimmed = trim_transform(points_heeled, trim_angle=5)
```

### Custom Integration Methods

Use different numerical integration:

```python
from src.hydrostatics.volume import calculate_volume

# Trapezoidal rule
volume_trap, cb = calculate_volume(hull, waterline_z=-0.1, method='trapezoidal')

# Simpson's rule (more accurate, default)
volume_simp, cb = calculate_volume(hull, waterline_z=-0.1, method='simpson')
```

### Waterplane Area

Calculate waterplane area (area of hull cross-section at waterline):

```python
from src.hydrostatics import calculate_waterplane_area

wp_area = calculate_waterplane_area(hull, waterline_z=-0.1)
print(f"Waterplane area: {wp_area:.3f} m²")
```

### Batch Processing Multiple Hulls

Analyze many hulls automatically:

```python
import glob
from pathlib import Path

# Find all JSON files in data directory
hull_files = glob.glob('data/*.json')

results_summary = []

for hull_file in hull_files:
    hull = load_hull_from_json(hull_file)
    cg = CenterOfGravity(x=2.5, y=0.0, z=-0.3, mass=100.0)
    analyzer = StabilityAnalyzer(hull, cg)
    results = analyzer.calculate_stability_curve(waterline_z=-0.1)
    
    results_summary.append({
        'file': Path(hull_file).name,
        'GM': results.initial_gm,
        'max_GZ': results.max_gz,
        'vanishing_angle': results.vanishing_angle
    })

# Print summary table
for r in results_summary:
    print(f"{r['file']:30s} GM={r['GM']:.3f} MaxGZ={r['max_GZ']:.3f}")
```

### Custom Visualization Styles

Customize plots:

```python
import matplotlib.pyplot as plt

# Set style
plt.style.use('seaborn-v0_8-darkgrid')

# Create custom plot
fig, ax = plt.subplots(figsize=(12, 6))
plot_stability_curve(results, ax=ax, color='navy', linewidth=2.5)
ax.set_title('My Custom Stability Curve', fontsize=16)
ax.grid(True, alpha=0.3)
plt.savefig('custom_curve.png', dpi=300, bbox_inches='tight')
```

### Programmatic Hull Generation

Create hull geometry programmatically:

```python
from src.geometry.hull import KayakHull, Profile, Point3D

# Create empty hull
hull = KayakHull()

# Generate profiles programmatically
for x in [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]:
    # Calculate profile shape based on position
    beam = 0.6 * (1 - abs(x - 2.5) / 2.5)  # Tapers toward ends
    depth = 0.3
    
    points = [
        Point3D(x, -beam/2, -depth),      # port bottom
        Point3D(x, -beam/2, 0),           # port waterline
        Point3D(x, 0, depth/4),           # centerline top
        Point3D(x, beam/2, 0),            # starboard waterline
        Point3D(x, beam/2, -depth)        # starboard bottom
    ]
    
    profile = Profile(station=x, points=points)
    hull.add_profile(profile)

# Set bow and stern
hull.bow = Point3D(6.0, 0, 0.2)
hull.stern = Point3D(-1.0, 0, 0.2)

# Now analyze this hull
analyzer = StabilityAnalyzer(hull, cg)
results = analyzer.calculate_stability_curve(waterline_z=-0.1)
```

---

## Conclusion

You now have a complete understanding of how to use the Kayak Calculation Tool!

### Next Steps

1. **Try the Examples** - Run scripts in `examples/` directory
2. **Analyze Your Own Hull** - Create a JSON/CSV file for your kayak
3. **Experiment** - Try different CG positions, waterlines, hull shapes
4. **Read the Theory** - See `docs/theory.rst` for mathematical background
5. **Explore the API** - See `docs/_build/html/index.html` for all functions

### Quick Reference

For experienced users, see:
- [QUICKREF.md](QUICKREF.md) - Fast reference guide
- [INPUT_DATA_FORMATS.md](INPUT_DATA_FORMATS.md) - File format specs
- [OUTPUT_DATA_FORMATS.md](OUTPUT_DATA_FORMATS.md) - Export formats
- API documentation - Complete function reference

### Getting Help

- Check [examples/README.md](examples/README.md) for example descriptions
- Review [docs/README.md](docs/README.md) for documentation guide
- See API documentation for detailed function signatures
- Check troubleshooting section in this guide

### Contributing

Found a bug? Have a feature request? Want to contribute?
- Report issues on GitHub
- Submit pull requests
- Improve documentation
- Share your kayak designs!

---

**Happy Calculating!** 🛶
