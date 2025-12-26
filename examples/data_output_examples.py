"""
Examples demonstrating data export and report generation functionality.

This module shows how to:
- Export hydrostatic properties to CSV
- Export stability curves and metrics
- Export CG summaries
- Generate analysis reports in Markdown
- Create complete analysis workflows with exports

Run individual examples or all at once.
"""

import numpy as np
from pathlib import Path

from src.geometry import Point3D, Profile, KayakHull
from src.hydrostatics import CenterOfGravity, calculate_center_of_buoyancy
from src.stability import StabilityAnalyzer
from src.io import (
    load_hull_from_json,
    export_hydrostatic_properties,
    export_stability_curve,
    export_stability_metrics,
    export_righting_arm,
    export_cg_summary,
    export_cross_sections,
    generate_hydrostatic_report,
    generate_stability_report,
    generate_complete_report,
)


def create_simple_hull() -> KayakHull:
    """Create a simple test hull for demonstrations."""
    hull = KayakHull()

    # Create profiles along the length
    for x_pos in np.linspace(0, 4, 7):
        # Simple cross-section shape
        points = [
            Point3D(x_pos, 0.0, 0.5),  # Deck center
            Point3D(x_pos, 0.4, -0.2),  # Starboard
            Point3D(x_pos, -0.4, -0.2),  # Port
        ]
        profile = Profile(station=x_pos, points=points)
        hull.add_profile(profile)

    return hull


def example1_export_hydrostatic_properties():
    """
    Example 1: Export Hydrostatic Properties

    Export displacement volume, center of buoyancy, and related properties to CSV.
    """
    print("\n" + "=" * 70)
    print("Example 1: Export Hydrostatic Properties")
    print("=" * 70)

    # Create or load hull
    hull = create_simple_hull()

    # Calculate center of buoyancy
    waterline_z = 0.0
    cb = calculate_center_of_buoyancy(hull, waterline_z=waterline_z)

    # Export to CSV
    output_path = Path("examples/output/hydrostatic_properties.csv")
    export_hydrostatic_properties(
        cb, filepath=output_path, metadata={"hull_name": "Simple Test Hull"}
    )

    print(f"\nHydrostatic properties exported to: {output_path}")
    print(f"  Volume: {cb.volume:.4f} m³")
    print(f"  LCB: {cb.lcb:.3f} m")
    print(f"  VCB: {cb.vcb:.3f} m")


def example2_export_stability_curve():
    """
    Example 2: Export Stability Curve

    Export GZ vs heel angle data to CSV for plotting or further analysis.
    """
    print("\n" + "=" * 70)
    print("Example 2: Export Stability Curve")
    print("=" * 70)

    # Setup
    hull = create_simple_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=100.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=0.0)

    # Generate stability curve
    curve = analyzer.generate_stability_curve(max_angle=60)

    # Export with CB data
    output_path = Path("examples/output/stability_curve.csv")
    export_stability_curve(curve, filepath=output_path, include_cb=True)

    print(f"\nStability curve exported to: {output_path}")
    print(f"  Points: {len(curve.heel_angles)}")
    print(f"  Max GZ: {curve.max_gz:.4f} m at {curve.angle_of_max_gz:.1f}°")


def example3_export_stability_metrics():
    """
    Example 3: Export Stability Metrics

    Export key stability parameters (GM, max GZ, etc.) to CSV.
    """
    print("\n" + "=" * 70)
    print("Example 3: Export Stability Metrics")
    print("=" * 70)

    # Setup
    hull = create_simple_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=100.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=0.0)

    # Analyze stability
    metrics = analyzer.analyze_stability()

    # Export metrics
    output_path = Path("examples/output/stability_metrics.csv")
    export_stability_metrics(metrics, filepath=output_path)

    print(f"\nStability metrics exported to: {output_path}")
    if metrics.gm_estimate is not None:
        print(f"  GM: {metrics.gm_estimate:.3f} m")
    print(f"  Max GZ: {metrics.max_gz:.3f} m")
    print(f"  Vanishing angle: {metrics.angle_of_vanishing_stability:.1f}°")


