"""
Examples demonstrating volume integration and displacement calculations.

This script shows how to:
1. Calculate volume using different integration methods
2. Calculate displacement (mass) from volume
3. Compare Simpson's rule vs. trapezoidal rule
4. Generate displacement curves vs. draft
5. Analyze volume distribution along hull length

Run this script with:
    python examples/volume_examples.py
"""

import numpy as np
import matplotlib.pyplot as plt

from src.geometry import Point3D, Profile, KayakHull
from src.hydrostatics import (
    calculate_volume,
    calculate_displacement,
    calculate_displacement_curve,
    calculate_volume_components
)


def create_simple_box_hull(length: float, width: float, depth: float) -> KayakHull:
    """
    Create a simple rectangular box hull for testing.
    
    Args:
        length: Length of box (m)
        width: Width of box (m)
        depth: Depth below waterline (m)
    
    Returns:
        KayakHull with rectangular cross-sections
    """
    hull = KayakHull()
    
    # Create 5 identical rectangular profiles along length
    num_stations = 5
    stations = np.linspace(0, length, num_stations)
    
    half_width = width / 2.0
    
    for station in stations:
        points = [
            Point3D(station, -half_width, 0.0),
            Point3D(station, -half_width, -depth),
            Point3D(station, half_width, -depth),
            Point3D(station, half_width, 0.0),
        ]
        hull.add_profile_from_points(station, points)
    
    return hull


def create_tapered_hull(length: float, max_width: float, depth: float) -> KayakHull:
    """
    Create a tapered hull (wider at center, narrower at ends).
    
    Args:
        length: Length of hull (m)
        max_width: Maximum width at center (m)
        depth: Depth below waterline (m)
    
    Returns:
        KayakHull with tapered cross-sections
    """
    hull = KayakHull()
    
    num_stations = 11
    stations = np.linspace(0, length, num_stations)
    
    for station in stations:
        # Width varies - maximum at center, tapering to zero at ends
        # Using a parabolic taper
        relative_pos = 2 * (station / length - 0.5)  # -1 to 1
        width_factor = 1.0 - relative_pos**2  # 1 at center, 0 at ends
        width = max_width * width_factor
        
        if width < 0.01:  # Minimum width at ends
            width = 0.01
        
        half_width = width / 2.0
        
        # Create V-shaped cross-section
        points = [
            Point3D(station, -half_width, 0.0),
            Point3D(station, 0.0, -depth),
            Point3D(station, half_width, 0.0),
        ]
        hull.add_profile_from_points(station, points)
    
    return hull


def create_realistic_kayak_hull(length: float = 4.5, beam: float = 0.6, depth: float = 0.25) -> KayakHull:
    """
    Create a more realistic kayak hull with varying cross-sections.
    
    Args:
        length: Hull length (m)
        beam: Maximum beam (m)
        depth: Maximum depth (m)
    
    Returns:
        KayakHull with realistic kayak shape
    """
    hull = KayakHull()
    
    num_stations = 15
    stations = np.linspace(0, length, num_stations)
    
    for i, station in enumerate(stations):
        # Relative position (0 to 1)
        t = station / length
        
        # Width varies along length (max at 40% from bow)
        # Using asymmetric distribution
        if t < 0.4:
            width_factor = np.sin(t / 0.4 * np.pi / 2)**0.7
        else:
            width_factor = np.cos((t - 0.4) / 0.6 * np.pi / 2)**0.5
        
        width = beam * width_factor
        
        # Depth varies (deeper at center)
        depth_factor = np.sin(t * np.pi)**0.6
        local_depth = depth * depth_factor
        
        if width < 0.05:
            width = 0.05
        if local_depth < 0.05:
            local_depth = 0.05
        
        half_width = width / 2.0
        
        # Create realistic cross-section with rounded bilges
        points = [
            Point3D(station, -half_width, 0.0),
            Point3D(station, -half_width * 0.9, -local_depth * 0.3),
            Point3D(station, -half_width * 0.6, -local_depth * 0.7),
            Point3D(station, -half_width * 0.2, -local_depth * 0.95),
            Point3D(station, 0.0, -local_depth),
            Point3D(station, half_width * 0.2, -local_depth * 0.95),
            Point3D(station, half_width * 0.6, -local_depth * 0.7),
            Point3D(station, half_width * 0.9, -local_depth * 0.3),
            Point3D(station, half_width, 0.0),
        ]
        hull.add_profile_from_points(station, points)
    
    return hull


