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
