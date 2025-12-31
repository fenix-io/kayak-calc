"""
Data validation functions for hull geometry input.

This module provides comprehensive validation for hull geometry data including
metadata, points, profiles, and complete hull definitions.
"""

import numpy as np
from typing import Dict, List, Any, Tuple, Optional, Union
from .formats import (
    RECOGNIZED_LENGTH_UNITS,
    RECOGNIZED_COORD_SYSTEMS,
    MIN_POINTS_PER_PROFILE,
    MIN_PROFILES_PER_HULL,
    POINT_FIELDS,
)
from .defaults import REQUIRED_METADATA


def validate_metadata(metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate metadata dictionary.

    Checks:
    - Required fields are present
    - Units are recognized
    - Water density is positive
    - Numerical values are valid (not NaN/Inf)

    Args:
        metadata: Metadata dictionary to validate

    Returns:
        Tuple of (is_valid, error_messages)
        - is_valid: True if validation passes
        - error_messages: List of error messages (empty if valid)

    Example:
        >>> meta = {'units': 'm', 'coordinate_system': 'centerline_origin', 'water_density': 1025.0}
        >>> is_valid, errors = validate_metadata(meta)
        >>> is_valid
        True
        >>> len(errors)
        0
    """
    errors = []

    # Check required fields
    for field in REQUIRED_METADATA:
        if field not in metadata:
            errors.append(f"Missing required metadata field: '{field}'")
        elif metadata[field] is None:
            errors.append(f"Required metadata field '{field}' cannot be None")

    # Validate units if present
    if "units" in metadata and metadata["units"] is not None:
        if metadata["units"] not in RECOGNIZED_LENGTH_UNITS:
            errors.append(
                f"Unrecognized length unit: '{metadata['units']}'. "
                f"Supported units: {', '.join(RECOGNIZED_LENGTH_UNITS)}"
            )

    # Validate coordinate system if present
    if "coordinate_system" in metadata and metadata["coordinate_system"] is not None:
        if metadata["coordinate_system"] not in RECOGNIZED_COORD_SYSTEMS:
            errors.append(
                f"Unrecognized coordinate system: '{metadata['coordinate_system']}'. "
                f"Supported systems: {', '.join(RECOGNIZED_COORD_SYSTEMS)}"
            )

    # Validate water density if present
    if "water_density" in metadata and metadata["water_density"] is not None:
        try:
            density = float(metadata["water_density"])
            if not np.isfinite(density):
                errors.append("Water density must be a finite number")
            elif density <= 0:
                errors.append(f"Water density must be positive, got {density}")
        except (TypeError, ValueError):
            errors.append(
                f"Water density must be a number, got {type(metadata['water_density']).__name__}"
            )

    # Validate length if present
    if "length" in metadata and metadata["length"] is not None:
        try:
            length = float(metadata["length"])
            if not np.isfinite(length):
                errors.append("Length must be a finite number")
            elif length <= 0:
                errors.append(f"Length must be positive, got {length}")
        except (TypeError, ValueError):
            errors.append(f"Length must be a number, got {type(metadata['length']).__name__}")

    # Validate beam if present
    if "beam" in metadata and metadata["beam"] is not None:
        try:
            beam = float(metadata["beam"])
            if not np.isfinite(beam):
                errors.append("Beam must be a finite number")
            elif beam <= 0:
                errors.append(f"Beam must be positive, got {beam}")
        except (TypeError, ValueError):
            errors.append(f"Beam must be a number, got {type(metadata['beam']).__name__}")

    return (len(errors) == 0, errors)


def validate_point_data(
    point_dict: Dict[str, Any], point_index: Optional[int] = None
) -> Tuple[bool, List[str]]:
    """
    Validate a single point's data.

    Checks:
    - All required fields (x, y, z) are present
    - All values are numeric
    - No NaN or Inf values

    Args:
        point_dict: Dictionary with point data
        point_index: Optional index for error messages

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> point = {'x': 0.0, 'y': 1.0, 'z': 2.0}
        >>> is_valid, errors = validate_point_data(point)
        >>> is_valid
        True
    """
    errors = []
    prefix = f"Point {point_index}: " if point_index is not None else "Point: "

    # Check required fields
    for field in POINT_FIELDS:
        if field not in point_dict:
            errors.append(f"{prefix}Missing required field '{field}'")
            continue

        # Check if numeric
        try:
            value = float(point_dict[field])
            if not np.isfinite(value):
                errors.append(f"{prefix}Field '{field}' must be finite, got {value}")
        except (TypeError, ValueError):
            errors.append(
                f"{prefix}Field '{field}' must be numeric, "
                f"got {type(point_dict[field]).__name__}"
            )

    return (len(errors) == 0, errors)


def validate_bow_stern_points(
    bow_stern_data: Union[Dict[str, Any], List[Dict[str, Any]]],
    name: str = "bow/stern",
    check_centerline: bool = True,
    tolerance: float = 1e-6,
) -> Tuple[bool, List[str]]:
    """
    Validate bow or stern point(s) data.

    Supports both single point (legacy) and multi-point array formats.

    Checks:
    - Point data validity (coordinates are numbers, not NaN/Inf)
    - Centerline constraint: all points have y = 0.0 (within tolerance)
    - Consistent level usage: if any point has 'level', all must have it

    Args:
        bow_stern_data: Single point dict or array of point dicts
        name: Name for error messages ("bow" or "stern")
        check_centerline: Whether to enforce y = 0.0 constraint
        tolerance: Maximum allowed deviation from centerline

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Handle both single point and array formats
    if isinstance(bow_stern_data, dict):
        # Single point format (legacy)
        points = [bow_stern_data]
        is_array = False
    elif isinstance(bow_stern_data, list):
        # Multi-point array format
        points = bow_stern_data
        is_array = True
        if len(points) == 0:
            errors.append(f"{name}: Array cannot be empty")
            return (False, errors)
    else:
        errors.append(
            f"{name}: Must be either a point object or array of points, "
            f"got {type(bow_stern_data).__name__}"
        )
        return (False, errors)

    # Track if any point has 'level' attribute
    has_level = []

    # Validate each point
    for i, point in enumerate(points):
        if not isinstance(point, dict):
            errors.append(f"{name} point {i}: Must be a dictionary")
            continue

        # Validate point coordinates
        is_valid, point_errors = validate_point_data(point, i)
        if not is_valid:
            errors.extend([f"{name}: {err}" for err in point_errors])

        # Check centerline constraint (y = 0.0)
        if check_centerline and "y" in point:
            try:
                y_val = float(point["y"])
                if not np.isfinite(y_val):
                    errors.append(f"{name} point {i}: y-coordinate must be finite")
                elif abs(y_val) > tolerance:
                    errors.append(
                        f"{name} point {i}: y-coordinate must be 0.0 (on centerline), "
                        f"got {y_val:.6f} (tolerance: {tolerance})"
                    )
            except (TypeError, ValueError):
                pass  # Already caught by validate_point_data

        # Track level attribute usage
        has_level.append("level" in point)

    # Check level consistency: if any point has level, all should have it
    if any(has_level) and not all(has_level):
        missing_level_indices = [i for i, has in enumerate(has_level) if not has]
        errors.append(
            f"{name}: Inconsistent 'level' attribute usage. "
            f"Points {missing_level_indices} missing 'level' attribute. "
            f"Either all points must have 'level' or none should."
        )

    return (len(errors) == 0, errors)


def validate_profile_data(
    profile_dict: Dict[str, Any], profile_index: Optional[int] = None
) -> Tuple[bool, List[str]]:
    """
    Validate a single profile's data.

    Checks:
    - Station field is present and numeric
    - Points list exists and has minimum length
    - All points are valid
    - All points have consistent x-coordinate (match station)

    Args:
        profile_dict: Dictionary with profile data
        profile_index: Optional index for error messages

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> profile = {
        ...     'station': 0.0,
        ...     'points': [
        ...         {'x': 0.0, 'y': 0.0, 'z': 1.0},
        ...         {'x': 0.0, 'y': 1.0, 'z': 1.0},
        ...         {'x': 0.0, 'y': -1.0, 'z': 1.0}
        ...     ]
        ... }
        >>> is_valid, errors = validate_profile_data(profile)
        >>> is_valid
        True
    """
    errors = []
    prefix = f"Profile {profile_index}: " if profile_index is not None else "Profile: "

    # Check required fields
    if "station" not in profile_dict:
        errors.append(f"{prefix}Missing required field 'station'")
        return (False, errors)

    if "points" not in profile_dict:
        errors.append(f"{prefix}Missing required field 'points'")
        return (False, errors)

    # Validate station
    try:
        station = float(profile_dict["station"])
        if not np.isfinite(station):
            errors.append(f"{prefix}Station must be finite, got {station}")
    except (TypeError, ValueError):
        errors.append(
            f"{prefix}Station must be numeric, " f"got {type(profile_dict['station']).__name__}"
        )
        return (False, errors)

    # Validate points list
    points = profile_dict["points"]
    if not isinstance(points, (list, tuple)):
        errors.append(f"{prefix}Points must be a list or tuple")
        return (False, errors)

    if len(points) < MIN_POINTS_PER_PROFILE:
        errors.append(
            f"{prefix}Must have at least {MIN_POINTS_PER_PROFILE} points, " f"got {len(points)}"
        )

    # Validate each point
    station_value = profile_dict["station"]
    for i, point in enumerate(points):
        if not isinstance(point, dict):
            errors.append(f"{prefix}Point {i} must be a dictionary")
            continue

        is_valid, point_errors = validate_point_data(point, i)
        if not is_valid:
            errors.extend([f"{prefix}{err}" for err in point_errors])

        # Check x-coordinate matches station
        if "x" in point:
            try:
                x_val = float(point["x"])
                if not np.isclose(x_val, station_value):
                    errors.append(
                        f"{prefix}Point {i} x-coordinate ({x_val}) "
                        f"doesn't match station ({station_value})"
                    )
            except (TypeError, ValueError):
                pass  # Already caught by validate_point_data

    return (len(errors) == 0, errors)


def validate_hull_data(hull_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate complete hull geometry data.

    Checks:
    - Metadata is valid (if present)
    - Profiles list exists and has minimum length
    - Each profile is valid
    - Stations are unique
    - Stations are in reasonable order

    Args:
        hull_data: Dictionary with complete hull data

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> hull = {
        ...     'metadata': {'units': 'm',
        ...                  'coordinate_system': 'centerline_origin',
        ...                  'water_density': 1025.0},
        ...     'profiles': [
        ...         {'station': 0.0,
        ...          'points': [{'x': 0.0, 'y': 0.0, 'z': 1.0},
        ...                     {'x': 0.0, 'y': 1.0, 'z': 0.0},
        ...                     {'x': 0.0, 'y': -1.0, 'z': 0.0}]},
        ...         {'station': 1.0,
        ...          'points': [{'x': 1.0, 'y': 0.0, 'z': 1.0},
        ...                     {'x': 1.0, 'y': 1.0, 'z': 0.0},
        ...                     {'x': 1.0, 'y': -1.0, 'z': 0.0}]}
        ...     ]
        ... }
        >>> is_valid, errors = validate_hull_data(hull)
        >>> is_valid
        True
    """
    errors = []

    # Validate metadata if present
    if "metadata" in hull_data and hull_data["metadata"] is not None:
        is_valid, meta_errors = validate_metadata(hull_data["metadata"])
        if not is_valid:
            errors.extend([f"Metadata: {err}" for err in meta_errors])

    # Validate bow points if present
    if "bow" in hull_data and hull_data["bow"] is not None:
        is_valid, bow_errors = validate_bow_stern_points(
            hull_data["bow"], name="bow", check_centerline=True
        )
        if not is_valid:
            errors.extend(bow_errors)

    # Validate stern points if present
    if "stern" in hull_data and hull_data["stern"] is not None:
        is_valid, stern_errors = validate_bow_stern_points(
            hull_data["stern"], name="stern", check_centerline=True
        )
        if not is_valid:
            errors.extend(stern_errors)

    # Check level consistency between bow/stern and profiles if levels are used
    if "bow" in hull_data or "stern" in hull_data:
        # Check if bow/stern use levels
        bow_has_level = False
        stern_has_level = False

        if "bow" in hull_data and hull_data["bow"]:
            bow_points = (
                hull_data["bow"] if isinstance(hull_data["bow"], list) else [hull_data["bow"]]
            )
            bow_has_level = any("level" in pt for pt in bow_points)

        if "stern" in hull_data and hull_data["stern"]:
            stern_points = (
                hull_data["stern"] if isinstance(hull_data["stern"], list) else [hull_data["stern"]]
            )
            stern_has_level = any("level" in pt for pt in stern_points)

        # If bow or stern use levels, check profile points
        if bow_has_level or stern_has_level:
            if "profiles" in hull_data and hull_data["profiles"]:
                profile_has_level = False
                for profile in hull_data["profiles"]:
                    if "points" in profile:
                        profile_has_level = any("level" in pt for pt in profile["points"])
                        break

                if not profile_has_level:
                    errors.append(
                        "Level consistency: bow/stern points use 'level' attribute but "
                        "profile points do not. If 'level' is used in bow/stern, "
                        "all profile points must also have 'level' attribute."
                    )

    # Check profiles field
    if "profiles" not in hull_data:
        errors.append("Missing required field 'profiles'")
        return (False, errors)

    profiles = hull_data["profiles"]
    if not isinstance(profiles, (list, tuple)):
        errors.append("Profiles must be a list or tuple")
        return (False, errors)

    if len(profiles) < MIN_PROFILES_PER_HULL:
        errors.append(
            f"Hull must have at least {MIN_PROFILES_PER_HULL} profiles, " f"got {len(profiles)}"
        )

    # Validate each profile and collect stations
    stations = []
    for i, profile in enumerate(profiles):
        if not isinstance(profile, dict):
            errors.append(f"Profile {i} must be a dictionary")
            continue

        is_valid, profile_errors = validate_profile_data(profile, i)
        if not is_valid:
            errors.extend(profile_errors)

        # Collect station for duplicate check
        if "station" in profile:
            try:
                stations.append(float(profile["station"]))
            except (TypeError, ValueError):
                pass  # Already caught by validate_profile_data

    # Check for duplicate stations
    if len(stations) > 0:
        unique_stations = set(stations)
        if len(unique_stations) < len(stations):
            errors.append(
                "Duplicate stations found. " "Each profile must have a unique station value."
            )

    return (len(errors) == 0, errors)


def validate_csv_data(
    data: Union[np.ndarray, List[List[float]]], columns: List[str], format_type: str = "xyz"
) -> Tuple[bool, List[str]]:
    """
    Validate CSV data array or list.

    Checks:
    - Data is 2D array-like
    - Has correct number of columns
    - No missing values (NaN)
    - All values are finite

    Args:
        data: 2D array or list of rows
        columns: Column names expected
        format_type: 'xyz' or 'station_yz'

    Returns:
        Tuple of (is_valid, error_messages)

    Example:
        >>> data = [[0.0, 0.0, 1.0], [0.0, 1.0, 0.0]]
        >>> is_valid, errors = validate_csv_data(data, ['x', 'y', 'z'])
        >>> is_valid
        True
    """
    errors = []

    # Convert to numpy array for easier validation
    try:
        arr = np.array(data, dtype=float)
    except (TypeError, ValueError) as e:
        errors.append(f"Could not convert data to numeric array: {e}")
        return (False, errors)

    # Check dimensions
    if arr.ndim != 2:
        errors.append(f"Data must be 2-dimensional, got {arr.ndim} dimensions")
        return (False, errors)

    # Check number of columns
    expected_cols = len(columns)
    if arr.shape[1] != expected_cols:
        errors.append(f"Expected {expected_cols} columns {columns}, " f"got {arr.shape[1]} columns")

    # Check for NaN values
    if np.any(np.isnan(arr)):
        nan_count = np.sum(np.isnan(arr))
        errors.append(f"Data contains {nan_count} NaN values")

    # Check for infinite values
    if np.any(np.isinf(arr)):
        inf_count = np.sum(np.isinf(arr))
        errors.append(f"Data contains {inf_count} infinite values")

    # Check minimum rows
    if arr.shape[0] < MIN_POINTS_PER_PROFILE:
        errors.append(
            f"CSV data must have at least {MIN_POINTS_PER_PROFILE} rows, "
            f"got {arr.shape[0]} rows"
        )

    return (len(errors) == 0, errors)


def validate_symmetry(
    points: List[Dict[str, float]], tolerance: float = 1e-6
) -> Tuple[bool, List[str]]:
    """
    Validate that points exhibit port-starboard symmetry.

    For each point with y != 0, there should be a corresponding point
    at y' = -y with the same x and z coordinates.

    Args:
        points: List of point dictionaries
        tolerance: Numerical tolerance for comparisons

    Returns:
        Tuple of (is_symmetric, error_messages)

    Example:
        >>> points = [
        ...     {'x': 0.0, 'y': 0.0, 'z': 1.0},
        ...     {'x': 0.0, 'y': 0.5, 'z': 0.5},
        ...     {'x': 0.0, 'y': -0.5, 'z': 0.5}
        ... ]
        >>> is_sym, errors = validate_symmetry(points)
        >>> is_sym
        True
    """
    errors = []

    # Group points by y-coordinate sign
    centerline_points = []
    port_points = []  # y < 0
    starboard_points = []  # y > 0

    for point in points:
        y = point.get("y", 0)
        if abs(y) < tolerance:
            centerline_points.append(point)
        elif y < 0:
            port_points.append(point)
        else:
            starboard_points.append(point)

    # For each port point, find matching starboard point
    for port_pt in port_points:
        found_match = False
        for stbd_pt in starboard_points:
            # Check if mirror image
            x_match = abs(port_pt.get("x", 0) - stbd_pt.get("x", 0)) < tolerance
            y_match = abs(port_pt.get("y", 0) + stbd_pt.get("y", 0)) < tolerance
            z_match = abs(port_pt.get("z", 0) - stbd_pt.get("z", 0)) < tolerance

            if x_match and y_match and z_match:
                found_match = True
                break

        if not found_match:
            errors.append(
                f"No symmetric match found for point at "
                f"y={port_pt.get('y', 0):.4f}, z={port_pt.get('z', 0):.4f}"
            )

    # Check count balance (ignoring centerline points)
    if len(port_points) != len(starboard_points):
        errors.append(
            f"Unequal number of port ({len(port_points)}) and "
            f"starboard ({len(starboard_points)}) points"
        )

    return (len(errors) == 0, errors)
