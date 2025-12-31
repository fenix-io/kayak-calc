"""
Example: Creating Multi-Point Bow and Stern Definitions

This script demonstrates how to:
1. Design kayak hulls with multi-point bow/stern arrays
2. Control rocker curves at different vertical levels
3. Generate JSON files with multi-point definitions
4. Visualize the results

Multi-point bow/stern provides independent control over the longitudinal
position of different levels (keel, chines, gunwale), enabling realistic
hull shapes with proper rocker characteristics.
"""

import json
from pathlib import Path
from src.visualization import plot_profile_view, plot_plan_view, plot_hull_3d
import matplotlib.pyplot as plt


def create_multipoint_hull_example1():
    """
    Example 1: Traditional Sea Kayak with Moderate Rocker

    Features:
    - Keel extends further forward/aft than gunwale
    - Pronounced bow/stern rocker
    - Four vertical levels (gunwale, 2 chines, keel)
    """
    hull_data = {
        "metadata": {
            "name": "Traditional Sea Kayak",
            "description": "Multi-point bow/stern with moderate rocker for good tracking and maneuverability",
            "units": "m",
            "coordinate_system": "bow_origin",
            "water_density": 1025.0,
            "length": 5.2,
            "beam": 0.55,
        },
        "bow": [
            {"x": 0.0, "y": 0.0, "z": 0.50, "level": "gunwale"},
            {"x": 0.15, "y": 0.0, "z": 0.10, "level": "chine_upper"},
            {"x": 0.25, "y": 0.0, "z": -0.05, "level": "chine_lower"},
            {"x": 0.45, "y": 0.0, "z": -0.18, "level": "keel"},
        ],
        "stern": [
            {"x": 5.2, "y": 0.0, "z": 0.48, "level": "gunwale"},
            {"x": 5.05, "y": 0.0, "z": 0.08, "level": "chine_upper"},
            {"x": 4.90, "y": 0.0, "z": -0.08, "level": "chine_lower"},
            {"x": 4.70, "y": 0.0, "z": -0.20, "level": "keel"},
        ],
        "profiles": [
            {
                "station": 0.65,
                "points": [
                    {"x": 0.65, "y": 0.0, "z": 0.40, "level": "gunwale"},
                    {"x": 0.65, "y": -0.22, "z": 0.20, "level": "chine_upper"},
                    {"x": 0.65, "y": 0.22, "z": 0.20, "level": "chine_upper"},
                    {"x": 0.65, "y": -0.24, "z": 0.0, "level": "chine_lower"},
                    {"x": 0.65, "y": 0.24, "z": 0.0, "level": "chine_lower"},
                    {"x": 0.65, "y": -0.20, "z": -0.18, "level": "keel"},
                    {"x": 0.65, "y": 0.20, "z": -0.18, "level": "keel"},
                ],
            },
            {
                "station": 2.6,
                "points": [
                    {"x": 2.6, "y": 0.0, "z": 0.45, "level": "gunwale"},
                    {"x": 2.6, "y": -0.27, "z": 0.22, "level": "chine_upper"},
                    {"x": 2.6, "y": 0.27, "z": 0.22, "level": "chine_upper"},
                    {"x": 2.6, "y": -0.275, "z": 0.0, "level": "chine_lower"},
                    {"x": 2.6, "y": 0.275, "z": 0.0, "level": "chine_lower"},
                    {"x": 2.6, "y": -0.25, "z": -0.20, "level": "keel"},
                    {"x": 2.6, "y": 0.25, "z": -0.20, "level": "keel"},
                ],
            },
            {
                "station": 4.55,
                "points": [
                    {"x": 4.55, "y": 0.0, "z": 0.42, "level": "gunwale"},
                    {"x": 4.55, "y": -0.23, "z": 0.18, "level": "chine_upper"},
                    {"x": 4.55, "y": 0.23, "z": 0.18, "level": "chine_upper"},
                    {"x": 4.55, "y": -0.25, "z": -0.02, "level": "chine_lower"},
                    {"x": 4.55, "y": 0.25, "z": -0.02, "level": "chine_lower"},
                    {"x": 4.55, "y": -0.22, "z": -0.16, "level": "keel"},
                    {"x": 4.55, "y": 0.22, "z": -0.16, "level": "keel"},
                ],
            },
        ],
    }

    return hull_data


