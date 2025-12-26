"""
Unit tests for cross-section properties calculations.

Tests include:
- CrossSectionProperties class functionality
- Area and centroid calculations with analytical validation
- Heel angle effects
- Edge cases (fully submerged, fully emerged, etc.)
"""

import pytest
import numpy as np

from src.geometry import Point3D, Profile
from src.hydrostatics import (
    CrossSectionProperties,
    calculate_section_properties,
    calculate_properties_at_heel_angles,
    calculate_first_moment_of_area,
    validate_cross_section_properties,
    compare_properties,
)


class TestCrossSectionProperties:
    """Tests for CrossSectionProperties dataclass."""

    def test_initialization(self):
        """Test basic initialization of CrossSectionProperties."""
        props = CrossSectionProperties(
            area=1.5, centroid_y=0.0, centroid_z=-0.25, station=2.0, waterline_z=0.0, heel_angle=0.0
        )

        assert props.area == 1.5
        assert props.centroid_y == 0.0
        assert props.centroid_z == -0.25
        assert props.station == 2.0
        assert props.waterline_z == 0.0
        assert props.heel_angle == 0.0

    def test_centroid_property(self):
        """Test centroid property returns tuple."""
        props = CrossSectionProperties(
            area=1.0, centroid_y=0.5, centroid_z=-0.3, station=1.0, waterline_z=0.0
        )

        assert props.centroid == (0.5, -0.3)

    def test_is_valid(self):
        """Test is_valid method."""
        # Valid properties (area > 0, centroid below waterline)
        props_valid = CrossSectionProperties(
            area=1.0, centroid_y=0.0, centroid_z=-0.5, station=1.0, waterline_z=0.0
        )
        assert props_valid.is_valid()

        # Invalid: zero area
        props_zero = CrossSectionProperties(
            area=0.0, centroid_y=0.0, centroid_z=-0.5, station=1.0, waterline_z=0.0
        )
        assert not props_zero.is_valid()

        # Invalid: centroid above waterline
        props_above = CrossSectionProperties(
            area=1.0,
            centroid_y=0.0,
            centroid_z=0.5,  # Above waterline
            station=1.0,
            waterline_z=0.0,
        )
        assert not props_above.is_valid()

    def test_repr(self):
        """Test string representation."""
        props = CrossSectionProperties(
            area=1.234,
            centroid_y=0.567,
            centroid_z=-0.890,
            station=2.0,
            waterline_z=0.0,
            heel_angle=15.0,
        )

        repr_str = repr(props)
        assert "CrossSectionProperties" in repr_str
        assert "1.234" in repr_str
        assert "15.00°" in repr_str