def example4_export_righting_arm():
    """
    Example 4: Export Single Righting Arm Calculation

    Export detailed GZ calculation at a specific heel angle.
    """
    print("\n" + "=" * 70)
    print("Example 4: Export Single Righting Arm")
    print("=" * 70)

    # Setup
    hull = create_simple_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=100.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=0.0)

    # Calculate at specific angle
    heel_angle = 30.0
    ra = analyzer.calculate_righting_arm(heel_angle)

    # Export
    output_path = Path(f"examples/output/righting_arm_{int(heel_angle)}deg.csv")
    export_righting_arm(ra, filepath=output_path)

    print(f"\nRighting arm at {heel_angle}° exported to: {output_path}")
    print(f"  GZ: {ra.gz:.4f} m")
    print(f"  Stable: {ra.is_stable}")


def example5_export_cg_summary():
    """
    Example 5: Export Center of Gravity Summary

    Export CG position and component breakdown.
    """
    print("\n" + "=" * 70)
    print("Example 5: Export CG Summary")
    print("=" * 70)

    # Create CG with components
    cg = CenterOfGravity(
        lcg=2.44,
        vcg=-0.36,
        tcg=0.0,
        total_mass=100.0,
        num_components=2,
        components=[
            {"name": "Kayak", "mass": 20.0, "lcg": 2.5, "vcg": -0.1, "tcg": 0.0},
            {"name": "Paddler", "mass": 80.0, "lcg": 2.4, "vcg": -0.4, "tcg": 0.0},
        ],
    )

    # Export with component breakdown
    output_path = Path("examples/output/cg_summary.csv")
    export_cg_summary(cg, filepath=output_path, include_components=True)

    print(f"\nCG summary exported to: {output_path}")
    print(f"  Total mass: {cg.total_mass:.1f} kg")
    print(f"  LCG: {cg.lcg:.3f} m")
    print(f"  VCG: {cg.vcg:.3f} m")
    print(f"  Components: {cg.num_components}")


def example6_export_cross_sections():
    """
    Example 6: Export Cross-Sectional Properties

    Export area, centroid, and waterline beam at each station.
    """
    print("\n" + "=" * 70)
    print("Example 6: Export Cross-Sectional Properties")
    print("=" * 70)

    # Create hull
    hull = create_simple_hull()

    # Export cross-sectional data
    output_path = Path("examples/output/cross_sections.csv")
    export_cross_sections(hull, waterline_z=0.0, filepath=output_path, num_stations=10)

    print(f"\nCross-sectional properties exported to: {output_path}")
    print(f"  Number of stations: 10")
    print(f"  Waterline: z = 0.0 m")


def example7_generate_hydrostatic_report():
    """
    Example 7: Generate Hydrostatic Analysis Report

    Create a formatted Markdown report with hydrostatic properties.
    """
    print("\n" + "=" * 70)
    print("Example 7: Generate Hydrostatic Report")
    print("=" * 70)

    # Setup
    hull = create_simple_hull()
    cb = calculate_center_of_buoyancy(hull, waterline_z=0.0)

    # Generate report
    output_path = Path("examples/output/hydrostatic_report.md")
    generate_hydrostatic_report(
        hull, cb, filepath=output_path, metadata={"name": "Simple Test Hull"}
    )

    print(f"\nHydrostatic report generated: {output_path}")
    print("  Contains: hull geometry, displacement, center of buoyancy")


def example8_generate_stability_report():
    """
    Example 8: Generate Stability Analysis Report

    Create a formatted Markdown report with stability analysis results.
    """
    print("\n" + "=" * 70)
    print("Example 8: Generate Stability Report")
    print("=" * 70)

    # Setup
    hull = create_simple_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=100.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=0.0)

    # Analyze
    curve = analyzer.generate_stability_curve()
    metrics = analyzer.analyze_stability()

    # Generate report
    output_path = Path("examples/output/stability_report.md")
    generate_stability_report(
        curve, metrics, filepath=output_path, metadata={"name": "Simple Test Hull"}
    )

    print(f"\nStability report generated: {output_path}")
    print("  Contains: stability curve data, key metrics, configuration")


