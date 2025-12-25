"""
Examples demonstrating center of gravity (CG) calculations.

This module shows how to:
1. Calculate CG from mass components
2. Specify CG manually
3. Adjust CG for loading changes
4. Validate CG position
5. Analyze mass distribution
"""

import numpy as np
import matplotlib.pyplot as plt
from src.hydrostatics import (
    MassComponent,
    CenterOfGravity,
    calculate_cg_from_components,
    create_cg_manual,
    validate_center_of_gravity,
    adjust_cg_for_loading,
    calculate_mass_summary
)


def example_1_basic_cg_calculation():
    """Example 1: Basic CG calculation from components."""
    print("=" * 70)
    print("Example 1: Basic CG Calculation from Components")
    print("=" * 70)
    
    # Define mass components for a touring kayak
    components = [
        MassComponent(
            name="Hull",
            mass=28.0,  # kg
            x=2.3,      # meters from origin (longitudinal)
            y=0.0,      # on centerline
            z=-0.05,    # below origin (vertical)
            description="Fiberglass hull"
        ),
        MassComponent(
            name="Paddler",
            mass=75.0,
            x=2.0,
            y=0.0,
            z=0.25,
            description="Adult paddler"
        ),
        MassComponent(
            name="Paddle",
            mass=1.0,
            x=2.0,
            y=0.3,  # Held to starboard side
            z=0.4,
            description="Fiberglass paddle"
        )
    ]
    
    # Calculate CG
    cg = calculate_cg_from_components(components, include_components=True)
    
    print(f"\nTotal mass: {cg.total_mass:.2f} kg")
    print(f"Weight: {cg.weight:.2f} N")
    print(f"\nCG Position:")
    print(f"  LCG (longitudinal): {cg.lcg:.4f} m")
    print(f"  VCG (vertical):     {cg.vcg:.4f} m")
    print(f"  TCG (transverse):   {cg.tcg:.4f} m")
    print(f"\nNumber of components: {cg.num_components}")
    
    # Validate
    is_valid, issues = validate_center_of_gravity(cg)
    print(f"\nValidation: {'PASS' if is_valid else 'FAIL'}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    
    print()


def example_2_manual_cg_specification():
    """Example 2: Manual CG specification."""
    print("=" * 70)
    print("Example 2: Manual CG Specification")
    print("=" * 70)
    
    # Sometimes we know the CG position directly (e.g., from CAD model)
    cg = create_cg_manual(
        lcg=2.15,      # 2.15 m from origin
        vcg=0.18,      # 0.18 m above origin
        tcg=0.0,       # On centerline
        total_mass=105.0  # 105 kg total
    )
    
    print(f"\nManual CG specification:")
    print(f"  LCG: {cg.lcg:.3f} m")
    print(f"  VCG: {cg.vcg:.3f} m")
    print(f"  TCG: {cg.tcg:.3f} m")
    print(f"  Total mass: {cg.total_mass:.1f} kg")
    print(f"  Weight: {cg.weight:.1f} N")
    
    # Validate with specific criteria
    is_valid, issues = validate_center_of_gravity(
        cg,
        min_mass=50.0,      # Minimum 50 kg
        max_mass=200.0,     # Maximum 200 kg
        max_tcg_offset=0.05  # Max 5 cm off centerline
    )
    
    print(f"\nValidation: {'PASS' if is_valid else 'FAIL'}")
    print()


def example_3_loading_adjustments():
    """Example 3: Adjusting CG for loading changes."""
    print("=" * 70)
    print("Example 3: Adjusting CG for Loading Changes")
    print("=" * 70)
    
    # Start with empty kayak
    empty_cg = create_cg_manual(
        lcg=2.5,
        vcg=0.0,
        tcg=0.0,
        total_mass=28.0  # Hull only
    )
    
    print("\n1. Empty Kayak:")
    print(f"   LCG: {empty_cg.lcg:.3f} m, VCG: {empty_cg.vcg:.3f} m, Mass: {empty_cg.total_mass:.1f} kg")
    
    # Add paddler
    paddler = MassComponent("Paddler", mass=75.0, x=2.0, y=0.0, z=0.25)
    with_paddler = adjust_cg_for_loading(empty_cg, [paddler])
    
    print("\n2. With Paddler:")
    print(f"   LCG: {with_paddler.lcg:.3f} m, VCG: {with_paddler.vcg:.3f} m, Mass: {with_paddler.total_mass:.1f} kg")
    print(f"   CG moved forward: {empty_cg.lcg - with_paddler.lcg:.3f} m")
    print(f"   CG moved up: {with_paddler.vcg - empty_cg.vcg:.3f} m")
    
    # Add camping gear
    gear = [
        MassComponent("Tent", mass=3.5, x=0.8, y=0.0, z=0.0),
        MassComponent("Sleeping bag", mass=1.5, x=1.0, y=0.0, z=0.05),
        MassComponent("Food", mass=8.0, x=1.2, y=0.0, z=0.1),
        MassComponent("Water", mass=5.0, x=2.2, y=0.0, z=0.0),
    ]
    
    fully_loaded = adjust_cg_for_loading(with_paddler, gear)
    
    print("\n3. Fully Loaded:")
    print(f"   LCG: {fully_loaded.lcg:.3f} m, VCG: {fully_loaded.vcg:.3f} m, Mass: {fully_loaded.total_mass:.1f} kg")
    print(f"   Total components: {fully_loaded.num_components}")
    
    # Compare configurations
    print("\n4. Summary of CG Changes:")
    print(f"   Empty -> With paddler: ΔLCG = {with_paddler.lcg - empty_cg.lcg:+.3f} m")
    print(f"   With paddler -> Loaded: ΔLCG = {fully_loaded.lcg - with_paddler.lcg:+.3f} m")
    print(f"   Empty -> Loaded:       ΔLCG = {fully_loaded.lcg - empty_cg.lcg:+.3f} m")
    print()


def example_4_mass_distribution_analysis():
    """Example 4: Mass distribution analysis."""
    print("=" * 70)
    print("Example 4: Mass Distribution Analysis")
    print("=" * 70)
    
    # Complete kayak system
    components = [
        MassComponent("Hull", mass=28.0, x=2.3, y=0.0, z=-0.05),
        MassComponent("Paddler", mass=75.0, x=2.0, y=0.0, z=0.25),
        MassComponent("Paddle", mass=1.0, x=2.0, y=0.3, z=0.4),
        MassComponent("PFD", mass=0.8, x=2.0, y=0.0, z=0.35),
        MassComponent("Dry bag 1", mass=3.0, x=0.8, y=0.0, z=0.0),
        MassComponent("Dry bag 2", mass=2.5, x=3.5, y=0.0, z=0.0),
        MassComponent("Water bottle", mass=1.0, x=2.1, y=0.0, z=0.1),
    ]
    
    # Calculate mass summary
    summary = calculate_mass_summary(components)
    
    print(f"\nTotal mass: {summary['total_mass']:.1f} kg")
    print(f"Number of components: {summary['num_components']}")
    print(f"Average mass per component: {summary['average_mass']:.2f} kg")
    print(f"\nHeaviest component:")
    print(f"  {summary['heaviest']['name']}: {summary['heaviest']['mass']:.1f} kg")
    print(f"\nLightest component:")
    print(f"  {summary['lightest']['name']}: {summary['lightest']['mass']:.1f} kg")
    
    print(f"\nMass distribution:")
    for item in summary['mass_distribution']:
        print(f"  {item['name']:15s}: {item['mass']:6.2f} kg ({item['percentage']:5.1f}%)")
    
    # Calculate CG
    cg = calculate_cg_from_components(components)
    print(f"\nOverall CG position:")
    print(f"  LCG: {cg.lcg:.3f} m")
    print(f"  VCG: {cg.vcg:.3f} m")
    print(f"  TCG: {cg.tcg:.3f} m")
    print()


def example_5_validation_criteria():
    """Example 5: CG validation with different criteria."""
    print("=" * 70)
    print("Example 5: CG Validation with Different Criteria")
    print("=" * 70)
    
    # Test different CG configurations
    test_cases = [
        {
            "name": "Balanced loading",
            "cg": create_cg_manual(2.0, 0.2, 0.0, 100.0),
            "criteria": {}
        },
        {
            "name": "Very light kayak",
            "cg": create_cg_manual(2.0, 0.2, 0.0, 30.0),
            "criteria": {"min_mass": 50.0}
        },
        {
            "name": "Very heavy kayak",
            "cg": create_cg_manual(2.0, 0.2, 0.0, 250.0),
            "criteria": {"max_mass": 200.0}
        },
        {
            "name": "Off-centerline",
            "cg": create_cg_manual(2.0, 0.2, 0.15, 100.0),
            "criteria": {"max_tcg_offset": 0.05}
        },
    ]
    
    for case in test_cases:
        print(f"\nTest: {case['name']}")
        cg = case['cg']
        print(f"  CG: LCG={cg.lcg:.2f} m, VCG={cg.vcg:.2f} m, TCG={cg.tcg:.2f} m, Mass={cg.total_mass:.1f} kg")
        
        is_valid, issues = validate_center_of_gravity(cg, **case['criteria'])
        print(f"  Result: {'✓ PASS' if is_valid else '✗ FAIL'}")
        
        if issues:
            for issue in issues:
                print(f"    - {issue}")
    print()


def example_6_component_positions():
    """Example 6: Visualizing component positions and CG."""
    print("=" * 70)
    print("Example 6: Visualizing Component Positions and CG")
    print("=" * 70)
    
    # Define components
    components = [
        MassComponent("Hull", mass=28.0, x=2.3, y=0.0, z=-0.05),
        MassComponent("Paddler", mass=75.0, x=2.0, y=0.0, z=0.25),
        MassComponent("Gear bow", mass=5.0, x=0.8, y=0.0, z=0.0),
        MassComponent("Gear stern", mass=3.0, x=3.5, y=0.0, z=0.0),
    ]
    
    # Calculate CG
    cg = calculate_cg_from_components(components)
    
    print(f"\nComponent positions:")
    for comp in components:
        print(f"  {comp.name:12s}: x={comp.x:.2f} m, mass={comp.mass:.1f} kg")
    
    print(f"\nCenter of Gravity:")
    print(f"  LCG: {cg.lcg:.3f} m")
    print(f"  VCG: {cg.vcg:.3f} m")
    print(f"  Total mass: {cg.total_mass:.1f} kg")
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Side view (x-z plane)
    ax1.set_title('Side View: Component Positions and CG')
    ax1.set_xlabel('Longitudinal Position (m)')
    ax1.set_ylabel('Vertical Position (m)')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='b', linestyle='--', alpha=0.3, label='Waterline')
    
    # Plot components (size proportional to mass)
    for comp in components:
        size = comp.mass * 10  # Scale for visibility
        ax1.scatter(comp.x, comp.z, s=size, alpha=0.6, label=comp.name)
    
    # Plot CG
    ax1.scatter(cg.lcg, cg.vcg, s=200, marker='x', color='red', 
                linewidths=3, label='CG', zorder=5)
    ax1.legend(loc='best')
    
    # Top view (x-y plane)
    ax2.set_title('Top View: Component Positions and CG')
    ax2.set_xlabel('Longitudinal Position (m)')
    ax2.set_ylabel('Transverse Position (m)')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3, label='Centerline')
    
    # Plot components
    for comp in components:
        size = comp.mass * 10
        ax2.scatter(comp.x, comp.y, s=size, alpha=0.6, label=comp.name)
    
    # Plot CG
    ax2.scatter(cg.lcg, cg.tcg, s=200, marker='x', color='red',
                linewidths=3, label='CG', zorder=5)
    ax2.legend(loc='best')
    
    plt.tight_layout()
    plt.savefig('center_of_gravity_visualization.png', dpi=150, bbox_inches='tight')
    print(f"\nVisualization saved to: center_of_gravity_visualization.png")
    print()


