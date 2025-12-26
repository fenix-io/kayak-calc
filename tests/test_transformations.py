"""
Unit tests for coordinate transformation functions.
"""

import pytest
import numpy as np
from src.geometry.point import Point3D
from src.geometry.profile import Profile
from src.geometry.hull import KayakHull
from src.geometry.transformations import (
    apply_heel,
    apply_heel_to_profile,
    apply_heel_to_hull,
    apply_trim,
    apply_trim_to_profile,
    apply_trim_to_hull,
    apply_heel_and_trim,
    apply_heel_and_trim_to_hull,
    Waterline,
    find_waterline_intersection_segment,
    find_profile_waterline_intersection,
    get_submerged_points,
    calculate_submerged_area,
    calculate_waterplane_area,
    transform_to_body_coordinates,
    transform_to_earth_coordinates,
)


class TestHeelTransformations:
    """Tests for heel angle transformations."""

    def test_apply_heel_no_rotation(self):
        """Test that 0° heel leaves point unchanged."""
        point = Point3D(1.0, 0.5, 0.1)
        heeled = apply_heel(point, 0.0)

        assert heeled.x == pytest.approx(point.x)
        assert heeled.y == pytest.approx(point.y)
        assert heeled.z == pytest.approx(point.z)

    def test_apply_heel_90_degrees(self):
        """Test 90° heel transformation."""
        point = Point3D(1.0, 0.0, 1.0)
        heeled = apply_heel(point, 90.0)

        assert heeled.x == pytest.approx(1.0)
        # 90° starboard down: z rotates to -y direction
        assert heeled.y == pytest.approx(-1.0, abs=1e-10)
        assert heeled.z == pytest.approx(0.0, abs=1e-10)

    def test_apply_heel_with_reference(self):
        """Test heel with custom reference point."""
        point = Point3D(2.0, 1.0, 0.5)
        reference = Point3D(2.0, 0.0, 0.0)

        heeled = apply_heel(point, 90.0, reference)

        # After rotating 90° about (2, 0, 0), point (2, 1, 0.5)
        # relative position (0, 1, 0.5) becomes (0, -0.5, 1)
        assert heeled.x == pytest.approx(2.0)
        assert heeled.y == pytest.approx(-0.5, abs=1e-10)
        assert heeled.z == pytest.approx(1.0, abs=1e-10)

    def test_apply_heel_to_profile(self):
        """Test heeling entire profile."""
        points = [Point3D(1.0, -0.5, 0.1), Point3D(1.0, 0.0, 0.0), Point3D(1.0, 0.5, 0.1)]
        profile = Profile(1.0, points)

        heeled = apply_heel_to_profile(profile, 30.0)

        assert heeled.station == 1.0
        assert len(heeled) == 3
        # Check that transformation was applied
        assert not all(
            p1.y == pytest.approx(p2.y) and p1.z == pytest.approx(p2.z)
            for p1, p2 in zip(profile.points, heeled.points)
        )

    def test_apply_heel_to_hull(self):
        """Test heeling entire hull."""
        hull = KayakHull()

        points1 = [Point3D(0.0, -0.5, 0.1), Point3D(0.0, 0.5, 0.1)]
        points2 = [Point3D(1.0, -0.5, 0.1), Point3D(1.0, 0.5, 0.1)]

        hull.add_profile(Profile(0.0, points1))
        hull.add_profile(Profile(1.0, points2))

        heeled_hull = apply_heel_to_hull(hull, 20.0)

        assert heeled_hull.num_profiles == 2
        assert 0.0 in heeled_hull.profiles
        assert 1.0 in heeled_hull.profiles


