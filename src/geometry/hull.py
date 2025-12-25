"""
KayakHull class for defining and managing kayak hull geometry.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Union
from .point import Point3D
from .profile import Profile


class KayakHull:
    """
    Represents the complete hull geometry of a kayak.
    
    The hull is defined by a collection of transverse profiles at various
    longitudinal stations. The coordinate system is referenced to the centerline
    plane (y=0), with:
    - X-axis: Longitudinal (along kayak length)
    - Y-axis: Transverse (port negative, starboard positive)
    - Z-axis: Vertical (down negative, up positive)
    
    Attributes:
        profiles (Dict[float, Profile]): Dictionary mapping station positions to profiles
        origin (Point3D): Reference origin point on centerline
        length (float): Overall length of kayak
        beam (float): Maximum beam (width)
    """
    
    def __init__(self, origin: Optional[Point3D] = None):
        """
        Initialize a kayak hull.
        
        Args:
            origin: Reference origin point (default: Point3D(0, 0, 0))
        """
        self.profiles: Dict[float, Profile] = {}
        self.origin = origin if origin is not None else Point3D(0.0, 0.0, 0.0)
        self._sorted_stations: Optional[List[float]] = None
    
    def add_profile(self, profile: Profile) -> None:
        """
        Add a profile to the hull at its station position.
        
        Args:
            profile: Profile object to add
            
        Raises:
            ValueError: If a profile already exists at this station
        """
        station = profile.station
        
        if station in self.profiles:
            raise ValueError(
                f"Profile already exists at station {station}. "
                f"Use update_profile() to replace it."
            )
        
        self.profiles[station] = profile
        self._sorted_stations = None  # Invalidate cached sorted stations
    
    def add_profile_from_points(self, station: float, points: List[Point3D]) -> None:
        """
        Create and add a profile from a list of points.
        
        Args:
            station: Longitudinal position for the profile
            points: List of Point3D objects defining the profile
            
        Raises:
            ValueError: If a profile already exists at this station
        """
        profile = Profile(station, points)
        self.add_profile(profile)
    
    def update_profile(self, profile: Profile) -> None:
        """
        Update or add a profile at its station position.
        
        Args:
            profile: Profile object to update/add
        """
        self.profiles[profile.station] = profile
        self._sorted_stations = None
    
    def remove_profile(self, station: float) -> None:
        """
        Remove a profile at the specified station.
        
        Args:
            station: Station position of profile to remove
            
        Raises:
            KeyError: If no profile exists at this station
        """
        if station not in self.profiles:
            raise KeyError(f"No profile exists at station {station}")
        
        del self.profiles[station]
        self._sorted_stations = None
    
    def get_profile(self, station: float, interpolate: bool = True) -> Optional[Profile]:
        """
        Retrieve a profile at the specified station.
        
        If a profile exists exactly at the station, return it.
        If interpolate=True and no exact match, interpolate between adjacent profiles.
        
        Args:
            station: Longitudinal position
            interpolate: Whether to interpolate if no exact match (default: True)
            
        Returns:
            Profile at the station, or None if not found and interpolate=False
            
        Raises:
            ValueError: If interpolation requested but insufficient profiles exist
        """
        # Check for exact match
        if station in self.profiles:
            return self.profiles[station]
        
        if not interpolate:
            return None
        
        # Interpolate between adjacent profiles
        return self._interpolate_profile(station)
    
    def _interpolate_profile(self, station: float) -> Profile:
        """
        Interpolate a profile at the given station from adjacent profiles.
        
        Args:
            station: Longitudinal position for interpolation
            
        Returns:
            Interpolated Profile
            
        Raises:
            ValueError: If insufficient profiles for interpolation
        """
        if len(self.profiles) < 2:
            raise ValueError(
                "Need at least 2 profiles to interpolate. "
                f"Currently have {len(self.profiles)} profile(s)."
            )
        
        stations = self.get_stations()
        
        # Check if station is within range
        if station < stations[0] or station > stations[-1]:
            raise ValueError(
                f"Station {station} is outside the hull range "
                f"[{stations[0]}, {stations[-1]}]"
            )
        
        # Find adjacent stations
        station_before = None
        station_after = None
        
        for s in stations:
            if s < station:
                station_before = s
            elif s > station:
                station_after = s
                break
        
        if station_before is None or station_after is None:
            raise ValueError(f"Cannot find adjacent profiles for station {station}")
        
        # Get the two profiles
        profile_before = self.profiles[station_before]
        profile_after = self.profiles[station_after]
        
        # Linear interpolation factor
        t = (station - station_before) / (station_after - station_before)
        
        # Interpolate points between the two profiles
        interpolated_points = self._interpolate_points_between_profiles(
            profile_before, profile_after, t, station
        )
        
        return Profile(station, interpolated_points)
    
    def _interpolate_points_between_profiles(
        self, 
        profile1: Profile, 
        profile2: Profile, 
        t: float,
        target_station: float
    ) -> List[Point3D]:
        """
        Interpolate points between two profiles.
        
        This method handles profiles with different numbers of points by
        interpolating both profiles to a common set of y-coordinates.
        
        Args:
            profile1: First profile (at lower station)
            profile2: Second profile (at higher station)
            t: Interpolation factor (0 = profile1, 1 = profile2)
            target_station: Target station for interpolated profile
            
        Returns:
            List of interpolated Point3D objects
        """
        # Sort points by y-coordinate
        points1 = sorted(profile1.points, key=lambda p: p.y)
        points2 = sorted(profile2.points, key=lambda p: p.y)
        
        # Get y-coordinate ranges
        y1 = np.array([p.y for p in points1])
        z1 = np.array([p.z for p in points1])
        
        y2 = np.array([p.y for p in points2])
        z2 = np.array([p.z for p in points2])
        
        # Determine common y-coordinate range
        y_min = max(y1.min(), y2.min())
        y_max = min(y1.max(), y2.max())
        
        # Use the average number of points
        num_points = (len(points1) + len(points2)) // 2
        num_points = max(num_points, 10)  # Minimum 10 points
        
        # Create common y-coordinates
        y_common = np.linspace(y_min, y_max, num_points)
        
        # Interpolate z-coordinates for both profiles
        z1_interp = np.interp(y_common, y1, z1)
        z2_interp = np.interp(y_common, y2, z2)
        
        # Linear interpolation between the two profiles
        z_result = (1 - t) * z1_interp + t * z2_interp
        
        # Create interpolated points
        interpolated_points = [
            Point3D(target_station, y, z) 
            for y, z in zip(y_common, z_result)
        ]
        
        return interpolated_points
    
    def get_stations(self) -> List[float]:
        """
        Get sorted list of all station positions.
        
        Returns:
            Sorted list of station positions
        """
        if self._sorted_stations is None:
            self._sorted_stations = sorted(self.profiles.keys())
        return self._sorted_stations
    
    @property
    def num_profiles(self) -> int:
        """Get the number of profiles in the hull."""
        return len(self.profiles)
    
    @property
    def length(self) -> float:
        """
        Get overall length of the hull.
        
        Returns:
            Distance between first and last stations
        """
        if len(self.profiles) < 2:
            return 0.0
        
        stations = self.get_stations()
        return stations[-1] - stations[0]
    
    @property
    def max_beam(self) -> float:
        """
        Get maximum beam (width) of the hull.
        
        Returns:
            Maximum transverse distance across all profiles
        """
        if len(self.profiles) == 0:
            return 0.0
        
        max_width = 0.0
        
        for profile in self.profiles.values():
            y_coords = profile.get_y_coordinates()
            if len(y_coords) > 0:
                width = y_coords.max() - y_coords.min()
                max_width = max(max_width, width)
        
        return max_width
    
    def validate_symmetry(self, tolerance: float = 1e-6) -> Tuple[bool, List[str]]:
        """
        Validate that all profiles are symmetric about the centerline (y=0).
        
        Args:
            tolerance: Maximum allowed asymmetry
            
        Returns:
            Tuple of (is_symmetric, list_of_error_messages)
        """
        is_symmetric = True
        errors = []
        
        for station, profile in self.profiles.items():
            # Get y-coordinates
            y_coords = profile.get_y_coordinates()
            
            # Check if we have points on both sides of centerline
            port_points = y_coords[y_coords < -tolerance]
            stbd_points = y_coords[y_coords > tolerance]
            
            if len(port_points) == 0 and len(stbd_points) == 0:
                # All points on centerline - symmetric
                continue
            
            if len(port_points) == 0 or len(stbd_points) == 0:
                is_symmetric = False
                errors.append(
                    f"Station {station}: Profile has points only on one side of centerline"
                )
                continue
            
            # Check symmetry by comparing port and starboard points
            # For each starboard point, find corresponding port point
            for p in profile.points:
                if abs(p.y) < tolerance:  # Skip centerline points
                    continue
                
                # Find mirror point
                mirror_y = -p.y
                found_mirror = False
                
                for p2 in profile.points:
                    if abs(p2.y - mirror_y) < tolerance:
                        # Check if z-coordinate matches
                        if abs(p2.z - p.z) < tolerance:
                            found_mirror = True
                            break
                
                if not found_mirror:
                    is_symmetric = False
                    errors.append(
                        f"Station {station}: No symmetric point found for y={p.y:.4f}, z={p.z:.4f}"
                    )
                    break  # Only report first error per profile
        
        return is_symmetric, errors
    
    def validate_data_consistency(self) -> Tuple[bool, List[str]]:
        """
        Validate data consistency across all profiles.
        
        Checks:
        - All profiles have at least 3 points
        - Profiles are ordered by station
        - No duplicate stations
        - All profile points have correct x-coordinate
        
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        is_valid = True
        errors = []
        
        if len(self.profiles) == 0:
            errors.append("Hull has no profiles")
            return False, errors
        
        stations = self.get_stations()
        
        # Check for minimum points in each profile
        for station, profile in self.profiles.items():
            if len(profile.points) < 3:
                is_valid = False
                errors.append(
                    f"Station {station}: Profile has only {len(profile.points)} points "
                    f"(minimum 3 required)"
                )
            
            # Validate that all points have correct x-coordinate
            for i, point in enumerate(profile.points):
                if not np.isclose(point.x, station):
                    is_valid = False
                    errors.append(
                        f"Station {station}: Point {i} has x={point.x} "
                        f"(should be {station})"
                    )
        
        # Check for reasonable station spacing
        if len(stations) > 1:
            spacings = np.diff(stations)
            if np.any(spacings <= 0):
                is_valid = False
                errors.append("Stations are not in ascending order")
        
        return is_valid, errors
    
    def get_bow_station(self) -> float:
        """
        Get the bow (forward) station position.
        
        Returns:
            Maximum station position (assumed to be bow)
        """
        if len(self.profiles) == 0:
            raise ValueError("Hull has no profiles")
        return max(self.profiles.keys())
    
    def get_stern_station(self) -> float:
        """
        Get the stern (aft) station position.
        
        Returns:
            Minimum station position (assumed to be stern)
        """
        if len(self.profiles) == 0:
            raise ValueError("Hull has no profiles")
        return min(self.profiles.keys())
    
    def rotate_about_x(self, angle_deg: float) -> 'KayakHull':
        """
        Create a new hull rotated about the X-axis (heel angle).
        
        This is used to simulate the hull geometry when heeled.
        
        Args:
            angle_deg: Heel angle in degrees (positive = starboard down)
            
        Returns:
            New KayakHull with all profiles rotated
        """
        new_hull = KayakHull(origin=self.origin.rotate_x(angle_deg))
        
        for station, profile in self.profiles.items():
            rotated_profile = profile.rotate_about_x(angle_deg)
            new_hull.add_profile(rotated_profile)
        
        return new_hull
    
    def translate(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> 'KayakHull':
        """
        Create a new hull translated by given offsets.
        
        Args:
            dx: Translation in x direction
            dy: Translation in y direction
            dz: Translation in z direction
            
        Returns:
            New KayakHull with all profiles translated
        """
        new_hull = KayakHull(origin=self.origin.translate(dx, dy, dz))
        
        for station, profile in self.profiles.items():
            translated_profile = profile.translate(dx, dy, dz)
            new_hull.add_profile(translated_profile)
        
        return new_hull
    
    def copy(self) -> 'KayakHull':
        """
        Create a deep copy of this hull.
        
        Returns:
            New KayakHull with copied profiles
        """
        new_hull = KayakHull(origin=self.origin.copy())
        
        for station, profile in self.profiles.items():
            new_hull.add_profile(profile.copy())
        
        return new_hull
    
    def __repr__(self) -> str:
        """String representation of the hull."""
        return (
            f"KayakHull(num_profiles={self.num_profiles}, "
            f"length={self.length:.4f}, max_beam={self.max_beam:.4f})"
        )
    
    def __len__(self) -> int:
        """Get number of profiles in hull."""
        return len(self.profiles)
