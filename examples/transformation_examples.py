"""
Example script demonstrating coordinate transformation functions.

This script shows how to use heel, trim, and waterline calculations
for kayak hull geometry analysis.
"""

import numpy as np
import matplotlib.pyplot as plt

from src.geometry.point import Point3D
from src.geometry.profile import Profile
from src.geometry.hull import KayakHull
from src.geometry.transformations import (
    apply_heel_to_hull,
    apply_trim_to_hull,
    apply_heel_and_trim_to_hull,
    Waterline,
    find_profile_waterline_intersection,
    calculate_submerged_area,
    calculate_waterplane_area,
)


def create_simple_kayak():
    """Create a simple kayak hull for demonstrations."""
    hull = KayakHull()

    # Define profiles along the length
    # Stern (station 0)
    stern_points = [
        Point3D(0.0, -0.25, 0.15),
        Point3D(0.0, -0.15, 0.05),
        Point3D(0.0, 0.0, 0.0),
        Point3D(0.0, 0.15, 0.05),
        Point3D(0.0, 0.25, 0.15),
    ]
    hull.add_profile(Profile(0.0, stern_points))

    # Forward of stern (station 1)
    points1 = [
        Point3D(1.0, -0.4, 0.18),
        Point3D(1.0, -0.2, 0.06),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 0.2, 0.06),
        Point3D(1.0, 0.4, 0.18),
    ]
    hull.add_profile(Profile(1.0, points1))

    # Midship (station 2.5) - widest point
    midship_points = [
        Point3D(2.5, -0.5, 0.2),
        Point3D(2.5, -0.3, 0.08),
        Point3D(2.5, 0.0, 0.0),
        Point3D(2.5, 0.3, 0.08),
        Point3D(2.5, 0.5, 0.2),
    ]
    hull.add_profile(Profile(2.5, midship_points))

    # Forward of midship (station 4)
    points3 = [
        Point3D(4.0, -0.35, 0.15),
        Point3D(4.0, -0.18, 0.05),
        Point3D(4.0, 0.0, 0.0),
        Point3D(4.0, 0.18, 0.05),
        Point3D(4.0, 0.35, 0.15),
    ]
    hull.add_profile(Profile(4.0, points3))

    # Bow (station 5)
    bow_points = [
        Point3D(5.0, -0.2, 0.12),
        Point3D(5.0, -0.1, 0.03),
        Point3D(5.0, 0.0, 0.0),
        Point3D(5.0, 0.1, 0.03),
        Point3D(5.0, 0.2, 0.12),
    ]
    hull.add_profile(Profile(5.0, bow_points))

    return hull


def plot_hull_3d(ax, hull, label="Hull", color="blue", alpha=0.7, linestyle="-"):
    """Plot hull in 3D."""
    for station in sorted(hull.get_stations()):
        profile = hull.get_profile(station, interpolate=False)
        y = profile.get_y_coordinates()
        z = profile.get_z_coordinates()
        x = np.full_like(y, station)
        ax.plot(x, y, z, color=color, alpha=alpha, linestyle=linestyle, linewidth=1.5)


def example_heel_transformation():
    """Example 1: Heel angle transformation."""
    print("=" * 60)
    print("Example 1: Heel Angle Transformation")
    print("=" * 60)

    hull = create_simple_kayak()

    # Apply different heel angles
    heel_angles = [0, 15, 30, 45]

    fig = plt.figure(figsize=(14, 10))

    for i, heel_angle in enumerate(heel_angles, 1):
        ax = fig.add_subplot(2, 2, i, projection="3d")

        # Apply heel
        heeled_hull = apply_heel_to_hull(hull, heel_angle)

        # Plot original (faint)
        if heel_angle > 0:
            plot_hull_3d(ax, hull, label="Upright", color="gray", alpha=0.2)

        # Plot heeled hull
        plot_hull_3d(ax, heeled_hull, label=f"Heeled {heel_angle}°", color="blue")

        # Add waterline
        y_range = np.linspace(-0.6, 0.6, 20)
        x_range = np.linspace(0, 5, 20)
        Y, X = np.meshgrid(y_range, x_range)
        Z = np.zeros_like(Y) + 0.05  # Waterline at z=0.05
        ax.plot_surface(X, Y, Z, alpha=0.2, color="cyan")

        ax.set_xlabel("X (Longitudinal) [m]")
        ax.set_ylabel("Y (Transverse) [m]")
        ax.set_zlabel("Z (Vertical) [m]")
        ax.set_title(f"Heel Angle: {heel_angle}°")
        ax.set_xlim([-0.5, 5.5])
        ax.set_ylim([-0.6, 0.6])
        ax.set_zlim([-0.3, 0.3])
        ax.invert_zaxis()

    plt.suptitle("Kayak at Different Heel Angles")
    plt.tight_layout()
    plt.savefig("examples/example_heel_transformation.png", dpi=150)
    print("\nPlot saved to: examples/example_heel_transformation.png")
    print(f"Generated {len(heel_angles)} heel configurations\n")


