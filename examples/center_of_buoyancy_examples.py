"""
Center of Buoyancy Calculation Examples

This script demonstrates how to calculate the center of buoyancy (CB) for
kayak hulls using different methods and configurations.

The center of buoyancy is the centroid of the displaced volume - the point
through which the buoyant force acts.

Examples include:
1. Basic CB calculation for box hull
2. CB at different waterlines
3. CB at different heel angles
4. CB for realistic kayak hull
5. CB convergence with station refinement
6. CB movement visualization
"""

import numpy as np
import matplotlib.pyplot as plt
from src.geometry import Point3D, KayakHull
from src.hydrostatics import (
    calculate_center_of_buoyancy,
    calculate_cb_curve,
    calculate_cb_at_heel_angles,
    validate_center_of_buoyancy,
)


def create_box_hull(length: float, width: float, depth: float, num_stations: int = 5) -> KayakHull:
    """Create a simple box-shaped hull for testing."""
    hull = KayakHull()
    half_width = width / 2.0

    stations = np.linspace(0, length, num_stations)

    for station in stations:
        points = [
            Point3D(station, -half_width, 0.0),
            Point3D(station, -half_width, -depth),
            Point3D(station, half_width, -depth),
            Point3D(station, half_width, 0.0),
        ]
        hull.add_profile_from_points(station, points)

    return hull


def create_tapered_hull(
    length: float, max_width: float, depth: float, num_stations: int = 11
) -> KayakHull:
    """Create a tapered hull (narrower at bow and stern)."""
    hull = KayakHull()

    stations = np.linspace(0, length, num_stations)

    for station in stations:
        # Width varies from 0 at ends to max at middle
        t = 2 * abs(station - length / 2) / length  # 0 at center, 1 at ends
        width = max_width * (1 - t)
        half_width = width / 2.0

        if width > 0.01:
            points = [
                Point3D(station, -half_width, 0.0),
                Point3D(station, -half_width, -depth),
                Point3D(station, half_width, -depth),
                Point3D(station, half_width, 0.0),
            ]
            hull.add_profile_from_points(station, points)

    return hull


def create_realistic_kayak_hull(
    length: float = 4.5, max_beam: float = 0.6, num_stations: int = 15
) -> KayakHull:
    """Create a more realistic kayak hull with curved profiles."""
    hull = KayakHull()

    stations = np.linspace(0, length, num_stations)

    for station in stations:
        # Beam varies with station (widest at center)
        t = 2 * abs(station - length / 2) / length
        beam_factor = 1 - t**1.5  # Smoother taper
        beam = max_beam * beam_factor
        half_beam = beam / 2.0

        # Depth varies (deeper at center)
        depth = 0.25 * beam_factor + 0.05

        if beam > 0.01:
            # Create rounded profile (more realistic)
            num_points = 9
            y_coords = np.linspace(-half_beam, half_beam, num_points)

            # Rounded bottom (parabolic shape)
            z_coords = []
            for y in y_coords:
                # Parabolic bottom, flat at waterline
                z_bottom = -depth * (1 - (2 * y / beam) ** 2)
                z_coords.append(z_bottom)

            points = [Point3D(station, y, z) for y, z in zip(y_coords, z_coords)]
            hull.add_profile_from_points(station, points)

    return hull