class TestTrimTransformations:
    """Tests for trim angle transformations."""

    def test_apply_trim_no_rotation(self):
        """Test that 0° trim leaves point unchanged."""
        point = Point3D(2.0, 0.5, 0.1)
        trimmed = apply_trim(point, 0.0)

        assert trimmed.x == pytest.approx(point.x)
        assert trimmed.y == pytest.approx(point.y)
        assert trimmed.z == pytest.approx(point.z)

    def test_apply_trim_90_degrees(self):
        """Test 90° trim transformation."""
        point = Point3D(1.0, 0.0, 0.0)
        trimmed = apply_trim(point, 90.0)

        assert trimmed.x == pytest.approx(0.0, abs=1e-10)
        assert trimmed.y == pytest.approx(0.0)
        assert trimmed.z == pytest.approx(-1.0, abs=1e-10)

    def test_apply_trim_to_profile(self):
        """Test trimming entire profile."""
        points = [Point3D(2.0, -0.5, 0.1), Point3D(2.0, 0.0, 0.0), Point3D(2.0, 0.5, 0.1)]
        profile = Profile(2.0, points)

        trimmed = apply_trim_to_profile(profile, 10.0)

        # Station should change with trim
        assert trimmed.station != pytest.approx(2.0)
        assert len(trimmed) == 3

    def test_apply_trim_to_hull(self):
        """Test trimming entire hull."""
        hull = KayakHull()

        points1 = [Point3D(0.0, -0.5, 0.1), Point3D(0.0, 0.5, 0.1)]
        points2 = [Point3D(2.0, -0.5, 0.1), Point3D(2.0, 0.5, 0.1)]

        hull.add_profile(Profile(0.0, points1))
        hull.add_profile(Profile(2.0, points2))

        trimmed_hull = apply_trim_to_hull(hull, 5.0)

        assert trimmed_hull.num_profiles == 2


class TestCombinedTransformations:
    """Tests for combined heel and trim transformations."""

    def test_heel_and_trim_heel_first(self):
        """Test combined transformation with heel first."""
        point = Point3D(2.0, 1.0, 0.5)

        result = apply_heel_and_trim(point, 30.0, 10.0, order="heel_first")

        # Should be different from original
        assert not (
            result.x == pytest.approx(point.x)
            and result.y == pytest.approx(point.y)
            and result.z == pytest.approx(point.z)
        )

    def test_heel_and_trim_trim_first(self):
        """Test combined transformation with trim first."""
        point = Point3D(2.0, 1.0, 0.5)

        result = apply_heel_and_trim(point, 30.0, 10.0, order="trim_first")

        # Should be different from original
        assert not (
            result.x == pytest.approx(point.x)
            and result.y == pytest.approx(point.y)
            and result.z == pytest.approx(point.z)
        )

    def test_heel_and_trim_order_matters(self):
        """Test that order of rotations matters."""
        point = Point3D(2.0, 1.0, 0.5)

        result1 = apply_heel_and_trim(point, 30.0, 10.0, order="heel_first")
        result2 = apply_heel_and_trim(point, 30.0, 10.0, order="trim_first")

        # Results should be different (non-commutative)
        assert not (
            result1.x == pytest.approx(result2.x)
            and result1.y == pytest.approx(result2.y)
            and result1.z == pytest.approx(result2.z)
        )

    def test_invalid_order_raises_error(self):
        """Test that invalid order raises error."""
        point = Point3D(2.0, 1.0, 0.5)

        with pytest.raises(ValueError, match="Invalid order"):
            apply_heel_and_trim(point, 30.0, 10.0, order="invalid")

    def test_heel_and_trim_to_hull(self):
        """Test combined transformation on hull."""
        hull = KayakHull()

        points = [Point3D(1.0, -0.5, 0.1), Point3D(1.0, 0.5, 0.1)]
        hull.add_profile(Profile(1.0, points))

        result = apply_heel_and_trim_to_hull(hull, 20.0, 5.0)

        assert result.num_profiles == 1


