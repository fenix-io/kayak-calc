"""
Data export and report generation for kayak calculations.

This module provides functions to export calculation results to various
formats (CSV, Markdown, text) and generate comprehensive analysis reports.

Export Categories:
- Hydrostatic properties (displacement, center of buoyancy, volume)
- Stability curves (GZ vs heel angle)
- Stability metrics (GM, max GZ, vanishing angle, etc.)
- Cross-section data (area, centroid along hull length)
- Center of gravity data
- Multi-waterline comparisons

Report Types:
- Hydrostatic analysis reports
- Stability analysis reports
- Complete analysis reports (combined)

Features:
- CSV exports with metadata headers
- Markdown formatted reports
- Configurable precision and units
- Automatic directory creation
- Error handling with clear messages

Example:
    >>> from src.stability import StabilityAnalyzer
    >>> from src.io import export_stability_curve, generate_stability_report
    >>>
    >>> # Export stability curve data
    >>> curve = analyzer.generate_stability_curve()
    >>> export_stability_curve(curve, 'output/stability_curve.csv')
    >>>
    >>> # Generate analysis report
    >>> metrics = analyzer.analyze_stability(curve)
    >>> generate_stability_report(curve, metrics, 'output/report.md')
"""

import csv
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import numpy as np

from ..geometry import KayakHull
from ..hydrostatics import CenterOfBuoyancy, CenterOfGravity
from ..stability.righting_arm import RightingArm, StabilityCurve, StabilityMetrics

try:
    from ..stability.criteria import CriteriaCheck
except ImportError:
    # Criteria module might not be available
    CriteriaCheck = None


