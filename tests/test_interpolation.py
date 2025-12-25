"""
Unit tests for interpolation functions.
"""

import pytest
import numpy as np
from src.geometry.point import Point3D
from src.geometry.profile import Profile
from src.geometry.interpolation import (
    interpolate_transverse,
    interpolate_profile_transverse,
    interpolate_longitudinal,
    interpolate_multiple_profiles,
    interpolate_to_apex,
    create_symmetric_profile,
    resample_profile_uniform_y,
    resample_profile_uniform_arc
)


class TestInterpolateTransverse:
    """Tests for transverse interpolation function."""
    
    def test_basic_linear_interpolation(self):
        """Test basic linear interpolation between points."""
        points = [
            Point3D(0.0, -1.0, 0.0),
            Point3D(0.0, 1.0, 0.0)
        ]
        
        result = interpolate_transverse(points, 5)
        
        assert len(result) == 5
        assert all(p.x == 0.0 for p in result)
        assert result[0].y == pytest.approx(-1.0)
        assert result[2].y == pytest.approx(0.0)
        assert result[4].y == pytest.approx(1.0)
        assert all(p.z == 0.0 for p in result)
    
    def test_interpolation_with_z_variation(self):
        """Test interpolation with varying z-coordinates."""
        points = [
            Point3D(1.0, -0.5, 0.1),
            Point3D(1.0, 0.0, 0.0),
            Point3D(1.0, 0.5, 0.1)
        ]
        
        result = interpolate_transverse(points, 5)
        
        assert len(result) == 5
        assert result[0].y == pytest.approx(-0.5)
        assert result[2].y == pytest.approx(0.0)
        assert result[4].y == pytest.approx(0.5)
        
        # Check z-coordinate at center should be close to 0
        assert result[2].z == pytest.approx(0.0, abs=0.01)
    
    def test_minimum_points_requirement(self):
        """Test that at least 2 points are required."""
        points = [Point3D(0.0, 0.0, 0.0)]
        
        with pytest.raises(ValueError, match="at least 2 points"):
            interpolate_transverse(points, 10)
    
    def test_inconsistent_x_coordinates(self):
        """Test that all points must have same x-coordinate."""
        points = [
            Point3D(0.0, -1.0, 0.0),
            Point3D(1.0, 1.0, 0.0)  # Different x
        ]
        
        with pytest.raises(ValueError, match="same x-coordinate"):
            interpolate_transverse(points, 5)
    
    def test_unsorted_input_points(self):
        """Test that function handles unsorted input points."""
        points = [
            Point3D(0.0, 1.0, 0.0),
            Point3D(0.0, -1.0, 0.0),
            Point3D(0.0, 0.0, 0.5)
        ]
        
        result = interpolate_transverse(points, 5)
        
        # Should be sorted by y-coordinate
        assert result[0].y < result[1].y < result[2].y


class TestInterpolateProfileTransverse:
    """Tests for profile transverse interpolation."""
    
    def test_profile_interpolation(self):
        """Test interpolation of a Profile object."""
        points = [
            Point3D(2.0, -0.5, 0.1),
            Point3D(2.0, 0.5, 0.1)
        ]
        profile = Profile(2.0, points)
        
        result = interpolate_profile_transverse(profile, 10)
        
        assert isinstance(result, Profile)
        assert result.station == 2.0
        assert len(result) == 10


class TestInterpolateLongitudinal:
    """Tests for longitudinal interpolation between profiles."""
    
    def test_midpoint_interpolation(self):
        """Test interpolation at midpoint between two profiles."""
        points1 = [
            Point3D(0.0, -1.0, 0.0),
            Point3D(0.0, 1.0, 0.0)
        ]
        points2 = [
            Point3D(2.0, -0.5, 0.0),
            Point3D(2.0, 0.5, 0.0)
        ]
        
        profile1 = Profile(0.0, points1)
        profile2 = Profile(2.0, points2)
        
        result = interpolate_longitudinal(profile1, profile2, 1.0)
        
        assert result.station == 1.0
        assert len(result) >= 2
        
        # Check that y-coordinates are interpolated
        # At midpoint, y should be between original values
        y_coords = result.get_y_coordinates()
        assert y_coords.min() >= -1.0
        assert y_coords.max() <= 1.0
    
    def test_interpolation_at_boundary(self):
        """Test interpolation at profile boundary stations."""
        points1 = [Point3D(0.0, -1.0, 0.0), Point3D(0.0, 1.0, 0.0)]
        points2 = [Point3D(2.0, -0.5, 0.0), Point3D(2.0, 0.5, 0.0)]
        
        profile1 = Profile(0.0, points1)
        profile2 = Profile(2.0, points2)
        
        # Interpolate at first profile station
        result = interpolate_longitudinal(profile1, profile2, 0.0)
        assert result.station == 0.0
        
        # Interpolate at second profile station
        result = interpolate_longitudinal(profile1, profile2, 2.0)
        assert result.station == 2.0
    
    def test_outside_range_raises_error(self):
        """Test that interpolation outside range raises error."""
        points1 = [Point3D(0.0, -1.0, 0.0), Point3D(0.0, 1.0, 0.0)]
        points2 = [Point3D(2.0, -0.5, 0.0), Point3D(2.0, 0.5, 0.0)]
        
        profile1 = Profile(0.0, points1)
        profile2 = Profile(2.0, points2)
        
        with pytest.raises(ValueError, match="must be between"):
            interpolate_longitudinal(profile1, profile2, -1.0)
        
        with pytest.raises(ValueError, match="must be between"):
            interpolate_longitudinal(profile1, profile2, 3.0)
    
    def test_automatic_profile_ordering(self):
        """Test that profiles are automatically ordered by station."""
        points1 = [Point3D(0.0, -1.0, 0.0), Point3D(0.0, 1.0, 0.0)]
        points2 = [Point3D(2.0, -0.5, 0.0), Point3D(2.0, 0.5, 0.0)]
        
        profile1 = Profile(0.0, points1)
        profile2 = Profile(2.0, points2)
        
        # Pass profiles in reverse order
        result = interpolate_longitudinal(profile2, profile1, 1.0)
        
        assert result.station == 1.0
        assert len(result) >= 2
    
    def test_different_point_counts(self):
        """Test interpolation between profiles with different point counts."""
        points1 = [
            Point3D(0.0, -1.0, 0.0),
            Point3D(0.0, 0.0, 0.5),
            Point3D(0.0, 1.0, 0.0)
        ]
        points2 = [
            Point3D(2.0, -0.5, 0.0),
            Point3D(2.0, 0.5, 0.0)
        ]
        
        profile1 = Profile(0.0, points1)
        profile2 = Profile(2.0, points2)
        
        result = interpolate_longitudinal(profile1, profile2, 1.0)
        
        assert result.station == 1.0
        assert len(result) >= 2