class TestCalculateSectionProperties:
    """Tests for calculate_section_properties function."""

    def test_rectangular_profile_upright(self):
        """Test with rectangular profile (upright condition)."""
        # Create rectangular profile: 2m wide, 1m deep
        points = [
            Point3D(1.0, -1.0, 0.0),  # Port waterline
            Point3D(1.0, -1.0, -1.0),  # Port bottom
            Point3D(1.0, 1.0, -1.0),  # Starboard bottom
            Point3D(1.0, 1.0, 0.0),  # Starboard waterline
        ]
        profile = Profile(1.0, points)

        # Calculate properties
        props = calculate_section_properties(profile, waterline_z=0.0, heel_angle=0.0)

        # Check area: should be 2.0 * 1.0 = 2.0 m²
        assert np.isclose(props.area, 2.0, atol=0.01)

        # Check centroid: should be at (0, -0.5) for symmetric rectangle
        assert np.isclose(props.centroid_y, 0.0, atol=0.01)
        assert np.isclose(props.centroid_z, -0.5, atol=0.01)

        # Check other properties
        assert props.station == 1.0
        assert props.waterline_z == 0.0
        assert props.heel_angle == 0.0

    def test_triangular_profile_upright(self):
        """Test with triangular profile (V-shaped hull)."""
        # Create V-shaped profile: 2m wide at waterline, 1m deep
        points = [
            Point3D(1.0, -1.0, 0.0),  # Port waterline
            Point3D(1.0, 0.0, -1.0),  # Bottom (keel)
            Point3D(1.0, 1.0, 0.0),  # Starboard waterline
        ]
        profile = Profile(1.0, points)

        # Calculate properties
        props = calculate_section_properties(profile, waterline_z=0.0, heel_angle=0.0)

        # Check area: triangle = 0.5 * base * height = 0.5 * 2.0 * 1.0 = 1.0 m²
        assert np.isclose(props.area, 1.0, atol=0.01)

        # Check centroid: for triangle, centroid is at 1/3 height from bottom
        # So z_centroid should be at -1.0 + (1/3) * 1.0 = -0.333
        assert np.isclose(props.centroid_y, 0.0, atol=0.01)
        assert np.isclose(props.centroid_z, -1.0 / 3.0, atol=0.01)

    def test_trapezoid_profile_upright(self):
        """Test with trapezoidal profile."""
        # Create trapezoid: 2m at waterline, 1m at bottom, 1m deep
        points = [
            Point3D(1.0, -1.0, 0.0),  # Port waterline
            Point3D(1.0, -0.5, -1.0),  # Port bottom
            Point3D(1.0, 0.5, -1.0),  # Starboard bottom
            Point3D(1.0, 1.0, 0.0),  # Starboard waterline
        ]
        profile = Profile(1.0, points)

        # Calculate properties
        props = calculate_section_properties(profile, waterline_z=0.0, heel_angle=0.0)

        # Trapezoid area = 0.5 * (b1 + b2) * h = 0.5 * (2.0 + 1.0) * 1.0 = 1.5 m²
        assert np.isclose(props.area, 1.5, atol=0.01)

        # Centroid should be on centerline
        assert np.isclose(props.centroid_y, 0.0, atol=0.01)

        # Trapezoid centroid height: h/3 * (2*b1 + b2)/(b1 + b2)
        # = 1.0/3 * (2*2.0 + 1.0)/(2.0 + 1.0) = 1.0/3 * 5.0/3.0 = 5/9 from bottom
        # So z = -1.0 + 5/9 = -4/9 ≈ -0.444
        expected_z = -1.0 + (1.0 / 3.0) * (2 * 2.0 + 1.0) / (2.0 + 1.0)
        assert np.isclose(props.centroid_z, expected_z, atol=0.02)

    def test_profile_above_waterline(self):
        """Test with profile entirely above waterline."""
        points = [
            Point3D(1.0, -0.5, 0.5),  # All points above waterline
            Point3D(1.0, 0.0, 0.3),
            Point3D(1.0, 0.5, 0.5),
        ]
        profile = Profile(1.0, points)

        # Calculate properties
        props = calculate_section_properties(profile, waterline_z=0.0, heel_angle=0.0)

        # Area should be zero (nothing submerged)
        assert props.area == 0.0

    def test_profile_with_heel_angle(self):
        """Test calculation with heel angle applied."""
        # Create rectangular profile
        points = [
            Point3D(1.0, -1.0, 0.0),
            Point3D(1.0, -1.0, -1.0),
            Point3D(1.0, 1.0, -1.0),
            Point3D(1.0, 1.0, 0.0),
        ]
        profile = Profile(1.0, points)

        # Calculate at 30 degrees heel
        props = calculate_section_properties(profile, waterline_z=0.0, heel_angle=30.0)

        # Area should still be positive
        assert props.area > 0

        # Heel angle should be recorded
        assert props.heel_angle == 30.0

        # For heeled condition, centroid_y should shift
        # (exact value depends on geometry, but should not be at centerline)
        # We just verify it's calculated
        assert np.isfinite(props.centroid_y)
        assert np.isfinite(props.centroid_z)

    def test_different_waterline_levels(self):
        """Test with different waterline levels."""
        # Create rectangular profile
        points = [
            Point3D(1.0, -1.0, 0.0),
            Point3D(1.0, -1.0, -2.0),
            Point3D(1.0, 1.0, -2.0),
            Point3D(1.0, 1.0, 0.0),
        ]
        profile = Profile(1.0, points)

        # Test at waterline z=0 (fully submerged)
        props_0 = calculate_section_properties(profile, waterline_z=0.0)
        assert np.isclose(props_0.area, 4.0, atol=0.01)  # 2m × 2m

        # Test at waterline z=-1 (half submerged)
        props_1 = calculate_section_properties(profile, waterline_z=-1.0)
        assert np.isclose(props_1.area, 2.0, atol=0.01)  # 2m × 1m

        # Test at waterline z=-2 (just touching bottom)
        props_2 = calculate_section_properties(profile, waterline_z=-2.0)
        assert props_2.area < 0.1  # Should be nearly zero


