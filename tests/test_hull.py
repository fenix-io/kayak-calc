"""
Unit tests for KayakHull class.
"""

import pytest
import numpy as np
from src.geometry import Point3D, Profile, KayakHull


class TestKayakHull:
    """Tests for the KayakHull class."""

    def create_simple_profile(
        self, station: float, width: float = 1.0, depth: float = 0.5
    ) -> Profile:
        """
        Helper method to create a simple symmetric V-shaped profile.

        Args:
            station: Longitudinal position
            width: Half-width of profile
            depth: Depth below centerline

        Returns:
            Profile object
        """
        points = [
            Point3D(station, -width, 0.0),  # Port side at waterline
            Point3D(station, -width / 2, -depth / 2),  # Port mid
            Point3D(station, 0.0, -depth),  # Bottom (centerline)
            Point3D(station, width / 2, -depth / 2),  # Starboard mid
            Point3D(station, width, 0.0),  # Starboard side at waterline
        ]
        return Profile(station, points)

    def test_initialization(self):
        """Test basic hull initialization."""
        hull = KayakHull()
        assert hull.num_profiles == 0
        assert hull.origin == Point3D(0.0, 0.0, 0.0)

    def test_initialization_with_origin(self):
        """Test hull initialization with custom origin."""
        origin = Point3D(1.0, 0.0, 0.5)
        hull = KayakHull(origin=origin)
        assert hull.origin == origin

    def test_add_profile(self):
        """Test adding profiles to hull."""
        hull = KayakHull()
        profile = self.create_simple_profile(station=1.0)

        hull.add_profile(profile)
        assert hull.num_profiles == 1
        assert 1.0 in hull.profiles

    def test_add_profile_duplicate_station(self):
        """Test that adding duplicate station raises error."""
        hull = KayakHull()
        profile1 = self.create_simple_profile(station=1.0)
        profile2 = self.create_simple_profile(station=1.0)

        hull.add_profile(profile1)
        with pytest.raises(ValueError, match="already exists"):
            hull.add_profile(profile2)

    def test_add_profile_from_points(self):
        """Test creating and adding profile from points."""
        hull = KayakHull()
        points = [Point3D(2.0, -0.5, 0.0), Point3D(2.0, 0.0, -0.3), Point3D(2.0, 0.5, 0.0)]

        hull.add_profile_from_points(station=2.0, points=points)
        assert hull.num_profiles == 1
        assert 2.0 in hull.profiles

    def test_update_profile(self):
        """Test updating an existing profile."""
        hull = KayakHull()
        profile1 = self.create_simple_profile(station=1.0, width=1.0)
        profile2 = self.create_simple_profile(station=1.0, width=2.0)

        hull.add_profile(profile1)
        hull.update_profile(profile2)

        assert hull.num_profiles == 1
        assert hull.profiles[1.0].get_y_coordinates().max() == 2.0

    def test_remove_profile(self):
        """Test removing a profile."""
        hull = KayakHull()
        profile = self.create_simple_profile(station=1.0)

        hull.add_profile(profile)
        assert hull.num_profiles == 1

        hull.remove_profile(1.0)
        assert hull.num_profiles == 0

    def test_remove_profile_not_exists(self):
        """Test removing non-existent profile raises error."""
        hull = KayakHull()
        with pytest.raises(KeyError):
            hull.remove_profile(1.0)

    def test_get_profile_exact_match(self):
        """Test retrieving profile with exact station match."""
        hull = KayakHull()
        profile = self.create_simple_profile(station=1.0)
        hull.add_profile(profile)

        retrieved = hull.get_profile(1.0)
        assert retrieved is not None
        assert retrieved.station == 1.0

    def test_get_profile_no_interpolation(self):
        """Test retrieving profile without interpolation."""
        hull = KayakHull()
        profile = self.create_simple_profile(station=1.0)
        hull.add_profile(profile)

        retrieved = hull.get_profile(1.5, interpolate=False)
        assert retrieved is None

    def test_get_profile_with_interpolation(self):
        """Test retrieving interpolated profile."""
        hull = KayakHull()
        profile1 = self.create_simple_profile(station=1.0, width=1.0, depth=0.5)
        profile2 = self.create_simple_profile(station=2.0, width=1.5, depth=0.7)

        hull.add_profile(profile1)
        hull.add_profile(profile2)

        # Interpolate at midpoint
        interpolated = hull.get_profile(1.5)
        assert interpolated is not None
        assert interpolated.station == 1.5
        assert len(interpolated.points) > 0

    def test_interpolate_insufficient_profiles(self):
        """Test interpolation with insufficient profiles."""
        hull = KayakHull()
        profile = self.create_simple_profile(station=1.0)
        hull.add_profile(profile)

        with pytest.raises(ValueError, match="at least 2 profiles"):
            hull.get_profile(1.5, interpolate=True)

    def test_interpolate_out_of_range(self):
        """Test interpolation outside station range."""
        hull = KayakHull()
        hull.add_profile(self.create_simple_profile(station=1.0))
        hull.add_profile(self.create_simple_profile(station=2.0))

        with pytest.raises(ValueError, match="outside the hull range"):
            hull.get_profile(0.5)  # Before first station

        with pytest.raises(ValueError, match="outside the hull range"):
            hull.get_profile(2.5)  # After last station

    def test_get_stations(self):
        """Test getting sorted list of stations."""
        hull = KayakHull()
        hull.add_profile(self.create_simple_profile(station=2.0))
        hull.add_profile(self.create_simple_profile(station=1.0))
        hull.add_profile(self.create_simple_profile(station=3.0))

        stations = hull.get_stations()
        assert stations == [1.0, 2.0, 3.0]  # Should be sorted

    def test_length_property(self):
        """Test hull length calculation."""
        hull = KayakHull()
        hull.add_profile(self.create_simple_profile(station=0.0))
        hull.add_profile(self.create_simple_profile(station=5.0))

        assert hull.length == 5.0

    def test_length_property_single_profile(self):
        """Test length with single profile."""
        hull = KayakHull()
        hull.add_profile(self.create_simple_profile(station=1.0))

        assert hull.length == 0.0

    def test_max_beam_property(self):
        """Test maximum beam calculation."""
        hull = KayakHull()
        hull.add_profile(self.create_simple_profile(station=1.0, width=1.0))
        hull.add_profile(self.create_simple_profile(station=2.0, width=1.5))
        hull.add_profile(self.create_simple_profile(station=3.0, width=1.2))

        # Max width should be 3.0 (1.5 * 2, from -1.5 to 1.5)
        assert np.isclose(hull.max_beam, 3.0, atol=0.01)

    def test_validate_symmetry_symmetric(self):
        """Test symmetry validation for symmetric profile."""
        hull = KayakHull()
        profile = self.create_simple_profile(station=1.0)
        hull.add_profile(profile)

        is_symmetric, errors = hull.validate_symmetry()
        assert is_symmetric
        assert len(errors) == 0

    def test_validate_symmetry_asymmetric(self):
        """Test symmetry validation for asymmetric profile."""
        hull = KayakHull()
        points = [
            Point3D(1.0, -1.0, 0.0),
            Point3D(1.0, 0.0, -0.5),
            Point3D(1.0, 0.5, 0.0),  # Different from port side
        ]
        profile = Profile(1.0, points)
        hull.add_profile(profile)

        is_symmetric, errors = hull.validate_symmetry()
        assert not is_symmetric
        assert len(errors) > 0

    def test_validate_data_consistency_valid(self):
        """Test data consistency validation for valid hull."""
        hull = KayakHull()
        hull.add_profile(self.create_simple_profile(station=1.0))
        hull.add_profile(self.create_simple_profile(station=2.0))

        is_valid, errors = hull.validate_data_consistency()
        assert is_valid
        assert len(errors) == 0

    def test_validate_data_consistency_empty(self):
        """Test data consistency for empty hull."""
        hull = KayakHull()

        is_valid, errors = hull.validate_data_consistency()
        assert not is_valid
        assert "no profiles" in errors[0].lower()

    def test_validate_data_consistency_too_few_points(self):
        """Test data consistency with insufficient points."""
        hull = KayakHull()
        points = [Point3D(1.0, -0.5, 0.0), Point3D(1.0, 0.5, 0.0)]  # Only 2 points
        profile = Profile(1.0, points)
        hull.add_profile(profile)

        is_valid, errors = hull.validate_data_consistency()
        assert not is_valid
        assert any("only 2 points" in e for e in errors)

    def test_get_bow_station(self):
        """Test getting bow station."""
        hull = KayakHull(coordinate_system="stern_origin")
        hull.add_profile(self.create_simple_profile(station=1.0))
        hull.add_profile(self.create_simple_profile(station=3.0))
        hull.add_profile(self.create_simple_profile(station=2.0))

        assert hull.get_bow_station() == 3.0

    def test_get_stern_station(self):
        """Test getting stern station."""
        hull = KayakHull(coordinate_system="stern_origin")
        hull.add_profile(self.create_simple_profile(station=1.0))
        hull.add_profile(self.create_simple_profile(station=3.0))
        hull.add_profile(self.create_simple_profile(station=2.0))

        assert hull.get_stern_station() == 1.0

    def test_get_bow_stern_empty_hull(self):
        """Test getting bow/stern from empty hull."""
        hull = KayakHull()

        with pytest.raises(ValueError, match="no profiles"):
            hull.get_bow_station()

        with pytest.raises(ValueError, match="no profiles"):
            hull.get_stern_station()

    def test_rotate_about_x(self):
        """Test hull rotation (heel simulation)."""
        hull = KayakHull()
        profile = self.create_simple_profile(station=1.0)
        hull.add_profile(profile)

        # Rotate 45 degrees
        rotated_hull = hull.rotate_about_x(45.0)

        assert rotated_hull.num_profiles == 1
        assert 1.0 in rotated_hull.profiles

        # Original hull should be unchanged
        assert hull.num_profiles == 1

        # Rotated hull should have different point coordinates
        orig_point = hull.profiles[1.0].points[0]
        rot_point = rotated_hull.profiles[1.0].points[0]
        assert not (orig_point == rot_point)

    def test_translate(self):
        """Test hull translation."""
        hull = KayakHull()
        hull.add_profile(self.create_simple_profile(station=1.0))
        hull.add_profile(self.create_simple_profile(station=2.0))

        # Translate
        translated_hull = hull.translate(dx=1.0, dy=0.5, dz=-0.5)

        assert translated_hull.num_profiles == 2

        # Check that stations are updated
        assert 2.0 in translated_hull.profiles  # 1.0 + 1.0
        assert 3.0 in translated_hull.profiles  # 2.0 + 1.0

        # Original hull should be unchanged
        assert 1.0 in hull.profiles
        assert 2.0 in hull.profiles

    def test_copy(self):
        """Test hull copying."""
        hull = KayakHull()
        hull.add_profile(self.create_simple_profile(station=1.0))
        hull.add_profile(self.create_simple_profile(station=2.0))

        copied_hull = hull.copy()

        # Same content
        assert copied_hull.num_profiles == hull.num_profiles
        assert copied_hull.get_stations() == hull.get_stations()

        # Different objects
        assert copied_hull is not hull
        assert copied_hull.profiles[1.0] is not hull.profiles[1.0]

    def test_repr(self):
        """Test string representation."""
        hull = KayakHull()
        hull.add_profile(self.create_simple_profile(station=0.0))
        hull.add_profile(self.create_simple_profile(station=5.0, width=1.5))

        repr_str = repr(hull)
        assert "KayakHull" in repr_str
        assert "num_profiles=2" in repr_str
        assert "length=5.0000" in repr_str

    def test_len(self):
        """Test len() function."""
        hull = KayakHull()
        hull.add_profile(self.create_simple_profile(station=1.0))
        hull.add_profile(self.create_simple_profile(station=2.0))

        assert len(hull) == 2

    def test_complex_interpolation(self):
        """Test interpolation with varying profile shapes."""
        hull = KayakHull()

        # Create profiles with different numbers of points
        points1 = [Point3D(0.0, -1.0, 0.0), Point3D(0.0, 0.0, -0.5), Point3D(0.0, 1.0, 0.0)]

        points2 = [
            Point3D(2.0, -1.5, 0.0),
            Point3D(2.0, -0.75, -0.4),
            Point3D(2.0, 0.0, -0.8),
            Point3D(2.0, 0.75, -0.4),
            Point3D(2.0, 1.5, 0.0),
        ]

        hull.add_profile(Profile(0.0, points1))
        hull.add_profile(Profile(2.0, points2))

        # Interpolate at midpoint
        interpolated = hull.get_profile(1.0)

        assert interpolated is not None
        assert interpolated.station == 1.0
        assert len(interpolated.points) >= 3

        # Check that interpolated profile has reasonable coordinates
        y_coords = interpolated.get_y_coordinates()
        z_coords = interpolated.get_z_coordinates()

        # Should be between the two profiles
        assert y_coords.min() >= -1.5
        assert y_coords.max() <= 1.5
        assert z_coords.min() >= -0.8
        assert z_coords.max() <= 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
