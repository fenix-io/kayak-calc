# Phase 7, Task 7.1: Data Input - Implementation Plan

## Objective
Implement comprehensive data input functionality for loading kayak hull geometry from JSON and CSV file formats, including metadata defaults, data validation, and error handling.

## Current State Analysis

### Existing Infrastructure
- **Config module** (`src/config.py`): Contains basic configuration constants
- **Data structures**: 
  - `Point3D`: Represents 3D coordinates (x, y, z)
  - `Profile`: Transverse cross-section at a station with list of points
  - `KayakHull`: Container for profiles, with methods for adding/managing profiles
- **IO module** (`src/io/__init__.py`): Placeholder module, currently empty
- **Data directory**: Empty, needs sample data files

### Required Capabilities
1. Define metadata schema (units, coordinate system, etc.)
2. JSON format support for complete hull geometry
3. CSV format support for simplified point data
4. Data loading and parsing functions
5. Comprehensive data validation
6. Error handling with helpful messages
7. Sample data files for testing and examples

## Implementation Plan

### Step 1: Define Metadata Schema and Data Format Specification

**File**: `src/io/formats.py` (new)

Define the standard data format specifications:

1. **Metadata schema**:
   - `units`: Length unit (default: "m")
   - `coordinate_system`: Description (default: "centerline_origin")
   - `name`: Hull name (optional)
   - `description`: Description (optional)
   - `water_density`: kg/m³ (default: 1025.0 for seawater)

2. **JSON format specification**:
   ```json
   {
     "metadata": {
       "name": "Example Kayak",
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
           {"x": 0.0, "y": 0.3, "z": 0.3}
         ]
       }
     ]
   }
   ```

3. **CSV format specification**:
   - Simple format: station, y, z (x derived from station)
   - First row: headers or comments
   - Metadata via separate columns or separate file
   - Group by station number

### Step 2: Implement Data Validation Module

**File**: `src/io/validators.py` (new)

Create comprehensive validation functions:

1. `validate_metadata(metadata: dict) -> tuple[bool, list[str]]`:
   - Check required fields
   - Validate units are recognized
   - Validate water_density is positive
   - Return (is_valid, error_messages)

2. `validate_point_data(point_dict: dict) -> tuple[bool, list[str]]`:
   - Check x, y, z fields exist
   - Check all values are numeric
   - Check for NaN/Inf values

3. `validate_profile_data(profile_dict: dict) -> tuple[bool, list[str]]`:
   - Check station field exists
   - Validate points list
   - Check minimum number of points (>= 3)
   - Validate all points have same x-coordinate (match station)

4. `validate_hull_data(hull_data: dict) -> tuple[bool, list[str]]`:
   - Validate metadata
   - Check profiles list exists and not empty
   - Validate each profile
   - Check station ordering (should be monotonic)
   - Check for duplicate stations
   - Validate symmetry if expected

5. `validate_csv_data(df_or_array, format_type: str) -> tuple[bool, list[str]]`:
   - Validate CSV data structure
   - Check for missing values
   - Validate column names/structure

### Step 3: Implement JSON Loader

**File**: `src/io/loaders.py` (new)

Create JSON loading functionality:

1. `load_hull_from_json(filepath: str) -> KayakHull`:
   - Load JSON file
   - Validate structure
   - Parse metadata and apply to hull
   - Create Point3D objects from point data
   - Create Profile objects from profile data
   - Build and return KayakHull object
   - Raise descriptive errors on validation failure

2. `parse_json_metadata(metadata: dict) -> dict`:
   - Parse metadata with defaults
   - Return normalized metadata dictionary

3. `parse_json_profile(profile_data: dict) -> Profile`:
   - Parse single profile from JSON
   - Create Point3D objects
   - Return Profile object

### Step 4: Implement CSV Loader

**File**: `src/io/loaders.py` (continued)

Create CSV loading functionality:

1. `load_hull_from_csv(filepath: str, **kwargs) -> KayakHull`:
   - Load CSV file (support various formats)
   - Parse with pandas or numpy
   - Validate data
   - Group points by station
   - Create profiles
   - Return KayakHull object

2. CSV format options to support:
   - Format A: `station, y, z` (x = station)
   - Format B: `x, y, z` (station from x values)
   - Format C: Separate station column indicator

