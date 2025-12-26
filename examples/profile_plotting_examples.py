"""
Examples demonstrating profile and hull plotting capabilities.

This module shows how to use the visualization functions for:
- Plotting individual profiles
- Comparing multiple profiles
- 3D hull visualization
- Annotated property plots
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from src.geometry import Point3D, Profile, KayakHull
from src.visualization import (
    plot_profile,
    plot_multiple_profiles,
    plot_hull_3d,
    plot_profile_with_properties,
    configure_plot_style,
    save_figure,
)


# Set up output directory
OUTPUT_DIR = Path("examples/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_example_hull() -> KayakHull:
    """
    Create an example kayak hull for demonstrations.

    Returns:
        Simple box-shaped hull with varying beam along length
    """
    hull = KayakHull()

    # Create profiles along the length with varying beam
    stations = np.linspace(0, 4, 9)
    for x_pos in stations:
        # Beam varies parabolically (wider in middle)
        beam_factor = 1.0 - 0.3 * ((x_pos - 2) / 2) ** 2
        beam = 0.6 * beam_factor

        # Create cross-section points
        points = [
            Point3D(x_pos, -beam, 0.1),  # Top-left (deck)
            Point3D(x_pos, -beam, -0.5),  # Bottom-left
            Point3D(x_pos, beam, -0.5),  # Bottom-right
            Point3D(x_pos, beam, 0.1),  # Top-right (deck)
        ]
        profile = Profile(station=x_pos, points=points)
        hull.add_profile(profile)

    return hull


def example1_single_profile_upright():
    """
    Example 1: Plot a single profile in upright condition.

    Shows basic profile plotting with waterline and submerged area.
    """
    print("\n" + "=" * 70)
    print("Example 1: Single Profile - Upright Condition")
    print("=" * 70)

    # Create hull and get profile at midship
    hull = create_example_hull()
    profile = hull.get_profile(2.0)

    # Plot the profile
    _ax = plot_profile(profile=profile, waterline_z=-0.2, show_submerged=True, show_waterline=True)

    # Save figure
    save_figure(plt.gcf(), OUTPUT_DIR / "example1_single_profile_upright.png")
    print("Plot saved to: examples/output/example1_single_profile_upright.png")

    plt.show()


def example2_single_profile_heeled():
    """
    Example 2: Plot a single profile at heel angle.

    Demonstrates heel transformation and visualization.
    """
    print("\n" + "=" * 70)
    print("Example 2: Single Profile - Heeled 30°")
    print("=" * 70)

    # Create hull and get profile
    hull = create_example_hull()
    profile = hull.get_profile(2.0)

    # Plot at 30° heel
    _ax = plot_profile(
        profile=profile,
        waterline_z=-0.2,
        heel_angle=30.0,
        show_submerged=True,
        show_waterline=True,
        profile_color="darkblue",
        submerged_color="lightcyan",
    )

    # Save figure
    save_figure(plt.gcf(), OUTPUT_DIR / "example2_single_profile_heeled.png")
    print("Plot saved to: examples/output/example2_single_profile_heeled.png")

    plt.show()


def example3_multiple_profiles():
    """
    Example 3: Plot multiple profiles along hull length.

    Shows profile comparison and variation along length.
    """
    print("\n" + "=" * 70)
    print("Example 3: Multiple Profiles Along Hull")
    print("=" * 70)

    # Create hull
    hull = create_example_hull()

    # Select profiles at various stations
    stations = [0.0, 1.0, 2.0, 3.0, 4.0]
    profiles = [hull.get_profile(x) for x in stations]

    # Plot multiple profiles
    fig, axes = plot_multiple_profiles(
        profiles=profiles, waterline_z=-0.2, ncols=3, show_submerged=True
    )

    # Save figure
    save_figure(fig, OUTPUT_DIR / "example3_multiple_profiles.png")
    print("Plot saved to: examples/output/example3_multiple_profiles.png")

    plt.show()


def example4_hull_3d():
    """
    Example 4: 3D hull visualization.

    Shows complete hull in wireframe view.
    """
    print("\n" + "=" * 70)
    print("Example 4: 3D Hull Visualization")
    print("=" * 70)

    # Create hull
    hull = create_example_hull()

    # Plot in 3D
    _ax = plot_hull_3d(
        hull=hull, waterline_z=-0.2, show_waterline_plane=True, view_mode="wireframe"
    )

    # Save figure
    save_figure(plt.gcf(), OUTPUT_DIR / "example4_hull_3d.png", dpi=200)
    print("Plot saved to: examples/output/example4_hull_3d.png")

    plt.show()


def example5_hull_3d_heeled():
    """
    Example 5: 3D hull visualization at heel angle.

    Shows heeled hull in 3D.
    """
    print("\n" + "=" * 70)
    print("Example 5: 3D Hull Heeled at 25°")
    print("=" * 70)

    # Create hull
    hull = create_example_hull()

    # Plot heeled hull
    _ax = plot_hull_3d(
        hull=hull,
        waterline_z=-0.2,
        heel_angle=25.0,
        show_waterline_plane=True,
        hull_color="navy",
        hull_alpha=0.6,
    )

    # Save figure
    save_figure(plt.gcf(), OUTPUT_DIR / "example5_hull_3d_heeled.png", dpi=200)
    print("Plot saved to: examples/output/example5_hull_3d_heeled.png")

    plt.show()


def example6_profile_with_properties():
    """
    Example 6: Profile with geometric properties annotated.

    Shows centroid, area, and waterline intersections.
    """
    print("\n" + "=" * 70)
    print("Example 6: Profile with Geometric Properties")
    print("=" * 70)

    # Create hull and get profile
    hull = create_example_hull()
    profile = hull.get_profile(2.0)

    # Plot with all properties
    _ax = plot_profile_with_properties(
        profile=profile,
        waterline_z=-0.1,
        show_centroid=True,
        show_area=True,
        show_waterline_intersection=True,
    )

    # Save figure
    save_figure(plt.gcf(), OUTPUT_DIR / "example6_profile_with_properties.png")
    print("Plot saved to: examples/output/example6_profile_with_properties.png")

    plt.show()


def example7_heel_angle_comparison():
    """
    Example 7: Compare same profile at different heel angles.

    Shows how profile and submerged area change with heel.
    """
    print("\n" + "=" * 70)
    print("Example 7: Heel Angle Comparison")
    print("=" * 70)

    # Create hull and get profile
    hull = create_example_hull()
    profile = hull.get_profile(2.0)

    # Create profiles at different heel angles
    heel_angles = [0, 15, 30, 45]
    profiles_at_angles = [profile for _ in heel_angles]

    # Plot with custom station labels
    station_labels = [f"{angle}° Heel" for angle in heel_angles]
    fig, axes = plot_multiple_profiles(
        profiles=profiles_at_angles,
        stations=station_labels,
        waterline_z=-0.2,
        heel_angle=0.0,  # We'll handle this differently
        ncols=2,
        show_submerged=True,
    )

    # Manually plot each at different heel angle
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for i, (angle, ax) in enumerate(zip(heel_angles, axes)):
        plot_profile(
            profile=profile,
            waterline_z=-0.2,
            heel_angle=angle,
            ax=ax,
            title=f"Heel Angle: {angle}°",
            show_submerged=True,
        )

        # Set consistent limits
        ax.set_xlim(-0.8, 0.8)
        ax.set_ylim(-0.6, 0.3)

    plt.suptitle("Profile at Different Heel Angles", fontsize=14, fontweight="bold")
    plt.tight_layout()

    # Save figure
    save_figure(fig, OUTPUT_DIR / "example7_heel_angle_comparison.png")
    print("Plot saved to: examples/output/example7_heel_angle_comparison.png")

    plt.show()


def example8_custom_styling():
    """
    Example 8: Custom plot styling and colors.

    Demonstrates customization options.
    """
    print("\n" + "=" * 70)
    print("Example 8: Custom Styling")
    print("=" * 70)

    # Configure plot style
    configure_plot_style(grid=True)

    # Create hull and get profile
    hull = create_example_hull()
    profile = hull.get_profile(2.0)

    # Create figure with custom styling
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Custom colors
    plot_profile(
        profile=profile,
        waterline_z=-0.2,
        ax=ax1,
        title="Custom Color Scheme",
        profile_color="darkgreen",
        profile_linewidth=3,
        waterline_color="red",
        waterline_linestyle=":",
        submerged_color="lightgreen",
        submerged_alpha=0.7,
    )

    # Right: Different waterline
    plot_profile(
        profile=profile,
        waterline_z=0.0,
        ax=ax2,
        title="Higher Waterline",
        profile_color="purple",
        waterline_color="orange",
        submerged_color="lavender",
    )

    plt.tight_layout()

    # Save figure
    save_figure(fig, OUTPUT_DIR / "example8_custom_styling.png")
    print("Plot saved to: examples/output/example8_custom_styling.png")

    plt.show()


def example9_3d_different_views():
    """
    Example 9: 3D hull from different viewing angles.

    Shows how viewing angle affects visualization.
    """
    print("\n" + "=" * 70)
    print("Example 9: 3D Hull - Different Views")
    print("=" * 70)

    # Create hull
    hull = create_example_hull()

    # Create figure with multiple 3D subplots
    fig = plt.figure(figsize=(15, 10))

    # View from different angles
    views = [
        {"elev": 20, "azim": -60, "title": "Default View"},
        {"elev": 10, "azim": 0, "title": "Side View"},
        {"elev": 90, "azim": 0, "title": "Top View"},
        {"elev": 0, "azim": 0, "title": "Front View"},
    ]

    for i, view in enumerate(views, 1):
        ax = fig.add_subplot(2, 2, i, projection="3d")
        plot_hull_3d(hull=hull, waterline_z=-0.2, ax=ax, elev=view["elev"], azim=view["azim"])
        ax.set_title(view["title"], fontsize=12, fontweight="bold")

    plt.tight_layout()

    # Save figure
    save_figure(fig, OUTPUT_DIR / "example9_3d_different_views.png", dpi=200)
    print("Plot saved to: examples/output/example9_3d_different_views.png")

    plt.show()


def run_all_examples():
    """Run all examples in sequence."""
    print("\n" + "=" * 70)
    print("PROFILE PLOTTING EXAMPLES")
    print("=" * 70)
    print("\nRunning all examples...")
    print("Note: Close each plot window to proceed to the next example.")

    example1_single_profile_upright()
    example2_single_profile_heeled()
    example3_multiple_profiles()
    example4_hull_3d()
    example5_hull_3d_heeled()
    example6_profile_with_properties()
    example7_heel_angle_comparison()
    example8_custom_styling()
    example9_3d_different_views()

    print("\n" + "=" * 70)
    print("All examples completed!")
    print(f"Output saved to: {OUTPUT_DIR.absolute()}")
    print("=" * 70)


if __name__ == "__main__":
    # Run all examples
    run_all_examples()