def example_trim_transformation():
    """Example 2: Trim angle transformation."""
    print("=" * 60)
    print("Example 2: Trim Angle Transformation")
    print("=" * 60)

    hull = create_simple_kayak()

    # Apply trim angles
    trim_angles = [-5, 0, 5, 10]  # Negative = bow down, positive = bow up

    fig = plt.figure(figsize=(14, 10))

    for i, trim_angle in enumerate(trim_angles, 1):
        ax = fig.add_subplot(2, 2, i, projection="3d")

        # Apply trim
        if trim_angle == 0:
            trimmed_hull = hull
        else:
            trimmed_hull = apply_trim_to_hull(hull, trim_angle)

        # Plot hull
        plot_hull_3d(ax, trimmed_hull, label=f"Trim {trim_angle}°", color="green")

        # Add waterline
        y_range = np.linspace(-0.6, 0.6, 20)
        x_range = np.linspace(0, 5, 20)
        Y, X = np.meshgrid(y_range, x_range)
        Z = np.zeros_like(Y) + 0.05
        ax.plot_surface(X, Y, Z, alpha=0.2, color="cyan")

        ax.set_xlabel("X (Longitudinal) [m]")
        ax.set_ylabel("Y (Transverse) [m]")
        ax.set_zlabel("Z (Vertical) [m]")

        trim_desc = (
            "Level"
            if trim_angle == 0
            else f"Bow {'Up' if trim_angle > 0 else 'Down'} {abs(trim_angle)}°"
        )
        ax.set_title(f"Trim: {trim_desc}")
        ax.set_xlim([-0.5, 5.5])
        ax.set_ylim([-0.6, 0.6])
        ax.set_zlim([-0.3, 0.3])
        ax.invert_zaxis()

    plt.suptitle("Kayak at Different Trim Angles")
    plt.tight_layout()
    plt.savefig("examples/example_trim_transformation.png", dpi=150)
    print("\nPlot saved to: examples/example_trim_transformation.png")
    print(f"Generated {len(trim_angles)} trim configurations\n")


def example_combined_heel_and_trim():
    """Example 3: Combined heel and trim transformation."""
    print("=" * 60)
    print("Example 3: Combined Heel and Trim")
    print("=" * 60)

    hull = create_simple_kayak()

    # Apply combined transformations
    configs = [
        (0, 0, "Level"),
        (20, 0, "20° Heel Only"),
        (0, 5, "5° Trim (Bow Up) Only"),
        (20, 5, "20° Heel + 5° Trim"),
    ]

    fig = plt.figure(figsize=(14, 10))

    for i, (heel, trim, label) in enumerate(configs, 1):
        ax = fig.add_subplot(2, 2, i, projection="3d")

        # Apply transformation
        if heel == 0 and trim == 0:
            transformed_hull = hull
        else:
            transformed_hull = apply_heel_and_trim_to_hull(hull, heel, trim)

        # Plot
        plot_hull_3d(ax, transformed_hull, label=label, color="purple")

        # Add waterline
        y_range = np.linspace(-0.6, 0.6, 20)
        x_range = np.linspace(0, 5, 20)
        Y, X = np.meshgrid(y_range, x_range)
        Z = np.zeros_like(Y) + 0.05
        ax.plot_surface(X, Y, Z, alpha=0.2, color="cyan")

        ax.set_xlabel("X [m]")
        ax.set_ylabel("Y [m]")
        ax.set_zlabel("Z [m]")
        ax.set_title(label)
        ax.set_xlim([-0.5, 5.5])
        ax.set_ylim([-0.6, 0.6])
        ax.set_zlim([-0.3, 0.3])
        ax.invert_zaxis()

    plt.suptitle("Combined Heel and Trim Transformations")
    plt.tight_layout()
    plt.savefig("examples/example_combined_heel_trim.png", dpi=150)
    print("\nPlot saved to: examples/example_combined_heel_trim.png")
    print(f"Generated {len(configs)} combined configurations\n")


