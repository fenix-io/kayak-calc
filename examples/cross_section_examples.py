"""
Examples demonstrating cross-section properties calculations.

This script shows how to:
1. Calculate area and centroid for a single profile (upright condition)
2. Calculate properties for heeled profiles
3. Compare properties across different heel angles
4. Visualize cross-sections with waterline and centroid

Run this script with:
    python examples/cross_section_examples.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from src.geometry import Point3D, Profile
from src.hydrostatics import (
    CrossSectionProperties,
    calculate_section_properties,
    calculate_properties_at_heel_angles
)


def create_rectangular_profile(station: float, width: float, depth: float) -> Profile:
    """
    Create a simple rectangular cross-section for testing.
    
    Args:
        station: Longitudinal position
        width: Total width (beam)
        depth: Total depth below waterline
    
    Returns:
        Profile object with rectangular shape
    """
    half_width = width / 2.0
    points = [
        Point3D(station, -half_width, 0.0),      # Port waterline
        Point3D(station, -half_width, -depth),   # Port bottom
        Point3D(station, half_width, -depth),    # Starboard bottom
        Point3D(station, half_width, 0.0),       # Starboard waterline
    ]
    return Profile(station, points)


def create_v_shaped_profile(station: float, beam: float, depth: float) -> Profile:
    """
    Create a V-shaped cross-section (typical kayak shape).
    
    Args:
        station: Longitudinal position
        beam: Width at waterline
        depth: Depth at centerline
    
    Returns:
        Profile object with V-shape
    """
    half_beam = beam / 2.0
    points = [
        Point3D(station, -half_beam, 0.0),   # Port waterline
        Point3D(station, 0.0, -depth),       # Bottom (keel)
        Point3D(station, half_beam, 0.0),    # Starboard waterline
    ]
    return Profile(station, points)


def create_realistic_kayak_profile(station: float, beam: float, depth: float) -> Profile:
    """
    Create a more realistic kayak cross-section with rounded bilges.
    
    Args:
        station: Longitudinal position
        beam: Width at waterline
        depth: Maximum depth
    
    Returns:
        Profile object with realistic kayak shape
    """
    half_beam = beam / 2.0
    
    # Create points defining kayak shape with smooth curves
    points = [
        Point3D(station, -half_beam, 0.0),           # Port waterline
        Point3D(station, -half_beam * 0.9, -depth * 0.3),  # Port bilge upper
        Point3D(station, -half_beam * 0.6, -depth * 0.7),  # Port bilge lower
        Point3D(station, -half_beam * 0.2, -depth * 0.95), # Port near bottom
        Point3D(station, 0.0, -depth),               # Bottom (keel)
        Point3D(station, half_beam * 0.2, -depth * 0.95),  # Starboard near bottom
        Point3D(station, half_beam * 0.6, -depth * 0.7),   # Starboard bilge lower
        Point3D(station, half_beam * 0.9, -depth * 0.3),   # Starboard bilge upper
        Point3D(station, half_beam, 0.0),            # Starboard waterline
    ]
    return Profile(station, points)


def example_1_basic_calculations():
    """Example 1: Basic area and centroid calculations."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Cross-Section Properties")
    print("="*70)
    
    # Create a rectangular profile (2m wide, 0.5m deep)
    profile = create_rectangular_profile(station=2.0, width=2.0, depth=0.5)
    
    # Calculate properties at upright condition
    props = calculate_section_properties(profile, waterline_z=0.0, heel_angle=0.0)
    
    print(f"\nRectangular Profile (2.0m × 0.5m):")
    print(f"  Station: {props.station:.2f} m")
    print(f"  Waterline Z: {props.waterline_z:.2f} m")
    print(f"  Heel angle: {props.heel_angle:.1f}°")
    print(f"  Area: {props.area:.4f} m²")
    print(f"  Centroid Y: {props.centroid_y:.4f} m (should be ~0 for symmetric)")
    print(f"  Centroid Z: {props.centroid_z:.4f} m (should be ~-0.25)")
    
    # Analytical verification
    expected_area = 2.0 * 0.5  # width × depth
    expected_centroid_z = -0.25  # center of rectangle
    
    print(f"\nAnalytical Verification:")
    print(f"  Expected area: {expected_area:.4f} m²")
    print(f"  Calculated area: {props.area:.4f} m²")
    print(f"  Error: {abs(props.area - expected_area):.6f} m²")
    print(f"  Expected centroid Z: {expected_centroid_z:.4f} m")
    print(f"  Calculated centroid Z: {props.centroid_z:.4f} m")
    print(f"  Error: {abs(props.centroid_z - expected_centroid_z):.6f} m")