def example_7_comparing_loading_scenarios():
    """Example 7: Comparing different loading scenarios."""
    print("=" * 70)
    print("Example 7: Comparing Different Loading Scenarios")
    print("=" * 70)
    
    # Base kayak
    hull = MassComponent("Hull", mass=28.0, x=2.3, y=0.0, z=-0.05)
    
    # Different loading scenarios
    scenarios = {
        "Day trip": [
            hull,
            MassComponent("Paddler", mass=75.0, x=2.0, y=0.0, z=0.25),
            MassComponent("Day pack", mass=3.0, x=2.2, y=0.0, z=0.1),
        ],
        "Weekend camping": [
            hull,
            MassComponent("Paddler", mass=75.0, x=2.0, y=0.0, z=0.25),
            MassComponent("Tent", mass=3.5, x=0.8, y=0.0, z=0.0),
            MassComponent("Food/gear", mass=8.0, x=1.2, y=0.0, z=0.1),
            MassComponent("Dry bag stern", mass=2.5, x=3.5, y=0.0, z=0.0),
        ],
        "Extended expedition": [
            hull,
            MassComponent("Paddler", mass=75.0, x=2.0, y=0.0, z=0.25),
            MassComponent("Gear bow 1", mass=5.0, x=0.8, y=0.0, z=0.0),
            MassComponent("Gear bow 2", mass=4.0, x=1.0, y=0.0, z=0.05),
            MassComponent("Food", mass=10.0, x=1.2, y=0.0, z=0.1),
            MassComponent("Water", mass=8.0, x=2.2, y=0.0, z=0.0),
            MassComponent("Gear stern", mass=4.0, x=3.5, y=0.0, z=0.0),
        ],
    }
    
    # Analyze each scenario
    results = {}
    for name, components in scenarios.items():
        cg = calculate_cg_from_components(components)
        results[name] = cg
        
        print(f"\n{name}:")
        print(f"  Total mass: {cg.total_mass:.1f} kg")
        print(f"  LCG: {cg.lcg:.3f} m")
        print(f"  VCG: {cg.vcg:.3f} m")
        print(f"  Components: {cg.num_components}")
    
    # Compare to day trip baseline
    baseline = results["Day trip"]
    print(f"\nChanges relative to day trip:")
    for name, cg in results.items():
        if name != "Day trip":
            print(f"  {name}:")
            print(f"    Mass change: {cg.total_mass - baseline.total_mass:+.1f} kg")
            print(f"    LCG shift: {cg.lcg - baseline.lcg:+.3f} m")
            print(f"    VCG shift: {cg.vcg - baseline.vcg:+.3f} m")
    
    # Visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    
    scenario_names = list(results.keys())
    masses = [results[name].total_mass for name in scenario_names]
    lcgs = [results[name].lcg for name in scenario_names]
    vcgs = [results[name].vcg for name in scenario_names]
    
    x = np.arange(len(scenario_names))
    width = 0.25
    
    ax.bar(x - width, masses, width, label='Total Mass (kg)', alpha=0.8)
    ax.bar(x, np.array(lcgs) * 50, width, label='LCG × 50 (m)', alpha=0.8)
    ax.bar(x + width, np.array(vcgs) * 50, width, label='VCG × 50 (m)', alpha=0.8)
    
    ax.set_xlabel('Loading Scenario')
    ax.set_ylabel('Value')
    ax.set_title('CG Comparison Across Loading Scenarios')
    ax.set_xticks(x)
    ax.set_xticklabels(scenario_names)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('loading_scenarios_comparison.png', dpi=150, bbox_inches='tight')
    print(f"\nComparison plot saved to: loading_scenarios_comparison.png")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  CENTER OF GRAVITY CALCULATION EXAMPLES".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print("\n")
    
    example_1_basic_cg_calculation()
    example_2_manual_cg_specification()
    example_3_loading_adjustments()
    example_4_mass_distribution_analysis()
    example_5_validation_criteria()
    
    # Examples with visualization (optional, requires matplotlib)
    try:
        example_6_component_positions()
        example_7_comparing_loading_scenarios()
    except Exception as e:
        print(f"\nVisualization examples skipped: {e}")
    
    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
