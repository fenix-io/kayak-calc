"""
Complete Stability Analysis Workflow

This script demonstrates a comprehensive professional-level stability analysis
from data loading through complete reporting and visualization.

This script demonstrates:
- Loading realistic hull geometry
- Defining center of gravity from multiple components
- Complete hydrostatic property calculations
- Full stability analysis with GZ curves
- Stability metrics calculation
- Stability criteria assessment
- Comprehensive visualization suite
- Professional report generation

Prerequisites:
- Sample hull data file: data/sample_hull_kayak.json
- Python packages: numpy, matplotlib

Expected outputs:
- examples/output/complete_analysis_hull_3d.png
- examples/output/complete_analysis_profiles.png
- examples/output/complete_analysis_stability_curve.png
- examples/output/complete_analysis_criteria_report.png
- examples/output/complete_analysis_report.md
- examples/output/complete_analysis_data.csv

Usage:
    python examples/complete_stability_analysis.py

Author: Kayak Calculation Tool
Version: 1.0
"""

import numpy as np
from pathlib import Path

# Import kayak calculation modules
from src.io import (
    load_hull_from_json,
    export_stability_curve,
    export_stability_metrics,
    generate_complete_report
)
from src.hydrostatics import CenterOfGravity, calculate_center_of_buoyancy
from src.stability import StabilityAnalyzer, assess_stability_criteria
from src.visualization import (
    plot_hull_3d,
    plot_multiple_profiles,
    plot_stability_curve,
    create_stability_report_plot
)

