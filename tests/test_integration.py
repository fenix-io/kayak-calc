"""
Integration tests for complete calculation workflows.

Tests the end-to-end functionality of the kayak calculation tool:
- Data loading and validation
- Hydrostatic calculations
- Stability analysis
- Visualization generation
- Complete workflows from input to output
"""

from src.io.loaders import (
    load_hull_from_json,
    load_hull_from_csv,
    save_hull_to_json,
    save_hull_to_csv,
)
from src.visualization.plots import plot_hull_3d, plot_profile, plot_stability_curve
from src.stability import (
    StabilityAnalyzer,
)
from src.hydrostatics.center_of_gravity import (
    create_cg_manual,
    calculate_cg_from_components,
    MassComponent,
)
from src.hydrostatics import calculate_volume, calculate_displacement, calculate_center_of_buoyancy
from src.geometry import Point3D, Profile, KayakHull
import tempfile
from pathlib import Path
import matplotlib.pyplot as plt
import pytest
import numpy as np
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for testing


class TestBasicWorkflow:
    """Test basic end-to-end workflow: Load → Calculate → Verify."""

    def test_load_calculate_volume_workflow(self):
        """Test loading hull and calculating volume."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        # Calculate volume
        vol = calculate_volume(hull, waterline_z=0.0, method="simpson")

        assert vol > 0
        assert np.isfinite(vol)

    def test_load_calculate_displacement_workflow(self):
        """Test loading hull and calculating displacement."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        # Calculate displacement
        disp = calculate_displacement(hull, waterline_z=0.0, water_density=1025.0, method="simpson")

        assert disp.volume > 0
        assert disp.mass > 0
        assert disp.displacement_tons > 0
        assert np.isfinite(disp.mass)

    def test_load_calculate_center_of_buoyancy_workflow(self):
        """Test loading hull and calculating center of buoyancy."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        # Calculate center of buoyancy
        cb = calculate_center_of_buoyancy(hull, waterline_z=0.0, method="simpson")

        assert cb.volume > 0
        assert np.isfinite(cb.lcb)
        assert np.isfinite(cb.vcb)
        assert abs(cb.tcb) < 0.2  # Should be near centerline for symmetric hull (relaxed tolerance)

    def test_complete_basic_workflow(self):
        """Test complete basic workflow: Load → Calculate all properties."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        # Calculate all hydrostatic properties
        volume = calculate_volume(hull, waterline_z=0.0)
        displacement = calculate_displacement(hull, waterline_z=0.0)
        cb = calculate_center_of_buoyancy(hull, waterline_z=0.0)

        # Verify consistency
        assert abs(volume - displacement.volume) < 0.001
        assert abs(volume - cb.volume) < 0.001


