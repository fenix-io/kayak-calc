"""
Example script demonstrating righting arm (GZ) calculations and stability analysis.

This script shows how to:
1. Calculate GZ at a single heel angle
2. Generate complete GZ curves
3. Analyze stability metrics
4. Compare different CG positions
5. Visualize results

The examples use simple hull geometries for clarity, but the same approach
applies to realistic kayak hulls.
"""

import numpy as np
import matplotlib.pyplot as plt
from src.geometry import Point3D, Profile, KayakHull
from src.hydrostatics import CenterOfGravity
from src.stability import (
    calculate_gz,
    calculate_gz_curve,
    analyze_stability,
    calculate_stability_at_multiple_waterlines,
)


def create_simple_hull(length=4.0, width=1.0, depth=0.6, num_stations=5):
    """Create a simple box hull for demonstration."""
    hull = KayakHull()
    half_width = width / 2.0

    stations = np.linspace(0, length, num_stations)

    for station in stations:
        points = [
            Point3D(station, -half_width, 0.0),  # Top-left
            Point3D(station, -half_width, -depth),  # Bottom-left
            Point3D(station, half_width, -depth),  # Bottom-right
            Point3D(station, half_width, 0.0),  # Top-right
        ]
        profile = Profile(station=station, points=points)
        hull.add_profile(profile)

    return hull


def example_1_single_heel_angle():
    """Example 1: Calculate GZ at a single heel angle."""
    print("=" * 70)
    print("Example 1: Calculate GZ at Single Heel Angle")
    print("=" * 70)

    # Create hull
    hull = create_simple_hull()

    # Define CG (above center of buoyancy for stability)
    cg = CenterOfGravity(
        lcg=2.0,  # Longitudinal position (midship)
        vcg=-0.35,  # Vertical position (above keel)
        tcg=0.0,  # On centerline
        total_mass=100.0,
    )

    # Calculate GZ at 30° heel
    ra = calculate_gz(hull=hull, cg=cg, waterline_z=-0.3, heel_angle=30.0)  # Half draft

    print(f"\nHeel angle: {ra.heel_angle}°")
    print(f"Righting arm (GZ): {ra.gz:.6f} m")
    print(f"Stable: {ra.is_stable}")
    print(f"\nCenter of Buoyancy:")
    print(f"  LCB: {ra.cb.lcb:.6f} m")
    print(f"  VCB: {ra.cb.vcb:.6f} m")
    print(f"  TCB: {ra.cb.tcb:.6f} m")
    print(f"\nCenter of Gravity (in heeled frame):")
    phi_rad = np.deg2rad(ra.heel_angle)
    tcg_heeled = cg.tcg * np.cos(phi_rad) + cg.vcg * np.sin(phi_rad)
    print(f"  TCG: {tcg_heeled:.6f} m")
    print(f"\nGZ = TCB - TCG = {ra.cb.tcb:.6f} - {tcg_heeled:.6f} = {ra.gz:.6f} m")
    print()


def example_2_gz_curve():
    """Example 2: Generate complete GZ curve."""
    print("=" * 70)
    print("Example 2: Generate Complete GZ Curve")
    print("=" * 70)

    hull = create_simple_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.35, tcg=0.0, total_mass=100.0)

    # Generate GZ curve from 0° to 90° in 5° steps
    curve = calculate_gz_curve(hull=hull, cg=cg, waterline_z=-0.3, heel_angles=np.arange(0, 91, 5))

    print(f"\nGenerated GZ curve with {len(curve.heel_angles)} points")
    print(f"Heel angle range: {curve.heel_angles[0]}° to {curve.heel_angles[-1]}°")
    print(f"\nMaximum GZ: {curve.max_gz:.6f} m at {curve.angle_of_max_gz:.1f}°")

    min_angle, max_angle = curve.range_of_positive_stability
    print(f"Range of positive stability: {min_angle:.1f}° to {max_angle:.1f}°")

    # Display some key points
    print(f"\nSample GZ values:")
    for i in [0, 4, 8, 12, 16]:  # 0°, 20°, 40°, 60°, 80°
        print(f"  {curve.heel_angles[i]:5.1f}°: GZ = {curve.gz_values[i]:9.6f} m")
    print()

    return curve


def example_3_stability_metrics():
    """Example 3: Analyze stability metrics."""
    print("=" * 70)
    print("Example 3: Analyze Stability Metrics")
    print("=" * 70)

    hull = create_simple_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.35, tcg=0.0, total_mass=100.0)

    # Generate curve with finer spacing for better GM estimate
    curve = calculate_gz_curve(
        hull=hull, cg=cg, waterline_z=-0.3, heel_angles=np.arange(0, 91, 2)  # 2° steps
    )

    # Analyze stability
    metrics = analyze_stability(curve, estimate_gm=True, calculate_area=True)

    print(f"\nStability Metrics:")
    print(f"-" * 50)
    print(f"Maximum GZ: {metrics.max_gz:.6f} m")
    print(f"Angle of maximum GZ: {metrics.angle_of_max_gz:.2f}°")
    print(f"Angle of vanishing stability: {metrics.angle_of_vanishing_stability:.2f}°")

    min_angle, max_angle = metrics.range_of_positive_stability
    print(f"Range of positive stability: {min_angle:.2f}° to {max_angle:.2f}°")

    if metrics.gm_estimate is not None:
        print(f"\nMetacentric height (GM) estimate: {metrics.gm_estimate:.6f} m")

    if metrics.area_under_curve is not None:
        print(f"Area under GZ curve (dynamic stability): {metrics.area_under_curve:.6f} m·rad")

    print(f"\nWaterline: z = {metrics.waterline_z:.4f} m")
    lcg, vcg, tcg = metrics.cg_position
    print(f"CG position: LCG={lcg:.4f}, VCG={vcg:.4f}, TCG={tcg:.4f}")
    print()