# Configure output directory
OUTPUT_DIR = Path('examples/output')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    """
    Complete stability analysis workflow.
    
    This demonstrates a full professional-level analysis suitable for
    design validation and documentation.
    """
    
    print("="*70)
    print("COMPLETE STABILITY ANALYSIS WORKFLOW")
    print("="*70)
    
    # =========================================================================
    # STEP 1: Load Hull Geometry
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 1: Loading Hull Geometry")
    print("-"*70)
    
    hull_file = Path('data/sample_hull_kayak.json')
    
    if not hull_file.exists():
        print(f"ERROR: Sample data file not found: {hull_file}")
        print("Please ensure the data file exists before running this script.")
        return
    
    print(f"Loading hull from: {hull_file}")
    hull = load_hull_from_json(hull_file)
    
    stations = hull.get_stations()
    num_profiles = len(stations)
    length = stations[-1] - stations[0]
    
    print(f"  ✓ Hull loaded successfully")
    print(f"  ✓ Number of profiles: {num_profiles}")
    print(f"  ✓ Hull length: {length:.2f} m")
    
    
    # =========================================================================
    # STEP 2: Define Center of Gravity (Multi-Component)
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 2: Defining Center of Gravity")
    print("-"*70)
    
    # Define CG from multiple components for realistic kayak scenario
    # This shows how to account for:
    #   - Hull mass
    #   - Paddler mass
    #   - Gear/equipment mass
    
    print("  Defining mass components...")
    
    # Method 1: Build from components
    # This is more realistic for actual kayak design
    components = [
        # (mass_kg, lcg_m, vcg_m, tcg_m, description)
        (18.0, 2.5, -0.05, 0.0, "Kayak hull"),
        (75.0, 2.4, -0.20, 0.0, "Paddler (seated)"),
        (5.0, 2.0, -0.10, 0.0, "Gear in cockpit"),
        (2.0, 3.5, -0.05, 0.0, "Gear in stern hatch"),
    ]
    
    # Calculate combined CG
    cg = CenterOfGravity.from_components(components)
    
    print(f"  ✓ Total mass: {cg.total_mass:.1f} kg")
    print(f"  ✓ Combined CG: LCG={cg.lcg:.3f}m, VCG={cg.vcg:.3f}m, TCG={cg.tcg:.3f}m")
    print(f"  ✓ Number of components: {len(components)}")
    
    # Show component breakdown
    print("\n  Component breakdown:")
    for i, (mass, lcg, vcg, tcg, desc) in enumerate(components, 1):
        print(f"    {i}. {desc}: {mass:.1f}kg at ({lcg:.2f}, {vcg:.2f}, {tcg:.2f})")
    
    
    # =========================================================================
    # STEP 3: Define Analysis Conditions
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 3: Defining Analysis Conditions")
    print("-"*70)
    
    # Define waterline level
    waterline_z = 0.0  # meters
    print(f"  Waterline level: z = {waterline_z:.3f} m")
    
    # Define heel angle range for stability curve
    max_heel_angle = 80  # degrees
    angle_step = 2  # degrees
    print(f"  Heel angle range: 0° to {max_heel_angle}°")
    print(f"  Angle step: {angle_step}°")
    
    
    # =========================================================================
    # STEP 4: Calculate Hydrostatic Properties
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 4: Calculating Hydrostatic Properties")
    print("-"*70)
    
    # Calculate center of buoyancy and displacement
    cb_result = calculate_center_of_buoyancy(hull, waterline_z=waterline_z)
    
    volume = cb_result.volume
    water_density = 1000.0  # kg/m³
    displaced_mass = volume * water_density
    
    lcb = cb_result.lcb
    vcb = cb_result.vcb
    tcb = cb_result.tcb
    
    print(f"  ✓ Displacement volume: {volume:.4f} m³")
    print(f"  ✓ Displaced mass: {displaced_mass:.2f} kg")
    print(f"  ✓ Center of Buoyancy:")
    print(f"      LCB (x): {lcb:.3f} m")
    print(f"      VCB (z): {vcb:.3f} m")
    print(f"      TCB (y): {tcb:.3f} m")
    
    # Check mass balance
    mass_difference = displaced_mass - cg.total_mass
    mass_percent_diff = (mass_difference / cg.total_mass) * 100
    
    print(f"\n  Mass balance check:")
    print(f"    Kayak + contents mass: {cg.total_mass:.2f} kg")
    print(f"    Displaced water mass:  {displaced_mass:.2f} kg")
    print(f"    Difference: {mass_difference:+.2f} kg ({mass_percent_diff:+.1f}%)")
    
    if abs(mass_percent_diff) < 2:
        print(f"    ✓ Mass balance is good (within 2%)")
    else:
        print(f"    ⚠ Significant mass imbalance - check waterline level")
    
    
    # =========================================================================
    # STEP 5: Perform Stability Analysis
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 5: Performing Stability Analysis")
    print("-"*70)
    
    print("  Creating stability analyzer...")
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=waterline_z)
    
    print("  Generating stability curve...")
    stability_curve = analyzer.generate_stability_curve(
        max_angle=max_heel_angle,
        angle_step=angle_step
    )
    
    # Extract key stability metrics
    heel_angles = stability_curve['heel_angles']
    gz_values = stability_curve['gz_values']
    
    print(f"  ✓ Stability curve generated: {len(heel_angles)} points")
    
    
    # =========================================================================
    # STEP 6: Calculate Stability Metrics
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 6: Calculating Stability Metrics")
    print("-"*70)
    
    # Get comprehensive stability summary
    summary = analyzer.get_stability_summary(max_angle=max_heel_angle)
    
    gm = summary['gm']
    max_gz = summary['max_gz']
    max_gz_angle = summary['max_gz_angle']
    vanishing_angle = summary['vanishing_angle']
    range_positive = summary['range_positive_stability']
    area_30 = summary.get('area_under_curve_0_30', 0)
    area_40 = summary.get('area_under_curve_30_40', 0)
    
    print(f"  ✓ Initial stability (GM): {gm:.3f} m")
    print(f"  ✓ Maximum righting arm: {max_gz:.3f} m at {max_gz_angle:.1f}°")
    print(f"  ✓ Vanishing stability angle: {vanishing_angle:.1f}°")
    print(f"  ✓ Range of positive stability: {range_positive:.1f}°")
    
    if area_30 > 0:
        print(f"  ✓ Area under curve (0-30°): {area_30:.4f} m·rad")
    if area_40 > 0:
        print(f"  ✓ Area under curve (30-40°): {area_40:.4f} m·rad")
    
    
    # =========================================================================
    # STEP 7: Assess Stability Criteria
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 7: Assessing Stability Criteria")
    print("-"*70)
    
    # Check against standard stability criteria
    criteria_assessment = assess_stability_criteria(
        hull=hull,
        cg=cg,
        waterline_z=waterline_z
    )
    
    overall_pass = criteria_assessment.overall_pass
    status_symbol = "✓" if overall_pass else "✗"
    status_text = "PASS" if overall_pass else "FAIL"
    
    print(f"\n  Overall Status: {status_symbol} {status_text}")
    
    # Show individual criteria results
    print("\n  Individual Criteria:")
    for check in criteria_assessment.checks:
        symbol = "✓" if check.passed else "✗"
        print(f"    {symbol} {check.name}:")
        print(f"        Value: {check.actual_value:.4f}")
        print(f"        Required: {check.threshold:.4f}")
        print(f"        Margin: {check.margin:.4f}")
    
    
    # =========================================================================
    # STEP 8: Generate Visualizations
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 8: Generating Visualizations")
    print("-"*70)
    
    # 8.1: Hull 3D plot
    print("  Creating 3D hull visualization...")
    fig_hull = plot_hull_3d(
        hull,
        waterline_z=waterline_z,
        show_waterline=True,
        show_cb=True,
        cb_point=(lcb, tcb, vcb),
        show_cg=True,
        cg_point=(cg.lcg, cg.tcg, cg.vcg),
        title='Kayak Hull with CG and CB'
    )
    
    hull_file_out = OUTPUT_DIR / 'complete_analysis_hull_3d.png'
    fig_hull.savefig(hull_file_out, dpi=150, bbox_inches='tight')
    print(f"    ✓ Saved: {hull_file_out.name}")
    
    # 8.2: Cross-section profiles
    print("  Creating cross-section plots...")
    stations = hull.get_stations()
    station_positions = np.linspace(
        stations[0],
        stations[-1],
        6
    )
    
    # Get profiles at these stations
    profiles_to_plot = [hull.get_profile(station) for station in station_positions]
    
    fig_profiles = plot_multiple_profiles(
        profiles_to_plot,
        waterline_z=waterline_z,
        title='Transverse Profiles'
    )
    
    profiles_file = OUTPUT_DIR / 'complete_analysis_profiles.png'
    fig_profiles.savefig(profiles_file, dpi=150, bbox_inches='tight')
    print(f"    ✓ Saved: {profiles_file.name}")
    
    # 8.3: Stability curve
    print("  Creating stability curve plot...")
    fig_curve = plot_stability_curve(
        heel_angles,
        gz_values,
        title='Stability Curve (GZ vs Heel Angle)',
        show_metrics=True
    )
    
    curve_file = OUTPUT_DIR / 'complete_analysis_stability_curve.png'
    fig_curve.savefig(curve_file, dpi=150, bbox_inches='tight')
    print(f"    ✓ Saved: {curve_file.name}")
    
    # 8.4: Criteria report
    print("  Creating criteria assessment report...")
    fig_criteria = create_stability_report_plot(
        criteria_assessment,
        stability_curve=stability_curve,
        title='Stability Criteria Assessment'
    )
    
    criteria_file = OUTPUT_DIR / 'complete_analysis_criteria_report.png'
    fig_criteria.savefig(criteria_file, dpi=150, bbox_inches='tight')
    print(f"    ✓ Saved: {criteria_file.name}")
    
    
    # =========================================================================
    # STEP 9: Export Data
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 9: Exporting Data")
    print("-"*70)
    
    # Export stability curve data
    curve_csv = OUTPUT_DIR / 'complete_analysis_curve_data.csv'
    export_stability_curve(
        stability_curve,
        filepath=curve_csv
    )
    print(f"  ✓ Stability curve data: {curve_csv.name}")
    
    # Export stability metrics
    metrics_csv = OUTPUT_DIR / 'complete_analysis_metrics.csv'
    export_stability_metrics(
        summary,
        filepath=metrics_csv
    )
    print(f"  ✓ Stability metrics: {metrics_csv.name}")
    
    
    # =========================================================================
    # STEP 10: Generate Complete Report
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 10: Generating Complete Report")
    print("-"*70)
    
    report_file = OUTPUT_DIR / 'complete_analysis_report.md'
    
    generate_complete_report(
        hull=hull,
        cg=cg,
        cb=cb_result,
        stability_summary=summary,
        criteria_assessment=criteria_assessment,
        filepath=report_file,
        metadata={
            'hull_file': str(hull_file),
            'waterline_z': waterline_z,
            'analysis_date': '2025-12-26',
            'analyst': 'Kayak Calculation Tool',
            'components': len(components)
        }
    )
    
    print(f"  ✓ Complete analysis report: {report_file.name}")
    
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    
    print("\nKey Results:")
    print(f"  • Displacement: {volume:.4f} m³ ({displaced_mass:.1f} kg)")
    print(f"  • Center of Buoyancy: ({lcb:.3f}, {vcb:.3f}) m")
    print(f"  • Center of Gravity: ({cg.lcg:.3f}, {cg.vcg:.3f}) m")
    print(f"  • Initial Stability (GM): {gm:.3f} m")
    print(f"  • Max Righting Arm: {max_gz:.3f} m at {max_gz_angle:.1f}°")
    print(f"  • Vanishing Angle: {vanishing_angle:.1f}°")
    print(f"  • Criteria Status: {status_text}")
    
    print("\nGenerated Outputs:")
    print(f"  Visualizations:")
    print(f"    • {hull_file_out.name}")
    print(f"    • {profiles_file.name}")
    print(f"    • {curve_file.name}")
    print(f"    • {criteria_file.name}")
    print(f"  Data Files:")
    print(f"    • {curve_csv.name}")
    print(f"    • {metrics_csv.name}")
    print(f"  Reports:")
    print(f"    • {report_file.name}")
    
    print("\n  All files saved to: examples/output/")
    
    print("\nNext Steps:")
    print("  • Review the generated visualizations and report")
    print("  • Try different CG configurations (parametric_study_workflow.py)")
    print("  • Explore interactive visualizations (advanced_visualization_workflow.py)")
    print("  • Use this script as a template for your own analysis")
    
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