class TestCalculatePropertiesAtHeelAngles:
    """Tests for calculate_properties_at_heel_angles function."""

    def test_multiple_heel_angles(self):
        """Test calculation at multiple heel angles."""
        # Create rectangular profile
        points = [
            Point3D(1.0, -1.0, 0.0),
            Point3D(1.0, -1.0, -1.0),
            Point3D(1.0, 1.0, -1.0),
            Point3D(1.0, 1.0, 0.0),
        ]
        profile = Profile(1.0, points)

        # Calculate at multiple angles
        heel_angles = [0, 10, 20, 30]
        properties_list = calculate_properties_at_heel_angles(profile, heel_angles)

        # Check we get one result for each angle
        assert len(properties_list) == len(heel_angles)

        # Check heel angles are correct
        for props, expected_angle in zip(properties_list, heel_angles):
            assert props.heel_angle == expected_angle

        # All should have positive area
        for props in properties_list:
            assert props.area > 0

    def test_results_order(self):
        """Test that results are in same order as input angles."""
        points = [
            Point3D(1.0, -0.5, 0.0),
            Point3D(1.0, 0.0, -0.5),
            Point3D(1.0, 0.5, 0.0),
        ]
        profile = Profile(1.0, points)

        heel_angles = [45, 0, 30, 15]
        properties_list = calculate_properties_at_heel_angles(profile, heel_angles)

        # Verify order matches
        for props, expected_angle in zip(properties_list, heel_angles):
            assert props.heel_angle == expected_angle


class TestCalculateFirstMomentOfArea:
    """Tests for calculate_first_moment_of_area function."""

    def test_first_moment_about_y_axis(self):
        """Test first moment calculation about y-axis."""
        # Rectangular profile
        points = [
            Point3D(1.0, -1.0, 0.0),
            Point3D(1.0, -1.0, -1.0),
            Point3D(1.0, 1.0, -1.0),
            Point3D(1.0, 1.0, 0.0),
        ]
        profile = Profile(1.0, points)

        # First moment about y-axis = Area × z_centroid
        q_y = calculate_first_moment_of_area(profile, waterline_z=0.0, axis="y")

        # Expected: area = 2.0, centroid_z = -0.5, so Q_y = 2.0 × (-0.5) = -1.0
        assert np.isclose(q_y, -1.0, atol=0.01)

    def test_first_moment_about_z_axis(self):
        """Test first moment calculation about z-axis."""
        # Rectangular profile (symmetric about centerline)
        points = [
            Point3D(1.0, -1.0, 0.0),
            Point3D(1.0, -1.0, -1.0),
            Point3D(1.0, 1.0, -1.0),
            Point3D(1.0, 1.0, 0.0),
        ]
        profile = Profile(1.0, points)

        # First moment about z-axis = Area × y_centroid
        q_z = calculate_first_moment_of_area(profile, waterline_z=0.0, axis="z")

        # Expected: area = 2.0, centroid_y = 0.0 (symmetric), so Q_z = 0.0
        assert np.isclose(q_z, 0.0, atol=0.01)

    def test_invalid_axis(self):
        """Test that invalid axis raises error."""
        # Create a proper profile with area
        points = [
            Point3D(1.0, -0.5, 0.0),
            Point3D(1.0, 0.0, -0.5),
            Point3D(1.0, 0.5, 0.0),
        ]
        profile = Profile(1.0, points)

        with pytest.raises(ValueError):
            calculate_first_moment_of_area(profile, axis="x")


