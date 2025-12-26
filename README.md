# Kayak Calculation Tool (kyk-calc)

**Professional hydrostatic and stability analysis for kayak hulls**

A Python application for calculating displacement, centers of buoyancy/gravity, and stability characteristics of kayak hulls using numerical naval architecture methods.

---

## 🚀 Quick Start

```bash
# Install
git clone <repository-url>
cd kyk-calc
pip install -e .

# Run first example
python examples/stability_analyzer_examples.py
```

**5-Minute Example:**

```python
from src.io import load_hull_from_json
from src.hydrostatics import CenterOfGravity
from src.stability import StabilityAnalyzer
from src.visualization import plot_stability_curve

# Load sample kayak hull
hull = load_hull_from_json('data/sample_hull_kayak.json')

# Define center of gravity (paddler + hull)
cg = CenterOfGravity(x=2.5, y=0.0, z=-0.3, mass=100.0)

# Analyze stability
analyzer = StabilityAnalyzer(hull, cg)
results = analyzer.calculate_stability_curve(waterline_z=-0.1)

# View results
print(f"Initial GM: {results.initial_gm:.3f} m")
print(f"Max GZ: {results.max_gz:.3f} m at {results.max_gz_angle:.0f}°")
plot_stability_curve(results, show=True)
```

---

## ✨ Features

### Hydrostatic Calculations
- **Displacement** - Volume and mass of water displaced
- **Center of Buoyancy (CB)** - 3D centroid of submerged volume
- **Center of Gravity (CG)** - Mass centroid from components or direct specification
- **Cross-Section Properties** - Area and centroid of individual profiles

### Stability Analysis
- **GZ Curves** - Righting arm vs. heel angle (0-90°)
- **Metacentric Height (GM)** - Initial stability metric
- **Vanishing Angle** - Ultimate stability limit
- **Dynamic Stability** - Area under GZ curve
- **Multi-Configuration Comparison** - Compare different loading conditions

### Visualization
- **3D Hull Plots** - Interactive hull geometry with waterline
- **Profile Plots** - Cross-sections with submerged area highlighted  
- **Stability Curves** - Professional GZ plots with key metrics annotated
- **Interactive Tools** - Real-time heel angle and CG adjustment
- **Animation** - Heel sequence animations (MP4/GIF export)

### Data I/O
- **Input Formats** - JSON (recommended) and CSV support
- **Output Formats** - CSV data export, Markdown reports, publication-quality plots
- **Validation** - Comprehensive input data validation and error reporting

---

## 📖 Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - Complete tutorial from installation to advanced usage
- **[QUICKREF.md](QUICKREF.md)** - Fast reference for experienced users
- **[API Documentation](docs/_build/html/index.html)** - Complete API reference (100% coverage)
- **[INPUT_DATA_FORMATS.md](INPUT_DATA_FORMATS.md)** - Hull geometry file format specifications
- **[OUTPUT_DATA_FORMATS.md](OUTPUT_DATA_FORMATS.md)** - Export format documentation
- **[Examples](examples/)** - 14 example scripts covering all features

---

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Standard Installation

```bash
# Clone repository
git clone <repository-url>
cd kyk-calc

# Install in development mode (recommended)
pip install -e .
```

This installs the package and all dependencies (NumPy, SciPy, Matplotlib).

### Virtual Environment (Recommended)

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install
pip install -e .
```

### Verify Installation

```bash
python -c "from src.io import load_hull_from_json; print('✓ Installation successful')"
```

---

## 📊 Usage Examples

### Calculate Displacement

```python
from src.io import load_hull_from_json
from src.hydrostatics import calculate_volume

hull = load_hull_from_json('data/sample_hull_kayak.json')
volume, cb = calculate_volume(hull, waterline_z=-0.1)
displacement_kg = volume * 1025  # seawater density

print(f"Volume: {volume:.4f} m³")
print(f"Displacement: {displacement_kg:.1f} kg")
print(f"Center of Buoyancy: ({cb.x:.2f}, {cb.y:.2f}, {cb.z:.2f})")
```

### Complete Stability Analysis

```python
from src.io import load_hull_from_json, generate_stability_report
from src.hydrostatics import CenterOfGravity
from src.stability import StabilityAnalyzer
from src.visualization import plot_stability_curve

# 1. Load hull geometry
hull = load_hull_from_json('data/sample_hull_kayak.json')

# 2. Define center of gravity
cg = CenterOfGravity.from_components([
    {'mass': 20.0, 'x': 2.0, 'y': 0.0, 'z': -0.15, 'name': 'hull'},
    {'mass': 80.0, 'x': 2.5, 'y': 0.0, 'z': -0.35, 'name': 'paddler'},
])

# 3. Analyze stability
analyzer = StabilityAnalyzer(hull, cg)
results = analyzer.calculate_stability_curve(
    waterline_z=-0.1,
    heel_angles=range(0, 91, 5)
)

# 4. View key metrics
print(f"Initial GM: {results.initial_gm:.3f} m")
print(f"Maximum GZ: {results.max_gz:.3f} m at {results.max_gz_angle:.0f}°")
print(f"Vanishing angle: {results.vanishing_angle:.0f}°")

# 5. Generate plots and report
plot_stability_curve(results, save_path='stability.png', show=True)
generate_stability_report(hull, cg, results, 'report.md')
```

### Interactive Exploration

```python
from src.visualization import interactive_heel_explorer, interactive_cg_adjustment

