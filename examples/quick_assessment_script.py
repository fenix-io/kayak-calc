"""
Quick Assessment Script

This script provides a template for rapid initial stability assessment of a kayak.
Perfect for quick checks during design iterations.

This script demonstrates:
- Minimal setup with quick data loading
- Using high-level convenience functions
- Rapid stability assessment
- Console summary output
- Quick report generation

Prerequisites:
- Sample hull data file: data/sample_hull_kayak.json
- Python packages: numpy

Expected outputs:
- Console summary of key stability parameters
- examples/output/quick_assessment_report.md (optional)

Usage:
    python examples/quick_assessment_script.py

Author: Kayak Calculation Tool
Version: 1.0
"""

from pathlib import Path

# Import kayak calculation modules
from src.io import load_hull_from_json
from src.hydrostatics import CenterOfGravity, calculate_center_of_buoyancy
from src.stability import StabilityAnalyzer, quick_stability_analysis, quick_stability_assessment

# Configure output directory
OUTPUT_DIR = Path("examples/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    """
    Quick assessment workflow - minimal setup, fast results.

    This is a template you can copy and adapt for your own quick checks.
    """

    print("=" * 70)
    print("QUICK STABILITY ASSESSMENT")
    print("=" * 70)

    # =========================================================================
    # STEP 1: Load Hull (or define simple hull)
    # =========================================================================
    print("\nLoading hull...")

    hull_file = Path("data/sample_hull_kayak.json")
    hull = load_hull_from_json(hull_file)
    print(f"  ✓ Hull loaded from {hull_file.name}")

    # =========================================================================
    # STEP 2: Define CG (Center of Gravity)
    # =========================================================================
    print("\nDefining center of gravity...")

    # Simple CG definition - adjust these values for your kayak
    # Typical values for a kayak with seated paddler:
    #   LCG: Near middle of kayak length
    #   VCG: Slightly below waterline (seated position lowers CG)
    #   Total mass: Kayak + paddler + gear

    cg = CenterOfGravity(
        lcg=2.5,  # meters - longitudinal position
        vcg=-0.15,  # meters - vertical position (below waterline is negative)
        tcg=0.0,  # meters - transverse position (0 = centerline)
        total_mass=95.0,  # kg - total mass (kayak + paddler + gear)
        num_components=1,
    )

    print(f"  ✓ CG defined: LCG={cg.lcg:.2f}m, VCG={cg.vcg:.2f}m, Mass={cg.total_mass:.0f}kg")

    # =========================================================================
    # STEP 3: Define Waterline
    # =========================================================================

    # Waterline at z = 0 (typical reference)
    waterline_z = 0.0
    print(f"\n  Waterline level: z = {waterline_z:.2f}m")

    # =========================================================================
    # STEP 4: Quick Stability Analysis
    # =========================================================================
    print("\n" + "-" * 70)
    print("RUNNING STABILITY ANALYSIS")
    print("-" * 70)

    # Calculate center of buoyancy for volume info
    cb = calculate_center_of_buoyancy(hull, waterline_z=waterline_z)

    # Use the high-level convenience function for stability
    # This calculates everything in one call
    results = quick_stability_analysis(hull=hull, cg=cg, waterline_z=waterline_z)

    # Extract key results
    volume = cb.volume
    water_density = 1000.0  # kg/m³
    displaced_mass = volume * water_density
    lcb = cb.lcb
    vcb = cb.vcb
    gm = results["gm"]
    max_gz = results["max_gz"]
    max_gz_angle = results["angle_of_max_gz"]
    vanishing_angle = results["vanishing_angle"]

    # =========================================================================
    # STEP 5: Display Results
    # =========================================================================
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    print("\nHydrostatic Properties:")
    print(f"  • Displacement Volume:  {volume:.4f} m³")
    print(f"  • Displaced Mass:       {displaced_mass:.1f} kg")
    print(f"  • Center of Buoyancy:   LCB={lcb:.3f}m, VCB={vcb:.3f}m")

    print("\nStability Metrics:")
    print(f"  • Initial Stability (GM):      {gm:.3f} m")
    print(f"  • Maximum Righting Arm (GZ):   {max_gz:.3f} m at {max_gz_angle:.1f}°")
    print(f"  • Vanishing Stability Angle:   {vanishing_angle:.1f}°")

    # =========================================================================
    # STEP 6: Quick Criteria Check
    # =========================================================================
    print("\n" + "-" * 70)
    print("STABILITY CRITERIA CHECK")
    print("-" * 70)

    # Check against standard stability criteria
    # We need to create an analyzer first to get the metrics
    analyzer = StabilityAnalyzer(hull, cg, waterline_z=waterline_z)
    curve_for_criteria = analyzer.generate_stability_curve(max_angle=70)
    metrics_obj = analyzer.analyze_stability(curve_for_criteria)

    # Perform assessment
    assessment = quick_stability_assessment(metrics_obj)

    # Display pass/fail status
    from src.stability.criteria import CriteriaResult

    overall_pass = assessment.overall_result == CriteriaResult.PASS
    status_symbol = "✓" if overall_pass else "✗"
    status_text = assessment.overall_result.value

    print(f"\nOverall Status: {status_symbol} {status_text}")

    # Show individual criteria
    print("\nIndividual Criteria:")
    for check in assessment.criteria_checks:
        passed = check.result == CriteriaResult.PASS
        symbol = "✓" if passed else ("⚠" if check.result == CriteriaResult.WARNING else "✗")
        value = check.measured_value if check.measured_value is not None else 0
        threshold = check.required_value if check.required_value is not None else 0

        print(f"  {symbol} {check.name}:")
        print(f"      Measured: {value:.3f}, Required: {threshold:.3f}")

    # =========================================================================
    # STEP 7: Interpretation
    # =========================================================================
    print("\n" + "-" * 70)
    print("INTERPRETATION")
    print("-" * 70)

    # Interpret GM
    if gm > 0.3:
        gm_assessment = "GOOD - High initial stability"
    elif gm > 0.15:
        gm_assessment = "ADEQUATE - Moderate initial stability"
    elif gm > 0:
        gm_assessment = "LOW - Minimal initial stability"
    else:
        gm_assessment = "UNSTABLE - Negative GM!"

    print(f"\nInitial Stability (GM = {gm:.3f}m): {gm_assessment}")

    # Interpret max GZ
    if max_gz > 0.5:
        gz_assessment = "EXCELLENT - Strong righting ability"
    elif max_gz > 0.3:
        gz_assessment = "GOOD - Adequate righting ability"
    elif max_gz > 0.15:
        gz_assessment = "MODERATE - Limited righting ability"
    else:
        gz_assessment = "POOR - Very limited righting ability"

    print(f"Max Righting Arm (GZ = {max_gz:.3f}m): {gz_assessment}")

    # Interpret vanishing angle
    if vanishing_angle > 80:
        va_assessment = "EXCELLENT - Can recover from extreme heels"
    elif vanishing_angle > 60:
        va_assessment = "GOOD - Can recover from large heels"
    elif vanishing_angle > 40:
        va_assessment = "MODERATE - Limited capsize recovery"
    else:
        va_assessment = "POOR - Very limited stability range"

    print(f"Vanishing Angle ({vanishing_angle:.1f}°): {va_assessment}")

    # Overall assessment
    print("\nOverall Assessment:")
    if overall_pass and gm > 0.2 and max_gz > 0.3:
        print("  ✓ This configuration appears suitable for typical kayak use.")
    elif overall_pass:
        print("  ⚠ Meets minimum criteria but consider improvements.")
    else:
        print("  ✗ Does not meet stability criteria. Design modifications needed.")

    # =========================================================================
    # STEP 8: Recommendations
    # =========================================================================
    print("\n" + "-" * 70)
    print("RECOMMENDATIONS")
    print("-" * 70)

    recommendations = []

    if gm < 0.15:
        recommendations.append("• Lower the CG to improve initial stability (GM)")

    if max_gz < 0.3:
        recommendations.append("• Increase beam width to improve maximum righting arm")

    if vanishing_angle < 60:
        recommendations.append(
            "• Consider hull shape modifications for better large-angle stability"
        )

    if displaced_mass < cg.total_mass * 0.95:
        recommendations.append("• Warning: Kayak may sit too low in water - check waterline")

    if displaced_mass > cg.total_mass * 1.05:
        recommendations.append("• Kayak will sit higher than designed waterline")

    if not recommendations:
        print("  No significant issues identified.")
    else:
        print("  Suggested improvements:")
        for rec in recommendations:
            print(f"  {rec}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("ASSESSMENT COMPLETE")
    print("=" * 70)

    print("\nFor detailed analysis and visualizations, run:")
    print("  python examples/complete_stability_analysis.py")

    print("\nTo compare multiple configurations, run:")
    print("  python examples/parametric_study_workflow.py")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
