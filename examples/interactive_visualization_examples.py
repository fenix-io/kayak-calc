"""
Interactive Visualization Examples

This script demonstrates the interactive visualization capabilities of the
kayak calculation tool, including:
1. Interactive heel angle explorer
2. Interactive stability curve explorer
3. Animated heel sequence
4. Interactive CG adjustment tool
5. Interactive waterline explorer
6. Combined interactive dashboard

Note: These examples require an interactive matplotlib backend (e.g., TkAgg, Qt5Agg).
Run this script with: python -m examples.interactive_visualization_examples
"""

import numpy as np
import matplotlib
# Use an interactive backend - uncomment one of these based on your system:
# matplotlib.use('TkAgg')  # For Tkinter backend
# matplotlib.use('Qt5Agg')  # For Qt5 backend
matplotlib.use('TkAgg')  # Default to TkAgg

import matplotlib.pyplot as plt
from pathlib import Path

from src.geometry import Point3D, Profile, KayakHull
from src.visualization import (
    interactive_heel_explorer,
    interactive_stability_curve,
    animate_heel_sequence,
    interactive_cg_adjustment,
    interactive_waterline_explorer
)


def create_example_hull():
    """Create an example kayak hull for demonstrations."""
    hull = KayakHull()
    
    # Create a realistic kayak shape
    # Length: 4.5m, beam variations from bow to stern
    stations = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
    beams = [0.2, 0.4, 0.5, 0.55, 0.6, 0.55, 0.5, 0.4, 0.3, 0.15]  # Tapering shape
    depths = [0.3, 0.4, 0.45, 0.5, 0.5, 0.5, 0.45, 0.4, 0.35, 0.25]
    
    for x, beam, depth in zip(stations, beams, depths):
        # Create symmetrical profile with realistic hull shape
        n_points = 7
        y_starboard = np.linspace(0, beam, n_points)
        
        # Create curved bottom (parabolic shape)
        z_bottom = -depth + (y_starboard / beam) ** 2 * 0.1
        
        # Create deck line
        z_deck = 0.15 - (y_starboard / beam) * 0.05
        
        # Combine bottom and side points
        points = []
        # Deck to bottom on starboard side
        for y, z in zip(y_starboard, z_deck):
            points.append(Point3D(x, y, z))
        for y, z in reversed(list(zip(y_starboard, z_bottom))):
            points.append(Point3D(x, y, z))
        # Bottom to deck on port side
        for y, z in zip(y_starboard[1:], z_bottom[1:]):
            points.append(Point3D(x, -y, z))
        for y, z in reversed(list(zip(y_starboard[:-1], z_deck[:-1]))):
            points.append(Point3D(x, -y, z))
        
        profile = Profile(station=x, points=points)
        hull.add_profile(profile)
    
    return hull


def example_1_interactive_heel_explorer():
    """Example 1: Interactive heel angle explorer."""
    print("\n" + "="*70)
    print("Example 1: Interactive Heel Angle Explorer")
    print("="*70)
    print("Use the slider to adjust the heel angle and see real-time updates:")
    print("- 3D hull visualization")
    print("- Cross-section profile")
    print("- Stability metrics (GZ, GM, CB position)")
    print("- Displacement volume")
    print("\nClose the window to continue to the next example.")
    print("="*70 + "\n")
    
    # Create hull and define CG
    hull = create_example_hull()
    cg = Point3D(2.25, 0.0, -0.15)  # Midship, slightly below waterline
    
    # Create interactive explorer
    fig = interactive_heel_explorer(
        hull,
        cg,
        waterline_z=0.0,
        heel_range=(0.0, 90.0),
        initial_heel=0.0
    )
    
    plt.show()


def example_2_interactive_stability_curve():
    """Example 2: Interactive stability curve explorer."""
    print("\n" + "="*70)
    print("Example 2: Interactive Stability Curve Explorer")
    print("="*70)
    print("Click on any point on the GZ curve to see detailed information:")
    print("- Hull geometry at that heel angle")
    print("- Cross-section profile")
    print("- Numerical values (GZ, volume, CB position)")
    print("\nClose the window to continue to the next example.")
    print("="*70 + "\n")
    
    # Create hull and define CG
    hull = create_example_hull()
    cg = Point3D(2.25, 0.0, -0.15)
    
    # Create interactive curve
    fig = interactive_stability_curve(
        hull,
        cg,
        waterline_z=0.0
    )
    
    plt.show()