def create_multipoint_hull_example2():
    """
    Example 2: High Rocker Whitewater Kayak

    Features:
    - Extreme rocker for maneuverability
    - Keel significantly curved up at ends
    - Shorter effective waterline when unladen
    """
    hull_data = {
        "metadata": {
            "name": "Whitewater Kayak - High Rocker",
            "description": "Multi-point bow/stern with extreme rocker for maximum maneuverability",
            "units": "m",
            "coordinate_system": "bow_origin",
            "water_density": 1000.0,
            "length": 3.5,
            "beam": 0.62,
        },
        "bow": [
            {"x": 0.0, "y": 0.0, "z": 0.60, "level": "gunwale"},
            {"x": 0.10, "y": 0.0, "z": 0.20, "level": "chine"},
            {"x": 0.25, "y": 0.0, "z": -0.05, "level": "keel"},
        ],
        "stern": [
            {"x": 3.5, "y": 0.0, "z": 0.58, "level": "gunwale"},
            {"x": 3.40, "y": 0.0, "z": 0.18, "level": "chine"},
            {"x": 3.25, "y": 0.0, "z": -0.08, "level": "keel"},
        ],
        "profiles": [
            {
                "station": 0.50,
                "points": [
                    {"x": 0.50, "y": 0.0, "z": 0.45, "level": "gunwale"},
                    {"x": 0.50, "y": -0.28, "z": 0.12, "level": "chine"},
                    {"x": 0.50, "y": 0.28, "z": 0.12, "level": "chine"},
                    {"x": 0.50, "y": -0.26, "z": -0.15, "level": "keel"},
                    {"x": 0.50, "y": 0.26, "z": -0.15, "level": "keel"},
                ],
            },
            {
                "station": 1.75,
                "points": [
                    {"x": 1.75, "y": 0.0, "z": 0.48, "level": "gunwale"},
                    {"x": 1.75, "y": -0.31, "z": 0.15, "level": "chine"},
                    {"x": 1.75, "y": 0.31, "z": 0.15, "level": "chine"},
                    {"x": 1.75, "y": -0.30, "z": -0.18, "level": "keel"},
                    {"x": 1.75, "y": 0.30, "z": -0.18, "level": "keel"},
                ],
            },
            {
                "station": 3.0,
                "points": [
                    {"x": 3.0, "y": 0.0, "z": 0.46, "level": "gunwale"},
                    {"x": 3.0, "y": -0.29, "z": 0.13, "level": "chine"},
                    {"x": 3.0, "y": 0.29, "z": 0.13, "level": "chine"},
                    {"x": 3.0, "y": -0.27, "z": -0.16, "level": "keel"},
                    {"x": 3.0, "y": 0.27, "z": -0.16, "level": "keel"},
                ],
            },
        ],
    }

    return hull_data


def create_multipoint_hull_example3():
    """
    Example 3: Racing Kayak with Minimal Rocker (Array Position Matching)

    Features:
    - Low rocker for maximum speed and tracking
    - Uses array position matching (no explicit level attributes)
    - Longer waterline
    """
    hull_data = {
        "metadata": {
            "name": "Racing Kayak - Minimal Rocker",
            "description": "Multi-point bow/stern with minimal rocker using array position matching",
            "units": "m",
            "coordinate_system": "bow_origin",
            "water_density": 1000.0,
            "length": 5.8,
            "beam": 0.48,
        },
        "bow": [
            {"x": 0.0, "y": 0.0, "z": 0.35},
            {"x": 0.20, "y": 0.0, "z": 0.10},
            {"x": 0.50, "y": 0.0, "z": -0.10},
        ],
        "stern": [
            {"x": 5.8, "y": 0.0, "z": 0.33},
            {"x": 5.60, "y": 0.0, "z": 0.08},
            {"x": 5.30, "y": 0.0, "z": -0.12},
        ],
        "profiles": [
            {
                "station": 0.80,
                "points": [
                    {"x": 0.80, "y": 0.0, "z": 0.30},
                    {"x": 0.80, "y": -0.20, "z": 0.08},
                    {"x": 0.80, "y": 0.20, "z": 0.08},
                    {"x": 0.80, "y": -0.22, "z": -0.12},
                    {"x": 0.80, "y": 0.22, "z": -0.12},
                ],
            },
            {
                "station": 2.9,
                "points": [
                    {"x": 2.9, "y": 0.0, "z": 0.32},
                    {"x": 2.9, "y": -0.24, "z": 0.10},
                    {"x": 2.9, "y": 0.24, "z": 0.10},
                    {"x": 2.9, "y": -0.24, "z": -0.15},
                    {"x": 2.9, "y": 0.24, "z": -0.15},
                ],
            },
            {
                "station": 5.0,
                "points": [
                    {"x": 5.0, "y": 0.0, "z": 0.31},
                    {"x": 5.0, "y": -0.21, "z": 0.09},
                    {"x": 5.0, "y": 0.21, "z": 0.09},
                    {"x": 5.0, "y": -0.23, "z": -0.13},
                    {"x": 5.0, "y": 0.23, "z": -0.13},
                ],
            },
        ],
    }

    return hull_data