def example_1_simple_box_volume():
    """Example 1: Calculate volume of a simple box hull."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Box Hull Volume Calculation")
    print("="*70)
    
    # Create a box: 3m long, 1m wide, 0.5m deep
    length = 3.0
    width = 1.0
    depth = 0.5
    
    hull = create_simple_box_hull(length, width, depth)
    
    print(f"\nBox Hull: {length}m × {width}m × {depth}m")
    print(f"Number of profiles: {len(hull)}")
    
    # Calculate volume using both methods
    vol_simpson = calculate_volume(hull, method='simpson')
    vol_trap = calculate_volume(hull, method='trapezoidal')
    
    # Analytical solution
    vol_analytical = length * width * depth
    
    print(f"\n{'Method':<20} {'Volume (m³)':<15} {'Error (%)':<15}")
    print("-" * 50)
    print(f"{'Analytical':<20} {vol_analytical:<15.6f} {'--':<15}")
    print(f"{'Simpson':<20} {vol_simpson:<15.6f} {abs(vol_simpson - vol_analytical)/vol_analytical * 100:<15.4f}")
    print(f"{'Trapezoidal':<20} {vol_trap:<15.6f} {abs(vol_trap - vol_analytical)/vol_analytical * 100:<15.4f}")
    
    # Calculate displacement
    disp = calculate_displacement(hull, water_density=1000.0)  # Freshwater
    
    print(f"\nDisplacement Properties:")
    print(f"  Volume: {disp.volume:.6f} m³")
    print(f"  Mass: {disp.mass:.2f} kg")
    print(f"  Displacement: {disp.displacement_tons:.4f} tonnes")


def example_2_tapered_hull():
    """Example 2: Tapered hull volume calculation."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Tapered Hull Volume")
    print("="*70)
    
    # Create tapered hull
    length = 4.0
    max_width = 0.8
    depth = 0.3
    
    hull = create_tapered_hull(length, max_width, depth)
    
    print(f"\nTapered Hull:")
    print(f"  Length: {length} m")
    print(f"  Max width: {max_width} m")
    print(f"  Depth: {depth} m")
    print(f"  Number of profiles: {len(hull)}")
    
    # Calculate with both methods
    vol_simpson = calculate_volume(hull, method='simpson')
    vol_trap = calculate_volume(hull, method='trapezoidal')
    
    print(f"\nVolume Calculations:")
    print(f"  Simpson's rule: {vol_simpson:.6f} m³")
    print(f"  Trapezoidal rule: {vol_trap:.6f} m³")
    print(f"  Difference: {abs(vol_simpson - vol_trap):.6f} m³ ({abs(vol_simpson - vol_trap)/vol_simpson * 100:.2f}%)")
    
    # Calculate displacement in seawater
    disp = calculate_displacement(hull, water_density=1025.0)
    
    print(f"\nDisplacement (seawater):")
    print(f"  Mass: {disp.mass:.2f} kg")
    print(f"  Displacement: {disp.displacement_tons:.4f} tonnes")