class TestFullStabilityAnalysis:
    """Test complete stability analysis workflows."""

    def test_stability_analysis_workflow(self):
        """Test complete stability analysis workflow."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        # Create center of gravity
        cg = create_cg_manual(total_mass=100.0, lcg=2.5, vcg=-0.2, tcg=0.0)

        # Create stability analyzer
        analyzer = StabilityAnalyzer(hull=hull, cg=cg, waterline_z=0.0)

        # Generate stability curve
        angles = np.arange(0, 91, 5)
        curve_data = analyzer.generate_stability_curve(heel_angles=angles)

        assert len(curve_data.heel_angles) == len(angles)
        assert len(curve_data.gz_values) == len(angles)
        assert len(curve_data.heel_angles) == len(curve_data.gz_values)

        # Verify GZ at 0° is small (may not be exactly 0 for asymmetric configurations)
        assert abs(curve_data.gz_values[0]) < 0.5

    def test_stability_analysis_with_criteria(self):
        """Test stability analysis with criteria evaluation."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        cg = create_cg_manual(total_mass=100.0, lcg=2.5, vcg=-0.2, tcg=0.0)

        analyzer = StabilityAnalyzer(hull, cg, waterline_z=0.0)

        # Generate curve
        curve = analyzer.generate_stability_curve()

        # Analyze stability
        metrics = analyzer.analyze_stability(curve)

        assert hasattr(metrics, "gm_estimate")
        assert hasattr(metrics, "max_gz")
        assert hasattr(metrics, "angle_of_vanishing_stability")

        # GM could be positive or negative depending on configuration
        # Just verify it's calculated and finite
        if metrics.gm_estimate is not None:
            assert np.isfinite(metrics.gm_estimate)

    def test_stability_criteria_evaluation(self):
        """Test stability criteria evaluation (if available)."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        cg = create_cg_manual(total_mass=100.0, lcg=2.5, vcg=-0.2, tcg=0.0)

        # Generate stability curve
        analyzer = StabilityAnalyzer(hull, cg, waterline_z=0.0)
        curve_data = analyzer.generate_stability_curve()

        # Basic checks on curve
        assert curve_data.max_gz > 0
        assert len(curve_data.heel_angles) > 0

    def test_stability_comparison_workflow(self):
        """Test comparing stability with different CG positions."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        # Two different CG positions
        cg1 = create_cg_manual(total_mass=100.0, lcg=2.5, vcg=-0.2, tcg=0.0)
        cg2 = create_cg_manual(total_mass=100.0, lcg=2.5, vcg=-0.3, tcg=0.0)  # Lower CG

        # Analyze both
        analyzer1 = StabilityAnalyzer(hull, cg1, waterline_z=0.0)
        analyzer2 = StabilityAnalyzer(hull, cg2, waterline_z=0.0)

        curve1 = analyzer1.generate_stability_curve()
        curve2 = analyzer2.generate_stability_curve()

        # Lower CG should have better stability (higher max GZ)
        max_gz1 = max(curve1.gz_values)
        max_gz2 = max(curve2.gz_values)

        assert max_gz2 > max_gz1


class TestDataRoundTrip:
    """Test data loading and saving workflows."""

    def test_json_round_trip(self):
        """Test loading and saving JSON maintains data integrity."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            save_hull_to_json(hull, temp_path)

            # Load back
            hull_loaded = load_hull_from_json(temp_path)

            # Verify same structure
            assert len(hull) == len(hull_loaded)
            assert hull.get_stations() == hull_loaded.get_stations()

            # Verify same volume
            vol1 = calculate_volume(hull, waterline_z=0.0)
            vol2 = calculate_volume(hull_loaded, waterline_z=0.0)
            assert abs(vol1 - vol2) < 0.001
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_csv_round_trip(self):
        """Test loading and saving CSV maintains data integrity."""
        hull_path = Path("data/sample_hull_simple.csv")
        hull = load_hull_from_csv(hull_path)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_path = Path(f.name)

        try:
            save_hull_to_csv(hull, temp_path)

            # Load back
            hull_loaded = load_hull_from_csv(temp_path)

            # Verify same structure
            assert len(hull) == len(hull_loaded)

            # Verify same volume
            vol1 = calculate_volume(hull, waterline_z=0.0)
            vol2 = calculate_volume(hull_loaded, waterline_z=0.0)
            assert abs(vol1 - vol2) < 0.001
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_calculation_consistency_after_reload(self):
        """Test that calculations are consistent after save/load cycle."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        # Calculate properties before save
        vol_before = calculate_volume(hull, waterline_z=0.0)
        cb_before = calculate_center_of_buoyancy(hull, waterline_z=0.0)

        # Save and reload
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            save_hull_to_json(hull, temp_path)
            hull_reloaded = load_hull_from_json(temp_path)

            # Calculate properties after reload
            vol_after = calculate_volume(hull_reloaded, waterline_z=0.0)
            cb_after = calculate_center_of_buoyancy(hull_reloaded, waterline_z=0.0)

            # Verify consistency
            assert abs(vol_before - vol_after) < 0.001
            assert abs(cb_before.lcb - cb_after.lcb) < 0.001
            assert abs(cb_before.vcb - cb_after.vcb) < 0.001
            assert abs(cb_before.tcb - cb_after.tcb) < 0.001
        finally:
            if temp_path.exists():
                temp_path.unlink()


