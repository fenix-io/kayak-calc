# Phase 7, Task 7.2: Data Output - Implementation Plan

**Date:** December 25, 2025  
**Status:** 📋 Planning  

## Overview

Implement comprehensive data output functionality for exporting calculation results, stability curve data, and generating formatted reports from kayak hydrostatics and stability analyses.

## Objectives

1. Export hydrostatic properties to structured data files (CSV)
2. Export stability curve data for further analysis or plotting
3. Export summary statistics and key parameters
4. Generate human-readable calculation reports (Markdown/Text)
5. Provide flexible output options with configurable formats

## Design Approach

### 1. Export Module: `src/io/exporters.py`

Create a comprehensive exporter module with functions for various output types.

#### Output Types

##### A. Hydrostatic Properties Export
Export displacement, center of buoyancy, and volume data:
- Volume (m³)
- Displacement mass (kg)
- Center of Buoyancy (LCB, VCB, TCB)
- Waterline information
- Hull dimensions

**Output format:** CSV with header row

##### B. Stability Curve Export
Export GZ curve data for analysis:
- Heel angle (degrees)
- GZ value (m)
- Center of Buoyancy (LCB, VCB, TCB)
- Optional: volume, displacement at each angle

**Output format:** CSV with header row

##### C. Stability Metrics Export
Export calculated stability metrics:
- GM (metacentric height)
- Maximum GZ and angle
- Range of positive stability
- Angle of vanishing stability
- Area under GZ curve (dynamic stability)
- Criteria pass/fail status

**Output format:** CSV with header row

##### D. Cross-Section Data Export
Export cross-sectional properties along hull length:
- Station position (x)
- Submerged area
- Centroid (y, z)
- Waterline beam
- Sectional area coefficient

**Output format:** CSV with header row

##### E. Center of Gravity Summary
Export CG data:
- Total CG position (LCG, VCG, TCG)
- Total mass
- Component breakdown (if available)

**Output format:** CSV with header row

#### Functions to Implement

```python
# Hydrostatic exports
export_hydrostatic_properties(cb, volume, displacement, filepath, metadata)
export_volume_distribution(hull, waterline_z, filepath, num_stations)

# Stability exports
export_stability_curve(curve, filepath, include_cb=True)
export_stability_metrics(metrics, filepath)
export_righting_arm(ra, filepath)

# Multi-waterline analysis
export_waterline_comparison(results, filepath)

# CG exports
export_cg_summary(cg, filepath)

# Cross-section exports
export_cross_sections(hull, waterline_z, filepath, num_stations)
```

### 2. Report Generation: Add to `src/io/exporters.py`

Generate formatted reports for human readability.

#### Report Types

##### A. Hydrostatic Report
```markdown
# Hydrostatic Analysis Report

## Hull Geometry
- Length: X.XX m
- Maximum Beam: X.XX m
- Draft: X.XX m

## Displacement
- Volume: X.XXX m³
- Mass: XXX.X kg

## Center of Buoyancy
- LCB: X.XXX m
- VCB: X.XXX m
- TCB: X.XXX m

## Waterline
- Z-coordinate: X.XX m
- Waterline beam: X.XX m
```

##### B. Stability Report
```markdown
# Stability Analysis Report

## Configuration
- Waterline: z = X.XX m
- CG Position: LCG=X.XX, VCG=X.XX, TCG=X.XX
- Total Mass: XXX.X kg

## Stability Metrics
- GM (Initial stability): X.XXX m
- Maximum GZ: X.XXX m at XX.X°
- Range of positive stability: X.X° to XX.X°
- Angle of vanishing stability: XX.X°
- Dynamic stability (area 0-30°): X.XXX m·rad

## Stability Criteria Assessment
✓ GM > 0.35 m: PASS (GM = X.XXX m)
✓ Max GZ ≥ 0.20 m: PASS (Max GZ = X.XXX m)
...
```

##### C. Complete Analysis Report
Combines hydrostatic + stability + plots references

#### Report Functions

