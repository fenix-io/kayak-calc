"""
Volume integration for kayak hull hydrostatics.

This module provides functions for calculating displaced volume by integrating
cross-sectional areas along the length of the hull. Supports multiple numerical
integration methods including Simpson's rule and trapezoidal rule.

Mathematical Background:
- Volume is calculated by integrating cross-sectional area along length
- V = ∫ A(x) dx where A(x) is the cross-sectional area at position x
- Numerical integration handles irregular station spacing

References:
- Rawson, K. J., & Tupper, E. C. (2001). Basic ship theory (5th ed.).
- Numerical Recipes in C (Press et al.)
"""

from typing import List, Tuple, Optional, Union
from dataclasses import dataclass
import numpy as np

from ..geometry import KayakHull
from .cross_section import calculate_section_properties


@dataclass
class DisplacementProperties:
    """
    Displacement and volume properties of a hull.

    This class encapsulates the calculated displacement properties including
    volume, mass, and related parameters.

    Attributes:
        volume: Displaced volume (m³)
        mass: Displaced mass (kg) = volume × water_density
        waterline_z: Z-coordinate of the waterline (m)
        heel_angle: Heel angle in degrees (0 = upright)
        water_density: Water density used (kg/m³), default 1025 for seawater
        num_stations: Number of stations used in integration
        integration_method: Integration method used ('simpson' or 'trapezoidal')
        stations: List of station positions used
        areas: List of cross-sectional areas at each station
    """

    volume: float
    mass: float
    waterline_z: float
    heel_angle: float = 0.0
    water_density: float = 1025.0
    num_stations: int = 0
    integration_method: str = "simpson"
    stations: Optional[List[float]] = None
    areas: Optional[List[float]] = None

    @property
    def displacement_tons(self) -> float:
        """Get displacement in metric tons (tonnes)."""
        return self.mass / 1000.0

    def __repr__(self) -> str:
        """String representation of displacement properties."""
        return (
            f"DisplacementProperties(\n"
            f"  volume={self.volume:.6f} m³,\n"
            f"  mass={self.mass:.2f} kg ({self.displacement_tons:.3f} tonnes),\n"
            f"  waterline_z={self.waterline_z:.4f} m,\n"
            f"  heel_angle={self.heel_angle:.2f}°,\n"
            f"  water_density={self.water_density:.1f} kg/m³,\n"
            f"  num_stations={self.num_stations},\n"
            f"  method='{self.integration_method}'\n"
            f")"
        )


@dataclass
class CenterOfBuoyancy:
    """
    Center of Buoyancy (CB) position and related properties.

    The center of buoyancy is the centroid of the displaced volume, i.e.,
    the point through which the buoyant force acts. It varies with waterline
    and heel angle.

    Attributes:
        lcb: Longitudinal Center of Buoyancy (m) - x-coordinate
        vcb: Vertical Center of Buoyancy (m) - z-coordinate
        tcb: Transverse Center of Buoyancy (m) - y-coordinate (0 for symmetric upright)
        volume: Displaced volume (m³)
        waterline_z: Z-coordinate of the waterline (m)
        heel_angle: Heel angle in degrees (0 = upright)
        num_stations: Number of stations used in integration
        integration_method: Integration method used ('simpson' or 'trapezoidal')

    Note:
        - LCB is measured from the origin along the longitudinal (x) axis
        - VCB is measured from the origin along the vertical (z) axis
        - TCB is measured from the centerline (y=0); should be ~0 for upright symmetric hulls
        - Positive x is typically forward (bow direction)
        - Positive z is typically up
        - Positive y is typically starboard
    """

    lcb: float
    vcb: float
    tcb: float
    volume: float
    waterline_z: float
    heel_angle: float = 0.0
    num_stations: int = 0
    integration_method: str = "simpson"

    def __repr__(self) -> str:
        """String representation of center of buoyancy."""
        return (
            f"CenterOfBuoyancy(\n"
            f"  LCB={self.lcb:.6f} m,\n"
            f"  VCB={self.vcb:.6f} m,\n"
            f"  TCB={self.tcb:.6f} m,\n"
            f"  volume={self.volume:.6f} m³,\n"
            f"  waterline_z={self.waterline_z:.4f} m,\n"
            f"  heel_angle={self.heel_angle:.2f}°,\n"
            f"  num_stations={self.num_stations},\n"
            f"  method='{self.integration_method}'\n"
            f")"
        )