# Explore heel behavior with real-time slider
interactive_heel_explorer(hull, cg, waterline_z=-0.1)

# Adjust CG position and see stability effects
interactive_cg_adjustment(hull, initial_cg=cg, waterline_z=-0.1)
```

### Compare Design Variations

```python
from src.stability import StabilityAnalyzer
from src.hydrostatics import CenterOfGravity
from src.visualization import plot_stability_comparison

# Analyze multiple CG heights
cg_high = CenterOfGravity(x=2.5, y=0.0, z=-0.25, mass=100.0)
cg_low = CenterOfGravity(x=2.5, y=0.0, z=-0.35, mass=100.0)

results_high = StabilityAnalyzer(hull, cg_high).calculate_stability_curve(waterline_z=-0.1)
results_low = StabilityAnalyzer(hull, cg_low).calculate_stability_curve(waterline_z=-0.1)

# Compare side-by-side
plot_stability_comparison(
    [results_high, results_low],
    labels=['High CG', 'Low CG'],
    save_path='comparison.png'
)
```

---

## 🏗️ Methodology

### Coordinate System

Right-handed 3D coordinates:
- **X**: Longitudinal (forward positive)
- **Y**: Transverse (starboard positive, port negative)
- **Z**: Vertical (up positive, down negative)
- **Origin**: On centerline, typically at midship

### Calculation Approach

1. **Volume Integration**: Simpson's rule numerical integration of cross-sections
2. **Point Interpolation**: Linear interpolation between profiles and points
3. **Heel Transformation**: Rotation matrices for heel angle simulation  
4. **Stability Curves**: Iterative GZ calculation at discrete heel angles

### Input Requirements

Hull geometry defined by:
- **Profiles**: Transverse cross-sections at longitudinal stations (5-10 recommended)
- **Points**: 5-10 points per profile defining the hull shape
- **Bow/Stern**: Apex points where hull tapers to a point

Formats: JSON (preferred) or CSV

---

## 🎯 Project Status

**Phase 9: Documentation and Examples** ✅ **COMPLETE**

All core features implemented and documented:
- ✅ Hull geometry and interpolation
- ✅ Hydrostatic calculations (volume, CB, CG)
- ✅ Stability analysis (GZ curves, metrics, criteria)
- ✅ Visualization (plots, interactive tools, animations)
- ✅ Data I/O (JSON/CSV input, CSV/report export)
- ✅ Testing (564 tests passing)
- ✅ Documentation (100% docstring coverage, Sphinx docs, user guides)
- ✅ Examples (14 comprehensive example scripts)

---

## 📁 Project Structure

```
kyk-calc/
├── src/                    # Main package
│   ├── geometry/          # Hull, profiles, interpolation, transformations
│   ├── hydrostatics/      # Volume, buoyancy, center of gravity
│   ├── stability/         # Stability analysis and criteria
│   ├── visualization/     # Plotting and interactive tools
│   └── io/                # Data loading and exporting
├── tests/                 # 564 unit and integration tests
├── examples/              # 14 example scripts
├── data/                  # Sample hull geometry files
├── docs/                  # Sphinx documentation
│   └── _build/html/       # Built HTML documentation
├── USER_GUIDE.md          # Complete usage tutorial
├── QUICKREF.md            # Quick reference for experienced users
├── INPUT_DATA_FORMATS.md  # File format specifications
├── OUTPUT_DATA_FORMATS.md # Export format specifications
└── README.md              # This file
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_analyzer.py
```

**Test Coverage:** 564 tests passing
- 515 unit tests
- 29 integration tests  
- 20 validation tests

---

## 📚 Learning Resources

### For Beginners
1. Read [USER_GUIDE.md](USER_GUIDE.md) - Start here!
2. Run examples in order:
   - `examples/data_input_examples.py`
   - `examples/volume_examples.py`
   - `examples/stability_analyzer_examples.py`
3. View [docs/getting_started.rst](docs/getting_started.rst)

### For Experienced Users
1. See [QUICKREF.md](QUICKREF.md) for quick reference
2. Browse [API documentation](docs/_build/html/index.html)
3. Check [examples/README.md](examples/README.md) for example descriptions

### Understanding the Theory
1. Read [docs/theory.rst](docs/theory.rst) for mathematical background
2. See [docs/interpolation.md](docs/interpolation.md) for interpolation methods
3. Check [docs/transformations.md](docs/transformations.md) for coordinate systems

---

## 🤝 Contributing

Contributions welcome! Areas for contribution:
- Additional hull validation cases
- Performance optimizations
- New visualization features
- Documentation improvements
- Bug reports and fixes

Please feel free to submit issues or pull requests.

---

## 📄 License

[To be determined]

---

## 🙏 Acknowledgments

Built using:
- **NumPy** - Numerical operations
- **SciPy** - Numerical integration
- **Matplotlib** - Visualization and interactive tools
- **Sphinx** - Documentation generation

---

## 📧 Support

- **Documentation Issues**: Check [USER_GUIDE.md](USER_GUIDE.md) troubleshooting section
- **Bug Reports**: Submit GitHub issue with example code
- **Feature Requests**: Open GitHub issue with use case
- **Questions**: Review [examples/](examples/) and [docs/](docs/) first

---

**Happy Calculating!** 🛶