```python
# Report generation
generate_hydrostatic_report(hull, cb, volume, filepath, metadata)
generate_stability_report(curve, metrics, criteria_results, filepath)
generate_complete_report(hull, cg, analyzer, filepath, include_plots=True)

# Report formatting helpers
format_hydrostatic_summary(cb, volume, displacement) -> str
format_stability_summary(metrics) -> str
format_criteria_summary(criteria_results) -> str
```

### 3. Output Options and Configuration

#### Common Parameters
- `filepath`: Path where to save output
- `format`: Output format ('csv', 'txt', 'md', 'json')
- `precision`: Decimal places for numeric values
- `include_metadata`: Whether to include metadata comments/headers
- `units`: Unit system for output

#### Metadata in Outputs
- Include metadata as comments in CSV files (# prefix)
- Include generation timestamp
- Include calculation parameters used
- Include software version/reference

### 4. Error Handling

- Validate input data before export
- Handle file I/O errors gracefully
- Provide clear error messages
- Create output directories if they don't exist

## File Structure

```
src/io/
├── __init__.py           # Update imports
├── exporters.py          # NEW: Export and report functions
├── formats.py            # Existing
├── defaults.py           # Existing
├── loaders.py            # Existing
└── validators.py         # Existing
```

## Testing Strategy

### Test Coverage

1. **CSV Export Tests**
   - Valid data export
   - File creation
   - Header correctness
   - Data accuracy
   - Metadata comments

2. **Report Generation Tests**
   - Markdown formatting
   - Complete content
   - Numeric precision
   - Error handling

3. **Integration Tests**
   - Full workflow: calculate → export → reload
   - Multiple export formats
   - Large datasets

4. **Edge Cases**
   - Empty data
   - Missing optional parameters
   - Invalid file paths
   - Overwrite existing files

### Test File
Add to existing `tests/test_io.py` with new test classes:
- `TestExportHydrostatics`
- `TestExportStability`
- `TestReportGeneration`
- `TestOutputIntegration`

## Example Usage

### Example Scripts: `examples/data_output_examples.py`

Create 10+ examples demonstrating:
1. Export hydrostatic properties
2. Export stability curve
3. Export stability metrics
4. Generate stability report
5. Generate complete analysis report
6. Export multi-waterline comparison
7. Export cross-section data
8. Export with custom formatting
9. Complete workflow (load → analyze → export)
10. Batch export multiple configurations

## Documentation

### OUTPUT_DATA_FORMATS.md

Create comprehensive documentation of all output formats:

```markdown
# Output Data Formats

## CSV Exports

### Stability Curve CSV
Description, columns, example

### Hydrostatic Properties CSV
Description, columns, example

### Stability Metrics CSV
Description, columns, example

## Reports

### Stability Report (Markdown)
Description, sections, example

### Hydrostatic Report (Markdown)
Description, sections, example

## Usage Examples
...
```

## Success Criteria

✅ Export functions implemented and working  
✅ Report generation functions implemented  
✅ All tests passing (target: 40+ tests)  
✅ Example scripts created and working  
✅ OUTPUT_DATA_FORMATS.md documentation complete  
✅ Integration with existing modules  
✅ Error handling robust  

## Timeline

1. Implement export functions (2-3 hours)
2. Implement report generation (1-2 hours)
3. Create tests (1-2 hours)
4. Create examples (1 hour)
5. Write documentation (1 hour)

**Total estimated time:** 6-9 hours

## Dependencies

- Existing `src/stability/` modules for data structures
- Existing `src/hydrostatics/` modules for calculations
- Existing `src/geometry/` modules for hull data
- `pathlib` for file operations
- `csv` module for CSV writing
- `datetime` for timestamps

## Implementation Notes

- Follow existing code style and conventions
- Use type hints throughout
- Add comprehensive docstrings
- Handle both Path and string for file paths
- Create output directories automatically
- Use consistent numeric precision
- Add metadata to all exports
- Make reports human-readable with clear formatting

## Future Enhancements (Post Phase 7)

- Excel export support
- JSON export for structured data
- HTML report generation
- Interactive HTML reports with embedded plots
- Database export options
- REST API for data export
