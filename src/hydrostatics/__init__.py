"""
Hydrostatics module for volume and buoyancy calculations.

This module contains functions for:
- Volume integration and displacement calculation
- Cross-sectional area calculations
- Center of buoyancy (CB) calculation
- Center of gravity (CG) calculation
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
    compare_properties,
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
    validate_displacement_properties,
    # Center of buoyancy (Phase 4, Task 4.3)
    CenterOfBuoyancy,
    calculate_center_of_buoyancy,
    calculate_cb_curve,
    calculate_cb_at_heel_angles,
    validate_center_of_buoyancy,
)

# Center of gravity (Phase 4, Task 4.4)
from .center_of_gravity import (
    MassComponent,
    CenterOfGravity,
    calculate_cg_from_components,
    create_cg_manual,
    validate_center_of_gravity,
    adjust_cg_for_loading,
    calculate_mass_summary,
)

__all__ = [
    # Cross-section properties
    "CrossSectionProperties",
    "calculate_section_properties",
    "calculate_properties_at_heel_angles",
    "calculate_first_moment_of_area",
    "validate_cross_section_properties",
    "compare_properties",
    # Volume and displacement
    "DisplacementProperties",
    "integrate_simpson",
    "integrate_trapezoidal",
    "calculate_volume",
    "calculate_displacement",
    "calculate_displacement_curve",
    "calculate_volume_components",
    "validate_displacement_properties",
    # Center of buoyancy
    "CenterOfBuoyancy",
    "calculate_center_of_buoyancy",
    "calculate_cb_curve",
    "calculate_cb_at_heel_angles",
    "validate_center_of_buoyancy",
    # Center of gravity
    "MassComponent",
    "CenterOfGravity",
    "calculate_cg_from_components",
    "create_cg_manual",
    "validate_center_of_gravity",
    "adjust_cg_for_loading",
    "calculate_mass_summary",
]

# Future imports:
# from .buoyancy import calculate_center_of_buoyancy
# from .properties import HydrostaticProperties