def integrate_simpson(x: np.ndarray, y: np.ndarray) -> float:
    """
    Integrate using Simpson's rule.

    Simpson's rule provides better accuracy than trapezoidal rule for smooth
    functions. Works best with an odd number of points (even number of intervals).

    Formula:
    ∫f(x)dx ≈ (h/3)[f(x₀) + 4f(x₁) + 2f(x₂) + 4f(x₃) + ... + f(xₙ)]

    where h is the spacing (for uniform spacing) or adjusted for non-uniform.

    Args:
        x: Array of x-coordinates (stations)
        y: Array of y-values (areas)

    Returns:
        Integrated value (volume)

    Note:
        For non-uniform spacing, uses composite Simpson's rule
        If number of intervals is odd, uses trapezoidal rule for last interval
    """
    n = len(x)

    if n < 2:
        return 0.0

    if n == 2:
        # Fall back to trapezoidal for 2 points
        return 0.5 * (y[0] + y[1]) * (x[1] - x[0])

    # Use scipy's simpson for non-uniform spacing if available
    try:
        from scipy.integrate import simpson

        return simpson(y, x=x)
    except ImportError:
        # Fallback: use trapezoidal for non-uniform spacing
        # Manual Simpson's implementation can have issues with non-uniform spacing
        return integrate_trapezoidal(x, y)


def integrate_trapezoidal(x: np.ndarray, y: np.ndarray) -> float:
    """
    Integrate using trapezoidal rule.

    The trapezoidal rule is simpler and more robust than Simpson's rule,
    especially for irregular spacing. It approximates the area under the
    curve as a series of trapezoids.

    Formula:
    ∫f(x)dx ≈ Σ[(x[i+1] - x[i]) * (y[i] + y[i+1]) / 2]

    Args:
        x: Array of x-coordinates (stations)
        y: Array of y-values (areas)

    Returns:
        Integrated value (volume)
    """
    n = len(x)

    if n < 2:
        return 0.0

    result = 0.0
    for i in range(n - 1):
        h = x[i + 1] - x[i]
        result += 0.5 * h * (y[i] + y[i + 1])

    return result


def calculate_volume(
    hull: KayakHull,
    waterline_z: float = 0.0,
    heel_angle: float = 0.0,
    num_stations: Optional[int] = None,
    method: str = "simpson",
    use_existing_stations: bool = True,
) -> float:
    """
    Calculate displaced volume of the hull.

    Integrates cross-sectional areas along the length of the hull to
    calculate total displaced volume.

    Args:
        hull: KayakHull object with defined profiles
        waterline_z: Z-coordinate of the waterline (default: 0.0)
        heel_angle: Heel angle in degrees (default: 0.0)
        num_stations: Number of stations to use for integration
                     If None, uses existing hull stations
        method: Integration method ('simpson' or 'trapezoidal')
        use_existing_stations: If True, uses hull's existing stations
                              If False, creates evenly spaced stations

    Returns:
        Volume in cubic meters (m³)

    Example:
        >>> hull = KayakHull()
        >>> # ... add profiles to hull ...
        >>> volume = calculate_volume(hull, waterline_z=0.0)
        >>> print(f"Volume: {volume:.3f} m³")

    Raises:
        ValueError: If hull has insufficient profiles
    """
    if len(hull) < 2:
        raise ValueError(
            f"Need at least 2 profiles to calculate volume. " f"Hull has {len(hull)} profile(s)."
        )

    # Determine stations to use
    if use_existing_stations and num_stations is None:
        stations = hull.get_stations()
    elif num_stations is not None:
        # Create evenly spaced stations
        # Note: bow and stern positions depend on coordinate system,
        # but we need min < max for integration
        stern_station = hull.get_stern_station()
        bow_station = hull.get_bow_station()
        min_station = min(stern_station, bow_station)
        max_station = max(stern_station, bow_station)
        stations = np.linspace(min_station, max_station, num_stations)
    else:
        stations = hull.get_stations()

    # Calculate areas at each station
    areas = []
    for station in stations:
        profile = hull.get_profile(station, interpolate=True)
        props = calculate_section_properties(profile, waterline_z, heel_angle)
        areas.append(props.area)

    # Convert to numpy arrays
    x = np.array(stations)
    y = np.array(areas)

    # Integrate using specified method
    if method.lower() == "simpson":
        volume = integrate_simpson(x, y)
    elif method.lower() == "trapezoidal":
        volume = integrate_trapezoidal(x, y)
    else:
        raise ValueError(
            f"Unknown integration method: {method}. " f"Use 'simpson' or 'trapezoidal'."
        )

    return volume


