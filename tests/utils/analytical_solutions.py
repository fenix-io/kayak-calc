"""
Analytical solutions for geometric shapes.

Provides functions to calculate exact analytical solutions for volume,
area, centroids, and other properties of simple geometric shapes.
These are used to validate numerical calculations.
"""

import numpy as np
from typing import Tuple


def box_volume(length: float, width: float, depth: float) -> float:
    """
    Calculate volume of a rectangular box.
    
    Parameters
    ----------
    length : float
        Length in x-direction
    width : float
        Width in y-direction
    depth : float
        Depth in z-direction
        
    Returns
    -------
    float
        Volume = length × width × depth
    """
    return length * width * depth


def box_centroid(
    length: float, 
    width: float, 
    depth: float,
    x_origin: float = 0.0,
    y_origin: float = 0.0,
    z_origin: float = 0.0
) -> Tuple[float, float, float]:
    """
    Calculate centroid of a rectangular box.
    
    Parameters
    ----------
    length, width, depth : float
        Box dimensions
    x_origin, y_origin, z_origin : float
        Origin coordinates (default: 0, 0, 0)
        
    Returns
    -------
    tuple of float
        (LCB, TCB, VCB) - centroid coordinates
        
    Notes
    -----
    For a box extending from origin to (length, width, -depth):
    - LCB = x_origin + length/2
    - TCB = y_origin (if symmetric about centerline)
    - VCB = z_origin - depth/2
    """
    lcb = x_origin + length / 2.0
    tcb = y_origin  # Centerline if symmetric
    vcb = z_origin - depth / 2.0
    
    return lcb, tcb, vcb


def cylinder_volume(radius: float, length: float, submerged_fraction: float = 1.0) -> float:
    """
    Calculate volume of a cylinder.
    
    Parameters
    ----------
    radius : float
        Radius of circular cross-section
    length : float
        Length of cylinder (axial direction)
    submerged_fraction : float
        Fraction of cross-section area that is submerged (0 to 1)
        Default 1.0 for fully submerged
        
    Returns
    -------
    float
        Volume = submerged_fraction × π × radius² × length
        
    Notes
    -----
    - For half-submerged cylinder: submerged_fraction = 0.5
    - For fully submerged: submerged_fraction = 1.0
    """
    return submerged_fraction * np.pi * radius**2 * length


def cylinder_centroid_vertical(
    radius: float,
    waterline_z: float = 0.0,
    center_z: float = None
) -> float:
    """
    Calculate vertical centroid (VCB) of submerged portion of horizontal cylinder.
    
    Parameters
    ----------
    radius : float
        Radius of cylinder
    waterline_z : float
        Z-coordinate of waterline (default 0)
    center_z : float
        Z-coordinate of cylinder center
        If None, assumes center at z = waterline_z - radius (half-submerged)
        
    Returns
    -------
    float
        Vertical position of centroid of submerged volume
        
    Notes
    -----
    For a half-submerged cylinder (waterline through center):
    VCB = center_z - (4*radius)/(3*π)
    """
    if center_z is None:
        center_z = waterline_z - radius
    
    # For half-submerged cylinder
    submergence = waterline_z - center_z
    
    if submergence >= radius:
        # Fully submerged
        return center_z
    elif submergence <= -radius:
        # Not submerged
        return float('nan')
    else:
        # Partially submerged - use circular segment formula
        # For half-submerged (submergence = radius):
        # vcb = center_z - (4*radius)/(3*π)
        
        # General formula for circular segment centroid:
        # Distance from center to centroid = (4*r*sin³(θ/2)) / (3*(θ - sin(θ)))
        # where θ is the angle of the segment
        
        h = radius + submergence  # Height of water above bottom of cylinder
        
        if abs(submergence) < 1e-10:  # Half-submerged
            return center_z - (4 * radius) / (3 * np.pi)
        else:
            # More complex formula for partial submergence
            # Simplified approximation for now
            angle = 2 * np.arccos((radius - h) / radius)
            segment_area = 0.5 * radius**2 * (angle - np.sin(angle))
            y_bar = (4 * radius * np.sin(angle/2)**3) / (3 * (angle - np.sin(angle)))
            
            # Centroid is measured from center, downward
            vcb = center_z - (radius - y_bar)
            return vcb