def example_4_compare_cg_positions():
    """Example 4: Compare stability with different CG positions."""
    print("=" * 70)
    print("Example 4: Compare Different CG Positions")
    print("=" * 70)

    hull = create_simple_hull()

    # Three CG positions: low, medium, high
    cg_configs = [
        ("Low CG (stable)", CenterOfGravity(lcg=2.0, vcg=-0.5, tcg=0.0, total_mass=100.0)),
        ("Medium CG", CenterOfGravity(lcg=2.0, vcg=-0.35, tcg=0.0, total_mass=100.0)),
        ("High CG (less stable)", CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=100.0)),
    ]

    print(f"\nComparing three CG positions:")
    print(f"{'':<20} {'Max GZ':<12} {'Angle @ Max':<14} {'Vanishing':<12}")
    print(f"-" * 60)

    curves = []
    for label, cg in cg_configs:
        curve = calculate_gz_curve(hull, cg, waterline_z=-0.3)
        metrics = analyze_stability(curve)
        curves.append((label, curve))

        print(
            f"{label:<20} {metrics.max_gz:8.6f} m   {metrics.angle_of_max_gz:8.2f}°      "
            f"{metrics.angle_of_vanishing_stability:8.2f}°"
        )

    print("\nObservation: Lower CG generally provides better stability")
    print("(larger GZ values, wider range of positive stability)\n")

    return curves


def example_5_multiple_waterlines():
    """Example 5: Stability at different waterlines (drafts)."""
    print("=" * 70)
    print("Example 5: Stability at Multiple Waterlines")
    print("=" * 70)

    hull = create_simple_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.35, tcg=0.0, total_mass=100.0)

    # Different drafts
    waterlines = [-0.45, -0.35, -0.25, -0.15]  # Light to heavy loading

    curves = calculate_stability_at_multiple_waterlines(hull=hull, cg=cg, waterlines=waterlines)

    print(f"\nComparing different waterlines (loading conditions):")
    print(f"{'Waterline (z)':<18} {'Draft':<12} {'Max GZ':<12} {'Angle @ Max':<14}")
    print(f"-" * 60)

    for wl, curve in zip(waterlines, curves):
        draft = abs(wl + 0.6)  # Distance from keel (at z=-0.6)
        metrics = analyze_stability(curve)
        print(
            f"{wl:10.2f} m      {draft:6.3f} m    {metrics.max_gz:8.6f} m   "
            f"{metrics.angle_of_max_gz:8.2f}°"
        )

    print("\nObservation: Deeper drafts generally improve stability")
    print("(more volume, CB effect, etc.)\n")

    return curves


def plot_gz_curve(curve, title="GZ Curve"):
    """Plot a GZ curve."""
    plt.figure(figsize=(10, 6))

    # Main GZ curve
    plt.plot(curve.heel_angles, curve.gz_values, "b-", linewidth=2, label="GZ")

    # Mark zero line
    plt.axhline(y=0, color="k", linestyle="--", linewidth=0.5, label="Zero GZ")

    # Mark maximum GZ
    max_idx = np.argmax(curve.gz_values)
    plt.plot(
        curve.heel_angles[max_idx],
        curve.gz_values[max_idx],
        "ro",
        markersize=10,
        label=f"Max GZ = {curve.max_gz:.3f} m @ {curve.angle_of_max_gz:.1f}°",
    )

    # Shade positive stability region
    positive_mask = curve.gz_values > 0
    if np.any(positive_mask):
        plt.fill_between(
            curve.heel_angles,
            0,
            curve.gz_values,
            where=positive_mask,
            alpha=0.3,
            color="green",
            label="Positive stability",
        )

    plt.xlabel("Heel Angle (degrees)", fontsize=12)
    plt.ylabel("GZ - Righting Arm (m)", fontsize=12)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="best")
    plt.tight_layout()


def plot_comparison(curves_with_labels, title="GZ Curve Comparison"):
    """Plot multiple GZ curves for comparison."""
    plt.figure(figsize=(12, 7))

    colors = ["b", "r", "g", "m", "c"]

    for i, (label, curve) in enumerate(curves_with_labels):
        color = colors[i % len(colors)]
        plt.plot(
            curve.heel_angles,
            curve.gz_values,
            color=color,
            linewidth=2,
            label=label,
            marker="o",
            markersize=3,
        )

    plt.axhline(y=0, color="k", linestyle="--", linewidth=0.5)
    plt.xlabel("Heel Angle (degrees)", fontsize=12)
    plt.ylabel("GZ - Righting Arm (m)", fontsize=12)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="best")
    plt.tight_layout()


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print(" RIGHTING ARM (GZ) CALCULATION EXAMPLES")
    print("=" * 70 + "\n")

    # Run text examples
    example_1_single_heel_angle()
    curve = example_2_gz_curve()
    example_3_stability_metrics()
    cg_curves = example_4_compare_cg_positions()
    wl_curves = example_5_multiple_waterlines()

    # Create plots
    print("=" * 70)
    print("Generating Plots...")
    print("=" * 70)

    # Plot single GZ curve
    plot_gz_curve(curve, title="GZ Curve - Medium CG")

    # Plot CG comparison
    plot_comparison(cg_curves, title="Effect of CG Height on Stability")

    # Plot waterline comparison
    wl_curves_labeled = [
        (f"WL = {wl:.2f} m", curve) for wl, curve in zip([-0.45, -0.35, -0.25, -0.15], wl_curves)
    ]
    plot_comparison(wl_curves_labeled, title="Effect of Draft on Stability")

    plt.show()

    print("\nAll examples completed!")
    print("Close the plot windows to exit.\n")


if __name__ == "__main__":
    main()
