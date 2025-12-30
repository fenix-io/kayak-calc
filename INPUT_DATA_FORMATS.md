# Kayak Hull Data Formats

This document describes the supported file formats for loading and saving kayak hull geometry in the kayak calculation tool.

## Table of Contents

- [Overview](#overview)
- [JSON Format](#json-format)
- [CSV Format](#csv-format)
- [Metadata Fields](#metadata-fields)
- [Coordinate System](#coordinate-system)
- [Examples](#examples)
- [Validation Rules](#validation-rules)

---

## Overview

The kayak calculation tool supports two primary file formats for hull geometry:

1. **JSON** - Complete format with metadata and structured profile data
2. **CSV** - Simplified tabular format with optional comment-based metadata

Both formats can represent the same hull geometry and can be converted between each other using the provided tools.

### Supported File Extensions

- `.json` - JSON format
- `.csv` - CSV format (comma-separated values)

---

## JSON Format

The JSON format provides a complete, structured representation of the kayak hull with explicit metadata and profile organization.

### Structure

```json
{
  "metadata": {
    "name": "string (optional)",
    "description": "string (optional)",
    "units": "string (required)",
    "coordinate_system": "string (required)",
    "water_density": number (required),
    "length": number (optional),
    "beam": number (optional)
  },
  "profiles": [
    {
      "station": number,
      "points": [
        {
          "x": number,
          "y": number,
          "z": number
        }
      ]
    }
  ]
}
```

### Field Descriptions

#### Metadata Section

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | No | - | Descriptive name for the kayak hull |
| `description` | string | No | - | Detailed description of the hull |
| `units` | string | Yes | "m" | Length unit: `m`, `cm`, `mm`, `ft`, or `in` |
| `coordinate_system` | string | Yes | "centerline_origin" | Coordinate reference: `centerline_origin`, `bow_origin`, `stern_origin`, or `midship_origin` |
| `water_density` | number | Yes | 1025.0 | Water density in kg/m³ (1025 for seawater, 1000 for freshwater) |
| `length` | number | No | - | Overall hull length in specified units |
| `beam` | number | No | - | Maximum hull width in specified units |

#### Profiles Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `station` | number | Yes | Longitudinal position along the hull (x-coordinate) |
| `points` | array | Yes | Array of 3D points defining the cross-section at this station |

#### Point Structure

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `x` | number | Yes | Longitudinal coordinate (must match station value) |
| `y` | number | Yes | Transverse coordinate (port=negative, starboard=positive) |
| `z` | number | Yes | Vertical coordinate (down=negative, up=positive) |

### Complete JSON Example

```json
{
  "metadata": {
    "name": "Sea Kayak Pro",
    "description": "High-performance sea kayak with excellent stability",
    "units": "m",
    "coordinate_system": "centerline_origin",
    "water_density": 1025.0,
    "length": 5.2,
    "beam": 0.55
  },
  "profiles": [
    {
      "station": 0.0,
      "points": [
        {"x": 0.0, "y": 0.0, "z": 0.45},
        {"x": 0.0, "y": -0.15, "z": 0.25},
        {"x": 0.0, "y": 0.15, "z": 0.25},
        {"x": 0.0, "y": -0.12, "z": 0.0},
        {"x": 0.0, "y": 0.12, "z": 0.0},
        {"x": 0.0, "y": -0.08, "z": -0.15},
        {"x": 0.0, "y": 0.08, "z": -0.15}
      ]
    },
    {
      "station": 2.6,
      "points": [
        {"x": 2.6, "y": 0.0, "z": 0.30},
        {"x": 2.6, "y": -0.27, "z": 0.10},
        {"x": 2.6, "y": 0.27, "z": 0.10},
        {"x": 2.6, "y": -0.275, "z": 0.0},
        {"x": 2.6, "y": 0.275, "z": 0.0},
        {"x": 2.6, "y": -0.265, "z": -0.22},
        {"x": 2.6, "y": 0.265, "z": -0.22}
      ]
    },
    {
      "station": 5.2,
      "points": [
        {"x": 5.2, "y": 0.0, "z": 0.45},
        {"x": 5.2, "y": -0.15, "z": 0.25},
        {"x": 5.2, "y": 0.15, "z": 0.25},
        {"x": 5.2, "y": -0.12, "z": 0.0},
        {"x": 5.2, "y": 0.12, "z": 0.0},
        {"x": 5.2, "y": -0.08, "z": -0.15},
        {"x": 5.2, "y": 0.08, "z": -0.15}
      ]
    }
  ]
}
```

### Minimal JSON Example

```json
{
  "profiles": [
    {
      "station": 0.0,
      "points": [
        {"x": 0.0, "y": 0.0, "z": 1.0},
        {"x": 0.0, "y": 0.5, "z": 0.5},
        {"x": 0.0, "y": -0.5, "z": 0.5}
      ]
    },
    {
      "station": 1.0,
      "points": [
        {"x": 1.0, "y": 0.0, "z": 1.0},
        {"x": 1.0, "y": 0.5, "z": 0.5},
        {"x": 1.0, "y": -0.5, "z": 0.5}
      ]
    }
  ]
}
```

*Note: If metadata is omitted, default values will be applied automatically.*

---

## CSV Format

The CSV format provides a simplified, tabular representation suitable for spreadsheet applications and manual data entry.

### Two Supported Formats

#### Format A: XYZ (Recommended)

Three columns: `x`, `y`, `z`

- The `x` coordinate serves as the station identifier
- Points are automatically grouped by unique `x` values
- Most intuitive for direct coordinate entry

#### Format B: Station-YZ

Three columns: `station`, `y`, `z`

- Explicit station column separate from coordinates
- The `x` coordinate of each point is set equal to the station value
- Useful when station values need to be distinct from x-coordinates

### CSV Structure

```
# Comment lines start with # (optional, can contain metadata)
# Key: Value format is recognized for metadata extraction
column1,column2,column3
value1,value2,value3
...
```

### CSV Format A: XYZ Example

```csv
# Name: Sea Kayak Pro
# Description: High-performance sea kayak
# Units: m
# Coordinate system: centerline_origin
# Water density: 1025.0
x,y,z
0.0,0.0,0.45
0.0,-0.15,0.25
0.0,0.15,0.25
0.0,-0.12,0.0
0.0,0.12,0.0
2.6,0.0,0.30
2.6,-0.27,0.10
2.6,0.27,0.10
2.6,-0.275,0.0
2.6,0.275,0.0
5.2,0.0,0.45
5.2,-0.15,0.25
5.2,0.15,0.25
```

### CSV Format B: Station-YZ Example

```csv
# Units: m
# Coordinate system: centerline_origin
station,y,z
0.0,0.0,0.45
0.0,-0.15,0.25
0.0,0.15,0.25
2.6,0.0,0.30
2.6,-0.27,0.10
2.6,0.27,0.10
5.2,0.0,0.45
5.2,-0.15,0.25
5.2,0.15,0.25
```

### CSV Metadata via Comments

Metadata can be specified in comment lines using the format `# Key: Value`:

```csv
# Name: My Kayak
# Description: Custom design
# Units: ft
# Coordinate system: centerline_origin
# Water density: 1000.0
# Length: 17.5
# Beam: 2.0
```

**Recognized metadata keys in comments:**
- `Name` → name
- `Description` → description
- `Units` → units
- `Coordinate system` → coordinate_system
- `Water density` → water_density
- `Length` → length
- `Beam` → beam

*Note: Keys are case-insensitive and spaces are converted to underscores.*

### CSV Options

When loading CSV files programmatically, you can specify:

- `format_type`: `'xyz'` or `'station_yz'`
- `has_header`: Whether first non-comment line is a header (default: `True`)
- `delimiter`: Column separator (default: `','`)
- `comment_char`: Comment line prefix (default: `'#'`)

---

## Metadata Fields

### Required Metadata

These fields must be present (or defaults will be applied):

| Field | Default Value | Description |
|-------|---------------|-------------|
| `units` | `"m"` | Length measurement unit |
| `coordinate_system` | `"centerline_origin"` | Origin reference point |
| `water_density` | `1025.0` | Water density in kg/m³ |

### Optional Metadata

| Field | Description |
|-------|-------------|
| `name` | Hull name/identifier |
| `description` | Detailed description |
| `length` | Overall hull length |
| `beam` | Maximum hull width |

### Units

**Supported length units:**
- `m` - Meters (SI standard)
- `cm` - Centimeters
- `mm` - Millimeters
- `ft` - Feet
- `in` - Inches

### Coordinate Systems

**Supported coordinate system origins:**
- `centerline_origin` - Origin at centerline (y=0), arbitrary longitudinal position
- `bow_origin` - Origin at bow (forward end)
- `stern_origin` - Origin at stern (aft end)
- `midship_origin` - Origin at midship (center)

### Water Density

**Common values:**
- `1025.0` kg/m³ - Seawater (default)
- `1000.0` kg/m³ - Freshwater
- Custom values can be specified for specific conditions

---

## Coordinate System

### Axis Orientation

The kayak calculation tool uses a right-handed coordinate system:

```
        Z (up)
        ↑
        |
        |
        o----→ X (longitudinal, forward)
       /
      /
     ↓
    Y (transverse)
```

**Conventions:**
- **X-axis**: Longitudinal direction (along kayak length)
  - Positive: Forward/bow direction
  - Increases from bow to stern (or vice versa, depending on origin)

- **Y-axis**: Transverse direction (across kayak width)
  - `y = 0`: Centerline plane (plane of symmetry)
  - Positive (`y > 0`): Starboard (right side when facing forward)
  - Negative (`y < 0`): Port (left side when facing forward)

- **Z-axis**: Vertical direction
  - Positive (`z > 0`): Upward
  - Negative (`z < 0`): Downward
  - `z = 0`: Waterline or reference plane

### Profile Organization

- **Profile**: A transverse cross-section at a specific longitudinal position (station)
- **Station**: The x-coordinate (longitudinal position) of a profile
- **Points**: 3D coordinates defining the hull surface at that cross-section

### Symmetry

The hull is typically assumed to be symmetric about the centerline (y=0):
- For each point at `(x, y, z)` with `y > 0`, there should be a corresponding point at `(x, -y, z)`
- Points exactly on the centerline have `y = 0`

### Profile Point Ordering

**Critical for accurate calculations:** Points within each profile must be ordered consistently.

**Recommended ordering (port → keel → starboard):**

1. Start at **port side** (y < 0) at deck/waterline level
2. Progress **downward** along port side  
3. Continue through **keel** (y = 0, lowest point)
4. Progress **upward** along starboard side
5. End at **starboard side** (y > 0) at deck/waterline level

**Example point sequence for a kayak profile:**

```
Point 0: Port deck edge      (x, y=-0.30, z=0.20)   ← Start here
Point 1: Port chine           (x, y=-0.28, z=0.00)   ↓
Point 2: Port bilge           (x, y=-0.25, z=-0.15)  ↓
Point 3: Keel (centerline)    (x, y=0.00,  z=-0.20)  ← Lowest point
Point 4: Starboard bilge      (x, y=0.25,  z=-0.15)  ↑
Point 5: Starboard chine      (x, y=0.28,  z=0.00)   ↑
Point 6: Starboard deck edge  (x, y=0.30,  z=0.20)   ← End here
```

**Why consistent ordering matters:**

- Ensures correct cross-sectional area calculations (shoelace formula)
- Maintains proper waterline intersection detection
- Enables accurate longitudinal interpolation between profiles
- Prevents surface normal reversals
- Avoids twisted interpolated sections

**Important:** Use the **same traversal direction** for **ALL** profiles. Mixing directions (e.g., port→starboard on one profile, starboard→port on another) will cause calculation errors.

### Bow and Stern Positions

**Important:** Modern hull files do **not** require explicit `bow` or `stern` entries.

**How bow/stern are determined:**

- **Bow**: Automatically derived from the **first profile** (lowest x-coordinate station)
- **Stern**: Automatically derived from the **last profile** (highest x-coordinate station)
- The software extracts bow/stern positions from profile endpoints

**Example:**

```json
{
  "profiles": [
    {"station": 0.0, "points": [...]},    ← First profile = BOW
    {"station": 2.5, "points": [...]},    ← Middle profiles
    {"station": 5.0, "points": [...]}     ← Last profile = STERN
  ]
}
```

After loading, bow and stern are automatically available via hull attributes.

**For tapered bow/stern:**
- First/last profiles should have points that converge toward centerline
- This naturally defines the tapered end geometry
- No special apex point needed

**Benefits of this approach:**
- Simpler data format (fewer fields to specify)
- Eliminates potential inconsistencies
- Profiles already contain all necessary geometric information

---

## Examples

### Example 1: Simple Box Hull (JSON)

```json
{
  "metadata": {
    "name": "Simple Box Kayak",
    "units": "m",
    "coordinate_system": "centerline_origin",
    "water_density": 1025.0
  },
  "profiles": [
    {
      "station": 0.0,
      "points": [
        {"x": 0.0, "y": 0.0, "z": 0.5},
        {"x": 0.0, "y": -0.3, "z": 0.3},
        {"x": 0.0, "y": 0.3, "z": 0.3},
        {"x": 0.0, "y": -0.3, "z": -0.1},
        {"x": 0.0, "y": 0.3, "z": -0.1}
      ]
    },
    {
      "station": 5.0,
      "points": [
        {"x": 5.0, "y": 0.0, "z": 0.5},
        {"x": 5.0, "y": -0.3, "z": 0.3},
        {"x": 5.0, "y": 0.3, "z": 0.3},
        {"x": 5.0, "y": -0.3, "z": -0.1},
        {"x": 5.0, "y": 0.3, "z": -0.1}
      ]
    }
  ]
}
```

### Example 2: Simple Box Hull (CSV)

```csv
# Name: Simple Box Kayak
# Units: m
# Coordinate system: centerline_origin
# Water density: 1025.0
x,y,z
0.0,0.0,0.5
0.0,-0.3,0.3
0.0,0.3,0.3
0.0,-0.3,-0.1
0.0,0.3,-0.1
5.0,0.0,0.5
5.0,-0.3,0.3
5.0,0.3,0.3
5.0,-0.3,-0.1
5.0,0.3,-0.1
```

### Example 3: CSV with Different Units

```csv
# Units: ft
# Water density: 1000.0
x,y,z
0.0,0.0,1.5
0.0,-1.0,1.0
0.0,1.0,1.0
17.0,0.0,1.5
17.0,-1.0,1.0
17.0,1.0,1.0
```

---

## Validation Rules

### Required Constraints

1. **Minimum profiles**: At least 2 profiles required
2. **Minimum points per profile**: At least 3 points required
3. **X-coordinate consistency**: All points in a profile must have the same x-coordinate (equal to station)
4. **Unique stations**: Each profile must have a unique station value
5. **Finite values**: All coordinates must be finite numbers (no NaN or Inf)

### Recommended Best Practices

1. **Symmetry**: Include symmetric port/starboard points
2. **Centerline points**: Include points on centerline (y=0) for accuracy
3. **Station spacing**: Use reasonable spacing between stations
4. **Point density**: More points in areas of high curvature
5. **Waterline coverage**: Include points above and below anticipated waterlines
6. **Ordering**: Order stations from bow to stern (or vice versa) consistently

### Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Missing required field" | Required metadata or data field omitted | Add missing field or let defaults apply |
| "x-coordinate doesn't match station" | Point x ≠ profile station | Ensure all points have x = station |
| "At least 3 points required" | Profile has < 3 points | Add more points to define profile |
| "At least 2 profiles required" | Hull has < 2 profiles | Add more profiles |
| "Duplicate stations found" | Multiple profiles at same station | Ensure each profile has unique station |
| "Invalid unit" | Unrecognized unit string | Use: m, cm, mm, ft, or in |
| "NaN or Inf value" | Non-finite number in data | Check for calculation errors in input |

---

## Loading and Saving

### Python API Examples

#### Load from JSON

```python
from src.io import load_hull_from_json

hull = load_hull_from_json('my_kayak.json')
print(f"Loaded {hull.num_profiles} profiles")
```

#### Load from CSV

```python
from src.io import load_hull_from_csv

# XYZ format
hull = load_hull_from_csv('my_kayak.csv', format_type='xyz')

# Station-YZ format
hull = load_hull_from_csv('my_kayak.csv', format_type='station_yz')
```

#### Save to JSON

```python
from src.io import save_hull_to_json

save_hull_to_json(
    hull,
    'output.json',
    metadata={'name': 'My Kayak', 'description': 'Modified design'}
)
```

#### Save to CSV

```python
from src.io import save_hull_to_csv

# XYZ format
save_hull_to_csv(hull, 'output.csv', format_type='xyz')

# Station-YZ format
save_hull_to_csv(hull, 'output.csv', format_type='station_yz')
```

### Command-Line Usage (Future)

*Note: Command-line interface not yet implemented*

```bash
# Convert CSV to JSON
kayak-calc convert input.csv output.json

# Convert JSON to CSV
kayak-calc convert input.json output.csv --format xyz

# Validate file
kayak-calc validate input.json
```

---

## Converting Between Formats

Both formats represent the same data and can be converted losslessly:

### JSON → CSV

```python
from src.io import load_hull_from_json, save_hull_to_csv

hull = load_hull_from_json('input.json')
save_hull_to_csv(hull, 'output.csv', format_type='xyz')
```

### CSV → JSON

```python
from src.io import load_hull_from_csv, save_hull_to_json

hull = load_hull_from_csv('input.csv', format_type='xyz')
save_hull_to_json(hull, 'output.json', metadata={'name': 'Converted Hull'})
```

---

## Additional Resources

- **Sample Files**: See `data/` directory for example hull geometries
- **Examples**: See `examples/data_input_examples.py` for usage examples
- **API Documentation**: See module docstrings in `src/io/`
- **Implementation Details**: See `docs/PHASE7_TASK7.1_SUMMARY.md`

---

## Version History

- **v1.0** (2025-12-25): Initial data format specification
  - JSON format support
  - CSV format support (xyz and station_yz)
  - Metadata handling
  - Validation system

---

## Support

For questions or issues with data formats:
1. Check sample files in `data/` directory
2. Review examples in `examples/data_input_examples.py`
3. Run validation: `validate_hull_data(data)`
4. Check error messages for specific issues