class TestWaterline:
    """Tests for Waterline class."""

    def test_horizontal_waterline(self):
        """Test horizontal waterline at z=0."""
        wl = Waterline(z_reference=0.0, heel_angle=0.0, trim_angle=0.0)

        # Normal should be vertical
        assert wl.a == pytest.approx(0.0)
        assert wl.b == pytest.approx(0.0)
        assert wl.c == pytest.approx(1.0)

        # Z at any (x, y) should be 0
        assert wl.z_at_point(0, 0) == pytest.approx(0.0)
        assert wl.z_at_point(1, 1) == pytest.approx(0.0)

    def test_waterline_with_heel(self):
        """Test waterline inclined by heel."""
        wl = Waterline(z_reference=0.0, heel_angle=10.0, trim_angle=0.0)

        # Normal should be inclined
        assert abs(wl.b) > 1e-6  # Should have y-component

        # Z should vary with y
        z1 = wl.z_at_point(0, -1)
        z2 = wl.z_at_point(0, 1)
        assert abs(z1 - z2) > 1e-6

    def test_waterline_with_trim(self):
        """Test waterline inclined by trim."""
        wl = Waterline(z_reference=0.0, heel_angle=0.0, trim_angle=5.0)

        # Normal should be inclined
        assert abs(wl.a) > 1e-6  # Should have x-component

        # Z should vary with x
        z1 = wl.z_at_point(-1, 0)
        z2 = wl.z_at_point(1, 0)
        assert abs(z1 - z2) > 1e-6

    def test_is_below_waterline(self):
        """Test checking if point is submerged."""
        wl = Waterline(z_reference=0.0)

        assert wl.is_below_waterline(Point3D(0, 0, -1))  # Below
        assert not wl.is_below_waterline(Point3D(0, 0, 1))  # Above
        assert wl.is_below_waterline(Point3D(0, 0, 0))  # On waterline

    def test_signed_distance(self):
        """Test signed distance calculation."""
        wl = Waterline(z_reference=0.0)

        # Point below waterline
        dist = wl.signed_distance(Point3D(0, 0, -1))
        assert dist < 0

        # Point above waterline
        dist = wl.signed_distance(Point3D(0, 0, 1))
        assert dist > 0

        # Point on waterline
        dist = wl.signed_distance(Point3D(0, 0, 0))
        assert abs(dist) < 1e-10


class TestWaterlineIntersections:
    """Tests for waterline intersection calculations."""

    def test_segment_crossing_waterline(self):
        """Test segment that crosses waterline."""
        p1 = Point3D(0, 0, -1)  # Below
        p2 = Point3D(0, 0, 1)  # Above
        wl = Waterline(z_reference=0.0)

        intersection = find_waterline_intersection_segment(p1, p2, wl)

        assert intersection is not None
        assert intersection.z == pytest.approx(0.0)

    def test_segment_not_crossing_waterline(self):
        """Test segment that doesn't cross waterline."""
        p1 = Point3D(0, 0, 1)  # Above
        p2 = Point3D(0, 0, 2)  # Above
        wl = Waterline(z_reference=0.0)

        intersection = find_waterline_intersection_segment(p1, p2, wl)

        assert intersection is None

    def test_segment_on_waterline(self):
        """Test segment on waterline."""
        p1 = Point3D(0, -1, 0)  # On waterline
        p2 = Point3D(0, 1, 0)  # On waterline
        wl = Waterline(z_reference=0.0)

        intersection = find_waterline_intersection_segment(p1, p2, wl)

        # Should return midpoint
        assert intersection is not None
        assert intersection.z == pytest.approx(0.0)

    def test_profile_waterline_intersection(self):
        """Test finding profile intersections with waterline."""
        points = [
            Point3D(1.0, -0.5, -0.2),  # Below
            Point3D(1.0, 0.0, -0.5),  # Below
            Point3D(1.0, 0.5, -0.2),  # Below
        ]
        profile = Profile(1.0, points)
        wl = Waterline(z_reference=0.0)

        # All points below - no intersection
        intersections = find_profile_waterline_intersection(profile, wl)
        assert len(intersections) == 0

        # Add points above waterline
        points_mixed = [
            Point3D(1.0, -0.5, 0.2),  # Above
            Point3D(1.0, -0.25, -0.1),  # Below
            Point3D(1.0, 0.0, -0.2),  # Below
            Point3D(1.0, 0.25, -0.1),  # Below
            Point3D(1.0, 0.5, 0.2),  # Above
        ]
        profile2 = Profile(1.0, points_mixed)

        intersections2 = find_profile_waterline_intersection(profile2, wl)
        # Should find 2 intersections (port and starboard)
        assert len(intersections2) >= 2


