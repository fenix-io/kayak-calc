# Examples Directory

This directory contains example scripts demonstrating the use of the kayak calculation library.

## Available Examples

### Workflow Examples (Complete End-to-End Demonstrations)

#### basic_displacement_workflow.py

Complete workflow for basic displacement calculation - perfect for beginners.

**Run the example:**
```bash
python examples/basic_displacement_workflow.py
```

**What it demonstrates:**
1. **Load Hull Geometry** - Load kayak data from JSON file
2. **Define Waterline** - Set water surface level
3. **Calculate Displacement** - Volume and mass calculations
4. **Calculate Center of Buoyancy** - LCB, VCB, TCB coordinates
5. **Visualize Results** - 3D hull and cross-sections
6. **Export Data** - Save results to CSV
7. **Generate Report** - Create markdown summary

**Generated outputs:**
- `basic_displacement_hull.png` - 3D hull visualization
- `basic_displacement_sections.png` - Cross-section plots
- `basic_displacement_volume.csv` - Data export
- `basic_displacement_report.md` - Summary report

**Use this when:** You need to calculate basic displacement and buoyancy for a kayak.

---

#### quick_assessment_script.py

Template for rapid initial stability assessment - minimal setup, fast results.

**Run the example:**
```bash
python examples/quick_assessment_script.py
```

**What it demonstrates:**
1. **Quick Setup** - Minimal configuration required
2. **Fast Analysis** - Using high-level convenience functions
3. **Stability Metrics** - GM, max GZ, vanishing angle
4. **Criteria Check** - Pass/fail assessment
5. **Interpretation** - Automatic assessment of results
6. **Recommendations** - Suggested improvements

**Generated outputs:**
- Console summary with all key metrics
- Pass/fail criteria assessment
- Design recommendations

**Use this when:** You need a quick stability check during design iterations.

---

#### complete_stability_analysis.py

Professional-level complete stability analysis with comprehensive reporting.

**Run the example:**
```bash
python examples/complete_stability_analysis.py
```

**What it demonstrates:**
1. **Multi-Component CG** - Define CG from hull, paddler, gear
2. **Hydrostatic Properties** - Displacement, CB, mass balance
3. **Stability Analysis** - Full GZ curve generation
4. **Stability Metrics** - GM, max GZ, vanishing angle, dynamic stability
5. **Criteria Assessment** - Comprehensive safety evaluation
6. **Complete Visualizations** - Hull, profiles, curves, reports
7. **Data Export** - CSV files for all results
8. **Professional Report** - Complete markdown documentation

**Generated outputs:**
- `complete_analysis_hull_3d.png` - Hull with CG and CB
- `complete_analysis_profiles.png` - Cross-sections
- `complete_analysis_stability_curve.png` - GZ curve
- `complete_analysis_criteria_report.png` - Criteria assessment
- `complete_analysis_curve_data.csv` - Stability data
- `complete_analysis_metrics.csv` - Metrics summary
- `complete_analysis_report.md` - Complete report

**Use this when:** You need a full professional analysis for design validation or documentation.

---

#### parametric_study_workflow.py

Systematic comparison of multiple configurations for design exploration.

**Run the example:**
```bash
python examples/parametric_study_workflow.py
```

**What it demonstrates:**
1. **Configuration Matrix** - Define multiple scenarios to compare
2. **CG Variations** - Compare different loading conditions
3. **Waterline Variations** - Compare displacement levels
4. **Systematic Analysis** - Automated calculation across parameter space
5. **Comparison Visualizations** - Side-by-side curve plots
6. **Comparison Tables** - Tabular data for all configurations
7. **Best Configuration** - Identify optimal design
8. **Study Report** - Comprehensive comparison documentation

**Generated outputs:**
- `parametric_cg_comparison.png` - CG configuration comparison
- `parametric_waterline_comparison.png` - Waterline level comparison
- `parametric_comparison_table.csv` - Comparison data
- `parametric_study_report.md` - Study summary

