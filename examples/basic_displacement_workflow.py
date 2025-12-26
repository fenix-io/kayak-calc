"""
Basic Displacement Calculation Workflow

This script demonstrates a complete workflow for calculating kayak displacement
and basic hydrostatic properties. This is the most common beginner use case.

This script demonstrates:
- Loading hull geometry from JSON file
- Defining waterline level
- Calculating displacement volume and mass
- Calculating center of buoyancy (LCB, VCB, TCB)
- Visualizing hull geometry and cross-sections
- Exporting results to CSV
- Generating a summary report

Prerequisites:
- Sample hull data file: data/sample_hull_kayak.json
- Python packages: numpy, matplotlib

Expected outputs:
- examples/output/basic_displacement_volume.csv
- examples/output/basic_displacement_report.md
- examples/output/basic_displacement_hull.png
- examples/output/basic_displacement_sections.png

Usage:
    python examples/basic_displacement_workflow.py

Author: Kayak Calculation Tool
Version: 1.0
"""

import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

# Import kayak calculation modules
from src.io import load_hull_from_json, export_hydrostatic_properties, generate_hydrostatic_report
from src.hydrostatics import calculate_center_of_buoyancy, calculate_volume
from src.visualization import plot_hull_3d, plot_multiple_profiles

# Configure output directory
OUTPUT_DIR = Path('examples/output')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    """
    Main workflow for basic displacement calculation.
    
    This function demonstrates a complete end-to-end workflow from loading
    data to generating outputs.
    """
    
    print("="*70)
    print("BASIC DISPLACEMENT CALCULATION WORKFLOW")
    print("="*70)
    
    # =========================================================================
    # STEP 1: Load Hull Geometry
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 1: Loading Hull Geometry")
    print("-"*70)
    
    # Load hull from JSON file
    # This file contains profile points, bow/stern points, and metadata
    hull_file = Path('data/sample_hull_kayak.json')
    
    if not hull_file.exists():
        print(f"ERROR: Sample data file not found: {hull_file}")
        print("Please ensure the data file exists before running this script.")
        return
    
    print(f"Loading hull from: {hull_file}")
    hull = load_hull_from_json(hull_file)
    
    # Display basic hull information
    stations = hull.get_stations()
    num_profiles = len(stations)
    print(f"  ✓ Hull loaded successfully")
    print(f"  ✓ Number of profiles: {num_profiles}")
    print(f"  ✓ Longitudinal range: {stations[0]:.2f} to {stations[-1]:.2f} m")
    
    
    # =========================================================================
    # STEP 2: Define Waterline Level
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 2: Defining Waterline")
    print("-"*70)
    
    # The waterline z-coordinate defines the water surface level
    # Points below this level are submerged
    # Convention: z = 0 is often at the waterline for an empty kayak
    waterline_z = 0.0  # meters
    
    print(f"  Waterline level: z = {waterline_z:.3f} m")
    print(f"  (Points with z < {waterline_z:.3f} are submerged)")
    
    
    # =========================================================================
    # STEP 3: Calculate Displacement Volume
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 3: Calculating Displacement Volume")
    print("-"*70)
    
    # Calculate the volume of water displaced by the hull
    # This uses numerical integration of cross-sectional areas
    volume = calculate_volume(hull, waterline_z=waterline_z)
    
    # Convert volume to displaced mass
    # Standard water density: 1000 kg/m³ for fresh water
    water_density = 1000.0  # kg/m³
    displaced_mass = volume * water_density
    
    print(f"  ✓ Displacement volume: {volume:.4f} m³")
    print(f"  ✓ Displaced mass: {displaced_mass:.2f} kg")
    print(f"    (Using water density: {water_density:.0f} kg/m³)")
    
    # Interpret the result
    if displaced_mass > 0:
        print(f"\n  Interpretation:")
        print(f"    The kayak displaces {volume:.4f} cubic meters of water")
        print(f"    This corresponds to a buoyant force supporting {displaced_mass:.1f} kg")
        print(f"    At equilibrium, the kayak + paddler mass should equal {displaced_mass:.1f} kg")
    
    
    # =========================================================================
    # STEP 4: Calculate Center of Buoyancy
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 4: Calculating Center of Buoyancy")
    print("-"*70)
    
    # The center of buoyancy (CB) is the centroid of the displaced volume
    # It's where the buoyant force effectively acts
    cb_result = calculate_center_of_buoyancy(hull, waterline_z=waterline_z)
    
    # Extract CB coordinates
    lcb = cb_result.lcb  # Longitudinal center of buoyancy (x-direction)
    vcb = cb_result.vcb  # Vertical center of buoyancy (z-direction)
    tcb = cb_result.tcb  # Transverse center of buoyancy (y-direction, should be ~0)
    
    print(f"  ✓ Center of Buoyancy calculated:")
    print(f"    LCB (x): {lcb:.3f} m")
    print(f"    VCB (z): {vcb:.3f} m")
    print(f"    TCB (y): {tcb:.3f} m")
    
    # Verify volume consistency
    print(f"\n  Verification:")
    print(f"    Volume from CB calculation: {cb_result.volume:.4f} m³")
    print(f"    Volume from direct calculation: {volume:.4f} m³")
    print(f"    Difference: {abs(cb_result.volume - volume):.6f} m³ (should be ~0)")
    
    # Interpret the results
    print(f"\n  Interpretation:")
    print(f"    The buoyant force acts vertically through point ({lcb:.3f}, {tcb:.3f}, {vcb:.3f})")
    print(f"    LCB position indicates fore/aft distribution of buoyancy")
    print(f"    VCB position affects stability characteristics")
    
    
    # =========================================================================
    # STEP 5: Visualize Hull Geometry
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 5: Generating Visualizations")
    print("-"*70)
    
    # Create 3D visualization of hull with waterline
    print("  Creating 3D hull plot...")
    ax_hull = plot_hull_3d(
        hull,
        waterline_z=waterline_z,
        show_waterline_plane=True
    )
    
    # Save the figure
    fig_hull = ax_hull.get_figure()
    hull_plot_file = OUTPUT_DIR / 'basic_displacement_hull.png'
    fig_hull.savefig(hull_plot_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Hull plot saved: {hull_plot_file}")
    plt.close(fig_hull)
    
    # Create cross-section plots at key stations
    print("  Creating cross-section plots...")
    
    # Select evenly spaced stations for visualization
    stations = hull.get_stations()
    station_positions = np.linspace(
        stations[0],
        stations[-1],
        min(5, len(stations))  # Show up to 5 sections
    )
    
    # Get profiles at these stations
    profiles_to_plot = [hull.get_profile(station) for station in station_positions]
    
    fig_sections, ax_sections = plot_multiple_profiles(
        profiles_to_plot,
        waterline_z=waterline_z
    )
    
    # Save the figure
    sections_plot_file = OUTPUT_DIR / 'basic_displacement_sections.png'
    fig_sections.savefig(sections_plot_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Cross-section plots saved: {sections_plot_file}")
    plt.close(fig_sections)
    
    
    # =========================================================================
    # STEP 6: Export Results to CSV
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 6: Exporting Results")
    print("-"*70)
    
    # Export hydrostatic properties to CSV format
    # This creates a structured data file for further analysis
    csv_file = OUTPUT_DIR / 'basic_displacement_volume.csv'
    
    export_hydrostatic_properties(
        cb_result,
        filepath=csv_file,
        metadata={
            'hull_file': str(hull_file),
            'waterline_z': waterline_z,
            'water_density': water_density,
            'analysis_type': 'Basic Displacement Calculation'
        }
    )
    
    print(f"  ✓ Results exported to CSV: {csv_file}")
    
    
    # =========================================================================
    # STEP 7: Generate Summary Report
    # =========================================================================
    print("\n" + "-"*70)
    print("STEP 7: Generating Report")
    print("-"*70)
    
    # Generate a comprehensive markdown report
    report_file = OUTPUT_DIR / 'basic_displacement_report.md'
    
    generate_hydrostatic_report(
        hull=hull,
        cb=cb_result,
        filepath=report_file,
        metadata={
            'hull_file': str(hull_file),
            'waterline_z': waterline_z,
            'water_density': water_density,
            'num_profiles': len(stations),
            'analysis_date': '2025-12-26'
        }
    )
    
    print(f"  ✓ Report generated: {report_file}")
    
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "="*70)
    print("WORKFLOW COMPLETE")
    print("="*70)
    
    print("\nCalculated Values:")
    print(f"  • Displacement Volume: {volume:.4f} m³")
    print(f"  • Displaced Mass: {displaced_mass:.2f} kg")
    print(f"  • LCB: {lcb:.3f} m")
    print(f"  • VCB: {vcb:.3f} m")
    print(f"  • TCB: {tcb:.3f} m")
    
    print("\nGenerated Outputs:")
    print(f"  • Hull visualization: {hull_plot_file.name}")
    print(f"  • Cross-section plots: {sections_plot_file.name}")
    print(f"  • Data export (CSV): {csv_file.name}")
    print(f"  • Summary report (MD): {report_file.name}")
    
    print("\nNext Steps:")
    print("  • Review the generated plots and report")
    print("  • Try different waterline levels to see how displacement changes")
    print("  • Proceed to stability analysis (see complete_stability_analysis.py)")
    print("  • Adapt this script for your own hull data")
    
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