class TestInterpolateMultipleProfiles:
    """Tests for multiple profile interpolation."""
    
    def test_multiple_interpolations(self):
        """Test interpolating multiple profiles at once."""
        points1 = [Point3D(0.0, -1.0, 0.0), Point3D(0.0, 1.0, 0.0)]
        points2 = [Point3D(2.0, -0.5, 0.0), Point3D(2.0, 0.5, 0.0)]
        points3 = [Point3D(4.0, -0.2, 0.0), Point3D(4.0, 0.2, 0.0)]
        
        profiles = [
            Profile(0.0, points1),
            Profile(2.0, points2),
            Profile(4.0, points3)
        ]
        
        target_stations = [0.5, 1.0, 1.5, 2.5, 3.0, 3.5]
        
        results = interpolate_multiple_profiles(profiles, target_stations)
        
        assert len(results) == 6
        for i, result in enumerate(results):
            assert result.station == target_stations[i]
    
    def test_insufficient_profiles_error(self):
        """Test that at least 2 profiles are required."""
        points = [Point3D(0.0, -1.0, 0.0), Point3D(0.0, 1.0, 0.0)]
        profiles = [Profile(0.0, points)]
        
        with pytest.raises(ValueError, match="at least 2 profiles"):
            interpolate_multiple_profiles(profiles, [0.5])
    
    def test_out_of_range_target_error(self):
        """Test that target outside range raises error."""
        points1 = [Point3D(0.0, -1.0, 0.0), Point3D(0.0, 1.0, 0.0)]
        points2 = [Point3D(2.0, -0.5, 0.0), Point3D(2.0, 0.5, 0.0)]
        
        profiles = [Profile(0.0, points1), Profile(2.0, points2)]
        
        with pytest.raises(ValueError, match="outside profile range"):
            interpolate_multiple_profiles(profiles, [3.0])


class TestInterpolateToApex:
    """Tests for bow/stern apex interpolation."""
    
    def test_bow_interpolation(self):
        """Test interpolation toward bow apex."""
        points = [
            Point3D(4.0, -0.5, 0.1),
            Point3D(4.0, 0.0, 0.0),
            Point3D(4.0, 0.5, 0.1)
        ]
        profile = Profile(4.0, points)
        apex = Point3D(5.0, 0.0, 0.15)
        
        results = interpolate_to_apex(profile, apex, num_intermediate_stations=3)
        
        assert len(results) == 3
        
        # Check stations are between profile and apex
        for result in results:
            assert 4.0 < result.station < 5.0
        
        # Check stations are ordered
        for i in range(len(results) - 1):
            assert results[i].station < results[i + 1].station
    
    def test_stern_interpolation(self):
        """Test interpolation toward stern apex."""
        points = [
            Point3D(1.0, -0.5, 0.1),
            Point3D(1.0, 0.0, 0.0),
            Point3D(1.0, 0.5, 0.1)
        ]
        profile = Profile(1.0, points)
        apex = Point3D(0.0, 0.0, 0.15)
        
        results = interpolate_to_apex(profile, apex, num_intermediate_stations=3)
        
        assert len(results) == 3
        
        # Check stations are between apex and profile
        for result in results:
            assert 0.0 < result.station < 1.0
    
    def test_tapering_effect(self):
        """Test that profiles taper toward apex."""
        points = [
            Point3D(4.0, -0.5, 0.1),
            Point3D(4.0, 0.0, 0.0),
            Point3D(4.0, 0.5, 0.1)
        ]
        profile = Profile(4.0, points)
        apex = Point3D(5.0, 0.0, 0.15)
        
        results = interpolate_to_apex(profile, apex, num_intermediate_stations=5)
        
        # Check that profiles get narrower toward apex
        widths = []
        for result in results:
            y_coords = result.get_y_coordinates()
            width = y_coords.max() - y_coords.min()
            widths.append(width)
        
        # Widths should generally decrease
        for i in range(len(widths) - 1):
            assert widths[i] >= widths[i + 1] * 0.8  # Allow some tolerance
    
    def test_apex_at_same_station_error(self):
        """Test that apex at same station raises error."""
        points = [Point3D(4.0, -0.5, 0.1), Point3D(4.0, 0.5, 0.1)]
        profile = Profile(4.0, points)
        apex = Point3D(4.0, 0.0, 0.15)  # Same x as profile
        
        with pytest.raises(ValueError, match="must be different"):
            interpolate_to_apex(profile, apex)


