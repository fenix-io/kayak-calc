"""
Hydrostatics module for volume and buoyancy calculations.

This module contains functions for:
- Volume integration and displacement calculation
- Cross-sectional area calculations
- Center of buoyancy (CB) calculation
- Waterline intersection calculation
- Hydrostatic properties
"""

# Cross-section properties (Phase 4, Task 4.1)
from .cross_section import (
    CrossSectionProperties,
    calculate_section_properties,
    calculate_properties_at_heel_angles,
    calculate_first_moment_of_area,
    validate_cross_section_properties,
    compare_properties
)

# Volume integration and displacement (Phase 4, Task 4.2)
from .volume import (
    DisplacementProperties,
    integrate_simpson,
    integrate_trapezoidal,
    calculate_volume,
    calculate_displacement,
    calculate_displacement_curve,
    calculate_volume_components,
    validate_displacement_properties
)

__all__ = [
    # Cross-section properties
    'CrossSectionProperties',
    'calculate_section_properties',
    'calculate_properties_at_heel_angles',
    'calculate_first_moment_of_area',
    'validate_cross_section_properties',
    'compare_properties',
    # Volume and displacement
    'DisplacementProperties',
    'integrate_simpson',
    'integrate_trapezoidal',
    'calculate_volume',
    'calculate_displacement',
    'calculate_displacement_curve',
    'calculate_volume_components',
    'validate_displacement_properties',
]

# Future imports:
# from .buoyancy import calculate_center_of_buoyancy
# from .properties import HydrostaticProperties
