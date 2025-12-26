"""
Geometric shape generators for testing.

Provides functions to create simple geometric hulls with known properties
for validation of volume, buoyancy, and stability calculations.
"""

import numpy as np
from src.geometry import Point3D, Profile, KayakHull


def create_box_hull(
    length: float, 
    width: float, 
    depth: float, 
    num_stations: int = 5
) -> KayakHull:
    """
    Create a rectangular box hull for testing.
    
    Parameters
    ----------
    length : float
        Length of the box (x-direction)
    width : float
        Width of the box (y-direction)
    depth : float
        Depth of the box (z-direction, positive downward from waterline)
    num_stations : int
        Number of transverse stations along the length
        
    Returns
    -------
    KayakHull
        Hull with rectangular box geometry
        
    Notes
    -----
    - Origin is at (0, 0, 0) - typically at midship, centerline, waterline
    - Hull extends from x=0 to x=length
    - Width extends from y=-width/2 to y=+width/2
    - Depth extends from z=0 to z=-depth
    - Analytical volume = length × width × depth (when fully submerged)
    """
    hull = KayakHull()
    stations = np.linspace(0, length, num_stations)
    half_width = width / 2.0
    
    for station in stations:
        points = [
            Point3D(station, -half_width, 0.0),      # Port waterline
            Point3D(station, -half_width, -depth),   # Port bottom
            Point3D(station, half_width, -depth),    # Starboard bottom
            Point3D(station, half_width, 0.0),       # Starboard waterline
        ]
        hull.add_profile_from_points(station, points)
    
    return hull


def create_cylindrical_hull(
    length: float,
    radius: float,
    num_stations: int = 11,
    num_points_per_profile: int = 21
) -> KayakHull:
    """
    Create a cylindrical hull with circular cross-sections.
    
    Parameters
    ----------
    length : float
        Length of the cylinder (x-direction)
    radius : float
        Radius of the circular cross-section
    num_stations : int
        Number of transverse stations along the length
    num_points_per_profile : int
        Number of points defining each circular profile
        
    Returns
    -------
    KayakHull
        Hull with cylindrical geometry
        
    Notes
    -----
    - Cylinder axis is along x-axis
    - Center is at (x, 0, -radius) for each station
    - Circular profiles in y-z plane
    - When waterline at z=0 and cylinder half-submerged:
      Analytical volume = (1/2) × π × radius² × length
    - When fully submerged to depth >= 2×radius:
      Analytical volume = π × radius² × length
    """
    hull = KayakHull()
    stations = np.linspace(0, length, num_stations)
    
    for station in stations:
        profile = create_circular_profile(
            center_x=station,
            center_y=0.0,
            center_z=-radius,
            radius=radius,
            num_points=num_points_per_profile
        )
        hull.add_profile_from_points(station, profile.points)
    
    return hull


def create_conical_hull(
    length: float,
    base_radius: float,
    apex_radius: float = 0.0,
    num_stations: int = 11,
    num_points_per_profile: int = 21
) -> KayakHull:
    """
    Create a conical or tapered hull with circular cross-sections.
    
    Parameters
    ----------
    length : float
        Length of the cone (x-direction)
    base_radius : float
        Radius at the base (x=0)
    apex_radius : float
        Radius at the apex (x=length). Default 0.0 for true cone
    num_stations : int
        Number of transverse stations along the length
    num_points_per_profile : int
        Number of points defining each circular profile
        
    Returns
    -------
    KayakHull
        Hull with conical/tapered geometry
        
    Notes
    -----
    - Cone axis is along x-axis
    - Base at x=0 with radius = base_radius
    - Apex at x=length with radius = apex_radius
    - Linear taper between base and apex
    - For true cone (apex_radius=0) fully submerged to depth >= 2×base_radius:
      Analytical volume = (1/3) × π × base_radius² × length
    - For truncated cone:
      Analytical volume = (π × length / 3) × (R₁² + R₁×R₂ + R₂²)
      where R₁=base_radius, R₂=apex_radius
    """
    hull = KayakHull()
    stations = np.linspace(0, length, num_stations)
    
    for station in stations:
        # Linear interpolation of radius along length
        t = station / length if length > 0 else 0
        radius = base_radius * (1 - t) + apex_radius * t
        
        if radius > 0:
            profile = create_circular_profile(
                center_x=station,
                center_y=0.0,
                center_z=-radius,
                radius=radius,
                num_points=num_points_per_profile
            )
            hull.add_profile_from_points(station, profile.points)
        else:
            # At apex with zero radius, add single point
            hull.add_profile_from_points(
                station, 
                [Point3D(station, 0.0, 0.0)]
            )
    
    return hull


