"""
Tests for StabilityAnalyzer class.

This test suite validates the stability analyzer functionality, including:
- Initialization and configuration
- Single heel angle calculations
- Stability curve generation
- Metrics analysis
- Comparison methods
- Convenience methods
"""

import pytest
import numpy as np
from numpy.testing import assert_allclose

from src.geometry import Point3D, Profile, KayakHull
from src.hydrostatics import CenterOfGravity
from src.stability import (
    StabilityAnalyzer,
    StabilityCurve,
    StabilityMetrics,
    quick_stability_analysis,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def simple_box_hull():
    """Create a simple box hull for testing."""
    hull = KayakHull()

    for x_pos in [0.0, 2.0, 4.0]:
        points = [
            Point3D(x_pos, -0.5, 0.0),  # Top-left
            Point3D(x_pos, -0.5, -0.6),  # Bottom-left
            Point3D(x_pos, 0.5, -0.6),  # Bottom-right
            Point3D(x_pos, 0.5, 0.0),  # Top-right
        ]
        profile = Profile(station=x_pos, points=points)
        hull.add_profile(profile)

    return hull


@pytest.fixture
def cg_centerline():
    """CG on centerline for testing."""
    return CenterOfGravity(lcg=2.0, vcg=-0.35, tcg=0.0, total_mass=100.0, num_components=1)


# ============================================================================
# Test StabilityAnalyzer Initialization
# ============================================================================


class TestStabilityAnalyzerInit:
    """Tests for StabilityAnalyzer initialization."""

    def test_basic_initialization(self, simple_box_hull, cg_centerline):
        """Test basic initialization with required parameters."""
        analyzer = StabilityAnalyzer(hull=simple_box_hull, cg=cg_centerline, waterline_z=-0.3)

        assert analyzer.hull is simple_box_hull
        assert analyzer.cg is cg_centerline
        assert analyzer.waterline_z == -0.3
        assert analyzer.integration_method == "simpson"
        assert analyzer.num_stations is None

    def test_initialization_with_options(self, simple_box_hull, cg_centerline):
        """Test initialization with optional parameters."""
        analyzer = StabilityAnalyzer(
            hull=simple_box_hull,
            cg=cg_centerline,
            waterline_z=-0.3,
            num_stations=10,
            integration_method="trapezoidal",
        )

        assert analyzer.num_stations == 10
        assert analyzer.integration_method == "trapezoidal"

    def test_insufficient_profiles_error(self, cg_centerline):
        """Should raise error if hull has too few profiles."""
        hull = KayakHull()
        profile = Profile(station=0.0, points=[Point3D(0, -0.5, -0.5), Point3D(0, 0.5, -0.5)])
        hull.add_profile(profile)

        with pytest.raises(ValueError, match="at least 2 profiles"):
            StabilityAnalyzer(hull, cg_centerline)

    def test_repr(self, simple_box_hull, cg_centerline):
        """Test string representation."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)
        repr_str = repr(analyzer)

        assert "StabilityAnalyzer" in repr_str
        assert "hull=KayakHull" in repr_str
        assert "cg=CenterOfGravity" in repr_str


# ============================================================================
# Test Single Heel Angle Methods
# ============================================================================


class TestSingleHeelAngle:
    """Tests for single heel angle calculations."""

    def test_calculate_gz_at_angle(self, simple_box_hull, cg_centerline):
        """Test GZ calculation at specific angle."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        gz = analyzer.calculate_gz_at_angle(30.0)

        assert isinstance(gz, (float, np.floating))
        assert np.isfinite(gz)

    def test_calculate_righting_arm(self, simple_box_hull, cg_centerline):
        """Test full righting arm data retrieval."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        ra = analyzer.calculate_righting_arm(30.0)

        assert ra.heel_angle == 30.0
        assert np.isfinite(ra.gz)
        assert ra.cb is not None
        assert ra.waterline_z == -0.3

    def test_gz_at_different_angles(self, simple_box_hull, cg_centerline):
        """Test GZ calculation at multiple angles."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        angles = [0, 15, 30, 45, 60]
        gz_values = [analyzer.calculate_gz_at_angle(angle) for angle in angles]

        assert len(gz_values) == len(angles)
        assert all(np.isfinite(gz) for gz in gz_values)

        # GZ at 0° should be ~0 for symmetric hull with centerline CG
        assert abs(gz_values[0]) < 0.01

    def test_is_stable_at_angle(self, simple_box_hull, cg_centerline):
        """Test stability check at given angle."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        # At 0°, should be at equilibrium
        stable_0 = analyzer.is_stable_at_angle(0.0, threshold=-0.01)
        assert stable_0

        # Check various angles
        for angle in [10, 20, 30, 40, 50]:
            stable = analyzer.is_stable_at_angle(angle)
            # Just verify it returns a boolean
            assert isinstance(stable, (bool, np.bool_))


# ============================================================================
# Test Stability Curve Generation
# ============================================================================


class TestCurveGeneration:
    """Tests for stability curve generation."""

    def test_generate_default_curve(self, simple_box_hull, cg_centerline):
        """Test default stability curve generation."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        curve = analyzer.generate_stability_curve()

        assert isinstance(curve, StabilityCurve)
        assert len(curve.heel_angles) > 0
        assert len(curve.gz_values) == len(curve.heel_angles)
        assert curve.heel_angles[0] == 0.0
        assert curve.heel_angles[-1] == 90.0

    def test_generate_curve_with_range(self, simple_box_hull, cg_centerline):
        """Test curve generation with custom range."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        curve = analyzer.generate_stability_curve(min_angle=0, max_angle=60, angle_step=10)

        assert curve.heel_angles[0] == 0.0
        assert curve.heel_angles[-1] == 60.0
        assert len(curve.heel_angles) == 7  # 0, 10, 20, 30, 40, 50, 60

    def test_generate_curve_with_specific_angles(self, simple_box_hull, cg_centerline):
        """Test curve generation with specific angles."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        angles = np.array([0, 15, 30, 45, 60, 75, 90])
        curve = analyzer.generate_stability_curve(heel_angles=angles)

        assert_allclose(curve.heel_angles, angles)

    def test_curve_properties(self, simple_box_hull, cg_centerline):
        """Test that generated curve has expected properties."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        curve = analyzer.generate_stability_curve()

        # Should have max GZ
        assert curve.max_gz > 0 or curve.max_gz < 0  # Just verify it's a number
        assert np.isfinite(curve.angle_of_max_gz)

        # Should have range of positive stability (even if NaN)
        min_angle, max_angle = curve.range_of_positive_stability
        assert isinstance(min_angle, (float, np.floating))
        assert isinstance(max_angle, (float, np.floating))


# ============================================================================
# Test Stability Analysis
# ============================================================================


class TestStabilityAnalysis:
    """Tests for stability metrics analysis."""

    def test_analyze_stability_with_curve(self, simple_box_hull, cg_centerline):
        """Test analysis with provided curve."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)
        curve = analyzer.generate_stability_curve()

        metrics = analyzer.analyze_stability(curve)

        assert isinstance(metrics, StabilityMetrics)
        assert np.isfinite(metrics.max_gz)
        assert np.isfinite(metrics.angle_of_max_gz)

    def test_analyze_stability_without_curve(self, simple_box_hull, cg_centerline):
        """Test analysis without provided curve (auto-generates)."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        metrics = analyzer.analyze_stability()

        assert isinstance(metrics, StabilityMetrics)
        assert np.isfinite(metrics.max_gz)

    def test_analyze_with_gm_estimate(self, simple_box_hull, cg_centerline):
        """Test analysis with GM estimation."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        metrics = analyzer.analyze_stability(estimate_gm=True)

        # GM may be positive or negative depending on configuration
        if metrics.gm_estimate is not None:
            assert np.isfinite(metrics.gm_estimate)

    def test_analyze_with_area_calculation(self, simple_box_hull, cg_centerline):
        """Test analysis with area under curve."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        metrics = analyzer.analyze_stability(calculate_area=True)

        if metrics.area_under_curve is not None:
            assert metrics.area_under_curve >= 0


# ============================================================================
# Test Convenience Methods
# ============================================================================


class TestConvenienceMethods:
    """Tests for convenience methods."""

    def test_get_stability_summary(self, simple_box_hull, cg_centerline):
        """Test comprehensive stability summary."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        summary = analyzer.get_stability_summary()

        assert isinstance(summary, dict)
        assert "curve" in summary
        assert "metrics" in summary
        assert "max_gz" in summary
        assert "angle_of_max_gz" in summary
        assert "gm" in summary
        assert "range_positive" in summary
        assert "vanishing_angle" in summary
        assert "dynamic_stability" in summary

        # Verify types
        assert isinstance(summary["curve"], StabilityCurve)
        assert isinstance(summary["metrics"], StabilityMetrics)
        assert isinstance(summary["max_gz"], (float, np.floating))

    def test_find_maximum_gz(self, simple_box_hull, cg_centerline):
        """Test finding maximum GZ."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        max_gz, angle = analyzer.find_maximum_gz()

        assert np.isfinite(max_gz)
        assert np.isfinite(angle)
        assert 0 <= angle <= 90

    def test_find_vanishing_stability_angle(self, simple_box_hull, cg_centerline):
        """Test finding vanishing stability angle."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        vanishing = analyzer.find_vanishing_stability_angle()

        assert np.isfinite(vanishing) or np.isnan(vanishing)
        if np.isfinite(vanishing):
            assert 0 <= vanishing <= 180

    def test_estimate_metacentric_height(self, simple_box_hull, cg_centerline):
        """Test GM estimation."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        gm = analyzer.estimate_metacentric_height()

        # GM may be None if cannot be estimated
        if gm is not None:
            assert np.isfinite(gm)

    def test_calculate_dynamic_stability(self, simple_box_hull, cg_centerline):
        """Test dynamic stability calculation."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        area = analyzer.calculate_dynamic_stability()

        if area is not None:
            assert area >= 0


# ============================================================================
# Test Comparison Methods
# ============================================================================


class TestComparisonMethods:
    """Tests for comparison methods."""

    def test_compare_with_different_cg(self, simple_box_hull):
        """Test comparison with different CG positions."""
        # Create analyzer with base CG
        cg_base = CenterOfGravity(lcg=2.0, vcg=-0.35, tcg=0.0, total_mass=100.0)
        analyzer = StabilityAnalyzer(simple_box_hull, cg_base, -0.3)

        # Create different CG positions
        cg_low = CenterOfGravity(lcg=2.0, vcg=-0.45, tcg=0.0, total_mass=100.0)
        cg_high = CenterOfGravity(lcg=2.0, vcg=-0.25, tcg=0.0, total_mass=100.0)

        results = analyzer.compare_with_different_cg(
            [cg_low, cg_high], labels=["Low CG", "High CG"]
        )

        assert len(results) == 2

        for label, curve, metrics in results:
            assert isinstance(label, str)
            assert isinstance(curve, StabilityCurve)
            assert isinstance(metrics, StabilityMetrics)

    def test_compare_without_labels(self, simple_box_hull):
        """Test comparison without custom labels."""
        cg_base = CenterOfGravity(lcg=2.0, vcg=-0.35, tcg=0.0, total_mass=100.0)
        analyzer = StabilityAnalyzer(simple_box_hull, cg_base, -0.3)

        cg1 = CenterOfGravity(lcg=2.0, vcg=-0.4, tcg=0.0, total_mass=100.0)
        cg2 = CenterOfGravity(lcg=2.0, vcg=-0.3, tcg=0.0, total_mass=100.0)

        results = analyzer.compare_with_different_cg([cg1, cg2])

        # Should use default labels CG1, CG2
        assert results[0][0] == "CG1"
        assert results[1][0] == "CG2"

    def test_compare_with_different_waterlines(self, simple_box_hull, cg_centerline):
        """Test comparison with different waterlines."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        waterlines = [-0.4, -0.3, -0.2]
        labels = ["Light", "Medium", "Heavy"]

        results = analyzer.compare_with_different_waterlines(waterlines, labels)

        assert len(results) == 3

        for i, (label, curve, metrics) in enumerate(results):
            assert label == labels[i]
            assert isinstance(curve, StabilityCurve)
            assert isinstance(metrics, StabilityMetrics)
            assert curve.waterline_z == waterlines[i]

    def test_compare_waterlines_without_labels(self, simple_box_hull, cg_centerline):
        """Test waterline comparison without custom labels."""
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        waterlines = [-0.4, -0.3, -0.2]
        results = analyzer.compare_with_different_waterlines(waterlines)

        # Should use default labels WL1, WL2, WL3
        assert results[0][0] == "WL1"
        assert results[1][0] == "WL2"
        assert results[2][0] == "WL3"


# ============================================================================
# Test Quick Analysis Function
# ============================================================================


class TestQuickAnalysis:
    """Tests for quick_stability_analysis convenience function."""

    def test_quick_analysis(self, simple_box_hull, cg_centerline):
        """Test quick stability analysis function."""
        summary = quick_stability_analysis(hull=simple_box_hull, cg=cg_centerline, waterline_z=-0.3)

        assert isinstance(summary, dict)
        assert "curve" in summary
        assert "metrics" in summary
        assert "max_gz" in summary

        # Verify it produces the same results as creating an analyzer
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)
        analyzer_summary = analyzer.get_stability_summary()

        assert summary["max_gz"] == analyzer_summary["max_gz"]
        assert summary["angle_of_max_gz"] == analyzer_summary["angle_of_max_gz"]


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_analysis_workflow(self, simple_box_hull, cg_centerline):
        """Test a complete analysis workflow."""
        # Create analyzer
        analyzer = StabilityAnalyzer(simple_box_hull, cg_centerline, -0.3)

        # Generate curve
        curve = analyzer.generate_stability_curve()
        assert len(curve.heel_angles) > 0

        # Analyze
        metrics = analyzer.analyze_stability(curve)
        assert metrics.max_gz is not None

        # Get summary
        summary = analyzer.get_stability_summary()
        assert "max_gz" in summary

        # Find key values
        max_gz, angle = analyzer.find_maximum_gz()
        assert max_gz == metrics.max_gz
        assert angle == metrics.angle_of_max_gz

    def test_comparison_workflow(self, simple_box_hull):
        """Test comparison workflow."""
        cg = CenterOfGravity(lcg=2.0, vcg=-0.35, tcg=0.0, total_mass=100.0)
        analyzer = StabilityAnalyzer(simple_box_hull, cg, -0.3)

        # Compare different CGs
        cg_list = [
            CenterOfGravity(lcg=2.0, vcg=-0.45, tcg=0.0, total_mass=100.0),
            CenterOfGravity(lcg=2.0, vcg=-0.35, tcg=0.0, total_mass=100.0),
            CenterOfGravity(lcg=2.0, vcg=-0.25, tcg=0.0, total_mass=100.0),
        ]

        results = analyzer.compare_with_different_cg(cg_list, labels=["Low", "Mid", "High"])

        assert len(results) == 3

        # Verify we can extract max GZ from each
        max_gz_values = [metrics.max_gz for _, _, metrics in results]
        assert all(np.isfinite(gz) for gz in max_gz_values)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
