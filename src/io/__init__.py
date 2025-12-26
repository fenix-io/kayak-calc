"""
Input/Output module for loading and saving data.

This module contains functions for:
- Loading hull geometry from files (JSON, CSV)
- Saving hull geometry to files (JSON, CSV)
- Exporting calculation results (CSV, reports)
- Data validation
- File format handling
- Metadata management
"""

from .loaders import (
    load_hull_from_json,
    load_hull_from_csv,
    save_hull_to_json,
    save_hull_to_csv,
    DataLoadError,
)
from .validators import (
    validate_hull_data,
    validate_metadata,
    validate_profile_data,
    validate_point_data,
    validate_csv_data,
    validate_symmetry,
)
from .defaults import (
    get_default_metadata,
    apply_metadata_defaults,
    create_metadata_template,
    merge_metadata,
    extract_metadata_from_comments,
    format_metadata_for_display,
)
from .formats import (
    get_json_example,
    get_csv_example,
    JSON_SCHEMA,
    CSV_FORMATS,
    SUPPORTED_FORMATS,
    RECOGNIZED_LENGTH_UNITS,
    RECOGNIZED_COORD_SYSTEMS,
)
from .exporters import (
    export_hydrostatic_properties,
    export_stability_curve,
    export_stability_metrics,
    export_righting_arm,
    export_cg_summary,
    export_cross_sections,
    export_waterline_comparison,
    generate_hydrostatic_report,
    generate_stability_report,
    generate_complete_report,
    format_hydrostatic_summary,
    format_stability_summary,
    format_criteria_summary,
)

__all__ = [
    # Loaders
    "load_hull_from_json",
    "load_hull_from_csv",
    "save_hull_to_json",
    "save_hull_to_csv",
    "DataLoadError",
    # Validators
    "validate_hull_data",
    "validate_metadata",
    "validate_profile_data",
    "validate_point_data",
    "validate_csv_data",
    "validate_symmetry",
    # Defaults
    "get_default_metadata",
    "apply_metadata_defaults",
    "create_metadata_template",
    "merge_metadata",
    "extract_metadata_from_comments",
    "format_metadata_for_display",
    # Formats
    "get_json_example",
    "get_csv_example",
    "JSON_SCHEMA",
    "CSV_FORMATS",
    "SUPPORTED_FORMATS",
    "RECOGNIZED_LENGTH_UNITS",
    "RECOGNIZED_COORD_SYSTEMS",
    # Exporters
    "export_hydrostatic_properties",
    "export_stability_curve",
    "export_stability_metrics",
    "export_righting_arm",
    "export_cg_summary",
    "export_cross_sections",
    "export_waterline_comparison",
    "generate_hydrostatic_report",
    "generate_stability_report",
    "generate_complete_report",
    "format_hydrostatic_summary",
    "format_stability_summary",
    "format_criteria_summary",
]
