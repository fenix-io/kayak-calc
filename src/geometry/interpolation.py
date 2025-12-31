"""
Interpolation functions for kayak hull geometry.

This module provides three types of interpolation functions:
1. Transverse interpolation - between port and starboard points on a single profile
2. Longitudinal interpolation - between adjacent profiles to create intermediate cross-sections
3. Bow/stern interpolation - from end profiles to bow/stern apex points
"""

import numpy as np
from typing import List, Optional
from .point import Point3D
from .profile import Profile


def interpolate_transverse(
    points: List[Point3D], num_points: int, method: str = "linear"
) -> List[Point3D]:
    """
    Interpolate points along a transverse profile curve.

    Creates evenly distributed points along the profile by interpolating
    between port and starboard points. This is useful for generating
    intermediate points along a profile curve for smoother calculations.

    Args:
        points: List of Point3D objects defining the profile (should all have same x)
        num_points: Number of points to generate in the interpolated result
        method: Interpolation method ('linear' or 'cubic')
            - 'linear': Linear interpolation between points
            - 'cubic': Cubic spline interpolation (smoother, requires scipy)

    Returns:
        List of interpolated Point3D objects

    Raises:
        ValueError: If less than 2 points provided or points have inconsistent x-coordinates

    Example:
        >>> points = [Point3D(0, -0.5, 0.1), Point3D(0, 0.0, 0.0), Point3D(0, 0.5, 0.1)]
        >>> interpolated = interpolate_transverse(points, 10)
        >>> len(interpolated)
        10
    """
    if len(points) < 2:
        raise ValueError("Need at least 2 points for transverse interpolation")

    # Verify all points have the same x-coordinate
    x_station = points[0].x
    for point in points:
        if not np.isclose(point.x, x_station):
            raise ValueError(
                f"All points must have the same x-coordinate. "
                f"Found x={point.x}, expected x={x_station}"
            )

    # Sort points by y-coordinate (transverse direction)
    sorted_points = sorted(points, key=lambda p: p.y)

    # Extract coordinates
    y_coords = np.array([p.y for p in sorted_points])
    z_coords = np.array([p.z for p in sorted_points])

    # Create evenly spaced y-coordinates for interpolation
    y_new = np.linspace(y_coords.min(), y_coords.max(), num_points)

    # Perform interpolation based on method
    if method == "linear":
        z_new = np.interp(y_new, y_coords, z_coords)
    elif method == "cubic":
        try:
            from scipy.interpolate import CubicSpline

            cs = CubicSpline(y_coords, z_coords)
            z_new = cs(y_new)
        except ImportError:
            # Fall back to linear if scipy not available
            z_new = np.interp(y_new, y_coords, z_coords)
    else:
        raise ValueError(f"Unknown interpolation method: {method}")

    # Create interpolated points
    interpolated_points = [Point3D(x_station, y, z) for y, z in zip(y_new, z_new)]

    return interpolated_points


def interpolate_profile_transverse(
    profile: Profile, num_points: int, method: str = "linear"
) -> Profile:
    """
    Create a new profile with interpolated points along the profile curve.

    Convenience function that wraps interpolate_transverse for Profile objects.

    Args:
        profile: Profile object to interpolate
        num_points: Number of points in the interpolated profile
        method: Interpolation method ('linear' or 'cubic')

    Returns:
        New Profile with interpolated points at the same station

    Example:
        >>> profile = Profile(0.0, [Point3D(0, -0.5, 0.1), Point3D(0, 0.5, 0.1)])
        >>> interpolated_profile = interpolate_profile_transverse(profile, 20)
    """
    interpolated_points = interpolate_transverse(profile.points, num_points, method)
    return Profile(profile.station, interpolated_points)


