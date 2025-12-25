"""
Geometry module for kayak hull definition and transformations.

This module contains classes and functions for:
- 3D point representation
- Profile definition and manipulation
- Hull geometry definition
- Coordinate transformations (heel, trim)
- Interpolation functions
"""

from .point import Point3D
from .profile import Profile
from .hull import KayakHull
from .interpolation import (
    interpolate_transverse,
    interpolate_profile_transverse,
    interpolate_longitudinal,
    interpolate_multiple_profiles,
    interpolate_to_apex,
    create_symmetric_profile,
    resample_profile_uniform_y,
    resample_profile_uniform_arc
)
from .transformations import (
    apply_heel,
    apply_heel_to_profile,
    apply_heel_to_hull,
    apply_trim,
    apply_trim_to_profile,
    apply_trim_to_hull,
    apply_heel_and_trim,
    apply_heel_and_trim_to_hull,
    Waterline,
    find_waterline_intersection_segment,
    find_profile_waterline_intersection,
    get_submerged_points,
    calculate_submerged_area,
    calculate_waterplane_area,
    get_heel_angle_for_waterline,
    transform_to_body_coordinates,
    transform_to_earth_coordinates
)

__all__ = [
    'Point3D',
    'Profile',
    'KayakHull',
    'interpolate_transverse',
    'interpolate_profile_transverse',
    'interpolate_longitudinal',
    'interpolate_multiple_profiles',
    'interpolate_to_apex',
    'create_symmetric_profile',
    'resample_profile_uniform_y',
    'resample_profile_uniform_arc',
    'apply_heel',
    'apply_heel_to_profile',
    'apply_heel_to_hull',
    'apply_trim',
    'apply_trim_to_profile',
    'apply_trim_to_hull',
    'apply_heel_and_trim',
    'apply_heel_and_trim_to_hull',
    'Waterline',
    'find_waterline_intersection_segment',
    'find_profile_waterline_intersection',
    'get_submerged_points',
    'calculate_submerged_area',
    'calculate_waterplane_area',
    'get_heel_angle_for_waterline',
    'transform_to_body_coordinates',
    'transform_to_earth_coordinates'
]
