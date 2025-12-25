"""
Example script demonstrating interpolation functions.

This script shows how to use the various interpolation functions
for kayak hull geometry calculations.
"""

import numpy as np
import matplotlib.pyplot as plt
from src.geometry.point import Point3D
from src.geometry.profile import Profile
from src.geometry.hull import KayakHull
from src.geometry.interpolation import (
    interpolate_transverse,
    interpolate_profile_transverse,
    interpolate_longitudinal,
    interpolate_multiple_profiles,
    interpolate_to_apex,
    create_symmetric_profile,
    resample_profile_uniform_y,
    resample_profile_uniform_arc
)


def example_transverse_interpolation():
    """
    Example 1: Transverse interpolation
    
    Shows how to interpolate points along a single profile to create
    a smoother representation of the cross-section.
    """
    print("=" * 60)
    print("Example 1: Transverse Interpolation")
    print("=" * 60)
    
    # Create a simple profile with few points
    points = [
        Point3D(1.0, -0.5, 0.15),
        Point3D(1.0, -0.25, 0.05),
        Point3D(1.0, 0.0, 0.0),
        Point3D(1.0, 0.25, 0.05),
        Point3D(1.0, 0.5, 0.15)
    ]
    
    print(f"\nOriginal profile has {len(points)} points")
    
    # Interpolate to create more points
    interpolated = interpolate_transverse(points, num_points=20)
    
    print(f"Interpolated profile has {len(interpolated)} points")
    
    # Plot the results
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Original points
    y_orig = [p.y for p in points]
    z_orig = [p.z for p in points]
    ax.plot(y_orig, z_orig, 'ro-', label='Original Points', markersize=8)
    
    # Interpolated points
    y_interp = [p.y for p in interpolated]
    z_interp = [p.z for p in interpolated]
    ax.plot(y_interp, z_interp, 'b.-', label='Interpolated Points', markersize=4)
    
    ax.set_xlabel('Y (Transverse) [m]')
    ax.set_ylabel('Z (Vertical) [m]')
    ax.set_title('Transverse Interpolation Example')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    ax.invert_yaxis()  # Water surface at top
    
    plt.tight_layout()
    plt.savefig('examples/example_transverse_interpolation.png', dpi=150)
    print("\nPlot saved to: examples/example_transverse_interpolation.png")


def example_longitudinal_interpolation():
    """
    Example 2: Longitudinal interpolation
    
    Shows how to interpolate profiles between two stations to create
    intermediate cross-sections.
    """
    print("\n" + "=" * 60)
    print("Example 2: Longitudinal Interpolation")
    print("=" * 60)
    
    # Create two profiles at different stations
    # Station 0.0 - wider profile
    points1 = [
        Point3D(0.0, -0.6, 0.2),
        Point3D(0.0, -0.3, 0.05),
        Point3D(0.0, 0.0, 0.0),
        Point3D(0.0, 0.3, 0.05),
        Point3D(0.0, 0.6, 0.2)
    ]
    profile1 = Profile(0.0, points1)
    
    # Station 2.0 - narrower profile
    points2 = [
        Point3D(2.0, -0.4, 0.15),
        Point3D(2.0, -0.2, 0.03),
        Point3D(2.0, 0.0, 0.0),
        Point3D(2.0, 0.2, 0.03),
        Point3D(2.0, 0.4, 0.15)
    ]
    profile2 = Profile(2.0, points2)
    
    print(f"\nProfile 1 at station {profile1.station} with {len(profile1)} points")
    print(f"Profile 2 at station {profile2.station} with {len(profile2)} points")
    
    # Interpolate intermediate profiles
    target_stations = [0.5, 1.0, 1.5]
    interpolated_profiles = []
    
    for station in target_stations:
        interp_profile = interpolate_longitudinal(profile1, profile2, station)
        interpolated_profiles.append(interp_profile)
        print(f"Interpolated profile at station {station} with {len(interp_profile)} points")
    
    # Plot the results in 3D
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot original profiles
    y1 = profile1.get_y_coordinates()
    z1 = profile1.get_z_coordinates()
    x1 = np.full_like(y1, profile1.station)
    ax.plot(x1, y1, z1, 'ro-', label='Profile 1', markersize=8, linewidth=2)
    
    y2 = profile2.get_y_coordinates()
    z2 = profile2.get_z_coordinates()
    x2 = np.full_like(y2, profile2.station)
    ax.plot(x2, y2, z2, 'bo-', label='Profile 2', markersize=8, linewidth=2)
    
    # Plot interpolated profiles
    colors = ['green', 'orange', 'purple']
    for i, profile in enumerate(interpolated_profiles):
        y = profile.get_y_coordinates()
        z = profile.get_z_coordinates()
        x = np.full_like(y, profile.station)
        ax.plot(x, y, z, color=colors[i], marker='.', 
                label=f'Interpolated at x={profile.station}', markersize=4)
    
    ax.set_xlabel('X (Longitudinal) [m]')
    ax.set_ylabel('Y (Transverse) [m]')
    ax.set_zlabel('Z (Vertical) [m]')
    ax.set_title('Longitudinal Interpolation Example')
    ax.legend()
    ax.invert_zaxis()  # Water surface at top
    
    plt.tight_layout()
    plt.savefig('examples/example_longitudinal_interpolation.png', dpi=150)
    print("\nPlot saved to: examples/example_longitudinal_interpolation.png")


