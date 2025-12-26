"""
Examples demonstrating data input/output functionality.

This script shows how to:
1. Load hull geometry from JSON files
2. Load hull geometry from CSV files
3. Validate data before loading
4. Handle loading errors
5. Save hull geometry to files
6. Work with metadata
7. Inspect loaded hull properties
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.io import (
    load_hull_from_json,
    load_hull_from_csv,
    save_hull_to_json,
    save_hull_to_csv,
    validate_hull_data,
    get_default_metadata,
    format_metadata_for_display,
    DataLoadError,
)
from src.geometry.hull import KayakHull
from src.geometry.profile import Profile
from src.geometry.point import Point3D


def example_1_load_from_json():
    """Example 1: Load hull geometry from a JSON file."""
    print("=" * 70)
    print("Example 1: Load hull from JSON file")
    print("=" * 70)
    
    # Load the sample hull
    hull = load_hull_from_json('data/sample_hull_simple.json')
    
    print(f"Successfully loaded hull from JSON")
    print(f"Number of profiles: {hull.num_profiles}")
    print(f"Stations: {hull.get_stations()}")
    print(f"Hull length: {hull.length:.2f} m")
    print(f"Maximum beam: {hull.max_beam:.2f} m")
    
    # Inspect metadata
    if hasattr(hull, 'metadata'):
        print("\nMetadata:")
        print(format_metadata_for_display(hull.metadata))
    
    print()


def example_2_load_from_csv():
    """Example 2: Load hull geometry from a CSV file."""
    print("=" * 70)
    print("Example 2: Load hull from CSV file")
    print("=" * 70)
    
    # Load the sample hull
    hull = load_hull_from_csv('data/sample_hull_simple.csv', format_type='xyz')
    
    print(f"Successfully loaded hull from CSV")
    print(f"Number of profiles: {hull.num_profiles}")
    print(f"Stations: {hull.get_stations()}")
    
    # Inspect first profile
    first_station = hull.get_stations()[0]
    profile = hull.get_profile(first_station)
    print(f"\nFirst profile at station {first_station}:")
    print(f"  Number of points: {len(profile.points)}")
    print(f"  First point: ({profile.points[0].x:.2f}, {profile.points[0].y:.2f}, {profile.points[0].z:.2f})")
    
    print()


def example_3_load_realistic_kayak():
    """Example 3: Load a more realistic kayak hull."""
    print("=" * 70)
    print("Example 3: Load realistic kayak hull")
    print("=" * 70)
    
    hull = load_hull_from_json('data/sample_hull_kayak.json')
    
    print(f"Successfully loaded realistic kayak hull")
    print(f"Number of profiles: {hull.num_profiles}")
    print(f"Stations: {[f'{s:.2f}' for s in hull.get_stations()]}")
    print(f"Hull length: {hull.length:.2f} m")
    print(f"Maximum beam: {hull.max_beam:.2f} m")
    
    if hasattr(hull, 'metadata'):
        print(f"\nKayak name: {hull.metadata.get('name', 'Unknown')}")
        print(f"Description: {hull.metadata.get('description', 'N/A')}")
    
    print()


def example_4_validate_before_loading():
    """Example 4: Validate data before loading (demonstrating validation)."""
    print("=" * 70)
    print("Example 4: Data validation")
    print("=" * 70)
    
    import json
    
    # Load and validate sample data
    with open('data/sample_hull_simple.json', 'r') as f:
        hull_data = json.load(f)
    
    # Validate the data
    is_valid, errors = validate_hull_data(hull_data)
    
    if is_valid:
        print("✓ Data validation passed!")
        print(f"  - {hull_data['metadata'].get('name', 'Unnamed hull')}")
        print(f"  - {len(hull_data['profiles'])} profiles")
        hull = load_hull_from_json('data/sample_hull_simple.json')
        print(f"  - Hull loaded successfully")
    else:
        print("✗ Data validation failed:")
        for error in errors:
            print(f"  - {error}")
    
    print()


def example_5_handle_errors():
    """Example 5: Handle loading errors gracefully."""
    print("=" * 70)
    print("Example 5: Error handling")
    print("=" * 70)
    
    # Try to load a non-existent file
    try:
        hull = load_hull_from_json('data/nonexistent_file.json')
        print("This shouldn't print")
    except FileNotFoundError as e:
        print(f"✓ Caught expected error: {e}")
    
    # Try to load invalid JSON
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json }")
        temp_path = f.name
    
    try:
        hull = load_hull_from_json(temp_path)
        print("This shouldn't print")
    except DataLoadError as e:
        print(f"✓ Caught expected error: Invalid JSON detected")
    finally:
        Path(temp_path).unlink()
    
    print()


def example_6_save_hull():
    """Example 6: Save hull to JSON and CSV files."""
    print("=" * 70)
    print("Example 6: Save hull to files")
    print("=" * 70)
    
    # Load a hull
    hull = load_hull_from_json('data/sample_hull_simple.json')
    
    # Save to JSON
    output_dir = Path('examples/output')
    output_dir.mkdir(exist_ok=True)
    
    json_path = output_dir / 'saved_hull.json'
    metadata = {
        'name': 'Saved Example Hull',
        'description': 'Hull saved from example script',
        'units': 'm'
    }
    save_hull_to_json(hull, json_path, metadata)
    print(f"✓ Saved hull to {json_path}")
    
    # Save to CSV
    csv_path = output_dir / 'saved_hull.csv'
    save_hull_to_csv(hull, csv_path, format_type='xyz', metadata=metadata)
    print(f"✓ Saved hull to {csv_path}")
    
    # Verify by loading back
    reloaded_hull = load_hull_from_json(json_path)
    print(f"✓ Successfully reloaded hull from {json_path}")
    print(f"  Profiles: {reloaded_hull.num_profiles}")
    
    print()


def example_7_work_with_metadata():
    """Example 7: Work with metadata."""
    print("=" * 70)
    print("Example 7: Working with metadata")
    print("=" * 70)
    
    # Get default metadata
    defaults = get_default_metadata()
    print("Default metadata:")
    print(format_metadata_for_display(defaults))
    
    # Load hull with custom metadata
    hull = load_hull_from_csv(
        'data/sample_hull_simple.csv',
        metadata={
            'name': 'Custom Named Hull',
            'description': 'Hull with custom metadata',
            'units': 'ft',  # Override default
        }
    )
    
    print("\nLoaded hull with custom metadata:")
    if hasattr(hull, 'metadata'):
        print(format_metadata_for_display(hull.metadata))
    
    print()


def example_8_inspect_profiles():
    """Example 8: Inspect profile details."""
    print("=" * 70)
    print("Example 8: Inspect profile details")
    print("=" * 70)
    
    hull = load_hull_from_json('data/sample_hull_kayak.json')
    
    print(f"Hull has {hull.num_profiles} profiles\n")
    
    # Inspect each profile
    for i, station in enumerate(hull.get_stations()):
        profile = hull.get_profile(station)
        
        # Calculate some basic stats
        y_coords = [pt.y for pt in profile.points]
        z_coords = [pt.z for pt in profile.points]
        
        max_beam = max(y_coords) - min(y_coords)
        max_height = max(z_coords) - min(z_coords)
        
        print(f"Profile {i+1} at station {station:.2f} m:")
        print(f"  Points: {len(profile.points)}")
        print(f"  Beam: {max_beam:.3f} m")
        print(f"  Height: {max_height:.3f} m")
    
    print()


def example_9_csv_formats():
    """Example 9: Different CSV format options."""
    print("=" * 70)
    print("Example 9: CSV format options")
    print("=" * 70)
    
    # Create a simple hull
    hull = KayakHull()
    profile1 = Profile(0.0, [
        Point3D(0.0, 0.0, 1.0),
        Point3D(0.0, 0.5, 0.5),
        Point3D(0.0, -0.5, 0.5)
    ])
    profile2 = Profile(1.0, [
        Point3D(1.0, 0.0, 1.0),
        Point3D(1.0, 0.5, 0.5),
        Point3D(1.0, -0.5, 0.5)
    ])
    hull.add_profile(profile1)
    hull.add_profile(profile2)
    
    output_dir = Path('examples/output')
    output_dir.mkdir(exist_ok=True)
    
    # Save in xyz format
    xyz_path = output_dir / 'hull_xyz.csv'
    save_hull_to_csv(hull, xyz_path, format_type='xyz')
    print(f"✓ Saved in xyz format to {xyz_path}")
    
    # Save in station_yz format
    station_yz_path = output_dir / 'hull_station_yz.csv'
    save_hull_to_csv(hull, station_yz_path, format_type='station_yz')
    print(f"✓ Saved in station_yz format to {station_yz_path}")
    
    # Load both back
    hull_xyz = load_hull_from_csv(xyz_path, format_type='xyz')
    hull_station_yz = load_hull_from_csv(station_yz_path, format_type='station_yz')
    
    print(f"✓ Both formats loaded successfully")
    print(f"  xyz format: {hull_xyz.num_profiles} profiles")
    print(f"  station_yz format: {hull_station_yz.num_profiles} profiles")
    
    print()


def example_10_round_trip():
    """Example 10: Complete round-trip (load → modify → save → reload)."""
    print("=" * 70)
    print("Example 10: Complete round-trip workflow")
    print("=" * 70)
    
    # Load original hull
    print("Step 1: Load original hull...")
    original_hull = load_hull_from_json('data/sample_hull_simple.json')
    print(f"  Loaded {original_hull.num_profiles} profiles")
    
    # Inspect
    print(f"\nStep 2: Inspect hull properties...")
    print(f"  Length: {original_hull.length:.2f} m")
    print(f"  Beam: {original_hull.max_beam:.2f} m")
    
    # Save to new location
    print(f"\nStep 3: Save to new location...")
    output_dir = Path('examples/output')
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / 'round_trip_hull.json'
    
    save_hull_to_json(
        original_hull,
        output_path,
        metadata={
            'name': 'Round Trip Test Hull',
            'description': 'Hull that has been saved and reloaded',
        }
    )
    print(f"  Saved to {output_path}")
    
    # Reload
    print(f"\nStep 4: Reload from saved file...")
    reloaded_hull = load_hull_from_json(output_path)
    print(f"  Loaded {reloaded_hull.num_profiles} profiles")
    
    # Verify properties match
    print(f"\nStep 5: Verify properties...")
    assert original_hull.num_profiles == reloaded_hull.num_profiles
    assert abs(original_hull.length - reloaded_hull.length) < 0.001
    assert abs(original_hull.max_beam - reloaded_hull.max_beam) < 0.001
    print(f"  ✓ All properties match!")
    
    print()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "DATA INPUT/OUTPUT EXAMPLES" + " " * 27 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    examples = [
        example_1_load_from_json,
        example_2_load_from_csv,
        example_3_load_realistic_kayak,
        example_4_validate_before_loading,
        example_5_handle_errors,
        example_6_save_hull,
        example_7_work_with_metadata,
        example_8_inspect_profiles,
        example_9_csv_formats,
        example_10_round_trip,
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"ERROR in {example_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == '__main__':
    main()
