# Kayak Calculation Tool (kyk-calc)

A Python application for calculating hydrostatic parameters and stability characteristics of kayaks.

## Overview

This tool calculates essential hydrodynamic properties of kayak hulls, including displacement, centers of gravity and buoyancy, and stability curves. It's designed for kayak designers and builders who need to analyze hull performance and stability characteristics.

## Features

- **Displacement Calculation**: Compute the volume of water displaced by the hull
- **Center of Gravity (CG)**: Calculate the position of the mass centroid
- **Center of Buoyancy (CB)**: Determine the centroid of displaced volume
- **Stability Analysis**: Generate stability curves (GZ curves) showing righting moment versus heel angle
- **Heel Simulation**: Calculate hull behavior at various angles of inclination

## Methodology

### Input Data

The application accepts surface point data defining the kayak hull:

- **Bow profile**: Points defining the forward-most cross-section
- **Stern profile**: Points defining the aft-most cross-section
- **Transverse profiles**: Cross-sectional profiles at configurable longitudinal stations

All coordinates are referenced to an arbitrary origin located on the **centerline plane** (the vertical plane cutting longitudinally through the hull center).

### Calculation Approach

1. **Volume Integration**: Uses numerical integration of transverse cross-sections along the kayak's length
2. **Point Interpolation**: 
   - Linear interpolation between defined profiles to generate intermediate cross-sections
   - Interpolation between bow/stern profile lines to complete the hull definition
3. **Heel Analysis**: Transforms coordinates to simulate heel angles and recalculate buoyancy properties
4. **Stability Curves**: Plots the righting arm (GZ) against heel angle to visualize stability characteristics

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd kyk-calc

# Install dependencies
pip install -r requirements.txt
```

## Usage

```python
# Example usage (to be implemented)
import kayak

# Define hull geometry
hull = kayak.KayakHull()
hull.add_profile(station=0, points=bow_points)
hull.add_profile(station=150, points=mid_points)
hull.add_profile(station=300, points=stern_points)

# Calculate properties
displacement = hull.calculate_displacement(waterline=25)
cb = hull.calculate_center_of_buoyancy(waterline=25)

# Generate stability curve
analyzer = kayak.StabilityAnalyzer(hull, cg_height=30)
stability_curve = analyzer.generate_gz_curve(heel_angles=range(0, 91, 5))
analyzer.plot_stability_curve()
```

## Technical Requirements

- Python 3.8+
- NumPy (numerical operations)
- SciPy (numerical integration)
- Matplotlib (visualization)

## Project Status

🚧 **Under Development** 🚧

This project is in active development. Features and API may change.

## License

[To be determined]

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Contact

[Project maintainer information]