def create_wedge_hull(
    length: float, 
    width: float, 
    depth: float, 
    num_stations: int = 5
) -> KayakHull:
    """
    Create a wedge-shaped hull with triangular cross-section.
    
    Parameters
    ----------
    length : float
        Length of the wedge (x-direction)
    width : float
        Width at the waterline (y-direction)
    depth : float
        Depth from waterline to keel (z-direction)
    num_stations : int
        Number of transverse stations along the length
        
    Returns
    -------
    KayakHull
        Hull with triangular cross-section
        
    Notes
    -----
    - Triangular profile: port waterline, keel, starboard waterline
    - When fully submerged to depth:
      Analytical volume = (1/2) × length × width × depth
    """
    hull = KayakHull()
    stations = np.linspace(0, length, num_stations)
    half_width = width / 2.0
    
    for station in stations:
        points = [
            Point3D(station, -half_width, 0.0),   # Port waterline
            Point3D(station, 0.0, -depth),         # Keel
            Point3D(station, half_width, 0.0),    # Starboard waterline
        ]
        hull.add_profile_from_points(station, points)
    
    return hull


def create_circular_profile(
    center_x: float,
    center_y: float,
    center_z: float,
    radius: float,
    num_points: int = 21
) -> Profile:
    """
    Create a circular profile in the y-z plane at given x position.
    
    Parameters
    ----------
    center_x : float
        X-coordinate of the profile (longitudinal position)
    center_y : float
        Y-coordinate of circle center (typically 0 for centerline)
    center_z : float
        Z-coordinate of circle center (typically -radius for half-submerged)
    radius : float
        Radius of the circle
    num_points : int
        Number of points to define the circle
        
    Returns
    -------
    Profile
        Profile with circular shape
        
    Notes
    -----
    - Points go counterclockwise starting from starboard (y > 0)
    - This matches the pattern used by box profiles for Shoelace formula
    - For waterline at z=0, center should be at z=-radius for half-submerged
    """
    # Create points going counterclockwise around the circle
    # Start from angle=0 (starboard side, y=radius, z=center_z)
    # Go counterclockwise: starboard → top → port → bottom → starboard
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    points = []
    
    for angle in angles:
        y = center_y + radius * np.cos(angle)
        z = center_z + radius * np.sin(angle)
        points.append(Point3D(center_x, y, z))
    
    return Profile(center_x, points)


def create_elliptical_profile(
    center_x: float,
    center_y: float,
    center_z: float,
    semi_major: float,
    semi_minor: float,
    num_points: int = 21
) -> Profile:
    """
    Create an elliptical profile in the y-z plane at given x position.
    
    Parameters
    ----------
    center_x : float
        X-coordinate of the profile (longitudinal position)
    center_y : float
        Y-coordinate of ellipse center (typically 0)
    center_z : float
        Z-coordinate of ellipse center
    semi_major : float
        Semi-major axis length (horizontal, y-direction)
    semi_minor : float
        Semi-minor axis length (vertical, z-direction)
    num_points : int
        Number of points to define the ellipse
        
    Returns
    -------
    Profile
        Profile with elliptical shape
        
    Notes
    -----
    - Points are distributed uniformly by angle (not arc length)
    - Ellipse has horizontal semi-major axis (width)
    - Ellipse has vertical semi-minor axis (depth)
    """
    angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
    points = []
    
    for angle in angles:
        y = center_y + semi_major * np.cos(angle)
        z = center_z + semi_minor * np.sin(angle)
        points.append(Point3D(center_x, y, z))
    
    return Profile(center_x, points)
