"""
Stability analyzer class for comprehensive stability analysis.

This module provides a high-level object-oriented interface for stability
analysis. The StabilityAnalyzer class encapsulates hull geometry and CG
position, making it easy to perform multiple stability calculations without
repeatedly passing the same parameters.

The analyzer provides:
- Single heel angle GZ calculation
- Full stability curve generation
- Stability metrics analysis
- Comparison of different configurations
- Convenience methods for common analyses

Example:
    >>> hull = create_kayak_hull()
    >>> cg = CenterOfGravity(lcg=2.5, vcg=-0.3, tcg=0.0, total_mass=100.0)
    >>> analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.2)
    >>>
    >>> # Generate full stability curve
    >>> curve = analyzer.generate_stability_curve()
    >>> print(f"Max GZ: {curve.max_gz:.3f} m")
    >>>
    >>> # Analyze metrics
    >>> metrics = analyzer.analyze_stability()
    >>> print(f"GM: {metrics.gm_estimate:.3f} m")
"""

from typing import Optional, List, Tuple, Dict
import numpy as np

from ..geometry import KayakHull
from ..hydrostatics import CenterOfGravity
from .righting_arm import (
    RightingArm,
    StabilityCurve,
    StabilityMetrics,
    calculate_gz,
    calculate_gz_curve,
    analyze_stability as analyze_stability_curve,
)