def example_bow_stern_interpolation():
    """
    Example 3: Bow/Stern apex interpolation
    
    Shows how to interpolate profiles from an end profile to an apex point,
    creating the tapering geometry at bow or stern.
    """
    print("\n" + "=" * 60)
    print("Example 3: Bow/Stern Apex Interpolation")
    print("=" * 60)
    
    # Create a bow profile
    bow_profile_points = [
        Point3D(4.0, -0.3, 0.1),
        Point3D(4.0, -0.15, 0.02),
        Point3D(4.0, 0.0, 0.0),
        Point3D(4.0, 0.15, 0.02),
        Point3D(4.0, 0.3, 0.1)
    ]
    bow_profile = Profile(4.0, bow_profile_points)
    
    # Create bow apex point
    bow_apex = Point3D(5.0, 0.0, 0.12)
    
    print(f"\nBow profile at station {bow_profile.station} with {len(bow_profile)} points")
    print(f"Bow apex at x={bow_apex.x}, y={bow_apex.y}, z={bow_apex.z}")
    
    # Interpolate intermediate profiles
    tapered_profiles = interpolate_to_apex(
        bow_profile, 
        bow_apex, 
        num_intermediate_stations=6
    )
    
    print(f"Created {len(tapered_profiles)} intermediate tapered profiles")
    
    # Plot the results in 3D
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot original bow profile
    y_bow = bow_profile.get_y_coordinates()
    z_bow = bow_profile.get_z_coordinates()
    x_bow = np.full_like(y_bow, bow_profile.station)
    ax.plot(x_bow, y_bow, z_bow, 'ro-', label='Bow Profile', markersize=8, linewidth=2)
    
    # Plot apex point
    ax.scatter([bow_apex.x], [bow_apex.y], [bow_apex.z], 
               color='red', s=100, marker='*', label='Bow Apex')
    
    # Plot tapered profiles with color gradient
    cmap = plt.cm.viridis
    for i, profile in enumerate(tapered_profiles):
        y = profile.get_y_coordinates()
        z = profile.get_z_coordinates()
        x = np.full_like(y, profile.station)
        color = cmap(i / len(tapered_profiles))
        ax.plot(x, y, z, color=color, marker='.', markersize=4, alpha=0.7)
    
    ax.set_xlabel('X (Longitudinal) [m]')
    ax.set_ylabel('Y (Transverse) [m]')
    ax.set_zlabel('Z (Vertical) [m]')
    ax.set_title('Bow/Stern Apex Interpolation Example')
    ax.legend()
    ax.invert_zaxis()  # Water surface at top
    
    plt.tight_layout()
    plt.savefig('examples/example_bow_stern_interpolation.png', dpi=150)
    print("\nPlot saved to: examples/example_bow_stern_interpolation.png")


def example_symmetric_profile_creation():
    """
    Example 4: Creating symmetric profiles
    
    Shows how to create a full symmetric profile from just starboard
    side points.
    """
    print("\n" + "=" * 60)
    print("Example 4: Creating Symmetric Profiles")
    print("=" * 60)
    
    # Define only starboard side points (y >= 0)
    starboard_points = [
        Point3D(2.0, 0.0, 0.0),
        Point3D(2.0, 0.15, 0.03),
        Point3D(2.0, 0.3, 0.08),
        Point3D(2.0, 0.45, 0.15)
    ]
    
    print(f"\nStarting with {len(starboard_points)} starboard points")
    
    # Create symmetric profile
    symmetric_profile = create_symmetric_profile(2.0, starboard_points)
    
    print(f"Created symmetric profile with {len(symmetric_profile)} points")
    
    # Plot the results
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Original starboard points
    y_stbd = [p.y for p in starboard_points]
    z_stbd = [p.z for p in starboard_points]
    ax.plot(y_stbd, z_stbd, 'ro-', label='Starboard Points (Input)', markersize=8)
    
    # Complete symmetric profile
    y_sym = symmetric_profile.get_y_coordinates()
    z_sym = symmetric_profile.get_z_coordinates()
    ax.plot(y_sym, z_sym, 'b.-', label='Symmetric Profile', markersize=4)
    
    # Mark centerline
    ax.axvline(x=0, color='gray', linestyle='--', alpha=0.5, label='Centerline')
    
    ax.set_xlabel('Y (Transverse) [m]')
    ax.set_ylabel('Z (Vertical) [m]')
    ax.set_title('Symmetric Profile Creation Example')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    ax.invert_yaxis()  # Water surface at top
    
    plt.tight_layout()
    plt.savefig('examples/example_symmetric_profile.png', dpi=150)
    print("\nPlot saved to: examples/example_symmetric_profile.png")