def cone_volume(base_radius: float, height: float, apex_radius: float = 0.0) -> float:
    """
    Calculate volume of a cone or truncated cone.
    
    Parameters
    ----------
    base_radius : float
        Radius at the base
    height : float
        Height/length of the cone
    apex_radius : float
        Radius at the apex (default 0 for true cone)
        
    Returns
    -------
    float
        Volume
        
    Notes
    -----
    - For true cone (apex_radius = 0):
      V = (1/3) × π × base_radius² × height
    - For truncated cone (frustum):
      V = (π × height / 3) × (R₁² + R₁×R₂ + R₂²)
      where R₁ = base_radius, R₂ = apex_radius
    """
    if apex_radius == 0:
        # True cone
        return (1.0 / 3.0) * np.pi * base_radius**2 * height
    else:
        # Truncated cone (frustum)
        r1 = base_radius
        r2 = apex_radius
        return (np.pi * height / 3.0) * (r1**2 + r1*r2 + r2**2)


def cone_centroid_longitudinal(
    base_radius: float,
    height: float,
    apex_radius: float = 0.0,
    base_x: float = 0.0
) -> float:
    """
    Calculate longitudinal centroid (LCB) of a cone or frustum.
    
    Parameters
    ----------
    base_radius : float
        Radius at the base
    height : float
        Height/length of the cone
    apex_radius : float
        Radius at the apex (default 0 for true cone)
    base_x : float
        X-coordinate of the base (default 0)
        
    Returns
    -------
    float
        Longitudinal position of centroid
        
    Notes
    -----
    - For true cone: LCB = base_x + (3/4) × height
    - For truncated cone:
      LCB = base_x + (height/4) × (R₁² + 2×R₁×R₂ + 3×R₂²) / (R₁² + R₁×R₂ + R₂²)
    """
    if apex_radius == 0:
        # True cone - centroid at 3/4 of height from base
        return base_x + (3.0 / 4.0) * height
    else:
        # Truncated cone
        r1 = base_radius
        r2 = apex_radius
        numerator = r1**2 + 2*r1*r2 + 3*r2**2
        denominator = r1**2 + r1*r2 + r2**2
        return base_x + (height / 4.0) * (numerator / denominator)


def wedge_volume(length: float, width: float, depth: float) -> float:
    """
    Calculate volume of a wedge with triangular cross-section.
    
    Parameters
    ----------
    length : float
        Length of the wedge
    width : float
        Width at the waterline
    depth : float
        Depth from waterline to keel
        
    Returns
    -------
    float
        Volume = (1/2) × length × width × depth
        
    Notes
    -----
    Assumes triangular cross-section with base = width and height = depth.
    """
    return 0.5 * length * width * depth


def circular_area(radius: float) -> float:
    """
    Calculate area of a circle.
    
    Parameters
    ----------
    radius : float
        Radius of the circle
        
    Returns
    -------
    float
        Area = π × radius²
    """
    return np.pi * radius**2


def circular_segment_area(radius: float, height: float) -> float:
    """
    Calculate area of a circular segment.
    
    Parameters
    ----------
    radius : float
        Radius of the circle
    height : float
        Height of the segment (distance from chord to arc)
        
    Returns
    -------
    float
        Area of the circular segment
        
    Notes
    -----
    For a horizontal waterline cutting through a circle:
    - height is the depth of water
    - Area = r² × arccos((r-h)/r) - (r-h) × sqrt(2×r×h - h²)
    """
    r = radius
    h = height
    
    if h <= 0:
        return 0.0
    elif h >= 2 * r:
        return circular_area(r)
    else:
        angle = np.arccos((r - h) / r)
        area = r**2 * angle - (r - h) * np.sqrt(2*r*h - h**2)
        return area


def elliptical_area(semi_major: float, semi_minor: float) -> float:
    """
    Calculate area of an ellipse.
    
    Parameters
    ----------
    semi_major : float
        Semi-major axis length
    semi_minor : float
        Semi-minor axis length
        
    Returns
    -------
    float
        Area = π × semi_major × semi_minor
    """
    return np.pi * semi_major * semi_minor


def rectangular_area(width: float, height: float) -> float:
    """
    Calculate area of a rectangle.
    
    Parameters
    ----------
    width : float
        Width of the rectangle
    height : float
        Height of the rectangle
        
    Returns
    -------
    float
        Area = width × height
    """
    return width * height


def triangular_area(base: float, height: float) -> float:
    """
    Calculate area of a triangle.
    
    Parameters
    ----------
    base : float
        Base of the triangle
    height : float
        Height of the triangle
        
    Returns
    -------
    float
        Area = (1/2) × base × height
    """
    return 0.5 * base * height


def triangular_centroid_vertical(base: float, height: float, apex_z: float) -> float:
    """
    Calculate vertical centroid of a triangle.
    
    Parameters
    ----------
    base : float
        Base width of the triangle
    height : float
        Height of the triangle
    apex_z : float
        Z-coordinate of the apex (bottom point)
        
    Returns
    -------
    float
        Vertical position of centroid
        
    Notes
    -----
    For a triangle with apex at bottom:
    Centroid is at 1/3 of height from base
    VCG = apex_z + height/3
    """
    return apex_z + height / 3.0