def example_3_animated_heel_sequence():
    """Example 3: Animated heel sequence."""
    print("\n" + "="*70)
    print("Example 3: Animated Heel Sequence")
    print("="*70)
    print("Watch the hull heel smoothly from 0° to 90°:")
    print("- Animated 3D hull view")
    print("- Animated cross-section")
    print("- Real-time stability metrics")
    print("- GZ curve builds as animation progresses")
    print("- Use Play/Pause button to control animation")
    print("\nClose the window to continue to the next example.")
    print("="*70 + "\n")
    
    # Create hull and define CG
    hull = create_example_hull()
    cg = Point3D(2.25, 0.0, -0.15)
    
    # Create animation (save to file optional)
    output_dir = Path('examples/output')
    output_dir.mkdir(parents=True, exist_ok=True)
    save_path = output_dir / 'heel_animation.mp4'  # Or use .gif
    
    print(f"Note: Animation can be saved to {save_path}")
    print("Set save_path=None if you don't want to save the animation.")
    
    fig, anim = animate_heel_sequence(
        hull,
        cg,
        waterline_z=0.0,
        heel_range=(0.0, 90.0),
        n_frames=45,  # 45 frames for smoother animation
        interval=100,  # 100ms between frames
        save_path=None  # Set to save_path to save animation
    )
    
    plt.show()


def example_4_interactive_cg_adjustment():
    """Example 4: Interactive CG position adjustment."""
    print("\n" + "="*70)
    print("Example 4: Interactive CG Position Adjustment")
    print("="*70)
    print("Use sliders to adjust the center of gravity position:")
    print("- LCG slider: Move CG longitudinally (fore/aft)")
    print("- VCG slider: Move CG vertically (up/down)")
    print("- See real-time impact on stability curve")
    print("- Compare original vs. adjusted metrics")
    print("- Use Reset button to return to initial position")
    print("\nClose the window to continue to the next example.")
    print("="*70 + "\n")
    
    # Create hull and define CG
    hull = create_example_hull()
    initial_cg = Point3D(2.25, 0.0, -0.15)
    
    # Create interactive CG adjustment tool
    fig = interactive_cg_adjustment(
        hull,
        initial_cg,
        waterline_z=0.0,
        vcg_range=(-0.4, 0.1),  # Allow vertical adjustment
        lcg_range=(1.5, 3.0)    # Allow longitudinal adjustment
    )
    
    plt.show()


def example_5_interactive_waterline_explorer():
    """Example 5: Interactive waterline level explorer."""
    print("\n" + "="*70)
    print("Example 5: Interactive Waterline Explorer")
    print("="*70)
    print("Use the slider to adjust the waterline Z-coordinate:")
    print("- See how displacement changes with draft")
    print("- Observe center of buoyancy position changes")
    print("- View submerged hull geometry at different waterlines")
    print("- Understand loading condition effects")
    print("\nClose the window to continue to the next example.")
    print("="*70 + "\n")
    
    # Create hull and define CG
    hull = create_example_hull()
    cg = Point3D(2.25, 0.0, -0.15)
    
    # Create interactive waterline explorer
    fig = interactive_waterline_explorer(
        hull,
        cg,
        waterline_range=(-0.4, 0.2),
        initial_waterline=0.0,
        heel_angle=0.0  # Can also explore at heeled conditions
    )
    
    plt.show()


def example_6_waterline_explorer_heeled():
    """Example 6: Waterline explorer at heeled condition."""
    print("\n" + "="*70)
    print("Example 6: Waterline Explorer at Heeled Condition")
    print("="*70)
    print("Explore waterline effects when hull is heeled:")
    print("- Hull shown at 30° heel")
    print("- Adjust waterline to see draft effects when heeled")
    print("- Observe asymmetric displacement")
    print("\nClose the window to finish examples.")
    print("="*70 + "\n")
    
    # Create hull and define CG
    hull = create_example_hull()
    cg = Point3D(2.25, 0.0, -0.15)
    
    # Create interactive waterline explorer at heel
    fig = interactive_waterline_explorer(
        hull,
        cg,
        waterline_range=(-0.4, 0.2),
        initial_waterline=0.0,
        heel_angle=30.0  # Explore at 30° heel
    )
    
    plt.show()


def run_all_examples():
    """Run all examples in sequence."""
    print("\n" + "="*70)
    print("INTERACTIVE VISUALIZATION EXAMPLES")
    print("="*70)
    print("\nThese examples demonstrate interactive visualization features.")
    print("Each example will open in a new window.")
    print("Close each window to proceed to the next example.")
    print("\nNote: Some examples may take a moment to initialize.")
    print("="*70)
    
    examples = [
        example_1_interactive_heel_explorer,
        example_2_interactive_stability_curve,
        example_3_animated_heel_sequence,
        example_4_interactive_cg_adjustment,
        example_5_interactive_waterline_explorer,
        example_6_waterline_explorer_heeled,
    ]
    
    for example in examples:
        try:
            example()
        except KeyboardInterrupt:
            print("\n\nExamples interrupted by user.")
            break
        except Exception as e:
            print(f"\nError in example: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("="*70 + "\n")


if __name__ == '__main__':
    # You can run individual examples or all of them
    import sys
    
    if len(sys.argv) > 1:
        example_num = int(sys.argv[1])
        examples = {
            1: example_1_interactive_heel_explorer,
            2: example_2_interactive_stability_curve,
            3: example_3_animated_heel_sequence,
            4: example_4_interactive_cg_adjustment,
            5: example_5_interactive_waterline_explorer,
            6: example_6_waterline_explorer_heeled,
        }
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Example {example_num} not found. Valid examples: 1-6")
    else:
        # Run all examples
        run_all_examples()