def example_complete_hull_interpolation():
    """
    Example 5: Complete hull with interpolation
    
    Shows a complete workflow: creating a kayak hull with few profiles,
    then densifying with interpolation.
    """
    print("\n" + "=" * 60)
    print("Example 5: Complete Hull Interpolation")
    print("=" * 60)
    
    # Create a simple kayak hull with 3 profiles
    hull = KayakHull()
    
    # Stern profile (station 0.0)
    stern_points = [
        Point3D(0.0, -0.25, 0.15),
        Point3D(0.0, 0.0, 0.0),
        Point3D(0.0, 0.25, 0.15)
    ]
    hull.add_profile(Profile(0.0, stern_points))
    
    # Midship profile (station 2.0) - widest
    midship_points = [
        Point3D(2.0, -0.5, 0.2),
        Point3D(2.0, -0.25, 0.05),
        Point3D(2.0, 0.0, 0.0),
        Point3D(2.0, 0.25, 0.05),
        Point3D(2.0, 0.5, 0.2)
    ]
    hull.add_profile(Profile(2.0, midship_points))
    
    # Bow profile (station 4.0)
    bow_points = [
        Point3D(4.0, -0.3, 0.12),
        Point3D(4.0, 0.0, 0.0),
        Point3D(4.0, 0.3, 0.12)
    ]
    hull.add_profile(Profile(4.0, bow_points))
    
    print(f"\nOriginal hull has {hull.num_profiles} profiles")
    print(f"Stations: {hull.get_stations()}")
    
    # Interpolate additional profiles
    original_profiles = list(hull.profiles.values())
    target_stations = np.linspace(0.0, 4.0, 21)[1:-1]  # Exclude endpoints
    
    new_profiles = interpolate_multiple_profiles(
        original_profiles,
        target_stations.tolist()
    )
    
    print(f"Interpolated {len(new_profiles)} additional profiles")
    
    # Add interpolated profiles to hull
    for profile in new_profiles:
        hull.update_profile(profile)
    
    print(f"Final hull has {hull.num_profiles} profiles")
    
    # Plot the hull in 3D
    fig = plt.figure(figsize=(14, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot all profiles
    for station in sorted(hull.get_stations()):
        profile = hull.get_profile(station, interpolate=False)
        y = profile.get_y_coordinates()
        z = profile.get_z_coordinates()
        x = np.full_like(y, station)
        
        # Original profiles in red, interpolated in blue
        if station in [0.0, 2.0, 4.0]:
            ax.plot(x, y, z, 'r-', linewidth=2, alpha=0.8)
        else:
            ax.plot(x, y, z, 'b-', linewidth=0.5, alpha=0.5)
    
    # Create a surface mesh
    stations_array = sorted(hull.get_stations())
    num_points_per_profile = 20
    
    X = []
    Y = []
    Z = []
    
    for station in stations_array:
        profile = hull.get_profile(station, interpolate=False)
        # Resample for consistent mesh
        resampled = resample_profile_uniform_y(profile, num_points_per_profile)
        
        X.append([station] * num_points_per_profile)
        Y.append(resampled.get_y_coordinates().tolist())
        Z.append(resampled.get_z_coordinates().tolist())
    
    X = np.array(X)
    Y = np.array(Y)
    Z = np.array(Z)
    
    ax.plot_surface(X, Y, Z, alpha=0.3, cmap='coolwarm')
    
    ax.set_xlabel('X (Longitudinal) [m]')
    ax.set_ylabel('Y (Transverse) [m]')
    ax.set_zlabel('Z (Vertical) [m]')
    ax.set_title('Complete Hull with Interpolated Profiles')
    ax.invert_zaxis()  # Water surface at top
    
    plt.tight_layout()
    plt.savefig('examples/example_complete_hull.png', dpi=150)
    print("\nPlot saved to: examples/example_complete_hull.png")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("KAYAK HULL INTERPOLATION EXAMPLES")
    print("=" * 60)
    
    try:
        example_transverse_interpolation()
        example_longitudinal_interpolation()
        example_bow_stern_interpolation()
        example_symmetric_profile_creation()
        example_complete_hull_interpolation()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