def example_2_heel_angle_effects():
    """Example 2: Effects of heel angle on properties."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Heel Angle Effects")
    print("="*70)
    
    # Create a V-shaped profile
    profile = create_v_shaped_profile(station=2.0, beam=1.0, depth=0.3)
    
    # Calculate properties at various heel angles
    heel_angles = [0, 10, 20, 30, 40, 45]
    properties = calculate_properties_at_heel_angles(profile, heel_angles)
    
    print(f"\nV-Shaped Profile (1.0m beam, 0.3m depth):")
    print(f"\n{'Heel (°)':<10} {'Area (m²)':<12} {'Centroid Y (m)':<16} {'Centroid Z (m)':<16}")
    print("-" * 60)
    
    for props in properties:
        print(f"{props.heel_angle:<10.1f} {props.area:<12.6f} {props.centroid_y:<16.6f} {props.centroid_z:<16.6f}")
    
    # Observations
    print("\nObservations:")
    print("  - As heel angle increases, the submerged area may change")
    print("  - Centroid Y shifts to the low (submerged) side")
    print("  - Centroid Z changes due to different immersion pattern")


def example_3_realistic_kayak():
    """Example 3: Realistic kayak cross-section analysis."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Realistic Kayak Cross-Section")
    print("="*70)
    
    # Create a realistic kayak profile
    profile = create_realistic_kayak_profile(station=2.5, beam=0.6, depth=0.25)
    
    # Calculate properties for upright and heeled conditions
    heel_angles = [0, 5, 10, 15, 20, 25, 30]
    properties = calculate_properties_at_heel_angles(profile, heel_angles)
    
    print(f"\nRealistic Kayak Profile (0.6m beam, 0.25m depth):")
    print(f"\n{'Heel (°)':<10} {'Area (m²)':<12} {'Centroid Y (m)':<16} {'Centroid Z (m)':<16}")
    print("-" * 60)
    
    for props in properties:
        print(f"{props.heel_angle:<10.1f} {props.area:<12.6f} {props.centroid_y:<16.6f} {props.centroid_z:<16.6f}")