class StabilityAnalyzer:
    """
    High-level stability analyzer for kayak hulls.

    This class provides a convenient object-oriented interface for stability
    analysis. It encapsulates the hull geometry, CG position, and waterline,
    allowing you to perform multiple analyses without repeatedly passing
    the same parameters.

    The analyzer maintains state (hull, CG, waterline) and provides methods
    for various stability calculations and analyses.

    Attributes:
        hull: KayakHull object with defined profiles
        cg: CenterOfGravity object with CG position and mass
        waterline_z: Z-coordinate of the waterline (default: 0.0)
        num_stations: Number of stations for integration (None = use hull stations)
        integration_method: Integration method ('simpson' or 'trapezoidal')

    Example:
        >>> hull = create_kayak_hull()
        >>> cg = CenterOfGravity(lcg=2.5, vcg=-0.3, tcg=0.0, total_mass=100.0)
        >>> analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.2)
        >>>
        >>> # Single heel angle
        >>> gz_30 = analyzer.calculate_gz_at_angle(30.0)
        >>> print(f"GZ at 30°: {gz_30:.3f} m")
        >>>
        >>> # Full curve
        >>> curve = analyzer.generate_stability_curve()
        >>> metrics = analyzer.analyze_stability(curve)

    Note:
        - The analyzer is immutable once created (hull, CG, waterline are fixed)
        - To analyze different configurations, create new analyzer instances
        - Use convenience methods for common operations
    """

    def __init__(
        self,
        hull: KayakHull,
        cg: CenterOfGravity,
        waterline_z: float = 0.0,
        num_stations: Optional[int] = None,
        integration_method: str = "simpson",
    ):
        """
        Initialize the stability analyzer.

        Args:
            hull: KayakHull object with defined profiles
            cg: CenterOfGravity object with CG position
            waterline_z: Z-coordinate of the waterline (default: 0.0)
            num_stations: Number of stations for integration (None = use hull stations)
            integration_method: Integration method ('simpson' or 'trapezoidal')

        Raises:
            ValueError: If hull has insufficient profiles
        """
        if len(hull) < 2:
            raise ValueError(
                f"Hull must have at least 2 profiles for stability analysis. "
                f"Got {len(hull)} profile(s)."
            )

        self.hull = hull
        self.cg = cg
        self.waterline_z = waterline_z
        self.num_stations = num_stations
        self.integration_method = integration_method

    def calculate_gz_at_angle(self, heel_angle: float) -> float:
        """
        Calculate GZ (righting arm) at a specific heel angle.

        Args:
            heel_angle: Heel angle in degrees

        Returns:
            GZ value in meters (positive = righting moment)

        Example:
            >>> analyzer = StabilityAnalyzer(hull, cg)
            >>> gz = analyzer.calculate_gz_at_angle(30.0)
            >>> print(f"GZ at 30°: {gz:.3f} m")
        """
        ra = calculate_gz(
            hull=self.hull,
            cg=self.cg,
            waterline_z=self.waterline_z,
            heel_angle=heel_angle,
            num_stations=self.num_stations,
            method=self.integration_method,
        )
        return ra.gz

    def calculate_righting_arm(self, heel_angle: float) -> RightingArm:
        """
        Calculate complete righting arm data at a specific heel angle.

        Returns the full RightingArm object with GZ, CB, and all metadata.

        Args:
            heel_angle: Heel angle in degrees

        Returns:
            RightingArm object with complete data

        Example:
            >>> analyzer = StabilityAnalyzer(hull, cg)
            >>> ra = analyzer.calculate_righting_arm(30.0)
            >>> print(f"GZ: {ra.gz:.3f} m")
            >>> print(f"CB: ({ra.cb.lcb:.3f}, {ra.cb.vcb:.3f}, {ra.cb.tcb:.3f})")
        """
        return calculate_gz(
            hull=self.hull,
            cg=self.cg,
            waterline_z=self.waterline_z,
            heel_angle=heel_angle,
            num_stations=self.num_stations,
            method=self.integration_method,
        )

    def generate_stability_curve(
        self,
        heel_angles: Optional[np.ndarray] = None,
        min_angle: float = 0.0,
        max_angle: float = 90.0,
        angle_step: float = 5.0,
    ) -> StabilityCurve:
        """
        Generate complete stability curve (GZ vs heel angle).

        This is the primary method for generating stability curves. If heel_angles
        is not provided, creates a range from min_angle to max_angle with angle_step.

        Args:
            heel_angles: Array of heel angles (optional, overrides min/max/step)
            min_angle: Minimum heel angle in degrees (default: 0.0)
            max_angle: Maximum heel angle in degrees (default: 90.0)
            angle_step: Step size in degrees (default: 5.0)

        Returns:
            StabilityCurve object with complete curve data

        Example:
            >>> analyzer = StabilityAnalyzer(hull, cg)
            >>>
            >>> # Default: 0° to 90° in 5° steps
            >>> curve = analyzer.generate_stability_curve()
            >>>
            >>> # Custom range: 0° to 60° in 2° steps
            >>> curve = analyzer.generate_stability_curve(
            ...     min_angle=0, max_angle=60, angle_step=2
            ... )
            >>>
            >>> # Specific angles
            >>> curve = analyzer.generate_stability_curve(
            ...     heel_angles=np.array([0, 10, 20, 30, 45, 60, 75, 90])
            ... )
        """
        if heel_angles is None:
            heel_angles = np.arange(min_angle, max_angle + angle_step / 2, angle_step)

        return calculate_gz_curve(
            hull=self.hull,
            cg=self.cg,
            waterline_z=self.waterline_z,
            heel_angles=heel_angles,
            num_stations=self.num_stations,
            method=self.integration_method,
        )

    def analyze_stability(
        self,
        curve: Optional[StabilityCurve] = None,
        estimate_gm: bool = True,
        calculate_area: bool = True,
    ) -> StabilityMetrics:
        """
        Analyze stability and extract key metrics.

        If no curve is provided, generates a default curve (0° to 90° in 5° steps)
        and analyzes it.

        Args:
            curve: StabilityCurve to analyze (optional, will generate if None)
            estimate_gm: Whether to estimate metacentric height (GM)
            calculate_area: Whether to calculate area under curve

        Returns:
            StabilityMetrics object with derived parameters

        Example:
            >>> analyzer = StabilityAnalyzer(hull, cg)
            >>> metrics = analyzer.analyze_stability()
            >>> print(f"Max GZ: {metrics.max_gz:.3f} m")
            >>> print(f"GM: {metrics.gm_estimate:.3f} m")
        """
        if curve is None:
            curve = self.generate_stability_curve()

        return analyze_stability_curve(
            curve=curve, estimate_gm=estimate_gm, calculate_area=calculate_area
        )

    def get_stability_summary(self) -> Dict[str, any]:
        """
        Get a comprehensive stability summary as a dictionary.

        Generates stability curve, analyzes it, and returns all key
        information in a convenient dictionary format.

        Returns:
            Dictionary with stability information:
                - 'curve': StabilityCurve object
                - 'metrics': StabilityMetrics object
                - 'max_gz': Maximum GZ value (m)
                - 'angle_of_max_gz': Angle at max GZ (degrees)
                - 'gm': GM estimate (m), or None
                - 'range_positive': Tuple of (min, max) angles with positive GZ
                - 'vanishing_angle': Angle of vanishing stability (degrees)
                - 'dynamic_stability': Area under curve (m·rad), or None

        Example:
            >>> analyzer = StabilityAnalyzer(hull, cg)
            >>> summary = analyzer.get_stability_summary()
            >>> print(f"Max GZ: {summary['max_gz']:.3f} m")
            >>> print(f"GM: {summary['gm']:.3f} m")
        """
        curve = self.generate_stability_curve()
        metrics = self.analyze_stability(curve)

        return {
            "curve": curve,
            "metrics": metrics,
            "max_gz": metrics.max_gz,
            "angle_of_max_gz": metrics.angle_of_max_gz,
            "gm": metrics.gm_estimate,
            "range_positive": metrics.range_of_positive_stability,
            "vanishing_angle": metrics.angle_of_vanishing_stability,
            "dynamic_stability": metrics.area_under_curve,
        }

    def compare_with_different_cg(
        self, cg_list: List[CenterOfGravity], labels: Optional[List[str]] = None
    ) -> List[Tuple[str, StabilityCurve, StabilityMetrics]]:
        """
        Compare stability with different CG positions.

        Generates stability curves for multiple CG positions and analyzes each.
        Useful for understanding how CG location affects stability.

        Args:
            cg_list: List of CenterOfGravity objects to compare
            labels: Optional list of labels for each CG (default: CG1, CG2, ...)

        Returns:
            List of tuples: (label, curve, metrics) for each CG

        Example:
            >>> analyzer = StabilityAnalyzer(hull, cg)
            >>> cg_low = CenterOfGravity(lcg=2.5, vcg=-0.5, tcg=0.0, total_mass=100)
            >>> cg_high = CenterOfGravity(lcg=2.5, vcg=-0.2, tcg=0.0, total_mass=100)
            >>>
            >>> results = analyzer.compare_with_different_cg(
            ...     [cg_low, cg_high],
            ...     labels=["Low CG", "High CG"]
            ... )
            >>>
            >>> for label, curve, metrics in results:
            ...     print(f"{label}: Max GZ = {metrics.max_gz:.3f} m")
        """
        if labels is None:
            labels = [f"CG{i+1}" for i in range(len(cg_list))]

        results = []
        for cg, label in zip(cg_list, labels):
            # Create temporary analyzer with new CG
            temp_analyzer = StabilityAnalyzer(
                hull=self.hull,
                cg=cg,
                waterline_z=self.waterline_z,
                num_stations=self.num_stations,
                integration_method=self.integration_method,
            )
            curve = temp_analyzer.generate_stability_curve()
            metrics = temp_analyzer.analyze_stability(curve)
            results.append((label, curve, metrics))

        return results

    def compare_with_different_waterlines(
        self, waterlines: List[float], labels: Optional[List[str]] = None
    ) -> List[Tuple[str, StabilityCurve, StabilityMetrics]]:
        """
        Compare stability at different waterlines (drafts).

        Analyzes how stability changes with loading/displacement by varying
        the waterline position.

        Args:
            waterlines: List of waterline z-coordinates
            labels: Optional list of labels (default: WL1, WL2, ...)

        Returns:
            List of tuples: (label, curve, metrics) for each waterline

        Example:
            >>> analyzer = StabilityAnalyzer(hull, cg)
            >>> waterlines = [-0.4, -0.3, -0.2, -0.1]  # Light to heavy
            >>> labels = ["Light", "Medium", "Heavy", "Very Heavy"]
            >>>
            >>> results = analyzer.compare_with_different_waterlines(
            ...     waterlines, labels
            ... )
            >>>
            >>> for label, curve, metrics in results:
            ...     print(f"{label}: Max GZ = {metrics.max_gz:.3f} m")
        """
        if labels is None:
            labels = [f"WL{i+1}" for i in range(len(waterlines))]

        results = []
        for wl, label in zip(waterlines, labels):
            # Create temporary analyzer with new waterline
            temp_analyzer = StabilityAnalyzer(
                hull=self.hull,
                cg=self.cg,
                waterline_z=wl,
                num_stations=self.num_stations,
                integration_method=self.integration_method,
            )
            curve = temp_analyzer.generate_stability_curve()
            metrics = temp_analyzer.analyze_stability(curve)
            results.append((label, curve, metrics))

        return results

    def is_stable_at_angle(self, heel_angle: float, threshold: float = 0.0) -> bool:
        """
        Check if hull is stable at a given heel angle.

        Stability is defined as GZ > threshold (default: 0).

        Args:
            heel_angle: Heel angle in degrees
            threshold: Minimum GZ for stability (default: 0.0)

        Returns:
            True if GZ > threshold, False otherwise

        Example:
            >>> analyzer = StabilityAnalyzer(hull, cg)
            >>> if analyzer.is_stable_at_angle(30.0):
            ...     print("Stable at 30°")
        """
        gz = self.calculate_gz_at_angle(heel_angle)
        return gz > threshold

    def find_maximum_gz(self) -> Tuple[float, float]:
        """
        Find the maximum GZ and the angle at which it occurs.

        Generates a default stability curve and identifies the maximum.

        Returns:
            Tuple of (max_gz, angle_of_max_gz)

        Example:
            >>> analyzer = StabilityAnalyzer(hull, cg)
            >>> max_gz, angle = analyzer.find_maximum_gz()
            >>> print(f"Max GZ = {max_gz:.3f} m at {angle:.1f}°")
        """
        curve = self.generate_stability_curve()
        return curve.max_gz, curve.angle_of_max_gz

    def find_vanishing_stability_angle(self) -> float:
        """
        Find the angle of vanishing stability (where GZ returns to zero).

        This is the maximum heel angle at which positive stability exists.
        Beyond this angle, the vessel will capsize.

        Returns:
            Angle of vanishing stability in degrees

        Example:
            >>> analyzer = StabilityAnalyzer(hull, cg)
            >>> vanishing = analyzer.find_vanishing_stability_angle()
            >>> print(f"Stability vanishes at {vanishing:.1f}°")
        """
        curve = self.generate_stability_curve()
        _, max_angle = curve.range_of_positive_stability
        return max_angle

    def estimate_metacentric_height(self) -> Optional[float]:
        """
        Estimate metacentric height (GM) from initial stability slope.

        GM is estimated from GZ at small angles using: GM ≈ GZ / sin(φ)

        Returns:
            GM estimate in meters, or None if cannot be estimated

        Example:
            >>> analyzer = StabilityAnalyzer(hull, cg)
            >>> gm = analyzer.estimate_metacentric_height()
            >>> if gm is not None:
            ...     print(f"GM ≈ {gm:.3f} m")

        Note:
            - GM is a measure of initial stability
            - Larger GM = stiffer (but potentially uncomfortable)
            - GM is most accurate for small heel angles
        """
        # Generate fine-grained curve for better GM estimate
        curve = self.generate_stability_curve(min_angle=0, max_angle=15, angle_step=1)
        metrics = self.analyze_stability(curve, estimate_gm=True, calculate_area=False)
        return metrics.gm_estimate

    def calculate_dynamic_stability(self) -> Optional[float]:
        """
        Calculate dynamic stability (area under GZ curve).

        Dynamic stability represents the energy required to heel the vessel
        to a given angle. Larger area = more energy = better stability.

        Returns:
            Area under GZ curve in m·rad, or None if cannot be calculated

        Example:
            >>> analyzer = StabilityAnalyzer(hull, cg)
            >>> area = analyzer.calculate_dynamic_stability()
            >>> if area is not None:
            ...     print(f"Dynamic stability: {area:.3f} m·rad")

        Note:
            - Only positive portion of curve is integrated
            - Useful for comparing overall stability of different configurations
        """
        curve = self.generate_stability_curve()
        metrics = self.analyze_stability(curve, estimate_gm=False, calculate_area=True)
        return metrics.area_under_curve

    def __repr__(self) -> str:
        """String representation of the analyzer."""
        return (
            f"StabilityAnalyzer(\n"
            f"  hull=KayakHull(num_profiles={len(self.hull)}),\n"
            f"  cg=CenterOfGravity(lcg={self.cg.lcg:.3f}, "
            f"vcg={self.cg.vcg:.3f}, tcg={self.cg.tcg:.3f}),\n"
            f"  waterline_z={self.waterline_z:.4f},\n"
            f"  method='{self.integration_method}'\n"
            f")"
        )


def quick_stability_analysis(
    hull: KayakHull, cg: CenterOfGravity, waterline_z: float = 0.0
) -> Dict[str, any]:
    """
    Convenience function for quick stability analysis.

    Creates an analyzer and returns a comprehensive stability summary.
    Useful for one-off analyses without creating an analyzer object.

    Args:
        hull: KayakHull object
        cg: CenterOfGravity object
        waterline_z: Z-coordinate of waterline

    Returns:
        Dictionary with stability information (same as get_stability_summary)

    Example:
        >>> hull = create_kayak_hull()
        >>> cg = CenterOfGravity(lcg=2.5, vcg=-0.3, tcg=0.0, total_mass=100)
        >>> summary = quick_stability_analysis(hull, cg, waterline_z=-0.2)
        >>> print(f"Max GZ: {summary['max_gz']:.3f} m")
        >>> print(f"GM: {summary['gm']:.3f} m")
    """
    analyzer = StabilityAnalyzer(hull, cg, waterline_z)
    return analyzer.get_stability_summary()