def example_3_realistic_kayak():
    """Example 3: Realistic kayak hull volume."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Realistic Kayak Hull")
    print("="*70)
    
    # Create realistic kayak
    hull = create_realistic_kayak_hull(length=4.5, beam=0.6, depth=0.25)
    
    print(f"\nKayak Hull:")
    print(f"  Length: {hull.length:.2f} m")
    print(f"  Max beam: {hull.max_beam:.2f} m")
    print(f"  Number of profiles: {len(hull)}")
    
    # Calculate displacement at different waterline levels
    waterlines = [-0.25, -0.20, -0.15, -0.10, -0.05, 0.0]
    
    print(f"\n{'Waterline (m)':<15} {'Draft (m)':<12} {'Volume (m³)':<15} {'Mass (kg)':<12}")
    print("-" * 60)
    
    for wl_z in waterlines:
        disp = calculate_displacement(hull, waterline_z=wl_z, water_density=1025.0)
        draft = -wl_z
        print(f"{wl_z:<15.3f} {draft:<12.3f} {disp.volume:<15.6f} {disp.mass:<12.2f}")


def example_4_integration_method_comparison():
    """Example 4: Compare integration methods with varying station counts."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Integration Method Comparison")
    print("="*70)
    
    # Create a realistic kayak
    hull = create_realistic_kayak_hull()
    
    # Test with different numbers of stations
    station_counts = [5, 10, 20, 30, 50]
    
    print(f"\n{'Stations':<12} {'Simpson (m³)':<15} {'Trapezoidal (m³)':<18} {'Difference (%)':<15}")
    print("-" * 70)
    
    for num_stations in station_counts:
        vol_simp = calculate_volume(hull, num_stations=num_stations, 
                                    use_existing_stations=False, method='simpson')
        vol_trap = calculate_volume(hull, num_stations=num_stations,
                                    use_existing_stations=False, method='trapezoidal')
        diff_pct = abs(vol_simp - vol_trap) / vol_simp * 100
        
        print(f"{num_stations:<12} {vol_simp:<15.6f} {vol_trap:<18.6f} {diff_pct:<15.4f}")
    
    print("\nObservation: As number of stations increases, both methods converge.")


def example_5_volume_distribution():
    """Example 5: Analyze volume distribution along hull length."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Volume Distribution Along Hull")
    print("="*70)
    
    hull = create_realistic_kayak_hull()
    
    # Calculate volume components
    total_vol, stations, vol_components = calculate_volume_components(hull)
    
    print(f"\nTotal volume: {total_vol:.6f} m³")
    print(f"Number of segments: {len(vol_components)}")
    print(f"\nVolume distribution by segment:")
    print(f"{'Segment':<10} {'From (m)':<12} {'To (m)':<12} {'Volume (m³)':<15} {'% of Total':<12}")
    print("-" * 70)
    
    for i, vol_comp in enumerate(vol_components):
        if i < len(stations) - 1:
            pct = vol_comp / total_vol * 100
            print(f"{i+1:<10} {stations[i]:<12.3f} {stations[i+1]:<12.3f} {vol_comp:<15.6f} {pct:<12.2f}")


def example_6_displacement_curve():
    """Example 6: Generate displacement vs. draft curve."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Displacement vs. Draft Curve")
    print("="*70)
    print("\nGenerating displacement curve...")
    
    hull = create_realistic_kayak_hull()
    
    # Calculate for range of waterlines (drafts)
    waterline_levels = np.linspace(-0.25, 0.0, 26)
    displacements = calculate_displacement_curve(hull, waterline_levels, water_density=1025.0)
    
    # Extract data for plotting
    drafts = [-d.waterline_z for d in displacements]
    volumes = [d.volume for d in displacements]
    masses = [d.mass for d in displacements]
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot volume vs draft
    ax1.plot(drafts, volumes, 'b-', linewidth=2, marker='o', markersize=4)
    ax1.set_xlabel('Draft (m)', fontsize=12)
    ax1.set_ylabel('Volume (m³)', fontsize=12)
    ax1.set_title('Volume vs. Draft', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, max(drafts) * 1.05)
    ax1.set_ylim(0, max(volumes) * 1.05)
    
    # Plot mass vs draft
    ax2.plot(drafts, masses, 'r-', linewidth=2, marker='s', markersize=4)
    ax2.set_xlabel('Draft (m)', fontsize=12)
    ax2.set_ylabel('Displacement (kg)', fontsize=12)
    ax2.set_title('Displacement vs. Draft', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, max(drafts) * 1.05)
    ax2.set_ylim(0, max(masses) * 1.05)
    
    plt.tight_layout()
    
    output_file = 'displacement_curve.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Plot saved as: {output_file}")
    
    plt.show()


def example_7_heel_angle_effects():
    """Example 7: Volume changes with heel angle."""
    print("\n" + "="*70)
    print("EXAMPLE 7: Volume at Different Heel Angles")
    print("="*70)
    
    hull = create_realistic_kayak_hull()
    
    # Calculate at different heel angles
    heel_angles = [0, 10, 20, 30, 40, 45]
    
    print(f"\n{'Heel Angle (°)':<15} {'Volume (m³)':<15} {'Mass (kg)':<15}")
    print("-" * 50)
    
    volumes_heel = []
    for heel in heel_angles:
        disp = calculate_displacement(hull, waterline_z=0.0, heel_angle=heel, water_density=1025.0)
        volumes_heel.append(disp.volume)
        print(f"{heel:<15} {disp.volume:<15.6f} {disp.mass:<15.2f}")
    
    print(f"\nNote: Volume may change with heel angle due to asymmetric immersion.")


