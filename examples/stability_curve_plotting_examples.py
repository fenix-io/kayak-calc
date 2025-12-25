"""
Examples for stability curve plotting functions.

This module demonstrates various stability curve visualization techniques
including:
- Basic GZ curves
- Multiple curve comparisons
- Enhanced curves with dynamic stability areas
- Bar charts at specific angles
- Righting moment curves
- Comprehensive stability reports
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from src.geometry.hull import KayakHull
from src.geometry.profile import Profile
from src.geometry.point import Point3D
from src.hydrostatics.center_of_gravity import CenterOfGravity
from src.stability.analyzer import StabilityAnalyzer
from src.visualization.plots import (
    plot_stability_curve,
    plot_multiple_stability_curves,
    plot_stability_curve_with_areas,
    plot_gz_at_angles,
    plot_righting_moment_curve,
    create_stability_report_plot,
)

# Create output directory
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def create_sample_hull():
    """Create a sample kayak hull for demonstrations."""
    hull = KayakHull()
    
    # Define stations along the hull
    stations = [0.0, 1.0, 2.0, 3.0, 4.0]
    
    for x_pos in stations:
        # Vary cross-section shape slightly
        width_factor = 1.0 - 0.15 * abs(x_pos - 2.0) / 2.0
        depth_factor = 1.0 - 0.1 * abs(x_pos - 2.0) / 2.0
        
        points = [
            Point3D(x_pos, -0.5 * width_factor, 0.1 * depth_factor),
            Point3D(x_pos, -0.5 * width_factor, -0.3 * depth_factor),
            Point3D(x_pos, 0.5 * width_factor, -0.3 * depth_factor),
            Point3D(x_pos, 0.5 * width_factor, 0.1 * depth_factor),
        ]
        hull.add_profile(Profile(station=x_pos, points=points))
    
    return hull


def example_1_basic_stability_curve():
    """Example 1: Basic stability curve with default styling."""
    print("Example 1: Basic stability curve")
    
    # Create hull and analyzer
    hull = create_sample_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=80.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.15)
    
    # Generate stability curve
    curve = analyzer.generate_stability_curve(max_angle=60.0, angle_step=2.0)
    metrics = analyzer.analyze_stability(curve)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_stability_curve(curve, metrics, ax=ax)
    ax.set_title("Example 1: Basic Stability Curve", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "example_1_basic_curve.png", dpi=150, bbox_inches='tight')
    print(f"  Saved: {OUTPUT_DIR / 'example_1_basic_curve.png'}")
    plt.close()


def example_2_curve_with_key_points():
    """Example 2: Stability curve with marked key points."""
    print("\nExample 2: Curve with key points marked")
    
    hull = create_sample_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=80.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.15)
    
    curve = analyzer.generate_stability_curve(max_angle=60.0, angle_step=2.0)
    metrics = analyzer.analyze_stability(curve)
    
    # Plot with key points
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_stability_curve(
        curve, 
        metrics, 
        mark_key_points=True,
        ax=ax
    )
    ax.set_title("Example 2: Key Points Marked", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "example_2_key_points.png", dpi=150, bbox_inches='tight')
    print(f"  Saved: {OUTPUT_DIR / 'example_2_key_points.png'}")
    plt.close()


def example_3_custom_colors():
    """Example 3: Custom color scheme."""
    print("\nExample 3: Custom colors")
    
    hull = create_sample_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=80.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.15)
    
    curve = analyzer.generate_stability_curve(max_angle=60.0, angle_step=2.0)
    metrics = analyzer.analyze_stability(curve)
    
    # Plot with custom colors
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_stability_curve(
        curve,
        metrics,
        mark_key_points=True,
        curve_color='purple',
        positive_color='lightblue',
        max_gz_color='orange',
        vanishing_color='red',
        ax=ax
    )
    ax.set_title("Example 3: Custom Color Scheme", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "example_3_custom_colors.png", dpi=150, bbox_inches='tight')
    print(f"  Saved: {OUTPUT_DIR / 'example_3_custom_colors.png'}")
    plt.close()


def example_4_multiple_curves():
    """Example 4: Compare multiple loading conditions."""
    print("\nExample 4: Multiple curves comparison")
    
    hull = create_sample_hull()
    
    # Three different loading conditions
    cg_configs = [
        ("Light load (VCG=-0.15m)", CenterOfGravity(lcg=2.0, vcg=-0.15, tcg=0.0, total_mass=70.0, num_components=1)),
        ("Medium load (VCG=-0.20m)", CenterOfGravity(lcg=2.0, vcg=-0.20, tcg=0.0, total_mass=80.0, num_components=1)),
        ("Heavy load (VCG=-0.25m)", CenterOfGravity(lcg=2.0, vcg=-0.25, tcg=0.0, total_mass=90.0, num_components=1)),
    ]
    
    curves = []
    labels = []
    
    for label, cg in cg_configs:
        analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.15)
        curve = analyzer.generate_stability_curve(max_angle=60.0, angle_step=2.0)
        curves.append(curve)
        labels.append(label)
    
    # Plot comparison
    fig, ax = plt.subplots(figsize=(12, 7))
    plot_multiple_stability_curves(curves, labels, ax=ax)
    ax.set_title("Example 4: Loading Condition Comparison", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "example_4_multiple_curves.png", dpi=150, bbox_inches='tight')
    print(f"  Saved: {OUTPUT_DIR / 'example_4_multiple_curves.png'}")
    plt.close()


def example_5_curve_with_areas():
    """Example 5: Stability curve with dynamic stability area."""
    print("\nExample 5: Curve with dynamic stability area")
    
    hull = create_sample_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=80.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.15)
    
    curve = analyzer.generate_stability_curve(max_angle=60.0, angle_step=2.0)
    metrics = analyzer.analyze_stability(curve)
    
    # Plot with shaded area
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_stability_curve_with_areas(curve, metrics, ax=ax)
    ax.set_title("Example 5: Dynamic Stability Area", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "example_5_with_areas.png", dpi=150, bbox_inches='tight')
    print(f"  Saved: {OUTPUT_DIR / 'example_5_with_areas.png'}")
    plt.close()


def example_6_initial_slope():
    """Example 6: Show initial metacentric height slope."""
    print("\nExample 6: Initial GM slope")
    
    hull = create_sample_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=80.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.15)
    
    curve = analyzer.generate_stability_curve(max_angle=60.0, angle_step=2.0)
    metrics = analyzer.analyze_stability(curve)
    
    # Plot with GM slope line
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_stability_curve_with_areas(curve, metrics, show_slope=True, ax=ax)
    ax.set_title("Example 6: Initial GM Slope", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "example_6_initial_slope.png", dpi=150, bbox_inches='tight')
    print(f"  Saved: {OUTPUT_DIR / 'example_6_initial_slope.png'}")
    plt.close()


def example_7_gz_at_angles():
    """Example 7: Bar chart of GZ at specific angles."""
    print("\nExample 7: GZ at specific angles")
    
    hull = create_sample_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=80.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.15)
    
    curve = analyzer.generate_stability_curve(max_angle=60.0, angle_step=2.0)
    
    # Plot GZ at standard angles
    angles = [10.0, 20.0, 30.0, 40.0, 50.0]
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_gz_at_angles(curve, angles, ax=ax)
    ax.set_title("Example 7: GZ at Standard Angles", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "example_7_gz_at_angles.png", dpi=150, bbox_inches='tight')
    print(f"  Saved: {OUTPUT_DIR / 'example_7_gz_at_angles.png'}")
    plt.close()


def example_8_righting_moment():
    """Example 8: Righting moment curve (force × arm)."""
    print("\nExample 8: Righting moment curve")
    
    hull = create_sample_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=80.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.15)
    
    curve = analyzer.generate_stability_curve(max_angle=60.0, angle_step=2.0)
    
    # Plot righting moment
    mass = 80.0  # kg
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_righting_moment_curve(curve, mass, ax=ax)
    ax.set_title("Example 8: Righting Moment", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "example_8_righting_moment.png", dpi=150, bbox_inches='tight')
    print(f"  Saved: {OUTPUT_DIR / 'example_8_righting_moment.png'}")
    plt.close()


def example_9_stability_report():
    """Example 9: Comprehensive stability report."""
    print("\nExample 9: Comprehensive stability report")
    
    hull = create_sample_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=80.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.15)
    
    curve = analyzer.generate_stability_curve(max_angle=60.0, angle_step=2.0)
    metrics = analyzer.analyze_stability(curve)
    
    # Create comprehensive report
    fig, axes = create_stability_report_plot(curve, metrics, hull, mass=80.0)
    fig.suptitle("Example 9: Comprehensive Stability Report", fontsize=16, fontweight='bold', y=0.995)
    
    plt.savefig(OUTPUT_DIR / "example_9_full_report.png", dpi=150, bbox_inches='tight')
    print(f"  Saved: {OUTPUT_DIR / 'example_9_full_report.png'}")
    plt.close()


def example_10_comparison_with_criteria():
    """Example 10: Compare stability with IMO criteria lines."""
    print("\nExample 10: Comparison with stability criteria")
    
    hull = create_sample_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=80.0, num_components=1)
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.15)
    
    curve = analyzer.generate_stability_curve(max_angle=60.0, angle_step=2.0)
    metrics = analyzer.analyze_stability(curve)
    
    # Plot with reference lines for common criteria
    fig, ax = plt.subplots(figsize=(12, 7))
    plot_stability_curve(curve, metrics, mark_key_points=True, ax=ax)
    
    # Add reference lines (example values)
    ax.axhline(y=0.2, color='green', linestyle='--', alpha=0.5, label='Min GZ @ 30° (0.20m)')
    ax.axvline(x=30.0, color='orange', linestyle='--', alpha=0.5, label='30° reference')
    ax.axvline(x=40.0, color='red', linestyle='--', alpha=0.5, label='40° reference')
    
    ax.legend(loc='upper right')
    ax.set_title("Example 10: Stability with Criteria References", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "example_10_with_criteria.png", dpi=150, bbox_inches='tight')
    print(f"  Saved: {OUTPUT_DIR / 'example_10_with_criteria.png'}")
    plt.close()


def run_all_examples():
    """Run all examples."""
    print("=" * 60)
    print("Stability Curve Plotting Examples")
    print("=" * 60)
    
    example_1_basic_stability_curve()
    example_2_curve_with_key_points()
    example_3_custom_colors()
    example_4_multiple_curves()
    example_5_curve_with_areas()
    example_6_initial_slope()
    example_7_gz_at_angles()
    example_8_righting_moment()
    example_9_stability_report()
    example_10_comparison_with_criteria()
    
    print("\n" + "=" * 60)
    print(f"All examples completed!")
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()