class TestSubmergedCalculations:
    """Tests for submerged area and point calculations."""

    def test_get_submerged_points(self):
        """Test getting submerged portion of profile."""
        points = [
            Point3D(1.0, -0.5, 0.1),  # Above
            Point3D(1.0, 0.0, -0.2),  # Below
            Point3D(1.0, 0.5, 0.1),  # Above
        ]
        profile = Profile(1.0, points)
        wl = Waterline(z_reference=0.0)

        submerged = get_submerged_points(profile, wl)

        # Should include the one point below plus intersections
        assert len(submerged) >= 1

    def test_calculate_submerged_area(self):
        """Test calculating submerged cross-sectional area."""
        # Create a simple rectangular profile
        points = [
            Point3D(1.0, -0.5, -0.5),
            Point3D(1.0, -0.5, 0.5),
            Point3D(1.0, 0.5, 0.5),
            Point3D(1.0, 0.5, -0.5),
        ]
        profile = Profile(1.0, points)
        wl = Waterline(z_reference=0.0)

        # Half submerged - area should be ~0.5
        area = calculate_submerged_area(profile, wl)
        assert area == pytest.approx(0.5, abs=0.1)

    def test_calculate_submerged_area_fully_submerged(self):
        """Test area calculation when fully submerged."""
        # Rectangle 1.0 x 1.0
        points = [
            Point3D(1.0, -0.5, -0.5),
            Point3D(1.0, -0.5, 0.0),
            Point3D(1.0, 0.5, 0.0),
            Point3D(1.0, 0.5, -0.5),
        ]
        profile = Profile(1.0, points)
        wl = Waterline(z_reference=0.5)  # Above profile

        # Fully submerged - area should be ~0.5
        area = calculate_submerged_area(profile, wl)
        assert area == pytest.approx(0.5, abs=0.1)

    def test_calculate_submerged_area_not_submerged(self):
        """Test area calculation when not submerged."""
        points = [Point3D(1.0, -0.5, 0.5), Point3D(1.0, 0.5, 0.5)]
        profile = Profile(1.0, points)
        wl = Waterline(z_reference=0.0)

        # Not submerged
        area = calculate_submerged_area(profile, wl)
        assert area == pytest.approx(0.0)


class TestWaterplaneArea:
    """Tests for waterplane area calculations."""

    def test_waterplane_area_simple_hull(self):
        """Test waterplane area for simple rectangular hull."""
        hull = KayakHull()

        # Create rectangular cross-sections at two stations
        for x in [0.0, 1.0]:
            points = [
                Point3D(x, -0.5, -0.5),
                Point3D(x, -0.5, 0.5),
                Point3D(x, 0.5, 0.5),
                Point3D(x, 0.5, -0.5),
            ]
            hull.add_profile(Profile(x, points))

        wl = Waterline(z_reference=0.0)

        # At z=0, width is 1.0, length is 1.0, so area should be ~1.0
        area = calculate_waterplane_area(hull, wl, num_stations=10)
        assert area == pytest.approx(1.0, abs=0.2)


class TestCoordinateConversions:
    """Tests for coordinate system conversions."""

    def test_body_to_earth_and_back(self):
        """Test round-trip conversion."""
        point_body = Point3D(2.0, 1.0, 0.5)
        orientation = (15.0, 5.0, 10.0)  # heel, trim, yaw

        # Convert to earth coordinates
        point_earth = transform_to_earth_coordinates(point_body, orientation)

        # Convert back to body coordinates
        point_body_back = transform_to_body_coordinates(point_earth, orientation)

        # Should match original
        assert point_body_back.x == pytest.approx(point_body.x)
        assert point_body_back.y == pytest.approx(point_body.y)
        assert point_body_back.z == pytest.approx(point_body.z)

    def test_no_rotation(self):
        """Test conversion with no rotation."""
        point = Point3D(1.0, 2.0, 3.0)
        orientation = (0.0, 0.0, 0.0)

        earth = transform_to_earth_coordinates(point, orientation)

        assert earth.x == pytest.approx(point.x)
        assert earth.y == pytest.approx(point.y)
        assert earth.z == pytest.approx(point.z)


