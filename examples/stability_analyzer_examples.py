"""
Examples demonstrating the StabilityAnalyzer class.

This module shows how to use the object-oriented StabilityAnalyzer interface
for kayak stability analysis. The analyzer provides a convenient high-level
API for performing various stability calculations and comparisons.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from src.geometry import Point3D, Profile, KayakHull
from src.hydrostatics import CenterOfGravity
from src.stability import StabilityAnalyzer, quick_stability_analysis


def create_example_hull() -> KayakHull:
    """
    Create an example kayak hull for demonstrations.

    Returns:
        Simple box-shaped hull
    """
    hull = KayakHull()

    # Create profiles along the length
    for x_pos in np.linspace(0, 4, 7):
        # Box-shaped cross-section
        points = [
            Point3D(x_pos, -0.6, 0.1),  # Top-left (deck)
            Point3D(x_pos, -0.6, -0.5),  # Bottom-left
            Point3D(x_pos, 0.6, -0.5),  # Bottom-right
            Point3D(x_pos, 0.6, 0.1),  # Top-right (deck)
        ]
        profile = Profile(station=x_pos, points=points)
        hull.add_profile(profile)

    return hull


def example1_basic_usage():
    """
    Example 1: Basic StabilityAnalyzer Usage

    Shows how to create an analyzer and perform basic stability calculations.
    """
    print("\n" + "=" * 70)
    print("Example 1: Basic StabilityAnalyzer Usage")
    print("=" * 70)

    # Create hull and CG
    hull = create_example_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.3, tcg=0.0, total_mass=100.0, num_components=1)

    # Create analyzer
    analyzer = StabilityAnalyzer(hull=hull, cg=cg, waterline_z=-0.2)  # Waterline at z = -0.2

    print(f"\nCreated analyzer:")
    print(f"  Waterline: z = {analyzer.waterline_z:.3f} m")
    print(f"  CG: LCG={cg.lcg:.2f} m, VCG={cg.vcg:.2f} m, TCG={cg.tcg:.2f} m")

    # Calculate GZ at specific angle
    angle = 30.0
    gz = analyzer.calculate_gz_at_angle(angle)
    print(f"\nRighting arm (GZ) at {angle}°: {gz:.4f} m")

    # Check stability at angle
    is_stable = analyzer.is_stable_at_angle(angle)
    print(f"Is stable at {angle}°? {is_stable}")

    # Get full righting arm data
    ra = analyzer.calculate_righting_arm(angle)
    print(f"\nRighting Arm details at {angle}°:")
    print(f"  GZ: {ra.gz:.4f} m")
    print(f"  Center of Buoyancy: LCB={ra.cb.lcb:.3f}, VCB={ra.cb.vcb:.3f}, TCB={ra.cb.tcb:.3f}")


def example2_generate_stability_curve():
    """
    Example 2: Generate and Analyze Stability Curve

    Shows how to generate a stability curve and extract key metrics.
    """
    print("\n" + "=" * 70)
    print("Example 2: Generate and Analyze Stability Curve")
    print("=" * 70)

    # Setup
    hull = create_example_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.3, tcg=0.0, total_mass=100.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.2)

    # Generate stability curve with default range (0° to 90°)
    curve = analyzer.generate_stability_curve()

    print(f"\nStability Curve Generated:")
    print(f"  Heel angles: {curve.heel_angles[0]}° to {curve.heel_angles[-1]}°")
    print(f"  Number of points: {len(curve.heel_angles)}")

    # Key values from curve
    print(f"\nKey Values from Curve:")
    print(f"  Maximum GZ: {curve.max_gz:.4f} m at {curve.angle_of_max_gz:.1f}°")

    min_angle, max_angle = curve.range_of_positive_stability
    if np.isfinite(min_angle) and np.isfinite(max_angle):
        print(f"  Range of positive stability: {min_angle:.1f}° to {max_angle:.1f}°")
    else:
        print(f"  Range of positive stability: Not applicable")

    # Analyze to get comprehensive metrics
    metrics = analyzer.analyze_stability(curve)

    print(f"\nStability Metrics:")
    print(f"  Max GZ: {metrics.max_gz:.4f} m")
    print(f"  Angle of max GZ: {metrics.angle_of_max_gz:.1f}°")
    if metrics.gm_estimate is not None:
        print(f"  GM (estimated): {metrics.gm_estimate:.4f} m")
    if metrics.area_under_curve is not None:
        print(f"  Area under curve: {metrics.area_under_curve:.4f} m·rad")

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(curve.heel_angles, curve.gz_values, "b-", linewidth=2, label="GZ Curve")
    plt.axhline(y=0, color="k", linestyle="--", alpha=0.3)
    plt.axvline(
        x=curve.angle_of_max_gz,
        color="r",
        linestyle="--",
        alpha=0.5,
        label=f"Max GZ at {curve.angle_of_max_gz:.1f}°",
    )
    plt.xlabel("Heel Angle (degrees)")
    plt.ylabel("Righting Arm GZ (m)")
    plt.title("Kayak Stability Curve")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    # Save plot
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    plt.savefig(output_dir / "analyzer_example2_curve.png", dpi=150)
    print(f"\nPlot saved to {output_dir / 'analyzer_example2_curve.png'}")
    plt.close()


def example3_comprehensive_summary():
    """
    Example 3: Get Comprehensive Stability Summary

    Shows how to get all stability information in one call.
    """
    print("\n" + "=" * 70)
    print("Example 3: Comprehensive Stability Summary")
    print("=" * 70)

    # Setup
    hull = create_example_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.3, tcg=0.0, total_mass=100.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.2)

    # Get complete summary
    summary = analyzer.get_stability_summary()

    print(f"\nStability Summary:")
    print(f"  Maximum GZ: {summary['max_gz']:.4f} m")
    print(f"  Angle of max GZ: {summary['angle_of_max_gz']:.1f}°")

    if summary["gm"] is not None:
        print(f"  Metacentric height (GM): {summary['gm']:.4f} m")

    if summary["vanishing_angle"] is not None and np.isfinite(summary["vanishing_angle"]):
        print(f"  Vanishing stability angle: {summary['vanishing_angle']:.1f}°")

    if summary["dynamic_stability"] is not None:
        print(f"  Dynamic stability (area): {summary['dynamic_stability']:.4f} m·rad")

    min_angle, max_angle = summary["range_positive"]
    if np.isfinite(min_angle) and np.isfinite(max_angle):
        print(f"  Positive stability range: {min_angle:.1f}° to {max_angle:.1f}°")


def example4_compare_cg_positions():
    """
    Example 4: Compare Different CG Positions

    Shows how to compare stability for different CG configurations.
    """
    print("\n" + "=" * 70)
    print("Example 4: Compare Different CG Positions")
    print("=" * 70)

    # Setup base analyzer
    hull = create_example_hull()
    cg_base = CenterOfGravity(lcg=2.0, vcg=-0.3, tcg=0.0, total_mass=100.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg_base, waterline_z=-0.2)

    # Create different CG positions to compare
    cg_low = CenterOfGravity(lcg=2.0, vcg=-0.4, tcg=0.0, total_mass=100.0, num_components=1)
    cg_high = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=100.0, num_components=1)
    cg_offset = CenterOfGravity(lcg=2.0, vcg=-0.3, tcg=0.1, total_mass=100.0, num_components=1)

    # Compare
    results = analyzer.compare_with_different_cg(
        cg_list=[cg_low, cg_high, cg_offset],
        labels=["Low CG (VCG=-0.4)", "High CG (VCG=-0.2)", "Offset CG (TCG=0.1)"],
    )

    print(f"\nComparison of Different CG Positions:")
    print(f"{'Label':<25} {'Max GZ (m)':<12} {'Angle (deg)':<12} {'GM (m)':<10}")
    print("-" * 65)

    for label, curve, metrics in results:
        gm_str = f"{metrics.gm_estimate:.4f}" if metrics.gm_estimate is not None else "N/A"
        print(f"{label:<25} {metrics.max_gz:<12.4f} {metrics.angle_of_max_gz:<12.1f} {gm_str:<10}")

    # Plot comparison
    plt.figure(figsize=(12, 7))

    for label, curve, metrics in results:
        plt.plot(curve.heel_angles, curve.gz_values, linewidth=2, label=label)

    plt.axhline(y=0, color="k", linestyle="--", alpha=0.3)
    plt.xlabel("Heel Angle (degrees)", fontsize=12)
    plt.ylabel("Righting Arm GZ (m)", fontsize=12)
    plt.title("Stability Comparison: Different CG Positions", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    plt.tight_layout()

    # Save plot
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    plt.savefig(output_dir / "analyzer_example4_cg_comparison.png", dpi=150)
    print(f"\nPlot saved to {output_dir / 'analyzer_example4_cg_comparison.png'}")
    plt.close()


def example5_compare_waterlines():
    """
    Example 5: Compare Different Loading Conditions (Waterlines)

    Shows how to compare stability at different waterlines (loading conditions).
    """
    print("\n" + "=" * 70)
    print("Example 5: Compare Different Loading Conditions")
    print("=" * 70)

    # Setup base analyzer
    hull = create_example_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.3, tcg=0.0, total_mass=100.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.2)

    # Compare different waterlines (loading conditions)
    waterlines = [-0.15, -0.20, -0.25, -0.30]
    labels = ["Very Light", "Light", "Normal", "Heavy"]

    results = analyzer.compare_with_different_waterlines(waterlines, labels)

    print(f"\nComparison of Different Loading Conditions:")
    print(f"{'Load Condition':<15} {'WL (m)':<10} {'Max GZ (m)':<12} {'Angle (deg)':<12}")
    print("-" * 55)

    for label, curve, metrics in results:
        print(
            f"{label:<15} {curve.waterline_z:<10.2f} {metrics.max_gz:<12.4f} "
            f"{metrics.angle_of_max_gz:<12.1f}"
        )

    # Plot comparison
    plt.figure(figsize=(12, 7))

    for label, curve, metrics in results:
        plt.plot(
            curve.heel_angles,
            curve.gz_values,
            linewidth=2,
            label=f"{label} (WL={curve.waterline_z:.2f}m)",
        )

    plt.axhline(y=0, color="k", linestyle="--", alpha=0.3)
    plt.xlabel("Heel Angle (degrees)", fontsize=12)
    plt.ylabel("Righting Arm GZ (m)", fontsize=12)
    plt.title("Stability Comparison: Different Loading Conditions", fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=10)
    plt.tight_layout()

    # Save plot
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    plt.savefig(output_dir / "analyzer_example5_waterline_comparison.png", dpi=150)
    print(f"\nPlot saved to {output_dir / 'analyzer_example5_waterline_comparison.png'}")
    plt.close()


def example6_custom_angle_range():
    """
    Example 6: Custom Heel Angle Range

    Shows how to generate curves with custom angle ranges and steps.
    """
    print("\n" + "=" * 70)
    print("Example 6: Custom Heel Angle Range")
    print("=" * 70)

    # Setup
    hull = create_example_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.3, tcg=0.0, total_mass=100.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.2)

    # Generate curves with different ranges
    print("\nGenerating curves with different angle ranges:")

    # 1. Fine resolution for small angles
    curve_fine = analyzer.generate_stability_curve(min_angle=0, max_angle=30, angle_step=2)
    print(
        f"  Fine curve: {curve_fine.heel_angles[0]}° to {curve_fine.heel_angles[-1]}° "
        f"(step={2}°, {len(curve_fine.heel_angles)} points)"
    )

    # 2. Extended range
    curve_extended = analyzer.generate_stability_curve(min_angle=0, max_angle=120, angle_step=10)
    print(
        f"  Extended curve: {curve_extended.heel_angles[0]}° to {curve_extended.heel_angles[-1]}° "
        f"(step={10}°, {len(curve_extended.heel_angles)} points)"
    )

    # 3. Custom specific angles
    custom_angles = np.array([0, 10, 20, 30, 45, 60, 75, 90])
    curve_custom = analyzer.generate_stability_curve(heel_angles=custom_angles)
    print(f"  Custom angles: {list(curve_custom.heel_angles)}")

    # Plot all three
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    curves = [curve_fine, curve_extended, curve_custom]
    titles = [
        "Fine Resolution (0-30°, step=2°)",
        "Extended Range (0-120°, step=10°)",
        "Custom Angles",
    ]

    for ax, curve, title in zip(axes, curves, titles):
        ax.plot(curve.heel_angles, curve.gz_values, "b-o", linewidth=2, markersize=4)
        ax.axhline(y=0, color="k", linestyle="--", alpha=0.3)
        ax.set_xlabel("Heel Angle (degrees)")
        ax.set_ylabel("GZ (m)")
        ax.set_title(title)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save plot
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    plt.savefig(output_dir / "analyzer_example6_custom_ranges.png", dpi=150)
    print(f"\nPlot saved to {output_dir / 'analyzer_example6_custom_ranges.png'}")
    plt.close()


def example7_quick_analysis():
    """
    Example 7: Quick Stability Analysis

    Shows how to use the quick_stability_analysis convenience function.
    """
    print("\n" + "=" * 70)
    print("Example 7: Quick Stability Analysis")
    print("=" * 70)

    # Setup
    hull = create_example_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.3, tcg=0.0, total_mass=100.0, num_components=1)

    # Quick analysis - single function call
    summary = quick_stability_analysis(hull=hull, cg=cg, waterline_z=-0.2)

    print(f"\nQuick Stability Analysis Results:")
    print(f"  Maximum GZ: {summary['max_gz']:.4f} m")
    print(f"  Angle of max GZ: {summary['angle_of_max_gz']:.1f}°")

    if summary["gm"] is not None:
        print(f"  Metacentric height (GM): {summary['gm']:.4f} m")

    if summary["vanishing_angle"] is not None and np.isfinite(summary["vanishing_angle"]):
        print(f"  Vanishing angle: {summary['vanishing_angle']:.1f}°")

    if summary["dynamic_stability"] is not None:
        print(f"  Dynamic stability: {summary['dynamic_stability']:.4f} m·rad")

    print(f"\nThis is equivalent to:")
    print(f"  analyzer = StabilityAnalyzer(hull, cg, waterline_z)")
    print(f"  summary = analyzer.get_stability_summary()")


def example8_find_key_values():
    """
    Example 8: Find Key Stability Values

    Shows how to use convenience methods to find specific stability parameters.
    """
    print("\n" + "=" * 70)
    print("Example 8: Find Key Stability Values")
    print("=" * 70)

    # Setup
    hull = create_example_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.3, tcg=0.0, total_mass=100.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.2)

    # Find maximum GZ
    max_gz, angle_max = analyzer.find_maximum_gz()
    print(f"\nMaximum GZ:")
    print(f"  Value: {max_gz:.4f} m")
    print(f"  Occurs at: {angle_max:.1f}°")

    # Find vanishing stability angle
    vanishing = analyzer.find_vanishing_stability_angle()
    if np.isfinite(vanishing):
        print(f"\nVanishing Stability Angle: {vanishing:.1f}°")
    else:
        print(f"\nVanishing Stability Angle: Not found in range")

    # Estimate metacentric height
    gm = analyzer.estimate_metacentric_height()
    if gm is not None:
        print(f"\nMetacentric Height (GM): {gm:.4f} m")
        if gm > 0:
            print(f"  Status: Positive initial stability")
        else:
            print(f"  Status: Negative initial stability (unstable)")

    # Calculate dynamic stability
    dynamic = analyzer.calculate_dynamic_stability()
    if dynamic is not None:
        print(f"\nDynamic Stability (area under curve): {dynamic:.4f} m·rad")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("StabilityAnalyzer Examples")
    print("=" * 70)
    print("\nThese examples demonstrate the object-oriented stability analyzer")
    print("interface for kayak hydrostatic calculations.")

    # Run all examples
    example1_basic_usage()
    example2_generate_stability_curve()
    example3_comprehensive_summary()
    example4_compare_cg_positions()
    example5_compare_waterlines()
    example6_custom_angle_range()
    example7_quick_analysis()
    example8_find_key_values()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