class TestCreateSymmetricProfile:
    """Tests for creating symmetric profiles."""
    
    def test_basic_symmetry(self):
        """Test creating symmetric profile from starboard points."""
        starboard_points = [
            Point3D(1.0, 0.0, 0.0),
            Point3D(1.0, 0.5, 0.1)
        ]
        
        result = create_symmetric_profile(1.0, starboard_points)
        
        assert result.station == 1.0
        # Should have port mirror + starboard = 4 points (including centerline)
        assert len(result) >= 3
        
        # Check symmetry
        y_coords = result.get_y_coordinates()
        assert y_coords.min() < 0  # Has port points
        assert y_coords.max() > 0  # Has starboard points
    
    def test_centerline_inclusion(self):
        """Test centerline point inclusion."""
        starboard_points = [
            Point3D(1.0, 0.2, 0.05),
            Point3D(1.0, 0.5, 0.1)
        ]
        
        result = create_symmetric_profile(1.0, starboard_points, include_centerline=True)
        
        # Should include a centerline point
        y_coords = result.get_y_coordinates()
        assert any(abs(y) < 1e-6 for y in y_coords)
    
    def test_negative_y_error(self):
        """Test that negative y-coordinates raise error."""
        points = [
            Point3D(1.0, -0.5, 0.1),  # Negative y (port side)
            Point3D(1.0, 0.5, 0.1)
        ]
        
        with pytest.raises(ValueError, match="negative y-coordinate"):
            create_symmetric_profile(1.0, points)
    
    def test_wrong_station_error(self):
        """Test that wrong station raises error."""
        points = [Point3D(2.0, 0.5, 0.1)]  # x=2.0, but station=1.0
        
        with pytest.raises(ValueError, match="doesn't match station"):
            create_symmetric_profile(1.0, points)


class TestResampleProfileUniformY:
    """Tests for uniform y-coordinate resampling."""
    
    def test_uniform_y_resampling(self):
        """Test resampling with uniform y-coordinates."""
        points = [
            Point3D(1.0, -0.5, 0.1),
            Point3D(1.0, 0.0, 0.0),
            Point3D(1.0, 0.5, 0.1)
        ]
        profile = Profile(1.0, points)
        
        result = resample_profile_uniform_y(profile, 10)
        
        assert len(result) == 10
        assert result.station == 1.0
        
        # Check y-coordinates are uniformly spaced
        y_coords = result.get_y_coordinates()
        spacings = np.diff(y_coords)
        assert np.allclose(spacings, spacings[0])


class TestResampleProfileUniformArc:
    """Tests for uniform arc-length resampling."""
    
    def test_uniform_arc_resampling(self):
        """Test resampling with uniform arc length."""
        points = [
            Point3D(1.0, -0.5, 0.1),
            Point3D(1.0, 0.0, 0.0),
            Point3D(1.0, 0.5, 0.1)
        ]
        profile = Profile(1.0, points)
        
        result = resample_profile_uniform_arc(profile, 10)
        
        assert len(result) == 10
        assert result.station == 1.0
    
    def test_arc_length_distribution(self):
        """Test that arc lengths are more uniform than y-distribution."""
        # Create profile with varying point density
        points = [
            Point3D(1.0, -1.0, 0.0),
            Point3D(1.0, -0.9, 0.0),
            Point3D(1.0, -0.8, 0.0),
            Point3D(1.0, 0.0, 0.5),
            Point3D(1.0, 1.0, 0.0)
        ]
        profile = Profile(1.0, points)
        
        result = resample_profile_uniform_arc(profile, 10)
        
        assert len(result) == 10
        
        # Calculate arc lengths between consecutive points
        arc_lengths = []
        for i in range(len(result) - 1):
            length = result.points[i].distance_to(result.points[i + 1])
            arc_lengths.append(length)
        
        # Arc lengths should be relatively uniform
        # (allowing for some variation due to curve interpolation)
        mean_arc = np.mean(arc_lengths)
        assert all(0.5 * mean_arc < length < 1.5 * mean_arc for length in arc_lengths)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