def example9_generate_complete_report():
    """
    Example 9: Generate Complete Analysis Report

    Create a comprehensive report with all analysis results.
    """
    print("\n" + "=" * 70)
    print("Example 9: Generate Complete Analysis Report")
    print("=" * 70)

    # Setup
    hull = create_simple_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=100.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=0.0)

    # Perform full analysis
    curve = analyzer.generate_stability_curve()
    metrics = analyzer.analyze_stability()
    cb = calculate_center_of_buoyancy(hull, waterline_z=0.0)

    # Generate complete report
    output_path = Path("examples/output/complete_analysis_report.md")
    generate_complete_report(
        hull,
        cg,
        curve,
        metrics,
        filepath=output_path,
        cb_upright=cb,
        metadata={
            "name": "Simple Test Hull",
            "description": "Demonstration of complete analysis workflow",
        },
    )

    print(f"\nComplete analysis report generated: {output_path}")
    print("  Contains: hull geometry, hydrostatics, stability, CG, all metrics")


def example10_complete_workflow():
    """
    Example 10: Complete Workflow with Real Hull

    Load a real hull, perform complete analysis, and export everything.
    """
    print("\n" + "=" * 70)
    print("Example 10: Complete Workflow with Real Hull")
    print("=" * 70)

    # Load hull from file
    hull = load_hull_from_json("data/sample_hull_simple.json")

    print(f"Loaded hull:")
    print(f"  Profiles: {hull.num_profiles}")
    print(f"  Length: {hull.length:.2f} m")
    print(f"  Beam: {hull.max_beam:.2f} m")

    # Define CG
    cg = CenterOfGravity(lcg=2.5, vcg=-0.3, tcg=0.0, total_mass=100.0, num_components=1)

    # Create analyzer
    waterline_z = -0.1
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=waterline_z)

    print(f"\nPerforming analysis...")

    # Calculate everything
    cb = calculate_center_of_buoyancy(hull, waterline_z=waterline_z)
    curve = analyzer.generate_stability_curve(max_angle=60)
    metrics = analyzer.analyze_stability()

    # Export everything to output directory
    output_dir = Path("examples/output/workflow")

    print(f"\nExporting results to {output_dir}/...")

    export_hydrostatic_properties(cb, output_dir / "hydrostatics.csv")
    export_stability_curve(curve, output_dir / "stability_curve.csv")
    export_stability_metrics(metrics, output_dir / "metrics.csv")
    export_cg_summary(cg, output_dir / "cg.csv")
    export_cross_sections(hull, waterline_z, output_dir / "cross_sections.csv")

    generate_complete_report(
        hull,
        cg,
        curve,
        metrics,
        filepath=output_dir / "complete_report.md",
        cb_upright=cb,
        metadata={
            "name": "Sample Kayak Hull",
            "description": "Loaded from sample_hull_simple.json",
        },
    )

    print("\n✓ Hydrostatics CSV")
    print("✓ Stability curve CSV")
    print("✓ Stability metrics CSV")
    print("✓ CG summary CSV")
    print("✓ Cross-sections CSV")
    print("✓ Complete report (Markdown)")

    print(f"\nKey results:")
    print(f"  Volume: {cb.volume:.4f} m³")
    if metrics.gm_estimate is not None:
        print(f"  GM: {metrics.gm_estimate:.3f} m")
    print(f"  Max GZ: {metrics.max_gz:.3f} m at {metrics.angle_of_max_gz:.1f}°")


def run_all_examples():
    """Run all examples in sequence."""
    print("\n" + "=" * 70)
    print("DATA OUTPUT EXAMPLES")
    print("=" * 70)

    example1_export_hydrostatic_properties()
    example2_export_stability_curve()
    example3_export_stability_metrics()
    example4_export_righting_arm()
    example5_export_cg_summary()
    example6_export_cross_sections()
    example7_generate_hydrostatic_report()
    example8_generate_stability_report()
    example9_generate_complete_report()
    example10_complete_workflow()

    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print("\nOutput files created in examples/output/")
    print("Check the CSV files and Markdown reports for results.")


if __name__ == "__main__":
    # Run all examples
    run_all_examples()

    # Or run individual examples:
    # example1_export_hydrostatic_properties()
    # example2_export_stability_curve()
    # example3_export_stability_metrics()
    # example4_export_righting_arm()
    # example5_export_cg_summary()
    # example6_export_cross_sections()
    # example7_generate_hydrostatic_report()
    # example8_generate_stability_report()
    # example9_generate_complete_report()
    # example10_complete_workflow()