def calculate_displacement(
    hull: KayakHull,
    waterline_z: float = 0.0,
    heel_angle: float = 0.0,
    water_density: float = 1025.0,
    num_stations: Optional[int] = None,
    method: str = "simpson",
    use_existing_stations: bool = True,
    include_details: bool = False,
) -> DisplacementProperties:
    """
    Calculate displacement properties of the hull.

    This is the main high-level function for displacement calculations.
    Calculates both volume and mass (displacement).

    Args:
        hull: KayakHull object with defined profiles
        waterline_z: Z-coordinate of the waterline (default: 0.0)
        heel_angle: Heel angle in degrees (default: 0.0)
        water_density: Water density in kg/m³ (default: 1025.0 for seawater)
                      Use 1000.0 for freshwater
        num_stations: Number of stations for integration (None = use existing)
        method: Integration method ('simpson' or 'trapezoidal')
        use_existing_stations: Whether to use hull's existing stations
        include_details: If True, includes stations and areas in result

    Returns:
        DisplacementProperties object with volume, mass, and other parameters

    Example:
        >>> hull = create_kayak_hull()
        >>> disp = calculate_displacement(hull, waterline_z=0.0)
        >>> print(f"Volume: {disp.volume:.3f} m³")
        >>> print(f"Mass: {disp.mass:.1f} kg")
        >>> print(f"Displacement: {disp.displacement_tons:.3f} tonnes")

    Note:
        - Default water density is for seawater (1025 kg/m³)
        - For freshwater, use water_density=1000.0
        - Simpson's rule is generally more accurate for smooth hulls
        - Trapezoidal rule is more robust for irregular spacing
    """
    if len(hull) < 2:
        raise ValueError(
            f"Need at least 2 profiles to calculate displacement. "
            f"Hull has {len(hull)} profile(s)."
        )

    # Determine stations to use
    if use_existing_stations and num_stations is None:
        stations = hull.get_stations()
    elif num_stations is not None:
        min_station = hull.get_bow_station()
        max_station = hull.get_stern_station()
        stations = np.linspace(min_station, max_station, num_stations)
    else:
        stations = hull.get_stations()

    # Calculate areas at each station
    areas = []
    for station in stations:
        profile = hull.get_profile(station, interpolate=True)
        props = calculate_section_properties(profile, waterline_z, heel_angle)
        areas.append(props.area)

    # Convert to numpy arrays
    x = np.array(stations)
    y = np.array(areas)

    # Integrate to get volume
    if method.lower() == "simpson":
        volume = integrate_simpson(x, y)
    elif method.lower() == "trapezoidal":
        volume = integrate_trapezoidal(x, y)
    else:
        raise ValueError(
            f"Unknown integration method: {method}. " f"Use 'simpson' or 'trapezoidal'."
        )

    # Calculate mass
    mass = volume * water_density

    # Create displacement properties object
    disp_props = DisplacementProperties(
        volume=volume,
        mass=mass,
        waterline_z=waterline_z,
        heel_angle=heel_angle,
        water_density=water_density,
        num_stations=len(stations),
        integration_method=method,
        stations=list(stations) if include_details else None,
        areas=areas if include_details else None,
    )

    return disp_props