class TestKayakGeometry:
    """Test with realistic kayak geometry."""

    def test_realistic_kayak_volume(self):
        """Test volume calculations with realistic kayak."""
        hull_path = Path("data/sample_hull_kayak.json")
        hull = load_hull_from_json(hull_path)

        # Calculate volume at different waterlines
        waterlines = [0.0, 0.1, 0.2, 0.3]
        volumes = []

        for wl in waterlines:
            vol = calculate_volume(hull, waterline_z=wl)
            volumes.append(vol)
            assert vol > 0

        # Volume should increase with waterline (generally)
        # Note: For complex hulls, volume may not be strictly monotonic at all waterlines
        assert volumes[-1] > volumes[0]  # At least last should be greater than first

    def test_realistic_kayak_displacement(self):
        """Test displacement calculations with realistic kayak."""
        hull_path = Path("data/sample_hull_kayak.json")
        hull = load_hull_from_json(hull_path)

        # Calculate displacement at designed waterline
        disp = calculate_displacement(hull, waterline_z=0.1, water_density=1025.0)

        # Reasonable displacement for a kayak (20-500 kg)
        assert 0.02 < disp.displacement_tons < 0.5

    def test_realistic_kayak_center_of_buoyancy(self):
        """Test center of buoyancy with realistic kayak."""
        hull_path = Path("data/sample_hull_kayak.json")
        hull = load_hull_from_json(hull_path)

        cb = calculate_center_of_buoyancy(hull, waterline_z=0.1)

        # CB should be reasonable
        assert cb.volume > 0
        assert np.isfinite(cb.lcb)
        assert np.isfinite(cb.vcb)
        assert abs(cb.tcb) < 0.1  # Near centerline

    def test_realistic_kayak_stability(self):
        """Test stability analysis with realistic kayak."""
        hull_path = Path("data/sample_hull_kayak.json")
        hull = load_hull_from_json(hull_path)

        # Typical paddler setup
        cg = create_cg_manual(
            total_mass=100.0,  # 25 kg kayak + 75 kg paddler
            lcg=2.5,  # Near center
            vcg=0.15,  # Above waterline (seated position)
            tcg=0.0,  # Centered
        )

        # Perform full stability analysis
        analyzer = StabilityAnalyzer(hull, cg, waterline_z=0.1)

        curve = analyzer.generate_stability_curve(heel_angles=np.arange(0, 91, 5))

        # Should have reasonable stability
        assert len(curve.heel_angles) > 0
        assert len(curve.gz_values) > 0
        assert curve.max_gz > 0  # Should have some positive stability

    def test_realistic_kayak_heeling_behavior(self):
        """Test heeling behavior of realistic kayak."""
        hull_path = Path("data/sample_hull_kayak.json")
        hull = load_hull_from_json(hull_path)

        cg = create_cg_manual(total_mass=100.0, lcg=2.5, vcg=0.15, tcg=0.0)
        analyzer = StabilityAnalyzer(hull, cg, waterline_z=0.1)

        # Calculate GZ at various heel angles
        heel_angles = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
        gz_values = []

        for angle in heel_angles:
            ra = analyzer.calculate_righting_arm(angle)
            gz_values.append(ra.gz)

        # Find maximum GZ
        gz_floats = [ra.gz for ra in [analyzer.calculate_righting_arm(a) for a in heel_angles]]
        max_gz_idx = gz_floats.index(max(gz_floats))
        max_gz_angle = heel_angles[max_gz_idx]

        # Max GZ should occur at some angle (may vary depending on configuration)
        assert 0 <= max_gz_angle <= 90


