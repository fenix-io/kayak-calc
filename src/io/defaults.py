"""
Default metadata values and metadata handling functions.

This module provides functions for managing default metadata values and
applying them to hull geometry data.
"""

from typing import Dict, Any, Optional
from copy import deepcopy
from ..config import WATER_DENSITY, LENGTH_UNIT


# Default metadata values
DEFAULT_METADATA = {
    'units': LENGTH_UNIT,
    'coordinate_system': 'centerline_origin',
    'water_density': WATER_DENSITY,
}

# Required metadata fields (these must be present or have defaults)
REQUIRED_METADATA = ['units', 'coordinate_system', 'water_density']

# Optional metadata fields (can be None/missing)
OPTIONAL_METADATA = ['name', 'description', 'length', 'beam']


def get_default_metadata() -> Dict[str, Any]:
    """
    Get a dictionary of default metadata values.
    
    Returns:
        Dictionary with default metadata values
        
    Example:
        >>> defaults = get_default_metadata()
        >>> defaults['units']
        'm'
        >>> defaults['water_density']
        1025.0
    """
    return deepcopy(DEFAULT_METADATA)


def apply_metadata_defaults(metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Apply default values to metadata, filling in missing fields.
    
    User-provided values take precedence over defaults.
    
    Args:
        metadata: User-provided metadata dictionary (can be None or incomplete)
        
    Returns:
        Complete metadata dictionary with defaults applied
        
    Example:
        >>> user_meta = {'name': 'MyKayak', 'units': 'ft'}
        >>> complete_meta = apply_metadata_defaults(user_meta)
        >>> complete_meta['name']
        'MyKayak'
        >>> complete_meta['units']
        'ft'
        >>> complete_meta['coordinate_system']
        'centerline_origin'
    """
    # Start with defaults
    result = get_default_metadata()
    
    # Override with user-provided values
    if metadata is not None:
        for key, value in metadata.items():
            result[key] = value
    
    return result


def validate_metadata_completeness(metadata: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Check if metadata has all required fields.
    
    Args:
        metadata: Metadata dictionary to validate
        
    Returns:
        Tuple of (is_complete, missing_fields)
        - is_complete: True if all required fields present
        - missing_fields: List of missing required field names
        
    Example:
        >>> meta = {'units': 'm'}
        >>> is_complete, missing = validate_metadata_completeness(meta)
        >>> is_complete
        False
        >>> 'coordinate_system' in missing
        True
    """
    missing = []
    
    for field in REQUIRED_METADATA:
        if field not in metadata or metadata[field] is None:
            missing.append(field)
    
    return (len(missing) == 0, missing)


def create_metadata_template(include_optional: bool = True) -> Dict[str, Any]:
    """
    Create a metadata template with all fields and example values.
    
    Useful for generating example files or documentation.
    
    Args:
        include_optional: If True, include optional fields with None values
        
    Returns:
        Template metadata dictionary
        
    Example:
        >>> template = create_metadata_template()
        >>> 'name' in template
        True
        >>> 'units' in template
        True
    """
    template = get_default_metadata()
    
    if include_optional:
        template['name'] = 'Kayak Name'
        template['description'] = 'Description of the kayak hull'
        template['length'] = None  # Overall length (m)
        template['beam'] = None    # Maximum beam/width (m)
    
    return template


def merge_metadata(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two metadata dictionaries, with override taking precedence.
    
    Args:
        base: Base metadata dictionary
        override: Override metadata dictionary (takes precedence)
        
    Returns:
        Merged metadata dictionary
        
    Example:
        >>> base = {'units': 'm', 'name': 'Base'}
        >>> override = {'name': 'Override', 'description': 'New'}
        >>> merged = merge_metadata(base, override)
        >>> merged['units']
        'm'
        >>> merged['name']
        'Override'
        >>> merged['description']
        'New'
    """
    result = deepcopy(base)
    result.update(override)
    return result


def extract_metadata_from_comments(comment_lines: list[str]) -> Dict[str, Any]:
    """
    Extract metadata from comment lines (e.g., from CSV files).
    
    Looks for patterns like:
    - # Units: m
    - # Coordinate system: centerline_origin
    - # Water density: 1025.0
    
    Args:
        comment_lines: List of comment line strings (with or without # prefix)
        
    Returns:
        Dictionary of extracted metadata
        
    Example:
        >>> comments = ['# Units: m', '# Water density: 1000']
        >>> meta = extract_metadata_from_comments(comments)
        >>> meta['units']
        'm'
        >>> meta['water_density']
        1000.0
    """
    metadata = {}
    
    for line in comment_lines:
        # Remove comment character and strip whitespace
        line = line.lstrip('#').strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Look for key: value pattern
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()
            
            # Try to convert to appropriate type
            if key in ['water_density', 'length', 'beam']:
                try:
                    metadata[key] = float(value)
                except ValueError:
                    metadata[key] = value
            else:
                metadata[key] = value
    
    return metadata


def format_metadata_for_display(metadata: Dict[str, Any]) -> str:
    """
    Format metadata dictionary as a human-readable string.
    
    Args:
        metadata: Metadata dictionary
        
    Returns:
        Formatted string representation
        
    Example:
        >>> meta = {'name': 'MyKayak', 'units': 'm', 'water_density': 1025.0}
        >>> print(format_metadata_for_display(meta))
        Metadata:
          name: MyKayak
          units: m
          water_density: 1025.0
    """
    lines = ['Metadata:']
    
    # Sort keys for consistent output
    for key in sorted(metadata.keys()):
        value = metadata[key]
        if value is not None:
            lines.append(f'  {key}: {value}')
    
    return '\n'.join(lines)
