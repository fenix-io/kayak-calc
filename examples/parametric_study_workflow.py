"""
Parametric Study Workflow

This script demonstrates how to systematically compare multiple kayak
configurations for design exploration and optimization.

This script demonstrates:
- Comparing multiple CG configurations (loading conditions)
- Comparing multiple waterline levels (displacement variations)
- Systematic calculation across parameter space
- Side-by-side comparison visualizations
- Comparative analysis and decision support
- Export of comparison results

Prerequisites:
- Sample hull data file: data/sample_hull_kayak.json
- Python packages: numpy, matplotlib

Expected outputs:
- examples/output/parametric_cg_comparison.png
- examples/output/parametric_waterline_comparison.png
- examples/output/parametric_combined_comparison.png
- examples/output/parametric_comparison_table.csv
- examples/output/parametric_study_report.md

Usage:
    python examples/parametric_study_workflow.py

Author: Kayak Calculation Tool
Version: 1.0
"""

from pathlib import Path
import csv

# Import kayak calculation modules
from src.io import load_hull_from_json
from src.hydrostatics import CenterOfGravity, calculate_center_of_buoyancy
from src.stability import StabilityAnalyzer, assess_stability_criteria
from src.visualization import plot_multiple_stability_curves

# Configure output directory
OUTPUT_DIR = Path("examples/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    """
    Parametric study workflow for configuration comparison.

    This demonstrates how to systematically explore the design space
    and compare different configurations.
    """

    print("=" * 70)
    print("PARAMETRIC STUDY WORKFLOW")
    print("=" * 70)

    # =========================================================================
    # STEP 1: Load Base Hull Geometry
    # =========================================================================
    print("\n" + "-" * 70)
    print("STEP 1: Loading Base Hull Geometry")
    print("-" * 70)

    hull_file = Path("data/sample_hull_kayak.json")

    if not hull_file.exists():
        print(f"ERROR: Sample data file not found: {hull_file}")
        return

    print(f"Loading hull from: {hull_file}")
    hull = load_hull_from_json(hull_file)
    print(f"  ✓ Hull loaded successfully")

    # =========================================================================
    # STEP 2: Define Configuration Matrix
    # =========================================================================
    print("\n" + "-" * 70)
    print("STEP 2: Defining Configuration Matrix")
    print("-" * 70)

    # Define multiple loading scenarios to compare
    # Each scenario represents a different use case or loading condition

    print("\n  Defining CG configurations (loading scenarios)...")

    cg_configurations = {
        "Empty": CenterOfGravity(lcg=2.5, vcg=-0.02, tcg=0.0, total_mass=20.0, num_components=1),
        "Light Load": CenterOfGravity(
            lcg=2.4, vcg=-0.10, tcg=0.0, total_mass=85.0, num_components=2
        ),
        "Normal Load": CenterOfGravity(
            lcg=2.5, vcg=-0.15, tcg=0.0, total_mass=100.0, num_components=3
        ),
        "Heavy Load": CenterOfGravity(
            lcg=2.6, vcg=-0.20, tcg=0.0, total_mass=120.0, num_components=4
        ),
    }

    print(f"  ✓ Defined {len(cg_configurations)} CG configurations:")
    for name, cg in cg_configurations.items():
        print(f"      • {name}: {cg.total_mass:.0f}kg at ({cg.lcg:.2f}, {cg.vcg:.2f})")

    # Define waterline levels to compare
    print("\n  Defining waterline levels...")

    waterline_levels = {
        "Design WL": 0.0,
        "Light WL": 0.05,
        "Heavy WL": -0.05,
    }

    print(f"  ✓ Defined {len(waterline_levels)} waterline levels:")
    for name, wl in waterline_levels.items():
        print(f"      • {name}: z = {wl:.2f}m")

    # =========================================================================
    # STEP 3: Run Analyses for CG Comparison
    # =========================================================================
    print("\n" + "-" * 70)
    print("STEP 3: Analyzing CG Configurations")
    print("-" * 70)

    # Use design waterline for CG comparison
    waterline_z = 0.0

    # Store results for each configuration
    cg_results = {}

    print(f"\n  Running stability analysis for each CG configuration...")

    for config_name, cg in cg_configurations.items():
        print(f"\n    Analyzing: {config_name}...")

        # Create analyzer
        analyzer = StabilityAnalyzer(hull, cg, waterline_z=waterline_z)

        # Generate stability curve
        curve = analyzer.generate_stability_curve(max_angle=70, angle_step=2)

        # Get summary metrics
        summary = analyzer.get_stability_summary(max_angle=70)

        # Assess criteria
        criteria = assess_stability_criteria(hull, cg, waterline_z)

        # Store results
        cg_results[config_name] = {
            "cg": cg,
            "curve": curve,
            "summary": summary,
            "criteria": criteria,
        }

        # Display key metrics
        print(
            f"      GM: {summary['gm']:.3f}m, "
            f"Max GZ: {summary['max_gz']:.3f}m @ {summary['max_gz_angle']:.0f}°, "
            f"Vanish: {summary['vanishing_angle']:.0f}°"
        )

    print(f"\n  ✓ Completed analysis of {len(cg_results)} configurations")

    # =========================================================================
    # STEP 4: Run Analyses for Waterline Comparison
    # =========================================================================
    print("\n" + "-" * 70)
    print("STEP 4: Analyzing Waterline Levels")
    print("-" * 70)

    # Use normal load CG for waterline comparison
    cg_normal = cg_configurations["Normal Load"]

    # Store results for each waterline
    wl_results = {}

    print(f"\n  Running stability analysis for each waterline level...")

    for wl_name, wl_z in waterline_levels.items():
        print(f"\n    Analyzing: {wl_name} (z={wl_z:.2f}m)...")

        # Calculate displacement
        cb = calculate_center_of_buoyancy(hull, waterline_z=wl_z)

        # Create analyzer
        analyzer = StabilityAnalyzer(hull, cg_normal, waterline_z=wl_z)

        # Generate stability curve
        curve = analyzer.generate_stability_curve(max_angle=70, angle_step=2)

        # Get summary metrics
        summary = analyzer.get_stability_summary(max_angle=70)

        # Store results
        wl_results[wl_name] = {
            "waterline_z": wl_z,
            "displacement": cb.volume,
            "curve": curve,
            "summary": summary,
        }

        # Display key metrics
        print(
            f"      Disp: {cb.volume:.4f}m³, "
            f"GM: {summary['gm']:.3f}m, "
            f"Max GZ: {summary['max_gz']:.3f}m"
        )

    print(f"\n  ✓ Completed analysis of {len(wl_results)} waterline levels")

    # =========================================================================
    # STEP 5: Create Comparison Visualizations
    # =========================================================================
    print("\n" + "-" * 70)
    print("STEP 5: Creating Comparison Visualizations")
    print("-" * 70)

    # 5.1: CG configuration comparison
    print("\n  Creating CG configuration comparison plot...")

    fig_cg = plot_multiple_stability_curves(
        curves=[res["curve"] for res in cg_results.values()],
        labels=list(cg_results.keys()),
        title="Stability Comparison: Different Loading Conditions",
    )

    cg_plot_file = OUTPUT_DIR / "parametric_cg_comparison.png"
    fig_cg.savefig(cg_plot_file, dpi=150, bbox_inches="tight")
    print(f"    ✓ Saved: {cg_plot_file.name}")

    # 5.2: Waterline level comparison
    print("  Creating waterline level comparison plot...")

    fig_wl = plot_multiple_stability_curves(
        curves=[res["curve"] for res in wl_results.values()],
        labels=list(wl_results.keys()),
        title="Stability Comparison: Different Waterline Levels",
    )

    wl_plot_file = OUTPUT_DIR / "parametric_waterline_comparison.png"
    fig_wl.savefig(wl_plot_file, dpi=150, bbox_inches="tight")
    print(f"    ✓ Saved: {wl_plot_file.name}")

    # =========================================================================
    # STEP 6: Generate Comparison Table
    # =========================================================================
    print("\n" + "-" * 70)
    print("STEP 6: Generating Comparison Table")
    print("-" * 70)

    # Create CSV file with comparison data
    table_file = OUTPUT_DIR / "parametric_comparison_table.csv"

    with open(table_file, "w", newline="") as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(
            [
                "Configuration",
                "Mass (kg)",
                "LCG (m)",
                "VCG (m)",
                "GM (m)",
                "Max GZ (m)",
                "Max GZ Angle (°)",
                "Vanishing Angle (°)",
                "Criteria Pass",
            ]
        )

        # Write data for each CG configuration
        for config_name, results in cg_results.items():
            cg = results["cg"]
            summary = results["summary"]
            criteria = results["criteria"]

            writer.writerow(
                [
                    config_name,
                    f"{cg.total_mass:.1f}",
                    f"{cg.lcg:.3f}",
                    f"{cg.vcg:.3f}",
                    f"{summary['gm']:.3f}",
                    f"{summary['max_gz']:.3f}",
                    f"{summary['max_gz_angle']:.1f}",
                    f"{summary['vanishing_angle']:.1f}",
                    "Yes" if criteria.overall_pass else "No",
                ]
            )

    print(f"  ✓ Comparison table saved: {table_file.name}")

    # =========================================================================
    # STEP 7: Analyze and Compare Results
    # =========================================================================
    print("\n" + "-" * 70)
    print("STEP 7: Comparative Analysis")
    print("-" * 70)

    # Compare CG configurations
    print("\n  CG Configuration Comparison:")
    print("  " + "=" * 66)
    print(
        f"  {'Configuration':<15} {'GM (m)':<10} {'Max GZ (m)':<12} {'Vanish (°)':<12} {'Pass':<8}"
    )
    print("  " + "-" * 66)

    for config_name, results in cg_results.items():
        summary = results["summary"]
        criteria = results["criteria"]

        pass_status = "✓" if criteria.overall_pass else "✗"

        print(
            f"  {config_name:<15} "
            f"{summary['gm']:<10.3f} "
            f"{summary['max_gz']:<12.3f} "
            f"{summary['vanishing_angle']:<12.1f} "
            f"{pass_status:<8}"
        )

    # Compare waterline levels
    print("\n  Waterline Level Comparison:")
    print("  " + "=" * 60)
    print(f"  {'Waterline':<15} {'Disp (m³)':<12} {'GM (m)':<10} {'Max GZ (m)':<12}")
    print("  " + "-" * 60)

    for wl_name, results in wl_results.items():
        summary = results["summary"]
        displacement = results["displacement"]

        print(
            f"  {wl_name:<15} "
            f"{displacement:<12.4f} "
            f"{summary['gm']:<10.3f} "
            f"{summary['max_gz']:<12.3f}"
        )

    # =========================================================================
    # STEP 8: Identify Best Configuration
    # =========================================================================
    print("\n" + "-" * 70)
    print("STEP 8: Design Recommendations")
    print("-" * 70)

    # Find configuration with best GM
    best_gm_config = max(cg_results.items(), key=lambda x: x[1]["summary"]["gm"])

    # Find configuration with best max GZ
    best_gz_config = max(cg_results.items(), key=lambda x: x[1]["summary"]["max_gz"])

    # Find configuration with best vanishing angle
    best_va_config = max(cg_results.items(), key=lambda x: x[1]["summary"]["vanishing_angle"])

    print("\n  Best Configurations by Metric:")
    print(f"    • Best Initial Stability (GM): {best_gm_config[0]}")
    print(f"        GM = {best_gm_config[1]['summary']['gm']:.3f} m")

    print(f"\n    • Best Maximum Righting Arm: {best_gz_config[0]}")
    print(f"        Max GZ = {best_gz_config[1]['summary']['max_gz']:.3f} m")

    print(f"\n    • Best Stability Range: {best_va_config[0]}")
    print(f"        Vanishing Angle = {best_va_config[1]['summary']['vanishing_angle']:.1f}°")

    # Overall assessment
    print("\n  Overall Assessment:")

    # Count passing configurations
    passing_configs = sum(1 for res in cg_results.values() if res["criteria"].overall_pass)

    print(f"    • {passing_configs}/{len(cg_results)} configurations meet stability criteria")

    if passing_configs == len(cg_results):
        print(f"    ✓ All configurations are acceptable for normal use")
    elif passing_configs > 0:
        print(f"    ⚠ Some configurations do not meet criteria")
        print(f"      Recommend using: ", end="")
        passing_names = [name for name, res in cg_results.items() if res["criteria"].overall_pass]
        print(", ".join(passing_names))
    else:
        print(f"    ✗ No configurations meet stability criteria")
        print(f"      Design modifications needed")

    # =========================================================================
    # STEP 9: Generate Study Report
    # =========================================================================
    print("\n" + "-" * 70)
    print("STEP 9: Generating Study Report")
    print("-" * 70)

    report_file = OUTPUT_DIR / "parametric_study_report.md"

    with open(report_file, "w") as f:
        f.write("# Parametric Stability Study Report\n\n")
        f.write("## Study Overview\n\n")
        f.write(f"- **Hull:** {hull_file.name}\n")
        f.write(f"- **Configurations Analyzed:** {len(cg_results)}\n")
        f.write(f"- **Waterline Levels Tested:** {len(wl_results)}\n\n")

        f.write("## CG Configuration Results\n\n")
        f.write("| Configuration | Mass (kg) | GM (m) | Max GZ (m) | Vanishing (°) | Pass |\n")
        f.write("|---------------|-----------|--------|------------|---------------|------|\n")

        for config_name, results in cg_results.items():
            cg = results["cg"]
            summary = results["summary"]
            criteria = results["criteria"]
            pass_status = "✓" if criteria.overall_pass else "✗"

            f.write(
                f"| {config_name} | {cg.total_mass:.1f} | "
                f"{summary['gm']:.3f} | {summary['max_gz']:.3f} | "
                f"{summary['vanishing_angle']:.1f} | {pass_status} |\n"
            )

        f.write("\n## Recommendations\n\n")
        f.write(f"- **Best Initial Stability:** {best_gm_config[0]}\n")
        f.write(f"- **Best Maximum Righting Arm:** {best_gz_config[0]}\n")
        f.write(f"- **Best Stability Range:** {best_va_config[0]}\n")

        f.write("\n## Generated Outputs\n\n")
        f.write(f"- CG comparison plot: `{cg_plot_file.name}`\n")
        f.write(f"- Waterline comparison plot: `{wl_plot_file.name}`\n")
        f.write(f"- Comparison data table: `{table_file.name}`\n")

    print(f"  ✓ Study report saved: {report_file.name}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("PARAMETRIC STUDY COMPLETE")
    print("=" * 70)

    print("\nConfigurations Analyzed:")
    print(f"  • CG configurations: {len(cg_configurations)}")
    print(f"  • Waterline levels: {len(waterline_levels)}")
    print(f"  • Total analyses: {len(cg_results) + len(wl_results)}")

    print("\nGenerated Outputs:")
    print(f"  • {cg_plot_file.name}")
    print(f"  • {wl_plot_file.name}")
    print(f"  • {table_file.name}")
    print(f"  • {report_file.name}")

    print("\nKey Findings:")
    print(f"  • {passing_configs}/{len(cg_results)} configurations meet criteria")
    print(f"  • Best GM: {best_gm_config[0]} ({best_gm_config[1]['summary']['gm']:.3f}m)")
    print(f"  • Best Max GZ: {best_gz_config[0]} ({best_gz_config[1]['summary']['max_gz']:.3f}m)")

    print("\nNext Steps:")
    print("  • Review comparison plots and data table")
    print("  • Select optimal configuration based on design requirements")
    print("  • Explore interactive visualizations (advanced_visualization_workflow.py)")
    print("  • Adapt this script to explore your own parameter space")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
