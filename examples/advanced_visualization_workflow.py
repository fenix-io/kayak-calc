"""
Advanced Visualization Workflow

This script showcases all visualization capabilities of the kayak calculation
library, including static plots, interactive explorers, and animations.

This script demonstrates:
- Complete set of static visualizations
- Interactive parameter exploration
- Real-time heel angle adjustment
- CG position adjustment tools
- Waterline level exploration
- Animation of heel sequences
- Multi-format export (PNG, PDF, MP4, GIF)

Prerequisites:
- Sample hull data file: data/sample_hull_kayak.json
- Python packages: numpy, matplotlib
- Optional: ffmpeg (for video export)

Expected outputs:
- examples/output/viz_hull_3d.png
- examples/output/viz_profiles.png
- examples/output/viz_stability_curve.png
- examples/output/viz_heel_sequence.mp4 (if ffmpeg available)
- Interactive windows (user must close to continue)

Usage:
    python examples/advanced_visualization_workflow.py

    Use --skip-interactive flag to skip interactive plots:
    python examples/advanced_visualization_workflow.py --skip-interactive

Author: Kayak Calculation Tool
Version: 1.0
"""

import sys
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# Import kayak calculation modules
from src.io import load_hull_from_json
from src.hydrostatics import CenterOfGravity, calculate_center_of_buoyancy
from src.stability import StabilityAnalyzer
from src.visualization import (
    plot_hull_3d,
    plot_multiple_profiles,
    plot_stability_curve,
    plot_multiple_stability_curves,
    interactive_heel_explorer,
    interactive_stability_curve,
    interactive_cg_adjustment,
    interactive_waterline_explorer,
    animate_heel_sequence
)

# Configure output directory
OUTPUT_DIR = Path('examples/output')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Check if interactive plots should be skipped
SKIP_INTERACTIVE = '--skip-interactive' in sys.argv


