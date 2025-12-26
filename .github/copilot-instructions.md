# GitHub Copilot Instructions

## Project Overview
This is a Python application for calculating kayak hydrostatic parameters and stability characteristics.

## Core Functionality
The application calculates:
- **Displacement**: Volume of water displaced by the kayak
- **Stability Curves**: GZ curves showing righting moment vs. heel angle
- **Center of Gravity (CG)**: Vertical and horizontal position of the mass centroid
- **Center of Buoyancy (CB)**: Centroid of the displaced volume, both upright and heeled

## Input Data Structure
- Surface points on the kayak hull defined at:
  - Bow profile
  - Stern profile
  - Intermediate transverse profiles at configurable longitudinal positions
- All coordinates referenced to an arbitrary origin on the **centerline plane** (vertical plane through longitudinal axis)
- Coordinate system: origin on centerline, typically at midship or other reference point

## Calculation Methodology

### Volume Integration
- Numerical integration of transverse cross-sections along the kayak length
- Cross-section areas calculated from profile points
- Integration methods: Simpson's rule, trapezoidal rule, or similar numerical methods

### Point Interpolation
- **Transverse interpolation**: Linear interpolation between port and starboard points on each profile
- **Longitudinal interpolation**: Linear interpolation between adjacent profiles to generate intermediate sections
- **Bow/stern interpolation**: Linear interpolation from end profiles to bow/stern points

### Heel Calculations
- Transform coordinates to simulate heel angle (roll about longitudinal axis)
- Recalculate waterline intersection at heeled positions
- Compute submerged volume and center of buoyancy for each heel angle
- Generate stability curve by calculating righting arm (GZ) vs. heel angle

## Technical Considerations
- Use NumPy for numerical operations and array manipulations
- Consider using SciPy for integration routines
- Matplotlib for plotting stability curves
- Maintain symmetry assumptions (kayak symmetric about centerline)
- Handle waterline intersection calculations carefully when heeled

## Code Organization Preferences
- Separate modules for:
  - Geometry definitions and transformations
  - Volume and centroid calculations
  - Stability analysis
  - Visualization/plotting
  - Input/output handling
- Use type hints for better code clarity
- Document formulas and calculation steps clearly
- Please write Unit Tests for new code where is applicacble
- Please run the linter (flake8) and formatter (black) on the code before submission using make lint and make format commands.


# Planning and Tasks
- For every task, please create a detailed paln before impelementation.
- Break down complex calculations into smaller, manageable functions.
- Write all task to be implemented in a tasks.md file and get approval before starting coding.