def calculate_displacement_curve(
    hull: KayakHull,
    waterline_levels: Union[List[float], np.ndarray],
    heel_angle: float = 0.0,
    water_density: float = 1025.0,
    method: str = "simpson",
) -> List[DisplacementProperties]:
    """
    Calculate displacement at multiple waterline levels.

    Useful for generating displacement curves showing how displacement
    varies with draft (waterline level).

    Args:
        hull: KayakHull object
        waterline_levels: List of waterline Z-coordinates
        heel_angle: Heel angle in degrees (default: 0.0)
        water_density: Water density in kg/m³
        method: Integration method

    Returns:
        List of DisplacementProperties, one for each waterline level

    Example:
        >>> hull = create_kayak_hull()
        >>> waterlines = np.linspace(-0.3, 0.0, 11)
        >>> displacements = calculate_displacement_curve(hull, waterlines)
        >>> for disp in displacements:
        ...     print(f"Draft {-disp.waterline_z:.3f}m: {disp.volume:.3f} m³")
    """
    results = []

    for wl_z in waterline_levels:
        disp = calculate_displacement(
            hull=hull,
            waterline_z=wl_z,
            heel_angle=heel_angle,
            water_density=water_density,
            method=method,
        )
        results.append(disp)

    return results


def calculate_volume_components(
    hull: KayakHull, waterline_z: float = 0.0, heel_angle: float = 0.0, method: str = "simpson"
) -> Tuple[float, List[float], List[float]]:
    """
    Calculate volume with component breakdown by station.

    Returns the total volume along with the contribution from each
    segment between stations.

    Args:
        hull: KayakHull object
        waterline_z: Z-coordinate of waterline
        heel_angle: Heel angle in degrees
        method: Integration method

    Returns:
        Tuple of (total_volume, station_list, volume_components)

    Note:
        volume_components[i] is the volume contribution between
        station[i] and station[i+1]
    """
    stations = hull.get_stations()

    if len(stations) < 2:
        raise ValueError("Need at least 2 profiles")

    # Calculate areas at each station
    areas = []
    for station in stations:
        profile = hull.get_profile(station, interpolate=True)
        props = calculate_section_properties(profile, waterline_z, heel_angle)
        areas.append(props.area)

    # Calculate volume contribution for each segment
    volume_components = []

    x = np.array(stations)
    y = np.array(areas)

    for i in range(len(stations) - 1):
        # Volume of this segment
        if method.lower() == "simpson" and i < len(stations) - 2:
            # Use Simpson's rule for pairs of segments when possible
            segment_vol = integrate_simpson(x[i : i + 3], y[i : i + 3])
            volume_components.append(segment_vol)
        else:
            # Use trapezoidal for single segment or last segment
            segment_vol = integrate_trapezoidal(x[i : i + 2], y[i : i + 2])
            volume_components.append(segment_vol)

    total_volume = sum(volume_components)

    return total_volume, stations, volume_components