def main():
    """
    Advanced visualization workflow.
    
    This demonstrates the complete visualization capabilities of the library.
    """
    
    print("="*70)
    print("ADVANCED VISUALIZATION WORKFLOW")
    print("="*70)
    
    if SKIP_INTERACTIVE:
        print("\n  ⚠ Running in non-interactive mode (--skip-interactive flag set)")
        print("    Interactive visualizations will be skipped")
    
    # =========================================================================
    # STEP 1: Load Hull and Setup Analysis
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 1: Loading Hull and Setting Up Analysis")
    print("-"*70)
    
    hull_file = Path('data/sample_hull_kayak.json')
    
    if not hull_file.exists():
        print(f"ERROR: Sample data file not found: {hull_file}")
        return
    
    print(f"Loading hull from: {hull_file}")
    hull = load_hull_from_json(hull_file)
    print(f"  ✓ Hull loaded successfully")
    
    # Define CG
    cg = CenterOfGravity(
        lcg=2.5, vcg=-0.15, tcg=0.0, total_mass=100.0, num_components=1
    )
    print(f"  ✓ CG defined: {cg.total_mass:.0f}kg at ({cg.lcg:.2f}, {cg.vcg:.2f})")
    
    # Define waterline
    waterline_z = 0.0
    print(f"  ✓ Waterline: z = {waterline_z:.2f}m")
    
    # Calculate CB
    cb = calculate_center_of_buoyancy(hull, waterline_z=waterline_z)
    print(f"  ✓ CB calculated: ({cb.lcb:.3f}, {cb.vcb:.3f})")
    
    # Create analyzer
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=waterline_z)
    print(f"  ✓ Stability analyzer created")
    
    
    # =========================================================================
    # PART A: STATIC VISUALIZATIONS
    # =========================================================================
    print("\n" + "="*70)
    print("PART A: STATIC VISUALIZATIONS")
    print("="*70)
    
    # -------------------------------------------------------------------------
    # A1: 3D Hull Visualization
    # -------------------------------------------------------------------------
    print("\n" + "-"*70)
    print("A1: 3D Hull Visualization")
    print("-"*70)
    
    print("  Creating comprehensive 3D hull plot...")
    
    fig_hull = plot_hull_3d(
        hull,
        waterline_z=waterline_z,
        show_waterline=True,
        show_cb=True,
        cb_point=(cb.lcb, cb.tcb, cb.vcb),
        show_cg=True,
        cg_point=(cg.lcg, cg.tcg, cg.vcg),
        title='3D Hull Visualization with CG and CB',
        figsize=(12, 8)
    )
    
    output_file = OUTPUT_DIR / 'viz_hull_3d.png'
    fig_hull.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file.name}")
    plt.close(fig_hull)
    
    # -------------------------------------------------------------------------
    # A2: Cross-Section Profiles
    # -------------------------------------------------------------------------
    print("\n" + "-"*70)
    print("A2: Cross-Section Profiles")
    print("-"*70)
    
    print("  Creating detailed cross-section plots...")
    
    # Select stations for visualization
    hull_stations = hull.get_stations()
    stations = np.linspace(
        hull_stations[0],
        hull_stations[-1],
        8  # Show 8 sections
    )
    
    # Get profiles at these stations
    profiles_to_plot = [hull.get_profile(station) for station in stations]
    
    fig_profiles = plot_multiple_profiles(
        profiles_to_plot,
        waterline_z=waterline_z,
        title='Transverse Cross-Sections',
        figsize=(15, 10)
    )
    
    output_file = OUTPUT_DIR / 'viz_profiles.png'
    fig_profiles.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file.name}")
    plt.close(fig_profiles)
    
    # -------------------------------------------------------------------------
    # A3: Stability Curve
    # -------------------------------------------------------------------------
    print("\n" + "-"*70)
    print("A3: Stability Curve")
    print("-"*70)
    
    print("  Generating stability curve...")
    curve = analyzer.generate_stability_curve(max_angle=80, angle_step=1)
    
    fig_curve = plot_stability_curve(
        curve['heel_angles'],
        curve['gz_values'],
        title='Stability Curve (GZ vs Heel Angle)',
        show_metrics=True,
        figsize=(10, 6)
    )
    
    output_file = OUTPUT_DIR / 'viz_stability_curve.png'
    fig_curve.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file.name}")
    plt.close(fig_curve)
    
    # -------------------------------------------------------------------------
    # A4: Multi-Curve Comparison
    # -------------------------------------------------------------------------
    print("\n" + "-"*70)
    print("A4: Multi-Configuration Comparison")
    print("-"*70)
    
    print("  Creating comparison of different CG positions...")
    
    # Create multiple configurations
    cg_configs = [
        ('CG High', CenterOfGravity(2.5, -0.05, 0.0, 100.0, 1)),
        ('CG Normal', CenterOfGravity(2.5, -0.15, 0.0, 100.0, 1)),
        ('CG Low', CenterOfGravity(2.5, -0.25, 0.0, 100.0, 1)),
    ]
    
    curves = []
    labels = []
    
    for label, cg_config in cg_configs:
        analyzer_temp = StabilityAnalyzer(hull, cg_config, waterline_z=waterline_z)
        curve_temp = analyzer_temp.generate_stability_curve(max_angle=70, angle_step=2)
        curves.append(curve_temp)
        labels.append(label)
    
    fig_multi = plot_multiple_stability_curves(
        curves,
        labels,
        title='Stability Comparison: CG Height Variation',
        figsize=(10, 6)
    )
    
    output_file = OUTPUT_DIR / 'viz_multi_curve_comparison.png'
    fig_multi.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file.name}")
    plt.close(fig_multi)
    
    
    # =========================================================================
    # PART B: INTERACTIVE VISUALIZATIONS
    # =========================================================================
    print("\n" + "="*70)
    print("PART B: INTERACTIVE VISUALIZATIONS")
    print("="*70)
    
    if SKIP_INTERACTIVE:
        print("\n  ⚠ Skipping interactive visualizations (non-interactive mode)")
    else:
        print("\n  NOTE: Close each interactive window to continue to the next")
        print("        You can interact with sliders, buttons, and click on plots")
    
    # -------------------------------------------------------------------------
    # B1: Interactive Heel Explorer
    # -------------------------------------------------------------------------
    if not SKIP_INTERACTIVE:
        print("\n" + "-"*70)
        print("B1: Interactive Heel Explorer")
        print("-"*70)
        
        print("  Launching interactive heel angle explorer...")
        print("    • Use slider to adjust heel angle in real-time")
        print("    • See hull geometry and GZ curve update dynamically")
        print("    • Close window when done")
        
        try:
            interactive_heel_explorer(
                hull,
                cg,
                waterline_z=waterline_z,
                max_angle=70
            )
            print("  ✓ Interactive heel explorer completed")
        except Exception as e:
            print(f"  ⚠ Could not launch interactive explorer: {e}")
    
    # -------------------------------------------------------------------------
    # B2: Interactive Stability Curve
    # -------------------------------------------------------------------------
    if not SKIP_INTERACTIVE:
        print("\n" + "-"*70)
        print("B2: Interactive Stability Curve Explorer")
        print("-"*70)
        
        print("  Launching interactive stability curve...")
        print("    • Click on points to see detailed hull view at that angle")
        print("    • Explore stability characteristics interactively")
        print("    • Close window when done")
        
        try:
            interactive_stability_curve(
                hull,
                cg,
                waterline_z=waterline_z,
                max_angle=70
            )
            print("  ✓ Interactive stability curve completed")
        except Exception as e:
            print(f"  ⚠ Could not launch interactive curve: {e}")
    
    # -------------------------------------------------------------------------
    # B3: Interactive CG Adjustment
    # -------------------------------------------------------------------------
    if not SKIP_INTERACTIVE:
        print("\n" + "-"*70)
        print("B3: Interactive CG Adjustment Tool")
        print("-"*70)
        
        print("  Launching interactive CG adjustment tool...")
        print("    • Use sliders to adjust CG position in real-time")
        print("    • See how stability changes with CG location")
        print("    • Observe GM and max GZ values update")
        print("    • Close window when done")
        
        try:
            interactive_cg_adjustment(
                hull,
                cg,
                waterline_z=waterline_z
            )
            print("  ✓ Interactive CG adjustment completed")
        except Exception as e:
            print(f"  ⚠ Could not launch CG adjustment: {e}")
    
    # -------------------------------------------------------------------------
    # B4: Interactive Waterline Explorer
    # -------------------------------------------------------------------------
    if not SKIP_INTERACTIVE:
        print("\n" + "-"*70)
        print("B4: Interactive Waterline Explorer")
        print("-"*70)
        
        print("  Launching interactive waterline explorer...")
        print("    • Use slider to adjust waterline level")
        print("    • See displacement and stability change")
        print("    • Visualize different loading conditions")
        print("    • Close window when done")
        
        try:
            interactive_waterline_explorer(
                hull,
                cg,
                waterline_z=waterline_z
            )
            print("  ✓ Interactive waterline explorer completed")
        except Exception as e:
            print(f"  ⚠ Could not launch waterline explorer: {e}")
    
    
    # =========================================================================
    # PART C: ANIMATIONS
    # =========================================================================
    print("\n" + "="*70)
    print("PART C: ANIMATIONS")
    print("="*70)
    
    # -------------------------------------------------------------------------
    # C1: Heel Sequence Animation
    # -------------------------------------------------------------------------
    print("\n" + "-"*70)
    print("C1: Heel Sequence Animation")
    print("-"*70)
    
    print("  Creating heel sequence animation...")
    print("    This may take 10-30 seconds...")
    
    try:
        anim = animate_heel_sequence(
            hull,
            cg,
            waterline_z=waterline_z,
            max_angle=60,
            num_frames=30,
            interval=100  # milliseconds between frames
        )
        
        # Try to save as MP4
        output_file = OUTPUT_DIR / 'viz_heel_sequence.mp4'
        
        try:
            print("    Attempting to save as MP4 (requires ffmpeg)...")
            anim.save(str(output_file), writer='ffmpeg', fps=10, dpi=100)
            print(f"  ✓ Animation saved: {output_file.name}")
        except Exception as e:
            print(f"    ⚠ Could not save MP4: {e}")
            print(f"    (Install ffmpeg to enable video export)")
            
            # Try GIF as fallback
            output_file_gif = OUTPUT_DIR / 'viz_heel_sequence.gif'
            try:
                print("    Attempting to save as GIF (slower, larger file)...")
                anim.save(str(output_file_gif), writer='pillow', fps=10, dpi=80)
                print(f"  ✓ Animation saved: {output_file_gif.name}")
            except Exception as e2:
                print(f"    ⚠ Could not save GIF: {e2}")
        
        plt.close()
        
    except Exception as e:
        print(f"  ⚠ Could not create animation: {e}")
    
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "="*70)
    print("VISUALIZATION WORKFLOW COMPLETE")
    print("="*70)
    
    print("\nGenerated Visualizations:")
    print("  Static Plots:")
    print("    • viz_hull_3d.png - 3D hull with CG and CB")
    print("    • viz_profiles.png - Cross-section profiles")
    print("    • viz_stability_curve.png - Stability curve")
    print("    • viz_multi_curve_comparison.png - Multi-configuration comparison")
    
    if not SKIP_INTERACTIVE:
        print("\n  Interactive Tools (demonstrated):")
        print("    • Heel angle explorer with real-time updates")
        print("    • Clickable stability curve explorer")
        print("    • CG position adjustment tool")
        print("    • Waterline level explorer")
    
    print("\n  Animations:")
    animations = list(OUTPUT_DIR.glob('viz_heel_sequence.*'))
    if animations:
        for anim_file in animations:
            print(f"    • {anim_file.name} - Heel sequence animation")
    else:
        print("    • (No animations saved - may require ffmpeg)")
    
    print("\nVisualization Capabilities:")
    print("  ✓ Static publication-quality plots")
    print("  ✓ Interactive parameter exploration")
    print("  ✓ Real-time dynamic updates")
    print("  ✓ Multi-panel synchronized views")
    print("  ✓ Animation with playback controls")
    print("  ✓ Multi-format export (PNG, PDF, MP4, GIF)")
    
    print("\nUsage Tips:")
    print("  • Use static plots for reports and documentation")
    print("  • Use interactive tools for design exploration")
    print("  • Use animations for presentations and teaching")
    print("  • Export in multiple formats for different purposes")
    print("  • Adapt these examples for custom visualizations")
    
    print("\nNext Steps:")
    print("  • Review generated plots in examples/output/")
    print("  • Run again without --skip-interactive to explore interactive features")
    print("  • Integrate these visualizations into your workflow")
    print("  • Customize plot styles and formats as needed")
    
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