def example_1_basic_cb():
    """Example 1: Basic CB calculation for box hull."""
    print("=" * 70)
    print("EXAMPLE 1: Basic Center of Buoyancy Calculation")
    print("=" * 70)

    # Create a simple box hull
    hull = create_box_hull(3.0, 1.0, 0.5, num_stations=7)

    print("\nBox Hull: 3.0m × 1.0m × 0.5m")
    print(f"Number of profiles: {hull.num_profiles}")

    # Calculate CB at design waterline
    cb = calculate_center_of_buoyancy(hull, waterline_z=0.0, heel_angle=0.0)

    print("\nCenter of Buoyancy:")
    print(f"  LCB (Longitudinal): {cb.lcb:.6f} m")
    print(f"  VCB (Vertical):     {cb.vcb:.6f} m")
    print(f"  TCB (Transverse):   {cb.tcb:.6f} m")
    print(f"  Volume:             {cb.volume:.6f} m³")

    # Validate
    is_valid, issues = validate_center_of_buoyancy(cb, hull)
    print(f"\nValidation: {'PASS' if is_valid else 'FAIL'}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")

    # For fully submerged uniform box:
    expected_lcb = 1.5  # Midpoint of length
    expected_vcb = -0.25  # Midpoint of depth

    print(f"\nExpected values (analytical):")
    print(f"  LCB: {expected_lcb:.6f} m")
    print(f"  VCB: {expected_vcb:.6f} m")
    print(f"  TCB: 0.000000 m (centerline)")

    print(f"\nError:")
    print(f"  LCB: {abs(cb.lcb - expected_lcb):.6f} m")
    print(f"  VCB: {abs(cb.vcb - expected_vcb):.6f} m")


def example_2_cb_at_waterlines():
    """Example 2: CB at different waterlines."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Center of Buoyancy at Different Waterlines")
    print("=" * 70)

    hull = create_box_hull(3.0, 1.0, 0.5, num_stations=7)

    print("\nBox Hull: 3.0m × 1.0m × 0.5m (bottom at -0.5)")

    # Calculate CB at multiple waterlines
    waterlines = [-0.4, -0.3, -0.2, -0.1, 0.0]
    cb_curve = calculate_cb_curve(hull, waterlines)

    print(f"\nWaterline (m)   Draft (m)    LCB (m)      VCB (m)      Volume (m³)")
    print("-" * 75)

    for wl, cb in zip(waterlines, cb_curve):
        draft = 0.0 - wl  # Draft is distance from waterline to keel
        print(
            f"{wl:>8.3f}       {draft:>8.3f}    "
            f"{cb.lcb:>8.6f}   {cb.vcb:>8.6f}   {cb.volume:>10.6f}"
        )

    print("\nObservations:")
    print("  - LCB remains constant (hull is uniform along length)")
    print("  - VCB moves down as more volume is submerged")
    print("  - Volume increases linearly with draft (prismatic hull)")


def example_3_cb_at_heel_angles():
    """Example 3: CB at different heel angles."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Center of Buoyancy at Different Heel Angles")
    print("=" * 70)

    hull = create_box_hull(3.0, 1.0, 0.5, num_stations=7)

    print("\nBox Hull: 3.0m × 1.0m × 0.5m")
    print("Waterline at 0.0 m")

    # Calculate CB at different heel angles
    heel_angles = [0, 5, 10, 15, 20, 25, 30]
    cb_at_heels = calculate_cb_at_heel_angles(hull, heel_angles, waterline_z=0.0)

    print(f"\nHeel (°)    LCB (m)      VCB (m)      TCB (m)      Volume (m³)")
    print("-" * 75)

    for angle, cb in zip(heel_angles, cb_at_heels):
        print(
            f"{angle:>5.0f}      {cb.lcb:>8.6f}   {cb.vcb:>8.6f}   {cb.tcb:>8.6f}   {cb.volume:>10.6f}"
        )

    print("\nObservations:")
    print("  - TCB moves to the side as hull heels")
    print("  - LCB and VCB may change slightly due to asymmetric submersion")
    print("  - Volume may change if waterline cuts hull differently when heeled")