def validate_displacement_properties(
    props: DisplacementProperties, tolerance: float = 1e-6
) -> Tuple[bool, List[str]]:
    """
    Validate displacement properties for physical correctness.

    Args:
        props: DisplacementProperties to validate
        tolerance: Numerical tolerance

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    # Check for negative volume
    if props.volume < -tolerance:
        issues.append(f"Negative volume: {props.volume}")

    # Check for negative mass
    if props.mass < -tolerance:
        issues.append(f"Negative mass: {props.mass}")

    # Check mass = volume × density relationship
    expected_mass = props.volume * props.water_density
    if not np.isclose(props.mass, expected_mass, rtol=tolerance):
        issues.append(f"Mass-volume inconsistency: mass={props.mass}, " f"expected={expected_mass}")

    # Check for NaN or infinite values
    if not np.isfinite(props.volume):
        issues.append(f"Non-finite volume: {props.volume}")

    if not np.isfinite(props.mass):
        issues.append(f"Non-finite mass: {props.mass}")

    # Check reasonable water density
    if props.water_density < 900 or props.water_density > 1100:
        issues.append(
            f"Unusual water density: {props.water_density} kg/m³ "
            f"(typical range: 1000-1025 kg/m³)"
        )

    # Check heel angle range
    if abs(props.heel_angle) > 90 + tolerance:
        issues.append(f"Heel angle out of range: {props.heel_angle}°")

    # Check number of stations
    if props.num_stations < 2:
        issues.append(f"Too few stations: {props.num_stations}")

    is_valid = len(issues) == 0
    return is_valid, issues


def calculate_center_of_buoyancy(
    hull: KayakHull,
    waterline_z: float = 0.0,
    heel_angle: float = 0.0,
    num_stations: Optional[int] = None,
    method: str = "simpson",
    use_existing_stations: bool = True,
) -> CenterOfBuoyancy:
    """
    Calculate the center of buoyancy (CB) of the hull.

    The center of buoyancy is the centroid of the displaced volume. It is
    calculated by integrating the first moments of area along the hull length.

    Mathematical formulation:
        LCB = ∫ x·A(x) dx / V
        VCB = ∫ z_c(x)·A(x) dx / V
        TCB = ∫ y_c(x)·A(x) dx / V

    where:
        - x is the longitudinal position (station)
        - A(x) is the cross-sectional area at position x
        - z_c(x) is the vertical centroid of the cross-section
        - y_c(x) is the transverse centroid of the cross-section
        - V is the total displaced volume

    Args:
        hull: KayakHull object with defined profiles
        waterline_z: Z-coordinate of the waterline (default: 0.0)
        heel_angle: Heel angle in degrees (default: 0.0)
        num_stations: Number of stations to use for integration
                     If None, uses existing hull stations
        method: Integration method ('simpson' or 'trapezoidal')
        use_existing_stations: If True, uses hull's existing stations
                              If False, creates evenly spaced stations

    Returns:
        CenterOfBuoyancy object with LCB, VCB, TCB coordinates

    Example:
        >>> hull = create_kayak_hull()
        >>> cb = calculate_center_of_buoyancy(hull, waterline_z=0.0)
        >>> print(f"LCB: {cb.lcb:.3f} m")
        >>> print(f"VCB: {cb.vcb:.3f} m")

    Raises:
        ValueError: If hull has insufficient profiles
        ValueError: If calculated volume is zero or negative

    Note:
        - For symmetric upright hulls, TCB should be approximately 0
        - TCB varies significantly with heel angle
        - Increasing num_stations improves accuracy
    """
    if len(hull) < 2:
        raise ValueError(
            f"Need at least 2 profiles to calculate CB. " f"Hull has {len(hull)} profile(s)."
        )

    # Determine stations to use
    if use_existing_stations and num_stations is None:
        stations = hull.get_stations()
    elif num_stations is not None:
        # Create evenly spaced stations
        # Note: bow and stern positions depend on coordinate system,
        # but we need min < max for integration
        stern_station = hull.get_stern_station()
        bow_station = hull.get_bow_station()
        min_station = min(stern_station, bow_station)
        max_station = max(stern_station, bow_station)
        stations = np.linspace(min_station, max_station, num_stations)
    else:
        stations = hull.get_stations()

    # Calculate properties at each station
    areas = []
    y_centroids = []
    z_centroids = []

    for station in stations:
        profile = hull.get_profile(station, interpolate=True)
        props = calculate_section_properties(profile, waterline_z, heel_angle)
        areas.append(props.area)
        y_centroids.append(props.centroid_y)
        z_centroids.append(props.centroid_z)

    # Convert to numpy arrays
    x = np.array(stations)
    a = np.array(areas)
    y_c = np.array(y_centroids)
    z_c = np.array(z_centroids)

    # Calculate volume
    if method.lower() == "simpson":
        volume = integrate_simpson(x, a)
    elif method.lower() == "trapezoidal":
        volume = integrate_trapezoidal(x, a)
    else:
        raise ValueError(
            f"Unknown integration method: {method}. " f"Use 'simpson' or 'trapezoidal'."
        )

    if volume <= 0:
        raise ValueError(
            f"Calculated volume is {volume:.6f} m³. "
            f"Volume must be positive to calculate center of buoyancy."
        )

    # Calculate first moments (integrate area × coordinate)
    if method.lower() == "simpson":
        moment_x = integrate_simpson(x, a * x)  # Longitudinal moment
        moment_y = integrate_simpson(x, a * y_c)  # Transverse moment
        moment_z = integrate_simpson(x, a * z_c)  # Vertical moment
    else:
        moment_x = integrate_trapezoidal(x, a * x)
        moment_y = integrate_trapezoidal(x, a * y_c)
        moment_z = integrate_trapezoidal(x, a * z_c)

    # Calculate centroid coordinates (moment / volume)
    lcb = moment_x / volume
    tcb = moment_y / volume
    vcb = moment_z / volume

    return CenterOfBuoyancy(
        lcb=lcb,
        vcb=vcb,
        tcb=tcb,
        volume=volume,
        waterline_z=waterline_z,
        heel_angle=heel_angle,
        num_stations=len(stations),
        integration_method=method,
    )


def calculate_cb_curve(
    hull: KayakHull,
    waterlines: List[float],
    heel_angle: float = 0.0,
    num_stations: Optional[int] = None,
    method: str = "simpson",
    use_existing_stations: bool = True,
) -> List[CenterOfBuoyancy]:
    """
    Calculate center of buoyancy at multiple waterline positions.

    This function is useful for analyzing how CB moves with draft/waterline.

    Args:
        hull: KayakHull object
        waterlines: List of waterline z-coordinates
        heel_angle: Heel angle in degrees (default: 0.0)
        num_stations: Number of stations for integration
        method: Integration method ('simpson' or 'trapezoidal')
        use_existing_stations: Whether to use hull's existing stations

    Returns:
        List of CenterOfBuoyancy objects, one for each waterline

    Example:
        >>> waterlines = [-0.3, -0.2, -0.1, 0.0]
        >>> cb_curve = calculate_cb_curve(hull, waterlines)
        >>> for wl, cb in zip(waterlines, cb_curve):
        ...     print(f"WL {wl:.2f}: LCB={cb.lcb:.3f}, VCB={cb.vcb:.3f}")
    """
    results = []

    for wl in waterlines:
        try:
            cb = calculate_center_of_buoyancy(
                hull,
                waterline_z=wl,
                heel_angle=heel_angle,
                num_stations=num_stations,
                method=method,
                use_existing_stations=use_existing_stations,
            )
            results.append(cb)
        except ValueError:
            # Handle cases where volume might be zero at certain waterlines
            # Create a CB object with NaN values
            cb = CenterOfBuoyancy(
                lcb=np.nan,
                vcb=np.nan,
                tcb=np.nan,
                volume=0.0,
                waterline_z=wl,
                heel_angle=heel_angle,
                num_stations=num_stations or len(hull.get_stations()),
                integration_method=method,
            )
            results.append(cb)

    return results


def calculate_cb_at_heel_angles(
    hull: KayakHull,
    heel_angles: List[float],
    waterline_z: float = 0.0,
    num_stations: Optional[int] = None,
    method: str = "simpson",
    use_existing_stations: bool = True,
) -> List[CenterOfBuoyancy]:
    """
    Calculate center of buoyancy at multiple heel angles.

    This function is useful for stability analysis, showing how CB moves
    with heel angle. The transverse position (TCB) is particularly important
    for stability calculations.

    Args:
        hull: KayakHull object
        heel_angles: List of heel angles in degrees
        waterline_z: Z-coordinate of the waterline (default: 0.0)
        num_stations: Number of stations for integration
        method: Integration method ('simpson' or 'trapezoidal')
        use_existing_stations: Whether to use hull's existing stations

    Returns:
        List of CenterOfBuoyancy objects, one for each heel angle

    Example:
        >>> heel_angles = [0, 5, 10, 15, 20]
        >>> cb_at_heels = calculate_cb_at_heel_angles(hull, heel_angles)
        >>> for angle, cb in zip(heel_angles, cb_at_heels):
        ...     print(f"Heel {angle}°: TCB={cb.tcb:.3f} m")
    """
    results = []

    for angle in heel_angles:
        cb = calculate_center_of_buoyancy(
            hull,
            waterline_z=waterline_z,
            heel_angle=angle,
            num_stations=num_stations,
            method=method,
            use_existing_stations=use_existing_stations,
        )
        results.append(cb)

    return results


def validate_center_of_buoyancy(
    cb: CenterOfBuoyancy, hull: Optional[KayakHull] = None, tolerance: float = 1e-6
) -> Tuple[bool, List[str]]:
    """
    Validate center of buoyancy calculation results.

    Checks for:
    - Finite CB coordinates
    - Positive volume
    - CB within reasonable bounds relative to hull
    - TCB near zero for upright symmetric hulls

    Args:
        cb: CenterOfBuoyancy object to validate
        hull: Optional KayakHull for bounds checking
        tolerance: Tolerance for numerical checks

    Returns:
        Tuple of (is_valid, list_of_issues)

    Example:
        >>> cb = calculate_center_of_buoyancy(hull)
        >>> is_valid, issues = validate_center_of_buoyancy(cb, hull)
        >>> if not is_valid:
        ...     for issue in issues:
        ...         print(f"Warning: {issue}")
    """
    issues = []

    # Check for finite values
    if not np.isfinite(cb.lcb):
        issues.append(f"Non-finite LCB: {cb.lcb}")

    if not np.isfinite(cb.vcb):
        issues.append(f"Non-finite VCB: {cb.vcb}")

    if not np.isfinite(cb.tcb):
        issues.append(f"Non-finite TCB: {cb.tcb}")

    # Check volume
    if cb.volume <= tolerance:
        issues.append(f"Volume too small or negative: {cb.volume:.6f} m³")

    # If hull provided, check if CB is within hull bounds
    if hull is not None and len(issues) == 0:  # Only check if no issues so far
        stations = hull.get_stations()
        min_station = min(stations)
        max_station = max(stations)

        # LCB should be within hull length
        if cb.lcb < min_station - tolerance or cb.lcb > max_station + tolerance:
            issues.append(
                f"LCB ({cb.lcb:.3f} m) outside hull bounds "
                f"[{min_station:.3f}, {max_station:.3f}]"
            )

        # For upright condition, TCB should be near zero for symmetric hulls
        if abs(cb.heel_angle) < 1.0:  # Nearly upright
            if abs(cb.tcb) > 0.01:  # More than 1 cm off centerline
                issues.append(
                    f"TCB ({cb.tcb:.4f} m) significantly off centerline "
                    f"for upright condition (expected ~0 for symmetric hull)"
                )

        # VCB should be below waterline (negative z if waterline at z=0)
        if cb.vcb > cb.waterline_z + tolerance:
            issues.append(
                f"VCB ({cb.vcb:.3f} m) above waterline ({cb.waterline_z:.3f} m). "
                f"This is physically impossible."
            )

    # Check heel angle range
    if abs(cb.heel_angle) > 90 + tolerance:
        issues.append(f"Heel angle out of range: {cb.heel_angle}°")

    # Check number of stations
    if cb.num_stations < 2:
        issues.append(f"Too few stations: {cb.num_stations}")

    is_valid = len(issues) == 0
    return is_valid, issues