class TestEdgeCases:
    """Tests for edge cases and special conditions."""

    def test_heel_360_degrees(self):
        """Test that 360° rotation returns to original."""
        point = Point3D(1.0, 0.5, 0.3)
        heeled = apply_heel(point, 360.0)

        assert heeled.x == pytest.approx(point.x)
        assert heeled.y == pytest.approx(point.y)
        assert heeled.z == pytest.approx(point.z)

    def test_negative_heel_angle(self):
        """Test negative heel angle (port side down)."""
        point = Point3D(1.0, 0.0, 1.0)
        heeled = apply_heel(point, -90.0)

        assert heeled.x == pytest.approx(1.0)
        # -90° port down: z rotates to +y direction
        assert heeled.y == pytest.approx(1.0, abs=1e-10)
        assert heeled.z == pytest.approx(0.0, abs=1e-10)

    def test_waterline_at_different_levels(self):
        """Test waterline at non-zero reference."""
        wl = Waterline(z_reference=0.5)

        assert wl.is_below_waterline(Point3D(0, 0, 0))  # Below
        assert not wl.is_below_waterline(Point3D(0, 0, 1))  # Above


class TestRotationMatrixProperties:
    """Tests for rotation matrix mathematical properties."""

    def test_rotation_preserves_distance(self):
        """Test that rotation preserves distance from origin."""
        point = Point3D(1.0, 2.0, 3.0)
        original_dist = np.sqrt(point.x**2 + point.y**2 + point.z**2)

        # Apply various heel angles
        for angle in [30, 45, 60, 90, 120, 180]:
            heeled = apply_heel(point, angle)
            heeled_dist = np.sqrt(heeled.x**2 + heeled.y**2 + heeled.z**2)
            assert heeled_dist == pytest.approx(original_dist, rel=1e-10)

    def test_rotation_preserves_x_coordinate(self):
        """Test that heel rotation doesn't change x-coordinate."""
        point = Point3D(1.0, 2.0, 3.0)

        for angle in [0, 15, 30, 45, 60, 75, 90]:
            heeled = apply_heel(point, angle)
            assert heeled.x == pytest.approx(point.x, abs=1e-10)

    def test_inverse_rotation(self):
        """Test that positive and negative rotations are inverses."""
        point = Point3D(1.0, 2.0, 3.0)

        for angle in [30, 45, 60, 90]:
            # Apply rotation
            rotated = apply_heel(point, angle)
            # Apply inverse rotation
            back = apply_heel(rotated, -angle)

            assert back.x == pytest.approx(point.x, abs=1e-10)
            assert back.y == pytest.approx(point.y, abs=1e-10)
            assert back.z == pytest.approx(point.z, abs=1e-10)

    def test_rotation_composition(self):
        """Test that rotating by A then B equals rotating by A+B."""
        point = Point3D(1.0, 2.0, 3.0)

        # Rotate by 30° then 45°
        step1 = apply_heel(point, 30)
        step2 = apply_heel(step1, 45)

        # Rotate directly by 75°
        direct = apply_heel(point, 75)

        assert step2.x == pytest.approx(direct.x, abs=1e-10)
        assert step2.y == pytest.approx(direct.y, abs=1e-10)
        assert step2.z == pytest.approx(direct.z, abs=1e-10)

    def test_360_degree_rotation_identity(self):
        """Test that 360° rotation returns to original position."""
        point = Point3D(1.5, 2.5, 3.5)
        rotated = apply_heel(point, 360)

        assert rotated.x == pytest.approx(point.x, abs=1e-10)
        assert rotated.y == pytest.approx(point.y, abs=1e-10)
        assert rotated.z == pytest.approx(point.z, abs=1e-10)

    def test_180_degree_rotation_symmetry(self):
        """Test that 180° rotation inverts y and z."""
        point = Point3D(1.0, 2.0, 3.0)
        rotated = apply_heel(point, 180)

        assert rotated.x == pytest.approx(point.x, abs=1e-10)
        assert rotated.y == pytest.approx(-point.y, abs=1e-10)
        assert rotated.z == pytest.approx(-point.z, abs=1e-10)

    def test_small_angle_approximation(self):
        """Test rotation for very small angles."""
        point = Point3D(1.0, 0.0, 1.0)

        # For small angles, rotation should be approximately linear
        angle_degrees = 0.01  # Very small angle
        heeled = apply_heel(point, angle_degrees)

        # Change should be proportional to angle
        dy = heeled.y - point.y
        dz = heeled.z - point.z

        # For small angle θ in radians: y_new ≈ y - z*θ, z_new ≈ z + y*θ
        angle_rad = np.deg2rad(angle_degrees)
        expected_dy = -point.z * angle_rad
        expected_dz = point.y * angle_rad

        assert dy == pytest.approx(expected_dy, abs=1e-6)
        assert dz == pytest.approx(expected_dz, abs=1e-6)