def example_4_realistic_kayak():
    """Example 4: CB for realistic kayak hull."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Center of Buoyancy for Realistic Kayak Hull")
    print("=" * 70)

    # Create a realistic kayak hull
    hull = create_realistic_kayak_hull(length=4.5, max_beam=0.6, num_stations=15)

    print("\nRealistic Kayak Hull:")
    print(f"  Length: 4.50 m")
    print(f"  Max beam: 0.60 m")
    print(f"  Number of profiles: {hull.num_profiles}")

    # Calculate CB at design waterline
    cb = calculate_center_of_buoyancy(hull, waterline_z=0.0)

    print("\nCenter of Buoyancy at design waterline:")
    print(f"  LCB: {cb.lcb:.6f} m from origin")
    print(f"  VCB: {cb.vcb:.6f} m (below waterline)")
    print(f"  TCB: {cb.tcb:.6f} m (from centerline)")
    print(f"  Volume: {cb.volume:.6f} m³")

    # Calculate percentage along length
    lcb_percent = (cb.lcb / 4.5) * 100
    print(f"\nLCB position: {lcb_percent:.1f}% of hull length")
    print(f"(50% would be exactly at midpoint)")


def example_5_convergence():
    """Example 5: CB convergence with station refinement."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: CB Convergence with Station Refinement")
    print("=" * 70)

    hull = create_tapered_hull(4.0, 0.8, 0.3, num_stations=21)

    print("\nTapered Hull: 4.0m length, 0.8m max width")

    # Calculate CB with different numbers of stations
    station_counts = [5, 10, 20, 30, 50]

    print(f"\nStations    LCB (m)      VCB (m)      TCB (m)      Volume (m³)")
    print("-" * 75)

    results = []
    for n_stations in station_counts:
        cb = calculate_center_of_buoyancy(
            hull, num_stations=n_stations, use_existing_stations=False, method="simpson"
        )
        results.append(cb)
        print(
            f"{n_stations:>5}      {cb.lcb:>8.6f}   {cb.vcb:>8.6f}   {cb.tcb:>8.6f}   {cb.volume:>10.6f}"
        )

    print("\nObservation: Values should converge as number of stations increases.")


