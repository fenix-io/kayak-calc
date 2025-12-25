# Examples Directory

This directory contains example scripts demonstrating the use of the kayak calculation library.

## Available Examples

### interpolation_examples.py

Comprehensive demonstration of all interpolation functions with visualizations.

**Run the examples:**
```bash
python examples/interpolation_examples.py
```

**What it demonstrates:**
1. **Transverse Interpolation** - Creating smooth profiles from sparse points
2. **Longitudinal Interpolation** - Creating intermediate profiles between stations
3. **Bow/Stern Apex Interpolation** - Tapering profiles toward bow/stern points
4. **Symmetric Profile Creation** - Building full profiles from starboard data only
5. **Complete Hull Interpolation** - Full workflow with 3D visualization

**Generated visualizations:**
- `example_transverse_interpolation.png` - 2D profile smoothing
- `example_longitudinal_interpolation.png` - 3D interpolation between stations
- `example_bow_stern_interpolation.png` - 3D tapering toward apex
- `example_symmetric_profile.png` - 2D symmetric profile generation
- `example_complete_hull.png` - 3D complete hull with surface mesh

### righting_arm_examples.py

Comprehensive demonstration of righting arm (GZ) and stability curve calculations.

**Run the examples:**
```bash
python examples/righting_arm_examples.py
```

**What it demonstrates:**
1. **Single Angle GZ Calculation** - Calculate righting arm at specific heel angle
2. **Complete GZ Curve Generation** - Generate full stability curve (0° to 90°)
3. **Stability Metrics Analysis** - Extract key stability parameters
4. **CG Position Comparison** - Compare stability for different CG locations
5. **Waterline Comparison** - Compare stability at different loading conditions

**Generated visualizations:**
- `example_single_gz.png` - Single heel angle calculation
- `example_gz_curve.png` - Complete stability curve
- `example_stability_metrics.png` - Key stability metrics
- `example_cg_comparison.png` - CG position comparison
- `example_waterline_comparison.png` - Loading condition comparison

### stability_analyzer_examples.py

Demonstration of the object-oriented StabilityAnalyzer interface for stability analysis.

**Run the examples:**
```bash
python examples/stability_analyzer_examples.py
```

**What it demonstrates:**
1. **Basic Analyzer Usage** - Create analyzer and calculate GZ at specific angles
2. **Generate Stability Curves** - Generate and analyze complete stability curves
3. **Comprehensive Summary** - Get all stability information in one call
4. **Compare CG Positions** - Compare stability for multiple CG configurations
5. **Compare Waterlines** - Compare different loading conditions
6. **Custom Angle Ranges** - Use custom heel angle ranges and steps
7. **Quick Analysis** - Use convenience function for rapid analysis
8. **Find Key Values** - Extract maximum GZ, GM, vanishing angle, etc.

**Generated visualizations:**
- `analyzer_example2_curve.png` - Stability curve generation
- `analyzer_example4_cg_comparison.png` - CG position comparison
- `analyzer_example5_waterline_comparison.png` - Loading condition comparison
- `analyzer_example6_custom_ranges.png` - Custom angle range curves

### stability_criteria_examples.py

Demonstration of stability criteria checking and assessment for safety evaluation.

**Run the examples:**
```bash
python examples/stability_criteria_examples.py
```

**What it demonstrates:**
1. **Basic Criteria Check** - Check if kayak meets stability requirements
2. **Compare Configurations** - Assess multiple configurations against criteria
3. **Custom Criteria** - Use custom thresholds for different applications
4. **Detailed Check Analysis** - Detailed information for each criterion
5. **Strict vs Normal Mode** - Comparison of evaluation modes
6. **Quick Assessment** - Convenience function for rapid criteria checking
7. **Visual Criteria Report** - Comprehensive visual assessment report

**Generated visualizations:**
- `criteria_example2_comparison.png` - Configuration comparison
- `criteria_example7_report.png` - Comprehensive stability report

## Requirements

To run the examples, you need:
```bash
pip install numpy matplotlib scipy
```

Or install from requirements:
```bash
pip install -r requirements.txt
```

## Example Output

Each example prints progress information and saves visualization plots to this directory.

Example console output:
```
============================================================
Example 1: Transverse Interpolation
============================================================

Original profile has 5 points
Interpolated profile has 20 points

Plot saved to: examples/example_transverse_interpolation.png
```

## Adding Your Own Examples

To add a new example:

1. Create a new Python file in this directory
2. Import the necessary modules from `src.geometry`
3. Add docstrings explaining what your example demonstrates
4. Include visualization or output that shows the results
5. Update this README with your example information

Example template:
```python
"""
Example: [Your Example Name]

Description of what this example demonstrates.
"""

from src.geometry import Point3D, Profile, KayakHull

def main():
    # Your example code here
    pass

if __name__ == '__main__':
    main()
```

## Data Directory

The `data/` directory (in the parent folder) can be used to store:
- Sample kayak geometry files
- Test profiles in CSV or JSON format
- Reference data for validation

## Documentation

For detailed documentation on the interpolation functions, see:
- `docs/interpolation.md` - Complete interpolation function reference
- Module docstrings - In-code documentation

## Troubleshooting

**Import errors:**
Make sure you're running from the project root directory, or install the package in development mode:
```bash
pip install -e .
```

**matplotlib backend issues:**
If you get display errors, you can save plots without displaying:
```python
import matplotlib
matplotlib.use('Agg')
```

**Missing scipy:**
Cubic interpolation requires scipy. If not installed, the code will automatically fall back to linear interpolation.

## Future Examples

Planned examples to be added:
- Volume and displacement calculations
- Stability curve generation
- Waterline calculations at various heel angles
- Complete kayak analysis workflow
- Loading and saving hull geometry data