def save_hull_json(hull_data, filename):
    """Save hull data to JSON file."""
    output_path = Path("my_kayaks") / filename
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(hull_data, f, indent=2)

    print(f"Saved: {output_path}")
    return output_path


def visualize_hull(json_path, title):
    """Load and visualize a hull."""
    from src.io import load_hull_from_json

    hull = load_hull_from_json(str(json_path))

    print(f"\n{title}")
    print(f"  Profiles: {hull.num_profiles}")
    print(f"  Bow points: {len(hull.bow_points) if hull.bow_points else 0}")
    print(f"  Stern points: {len(hull.stern_points) if hull.stern_points else 0}")
    print(f"  Length: {hull.length:.2f} m")
    print(f"  Max Beam: {hull.max_beam:.2f} m")

    # Create visualization
    fig = plt.figure(figsize=(16, 5))

    # Profile view (side)
    ax1 = fig.add_subplot(1, 3, 1)
    plot_profile_view(hull, waterline_z=0.0, ax=ax1)
    ax1.set_title(f"{title}\nProfile View (Side)")

    # Plan view (top)
    ax2 = fig.add_subplot(1, 3, 2)
    plot_plan_view(hull, z_level=0.0, ax=ax2)
    ax2.set_title("Plan View (Top)")

    # 3D view
    ax3 = fig.add_subplot(1, 3, 3, projection="3d")
    plot_hull_3d(hull, waterline_z=0.0, ax=ax3, view_mode="wireframe")
    ax3.set_title("3D View")

    plt.tight_layout()

    # Save figure
    output_fig = json_path.with_suffix(".png")
    plt.savefig(output_fig, dpi=150, bbox_inches="tight")
    print(f"  Saved visualization: {output_fig}")
    plt.close()


def main():
    """
    Main function demonstrating multi-point bow/stern hull creation.
    """
    print("=" * 70)
    print("Multi-Point Bow/Stern Hull Creation Examples")
    print("=" * 70)

    # Example 1: Traditional sea kayak with moderate rocker
    print("\n1. Creating traditional sea kayak with moderate rocker...")
    hull1 = create_multipoint_hull_example1()
    path1 = save_hull_json(hull1, "example1_traditional_sea_kayak.json")
    visualize_hull(path1, "Example 1: Traditional Sea Kayak")

    # Example 2: Whitewater kayak with high rocker
    print("\n2. Creating whitewater kayak with high rocker...")
    hull2 = create_multipoint_hull_example2()
    path2 = save_hull_json(hull2, "example2_whitewater_high_rocker.json")
    visualize_hull(path2, "Example 2: Whitewater Kayak")

    # Example 3: Racing kayak with minimal rocker
    print("\n3. Creating racing kayak with minimal rocker...")
    hull3 = create_multipoint_hull_example3()
    path3 = save_hull_json(hull3, "example3_racing_minimal_rocker.json")
    visualize_hull(path3, "Example 3: Racing Kayak")

    print("\n" + "=" * 70)
    print("All examples created successfully!")
    print("=" * 70)
    print("\nGenerated files:")
    print(f"  - {path1}")
    print(f"  - {path2}")
    print(f"  - {path3}")
    print("\nVisualization files:")
    print(f"  - {path1.with_suffix('.png')}")
    print(f"  - {path2.with_suffix('.png')}")
    print(f"  - {path3.with_suffix('.png')}")
    print("\nKey differences between examples:")
    print("  1. Traditional: Moderate rocker, 4 levels with explicit names")
    print("  2. Whitewater: High rocker, 3 levels, extreme curve")
    print("  3. Racing: Minimal rocker, 3 levels, array position matching (no level names)")
    print("\nTo use these hulls:")
    print("  from src.io import load_hull_from_json")
    print("  hull = load_hull_from_json('my_kayaks/example1_traditional_sea_kayak.json')")


if __name__ == "__main__":
    main()