def _ensure_directory(filepath: Union[str, Path]) -> Path:
    """
    Ensure directory exists for output file.

    Args:
        filepath: Path to output file

    Returns:
        Path object with directory created
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    return filepath


def _write_csv_metadata(file, metadata: Dict[str, Any]):
    """
    Write metadata as comments at top of CSV file.

    Args:
        file: Open file object
        metadata: Dictionary of metadata key-value pairs
    """
    file.write("# Generated: {}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    file.write("# Kayak Calculation Tool - Data Export\n")
    file.write("#\n")
    for key, value in metadata.items():
        file.write(f"# {key}: {value}\n")
    file.write("#\n")


def export_hydrostatic_properties(
    cb: CenterOfBuoyancy,
    filepath: Union[str, Path],
    metadata: Optional[Dict[str, Any]] = None,
    precision: int = 6,
) -> None:
    """
    Export hydrostatic properties to CSV file.

    Exports displacement volume, mass, center of buoyancy coordinates,
    and waterline information.

    Args:
        cb: CenterOfBuoyancy object with calculated properties
        filepath: Path where to save CSV file
        metadata: Optional metadata to include in file header
        precision: Number of decimal places for numeric values (default: 6)

    Raises:
        IOError: If file cannot be written

    Example:
        >>> from src.hydrostatics import calculate_center_of_buoyancy
        >>> cb = calculate_center_of_buoyancy(hull, waterline_z=-0.2)
        >>> export_hydrostatic_properties(cb, 'output/hydrostatics.csv')
    """
    filepath = _ensure_directory(filepath)

    # Prepare metadata
    meta = {
        "Export Type": "Hydrostatic Properties",
        "Waterline Z": f"{cb.waterline_z:.{precision}f} m",
        "Number of Stations": cb.num_stations,
        "Integration Method": cb.integration_method,
    }
    if metadata:
        meta.update(metadata)

    # Write CSV
    with open(filepath, "w", newline="") as f:
        _write_csv_metadata(f, meta)

        writer = csv.writer(f)

        # Header
        writer.writerow(["Property", "Value", "Unit"])

        # Data rows
        writer.writerow(["Volume", f"{cb.volume:.{precision}f}", "m³"])

        # Calculate displacement (mass = volume * density)
        # Use standard seawater density if not provided in metadata
        water_density = metadata.get("water_density", 1025.0) if metadata else 1025.0
        displacement = cb.volume * water_density
        writer.writerow(["Displacement", f"{displacement:.{precision}f}", "kg"])

        writer.writerow(["LCB (Longitudinal CB)", f"{cb.lcb:.{precision}f}", "m"])
        writer.writerow(["VCB (Vertical CB)", f"{cb.vcb:.{precision}f}", "m"])
        writer.writerow(["TCB (Transverse CB)", f"{cb.tcb:.{precision}f}", "m"])
        writer.writerow(["Waterline Z", f"{cb.waterline_z:.{precision}f}", "m"])
        writer.writerow(["Heel Angle", f"{cb.heel_angle:.{precision}f}", "degrees"])

    print(f"Hydrostatic properties exported to: {filepath}")


def export_stability_curve(
    curve: StabilityCurve,
    filepath: Union[str, Path],
    include_cb: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
    precision: int = 6,
) -> None:
    """
    Export stability curve (GZ vs heel angle) to CSV file.

    Exports heel angles, GZ values, and optionally center of buoyancy
    coordinates at each heel angle.

    Args:
        curve: StabilityCurve object with GZ data
        filepath: Path where to save CSV file
        include_cb: If True, include CB coordinates (default: True)
        metadata: Optional metadata to include in file header
        precision: Number of decimal places for numeric values (default: 6)

    Raises:
        IOError: If file cannot be written

    Example:
        >>> curve = analyzer.generate_stability_curve()
        >>> export_stability_curve(curve, 'output/gz_curve.csv')
    """
    filepath = _ensure_directory(filepath)

    # Prepare metadata
    meta = {
        "Export Type": "Stability Curve",
        "Waterline Z": f"{curve.waterline_z:.{precision}f} m",
        "CG Position": f"LCG={curve.cg.lcg:.3f}, VCG={curve.cg.vcg:.3f}, TCG={curve.cg.tcg:.3f} m",
        "Total Mass": f"{curve.cg.total_mass:.2f} kg",
        "Number of Points": len(curve.heel_angles),
        "Integration Method": curve.integration_method,
    }
    if metadata:
        meta.update(metadata)

    # Write CSV
    with open(filepath, "w", newline="") as f:
        _write_csv_metadata(f, meta)

        writer = csv.writer(f)

        # Header
        if include_cb:
            writer.writerow(["Heel_Angle_deg", "GZ_m", "LCB_m", "VCB_m", "TCB_m"])
        else:
            writer.writerow(["Heel_Angle_deg", "GZ_m"])

        # Data rows
        for i, angle in enumerate(curve.heel_angles):
            gz = curve.gz_values[i]
            if include_cb:
                cb = curve.cb_values[i]
                writer.writerow(
                    [
                        f"{angle:.{precision}f}",
                        f"{gz:.{precision}f}",
                        f"{cb.lcb:.{precision}f}",
                        f"{cb.vcb:.{precision}f}",
                        f"{cb.tcb:.{precision}f}",
                    ]
                )
            else:
                writer.writerow([f"{angle:.{precision}f}", f"{gz:.{precision}f}"])

    print(f"Stability curve exported to: {filepath}")


def export_stability_metrics(
    metrics: StabilityMetrics,
    filepath: Union[str, Path],
    metadata: Optional[Dict[str, Any]] = None,
    precision: int = 6,
) -> None:
    """
    Export stability metrics to CSV file.

    Exports key stability parameters: GM, max GZ, vanishing angle,
    range of positive stability, and dynamic stability areas.

    Args:
        metrics: StabilityMetrics object with calculated metrics
        filepath: Path where to save CSV file
        metadata: Optional metadata to include in file header
        precision: Number of decimal places for numeric values (default: 6)

    Raises:
        IOError: If file cannot be written

    Example:
        >>> metrics = analyzer.analyze_stability()
        >>> export_stability_metrics(metrics, 'output/metrics.csv')
    """
    filepath = _ensure_directory(filepath)

    # Prepare metadata
    meta = {
        "Export Type": "Stability Metrics",
        "Waterline Z": f"{metrics.waterline_z:.{precision}f} m",
        "CG Position": (
            f"LCG={metrics.cg_position[0]:.3f}, "
            f"VCG={metrics.cg_position[1]:.3f}, "
            f"TCG={metrics.cg_position[2]:.3f} m"
        ),
    }
    if metadata:
        meta.update(metadata)

    # Write CSV
    with open(filepath, "w", newline="") as f:
        _write_csv_metadata(f, meta)

        writer = csv.writer(f)

        # Header
        writer.writerow(["Metric", "Value", "Unit"])

        # Data rows
        writer.writerow(["GM (Metacentric Height)", f"{metrics.gm_estimate:.{precision}f}", "m"])
        writer.writerow(["Maximum GZ", f"{metrics.max_gz:.{precision}f}", "m"])
        writer.writerow(
            ["Angle of Maximum GZ", f"{metrics.angle_of_max_gz:.{precision}f}", "degrees"]
        )

        # Range of positive stability
        if not np.isnan(metrics.range_of_positive_stability[0]):
            writer.writerow(
                [
                    "Range Positive Stability (Min)",
                    f"{metrics.range_of_positive_stability[0]:.{precision}f}",
                    "degrees",
                ]
            )
            writer.writerow(
                [
                    "Range Positive Stability (Max)",
                    f"{metrics.range_of_positive_stability[1]:.{precision}f}",
                    "degrees",
                ]
            )
        else:
            writer.writerow(["Range Positive Stability (Min)", "N/A", "degrees"])
            writer.writerow(["Range Positive Stability (Max)", "N/A", "degrees"])

        # Vanishing angle
        if not np.isnan(metrics.angle_of_vanishing_stability):
            writer.writerow(
                [
                    "Angle of Vanishing Stability",
                    f"{metrics.angle_of_vanishing_stability:.{precision}f}",
                    "degrees",
                ]
            )
        else:
            writer.writerow(["Angle of Vanishing Stability", "N/A", "degrees"])

        # Dynamic stability (area under curve)
        if metrics.area_under_curve is not None and not np.isnan(metrics.area_under_curve):
            writer.writerow(
                [
                    "Dynamic Stability (Area Under Curve)",
                    f"{metrics.area_under_curve:.{precision}f}",
                    "m·rad",
                ]
            )
        else:
            writer.writerow(["Dynamic Stability (Area Under Curve)", "N/A", "m·rad"])

    print(f"Stability metrics exported to: {filepath}")


def export_righting_arm(
    ra: RightingArm,
    filepath: Union[str, Path],
    metadata: Optional[Dict[str, Any]] = None,
    precision: int = 6,
) -> None:
    """
    Export single righting arm calculation to CSV file.

    Exports GZ, heel angle, CB position, and CG position for a single
    heel angle calculation.

    Args:
        ra: RightingArm object with calculation result
        filepath: Path where to save CSV file
        metadata: Optional metadata to include in file header
        precision: Number of decimal places for numeric values (default: 6)

    Raises:
        IOError: If file cannot be written

    Example:
        >>> ra = analyzer.calculate_righting_arm(30.0)
        >>> export_righting_arm(ra, 'output/gz_30deg.csv')
    """
    filepath = _ensure_directory(filepath)

    # Prepare metadata
    meta = {
        "Export Type": "Righting Arm (Single Angle)",
        "Heel Angle": f"{ra.heel_angle:.{precision}f} degrees",
        "Waterline Z": f"{ra.waterline_z:.{precision}f} m",
    }
    if metadata:
        meta.update(metadata)

    # Write CSV
    with open(filepath, "w", newline="") as f:
        _write_csv_metadata(f, meta)

        writer = csv.writer(f)

        # Header
        writer.writerow(["Property", "Value", "Unit"])

        # Data rows
        writer.writerow(["Heel Angle", f"{ra.heel_angle:.{precision}f}", "degrees"])
        writer.writerow(["GZ (Righting Arm)", f"{ra.gz:.{precision}f}", "m"])
        writer.writerow(["Stable", str(ra.is_stable), ""])
        writer.writerow(["", "", ""])
        writer.writerow(["Center of Buoyancy", "", ""])
        writer.writerow(["LCB", f"{ra.cb.lcb:.{precision}f}", "m"])
        writer.writerow(["VCB", f"{ra.cb.vcb:.{precision}f}", "m"])
        writer.writerow(["TCB", f"{ra.cb.tcb:.{precision}f}", "m"])
        writer.writerow(["Volume", f"{ra.cb.volume:.{precision}f}", "m³"])

        # Calculate displacement
        displacement = ra.cb.volume * 1025.0  # seawater density
        writer.writerow(["Displacement", f"{displacement:.{precision}f}", "kg"])
        writer.writerow(["", "", ""])
        writer.writerow(["Center of Gravity", "", ""])
        writer.writerow(["LCG", f"{ra.cg_lcg:.{precision}f}", "m"])
        writer.writerow(["VCG", f"{ra.cg_vcg:.{precision}f}", "m"])
        writer.writerow(["TCG", f"{ra.cg_tcg:.{precision}f}", "m"])

    print(f"Righting arm data exported to: {filepath}")


def export_cg_summary(
    cg: CenterOfGravity,
    filepath: Union[str, Path],
    include_components: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
    precision: int = 6,
) -> None:
    """
    Export center of gravity summary to CSV file.

    Exports total CG position, total mass, and optionally component breakdown.

    Args:
        cg: CenterOfGravity object
        filepath: Path where to save CSV file
        include_components: If True, include component breakdown (default: True)
        metadata: Optional metadata to include in file header
        precision: Number of decimal places for numeric values (default: 6)

    Raises:
        IOError: If file cannot be written

    Example:
        >>> cg = CenterOfGravity(lcg=2.5, vcg=-0.3, tcg=0.0, total_mass=100.0)
        >>> export_cg_summary(cg, 'output/cg_summary.csv')
    """
    filepath = _ensure_directory(filepath)

    # Prepare metadata
    meta = {
        "Export Type": "Center of Gravity Summary",
        "Total Mass": f"{cg.total_mass:.{precision}f} kg",
        "Number of Components": cg.num_components,
    }
    if metadata:
        meta.update(metadata)

    # Write CSV
    with open(filepath, "w", newline="") as f:
        _write_csv_metadata(f, meta)

        writer = csv.writer(f)

        # Total CG section
        writer.writerow(["Total Center of Gravity", "", ""])
        writer.writerow(["Property", "Value", "Unit"])
        writer.writerow(["LCG (Longitudinal)", f"{cg.lcg:.{precision}f}", "m"])
        writer.writerow(["VCG (Vertical)", f"{cg.vcg:.{precision}f}", "m"])
        writer.writerow(["TCG (Transverse)", f"{cg.tcg:.{precision}f}", "m"])
        writer.writerow(["Total Mass", f"{cg.total_mass:.{precision}f}", "kg"])

        # Component breakdown if available and requested
        if include_components and cg.num_components > 1:
            writer.writerow(["", "", ""])
            writer.writerow(["Component Breakdown", "", ""])
            writer.writerow(["Component", "Mass_kg", "LCG_m", "VCG_m", "TCG_m"])

            for i, comp in enumerate(cg.components):
                writer.writerow(
                    [
                        comp.get("name", f"Component {i+1}"),
                        f'{comp["mass"]:.{precision}f}',
                        f'{comp["lcg"]:.{precision}f}',
                        f'{comp["vcg"]:.{precision}f}',
                        f'{comp["tcg"]:.{precision}f}',
                    ]
                )

    print(f"CG summary exported to: {filepath}")


def export_cross_sections(
    hull: KayakHull,
    waterline_z: float,
    filepath: Union[str, Path],
    num_stations: Optional[int] = None,
    heel_angle: float = 0.0,
    metadata: Optional[Dict[str, Any]] = None,
    precision: int = 6,
) -> None:
    """
    Export cross-sectional properties along hull length to CSV.

    Calculates and exports submerged area, centroid, and waterline beam
    at each station along the hull length.

    Args:
        hull: KayakHull object
        waterline_z: Z-coordinate of waterline
        filepath: Path where to save CSV file
        num_stations: Number of stations to calculate (None = use hull stations)
        heel_angle: Heel angle in degrees (default: 0.0)
        metadata: Optional metadata to include in file header
        precision: Number of decimal places for numeric values (default: 6)

    Raises:
        IOError: If file cannot be written

    Example:
        >>> export_cross_sections(hull, waterline_z=-0.2, filepath='output/sections.csv')
    """
    from ..hydrostatics import calculate_section_properties

    filepath = _ensure_directory(filepath)

    # Get station positions
    if num_stations is None:
        stations = hull.get_stations()
    else:
        stations = np.linspace(hull.stations[0], hull.stations[-1], num_stations)

    # Prepare metadata
    meta = {
        "Export Type": "Cross-Sectional Properties",
        "Waterline Z": f"{waterline_z:.{precision}f} m",
        "Heel Angle": f"{heel_angle:.{precision}f} degrees",
        "Number of Stations": len(stations),
        "Hull Length": f"{hull.length:.{precision}f} m",
    }
    if metadata:
        meta.update(metadata)

    # Calculate properties at each station
    with open(filepath, "w", newline="") as f:
        _write_csv_metadata(f, meta)

        writer = csv.writer(f)

        # Header
        writer.writerow(
            ["Station_m", "Area_m2", "Centroid_Y_m", "Centroid_Z_m", "Waterline_Beam_m"]
        )

        # Data rows
        for station in stations:
            try:
                profile = hull.get_profile(station)
                props = calculate_section_properties(
                    profile, waterline_z=waterline_z, heel_angle=heel_angle
                )

                writer.writerow(
                    [
                        f"{station:.{precision}f}",
                        f"{props.area:.{precision}f}",
                        f"{props.centroid_y:.{precision}f}",
                        f"{props.centroid_z:.{precision}f}",
                        f"{props.waterline_beam:.{precision}f}",
                    ]
                )
            except Exception:
                # Write NaN for stations that fail
                writer.writerow([f"{station:.{precision}f}", "NaN", "NaN", "NaN", "NaN"])

    print(f"Cross-sectional properties exported to: {filepath}")


def export_waterline_comparison(
    results: Dict[float, StabilityCurve],
    filepath: Union[str, Path],
    metadata: Optional[Dict[str, Any]] = None,
    precision: int = 6,
) -> None:
    """
    Export comparison of stability curves at different waterlines.

    Exports max GZ, GM, and vanishing angle for each waterline level.

    Args:
        results: Dictionary mapping waterline_z to StabilityCurve
        filepath: Path where to save CSV file
        metadata: Optional metadata to include in file header
        precision: Number of decimal places for numeric values (default: 6)

    Raises:
        IOError: If file cannot be written

    Example:
        >>> from src.stability import calculate_stability_at_multiple_waterlines
        >>> results = calculate_stability_at_multiple_waterlines(...)
        >>> export_waterline_comparison(results, 'output/waterline_comp.csv')
    """
    from ..stability import analyze_stability as analyze_stability_curve

    filepath = _ensure_directory(filepath)

    # Prepare metadata
    meta = {
        "Export Type": "Waterline Comparison",
        "Number of Waterlines": len(results),
    }
    if metadata:
        meta.update(metadata)

    # Write CSV
    with open(filepath, "w", newline="") as f:
        _write_csv_metadata(f, meta)

        writer = csv.writer(f)

        # Header
        writer.writerow(
            [
                "Waterline_Z_m",
                "GM_m",
                "Max_GZ_m",
                "Angle_Max_GZ_deg",
                "Vanishing_Angle_deg",
                "Range_Min_deg",
                "Range_Max_deg",
                "Area_Under_Curve_m_rad",
            ]
        )

        # Data rows - sort by waterline
        for wl_z in sorted(results.keys()):
            curve = results[wl_z]
            metrics = analyze_stability_curve(curve)

            # Get area under curve
            area = metrics.area_under_curve if metrics.area_under_curve is not None else np.nan

            writer.writerow(
                [
                    f"{wl_z:.{precision}f}",
                    (
                        f"{metrics.gm_estimate:.{precision}f}"
                        if metrics.gm_estimate is not None
                        else "N/A"
                    ),
                    f"{metrics.max_gz:.{precision}f}",
                    f"{metrics.angle_of_max_gz:.{precision}f}",
                    (
                        f"{metrics.angle_of_vanishing_stability:.{precision}f}"
                        if not np.isnan(metrics.angle_of_vanishing_stability)
                        else "N/A"
                    ),
                    (
                        f"{metrics.range_of_positive_stability[0]:.{precision}f}"
                        if not np.isnan(metrics.range_of_positive_stability[0])
                        else "N/A"
                    ),
                    (
                        f"{metrics.range_of_positive_stability[1]:.{precision}f}"
                        if not np.isnan(metrics.range_of_positive_stability[1])
                        else "N/A"
                    ),
                    f"{area:.{precision}f}" if not np.isnan(area) else "N/A",
                ]
            )

    print(f"Waterline comparison exported to: {filepath}")


# Report generation functions


def format_hydrostatic_summary(
    cb: CenterOfBuoyancy, hull: Optional[KayakHull] = None, precision: int = 3
) -> str:
    """
    Format hydrostatic properties as text summary.

    Args:
        cb: CenterOfBuoyancy object
        hull: Optional KayakHull for additional geometry info
        precision: Number of decimal places (default: 3)

    Returns:
        Formatted text string
    """
    lines = []
    lines.append("## Hydrostatic Properties")
    lines.append("")

    if hull:
        lines.append("### Hull Geometry")
        lines.append(f"- Length: {hull.length:.{precision}f} m")
        lines.append(f"- Maximum Beam: {hull.max_beam:.{precision}f} m")
        lines.append(f"- Number of Profiles: {hull.num_profiles}")
        lines.append("")

    lines.append("### Displacement")
    lines.append(f"- Volume: {cb.volume:.{precision+1}f} m³")

    # Calculate displacement (mass = volume * density)
    displacement = cb.volume * 1025.0  # Use seawater density
    lines.append(f"- Mass: {displacement:.1f} kg")
    lines.append("")

    lines.append("### Center of Buoyancy")
    lines.append(f"- LCB (Longitudinal): {cb.lcb:.{precision}f} m")
    lines.append(f"- VCB (Vertical): {cb.vcb:.{precision}f} m")
    lines.append(f"- TCB (Transverse): {cb.tcb:.{precision}f} m")
    lines.append("")

    lines.append("### Waterline")
    lines.append(f"- Z-coordinate: {cb.waterline_z:.{precision}f} m")
    lines.append(f"- Heel angle: {cb.heel_angle:.1f}°")
    lines.append("")

    return "\n".join(lines)


def format_stability_summary(metrics: StabilityMetrics, precision: int = 3) -> str:
    """
    Format stability metrics as text summary.

    Args:
        metrics: StabilityMetrics object
        precision: Number of decimal places (default: 3)

    Returns:
        Formatted text string
    """
    lines = []
    lines.append("## Stability Metrics")
    lines.append("")

    lines.append("### Initial Stability")
    lines.append(f"- GM (Metacentric Height): {metrics.gm_estimate:.{precision}f} m")
    lines.append("")

    lines.append("### Maximum Righting Arm")
    lines.append(f"- Maximum GZ: {metrics.max_gz:.{precision}f} m")
    lines.append(f"- Angle of Maximum GZ: {metrics.angle_of_max_gz:.1f}°")
    lines.append("")

    lines.append("### Range of Stability")
    if not np.isnan(metrics.range_of_positive_stability[0]):
        lines.append(
            f"- Range of Positive Stability: "
            f"{metrics.range_of_positive_stability[0]:.1f}° to "
            f"{metrics.range_of_positive_stability[1]:.1f}°"
        )
    else:
        lines.append("- Range of Positive Stability: N/A")

    if not np.isnan(metrics.angle_of_vanishing_stability):
        lines.append(f"- Angle of Vanishing Stability: {metrics.angle_of_vanishing_stability:.1f}°")
    else:
        lines.append("- Angle of Vanishing Stability: N/A")
    lines.append("")

    lines.append("### Dynamic Stability")
    if metrics.area_under_curve is not None and not np.isnan(metrics.area_under_curve):
        lines.append(f"- Area Under Curve: {metrics.area_under_curve:.{precision+1}f} m·rad")
    else:
        lines.append("- Area Under Curve: N/A")
    lines.append("")

    return "\n".join(lines)


def format_criteria_summary(criteria_results: List, precision: int = 3) -> str:
    """
    Format stability criteria assessment as text summary.

    Args:
        criteria_results: List of CriteriaCheck objects
        precision: Number of decimal places (default: 3)

    Returns:
        Formatted text string
    """
    lines = []
    lines.append("## Stability Criteria Assessment")
    lines.append("")

    for result in criteria_results:
        # Handle both CriteriaCheck and dictionary formats
        if hasattr(result, "result"):
            # CriteriaCheck object
            status = f"{result.result.value}"
            name = result.name
            description = result.description
            measured = result.measured_value
            required = result.required_value
            units = result.units
        else:
            # Legacy dictionary format
            status = "✓ PASS" if result.get("passes", False) else "✗ FAIL"
            name = result.get("criterion_name", "Unknown")
            description = result.get("description", "")
            measured = result.get("actual_value", None)
            required = result.get("requirement", "")
            units = result.get("unit", "")

        lines.append(f"### {name}: {status}")
        lines.append(f"- {description}")

        if required:
            lines.append(f"- Required: {required}")

        if measured is not None:
            lines.append(f"- Actual: {measured:.{precision}f} {units}")

        if hasattr(result, "details") and result.details:
            lines.append(f"- Details: {result.details}")

        lines.append("")

    return "\n".join(lines)


def generate_hydrostatic_report(
    hull: KayakHull,
    cb: CenterOfBuoyancy,
    filepath: Union[str, Path],
    metadata: Optional[Dict[str, Any]] = None,
    precision: int = 3,
) -> None:
    """
    Generate hydrostatic analysis report in Markdown format.

    Creates a comprehensive report with hull geometry, displacement,
    and center of buoyancy information.

    Args:
        hull: KayakHull object
        cb: CenterOfBuoyancy object
        filepath: Path where to save report file
        metadata: Optional metadata to include
        precision: Number of decimal places (default: 3)

    Raises:
        IOError: If file cannot be written

    Example:
        >>> from src.hydrostatics import calculate_center_of_buoyancy
        >>> cb = calculate_center_of_buoyancy(hull, waterline_z=-0.2)
        >>> generate_hydrostatic_report(hull, cb, 'output/hydrostatic_report.md')
    """
    filepath = _ensure_directory(filepath)

    with open(filepath, "w") as f:
        # Title
        f.write("# Hydrostatic Analysis Report\n\n")

        # Metadata
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        if metadata and "name" in metadata:
            f.write(f"**Hull Name:** {metadata['name']}  \n")
        f.write("\n")

        # Hydrostatic summary
        f.write(format_hydrostatic_summary(cb, hull, precision))

        # Calculation details
        f.write("## Calculation Details\n")
        f.write(f"- Number of Stations: {cb.num_stations}\n")
        f.write(f"- Integration Method: {cb.integration_method}\n")
        f.write("\n")

    print(f"Hydrostatic report generated: {filepath}")


def generate_stability_report(
    curve: StabilityCurve,
    metrics: StabilityMetrics,
    filepath: Union[str, Path],
    criteria_results: Optional[List] = None,
    metadata: Optional[Dict[str, Any]] = None,
    precision: int = 3,
) -> None:
    """
    Generate stability analysis report in Markdown format.

    Creates a comprehensive report with stability curve data, metrics,
    and optional criteria assessment.

    Args:
        curve: StabilityCurve object
        metrics: StabilityMetrics object
        filepath: Path where to save report file
        criteria_results: Optional list of stability criteria results (CriteriaCheck objects)
        metadata: Optional metadata to include
        precision: Number of decimal places (default: 3)

    Raises:
        IOError: If file cannot be written

    Example:
        >>> curve = analyzer.generate_stability_curve()
        >>> metrics = analyzer.analyze_stability()
        >>> generate_stability_report(curve, metrics, 'output/stability_report.md')
    """
    filepath = _ensure_directory(filepath)

    with open(filepath, "w") as f:
        # Title
        f.write("# Stability Analysis Report\n\n")

        # Metadata
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        if metadata and "name" in metadata:
            f.write(f"**Hull Name:** {metadata['name']}  \n")
        f.write("\n")

        # Configuration
        f.write("## Configuration\n\n")
        f.write(f"- Waterline: z = {curve.waterline_z:.{precision}f} m\n")
        f.write(
            f"- CG Position: LCG={curve.cg.lcg:.{precision}f} m, "
            f"VCG={curve.cg.vcg:.{precision}f} m, "
            f"TCG={curve.cg.tcg:.{precision}f} m\n"
        )
        f.write(f"- Total Mass: {curve.cg.total_mass:.1f} kg\n")
        f.write(
            f"- Heel Angle Range: {curve.heel_angles[0]:.1f}° to {curve.heel_angles[-1]:.1f}°\n"
        )
        f.write(f"- Number of Points: {len(curve.heel_angles)}\n")
        f.write("\n")

        # Stability metrics
        f.write(format_stability_summary(metrics, precision))

        # Criteria assessment if provided
        if criteria_results:
            f.write(format_criteria_summary(criteria_results, precision))

        # Calculation details
        f.write("## Calculation Details\n")
        f.write(f"- Number of Stations: {curve.num_stations}\n")
        f.write(f"- Integration Method: {curve.integration_method}\n")
        f.write("\n")

    print(f"Stability report generated: {filepath}")


def generate_complete_report(
    hull: KayakHull,
    cg: CenterOfGravity,
    curve: StabilityCurve,
    metrics: StabilityMetrics,
    filepath: Union[str, Path],
    cb_upright: Optional[CenterOfBuoyancy] = None,
    criteria_results: Optional[List] = None,
    metadata: Optional[Dict[str, Any]] = None,
    precision: int = 3,
) -> None:
    """
    Generate complete analysis report combining hydrostatics and stability.

    Creates a comprehensive report with all analysis results, including
    hull geometry, hydrostatics, stability curves, metrics, and criteria.

    Args:
        hull: KayakHull object
        cg: CenterOfGravity object
        curve: StabilityCurve object
        metrics: StabilityMetrics object
        filepath: Path where to save report file
        cb_upright: Optional CenterOfBuoyancy for upright condition
        criteria_results: Optional list of stability criteria results (CriteriaCheck objects)
        metadata: Optional metadata to include
        precision: Number of decimal places (default: 3)

    Raises:
        IOError: If file cannot be written

    Example:
        >>> from src.stability import StabilityAnalyzer
        >>> analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.2)
        >>> curve = analyzer.generate_stability_curve()
        >>> metrics = analyzer.analyze_stability()
        >>> generate_complete_report(hull, cg, curve, metrics, 'output/report.md')
    """
    filepath = _ensure_directory(filepath)

    with open(filepath, "w") as f:
        # Title
        f.write("# Complete Kayak Analysis Report\n\n")

        # Metadata
        f.write("**Generated:** {}  \n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        f.write("**Kayak Calculation Tool**  \n")
        if metadata and "name" in metadata:
            f.write(f"**Hull Name:** {metadata['name']}  \n")
        if metadata and "description" in metadata:
            f.write(f"**Description:** {metadata['description']}  \n")
        f.write("\n")

        f.write("---\n\n")

        # Table of contents
        f.write("## Table of Contents\n\n")
        f.write("1. [Hull Geometry](#hull-geometry)\n")
        f.write("2. [Hydrostatic Properties](#hydrostatic-properties)\n")
        f.write("3. [Center of Gravity](#center-of-gravity)\n")
        f.write("4. [Stability Analysis](#stability-analysis)\n")
        if criteria_results:
            f.write("5. [Stability Criteria](#stability-criteria-assessment)\n")
        f.write("\n")

        f.write("---\n\n")

        # Hull geometry
        f.write("## Hull Geometry\n\n")
        f.write(f"- Length: {hull.length:.{precision}f} m\n")
        f.write(f"- Maximum Beam: {hull.max_beam:.{precision}f} m\n")
        f.write(f"- Number of Profiles: {hull.num_profiles}\n")
        stations = hull.get_stations()
        f.write(
            f"- Station Range: {stations[0]:.{precision}f} m to {stations[-1]:.{precision}f} m\n"
        )
        f.write("\n")

        # Hydrostatic properties
        if cb_upright:
            f.write(format_hydrostatic_summary(cb_upright, hull, precision))
        else:
            # Use first CB from curve if upright not provided
            cb = curve.cb_values[0] if curve.cb_values else None
            if cb:
                f.write(format_hydrostatic_summary(cb, hull, precision))

        # Center of gravity
        f.write("## Center of Gravity\n\n")
        f.write(f"- LCG (Longitudinal): {cg.lcg:.{precision}f} m\n")
        f.write(f"- VCG (Vertical): {cg.vcg:.{precision}f} m\n")
        f.write(f"- TCG (Transverse): {cg.tcg:.{precision}f} m\n")
        f.write(f"- Total Mass: {cg.total_mass:.1f} kg\n")
        f.write(f"- Number of Components: {cg.num_components}\n")
        f.write("\n")

        # Stability analysis
        f.write("## Stability Analysis\n\n")
        f.write(f"- Waterline: z = {curve.waterline_z:.{precision}f} m\n")
        f.write(
            f"- Heel Angle Range: {curve.heel_angles[0]:.1f}° to {curve.heel_angles[-1]:.1f}°\n"
        )
        f.write("\n")

        f.write(format_stability_summary(metrics, precision))

        # Criteria assessment
        if criteria_results:
            f.write(format_criteria_summary(criteria_results, precision))

        # Calculation details
        f.write("## Calculation Details\n\n")
        f.write(f"- Number of Stations: {curve.num_stations}\n")
        f.write(f"- Integration Method: {curve.integration_method}\n")
        f.write(f"- Number of Heel Angles: {len(curve.heel_angles)}\n")
        f.write("\n")

        f.write("---\n\n")
        f.write("*Report generated by Kayak Calculation Tool*\n")

    print(f"Complete analysis report generated: {filepath}")