def interpolate_longitudinal(
    profile1: Profile, profile2: Profile, target_station: float, num_points: Optional[int] = None
) -> Profile:
    """
    Interpolate a profile between two adjacent profiles at a target station.

    Creates an intermediate profile by linearly interpolating between two
    profiles at different longitudinal stations. Handles profiles with
    different numbers of points by first interpolating both to a common
    set of y-coordinates.

    Args:
        profile1: First profile (at lower station)
        profile2: Second profile (at higher station)
        target_station: Longitudinal position for the interpolated profile
        num_points: Number of points in result (default: average of input profiles)

    Returns:
        Interpolated Profile at target_station

    Raises:
        ValueError: If target_station is outside the range [profile1.station, profile2.station]

    Example:
        >>> p1 = Profile(0.0, [Point3D(0, -0.5, 0.1), Point3D(0, 0.5, 0.1)])
        >>> p2 = Profile(1.0, [Point3D(1, -0.4, 0.08), Point3D(1, 0.4, 0.08)])
        >>> p_mid = interpolate_longitudinal(p1, p2, 0.5)
        >>> p_mid.station
        0.5
    """
    # Ensure profile1 is at lower station
    if profile1.station > profile2.station:
        profile1, profile2 = profile2, profile1

    # Validate target station is within range
    if target_station < profile1.station or target_station > profile2.station:
        raise ValueError(
            f"Target station {target_station} must be between "
            f"{profile1.station} and {profile2.station}"
        )

    # Calculate interpolation factor
    if np.isclose(profile1.station, profile2.station):
        # Profiles at same station - return copy of first profile
        return profile1.copy()

    t = (target_station - profile1.station) / (profile2.station - profile1.station)

    # Determine number of points for interpolated profile
    if num_points is None:
        num_points = (len(profile1) + len(profile2)) // 2
        num_points = max(num_points, 10)  # Minimum 10 points

    # Sort points by y-coordinate
    points1 = sorted(profile1.points, key=lambda p: p.y)
    points2 = sorted(profile2.points, key=lambda p: p.y)

    # Extract coordinates
    y1 = np.array([p.y for p in points1])
    z1 = np.array([p.z for p in points1])

    y2 = np.array([p.y for p in points2])
    z2 = np.array([p.z for p in points2])

    # Determine common y-coordinate range (intersection of both profiles)
    y_min = max(y1.min(), y2.min())
    y_max = min(y1.max(), y2.max())

    # If no overlap, use the union range but warn
    if y_min > y_max:
        y_min = min(y1.min(), y2.min())
        y_max = max(y1.max(), y2.max())

    # Create common y-coordinates
    y_common = np.linspace(y_min, y_max, num_points)

    # Interpolate z-coordinates for both profiles at common y values
    z1_interp = np.interp(y_common, y1, z1)
    z2_interp = np.interp(y_common, y2, z2)

    # Linear interpolation between the two profiles
    z_result = (1 - t) * z1_interp + t * z2_interp

    # Create interpolated points
    interpolated_points = [Point3D(target_station, y, z) for y, z in zip(y_common, z_result)]

    return Profile(target_station, interpolated_points)


def interpolate_multiple_profiles(
    profiles: List[Profile], target_stations: List[float], num_points: Optional[int] = None
) -> List[Profile]:
    """
    Interpolate multiple profiles at specified target stations.

    For each target station, finds the appropriate adjacent profiles and
    performs longitudinal interpolation. This is useful for densifying
    the profile distribution along the hull.

    Args:
        profiles: List of Profile objects (will be sorted by station)
        target_stations: List of longitudinal positions for interpolated profiles
        num_points: Number of points in each interpolated profile (optional)

    Returns:
        List of interpolated Profile objects

    Raises:
        ValueError: If less than 2 profiles provided
        ValueError: If any target station is outside profile range

    Example:
        >>> profiles = [Profile(0.0, [...]), Profile(2.0, [...])]
        >>> targets = [0.5, 1.0, 1.5]
        >>> interpolated = interpolate_multiple_profiles(profiles, targets)
        >>> len(interpolated)
        3
    """
    if len(profiles) < 2:
        raise ValueError("Need at least 2 profiles for longitudinal interpolation")

    # Sort profiles by station
    sorted_profiles = sorted(profiles, key=lambda p: p.station)
    stations = [p.station for p in sorted_profiles]

    # Validate all target stations are within range
    min_station = stations[0]
    max_station = stations[-1]

    for target in target_stations:
        if target < min_station or target > max_station:
            raise ValueError(
                f"Target station {target} is outside profile range "
                f"[{min_station}, {max_station}]"
            )

    interpolated_profiles = []

    for target in target_stations:
        # Find adjacent profiles
        profile_before = None
        profile_after = None

        for i, station in enumerate(stations):
            if station <= target:
                profile_before = sorted_profiles[i]
            if station >= target:
                profile_after = sorted_profiles[i]
                break

        if profile_before is None or profile_after is None:
            raise ValueError(f"Cannot find adjacent profiles for station {target}")

        # Interpolate between adjacent profiles
        interpolated = interpolate_longitudinal(profile_before, profile_after, target, num_points)
        interpolated_profiles.append(interpolated)

    return interpolated_profiles


