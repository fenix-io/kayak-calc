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
from .validators import (
    validate_hull_data,
    validate_profile_data,
    validate_point_data,
    validate_csv_data,
)
from .defaults import apply_metadata_defaults, extract_metadata_from_comments
from .formats import CSV_FORMATS


class DataLoadError(Exception):
    """Exception raised when data loading fails."""
    pass


def load_hull_from_json(
    filepath: Union[str, Path],
    validate: bool = True
) -> KayakHull:
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
        with open(filepath, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise DataLoadError(f"Invalid JSON in {filepath}: {e}")
    except Exception as e:
        raise DataLoadError(f"Error reading {filepath}: {e}")
    
    # Validate data structure
    if validate:
        is_valid, errors = validate_hull_data(data)
        if not is_valid:
            error_msg = f"Invalid hull data in {filepath}:\n" + "\n".join(f"  - {err}" for err in errors)
            raise DataLoadError(error_msg)
    
    # Parse and create hull
    try:
        hull = _create_hull_from_dict(data)
    except Exception as e:
        raise DataLoadError(f"Error creating hull from {filepath}: {e}")
    
    return hull


def load_hull_from_csv(
    filepath: Union[str, Path],
    format_type: str = 'xyz',
    has_header: bool = True,
    delimiter: str = ',',
    comment_char: str = '#',
    validate: bool = True,
    metadata: Optional[Dict[str, Any]] = None
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
        with open(filepath, 'r') as f:
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
        header = CSV_FORMATS[format_type]['columns']
    
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
            error_msg = f"Invalid CSV data in {filepath}:\n" + "\n".join(f"  - {err}" for err in errors)
            raise DataLoadError(error_msg)
    
    # Parse based on format
    if format_type == 'xyz':
        points_data = _parse_xyz_format(data_array)
    elif format_type == 'station_yz':
        points_data = _parse_station_yz_format(data_array)
    else:
        raise ValueError(f"Unhandled format_type: {format_type}")
    
    # Create hull data structure
    hull_data = {
        'metadata': complete_metadata,
        'profiles': points_data
    }
    
    # Validate hull data
    if validate:
        is_valid, errors = validate_hull_data(hull_data)
        if not is_valid:
            error_msg = f"Invalid hull data in {filepath}:\n" + "\n".join(f"  - {err}" for err in errors)
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
            {
                'x': float(pt[0]),
                'y': float(pt[1]),
                'z': float(pt[2])
            }
            for pt in station_points
        ]
        
        profiles.append({
            'station': float(station),
            'points': points
        })
    
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
            {
                'x': float(station),
                'y': float(pt[1]),
                'z': float(pt[2])
            }
            for pt in station_data
        ]
        
        profiles.append({
            'station': float(station),
            'points': points
        })
    
    return profiles


def _create_hull_from_dict(data: Dict[str, Any]) -> KayakHull:
    """
    Create a KayakHull object from a validated data dictionary.
    
    Args:
        data: Dictionary with 'metadata' and 'profiles' keys
        
    Returns:
        KayakHull object
    """
    # Create hull
    hull = KayakHull()
    
    # Store metadata as attributes (if needed in future)
    if 'metadata' in data:
        hull.metadata = data['metadata']
    
    # Add profiles
    for profile_data in data['profiles']:
        profile = _create_profile_from_dict(profile_data)
        hull.add_profile(profile)
    
    return hull


def _create_profile_from_dict(profile_data: Dict[str, Any]) -> Profile:
    """
    Create a Profile object from a dictionary.
    
    Args:
        profile_data: Dictionary with 'station' and 'points' keys
        
    Returns:
        Profile object
    """
    station = float(profile_data['station'])
    points = [
        Point3D(
            float(pt['x']),
            float(pt['y']),
            float(pt['z'])
        )
        for pt in profile_data['points']
    ]
    
    return Profile(station, points)


def save_hull_to_json(
    hull: KayakHull,
    filepath: Union[str, Path],
    metadata: Optional[Dict[str, Any]] = None,
    indent: int = 2
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
    
    # Apply defaults to metadata
    complete_metadata = apply_metadata_defaults(metadata)
    
    # Build data structure
    hull_data = {
        'metadata': complete_metadata,
        'profiles': []
    }
    
    # Add profiles
    for station in hull.get_stations():
        profile = hull.get_profile(station)
        profile_data = {
            'station': station,
            'points': [
                {'x': pt.x, 'y': pt.y, 'z': pt.z}
                for pt in profile.points
            ]
        }
        hull_data['profiles'].append(profile_data)
    
    # Write to file
    try:
        with open(filepath, 'w') as f:
            json.dump(hull_data, f, indent=indent)
    except Exception as e:
        raise DataLoadError(f"Error writing to {filepath}: {e}")


def save_hull_to_csv(
    hull: KayakHull,
    filepath: Union[str, Path],
    format_type: str = 'xyz',
    metadata: Optional[Dict[str, Any]] = None,
    include_header: bool = True
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
            if format_type == 'xyz':
                points.append([pt.x, pt.y, pt.z])
            elif format_type == 'station_yz':
                points.append([station, pt.y, pt.z])
    
    # Write to file
    try:
        with open(filepath, 'w', newline='') as f:
            # Write metadata as comments
            if metadata:
                for key, value in metadata.items():
                    if value is not None:
                        f.write(f"# {key.replace('_', ' ').title()}: {value}\n")
            
            writer = csv.writer(f)
            
            # Write header
            if include_header:
                writer.writerow(CSV_FORMATS[format_type]['columns'])
            
            # Write data
            writer.writerows(points)
    except Exception as e:
        raise DataLoadError(f"Error writing to {filepath}: {e}")