class TestWaterlineEdgeCases:
    """Additional edge cases for waterline calculations."""

    def test_waterline_at_exact_keel(self):
        """Test waterline positioned exactly at keel level."""
        points = [
            Point3D(0.0, -1.0, 0.0),
            Point3D(0.0, -1.0, -1.0),  # Keel
            Point3D(0.0, 1.0, -1.0),  # Keel
            Point3D(0.0, 1.0, 0.0),
        ]
        profile = Profile(0.0, points)

        # Waterline at keel
        waterline = Waterline(z_reference=-1.0)
        submerged = get_submerged_points(profile, waterline)

        # Should have minimal or no submerged area
        assert len(submerged) <= 2

    def test_waterline_at_exact_deck(self):
        """Test waterline positioned exactly at deck level."""
        points = [
            Point3D(0.0, -1.0, 0.0),  # Deck
            Point3D(0.0, -1.0, -1.0),
            Point3D(0.0, 1.0, -1.0),
            Point3D(0.0, 1.0, 0.0),  # Deck
        ]
        profile = Profile(0.0, points)

        # Waterline at deck
        waterline = Waterline(z_reference=0.0)
        submerged = get_submerged_points(profile, waterline)

        # Should include full profile
        assert len(submerged) >= 3

    def test_waterline_above_hull(self):
        """Test waterline positioned above entire hull."""
        points = [
            Point3D(0.0, -1.0, -0.5),
            Point3D(0.0, -1.0, -1.0),
            Point3D(0.0, 1.0, -1.0),
            Point3D(0.0, 1.0, -0.5),
        ]
        profile = Profile(0.0, points)

        # Waterline well above hull - all points are below waterline
        waterline = Waterline(z_reference=1.0)
        area = calculate_submerged_area(profile, waterline)

        # Should have full profile area (entire hull is submerged)
        # Area of rectangle: width=2.0, height=0.5
        expected_area = 2.0 * 0.5
        assert area == pytest.approx(expected_area, rel=1e-3)

    def test_waterline_below_hull(self):
        """Test waterline positioned below entire hull."""
        points = [
            Point3D(0.0, -1.0, 0.0),
            Point3D(0.0, -1.0, -1.0),
            Point3D(0.0, 1.0, -1.0),
            Point3D(0.0, 1.0, 0.0),
        ]
        profile = Profile(0.0, points)

        # Waterline well below hull
        waterline = Waterline(z_reference=-2.0)
        submerged = get_submerged_points(profile, waterline)

        # Should have no submerged points
        assert len(submerged) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