def interpolate_to_apex(
    profile: Profile,
    apex_point: Point3D,
    num_intermediate_stations: int = 5,
    num_points_per_profile: Optional[int] = None,
) -> List[Profile]:
    """
    Interpolate profiles from an end profile to a bow/stern apex point.

    Creates intermediate profiles that taper from the end profile to the
    apex point (bow or stern). This handles the geometry where the hull
    narrows to a point at the ends.

    The interpolation creates profiles that progressively reduce in size
    as they approach the apex, maintaining the shape characteristics.

    Args:
        profile: End profile (bow or stern profile)
        apex_point: Apex point (bow or stern tip)
        num_intermediate_stations: Number of profiles to create between profile and apex
        num_points_per_profile: Number of points in each intermediate profile (optional)

    Returns:
        List of Profile objects from the end profile toward the apex
        (not including the original profile or the apex itself)

    Raises:
        ValueError: If apex_point x-coordinate doesn't extend beyond profile station

    Example:
        >>> bow_profile = Profile(4.5, [Point3D(4.5, -0.2, 0.1), Point3D(4.5, 0.2, 0.1)])
        >>> bow_apex = Point3D(5.0, 0.0, 0.15)
        >>> tapered_profiles = interpolate_to_apex(bow_profile, bow_apex, 3)
        >>> len(tapered_profiles)
        3
    """
    # Validate that apex point is in the correct direction
    if apex_point.x == profile.station:
        raise ValueError(
            f"Apex point x={apex_point.x} must be different from "
            f"profile station {profile.station}"
        )

    # Determine number of points if not specified
    if num_points_per_profile is None:
        num_points_per_profile = max(len(profile) // 2, 5)

    # Generate intermediate stations
    stations = np.linspace(
        profile.station, apex_point.x, num_intermediate_stations + 2  # +2 for start and end
    )[
        1:-1
    ]  # Exclude start (original profile) and end (apex point)

    intermediate_profiles = []

    # Sort profile points by distance from centerline
    sorted_points = sorted(profile.points, key=lambda p: abs(p.y))

    # Extract coordinates
    y_coords = np.array([p.y for p in sorted_points])
    z_coords = np.array([p.z for p in sorted_points])

    # For each intermediate station, create a tapered profile
    for station in stations:
        # Calculate scaling factor (0 at apex, 1 at original profile)
        t = abs(station - profile.station) / abs(apex_point.x - profile.station)
        scale = 1 - t  # Linear tapering

        # Scale the profile points toward the apex
        # The y-coordinates scale toward centerline (y=0)
        # The z-coordinates interpolate toward apex z-coordinate
        y_scaled = y_coords * scale
        z_scaled = z_coords * (1 - t) + apex_point.z * t

        # Create points for this station
        # Reduce number of points as we approach apex
        points_in_this_profile = max(
            int(num_points_per_profile * (1 - t * 0.5)), 3  # Minimum 3 points
        )

        # Sample evenly from scaled coordinates
        if len(y_scaled) >= points_in_this_profile:
            indices = np.linspace(0, len(y_scaled) - 1, points_in_this_profile, dtype=int)
            y_sampled = y_scaled[indices]
            z_sampled = z_scaled[indices]
        else:
            y_sampled = y_scaled
            z_sampled = z_scaled

        # Create points
        station_points = [Point3D(station, y, z) for y, z in zip(y_sampled, z_sampled)]

        # Ensure we have at least centerline point if very close to apex
        if scale < 0.1 and not any(abs(p.y) < 1e-6 for p in station_points):
            # Add centerline point
            station_points.append(Point3D(station, 0.0, apex_point.z))
            station_points.sort(key=lambda p: p.y)

        intermediate_profiles.append(Profile(station, station_points))

    return intermediate_profiles


def create_symmetric_profile(
    station: float, starboard_points: List[Point3D], include_centerline: bool = True
) -> Profile:
    """
    Create a symmetric profile from starboard side points only.

    Generates a complete profile by mirroring starboard points to port side.
    Assumes y > 0 is starboard, y < 0 is port.

    Args:
        station: Longitudinal position for the profile
        starboard_points: List of points on starboard side (y >= 0)
        include_centerline: Whether to include centerline point (y=0) if not present

    Returns:
        Complete symmetric Profile with port and starboard points

    Raises:
        ValueError: If any points have negative y-coordinates

    Example:
        >>> stbd_points = [Point3D(1.0, 0.0, 0.0), Point3D(1.0, 0.5, 0.1)]
        >>> profile = create_symmetric_profile(1.0, stbd_points)
        >>> len(profile)  # Should have port mirror plus original
        4
    """
    # Validate starboard points
    for point in starboard_points:
        if point.y < -1e-6:  # Allow small numerical error
            raise ValueError(
                f"Point has negative y-coordinate: y={point.y}. "
                f"Only starboard points (y >= 0) should be provided."
            )
        if not np.isclose(point.x, station):
            raise ValueError(f"Point x={point.x} doesn't match station {station}")

    # Create complete list with port and starboard points
    all_points = []

    # Add port (mirrored) points
    for point in starboard_points:
        if point.y > 1e-6:  # Not on centerline
            all_points.append(Point3D(station, -point.y, point.z))

    # Add centerline point if requested and not present
    has_centerline = any(abs(p.y) < 1e-6 for p in starboard_points)
    if include_centerline and not has_centerline:
        # Find z-coordinate at centerline by interpolation
        if len(starboard_points) > 0:
            sorted_stbd = sorted(starboard_points, key=lambda p: p.y)
            if sorted_stbd[0].y < 1e-6:
                z_center = sorted_stbd[0].z
            else:
                # Interpolate
                y_coords = [p.y for p in sorted_stbd]
                z_coords = [p.z for p in sorted_stbd]
                z_center = np.interp(0.0, y_coords, z_coords)
            all_points.append(Point3D(station, 0.0, z_center))

    # Add starboard points
    all_points.extend(starboard_points)

    # Sort by y-coordinate (port to starboard)
    all_points.sort(key=lambda p: p.y)

    return Profile(station, all_points)


def resample_profile_uniform_y(profile: Profile, num_points: int) -> Profile:
    """
    Resample profile with uniformly spaced y-coordinates.

    Creates a new profile with points evenly distributed in the transverse
    (y) direction. Useful for ensuring consistent point distribution.

    Args:
        profile: Profile to resample
        num_points: Number of points in resampled profile

    Returns:
        New Profile with uniform y-spacing

    Example:
        >>> profile = Profile(0.0, [Point3D(0, -1, 0.2), Point3D(0, 0.5, 0.1)])
        >>> uniform = resample_profile_uniform_y(profile, 20)
    """
    return interpolate_profile_transverse(profile, num_points, method="linear")


def resample_profile_uniform_arc(profile: Profile, num_points: int) -> Profile:
    """
    Resample profile with points uniformly distributed along arc length.

    Creates a new profile where points are evenly spaced along the curve
    length rather than in y-coordinate. This provides better resolution
    in areas of high curvature.

    Args:
        profile: Profile to resample
        num_points: Number of points in resampled profile

    Returns:
        New Profile with uniform arc-length spacing

    Example:
        >>> profile = Profile(0.0, [Point3D(0, -0.5, 0.1), Point3D(0, 0.5, 0.1)])
        >>> arc_uniform = resample_profile_uniform_arc(profile, 20)
    """
    if len(profile) < 2:
        return profile.copy()

    # Sort points by y-coordinate
    sorted_points = sorted(profile.points, key=lambda p: p.y)

    # Calculate cumulative arc length
    arc_lengths = [0.0]
    for i in range(1, len(sorted_points)):
        p1 = sorted_points[i - 1]
        p2 = sorted_points[i]
        segment_length = p1.distance_to(p2)
        arc_lengths.append(arc_lengths[-1] + segment_length)

    total_length = arc_lengths[-1]

    if total_length < 1e-10:
        # All points are at same location
        return profile.copy()

    # Create uniform arc length distribution
    uniform_arc = np.linspace(0, total_length, num_points)

    # Extract coordinates
    y_coords = np.array([p.y for p in sorted_points])
    z_coords = np.array([p.z for p in sorted_points])

    # Interpolate coordinates at uniform arc lengths
    y_new = np.interp(uniform_arc, arc_lengths, y_coords)
    z_new = np.interp(uniform_arc, arc_lengths, z_coords)

    # Create resampled points
    resampled_points = [Point3D(profile.station, y, z) for y, z in zip(y_new, z_new)]

    return Profile(profile.station, resampled_points)


def interpolate_to_bow_stern_multipoint(
    end_profile: Profile,
    end_points: List[Point3D],
    num_intermediate_stations: int = 5,
    is_bow: bool = True,
) -> List[Profile]:
    """
    Interpolate profiles from an end profile to multi-point bow/stern definition.

    Creates intermediate profiles that transition from the last data station to
    the bow/stern end points. Handles both level-based matching and position-based
    matching approaches.

    This function supports Task 9.7's multi-point bow/stern feature, which allows
    defining multiple points at different vertical levels (keel, chines, gunwale)
    at the bow and stern for better control over hull rocker and shape.

    **Matching Approaches**:
    1. **Level-based**: If 'level' attribute is present in end_points, matches points
       by level name (e.g., 'keel', 'chine1', 'gunwale')
    2. **Position-based**: If no 'level' attributes, matches by array position
       (assumes consistent ordering: centerline first, then port/starboard pairs)

    **Algorithm**:
    1. Detect matching approach (level names vs. positions)
    2. Group profile points by level or position
    3. For each level/position:
       - Find corresponding point in end_profile (centerline)
       - Find port/starboard pair in end_profile (if not centerline)
       - Interpolate from profile point(s) to bow/stern point
    4. Create intermediate profiles at evenly spaced stations
    5. Create final profile at bow/stern point location

    Args:
        end_profile: Last data station profile (bow or stern profile)
        end_points: List of bow/stern points (from bow_points or stern_points)
        num_intermediate_stations: Number of profiles between end_profile and bow/stern
        is_bow: True if interpolating to bow, False if to stern

    Returns:
        List of Profile objects from end_profile toward bow/stern points
        (includes final profile at bow/stern location, excludes original end_profile)

    Raises:
        ValueError: If end_points is empty
        ValueError: If level-based matching fails to find corresponding points
        ValueError: If position-based matching has inconsistent point counts

    Example:
        >>> # Level-based matching
        >>> bow_profile = Profile(4.5, [
        ...     Point3D(4.5, 0.0, 0.3, level='gunwale'),
        ...     Point3D(4.5, -0.2, 0.1, level='chine'),
        ...     Point3D(4.5, 0.2, 0.1, level='chine'),
        ... ])
        >>> bow_points = [
        ...     Point3D(5.0, 0.0, 0.5, level='gunwale'),
        ...     Point3D(4.8, 0.0, 0.3, level='chine'),
        ... ]
        >>> profiles = interpolate_to_bow_stern_multipoint(bow_profile, bow_points, 3)
        >>> len(profiles)
        4  # 3 intermediate + 1 final

        >>> # Position-based matching
        >>> bow_points_no_levels = [
        ...     Point3D(5.0, 0.0, 0.5),
        ...     Point3D(4.8, 0.0, 0.3),
        ... ]
        >>> profiles = interpolate_to_bow_stern_multipoint(bow_profile, bow_points_no_levels, 3)
    """
    if not end_points:
        raise ValueError("end_points cannot be empty")

    # Detect matching approach: check if any end_point has 'level' attribute
    use_level_matching = any(hasattr(pt, "level") and pt.level is not None for pt in end_points)

    if use_level_matching:
        return _interpolate_multipoint_by_level(
            end_profile, end_points, num_intermediate_stations, is_bow
        )
    else:
        return _interpolate_multipoint_by_position(
            end_profile, end_points, num_intermediate_stations, is_bow
        )


def _interpolate_multipoint_by_level(
    end_profile: Profile,
    end_points: List[Point3D],
    num_intermediate_stations: int,
    is_bow: bool,
) -> List[Profile]:
    """
    Interpolate to multi-point bow/stern using level-based matching.

    Internal function that handles level-based point correspondence.
    """
    # Group profile points by level
    profile_by_level = {}
    for point in end_profile.points:
        level = point.level if hasattr(point, "level") else None
        if level is None:
            raise ValueError(
                "Level-based matching requires all profile points to have 'level' attribute"
            )
        if level not in profile_by_level:
            profile_by_level[level] = []
        profile_by_level[level].append(point)

    # Validate that all end_points have levels
    for pt in end_points:
        if not hasattr(pt, "level") or pt.level is None:
            raise ValueError(
                "Level-based matching requires all end_points to have 'level' attribute"
            )

    # Determine station range
    profile_station = end_profile.station
    # Find furthest bow/stern point
    if is_bow:
        end_station = max(pt.x for pt in end_points)
    else:
        end_station = min(pt.x for pt in end_points)

    # Generate intermediate stations
    stations = np.linspace(
        profile_station, end_station, num_intermediate_stations + 2
    )  # +2 for start and end
    stations = stations[1:]  # Exclude original profile station

    intermediate_profiles = []

    # For each intermediate station, create a profile
    for station in stations:
        # Calculate interpolation factor (0 at profile, 1 at bow/stern)
        if abs(end_station - profile_station) < 1e-10:
            t = 1.0
        else:
            t = abs(station - profile_station) / abs(end_station - profile_station)

        station_points = []

        # For each level in end_points, interpolate corresponding profile points
        for end_pt in end_points:
            level = end_pt.level

            # Find corresponding points in profile
            if level not in profile_by_level:
                # If this level doesn't exist in profile, we need to interpolate
                # from some representative profile point(s) to the end point
                # Use centerline points or average of all points
                profile_centerline = [p for p in end_profile.points if abs(p.y) < 1e-6]
                if profile_centerline:
                    # Interpolate from centerline
                    avg_z = sum(p.z for p in profile_centerline) / len(profile_centerline)
                    z_new = (1 - t) * avg_z + t * end_pt.z
                    station_points.append(Point3D(station, 0.0, z_new, level=level))

                    # Also taper port/starboard points toward centerline
                    port_pts = [p for p in end_profile.points if p.y < -1e-6]
                    starboard_pts = [p for p in end_profile.points if p.y > 1e-6]

                    for pt in port_pts:
                        y_new = pt.y * (1 - t)
                        z_new = (1 - t) * pt.z + t * end_pt.z
                        if abs(y_new) > 1e-6:
                            station_points.append(Point3D(station, y_new, z_new, level=level))

                    for pt in starboard_pts:
                        y_new = pt.y * (1 - t)
                        z_new = (1 - t) * pt.z + t * end_pt.z
                        if abs(y_new) > 1e-6:
                            station_points.append(Point3D(station, y_new, z_new, level=level))
                else:
                    # No centerline, just use any profile point
                    avg_z = sum(p.z for p in end_profile.points) / len(end_profile.points)
                    z_new = (1 - t) * avg_z + t * end_pt.z
                    station_points.append(Point3D(station, 0.0, z_new, level=level))
                continue

            profile_pts = profile_by_level[level]

            # Separate centerline and port/starboard points
            centerline_pts = [p for p in profile_pts if abs(p.y) < 1e-6]
            port_pts = [p for p in profile_pts if p.y < -1e-6]
            starboard_pts = [p for p in profile_pts if p.y > 1e-6]

            # Interpolate based on end point being on centerline or not
            if abs(end_pt.y) < 1e-6:
                # Centerline point
                if centerline_pts:
                    # Interpolate from centerline point to end point
                    profile_pt = centerline_pts[0]
                    z_new = (1 - t) * profile_pt.z + t * end_pt.z
                    station_points.append(Point3D(station, 0.0, z_new, level=level))
                else:
                    # No centerline point in profile, create tapering path
                    # Average the port/starboard points
                    if port_pts and starboard_pts:
                        avg_z = (port_pts[0].z + starboard_pts[0].z) / 2
                        z_new = (1 - t) * avg_z + t * end_pt.z
                        station_points.append(Point3D(station, 0.0, z_new, level=level))
                    else:
                        # Just use the end point position
                        station_points.append(
                            Point3D(
                                station,
                                0.0,
                                (1 - t) * end_profile.points[0].z + t * end_pt.z,
                                level=level,
                            )
                        )

                # Also interpolate port/starboard points tapering to centerline
                if port_pts:
                    for pt in port_pts:
                        # Scale y toward centerline
                        y_new = pt.y * (1 - t)
                        z_new = (1 - t) * pt.z + t * end_pt.z
                        if abs(y_new) > 1e-6:  # Don't duplicate centerline
                            station_points.append(Point3D(station, y_new, z_new, level=level))

                if starboard_pts:
                    for pt in starboard_pts:
                        # Scale y toward centerline
                        y_new = pt.y * (1 - t)
                        z_new = (1 - t) * pt.z + t * end_pt.z
                        if abs(y_new) > 1e-6:  # Don't duplicate centerline
                            station_points.append(Point3D(station, y_new, z_new, level=level))

            else:
                # Off-centerline end point (unusual but handle it)
                # Find closest profile point
                closest_pt = min(profile_pts, key=lambda p: abs(p.y - end_pt.y))
                y_new = (1 - t) * closest_pt.y + t * end_pt.y
                z_new = (1 - t) * closest_pt.z + t * end_pt.z
                station_points.append(Point3D(station, y_new, z_new, level=level))

        if station_points:
            # Sort points by y-coordinate
            station_points.sort(key=lambda p: p.y)
            intermediate_profiles.append(Profile(station, station_points))

    return intermediate_profiles


def _interpolate_multipoint_by_position(
    end_profile: Profile,
    end_points: List[Point3D],
    num_intermediate_stations: int,
    is_bow: bool,
) -> List[Profile]:
    """
    Interpolate to multi-point bow/stern using position-based matching.

    Internal function that handles position-based point correspondence.
    Assumes consistent ordering: centerline points first, then port/starboard pairs.
    """
    # For position-based matching, we assume:
    # - end_points are ordered by vertical level (top to bottom or bottom to top)
    # - profile points are grouped similarly
    # - We match by finding corresponding "levels" based on z-coordinate proximity

    # Sort end_points by z-coordinate (vertical)
    sorted_end_points = sorted(end_points, key=lambda p: -p.z)  # High to low

    # Group profile points by approximate z-level
    # Find unique z-levels in profile
    profile_centerline = [p for p in end_profile.points if abs(p.y) < 1e-6]
    profile_centerline_sorted = sorted(profile_centerline, key=lambda p: -p.z)

    # Determine station range
    profile_station = end_profile.station
    if is_bow:
        end_station = max(pt.x for pt in end_points)
    else:
        end_station = min(pt.x for pt in end_points)

    # Generate intermediate stations
    stations = np.linspace(profile_station, end_station, num_intermediate_stations + 2)
    stations = stations[1:]

    intermediate_profiles = []

    # Match end_points to profile levels by z-proximity
    for station in stations:
        t = (
            abs(station - profile_station) / abs(end_station - profile_station)
            if abs(end_station - profile_station) > 1e-10
            else 1.0
        )

        station_points = []

        # For each end_point, find corresponding profile points
        for end_pt in sorted_end_points:
            # Find closest centerline point in profile by z-coordinate
            if profile_centerline_sorted:
                closest_profile_pt = min(
                    profile_centerline_sorted, key=lambda p: abs(p.z - end_pt.z)
                )

                # Find port/starboard points at similar z-level
                z_tolerance = 0.15  # meters, adjust as needed
                profile_pts_at_level = [
                    p for p in end_profile.points if abs(p.z - closest_profile_pt.z) < z_tolerance
                ]

                # Separate by side
                centerline_pts = [p for p in profile_pts_at_level if abs(p.y) < 1e-6]
                port_pts = [p for p in profile_pts_at_level if p.y < -1e-6]
                starboard_pts = [p for p in profile_pts_at_level if p.y > 1e-6]

                # Interpolate centerline point
                if centerline_pts:
                    profile_pt = centerline_pts[0]
                    z_new = (1 - t) * profile_pt.z + t * end_pt.z
                    station_points.append(Point3D(station, 0.0, z_new, level=end_pt.level))

                # Interpolate and taper port/starboard points
                for pt in port_pts:
                    y_new = pt.y * (1 - t)  # Taper toward centerline
                    z_new = (1 - t) * pt.z + t * end_pt.z
                    if abs(y_new) > 1e-6:
                        station_points.append(Point3D(station, y_new, z_new, level=end_pt.level))

                for pt in starboard_pts:
                    y_new = pt.y * (1 - t)  # Taper toward centerline
                    z_new = (1 - t) * pt.z + t * end_pt.z
                    if abs(y_new) > 1e-6:
                        station_points.append(Point3D(station, y_new, z_new, level=end_pt.level))
            else:
                # No centerline points, just interpolate directly
                station_points.append(Point3D(station, 0.0, end_pt.z * t, level=end_pt.level))

        if station_points:
            station_points.sort(key=lambda p: p.y)
            intermediate_profiles.append(Profile(station, station_points))

    return intermediate_profiles