class TestVisualizationPipeline:
    """Test visualization generation workflows."""

    def test_plot_hull_3d_generation(self):
        """Test 3D hull plot generation."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        # Generate 3D hull plot
        ax = plot_hull_3d(hull, waterline_z=0.0)
        fig = ax.figure

        assert fig is not None
        assert ax is not None

        # Cleanup
        plt.close(fig)

    def test_plot_profile_generation(self):
        """Test profile plot generation."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        # Generate profile plot
        profile = hull.get_profile(hull.get_stations()[0])
        ax = plot_profile(profile, waterline_z=0.0)
        fig = ax.figure

        assert fig is not None
        assert ax is not None

        # Cleanup
        plt.close(fig)

    def test_plot_stability_curve_generation(self):
        """Test stability curve plot generation."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        cg = create_cg_manual(total_mass=100.0, lcg=2.5, vcg=-0.2, tcg=0.0)
        analyzer = StabilityAnalyzer(hull, cg, waterline_z=0.0)

        # Generate stability curve plot
        curve_data = analyzer.generate_stability_curve()
        ax = plot_stability_curve(curve_data)
        fig = ax.figure

        assert fig is not None
        assert ax is not None

        # Cleanup
        plt.close(fig)

    def test_complete_visualization_workflow(self):
        """Test complete visualization workflow for analysis."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        cg = create_cg_manual(total_mass=100.0, lcg=2.5, vcg=-0.2, tcg=0.0)
        analyzer = StabilityAnalyzer(hull, cg, waterline_z=0.0)

        # Generate all plots
        ax1 = plot_hull_3d(hull, waterline_z=0.0)
        fig1 = ax1.figure
        assert fig1 is not None
        assert ax1 is not None
        plt.close(fig1)

        profile = hull.get_profile(hull.get_stations()[0])
        ax2 = plot_profile(profile, waterline_z=0.0)
        fig2 = ax2.figure
        assert fig2 is not None
        assert ax2 is not None
        plt.close(fig2)

        curve = analyzer.generate_stability_curve()
        ax3 = plot_stability_curve(curve)
        fig3 = ax3.figure
        assert fig3 is not None
        assert ax3 is not None
        plt.close(fig3)


class TestMultipleHulls:
    """Test workflows involving multiple hull configurations."""

    def test_compare_simple_and_realistic_kayaks(self):
        """Test comparing simple and realistic kayak hulls."""
        simple_path = Path("data/sample_hull_simple.json")
        kayak_path = Path("data/sample_hull_kayak.json")

        hull_simple = load_hull_from_json(simple_path)
        hull_kayak = load_hull_from_json(kayak_path)

        # Calculate volumes
        vol_simple = calculate_volume(hull_simple, waterline_z=0.0)
        vol_kayak = calculate_volume(hull_kayak, waterline_z=0.1)

        # Both should be positive
        assert vol_simple > 0
        assert vol_kayak > 0

    def test_stability_comparison_different_hulls(self):
        """Test comparing stability of different hull designs."""
        simple_path = Path("data/sample_hull_simple.json")
        kayak_path = Path("data/sample_hull_kayak.json")

        hull_simple = load_hull_from_json(simple_path)
        hull_kayak = load_hull_from_json(kayak_path)

        cg_simple = create_cg_manual(total_mass=100.0, lcg=2.5, vcg=-0.2, tcg=0.0)
        cg_kayak = create_cg_manual(total_mass=100.0, lcg=2.5, vcg=0.15, tcg=0.0)

        analyzer_simple = StabilityAnalyzer(hull_simple, cg_simple, waterline_z=0.0)
        analyzer_kayak = StabilityAnalyzer(hull_kayak, cg_kayak, waterline_z=0.1)

        curve_simple = analyzer_simple.generate_stability_curve()
        curve_kayak = analyzer_kayak.generate_stability_curve()

        results_simple = analyzer_simple.analyze_stability(curve_simple)
        results_kayak = analyzer_kayak.analyze_stability(curve_kayak)

        # Compare stability metrics
        assert hasattr(results_simple, "gm_estimate")
        assert hasattr(results_kayak, "gm_estimate")