class TestValidateCrossSectionProperties:
    """Tests for validate_cross_section_properties function."""

    def test_valid_properties(self):
        """Test validation of correct properties."""
        props = CrossSectionProperties(
            area=1.0, centroid_y=0.0, centroid_z=-0.5, station=2.0, waterline_z=0.0, heel_angle=15.0
        )

        is_valid, issues = validate_cross_section_properties(props)
        assert is_valid
        assert len(issues) == 0

    def test_negative_area(self):
        """Test detection of negative area."""
        props = CrossSectionProperties(
            area=-1.0, centroid_y=0.0, centroid_z=-0.5, station=2.0, waterline_z=0.0  # Invalid
        )

        is_valid, issues = validate_cross_section_properties(props)
        assert not is_valid
        assert any("Negative area" in issue for issue in issues)

    def test_centroid_above_waterline(self):
        """Test detection of centroid above waterline."""
        props = CrossSectionProperties(
            area=1.0,
            centroid_y=0.0,
            centroid_z=0.5,  # Above waterline
            station=2.0,
            waterline_z=0.0,
        )

        is_valid, issues = validate_cross_section_properties(props)
        assert not is_valid
        assert any("above waterline" in issue for issue in issues)

    def test_non_finite_values(self):
        """Test detection of NaN/infinite values."""
        props = CrossSectionProperties(
            area=np.nan, centroid_y=0.0, centroid_z=-0.5, station=2.0, waterline_z=0.0
        )

        is_valid, issues = validate_cross_section_properties(props)
        assert not is_valid
        assert any("Non-finite" in issue for issue in issues)

    def test_extreme_heel_angle(self):
        """Test detection of extreme heel angles."""
        props = CrossSectionProperties(
            area=1.0,
            centroid_y=0.0,
            centroid_z=-0.5,
            station=2.0,
            waterline_z=0.0,
            heel_angle=120.0,  # Extreme
        )

        is_valid, issues = validate_cross_section_properties(props)
        assert not is_valid
        assert any("Heel angle" in issue for issue in issues)


class TestCompareProperties:
    """Tests for compare_properties function."""

    def test_identical_properties(self):
        """Test comparison of identical properties."""
        props1 = CrossSectionProperties(
            area=1.5, centroid_y=0.1, centroid_z=-0.3, station=2.0, waterline_z=0.0, heel_angle=10.0
        )

        props2 = CrossSectionProperties(
            area=1.5, centroid_y=0.1, centroid_z=-0.3, station=2.0, waterline_z=0.0, heel_angle=10.0
        )

        assert compare_properties(props1, props2)

    def test_different_properties(self):
        """Test comparison of different properties."""
        props1 = CrossSectionProperties(
            area=1.5, centroid_y=0.1, centroid_z=-0.3, station=2.0, waterline_z=0.0, heel_angle=10.0
        )

        props2 = CrossSectionProperties(
            area=1.6,  # Different
            centroid_y=0.1,
            centroid_z=-0.3,
            station=2.0,
            waterline_z=0.0,
            heel_angle=10.0,
        )

        assert not compare_properties(props1, props2)

    def test_comparison_with_tolerance(self):
        """Test comparison with numerical tolerance."""
        props1 = CrossSectionProperties(
            area=1.501,
            centroid_y=0.1,
            centroid_z=-0.3,
            station=2.0,
            waterline_z=0.0,
            heel_angle=10.0,
        )

        props2 = CrossSectionProperties(
            area=1.5, centroid_y=0.1, centroid_z=-0.3, station=2.0, waterline_z=0.0, heel_angle=10.0
        )

        # Should be equal within loose tolerance
        assert compare_properties(props1, props2, tolerance=0.01)

        # Should be different with tight tolerance
        assert not compare_properties(props1, props2, tolerance=1e-5)


class TestEdgeCases:
    """Tests for edge cases and special situations."""

    def test_zero_area_profile(self):
        """Test with profile that has zero submerged area."""
        # Single point above waterline
        points = [Point3D(1.0, 0.0, 1.0)]
        profile = Profile(1.0, points)

        props = calculate_section_properties(profile, waterline_z=0.0)
        assert props.area == 0.0

    def test_very_small_profile(self):
        """Test with very small profile dimensions."""
        points = [
            Point3D(1.0, -0.001, 0.0),
            Point3D(1.0, 0.0, -0.001),
            Point3D(1.0, 0.001, 0.0),
        ]
        profile = Profile(1.0, points)

        props = calculate_section_properties(profile, waterline_z=0.0)

        # Should still calculate (even if very small)
        assert props.area >= 0
        assert np.isfinite(props.centroid_y)
        assert np.isfinite(props.centroid_z)

    def test_large_heel_angle(self):
        """Test with large heel angles (near capsize)."""
        points = [
            Point3D(1.0, -1.0, 0.0),
            Point3D(1.0, -1.0, -1.0),
            Point3D(1.0, 1.0, -1.0),
            Point3D(1.0, 1.0, 0.0),
        ]
        profile = Profile(1.0, points)

        # Test at 80 degrees heel (nearly capsized)
        props = calculate_section_properties(profile, waterline_z=0.0, heel_angle=80.0)

        # Should still calculate something
        assert np.isfinite(props.area)
        assert props.heel_angle == 80.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
