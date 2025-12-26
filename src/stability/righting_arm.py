"""
Righting arm (GZ) calculations for stability analysis.

This module provides functionality for calculating the righting arm (GZ),
which is the horizontal distance between the center of gravity (CG) and
the center of buoyancy (CB) when the hull is heeled. The GZ curve is
fundamental to static stability analysis.

Physical Background:
- The righting arm GZ represents the moment arm of the restoring moment
- Restoring moment = Displacement × g × GZ
- Positive GZ indicates a righting (restoring) moment
- Negative GZ indicates a capsizing moment
- The GZ curve (GZ vs heel angle) characterizes stability

Mathematical Formulation:
When heeled by angle φ:
- CG remains fixed in space
- CB moves as the shape of the immersed volume changes
- GZ is the horizontal distance between the vertical lines through CG and CB

In the heeled coordinate system:
- GZ = TCB_heeled - TCG_heeled
- where TCG_heeled = TCG × cos(φ) + VCG × sin(φ)

References:
- Rawson, K. J., & Tupper, E. C. (2001). Basic ship theory (5th ed.).
- Principles of Naval Architecture (SNAME)
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
import numpy as np

from ..geometry import KayakHull
from ..hydrostatics import CenterOfBuoyancy, CenterOfGravity, calculate_center_of_buoyancy


@dataclass
class RightingArm:
    """
    Righting arm (GZ) calculation result for a single heel angle.

    The righting arm is the horizontal distance between the center of gravity
    and the center of buoyancy when heeled. It represents the moment arm
    through which the buoyant force creates a restoring (or capsizing) moment.

    Attributes:
        gz: Righting arm in meters (positive = righting moment)
        heel_angle: Heel angle in degrees
        cb: Center of buoyancy at this heel angle
        waterline_z: Z-coordinate of the waterline
        cg_lcg: Longitudinal CG position (for reference)
        cg_vcg: Vertical CG position (for reference)
        cg_tcg: Transverse CG position (for reference)

    Properties:
        righting_moment: Restoring moment per unit weight (same as gz)
        is_stable: True if GZ > 0 (righting moment)

    Note:
        - Positive GZ: stable (righting moment exists)
        - Zero GZ: neutral equilibrium
        - Negative GZ: unstable (capsizing moment)
    """

    gz: float
    heel_angle: float
    cb: CenterOfBuoyancy
    waterline_z: float
    cg_lcg: float
    cg_vcg: float
    cg_tcg: float

    @property
    def righting_moment(self) -> float:
        """
        Righting moment per unit weight.

        The actual moment is: M = Δ × g × GZ
        where Δ is displacement mass and g is gravitational acceleration.

        Returns:
            Righting moment arm (same as gz)
        """
        return self.gz

    @property
    def is_stable(self) -> bool:
        """Check if the heel angle is in stable region (GZ > 0)."""
        return self.gz > 0

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"RightingArm(\n"
            f"  heel_angle={self.heel_angle:.2f}°,\n"
            f"  GZ={self.gz:.6f} m,\n"
            f"  stable={self.is_stable},\n"
            f"  CB=(LCB={self.cb.lcb:.4f}, VCB={self.cb.vcb:.4f}, TCB={self.cb.tcb:.4f}),\n"
            f"  CG=(LCG={self.cg_lcg:.4f}, VCG={self.cg_vcg:.4f}, TCG={self.cg_tcg:.4f})\n"
            f")"
        )


@dataclass
class StabilityCurve:
    """
    Complete GZ curve with multiple heel angles.

    Contains the full stability curve (GZ vs heel angle) and associated data.
    This is the primary output of stability analysis.

    Attributes:
        heel_angles: Array of heel angles in degrees
        gz_values: Array of GZ values in meters (same length as heel_angles)
        cb_values: List of CenterOfBuoyancy objects at each heel angle
        waterline_z: Z-coordinate of the waterline
        cg: Center of gravity used for calculation
        num_stations: Number of stations used for integration
        integration_method: Integration method ('simpson' or 'trapezoidal')

    Properties:
        max_gz: Maximum GZ value
        angle_of_max_gz: Heel angle at which maximum GZ occurs
        range_of_positive_stability: Tuple of (min_angle, max_angle) where GZ > 0
    """

    heel_angles: np.ndarray
    gz_values: np.ndarray
    cb_values: List[CenterOfBuoyancy]
    waterline_z: float
    cg: CenterOfGravity
    num_stations: int = 0
    integration_method: str = "simpson"

    def __post_init__(self):
        """Validate data after initialization."""
        if len(self.heel_angles) != len(self.gz_values):
            raise ValueError(
                f"Mismatch: {len(self.heel_angles)} heel angles "
                f"but {len(self.gz_values)} GZ values"
            )

        if len(self.heel_angles) != len(self.cb_values):
            raise ValueError(
                f"Mismatch: {len(self.heel_angles)} heel angles "
                f"but {len(self.cb_values)} CB values"
            )

        # Convert to numpy arrays if not already
        self.heel_angles = np.asarray(self.heel_angles)
        self.gz_values = np.asarray(self.gz_values)

    @property
    def max_gz(self) -> float:
        """Maximum GZ value in the curve."""
        return float(np.max(self.gz_values))

    @property
    def angle_of_max_gz(self) -> float:
        """Heel angle (degrees) at which maximum GZ occurs."""
        idx = np.argmax(self.gz_values)
        return float(self.heel_angles[idx])

    @property
    def range_of_positive_stability(self) -> Tuple[float, float]:
        """
        Range of heel angles where GZ > 0.

        Returns:
            Tuple of (min_angle, max_angle) where GZ is positive.
            If GZ is never positive, returns (np.nan, np.nan).
        """
        positive_indices = np.where(self.gz_values > 0)[0]

        if len(positive_indices) == 0:
            return (np.nan, np.nan)

        min_idx = positive_indices[0]
        max_idx = positive_indices[-1]

        # Interpolate to find more precise zero crossings
        min_angle = self._interpolate_zero_crossing(min_idx, forward=False)
        max_angle = self._interpolate_zero_crossing(max_idx, forward=True)

        return (min_angle, max_angle)

    def _interpolate_zero_crossing(self, idx: int, forward: bool) -> float:
        """
        Interpolate to find zero crossing near given index.

        Args:
            idx: Index near zero crossing
            forward: If True, look forward; if False, look backward

        Returns:
            Interpolated angle where GZ crosses zero
        """
        if forward:
            if idx >= len(self.gz_values) - 1:
                return float(self.heel_angles[idx])

            # Interpolate between idx and idx+1
            if self.gz_values[idx] > 0 and self.gz_values[idx + 1] <= 0:
                # Found zero crossing
                angle1, gz1 = self.heel_angles[idx], self.gz_values[idx]
                angle2, gz2 = self.heel_angles[idx + 1], self.gz_values[idx + 1]

                if gz1 != gz2:
                    # Linear interpolation
                    angle_zero = angle1 + (0 - gz1) * (angle2 - angle1) / (gz2 - gz1)
                    return float(angle_zero)

            return float(self.heel_angles[idx])
        else:
            if idx <= 0:
                return float(self.heel_angles[idx])

            # Interpolate between idx-1 and idx
            if self.gz_values[idx - 1] <= 0 and self.gz_values[idx] > 0:
                # Found zero crossing
                angle1, gz1 = self.heel_angles[idx - 1], self.gz_values[idx - 1]
                angle2, gz2 = self.heel_angles[idx], self.gz_values[idx]

                if gz1 != gz2:
                    # Linear interpolation
                    angle_zero = angle1 + (0 - gz1) * (angle2 - angle1) / (gz2 - gz1)
                    return float(angle_zero)

            return float(self.heel_angles[idx])

    def get_gz_at_angle(self, angle: float) -> float:
        """
        Get GZ value at specific heel angle by interpolation.

        Args:
            angle: Heel angle in degrees

        Returns:
            Interpolated GZ value
        """
        return float(np.interp(angle, self.heel_angles, self.gz_values))

    def __repr__(self) -> str:
        """String representation."""
        min_angle, max_angle = self.range_of_positive_stability

        return (
            f"StabilityCurve(\n"
            f"  heel_angles: {self.heel_angles[0]:.1f}° to {self.heel_angles[-1]:.1f}° "
            f"({len(self.heel_angles)} points),\n"
            f"  max_GZ={self.max_gz:.6f} m at {self.angle_of_max_gz:.1f}°,\n"
            f"  range_of_positive_stability=({min_angle:.1f}°, {max_angle:.1f}°),\n"
            f"  waterline_z={self.waterline_z:.4f} m,\n"
            f"  CG=(LCG={self.cg.lcg:.4f}, VCG={self.cg.vcg:.4f}, TCG={self.cg.tcg:.4f}),\n"
            f"  num_stations={self.num_stations}\n"
            f")"
        )


@dataclass
class StabilityMetrics:
    """
    Key stability metrics derived from GZ curve.

    These metrics are commonly used to characterize vessel stability
    and compare different designs or loading conditions.

    Attributes:
        max_gz: Maximum GZ value (m)
        angle_of_max_gz: Heel angle at maximum GZ (degrees)
        angle_of_vanishing_stability: Angle where GZ returns to zero (degrees)
        range_of_positive_stability: Range of angles where GZ > 0 (degrees)
        gm_estimate: Estimated metacentric height from initial slope (m)
        area_under_curve: Area under GZ curve (dynamic stability, m·rad)
        waterline_z: Waterline position (m)
        cg_position: Tuple of (lcg, vcg, tcg)

    Note:
        - GM estimate is calculated from the initial slope: GM ≈ GZ / sin(φ) for small φ
        - Area under curve represents dynamic stability (energy to heel)
        - Angle of vanishing stability is important for capsize resistance
    """

    max_gz: float
    angle_of_max_gz: float
    angle_of_vanishing_stability: float
    range_of_positive_stability: Tuple[float, float]
    gm_estimate: Optional[float] = None
    area_under_curve: Optional[float] = None
    waterline_z: float = 0.0
    cg_position: Tuple[float, float, float] = (0.0, 0.0, 0.0)

    def __repr__(self) -> str:
        """String representation."""
        min_angle, max_angle = self.range_of_positive_stability
        gm_str = f"{self.gm_estimate:.6f} m" if self.gm_estimate is not None else "N/A"
        area_str = (
            f"{self.area_under_curve:.6f} m·rad" if self.area_under_curve is not None else "N/A"
        )

        return (
            f"StabilityMetrics(\n"
            f"  max_GZ={self.max_gz:.6f} m at {self.angle_of_max_gz:.2f}°,\n"
            f"  angle_of_vanishing_stability={self.angle_of_vanishing_stability:.2f}°,\n"
            f"  range_of_positive_stability=({min_angle:.2f}°, {max_angle:.2f}°),\n"
            f"  GM_estimate={gm_str},\n"
            f"  area_under_curve={area_str},\n"
            f"  waterline_z={self.waterline_z:.4f} m,\n"
            f"  CG_position={self.cg_position}\n"
            f")"
        )


def calculate_gz(
    hull: KayakHull,
    cg: CenterOfGravity,
    waterline_z: float = 0.0,
    heel_angle: float = 0.0,
    num_stations: Optional[int] = None,
    method: str = "simpson",
    use_existing_stations: bool = True,
) -> RightingArm:
    """
    Calculate righting arm (GZ) at a specific heel angle.

    The righting arm is the horizontal distance between the center of gravity
    and the center of buoyancy when the hull is heeled. It determines the
    magnitude of the restoring moment.

    Mathematical formulation:
        When heeled by angle φ:
        - TCG_heeled = TCG × cos(φ) + VCG × sin(φ)
        - GZ = TCB_heeled - TCG_heeled

    where TCB_heeled is the transverse position of CB in the heeled coordinate
    system, calculated by integrate_center_of_buoyancy with the heel angle.

    Args:
        hull: KayakHull object with defined profiles
        cg: CenterOfGravity object with CG position
        waterline_z: Z-coordinate of the waterline (default: 0.0)
        heel_angle: Heel angle in degrees (default: 0.0)
        num_stations: Number of stations to use for integration
        method: Integration method ('simpson' or 'trapezoidal')
        use_existing_stations: If True, uses hull's existing stations

    Returns:
        RightingArm object with GZ value and associated data

    Example:
        >>> hull = create_kayak_hull()
        >>> cg = CenterOfGravity(lcg=2.5, vcg=0.3, tcg=0.0, total_mass=100.0)
        >>> ra = calculate_gz(hull, cg, waterline_z=0.0, heel_angle=30.0)
        >>> print(f"GZ at 30°: {ra.gz:.4f} m")

    Raises:
        ValueError: If hull has insufficient profiles
        ValueError: If calculated volume is zero or negative

    Note:
        - For upright symmetric hulls with CG on centerline, GZ at 0° should be ≈0
        - GZ typically increases with heel angle initially, then decreases
        - Maximum GZ usually occurs between 30° and 60° for typical hulls
    """
    # Calculate center of buoyancy at heeled condition
    cb = calculate_center_of_buoyancy(
        hull=hull,
        waterline_z=waterline_z,
        heel_angle=heel_angle,
        num_stations=num_stations,
        method=method,
        use_existing_stations=use_existing_stations,
    )

    # Transform CG to heeled coordinate system
    # In heeled frame, CG's transverse position is:
    # y_g_heeled = y_g × cos(φ) + z_g × sin(φ)
    phi_rad = np.deg2rad(heel_angle)
    tcg_heeled = cg.tcg * np.cos(phi_rad) + cg.vcg * np.sin(phi_rad)

    # Calculate righting arm
    # GZ is the horizontal (transverse in heeled frame) distance from CG to CB
    # Positive GZ means CB is outboard of CG (restoring moment)
    # When heeling to starboard (positive angle), CB moves to starboard
    # GZ = distance from CG to CB = TCB - TCG
    gz = cb.tcb - tcg_heeled

    return RightingArm(
        gz=gz,
        heel_angle=heel_angle,
        cb=cb,
        waterline_z=waterline_z,
        cg_lcg=cg.lcg,
        cg_vcg=cg.vcg,
        cg_tcg=cg.tcg,
    )


def calculate_gz_curve(
    hull: KayakHull,
    cg: CenterOfGravity,
    waterline_z: float = 0.0,
    heel_angles: Optional[np.ndarray] = None,
    num_stations: Optional[int] = None,
    method: str = "simpson",
    use_existing_stations: bool = True,
) -> StabilityCurve:
    """
    Calculate complete GZ curve for range of heel angles.

    This is the primary function for generating stability curves. It calculates
    GZ at multiple heel angles to create the complete stability characteristic.

    Args:
        hull: KayakHull object with defined profiles
        cg: CenterOfGravity object with CG position
        waterline_z: Z-coordinate of the waterline (default: 0.0)
        heel_angles: Array of heel angles in degrees
                     If None, uses default range: 0° to 90° in 5° steps
        num_stations: Number of stations to use for integration
        method: Integration method ('simpson' or 'trapezoidal')
        use_existing_stations: If True, uses hull's existing stations

    Returns:
        StabilityCurve object with complete GZ curve data

    Example:
        >>> hull = create_kayak_hull()
        >>> cg = CenterOfGravity(lcg=2.5, vcg=0.3, tcg=0.0, total_mass=100.0)
        >>> curve = calculate_gz_curve(hull, cg, waterline_z=0.0)
        >>> print(f"Max GZ: {curve.max_gz:.4f} m at {curve.angle_of_max_gz:.1f}°")

    Raises:
        ValueError: If hull has insufficient profiles

    Note:
        - Default range is 0° to 90° which covers most practical scenarios
        - For very stable hulls, may want to extend to 120° or 180°
        - Finer angle spacing (e.g., 1° or 2°) gives smoother curves
    """
    # Set default heel angles if not provided
    if heel_angles is None:
        heel_angles = np.arange(0, 91, 5)  # 0° to 90° in 5° steps
    else:
        heel_angles = np.asarray(heel_angles)

    # Calculate GZ for each heel angle
    gz_values = []
    cb_values = []

    for angle in heel_angles:
        ra = calculate_gz(
            hull=hull,
            cg=cg,
            waterline_z=waterline_z,
            heel_angle=angle,
            num_stations=num_stations,
            method=method,
            use_existing_stations=use_existing_stations,
        )
        gz_values.append(ra.gz)
        cb_values.append(ra.cb)

    # Determine number of stations from first calculation
    num_stations_used = cb_values[0].num_stations if cb_values else 0

    return StabilityCurve(
        heel_angles=heel_angles,
        gz_values=np.array(gz_values),
        cb_values=cb_values,
        waterline_z=waterline_z,
        cg=cg,
        num_stations=num_stations_used,
        integration_method=method,
    )


def analyze_stability(
    curve: StabilityCurve, estimate_gm: bool = True, calculate_area: bool = True
) -> StabilityMetrics:
    """
    Extract key stability metrics from GZ curve.

    Analyzes the stability curve to determine important characteristics such as
    maximum GZ, range of positive stability, and metacentric height estimate.

    Args:
        curve: StabilityCurve object with GZ data
        estimate_gm: If True, estimate GM from initial slope
        calculate_area: If True, calculate area under GZ curve

    Returns:
        StabilityMetrics object with derived parameters

    Example:
        >>> curve = calculate_gz_curve(hull, cg, waterline_z=0.0)
        >>> metrics = analyze_stability(curve)
        >>> print(metrics)

    Note:
        - GM estimate uses the slope at small angles: GM ≈ GZ / sin(φ)
        - Area under curve represents dynamic stability (energy required to heel)
        - These metrics are useful for comparing different designs or loadings
    """
    # Get basic properties from curve
    max_gz = curve.max_gz
    angle_of_max_gz = curve.angle_of_max_gz
    min_angle, max_angle = curve.range_of_positive_stability
    angle_of_vanishing = max_angle

    # Estimate metacentric height (GM) from initial slope
    gm_estimate = None
    if estimate_gm:
        # Use GZ at small angle (5° to 10°) to estimate GM
        # GM ≈ GZ / sin(φ) for small φ
        small_angles = curve.heel_angles[(curve.heel_angles >= 5) & (curve.heel_angles <= 10)]

        if len(small_angles) > 0:
            # Use first suitable angle
            idx = np.where(curve.heel_angles == small_angles[0])[0][0]
            angle_rad = np.deg2rad(curve.heel_angles[idx])
            gz_value = curve.gz_values[idx]

            if abs(np.sin(angle_rad)) > 1e-10:
                gm_estimate = gz_value / np.sin(angle_rad)

    # Calculate area under GZ curve (dynamic stability)
    area = None
    if calculate_area:
        # Convert angles to radians for integration
        angles_rad = np.deg2rad(curve.heel_angles)

        # Integrate GZ curve using trapezoidal rule
        # Only integrate positive portion
        positive_mask = curve.gz_values > 0
        if np.any(positive_mask):
            angles_positive = angles_rad[positive_mask]
            gz_positive = curve.gz_values[positive_mask]
            # Use np.trapezoid (np.trapz deprecated in NumPy 2.0)
            try:
                area = np.trapezoid(gz_positive, angles_positive)
            except AttributeError:
                # Fallback for older NumPy versions
                area = np.trapz(gz_positive, angles_positive)

    # Get CG position
    cg_position = (curve.cg.lcg, curve.cg.vcg, curve.cg.tcg)

    return StabilityMetrics(
        max_gz=max_gz,
        angle_of_max_gz=angle_of_max_gz,
        angle_of_vanishing_stability=angle_of_vanishing,
        range_of_positive_stability=(min_angle, max_angle),
        gm_estimate=gm_estimate,
        area_under_curve=area,
        waterline_z=curve.waterline_z,
        cg_position=cg_position,
    )


def calculate_stability_at_multiple_waterlines(
    hull: KayakHull,
    cg: CenterOfGravity,
    waterlines: List[float],
    heel_angles: Optional[np.ndarray] = None,
    num_stations: Optional[int] = None,
    method: str = "simpson",
) -> List[StabilityCurve]:
    """
    Calculate GZ curves at multiple waterline positions.

    Useful for analyzing how stability changes with loading/displacement.

    Args:
        hull: KayakHull object
        cg: CenterOfGravity object
        waterlines: List of waterline z-coordinates
        heel_angles: Array of heel angles (optional)
        num_stations: Number of stations for integration
        method: Integration method

    Returns:
        List of StabilityCurve objects, one for each waterline

    Example:
        >>> waterlines = [-0.2, -0.1, 0.0, 0.1]
        >>> curves = calculate_stability_at_multiple_waterlines(
        ...     hull, cg, waterlines
        ... )
        >>> for wl, curve in zip(waterlines, curves):
        ...     print(f"WL={wl:.2f}: max GZ={curve.max_gz:.4f} m")
    """
    curves = []

    for wl in waterlines:
        curve = calculate_gz_curve(
            hull=hull,
            cg=cg,
            waterline_z=wl,
            heel_angles=heel_angles,
            num_stations=num_stations,
            method=method,
        )
        curves.append(curve)

    return curves
