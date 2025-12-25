"""
Examples demonstrating stability criteria checking and assessment.

This module shows how to use the stability criteria system to
evaluate kayak stability against standard requirements.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from src.geometry import Point3D, Profile, KayakHull
from src.hydrostatics import CenterOfGravity
from src.stability import (
    StabilityAnalyzer,
    StabilityCriteria,
    CriteriaResult,
    quick_stability_assessment
)


def create_example_hull() -> KayakHull:
    """Create an example kayak hull for demonstrations."""
    hull = KayakHull()
    
    for x_pos in np.linspace(0, 4, 7):
        points = [
            Point3D(x_pos, -0.6, 0.1),
            Point3D(x_pos, -0.6, -0.5),
            Point3D(x_pos, 0.6, -0.5),
            Point3D(x_pos, 0.6, 0.1),
        ]
        profile = Profile(station=x_pos, points=points)
        hull.add_profile(profile)
    
    return hull


def example1_basic_criteria_check():
    """
    Example 1: Basic Stability Criteria Check
    
    Shows how to check if a kayak meets basic stability requirements.
    """
    print("\n" + "="*70)
    print("Example 1: Basic Stability Criteria Check")
    print("="*70)
    
    # Create hull and CG
    hull = create_example_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.30, tcg=0.0, total_mass=100.0, num_components=1)
    
    # Analyze stability
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.25)
    metrics = analyzer.analyze_stability()
    
    # Create criteria checker with default thresholds
    criteria = StabilityCriteria()
    
    # Assess stability
    assessment = criteria.assess_stability(metrics)
    
    print(f"\nStability Assessment Results:")
    print(f"  Overall Result: {assessment.overall_result.value}")
    print(f"  Summary: {assessment.summary}")
    
    print(f"\nIndividual Criteria:")
    for check in assessment.criteria_checks:
        status_symbol = "✓" if check.result == CriteriaResult.PASS else "✗"
        print(f"  {status_symbol} {check.name}: {check.result.value}")
        if check.measured_value is not None:
            print(f"    Measured: {check.measured_value:.4f} {check.units}")
            print(f"    Required: >={check.required_value:.4f} {check.units}")
    
    if assessment.recommendations:
        print(f"\nRecommendations:")
        for i, rec in enumerate(assessment.recommendations, 1):
            print(f"  {i}. {rec}")


def example2_compare_configurations():
    """
    Example 2: Compare Multiple Configurations Against Criteria
    
    Shows how to assess and compare different kayak configurations.
    """
    print("\n" + "="*70)
    print("Example 2: Compare Multiple Configurations")
    print("="*70)
    
    hull = create_example_hull()
    
    # Three different CG configurations
    configs = [
        ("Low CG", CenterOfGravity(lcg=2.0, vcg=-0.35, tcg=0.0, total_mass=100.0)),
        ("Mid CG", CenterOfGravity(lcg=2.0, vcg=-0.28, tcg=0.0, total_mass=100.0)),
        ("High CG", CenterOfGravity(lcg=2.0, vcg=-0.22, tcg=0.0, total_mass=100.0)),
    ]
    
    criteria = StabilityCriteria()
    
    print(f"\nComparing {len(configs)} configurations:")
    print(f"{'Configuration':<15} {'Result':<10} {'Max GZ':<12} {'GM':<12} {'Vanish':<10}")
    print("-" * 65)
    
    results = []
    for name, cg in configs:
        analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.25)
        metrics = analyzer.analyze_stability()
        assessment = criteria.assess_stability(metrics)
        
        gm_str = f"{metrics.gm_estimate:.4f}" if metrics.gm_estimate else "N/A"
        
        print(f"{name:<15} {assessment.overall_result.value:<10} "
              f"{metrics.max_gz:<12.4f} {gm_str:<12} "
              f"{metrics.angle_of_vanishing_stability:<10.1f}")
        
        results.append((name, metrics, assessment))
    
    # Visualize comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Key metrics comparison
    ax1 = axes[0]
    names = [r[0] for r in results]
    max_gzs = [r[1].max_gz for r in results]
    gms = [r[1].gm_estimate if r[1].gm_estimate else 0 for r in results]
    
    x = np.arange(len(names))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, max_gzs, width, label='Max GZ (m)', alpha=0.8)
    bars2 = ax1.bar(x + width/2, gms, width, label='GM (m)', alpha=0.8)
    
    ax1.set_xlabel('Configuration')
    ax1.set_ylabel('Value (m)')
    ax1.set_title('Stability Metrics Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(names)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.8)
    
    # Plot 2: Criteria pass/fail counts
    ax2 = axes[1]
    passed = [len(r[2].get_passed_checks()) for r in results]
    failed = [len(r[2].get_failed_checks()) for r in results]
    warnings = [len(r[2].get_warning_checks()) for r in results]
    
    bars1 = ax2.bar(x, passed, label='Passed', color='green', alpha=0.7)
    bars2 = ax2.bar(x, warnings, bottom=passed, label='Warnings', color='orange', alpha=0.7)
    bars3 = ax2.bar(x, failed, bottom=np.array(passed)+np.array(warnings), 
                    label='Failed', color='red', alpha=0.7)
    
    ax2.set_xlabel('Configuration')
    ax2.set_ylabel('Number of Criteria')
    ax2.set_title('Criteria Check Results')
    ax2.set_xticks(x)
    ax2.set_xticklabels(names)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    plt.savefig(output_dir / "criteria_example2_comparison.png", dpi=150)
    print(f"\nPlot saved to {output_dir / 'criteria_example2_comparison.png'}")
    plt.close()


def example3_custom_criteria():
    """
    Example 3: Custom Criteria Thresholds
    
    Shows how to use custom thresholds for specific applications.
    """
    print("\n" + "="*70)
    print("Example 3: Custom Criteria Thresholds")
    print("="*70)
    
    hull = create_example_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.30, tcg=0.0, total_mass=100.0, num_components=1)
    
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.25)
    metrics = analyzer.analyze_stability()
    
    # Test with three different criteria strictness levels
    criteria_sets = [
        ("Relaxed", StabilityCriteria(
            min_gm=0.03,
            min_max_gz=0.10,
            min_angle_of_max_gz=20.0,
            min_range_positive=40.0,
            min_vanishing_angle=60.0,
            min_dynamic_stability=0.03
        )),
        ("Standard", StabilityCriteria()),  # Default values
        ("Strict", StabilityCriteria(
            min_gm=0.10,
            min_max_gz=0.25,
            min_angle_of_max_gz=35.0,
            min_range_positive=70.0,
            min_vanishing_angle=85.0,
            min_dynamic_stability=0.10
        )),
    ]
    
    print(f"\nTesting kayak against different criteria levels:")
    print(f"\nKayak Metrics:")
    print(f"  Max GZ: {metrics.max_gz:.4f} m")
    print(f"  GM: {metrics.gm_estimate:.4f} m" if metrics.gm_estimate else "  GM: N/A")
    print(f"  Vanishing Angle: {metrics.angle_of_vanishing_stability:.1f}°")
    
    print(f"\n{'Criteria Level':<15} {'Result':<12} {'Passed':<10} {'Warnings':<10} {'Failed':<10}")
    print("-" * 60)
    
    for name, criteria in criteria_sets:
        assessment = criteria.assess_stability(metrics)
        
        print(f"{name:<15} {assessment.overall_result.value:<12} "
              f"{len(assessment.get_passed_checks()):<10} "
              f"{len(assessment.get_warning_checks()):<10} "
              f"{len(assessment.get_failed_checks()):<10}")


def example4_detailed_check_analysis():
    """
    Example 4: Detailed Analysis of Individual Checks
    
    Shows detailed information for each criterion check.
    """
    print("\n" + "="*70)
    print("Example 4: Detailed Criterion Check Analysis")
    print("="*70)
    
    hull = create_example_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.30, tcg=0.0, total_mass=100.0, num_components=1)
    
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.25)
    metrics = analyzer.analyze_stability()
    
    criteria = StabilityCriteria()
    assessment = criteria.assess_stability(metrics)
    
    print(f"\nDetailed Criterion Analysis:")
    print("=" * 70)
    
    for check in assessment.criteria_checks:
        print(f"\n{check.name}")
        print(f"  Description: {check.description}")
        print(f"  Result: {check.result.value}")
        
        if check.measured_value is not None:
            print(f"  Measured: {check.measured_value:.6f} {check.units}")
        if check.required_value is not None:
            print(f"  Required: ≥ {check.required_value:.6f} {check.units}")
        
        print(f"  Details: {check.details}")
        
        if check.result == CriteriaResult.FAIL:
            print(f"  ⚠️  ATTENTION REQUIRED")
        elif check.result == CriteriaResult.WARNING:
            print(f"  ⚡ Warning - consider improvements")


def example5_strict_vs_normal_mode():
    """
    Example 5: Strict Mode Comparison
    
    Shows the difference between normal and strict mode evaluation.
    """
    print("\n" + "="*70)
    print("Example 5: Strict Mode vs Normal Mode")
    print("="*70)
    
    hull = create_example_hull()
    # Use marginal stability
    cg = CenterOfGravity(lcg=2.0, vcg=-0.27, tcg=0.0, total_mass=100.0, num_components=1)
    
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.25)
    metrics = analyzer.analyze_stability()
    
    # Normal mode
    criteria_normal = StabilityCriteria(strict_mode=False)
    assessment_normal = criteria_normal.assess_stability(metrics)
    
    # Strict mode
    criteria_strict = StabilityCriteria(strict_mode=True)
    assessment_strict = criteria_strict.assess_stability(metrics)
    
    print(f"\nNormal Mode Assessment:")
    print(f"  Overall Result: {assessment_normal.overall_result.value}")
    print(f"  Passed: {len(assessment_normal.get_passed_checks())}")
    print(f"  Warnings: {len(assessment_normal.get_warning_checks())}")
    print(f"  Failed: {len(assessment_normal.get_failed_checks())}")
    
    print(f"\nStrict Mode Assessment:")
    print(f"  Overall Result: {assessment_strict.overall_result.value}")
    print(f"  Passed: {len(assessment_strict.get_passed_checks())}")
    print(f"  Warnings: {len(assessment_strict.get_warning_checks())}")
    print(f"  Failed: {len(assessment_strict.get_failed_checks())}")
    
    print(f"\nDifference:")
    print(f"  In strict mode, warnings become failures")
    print(f"  Strict mode converted {len(assessment_normal.get_warning_checks())} warnings")
    print(f"  to failures for more conservative evaluation")


def example6_quick_assessment():
    """
    Example 6: Quick Stability Assessment
    
    Shows using the convenience function for rapid evaluation.
    """
    print("\n" + "="*70)
    print("Example 6: Quick Stability Assessment")
    print("="*70)
    
    hull = create_example_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.30, tcg=0.0, total_mass=100.0, num_components=1)
    
    # Get metrics
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.25)
    metrics = analyzer.analyze_stability()
    
    # Quick assessment
    assessment = quick_stability_assessment(metrics)
    
    print(f"\nQuick Assessment Result: {assessment.overall_result.value}")
    print(f"Summary: {assessment.summary}")
    
    if assessment.overall_result != CriteriaResult.PASS:
        print(f"\nTop Recommendations:")
        for i, rec in enumerate(assessment.recommendations[:3], 1):
            print(f"  {i}. {rec}")


def example7_visual_criteria_report():
    """
    Example 7: Visual Criteria Report
    
    Creates a comprehensive visual report of stability criteria.
    """
    print("\n" + "="*70)
    print("Example 7: Visual Criteria Report")
    print("="*70)
    
    hull = create_example_hull()
    cg = CenterOfGravity(lcg=2.0, vcg=-0.30, tcg=0.0, total_mass=100.0, num_components=1)
    
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.25)
    metrics = analyzer.analyze_stability()
    curve = analyzer.generate_stability_curve()
    
    criteria = StabilityCriteria()
    assessment = criteria.assess_stability(metrics, curve)
    
    # Create comprehensive report figure
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # Plot 1: GZ Curve with key points
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(curve.heel_angles, curve.gz_values, 'b-', linewidth=2)
    ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax1.axvline(x=metrics.angle_of_max_gz, color='r', linestyle='--', 
                alpha=0.5, label=f'Max GZ at {metrics.angle_of_max_gz:.1f}°')
    ax1.axvline(x=metrics.angle_of_vanishing_stability, color='orange', 
                linestyle='--', alpha=0.5, 
                label=f'Vanishing at {metrics.angle_of_vanishing_stability:.1f}°')
    ax1.set_xlabel('Heel Angle (degrees)')
    ax1.set_ylabel('GZ (m)')
    ax1.set_title('Stability Curve with Key Points')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Criteria check results
    ax2 = fig.add_subplot(gs[1, 0])
    
    results_count = {
        'Pass': len(assessment.get_passed_checks()),
        'Warning': len(assessment.get_warning_checks()),
        'Fail': len(assessment.get_failed_checks())
    }
    
    colors = ['green', 'orange', 'red']
    ax2.bar(results_count.keys(), results_count.values(), color=colors, alpha=0.7)
    ax2.set_ylabel('Number of Criteria')
    ax2.set_title('Criteria Check Summary')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Plot 3: Metric comparison to requirements
    ax3 = fig.add_subplot(gs[1, 1])
    
    metric_names = ['GM', 'Max GZ', 'Max GZ\nAngle', 'Vanish\nAngle']
    measured = [
        metrics.gm_estimate if metrics.gm_estimate else 0,
        metrics.max_gz,
        metrics.angle_of_max_gz,
        metrics.angle_of_vanishing_stability
    ]
    required = [
        criteria.min_gm,
        criteria.min_max_gz,
        criteria.min_angle_of_max_gz,
        criteria.min_vanishing_angle
    ]
    
    # Normalize to percentages of requirement
    percentages = [m/r*100 if r > 0 else 0 for m, r in zip(measured, required)]
    
    bars = ax3.barh(metric_names, percentages, alpha=0.7)
    
    # Color bars based on performance
    for i, (bar, pct) in enumerate(zip(bars, percentages)):
        if pct >= 100:
            bar.set_color('green')
        elif pct >= 80:
            bar.set_color('orange')
        else:
            bar.set_color('red')
    
    ax3.axvline(x=100, color='k', linestyle='--', linewidth=2, label='Required')
    ax3.set_xlabel('% of Requirement')
    ax3.set_title('Metrics vs Requirements')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='x')
    
    # Plot 4: Assessment text
    ax4 = fig.add_subplot(gs[2, :])
    ax4.axis('off')
    
    report_text = f"STABILITY ASSESSMENT REPORT\n\n"
    report_text += f"Overall Result: {assessment.overall_result.value}\n"
    report_text += f"{assessment.summary}\n\n"
    report_text += "Individual Criteria:\n"
    
    for check in assessment.criteria_checks:
        status = "✓" if check.result == CriteriaResult.PASS else "✗"
        report_text += f"  {status} {check.name}: {check.result.value}\n"
    
    ax4.text(0.05, 0.95, report_text, transform=ax4.transAxes,
             fontsize=9, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.suptitle('Kayak Stability Criteria Assessment', fontsize=14, fontweight='bold')
    
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    plt.savefig(output_dir / "criteria_example7_report.png", dpi=150)
    print(f"\nVisual report saved to {output_dir / 'criteria_example7_report.png'}")
    plt.close()


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("Stability Criteria Examples")
    print("="*70)
    print("\nThese examples demonstrate the stability criteria assessment")
    print("system for evaluating kayak safety and seaworthiness.")
    
    example1_basic_criteria_check()
    example2_compare_configurations()
    example3_custom_criteria()
    example4_detailed_check_analysis()
    example5_strict_vs_normal_mode()
    example6_quick_assessment()
    example7_visual_criteria_report()
    
    print("\n" + "="*70)
    print("All examples completed successfully!")
    print("="*70)


if __name__ == '__main__':
    main()
