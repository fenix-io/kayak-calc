"""
Functions for loading hull geometry data from files.

This module provides functions to load kayak hull geometry from JSON and CSV files,
with comprehensive validation and error handling.
"""

import json
import csv
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from ..geometry.hull import KayakHull
from ..geometry.profile import Profile
from ..geometry.point import Point3D
from ..geometry.interpolation import interpolate_longitudinal
from .validators import (
    validate_hull_data,
    validate_csv_data,
)
from .defaults import apply_metadata_defaults, extract_metadata_from_comments
from .formats import CSV_FORMATS


class DataLoadError(Exception):
    """Exception raised when data loading fails."""


def load_hull_from_json(filepath: Union[str, Path], validate: bool = True) -> KayakHull:
    """
    Load kayak hull geometry from a JSON file.

    The JSON file should have the following structure:
    {
        "metadata": {
            "name": "Kayak Name",
            "units": "m",
            "coordinate_system": "centerline_origin",
            "water_density": 1025.0
        },
        "profiles": [
            {
                "station": 0.0,
                "points": [
                    {"x": 0.0, "y": 0.0, "z": 1.0},
                    {"x": 0.0, "y": 0.5, "z": 0.5},
                    ...
                ]
            },
            ...
        ]
    }

    Args:
        filepath: Path to JSON file
        validate: If True, validate data before creating hull

    Returns:
        KayakHull object with loaded geometry

    Raises:
        DataLoadError: If file cannot be loaded or data is invalid
        FileNotFoundError: If file doesn't exist

    Example:
        >>> hull = load_hull_from_json('data/my_kayak.json')
        >>> len(hull.get_stations())
        5
    """
    filepath = Path(filepath)

    # Check file exists
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Load JSON
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise DataLoadError(f"Invalid JSON in {filepath}: {e}")
    except Exception as e:
        raise DataLoadError(f"Error reading {filepath}: {e}")

    # Validate data structure
    if validate:
        is_valid, errors = validate_hull_data(data)
        if not is_valid:
            error_msg = f"Invalid hull data in {filepath}:\n" + "\n".join(
                f"  - {err}" for err in errors
            )
            raise DataLoadError(error_msg)

    # Parse and create hull
    try:
        hull = _create_hull_from_dict(data)
    except Exception as e:
        raise DataLoadError(f"Error creating hull from {filepath}: {e}")

    return hull