def example_4_visualization():
    """Example 4: Visualize cross-sections with waterline and centroid."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Visualization of Cross-Sections")
    print("="*70)
    print("\nGenerating plots...")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Cross-Section Properties at Different Heel Angles', fontsize=16, fontweight='bold')
    
    # Create a realistic kayak profile
    profile = create_realistic_kayak_profile(station=2.5, beam=0.6, depth=0.25)
    
    # Heel angles to visualize
    heel_angles = [0, 10, 20, 30, 40, 45]
    
    for idx, (ax, heel_angle) in enumerate(zip(axes.flat, heel_angles)):
        # Calculate properties
        props = calculate_section_properties(profile, waterline_z=0.0, heel_angle=heel_angle)
        
        # Get rotated profile for visualization
        if heel_angle != 0:
            rotated_profile = profile.rotate_about_x(heel_angle)
        else:
            rotated_profile = profile
        
        # Get profile coordinates
        y_coords = rotated_profile.get_y_coordinates()
        z_coords = rotated_profile.get_z_coordinates()
        
        # Plot profile outline
        ax.plot(y_coords, z_coords, 'b-', linewidth=2, label='Hull profile')
        ax.plot(y_coords, z_coords, 'bo', markersize=4)
        
        # Draw waterline
        y_range = [y_coords.min() - 0.1, y_coords.max() + 0.1]
        ax.plot(y_range, [props.waterline_z, props.waterline_z], 'c--', linewidth=1.5, label='Waterline')
        
        # Mark centroid
        if props.area > 0:
            ax.plot(props.centroid_y, props.centroid_z, 'r*', markersize=15, label='Centroid')
            
            # Add crosshairs at centroid
            ax.axhline(y=props.centroid_z, color='r', linestyle=':', alpha=0.3)
            ax.axvline(x=props.centroid_y, color='r', linestyle=':', alpha=0.3)
        
        # Shade submerged area
        submerged_points = rotated_profile._get_submerged_polygon(props.waterline_z)
        if len(submerged_points) >= 3:
            poly_coords = [(p.y, p.z) for p in submerged_points]
            polygon = Polygon(poly_coords, alpha=0.3, facecolor='cyan', edgecolor='blue')
            ax.add_patch(polygon)
        
        # Formatting
        ax.set_xlabel('Y (m)', fontsize=10)
        ax.set_ylabel('Z (m)', fontsize=10)
        ax.set_title(f'Heel: {heel_angle}° | Area: {props.area:.4f} m²', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        ax.legend(fontsize=8, loc='upper right')
        
        # Set consistent axis limits
        ax.set_xlim(-0.4, 0.4)
        ax.set_ylim(-0.3, 0.1)
    
    plt.tight_layout()
    
    # Save the figure
    output_file = 'cross_section_visualization.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved as: {output_file}")
    
    # Show plot
    plt.show()


def example_5_area_vs_heel_curve():
    """Example 5: Plot area and centroid vs. heel angle."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Area and Centroid vs. Heel Angle")
    print("="*70)
    print("\nGenerating plots...")
    
    # Create profiles
    profiles = {
        'Rectangular': create_rectangular_profile(2.0, 2.0, 0.5),
        'V-Shaped': create_v_shaped_profile(2.0, 1.0, 0.3),
        'Realistic Kayak': create_realistic_kayak_profile(2.5, 0.6, 0.25),
    }
    
    # Heel angles to test
    heel_angles = np.linspace(0, 45, 19)
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Cross-Section Properties vs. Heel Angle', fontsize=16, fontweight='bold')
    
    colors = {'Rectangular': 'blue', 'V-Shaped': 'green', 'Realistic Kayak': 'red'}
    
    # Calculate and plot for each profile type
    for name, profile in profiles.items():
        properties = calculate_properties_at_heel_angles(profile, heel_angles.tolist())
        
        areas = [p.area for p in properties]
        centroid_y = [p.centroid_y for p in properties]
        centroid_z = [p.centroid_z for p in properties]
        
        color = colors[name]
        
        # Plot area vs heel
        axes[0, 0].plot(heel_angles, areas, 'o-', color=color, label=name, linewidth=2)
        
        # Plot centroid Y vs heel
        axes[0, 1].plot(heel_angles, centroid_y, 'o-', color=color, label=name, linewidth=2)
        
        # Plot centroid Z vs heel
        axes[1, 0].plot(heel_angles, centroid_z, 'o-', color=color, label=name, linewidth=2)
        
        # Plot centroid trajectory (Y vs Z)
        axes[1, 1].plot(centroid_y, centroid_z, 'o-', color=color, label=name, linewidth=2)
    
    # Format plots
    axes[0, 0].set_xlabel('Heel Angle (°)', fontsize=11)
    axes[0, 0].set_ylabel('Submerged Area (m²)', fontsize=11)
    axes[0, 0].set_title('Area vs. Heel Angle', fontsize=12, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()
    
    axes[0, 1].set_xlabel('Heel Angle (°)', fontsize=11)
    axes[0, 1].set_ylabel('Centroid Y (m)', fontsize=11)
    axes[0, 1].set_title('Transverse Centroid Position vs. Heel', fontsize=12, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend()
    axes[0, 1].axhline(y=0, color='k', linestyle='--', alpha=0.5)
    
    axes[1, 0].set_xlabel('Heel Angle (°)', fontsize=11)
    axes[1, 0].set_ylabel('Centroid Z (m)', fontsize=11)
    axes[1, 0].set_title('Vertical Centroid Position vs. Heel', fontsize=12, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].legend()
    
    axes[1, 1].set_xlabel('Centroid Y (m)', fontsize=11)
    axes[1, 1].set_ylabel('Centroid Z (m)', fontsize=11)
    axes[1, 1].set_title('Centroid Trajectory', fontsize=12, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].legend()
    axes[1, 1].set_aspect('equal')
    axes[1, 1].axvline(x=0, color='k', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    
    # Save the figure
    output_file = 'properties_vs_heel_angle.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved as: {output_file}")
    
    # Show plot
    plt.show()


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("CROSS-SECTION PROPERTIES CALCULATION EXAMPLES")
    print("="*70)
    print("\nThis script demonstrates the calculation of hydrostatic properties")
    print("for transverse cross-sections of kayak hulls.")
    
    # Run examples
    example_1_basic_calculations()
    example_2_heel_angle_effects()
    example_3_realistic_kayak()
    example_4_visualization()
    example_5_area_vs_heel_curve()
    
    print("\n" + "="*70)
    print("All examples completed successfully!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