**Use this when:** You need to compare multiple design options or loading scenarios.

---

#### advanced_visualization_workflow.py

Complete showcase of all visualization capabilities.

**Run the example:**
```bash
python examples/advanced_visualization_workflow.py

# Skip interactive plots (for automated testing):
python examples/advanced_visualization_workflow.py --skip-interactive
```

**What it demonstrates:**
1. **Static Plots** - Publication-quality visualizations
2. **3D Hull Views** - Multiple perspectives
3. **Multi-Curve Comparisons** - Side-by-side stability curves
4. **Interactive Heel Explorer** - Real-time angle adjustment
5. **Interactive Stability Curve** - Clickable exploration
6. **Interactive CG Adjustment** - Dynamic CG positioning
7. **Interactive Waterline Explorer** - Displacement variation
8. **Animations** - Heel sequence with playback
9. **Multi-Format Export** - PNG, PDF, MP4, GIF

**Generated outputs:**
- `viz_hull_3d.png` - 3D hull visualization
- `viz_profiles.png` - Cross-section profiles
- `viz_stability_curve.png` - Stability curve
- `viz_multi_curve_comparison.png` - Multiple configurations
- `viz_heel_sequence.mp4` - Animation (requires ffmpeg)

**Use this when:** You need advanced visualizations for presentations, teaching, or publications.

---

### Component Examples (Individual Feature Demonstrations)

#### interpolation_examples.py

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

---

#### righting_arm_examples.py

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

---

#### stability_analyzer_examples.py

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

---

#### stability_criteria_examples.py

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

---

### Additional Component Examples

The following scripts demonstrate specific components and features:

- **transformation_examples.py** - Heel and trim transformations
- **volume_examples.py** - Displacement volume calculations
- **center_of_buoyancy_examples.py** - CB calculation demonstrations
- **center_of_gravity_examples.py** - CG definition and manipulation
- **cross_section_examples.py** - Cross-section property calculations
- **data_input_examples.py** - Loading hull data from JSON/CSV
- **data_output_examples.py** - Exporting results and generating reports
- **profile_plotting_examples.py** - Profile and hull plotting
- **stability_curve_plotting_examples.py** - Stability visualization
- **interactive_visualization_examples.py** - Interactive plots and animations

---

## Quick Start Guide

### For Beginners

1. **Start here:** `basic_displacement_workflow.py`
   - Simplest complete workflow
   - Learn the basic concepts
   - Understand input/output

2. **Next:** `quick_assessment_script.py`
   - Fast stability checks
   - Use as a template for your own scripts

3. **Then:** `complete_stability_analysis.py`
   - Full professional analysis
   - All features demonstrated

### For Advanced Users

1. **Design exploration:** `parametric_study_workflow.py`
   - Compare multiple configurations
   - Optimize your design

2. **Visualization:** `advanced_visualization_workflow.py`
   - Interactive tools
   - Animations
   - Publication-quality plots

3. **Component examples:** Browse individual feature demonstrations

---

## Example Progression

```
Level 1: Basic Concepts
└── basic_displacement_workflow.py
    └── Learn: Loading data, calculating displacement, basic viz

Level 2: Stability Analysis
├── quick_assessment_script.py
│   └── Learn: Fast checks, convenience functions
└── complete_stability_analysis.py
    └── Learn: Full analysis, reporting, criteria

Level 3: Advanced Workflows
├── parametric_study_workflow.py
│   └── Learn: Configuration comparison, optimization
└── advanced_visualization_workflow.py
    └── Learn: Interactive tools, animations

Level 4: Specialized Features
└── Component examples (interpolation, CG, etc.)
    └── Learn: Specific features in depth
```

---

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

The workflow examples provide comprehensive coverage of the library's capabilities. Additional specialized examples may be added based on user feedback.