def example_8_visualization():
    """Example 8: Visualize volume distribution and cross-sections."""
    print("\n" + "="*70)
    print("EXAMPLE 8: Volume Distribution Visualization")
    print("="*70)
    print("\nGenerating visualization...")
    
    hull = create_realistic_kayak_hull()
    
    # Get volume components
    total_vol, stations, vol_components = calculate_volume_components(hull)
    
    # Get cross-sectional areas at each station
    from src.hydrostatics import calculate_section_properties
    areas = []
    for station in stations:
        profile = hull.get_profile(station)
        props = calculate_section_properties(profile, waterline_z=0.0)
        areas.append(props.area)
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(15, 10))
    
    # Plot 1: Cross-sectional area along length
    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(stations, areas, 'b-', linewidth=2, marker='o', markersize=6)
    ax1.fill_between(stations, 0, areas, alpha=0.3)
    ax1.set_xlabel('Station (m)', fontsize=11)
    ax1.set_ylabel('Cross-sectional Area (m²)', fontsize=11)
    ax1.set_title('Area Distribution Along Hull', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Volume components by segment
    ax2 = plt.subplot(2, 2, 2)
    segment_centers = [(stations[i] + stations[i+1])/2 for i in range(len(vol_components))]
    ax2.bar(segment_centers, vol_components, width=stations[1]-stations[0], alpha=0.7, color='green')
    ax2.set_xlabel('Station (m)', fontsize=11)
    ax2.set_ylabel('Segment Volume (m³)', fontsize=11)
    ax2.set_title('Volume by Segment', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Cumulative volume
    ax3 = plt.subplot(2, 2, 3)
    cumulative_vol = np.cumsum([0] + vol_components)
    ax3.plot(stations, cumulative_vol, 'r-', linewidth=2, marker='s', markersize=6)
    ax3.fill_between(stations, 0, cumulative_vol, alpha=0.3, color='red')
    ax3.set_xlabel('Station (m)', fontsize=11)
    ax3.set_ylabel('Cumulative Volume (m³)', fontsize=11)
    ax3.set_title('Cumulative Volume Distribution', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=total_vol, color='k', linestyle='--', alpha=0.5, label=f'Total: {total_vol:.4f} m³')
    ax3.legend()
    
    # Plot 4: Hull profile view (top down)
    ax4 = plt.subplot(2, 2, 4)
    max_widths = []
    for station in stations:
        profile = hull.get_profile(station)
        y_coords = profile.get_y_coordinates()
        max_widths.append(max(abs(y_coords)))
    
    ax4.plot(stations, max_widths, 'b-', linewidth=2, label='Starboard')
    ax4.plot(stations, [-w for w in max_widths], 'b-', linewidth=2, label='Port')
    ax4.fill_between(stations, max_widths, [-w for w in max_widths], alpha=0.2)
    ax4.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax4.set_xlabel('Station (m)', fontsize=11)
    ax4.set_ylabel('Half-beam (m)', fontsize=11)
    ax4.set_title('Hull Plan View', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    ax4.set_aspect('equal')
    
    plt.tight_layout()
    
    output_file = 'volume_distribution.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Plot saved as: {output_file}")
    
    plt.show()


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("VOLUME INTEGRATION AND DISPLACEMENT CALCULATION EXAMPLES")
    print("="*70)
    print("\nThis script demonstrates volume and displacement calculations")
    print("for kayak hulls using numerical integration.")
    
    # Run examples
    example_1_simple_box_volume()
    example_2_tapered_hull()
    example_3_realistic_kayak()
    example_4_integration_method_comparison()
    example_5_volume_distribution()
    example_6_displacement_curve()
    example_7_heel_angle_effects()
    example_8_visualization()
    
    print("\n" + "="*70)
    print("All examples completed successfully!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