def example_waterline_intersection():
    """Example 4: Waterline intersection calculations."""
    print("=" * 60)
    print("Example 4: Waterline Intersection")
    print("=" * 60)

    hull = create_simple_kayak()

    # Test at different heel angles
    heel_angles = [0, 15, 30]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for ax, heel_angle in zip(axes, heel_angles):
        # Apply heel
        heeled_hull = apply_heel_to_hull(hull, heel_angle)

        # Create waterline
        waterline = Waterline(z_reference=0.05, heel_angle=heel_angle)

        # Get a midship profile
        midship_profile = heeled_hull.get_profile(2.5, interpolate=False)

        # Find waterline intersections
        intersections = find_profile_waterline_intersection(midship_profile, waterline)

        # Plot profile
        y_coords = midship_profile.get_y_coordinates()
        z_coords = midship_profile.get_z_coordinates()
        ax.plot(y_coords, z_coords, "b-o", label="Profile", markersize=4)

        # Plot waterline intersections
        if intersections:
            int_y = [p.y for p in intersections]
            int_z = [p.z for p in intersections]
            ax.plot(
                int_y, int_z, "r*", markersize=15, label=f"Intersections ({len(intersections)})"
            )

        # Plot waterline
        y_range = np.linspace(-0.6, 0.6, 100)
        z_waterline = [waterline.z_at_point(2.5, y) for y in y_range]
        ax.plot(y_range, z_waterline, "c--", label="Waterline", linewidth=2)

        ax.set_xlabel("Y (Transverse) [m]")
        ax.set_ylabel("Z (Vertical) [m]")
        ax.set_title(f"Heel: {heel_angle}°")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axis("equal")
        ax.invert_yaxis()

        # Calculate submerged area
        area = calculate_submerged_area(midship_profile, waterline)
        ax.text(
            0.02,
            0.98,
            f"Submerged Area: {area:.4f} m²",
            transform=ax.transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

    plt.suptitle("Waterline Intersections at Different Heel Angles")
    plt.tight_layout()
    plt.savefig("examples/example_waterline_intersection.png", dpi=150)
    print("\nPlot saved to: examples/example_waterline_intersection.png")
    print(f"Analyzed waterline intersections at {len(heel_angles)} heel angles\n")


def example_waterplane_area():
    """Example 5: Waterplane area calculation."""
    print("=" * 60)
    print("Example 5: Waterplane Area Calculation")
    print("=" * 60)

    hull = create_simple_kayak()

    # Calculate waterplane area at different heel angles
    heel_angles = np.linspace(0, 45, 10)
    waterplane_areas = []

    for heel_angle in heel_angles:
        # Apply heel
        heeled_hull = apply_heel_to_hull(hull, heel_angle)

        # Create waterline
        waterline = Waterline(z_reference=0.05, heel_angle=heel_angle)

        # Calculate waterplane area
        area = calculate_waterplane_area(heeled_hull, waterline, num_stations=30)
        waterplane_areas.append(area)

        print(f"Heel {heel_angle:5.1f}°: Waterplane area = {area:.4f} m²")

    # Plot results
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Plot 1: Waterplane area vs heel angle
    ax1.plot(heel_angles, waterplane_areas, "b-o", linewidth=2, markersize=6)
    ax1.set_xlabel("Heel Angle [degrees]")
    ax1.set_ylabel("Waterplane Area [m²]")
    ax1.set_title("Waterplane Area vs Heel Angle")
    ax1.grid(True, alpha=0.3)

    # Plot 2: Normalized waterplane area
    area_upright = waterplane_areas[0]
    normalized_areas = [a / area_upright for a in waterplane_areas]

    ax2.plot(heel_angles, normalized_areas, "g-o", linewidth=2, markersize=6)
    ax2.axhline(y=1.0, color="r", linestyle="--", alpha=0.5, label="Upright")
    ax2.set_xlabel("Heel Angle [degrees]")
    ax2.set_ylabel("Normalized Waterplane Area")
    ax2.set_title("Relative Change in Waterplane Area")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("examples/example_waterplane_area.png", dpi=150)
    print("\nPlot saved to: examples/example_waterplane_area.png\n")


def main():
    """Run all transformation examples."""
    print("\n" + "=" * 60)
    print("KAYAK HULL TRANSFORMATION EXAMPLES")
    print("=" * 60)

    try:
        example_heel_transformation()
        example_trim_transformation()
        example_combined_heel_and_trim()
        example_waterline_intersection()
        example_waterplane_area()

        print("=" * 60)
        print("All transformation examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
