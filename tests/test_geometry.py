"""
Unit tests for geometry module (Point3D and Profile classes).
"""

import pytest
import numpy as np
from src.geometry import Point3D, Profile


class TestPoint3D:
    """Tests for the Point3D class."""

    def test_initialization(self):
        """Test basic point initialization."""
        p = Point3D(1.0, 2.0, 3.0)
        assert p.x == 1.0
        assert p.y == 2.0
        assert p.z == 3.0

    def test_coordinates_property(self):
        """Test coordinates property returns numpy array."""
        p = Point3D(1.0, 2.0, 3.0)
        coords = p.coordinates
        assert isinstance(coords, np.ndarray)
        assert np.allclose(coords, [1.0, 2.0, 3.0])

    def test_distance_to(self):
        """Test distance calculation between two points."""
        p1 = Point3D(0.0, 0.0, 0.0)
        p2 = Point3D(3.0, 4.0, 0.0)
        assert np.isclose(p1.distance_to(p2), 5.0)

    def test_distance_to_origin(self):
        """Test distance calculation to origin."""
        p = Point3D(3.0, 4.0, 0.0)
        assert np.isclose(p.distance_to_origin(), 5.0)

    def test_translate(self):
        """Test point translation."""
        p = Point3D(1.0, 2.0, 3.0)
        p_translated = p.translate(dx=1.0, dy=-1.0, dz=2.0)
        assert p_translated.x == 2.0
        assert p_translated.y == 1.0
        assert p_translated.z == 5.0
        # Original point should be unchanged
        assert p.x == 1.0

    def test_rotate_x(self):
        """Test rotation around X-axis (heel)."""
        p = Point3D(0.0, 1.0, 0.0)
        p_rotated = p.rotate_x(90.0)  # 90 degrees (starboard down)
        assert np.isclose(p_rotated.x, 0.0)
        assert np.isclose(p_rotated.y, 0.0)
        assert np.isclose(p_rotated.z, -1.0)  # Point on port side goes down

    def test_rotate_y(self):
        """Test rotation around Y-axis."""
        p = Point3D(1.0, 0.0, 0.0)
        p_rotated = p.rotate_y(90.0)
        assert np.isclose(p_rotated.x, 0.0)
        assert np.isclose(p_rotated.y, 0.0)
        assert np.isclose(p_rotated.z, -1.0)

    def test_rotate_z(self):
        """Test rotation around Z-axis."""
        p = Point3D(1.0, 0.0, 0.0)
        p_rotated = p.rotate_z(90.0)
        assert np.isclose(p_rotated.x, 0.0)
        assert np.isclose(p_rotated.y, 1.0)
        assert np.isclose(p_rotated.z, 0.0)

    def test_scale(self):
        """Test point scaling."""
        p = Point3D(1.0, 2.0, 3.0)
        p_scaled = p.scale(sx=2.0, sy=0.5, sz=3.0)
        assert p_scaled.x == 2.0
        assert p_scaled.y == 1.0
        assert p_scaled.z == 9.0

    def test_equality(self):
        """Test point equality comparison."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(1.0, 2.0, 3.0)
        p3 = Point3D(1.0, 2.0, 3.1)
        assert p1 == p2
        assert p1 != p3

    def test_addition(self):
        """Test point addition (vector addition)."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(4.0, 5.0, 6.0)
        p3 = p1 + p2
        assert p3.x == 5.0
        assert p3.y == 7.0
        assert p3.z == 9.0

    def test_subtraction(self):
        """Test point subtraction (vector subtraction)."""
        p1 = Point3D(5.0, 7.0, 9.0)
        p2 = Point3D(1.0, 2.0, 3.0)
        p3 = p1 - p2
        assert p3.x == 4.0
        assert p3.y == 5.0
        assert p3.z == 6.0

    def test_multiplication(self):
        """Test point multiplication by scalar."""
        p = Point3D(1.0, 2.0, 3.0)
        p2 = p * 2.0
        assert p2.x == 2.0
        assert p2.y == 4.0
        assert p2.z == 6.0

        # Test right multiplication
        p3 = 3.0 * p
        assert p3.x == 3.0
        assert p3.y == 6.0
        assert p3.z == 9.0

    def test_division(self):
        """Test point division by scalar."""
        p = Point3D(2.0, 4.0, 6.0)
        p2 = p / 2.0
        assert p2.x == 1.0
        assert p2.y == 2.0
        assert p2.z == 3.0

        # Test division by zero
        with pytest.raises(ValueError):
            p / 0.0

    def test_dot_product(self):
        """Test dot product calculation."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = Point3D(4.0, 5.0, 6.0)
        dot = p1.dot(p2)
        assert dot == 1 * 4 + 2 * 5 + 3 * 6  # 32

    def test_cross_product(self):
        """Test cross product calculation."""
        p1 = Point3D(1.0, 0.0, 0.0)
        p2 = Point3D(0.0, 1.0, 0.0)
        p3 = p1.cross(p2)
        assert np.isclose(p3.x, 0.0)
        assert np.isclose(p3.y, 0.0)
        assert np.isclose(p3.z, 1.0)

    def test_copy(self):
        """Test point copying."""
        p1 = Point3D(1.0, 2.0, 3.0)
        p2 = p1.copy()
        assert p1 == p2
        assert p1 is not p2  # Different objects

    def test_repr(self):
        """Test string representation."""
        p = Point3D(1.0, 2.0, 3.0)
        repr_str = repr(p)
        assert "Point3D" in repr_str
        assert "1.0000" in repr_str


class TestProfile:
    """Tests for the Profile class."""

    def test_initialization(self):
        """Test basic profile initialization."""
        points = [Point3D(1.0, -0.5, 0.0), Point3D(1.0, 0.0, -0.2), Point3D(1.0, 0.5, 0.0)]
        profile = Profile(station=1.0, points=points)
        assert profile.station == 1.0
        assert profile.num_points == 3

    def test_validation(self):
        """Test that validation catches inconsistent x-coordinates."""
        points = [
            Point3D(1.0, -0.5, 0.0),
            Point3D(2.0, 0.0, -0.2),  # Wrong x-coordinate
            Point3D(1.0, 0.5, 0.0),
        ]
        with pytest.raises(ValueError):
            Profile(station=1.0, points=points)

    def test_add_point(self):
        """Test adding points to profile."""
        profile = Profile(station=1.0, points=[])
        profile.add_point(Point3D(1.0, 0.0, 0.0))
        assert profile.num_points == 1

        # Test adding point with wrong station
        with pytest.raises(ValueError):
            profile.add_point(Point3D(2.0, 0.0, 0.0))

    def test_sort_points(self):
        """Test sorting points in profile."""
        points = [Point3D(1.0, 0.5, 0.0), Point3D(1.0, -0.5, 0.0), Point3D(1.0, 0.0, -0.2)]
        profile = Profile(station=1.0, points=points)
        profile.sort_points(by="y")

        y_coords = profile.get_y_coordinates()
        assert np.all(y_coords[:-1] <= y_coords[1:])  # Check sorted

    def test_get_coordinates(self):
        """Test getting coordinate arrays."""
        points = [Point3D(1.0, -0.5, 0.0), Point3D(1.0, 0.0, -0.2), Point3D(1.0, 0.5, 0.0)]
        profile = Profile(station=1.0, points=points)

        y_coords = profile.get_y_coordinates()
        z_coords = profile.get_z_coordinates()

        assert len(y_coords) == 3
        assert len(z_coords) == 3
        assert np.allclose(y_coords, [-0.5, 0.0, 0.5])
        assert np.allclose(z_coords, [0.0, -0.2, 0.0])

    def test_interpolate_points(self):
        """Test point interpolation."""
        points = [Point3D(1.0, -1.0, 0.0), Point3D(1.0, 0.0, -0.5), Point3D(1.0, 1.0, 0.0)]
        profile = Profile(station=1.0, points=points)

        # Interpolate to 5 points
        interpolated = profile.interpolate_points(5)
        assert interpolated.num_points == 5
        assert interpolated.station == 1.0

    def test_find_waterline_intersection(self):
        """Test finding waterline intersections."""
        # Create a simple V-shaped profile
        points = [
            Point3D(1.0, -1.0, 0.5),  # Above waterline (port)
            Point3D(1.0, 0.0, -0.5),  # Below waterline (bottom)
            Point3D(1.0, 1.0, 0.5),  # Above waterline (starboard)
        ]
        profile = Profile(station=1.0, points=points)

        # Find intersections at z=0
        intersections = profile.find_waterline_intersection(waterline_z=0.0)

        # Should find 2 intersections (one on each side)
        assert len(intersections) >= 2

        # All intersections should be at z=0
        for point in intersections:
            assert np.isclose(point.z, 0.0)

    def test_calculate_area_below_waterline(self):
        """Test area calculation below waterline."""
        # Create a rectangular profile below waterline
        points = [
            Point3D(1.0, -1.0, 0.0),  # Waterline (port)
            Point3D(1.0, -1.0, -1.0),  # Bottom (port)
            Point3D(1.0, 1.0, -1.0),  # Bottom (starboard)
            Point3D(1.0, 1.0, 0.0),  # Waterline (starboard)
        ]
        profile = Profile(station=1.0, points=points)

        # Area should be approximately 2.0 (width) * 1.0 (depth) = 2.0
        area = profile.calculate_area_below_waterline(waterline_z=0.0)
        assert area > 0.0
        assert np.isclose(area, 2.0, atol=0.1)

    def test_calculate_centroid_below_waterline(self):
        """Test centroid calculation below waterline."""
        # Create a rectangular profile below waterline
        points = [
            Point3D(1.0, -1.0, 0.0),  # Waterline (port)
            Point3D(1.0, -1.0, -1.0),  # Bottom (port)
            Point3D(1.0, 1.0, -1.0),  # Bottom (starboard)
            Point3D(1.0, 1.0, 0.0),  # Waterline (starboard)
        ]
        profile = Profile(station=1.0, points=points)

        y_c, z_c = profile.calculate_centroid_below_waterline(waterline_z=0.0)

        # Centroid should be at center: y=0, z=-0.5
        assert np.isclose(y_c, 0.0, atol=0.1)
        assert np.isclose(z_c, -0.5, atol=0.1)

    def test_rotate_about_x(self):
        """Test profile rotation (heel simulation)."""
        points = [Point3D(1.0, 0.0, 0.0), Point3D(1.0, 1.0, 0.0)]
        profile = Profile(station=1.0, points=points)

        # Rotate 90 degrees (starboard down)
        rotated = profile.rotate_about_x(90.0)

        # Check that points are rotated correctly
        assert rotated.station == 1.0
        assert rotated.num_points == 2

        # Second point at (1, 1, 0) should become (1, 0, -1) after 90° starboard heel
        # Port side (positive y) goes down (negative z)
        assert np.isclose(rotated.points[1].y, 0.0)
        assert np.isclose(rotated.points[1].z, -1.0)

    def test_translate(self):
        """Test profile translation."""
        points = [Point3D(1.0, 0.0, 0.0), Point3D(1.0, 1.0, 0.0)]
        profile = Profile(station=1.0, points=points)

        # Translate
        translated = profile.translate(dx=1.0, dy=0.5, dz=-0.5)

        # Check new station
        assert translated.station == 2.0

        # Check translated points
        assert translated.points[0].x == 2.0
        assert translated.points[0].y == 0.5
        assert translated.points[0].z == -0.5

    def test_copy(self):
        """Test profile copying."""
        points = [Point3D(1.0, 0.0, 0.0)]
        profile1 = Profile(station=1.0, points=points)
        profile2 = profile1.copy()

        assert profile1.station == profile2.station
        assert profile1.num_points == profile2.num_points
        assert profile1 is not profile2  # Different objects
        assert profile1.points[0] is not profile2.points[0]  # Different point objects

    def test_repr(self):
        """Test string representation."""
        points = [Point3D(1.0, 0.0, 0.0)]
        profile = Profile(station=1.0, points=points)
        repr_str = repr(profile)
        assert "Profile" in repr_str
        assert "1.0000" in repr_str

    def test_len(self):
        """Test len() function."""
        points = [Point3D(1.0, 0.0, 0.0), Point3D(1.0, 1.0, 0.0)]
        profile = Profile(station=1.0, points=points)
        assert len(profile) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