3. Optional parameters:
   - `units`: Override default units
   - `water_density`: Override default
   - `has_header`: Whether first row is header
   - `delimiter`: CSV delimiter (default: ',')

### Step 5: Create Default Metadata Handler

**File**: `src/io/defaults.py` (new)

Create defaults management:

1. `get_default_metadata() -> dict`:
   - Return dictionary with all default metadata values
   
2. `apply_metadata_defaults(metadata: dict) -> dict`:
   - Fill in missing metadata fields with defaults
   - Preserve user-provided values

3. `create_metadata_template() -> dict`:
   - Return template with comments/descriptions

### Step 6: Update IO Module Init

**File**: `src/io/__init__.py` (update)

Export public API:
- `load_hull_from_json`
- `load_hull_from_csv`
- `validate_hull_data`
- `get_default_metadata`

### Step 7: Create Sample Data Files

**Files**: Create in `data/` directory

1. `sample_hull.json`:
   - Complete example with metadata
   - Simple rectangular-like hull
   - 5-7 profiles
   - Well-commented

2. `sample_hull_simple.csv`:
   - Simple CSV format
   - Same geometry as JSON example
   - Header row with column names

3. `sample_hull_kayak.json`:
   - More realistic kayak shape
   - 10+ profiles
   - Proper taper at bow/stern

### Step 8: Create Comprehensive Tests

**File**: `tests/test_io.py` (new)

Test coverage:

1. **Test validators**:
   - Valid data passes validation
   - Invalid data fails with appropriate errors
   - Edge cases (empty data, missing fields)

2. **Test JSON loader**:
   - Load valid JSON files
   - Handle invalid JSON
   - Handle missing required fields
   - Handle malformed data
   - Verify correct hull construction

3. **Test CSV loader**:
   - Load various CSV formats
   - Handle different delimiters
   - Handle missing headers
   - Handle invalid data

4. **Test metadata defaults**:
   - Defaults applied correctly
   - User values override defaults

5. **Integration tests**:
   - Load sample files successfully
   - Loaded hull has correct properties
   - Can perform calculations on loaded hull

### Step 9: Create Example Scripts

**File**: `examples/data_input_examples.py` (new)

Examples to include:

1. Load hull from JSON
2. Load hull from CSV
3. Load with custom metadata
4. Validate data before loading
5. Handle loading errors gracefully
6. Inspect loaded hull properties
7. Convert between formats

### Step 10: Documentation

**File**: `docs/PHASE7_TASK7.1_SUMMARY.md` (new)

Document:
- Data format specifications
- JSON schema details
- CSV format options
- Metadata fields and defaults
- Usage examples
- Validation rules
- Error handling approach

## Implementation Order

1. ✅ Create plan document
2. Create `src/io/formats.py` - Format specifications and constants
3. Create `src/io/defaults.py` - Default metadata handling
4. Create `src/io/validators.py` - Data validation functions
5. Create `src/io/loaders.py` - JSON and CSV loading functions
6. Update `src/io/__init__.py` - Export public API
7. Create sample data files in `data/`
8. Create comprehensive tests in `tests/test_io.py`
9. Create example scripts in `examples/data_input_examples.py`
10. Create documentation in `docs/PHASE7_TASK7.1_SUMMARY.md`
11. Update main TASKS.md to mark task complete

## Success Criteria

- ✅ JSON format fully specified and documented
- ✅ CSV format fully specified and documented  
- ✅ Metadata defaults defined and applied automatically
- ✅ Comprehensive data validation with clear error messages
- ✅ JSON loader working with sample files
- ✅ CSV loader working with sample files
- ✅ All validation edge cases handled
- ✅ Sample data files created and loadable
- ✅ Comprehensive test suite (target: 50+ tests)
- ✅ Example scripts demonstrating all features
- ✅ Complete documentation
- ✅ All tests passing

## Error Handling Strategy

1. **File not found**: Clear message with file path
2. **Invalid JSON/CSV**: Parse error with line number if possible
3. **Validation errors**: List all validation issues found
4. **Type errors**: Indicate expected vs. actual type
5. **Missing required fields**: List all missing fields
6. **Invalid values**: Indicate which field and why invalid

## Notes

- Use standard library `json` module for JSON parsing
- Use `csv` module or numpy for CSV parsing (avoid pandas dependency if possible)
- Provide helpful error messages for common mistakes
- Support flexible input formats where reasonable
- Maintain backward compatibility in future format changes