def example_6_cb_movement_visualization():
    """Example 6: Visualize CB movement with waterline."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: CB Movement Visualization")
    print("=" * 70)

    hull = create_realistic_kayak_hull(length=4.5, max_beam=0.6, num_stations=21)

    print("\nCalculating CB at multiple waterlines...")

    # Calculate CB at many waterlines
    waterlines = np.linspace(-0.25, 0.0, 15)
    cb_curve = calculate_cb_curve(hull, waterlines.tolist())

    # Extract data for plotting
    lcbs = [cb.lcb for cb in cb_curve]
    vcbs = [cb.vcb for cb in cb_curve]
    volumes = [cb.volume for cb in cb_curve]

    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Plot 1: LCB vs Waterline
    axes[0, 0].plot(waterlines, lcbs, "b-o", linewidth=2, markersize=4)
    axes[0, 0].set_xlabel("Waterline Z (m)")
    axes[0, 0].set_ylabel("LCB (m)")
    axes[0, 0].set_title("Longitudinal Center of Buoyancy vs Waterline")
    axes[0, 0].grid(True, alpha=0.3)

    # Plot 2: VCB vs Waterline
    axes[0, 1].plot(waterlines, vcbs, "g-o", linewidth=2, markersize=4)
    axes[0, 1].set_xlabel("Waterline Z (m)")
    axes[0, 1].set_ylabel("VCB (m)")
    axes[0, 1].set_title("Vertical Center of Buoyancy vs Waterline")
    axes[0, 1].grid(True, alpha=0.3)

    # Plot 3: Volume vs Waterline
    axes[1, 0].plot(waterlines, volumes, "r-o", linewidth=2, markersize=4)
    axes[1, 0].set_xlabel("Waterline Z (m)")
    axes[1, 0].set_ylabel("Volume (m³)")
    axes[1, 0].set_title("Displaced Volume vs Waterline")
    axes[1, 0].grid(True, alpha=0.3)

    # Plot 4: CB trajectory (LCB vs VCB)
    axes[1, 1].plot(lcbs, vcbs, "purple", linewidth=2, marker="o", markersize=4)
    axes[1, 1].set_xlabel("LCB (m)")
    axes[1, 1].set_ylabel("VCB (m)")
    axes[1, 1].set_title("CB Trajectory (LCB vs VCB)")
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].axis("equal")

    # Add arrows to show direction of increasing waterline
    for i in range(0, len(lcbs) - 1, 3):
        dx = lcbs[i + 1] - lcbs[i]
        dy = vcbs[i + 1] - vcbs[i]
        if abs(dx) > 0.001 or abs(dy) > 0.001:
            axes[1, 1].arrow(
                lcbs[i],
                vcbs[i],
                dx * 0.7,
                dy * 0.7,
                head_width=0.02,
                head_length=0.01,
                fc="purple",
                ec="purple",
            )

    plt.tight_layout()
    plt.savefig("cb_movement.png", dpi=150, bbox_inches="tight")
    print(f"\nVisualization saved as 'cb_movement.png'")

    try:
        plt.show()
    except BaseException:
        pass  # In case display is not available


def example_7_cb_with_heel():
    """Example 7: Visualize CB movement with heel angle."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: CB Movement with Heel Angle")
    print("=" * 70)

    hull = create_box_hull(3.0, 1.0, 0.5, num_stations=11)

    print("\nCalculating CB at multiple heel angles...")

    # Calculate CB at heel angles from 0 to 30 degrees
    heel_angles = np.linspace(0, 30, 16)
    cb_at_heels = calculate_cb_at_heel_angles(hull, heel_angles.tolist(), waterline_z=0.0)

    # Extract data
    lcbs = [cb.lcb for cb in cb_at_heels]
    vcbs = [cb.vcb for cb in cb_at_heels]
    tcbs = [cb.tcb for cb in cb_at_heels]
    volumes = [cb.volume for cb in cb_at_heels]

    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Plot 1: TCB vs Heel Angle
    axes[0, 0].plot(heel_angles, tcbs, "b-o", linewidth=2, markersize=4)
    axes[0, 0].set_xlabel("Heel Angle (°)")
    axes[0, 0].set_ylabel("TCB (m)")
    axes[0, 0].set_title("Transverse Center of Buoyancy vs Heel Angle")
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].axhline(y=0, color="k", linestyle="--", alpha=0.3)

    # Plot 2: LCB vs Heel Angle
    axes[0, 1].plot(heel_angles, lcbs, "g-o", linewidth=2, markersize=4)
    axes[0, 1].set_xlabel("Heel Angle (°)")
    axes[0, 1].set_ylabel("LCB (m)")
    axes[0, 1].set_title("Longitudinal Center of Buoyancy vs Heel Angle")
    axes[0, 1].grid(True, alpha=0.3)

    # Plot 3: VCB vs Heel Angle
    axes[1, 0].plot(heel_angles, vcbs, "r-o", linewidth=2, markersize=4)
    axes[1, 0].set_xlabel("Heel Angle (°)")
    axes[1, 0].set_ylabel("VCB (m)")
    axes[1, 0].set_title("Vertical Center of Buoyancy vs Heel Angle")
    axes[1, 0].grid(True, alpha=0.3)

    # Plot 4: Volume vs Heel Angle
    axes[1, 1].plot(heel_angles, volumes, "purple", linewidth=2, marker="o", markersize=4)
    axes[1, 1].set_xlabel("Heel Angle (°)")
    axes[1, 1].set_ylabel("Volume (m³)")
    axes[1, 1].set_title("Displaced Volume vs Heel Angle")
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("cb_heel_angle.png", dpi=150, bbox_inches="tight")
    print(f"\nVisualization saved as 'cb_heel_angle.png'")

    try:
        plt.show()
    except BaseException:
        pass


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("CENTER OF BUOYANCY CALCULATION EXAMPLES")
    print("=" * 70)

    print("\nThis script demonstrates center of buoyancy (CB) calculations")
    print("for kayak hulls using numerical integration.")
    print("\nThe center of buoyancy is the centroid of the displaced volume,")
    print("i.e., the point through which the buoyant force acts.")

    # Run examples
    example_1_basic_cb()
    example_2_cb_at_waterlines()
    example_3_cb_at_heel_angles()
    example_4_realistic_kayak()
    example_5_convergence()
    example_6_cb_movement_visualization()
    example_7_cb_with_heel()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