def load_hull_from_csv(
    filepath: Union[str, Path],
    format_type: str = "xyz",
    has_header: bool = True,
    delimiter: str = ",",
    comment_char: str = "#",
    validate: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> KayakHull:
    """
    Load kayak hull geometry from a CSV file.

    Supports two CSV formats:
    - 'xyz': Three columns (x, y, z) where x is the station
    - 'station_yz': Three columns (station, y, z) where x is derived from station

    Metadata can be provided as:
    1. Comment lines in the CSV (e.g., "# Units: m")
    2. Passed as metadata parameter
    3. Default values will be used if not specified

    Args:
        filepath: Path to CSV file
        format_type: 'xyz' or 'station_yz'
        has_header: If True, first non-comment line is treated as header
        delimiter: Column delimiter (default: ',')
        comment_char: Character for comment lines (default: '#')
        validate: If True, validate data before creating hull
        metadata: Optional metadata dictionary to use/override

    Returns:
        KayakHull object with loaded geometry

    Raises:
        DataLoadError: If file cannot be loaded or data is invalid
        FileNotFoundError: If file doesn't exist
        ValueError: If format_type is not recognized

    Example:
        >>> hull = load_hull_from_csv('data/my_kayak.csv', format_type='xyz')
        >>> len(hull.get_stations())
        5
    """
    filepath = Path(filepath)

    # Check file exists
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    # Validate format type
    if format_type not in CSV_FORMATS:
        raise ValueError(
            f"Unknown format_type '{format_type}'. "
            f"Must be one of: {', '.join(CSV_FORMATS.keys())}"
        )

    # Read file and separate comments from data
    comment_lines = []
    data_lines = []

    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith(comment_char):
                    comment_lines.append(line)
                elif line:  # Non-empty, non-comment line
                    data_lines.append(line)
    except Exception as e:
        raise DataLoadError(f"Error reading {filepath}: {e}")

    if not data_lines:
        raise DataLoadError(f"No data found in {filepath}")

    # Extract metadata from comments
    csv_metadata = extract_metadata_from_comments(comment_lines)

    # Merge with provided metadata (provided metadata takes precedence)
    if metadata:
        csv_metadata.update(metadata)

    # Apply defaults
    complete_metadata = apply_metadata_defaults(csv_metadata)

    # Parse CSV data
    try:
        reader = csv.reader(data_lines, delimiter=delimiter)
        rows = list(reader)
    except Exception as e:
        raise DataLoadError(f"Error parsing CSV in {filepath}: {e}")

    # Handle header
    if has_header and rows:
        header = rows[0]
        rows = rows[1:]
    else:
        header = CSV_FORMATS[format_type]["columns"]

    if not rows:
        raise DataLoadError(f"No data rows found in {filepath}")

    # Convert to numpy array
    try:
        data_array = np.array(rows, dtype=float)
    except (TypeError, ValueError) as e:
        raise DataLoadError(f"Could not convert CSV data to numbers: {e}")

    # Validate CSV data
    if validate:
        is_valid, errors = validate_csv_data(data_array, header, format_type)
        if not is_valid:
            error_msg = f"Invalid CSV data in {filepath}:\n" + "\n".join(
                f"  - {err}" for err in errors
            )
            raise DataLoadError(error_msg)

    # Parse based on format
    if format_type == "xyz":
        points_data = _parse_xyz_format(data_array)
    elif format_type == "station_yz":
        points_data = _parse_station_yz_format(data_array)
    else:
        raise ValueError(f"Unhandled format_type: {format_type}")

    # Create hull data structure
    hull_data = {"metadata": complete_metadata, "profiles": points_data}

    # Validate hull data
    if validate:
        is_valid, errors = validate_hull_data(hull_data)
        if not is_valid:
            error_msg = f"Invalid hull data in {filepath}:\n" + "\n".join(
                f"  - {err}" for err in errors
            )
            raise DataLoadError(error_msg)

    # Create hull
    try:
        hull = _create_hull_from_dict(hull_data)
    except Exception as e:
        raise DataLoadError(f"Error creating hull from {filepath}: {e}")

    return hull


def _parse_xyz_format(data_array: np.ndarray) -> List[Dict[str, Any]]:
    """
    Parse CSV data in xyz format (x, y, z columns).

    Groups points by unique x values (stations).

    Args:
        data_array: Nx3 numpy array of (x, y, z) coordinates

    Returns:
        List of profile dictionaries
    """
    # Group by x coordinate (station)
    unique_stations = np.unique(data_array[:, 0])
    unique_stations.sort()

    profiles = []
    for station in unique_stations:
        # Find all points at this station
        mask = np.isclose(data_array[:, 0], station)
        station_points = data_array[mask]

        # Create point dictionaries
        points = [
            {"x": float(pt[0]), "y": float(pt[1]), "z": float(pt[2])} for pt in station_points
        ]

        profiles.append({"station": float(station), "points": points})

    return profiles


def _parse_station_yz_format(data_array: np.ndarray) -> List[Dict[str, Any]]:
    """
    Parse CSV data in station_yz format (station, y, z columns).

    The x coordinate for each point is set equal to the station value.

    Args:
        data_array: Nx3 numpy array of (station, y, z) coordinates

    Returns:
        List of profile dictionaries
    """
    # Group by station
    unique_stations = np.unique(data_array[:, 0])
    unique_stations.sort()

    profiles = []
    for station in unique_stations:
        # Find all points at this station
        mask = np.isclose(data_array[:, 0], station)
        station_data = data_array[mask]

        # Create point dictionaries (x = station)
        points = [
            {"x": float(station), "y": float(pt[1]), "z": float(pt[2])} for pt in station_data
        ]

        profiles.append({"station": float(station), "points": points})

    return profiles


def _create_hull_from_dict(data: Dict[str, Any]) -> KayakHull:
    """
    Create a KayakHull object from a validated data dictionary.

    Automatically creates intermediate profiles between end profiles and
    bow/stern apex points if they are defined.

    Args:
        data: Dictionary with 'metadata' and 'profiles' keys

    Returns:
        KayakHull object with interpolated bow/stern profiles if apex points defined
    """
    # Extract metadata
    metadata = data.get("metadata", {})
    coordinate_system = metadata.get("coordinate_system", "bow_origin")

    # Extract bow and stern apex points if present
    bow_apex = None
    stern_apex = None

    if "bow" in data:
        bow_data = data["bow"]
        bow_apex = Point3D(float(bow_data["x"]), float(bow_data["y"]), float(bow_data["z"]))

    if "stern" in data:
        stern_data = data["stern"]
        stern_apex = Point3D(float(stern_data["x"]), float(stern_data["y"]), float(stern_data["z"]))

    # Create hull with coordinate system and apex points
    hull = KayakHull(
        coordinate_system=coordinate_system,
        bow_apex=bow_apex,
        stern_apex=stern_apex,
    )

    # Store metadata as attributes (if needed in future)
    hull.metadata = metadata

    # Add profiles
    for profile_data in data["profiles"]:
        profile = _create_profile_from_dict(profile_data)
        hull.add_profile(profile)

    # Automatically create interpolated profiles to bow/stern if apex points are defined
    # We create end profiles that taper appropriately and use longitudinal interpolation
    if bow_apex is not None and len(hull.profiles) > 0:
        stations = sorted(hull.get_stations())

        # Find the profile closest to the bow apex
        if coordinate_system == "bow_origin":
            closest_station = min(stations)
        elif coordinate_system == "stern_origin":
            closest_station = max(stations)
        else:
            closest_station = min(stations, key=lambda s: abs(s - bow_apex.x))

        # Only interpolate if bow apex is not at the same station
        if abs(closest_station - bow_apex.x) > 1e-6:
            closest_profile = hull.get_profile(closest_station, interpolate=False)

            # Create end profile that matches the structure of the closest profile
            # but scaled down in beam while maintaining the depth (z) characteristics
            closest_points = sorted(closest_profile.points, key=lambda p: p.y)

            # Calculate scale factor for beam (15% of original)
            beam_scale = 0.15

            # Create scaled points maintaining z-structure
            end_points = []
            for pt in closest_points:
                # Scale y-coordinate (transverse)
                scaled_y = pt.y * beam_scale
                # Keep z-coordinate the same (depth profile stays similar)
                end_points.append(Point3D(bow_apex.x, scaled_y, pt.z))

            bow_end_profile = Profile(bow_apex.x, end_points)

            # Create intermediate stations
            distance = abs(bow_apex.x - closest_station)
            num_intermediate = max(2, int(distance / 0.25))

            intermediate_stations = np.linspace(bow_apex.x, closest_station, num_intermediate + 2)[
                1:-1
            ]

            # Manually create interpolated profiles that properly expand from narrow to wide
            for target_station in intermediate_stations:
                # Calculate interpolation factor
                # t = 0 at bow (narrow), t = 1 at closest_station (wide)
                t = abs(target_station - bow_apex.x) / abs(closest_station - bow_apex.x)

                # Interpolate each point: scale y-coordinates, interpolate z-coordinates
                interp_points = []
                for pt in closest_points:
                    # Interpolate y: from narrow (beam_scale * y) to wide (y)
                    y_interp = pt.y * (beam_scale + t * (1 - beam_scale))
                    # Interpolate z
                    z_interp = pt.z
                    interp_points.append(Point3D(target_station, y_interp, z_interp))

                hull.add_profile(Profile(target_station, interp_points))

            # Add the bow end profile
            hull.add_profile(bow_end_profile)

    if stern_apex is not None and len(hull.profiles) > 0:
        stations = sorted(hull.get_stations())

        # Find the profile closest to the stern apex
        if coordinate_system == "bow_origin":
            closest_station = max([s for s in stations if s < stern_apex.x])
        elif coordinate_system == "stern_origin":
            closest_station = min([s for s in stations if s > stern_apex.x])
        else:
            closest_station = min(stations, key=lambda s: abs(s - stern_apex.x))

        # Only interpolate if stern apex is not at the same station
        if abs(closest_station - stern_apex.x) > 1e-6:
            closest_profile = hull.get_profile(closest_station, interpolate=False)

            # Create end profile that matches the structure of the closest profile
            # but scaled down in beam while maintaining the depth (z) characteristics
            closest_points = sorted(closest_profile.points, key=lambda p: p.y)

            # Calculate scale factor for beam (15% of original)
            beam_scale = 0.15

            # Create scaled points maintaining z-structure
            end_points = []
            for pt in closest_points:
                # Scale y-coordinate (transverse)
                scaled_y = pt.y * beam_scale
                # Keep z-coordinate the same (depth profile stays similar)
                end_points.append(Point3D(stern_apex.x, scaled_y, pt.z))

            stern_end_profile = Profile(stern_apex.x, end_points)

            # Create intermediate stations
            distance = abs(stern_apex.x - closest_station)
            num_intermediate = max(2, int(distance / 0.25))

            intermediate_stations = np.linspace(
                closest_station, stern_apex.x, num_intermediate + 2
            )[1:-1]

            # Manually create interpolated profiles that properly expand from wide to narrow
            for target_station in intermediate_stations:
                # Calculate interpolation factor
                # t = 0 at closest_station (wide), t = 1 at stern (narrow)
                t = abs(target_station - closest_station) / abs(stern_apex.x - closest_station)

                # Interpolate each point: scale y-coordinates from wide to narrow
                interp_points = []
                for pt in closest_points:
                    # Interpolate y: from wide (y) to narrow (beam_scale * y)
                    y_interp = pt.y * (1 - t * (1 - beam_scale))
                    # Keep z the same
                    z_interp = pt.z
                    interp_points.append(Point3D(target_station, y_interp, z_interp))

                hull.add_profile(Profile(target_station, interp_points))

            # Add the stern end profile
            hull.add_profile(stern_end_profile)

    return hull


def _create_profile_from_dict(profile_data: Dict[str, Any]) -> Profile:
    """
    Create a Profile object from a dictionary.

    Args:
        profile_data: Dictionary with 'station' and 'points' keys

    Returns:
        Profile object
    """
    station = float(profile_data["station"])
    points = [
        Point3D(float(pt["x"]), float(pt["y"]), float(pt["z"])) for pt in profile_data["points"]
    ]

    return Profile(station, points)


def save_hull_to_json(
    hull: KayakHull,
    filepath: Union[str, Path],
    metadata: Optional[Dict[str, Any]] = None,
    indent: int = 2,
) -> None:
    """
    Save a KayakHull to a JSON file.

    Args:
        hull: KayakHull object to save
        filepath: Output file path
        metadata: Optional metadata to include
        indent: JSON indentation level

    Example:
        >>> hull = KayakHull()
        >>> # ... add profiles to hull ...
        >>> save_hull_to_json(hull, 'output.json', metadata={'name': 'MyKayak'})
    """
    filepath = Path(filepath)

    # Start with hull's existing metadata or empty dict
    complete_metadata = dict(hull.metadata) if hull.metadata else {}

    # Update with provided metadata
    if metadata:
        complete_metadata.update(metadata)

    # Ensure coordinate_system is in metadata
    if "coordinate_system" not in complete_metadata:
        complete_metadata["coordinate_system"] = hull.coordinate_system

    # Apply defaults
    complete_metadata = apply_metadata_defaults(complete_metadata)

    # Build data structure
    hull_data = {"metadata": complete_metadata, "profiles": []}

    # Add bow apex if present
    if hull.bow_apex is not None:
        hull_data["bow"] = {"x": hull.bow_apex.x, "y": hull.bow_apex.y, "z": hull.bow_apex.z}

    # Add stern apex if present
    if hull.stern_apex is not None:
        hull_data["stern"] = {
            "x": hull.stern_apex.x,
            "y": hull.stern_apex.y,
            "z": hull.stern_apex.z,
        }

    # Add profiles
    for station in hull.get_stations():
        profile = hull.get_profile(station)
        profile_data = {
            "station": station,
            "points": [{"x": pt.x, "y": pt.y, "z": pt.z} for pt in profile.points],
        }
        hull_data["profiles"].append(profile_data)

    # Write to file
    try:
        with open(filepath, "w") as f:
            json.dump(hull_data, f, indent=indent)
    except Exception as e:
        raise DataLoadError(f"Error writing to {filepath}: {e}")


def save_hull_to_csv(
    hull: KayakHull,
    filepath: Union[str, Path],
    format_type: str = "xyz",
    metadata: Optional[Dict[str, Any]] = None,
    include_header: bool = True,
) -> None:
    """
    Save a KayakHull to a CSV file.

    Args:
        hull: KayakHull object to save
        filepath: Output file path
        format_type: 'xyz' or 'station_yz'
        metadata: Optional metadata to include as comments
        include_header: If True, include column header

    Example:
        >>> hull = KayakHull()
        >>> # ... add profiles to hull ...
        >>> save_hull_to_csv(hull, 'output.csv', format_type='xyz')
    """
    filepath = Path(filepath)

    if format_type not in CSV_FORMATS:
        raise ValueError(f"Unknown format_type '{format_type}'")

    # Collect all points
    points = []
    for station in hull.get_stations():
        profile = hull.get_profile(station)
        for pt in profile.points:
            if format_type == "xyz":
                points.append([pt.x, pt.y, pt.z])
            elif format_type == "station_yz":
                points.append([station, pt.y, pt.z])

    # Write to file
    try:
        with open(filepath, "w", newline="") as f:
            # Write metadata as comments
            if metadata:
                for key, value in metadata.items():
                    if value is not None:
                        f.write(f"# {key.replace('_', ' ').title()}: {value}\n")

            writer = csv.writer(f)

            # Write header
            if include_header:
                writer.writerow(CSV_FORMATS[format_type]["columns"])

            # Write data
            writer.writerows(points)
    except Exception as e:
        raise DataLoadError(f"Error writing to {filepath}: {e}")
