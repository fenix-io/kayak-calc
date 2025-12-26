"""
Data format specifications and constants for kayak hull data input/output.

This module defines the standard data formats supported by the kayak calculation
tool, including JSON and CSV format specifications.
"""

from typing import Dict, List, Any

# Supported file formats
SUPPORTED_FORMATS = ['json', 'csv']

# Metadata field names
METADATA_FIELDS = {
    'name': str,
    'description': str,
    'units': str,
    'coordinate_system': str,
    'water_density': float,
    'length': float,
    'beam': float,
}

# Recognized units
RECOGNIZED_LENGTH_UNITS = ['m', 'cm', 'mm', 'ft', 'in']

# Recognized coordinate systems
RECOGNIZED_COORD_SYSTEMS = [
    'centerline_origin',
    'bow_origin',
    'stern_origin',
    'midship_origin',
]

# Point field names
POINT_FIELDS = ['x', 'y', 'z']

# Profile field names  
PROFILE_FIELDS = ['station', 'points']

# Minimum requirements
MIN_POINTS_PER_PROFILE = 3
MIN_PROFILES_PER_HULL = 2


# JSON Format Specification
JSON_SCHEMA = {
    "type": "object",
    "required": ["profiles"],
    "properties": {
        "metadata": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "units": {"type": "string", "enum": RECOGNIZED_LENGTH_UNITS},
                "coordinate_system": {"type": "string", "enum": RECOGNIZED_COORD_SYSTEMS},
                "water_density": {"type": "number", "minimum": 0},
                "length": {"type": "number", "minimum": 0},
                "beam": {"type": "number", "minimum": 0},
            }
        },
        "profiles": {
            "type": "array",
            "minItems": MIN_PROFILES_PER_HULL,
            "items": {
                "type": "object",
                "required": ["station", "points"],
                "properties": {
                    "station": {"type": "number"},
                    "points": {
                        "type": "array",
                        "minItems": MIN_POINTS_PER_PROFILE,
                        "items": {
                            "type": "object",
                            "required": ["x", "y", "z"],
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"},
                                "z": {"type": "number"},
                            }
                        }
                    }
                }
            }
        }
    }
}


def get_json_example() -> Dict[str, Any]:
    """
    Get an example of a valid JSON hull definition.
    
    Returns:
        Dictionary representing a valid JSON hull file
    """
    return {
        "metadata": {
            "name": "Example Kayak",
            "description": "Simple kayak hull for demonstration",
            "units": "m",
            "coordinate_system": "centerline_origin",
            "water_density": 1025.0,
            "length": 5.0,
            "beam": 0.6
        },
        "profiles": [
            {
                "station": 0.0,
                "points": [
                    {"x": 0.0, "y": 0.0, "z": 0.5},
                    {"x": 0.0, "y": -0.3, "z": 0.2},
                    {"x": 0.0, "y": 0.3, "z": 0.2},
                    {"x": 0.0, "y": -0.3, "z": -0.1},
                    {"x": 0.0, "y": 0.3, "z": -0.1},
                ]
            },
            {
                "station": 2.5,
                "points": [
                    {"x": 2.5, "y": 0.0, "z": 0.3},
                    {"x": 2.5, "y": -0.3, "z": 0.1},
                    {"x": 2.5, "y": 0.3, "z": 0.1},
                    {"x": 2.5, "y": -0.3, "z": -0.2},
                    {"x": 2.5, "y": 0.3, "z": -0.2},
                ]
            },
            {
                "station": 5.0,
                "points": [
                    {"x": 5.0, "y": 0.0, "z": 0.5},
                    {"x": 5.0, "y": -0.3, "z": 0.2},
                    {"x": 5.0, "y": 0.3, "z": 0.2},
                    {"x": 5.0, "y": -0.3, "z": -0.1},
                    {"x": 5.0, "y": 0.3, "z": -0.1},
                ]
            }
        ]
    }


# CSV Format Specifications

# Format A: station, y, z (x coordinate derived from station)
CSV_FORMAT_A = {
    'name': 'station_yz',
    'columns': ['station', 'y', 'z'],
    'description': 'Station number, Y coordinate, Z coordinate (X derived from station)',
}

# Format B: x, y, z (station derived from x values)
CSV_FORMAT_B = {
    'name': 'xyz',
    'columns': ['x', 'y', 'z'],
    'description': 'X coordinate, Y coordinate, Z coordinate (station = X)',
}

CSV_FORMATS = {
    'station_yz': CSV_FORMAT_A,
    'xyz': CSV_FORMAT_B,
}


def get_csv_example(format_type: str = 'xyz') -> str:
    """
    Get an example CSV string for the specified format.
    
    Args:
        format_type: 'xyz' or 'station_yz'
        
    Returns:
        CSV string example
    """
    if format_type == 'xyz':
        return """# Example kayak hull geometry
# Units: meters
# Coordinate system: centerline_origin
x,y,z
0.0,0.0,0.5
0.0,-0.3,0.2
0.0,0.3,0.2
0.0,-0.3,-0.1
0.0,0.3,-0.1
2.5,0.0,0.3
2.5,-0.3,0.1
2.5,0.3,0.1
2.5,-0.3,-0.2
2.5,0.3,-0.2
5.0,0.0,0.5
5.0,-0.3,0.2
5.0,0.3,0.2
5.0,-0.3,-0.1
5.0,0.3,-0.1
"""
    elif format_type == 'station_yz':
        return """# Example kayak hull geometry
# Units: meters
# Coordinate system: centerline_origin
station,y,z
0.0,0.0,0.5
0.0,-0.3,0.2
0.0,0.3,0.2
0.0,-0.3,-0.1
0.0,0.3,-0.1
2.5,0.0,0.3
2.5,-0.3,0.1
2.5,0.3,0.1
2.5,-0.3,-0.2
2.5,0.3,-0.2
5.0,0.0,0.5
5.0,-0.3,0.2
5.0,0.3,0.2
5.0,-0.3,-0.1
5.0,0.3,-0.1
"""
    else:
        raise ValueError(f"Unknown CSV format type: {format_type}")