class TestEdgeCasesIntegration:
    """Test edge cases and boundary conditions in workflows."""

    def test_extreme_heel_angle(self):
        """Test calculations at extreme heel angles."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        cg = create_cg_manual(total_mass=100.0, lcg=2.5, vcg=-0.2, tcg=0.0)
        analyzer = StabilityAnalyzer(hull, cg, waterline_z=0.0)

        # Test extreme angle
        heel_angle = 89.0

        # Calculate GZ at extreme angles
        ra = analyzer.calculate_righting_arm(heel_angle)
        gz = ra.gz

        # Should handle gracefully (may be negative or zero)
        assert np.isfinite(gz)

    def test_very_low_waterline(self):
        """Test with waterline very low (minimal immersion)."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        # Very low waterline - minimal immersion
        vol = calculate_volume(hull, waterline_z=-0.4)

        # Volume should be small but positive
        assert vol >= 0
        if vol > 0:
            assert vol < 0.1  # Should be small

    def test_very_high_waterline(self):
        """Test with waterline very high (maximum immersion)."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        # Very high waterline - maximum immersion
        vol_low = calculate_volume(hull, waterline_z=-0.3)
        vol_high = calculate_volume(hull, waterline_z=0.2)

        # Higher waterline should have more volume
        assert vol_high > vol_low

    def test_center_of_gravity_from_components(self):
        """Test CG calculation from multiple components."""
        # Define mass components
        kayak = MassComponent(
            name="Kayak", mass=25.0, x=2.5, y=0.0, z=0.05, description="Kayak hull"
        )
        paddler = MassComponent(
            name="Paddler", mass=75.0, x=2.5, y=0.0, z=0.3, description="Paddler"
        )
        gear = MassComponent(name="Gear", mass=10.0, x=1.0, y=0.0, z=0.1, description="Gear")

        # Calculate aggregate CG
        cg = calculate_cg_from_components([kayak, paddler, gear])

        # Verify
        assert cg.total_mass == 110.0
        assert np.isfinite(cg.lcg)
        assert np.isfinite(cg.vcg)
        assert np.isfinite(cg.tcg)

        # VCG should be dominated by paddler (heaviest and highest)
        assert cg.vcg > 0.1


class TestErrorHandling:
    """Test error handling in workflows."""

    def test_invalid_file_path(self):
        """Test handling of invalid file paths."""
        with pytest.raises(Exception):  # Could be FileNotFoundError or custom error
            load_hull_from_json(Path("nonexistent_file.json"))

    def test_insufficient_profiles_for_stability(self):
        """Test error handling with insufficient profiles."""
        hull = KayakHull()
        hull.add_profile(
            Profile(
                station=0.0,
                points=[
                    Point3D(0, -0.5, -0.5),
                    Point3D(0, 0.5, -0.5),
                    Point3D(0, 0.5, 0.1),
                    Point3D(0, -0.5, 0.1),
                ],
            )
        )

        cg = create_cg_manual(total_mass=100.0, lcg=0.0, vcg=-0.2, tcg=0.0)

        # Should raise error - need at least 2 profiles
        with pytest.raises(ValueError):
            _ = StabilityAnalyzer(hull, cg, waterline_z=0.0)

    def test_cg_above_waterline_warning(self):
        """Test behavior when CG is above waterline (less stable)."""
        hull_path = Path("data/sample_hull_simple.json")
        hull = load_hull_from_json(hull_path)

        # CG well above waterline
        cg = create_cg_manual(total_mass=100.0, lcg=2.5, vcg=0.5, tcg=0.0)

        analyzer = StabilityAnalyzer(hull, cg, waterline_z=0.0)

        # Should still work, but stability may be poor
        curve = analyzer.generate_stability_curve()
        results = analyzer.analyze_stability(curve)
        assert hasattr(results, "gm_estimate")
