"""
Stability criteria and standards for kayak/small vessel assessment.

This module implements various stability criteria used to evaluate
the safety and seaworthiness of small vessels. These criteria are
adapted from:
- IMO stability standards (adapted for small craft)
- ISO 12217 (Small craft stability and buoyancy assessment)
- General naval architecture principles

The criteria help determine if a kayak has adequate stability
characteristics for safe operation.
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

from .righting_arm import StabilityCurve, StabilityMetrics


class CriteriaResult(Enum):
    """Result of a stability criteria check."""

    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    NOT_APPLICABLE = "N/A"


@dataclass
class CriteriaCheck:
    """
    Result of a single stability criterion check.

    Attributes:
        name: Name of the criterion
        description: Description of what is being checked
        result: Pass/Fail/Warning/N/A status
        measured_value: Actual measured value
        required_value: Required value or threshold
        units: Units of measurement
        details: Additional details or explanation
    """

    name: str
    description: str
    result: CriteriaResult
    measured_value: Optional[float] = None
    required_value: Optional[float] = None
    units: str = ""
    details: str = ""

    def __repr__(self) -> str:
        """String representation."""
        value_str = f"{self.measured_value:.4f}" if self.measured_value is not None else "N/A"
        req_str = f"{self.required_value:.4f}" if self.required_value is not None else "N/A"

        return (
            f"CriteriaCheck(\n"
            f"  name='{self.name}',\n"
            f"  result={self.result.value},\n"
            f"  measured={value_str} {self.units},\n"
            f"  required={req_str} {self.units},\n"
            f"  details='{self.details}'\n"
            f")"
        )


@dataclass
class StabilityAssessment:
    """
    Complete stability assessment with all criteria checks.

    Attributes:
        criteria_checks: List of individual criterion checks
        overall_result: Overall pass/fail/warning status
        summary: Text summary of assessment
        recommendations: List of recommendations for improvement
    """

    criteria_checks: List[CriteriaCheck]
    overall_result: CriteriaResult
    summary: str
    recommendations: List[str]

    def get_passed_checks(self) -> List[CriteriaCheck]:
        """Get list of passed checks."""
        return [c for c in self.criteria_checks if c.result == CriteriaResult.PASS]

    def get_failed_checks(self) -> List[CriteriaCheck]:
        """Get list of failed checks."""
        return [c for c in self.criteria_checks if c.result == CriteriaResult.FAIL]

    def get_warning_checks(self) -> List[CriteriaCheck]:
        """Get list of warning checks."""
        return [c for c in self.criteria_checks if c.result == CriteriaResult.WARNING]

    def __repr__(self) -> str:
        """String representation."""
        passed = len(self.get_passed_checks())
        failed = len(self.get_failed_checks())
        warnings = len(self.get_warning_checks())

        return (
            f"StabilityAssessment(\n"
            f"  overall_result={self.overall_result.value},\n"
            f"  checks: {passed} passed, {failed} failed, {warnings} warnings,\n"
            f"  summary='{self.summary}'\n"
            f")"
        )


class StabilityCriteria:
    """
    Stability criteria evaluation for kayaks and small vessels.

    This class implements various stability criteria adapted for
    recreational kayaks. The criteria are based on general small craft
    standards but adjusted for typical kayak characteristics.

    Criteria Categories:
    1. Initial Stability (GM)
    2. Maximum GZ Angle and Value
    3. Range of Positive Stability
    4. Dynamic Stability (Area under curve)
    5. Vanishing Stability Angle

    Note: These criteria are guidelines and may need adjustment
    based on specific vessel type and intended use.
    """

    # Default criterion thresholds for recreational kayaks
    # These can be overridden when creating an instance

    DEFAULT_MIN_GM = 0.05  # Minimum GM in meters (5 cm)
    DEFAULT_MIN_MAX_GZ = 0.15  # Minimum maximum GZ in meters (15 cm)
    DEFAULT_MIN_ANGLE_OF_MAX_GZ = 25.0  # Minimum angle of max GZ in degrees
    DEFAULT_MIN_RANGE_POSITIVE = 50.0  # Minimum range of positive stability in degrees
    DEFAULT_MIN_VANISHING_ANGLE = 70.0  # Minimum vanishing angle in degrees
    DEFAULT_MIN_DYNAMIC_STABILITY = 0.05  # Minimum area under curve (m·rad)

    def __init__(
        self,
        min_gm: float = DEFAULT_MIN_GM,
        min_max_gz: float = DEFAULT_MIN_MAX_GZ,
        min_angle_of_max_gz: float = DEFAULT_MIN_ANGLE_OF_MAX_GZ,
        min_range_positive: float = DEFAULT_MIN_RANGE_POSITIVE,
        min_vanishing_angle: float = DEFAULT_MIN_VANISHING_ANGLE,
        min_dynamic_stability: float = DEFAULT_MIN_DYNAMIC_STABILITY,
        strict_mode: bool = False,
    ):
        """
        Initialize stability criteria checker.

        Args:
            min_gm: Minimum acceptable GM (m)
            min_max_gz: Minimum acceptable maximum GZ (m)
            min_angle_of_max_gz: Minimum angle of maximum GZ (degrees)
            min_range_positive: Minimum range of positive stability (degrees)
            min_vanishing_angle: Minimum vanishing stability angle (degrees)
            min_dynamic_stability: Minimum dynamic stability (m·rad)
            strict_mode: If True, warnings become failures
        """
        self.min_gm = min_gm
        self.min_max_gz = min_max_gz
        self.min_angle_of_max_gz = min_angle_of_max_gz
        self.min_range_positive = min_range_positive
        self.min_vanishing_angle = min_vanishing_angle
        self.min_dynamic_stability = min_dynamic_stability
        self.strict_mode = strict_mode

    def check_gm(self, metrics: StabilityMetrics) -> CriteriaCheck:
        """
        Check metacentric height (GM) criterion.

        GM is a measure of initial stability. Positive GM indicates
        stable equilibrium. Higher GM generally means stiffer (more stable)
        but can lead to jerky motion.

        Args:
            metrics: Stability metrics from analysis

        Returns:
            Criteria check result
        """
        if metrics.gm_estimate is None:
            return CriteriaCheck(
                name="Metacentric Height (GM)",
                description="Initial stability measure",
                result=CriteriaResult.NOT_APPLICABLE,
                units="m",
                details="GM could not be estimated from curve",
            )

        gm = metrics.gm_estimate

        if gm < 0:
            result = CriteriaResult.FAIL
            details = "Negative GM indicates unstable equilibrium"
        elif gm < self.min_gm:
            result = CriteriaResult.FAIL if self.strict_mode else CriteriaResult.WARNING
            details = f"GM below minimum threshold of {self.min_gm:.3f} m"
        else:
            result = CriteriaResult.PASS
            details = "GM meets minimum requirement for initial stability"

        return CriteriaCheck(
            name="Metacentric Height (GM)",
            description="Initial stability measure",
            result=result,
            measured_value=gm,
            required_value=self.min_gm,
            units="m",
            details=details,
        )

    def check_max_gz(self, metrics: StabilityMetrics) -> CriteriaCheck:
        """
        Check maximum GZ criterion.

        Maximum GZ represents the peak righting moment available.
        Higher values indicate greater stability at moderate heel angles.

        Args:
            metrics: Stability metrics from analysis

        Returns:
            Criteria check result
        """
        max_gz = metrics.max_gz

        if max_gz < 0:
            result = CriteriaResult.FAIL
            details = "Negative maximum GZ indicates capsizing tendency"
        elif max_gz < self.min_max_gz:
            result = CriteriaResult.FAIL if self.strict_mode else CriteriaResult.WARNING
            details = f"Maximum GZ below minimum of {self.min_max_gz:.3f} m"
        else:
            result = CriteriaResult.PASS
            details = "Maximum GZ meets minimum requirement"

        return CriteriaCheck(
            name="Maximum GZ",
            description="Peak righting arm value",
            result=result,
            measured_value=max_gz,
            required_value=self.min_max_gz,
            units="m",
            details=details,
        )

    def check_angle_of_max_gz(self, metrics: StabilityMetrics) -> CriteriaCheck:
        """
        Check angle of maximum GZ criterion.

        The angle at which maximum GZ occurs should not be too small.
        If max GZ occurs at very small angles, stability deteriorates
        quickly at larger heel angles.

        Args:
            metrics: Stability metrics from analysis

        Returns:
            Criteria check result
        """
        angle = metrics.angle_of_max_gz

        if angle < self.min_angle_of_max_gz:
            result = CriteriaResult.FAIL if self.strict_mode else CriteriaResult.WARNING
            details = f"Max GZ angle below minimum of {self.min_angle_of_max_gz:.1f}°"
        else:
            result = CriteriaResult.PASS
            details = "Max GZ occurs at acceptable heel angle"

        return CriteriaCheck(
            name="Angle of Maximum GZ",
            description="Heel angle at peak righting moment",
            result=result,
            measured_value=angle,
            required_value=self.min_angle_of_max_gz,
            units="degrees",
            details=details,
        )

    def check_range_of_positive_stability(self, metrics: StabilityMetrics) -> CriteriaCheck:
        """
        Check range of positive stability criterion.

        The range of angles over which GZ is positive indicates
        the vessel's resistance to capsizing. Wider range is better.

        Args:
            metrics: Stability metrics from analysis

        Returns:
            Criteria check result
        """
        min_angle, max_angle = metrics.range_of_positive_stability
        range_width = max_angle - min_angle

        if range_width < self.min_range_positive:
            result = CriteriaResult.FAIL if self.strict_mode else CriteriaResult.WARNING
            details = (
                f"Range of {range_width:.1f}° is below minimum of {self.min_range_positive:.1f}°"
            )
        else:
            result = CriteriaResult.PASS
            details = f"Positive stability range of {range_width:.1f}° is adequate"

        return CriteriaCheck(
            name="Range of Positive Stability",
            description="Angular range where GZ > 0",
            result=result,
            measured_value=range_width,
            required_value=self.min_range_positive,
            units="degrees",
            details=details,
        )

    def check_vanishing_angle(self, metrics: StabilityMetrics) -> CriteriaCheck:
        """
        Check vanishing stability angle criterion.

        The angle of vanishing stability indicates how far the vessel
        can heel before stability is lost. Larger angles provide more
        safety margin against capsizing.

        Args:
            metrics: Stability metrics from analysis

        Returns:
            Criteria check result
        """
        angle = metrics.angle_of_vanishing_stability

        if angle < self.min_vanishing_angle:
            result = CriteriaResult.FAIL if self.strict_mode else CriteriaResult.WARNING
            details = (
                f"Vanishing angle of {angle:.1f}° is below minimum of "
                f"{self.min_vanishing_angle:.1f}°"
            )
        else:
            result = CriteriaResult.PASS
            details = f"Vanishing angle of {angle:.1f}° provides adequate " f"capsize resistance"

        return CriteriaCheck(
            name="Angle of Vanishing Stability",
            description="Angle where stability is lost",
            result=result,
            measured_value=angle,
            required_value=self.min_vanishing_angle,
            units="degrees",
            details=details,
        )

    def check_dynamic_stability(self, metrics: StabilityMetrics) -> CriteriaCheck:
        """
        Check dynamic stability (area under GZ curve) criterion.

        Dynamic stability represents the energy required to heel the vessel.
        Larger area indicates greater resistance to capsizing from
        dynamic events (waves, wind gusts, etc.).

        Args:
            metrics: Stability metrics from analysis

        Returns:
            Criteria check result
        """
        if metrics.area_under_curve is None:
            return CriteriaCheck(
                name="Dynamic Stability",
                description="Area under GZ curve",
                result=CriteriaResult.NOT_APPLICABLE,
                units="m·rad",
                details="Area under curve was not calculated",
            )

        area = metrics.area_under_curve

        if area < 0:
            result = CriteriaResult.FAIL
            details = "Negative area indicates capsizing tendency"
        elif area < self.min_dynamic_stability:
            result = CriteriaResult.FAIL if self.strict_mode else CriteriaResult.WARNING
            details = (
                f"Area of {area:.4f} m·rad is below minimum of "
                f"{self.min_dynamic_stability:.4f} m·rad"
            )
        else:
            result = CriteriaResult.PASS
            details = f"Dynamic stability of {area:.4f} m·rad is adequate"

        return CriteriaCheck(
            name="Dynamic Stability",
            description="Area under GZ curve",
            result=result,
            measured_value=area,
            required_value=self.min_dynamic_stability,
            units="m·rad",
            details=details,
        )

    def assess_stability(
        self, metrics: StabilityMetrics, curve: Optional[StabilityCurve] = None
    ) -> StabilityAssessment:
        """
        Perform complete stability assessment against all criteria.

        Args:
            metrics: Stability metrics from analysis
            curve: Optional stability curve (for future detailed checks)

        Returns:
            Complete stability assessment with all checks
        """
        # Run all criterion checks
        checks = [
            self.check_gm(metrics),
            self.check_max_gz(metrics),
            self.check_angle_of_max_gz(metrics),
            self.check_range_of_positive_stability(metrics),
            self.check_vanishing_angle(metrics),
            self.check_dynamic_stability(metrics),
        ]

        # Determine overall result
        failed = [c for c in checks if c.result == CriteriaResult.FAIL]
        warnings = [c for c in checks if c.result == CriteriaResult.WARNING]

        if failed:
            overall_result = CriteriaResult.FAIL
        elif warnings:
            overall_result = CriteriaResult.WARNING
        else:
            overall_result = CriteriaResult.PASS

        # Create summary
        passed_count = len([c for c in checks if c.result == CriteriaResult.PASS])
        total_count = len([c for c in checks if c.result != CriteriaResult.NOT_APPLICABLE])

        if overall_result == CriteriaResult.PASS:
            summary = f"Passed all {passed_count}/{total_count} applicable stability criteria"
        elif overall_result == CriteriaResult.WARNING:
            summary = f"Passed {passed_count}/{total_count} criteria with {len(warnings)} warnings"
        else:
            summary = f"Failed {len(failed)}/{total_count} stability criteria"

        # Generate recommendations
        recommendations = self._generate_recommendations(checks, metrics)

        return StabilityAssessment(
            criteria_checks=checks,
            overall_result=overall_result,
            summary=summary,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self, checks: List[CriteriaCheck], metrics: StabilityMetrics
    ) -> List[str]:
        """
        Generate recommendations based on failed/warning checks.

        Args:
            checks: List of criteria checks
            metrics: Stability metrics

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Check for specific issues and provide targeted advice
        for check in checks:
            if check.result in [CriteriaResult.FAIL, CriteriaResult.WARNING]:
                if check.name == "Metacentric Height (GM)":
                    if metrics.gm_estimate is not None and metrics.gm_estimate < 0:
                        recommendations.append(
                            "CRITICAL: Negative GM - Lower the center of gravity (CG) "
                            "immediately. Current configuration is unstable."
                        )
                    else:
                        recommendations.append(
                            "Consider lowering the center of gravity to improve initial stability. "
                            "Ballast placement or equipment redistribution may help."
                        )

                elif check.name == "Maximum GZ":
                    recommendations.append(
                        "Increase hull beam width or adjust hull form to improve maximum GZ. "
                        "Lowering CG will also increase maximum GZ."
                    )

                elif check.name == "Angle of Maximum GZ":
                    recommendations.append(
                        "Maximum GZ occurs at low heel angle. Consider hull form modifications "
                        "to shift maximum stability to larger angles."
                    )

                elif check.name == "Range of Positive Stability":
                    recommendations.append(
                        "Narrow range of positive stability. Increase hull beam, add flare, "
                        "or lower CG to extend stable range."
                    )

                elif check.name == "Angle of Vanishing Stability":
                    recommendations.append(
                        "Low vanishing angle increases capsize risk. Consider increasing beam, "
                        "adding freeboard, or lowering center of gravity."
                    )

                elif check.name == "Dynamic Stability":
                    recommendations.append(
                        "Low dynamic stability reduces resistance to wave action. "
                        "Increase beam, lower CG, or modify hull sections to improve."
                    )

        # Add general recommendations if no specific issues
        if not recommendations:
            recommendations.append(
                "Stability criteria are met. Continue monitoring with different "
                "loading conditions and waterlines."
            )

        return recommendations

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"StabilityCriteria(\n"
            f"  min_GM={self.min_gm:.4f} m,\n"
            f"  min_max_GZ={self.min_max_gz:.4f} m,\n"
            f"  min_angle_of_max_GZ={self.min_angle_of_max_gz:.1f}°,\n"
            f"  min_range_positive={self.min_range_positive:.1f}°,\n"
            f"  min_vanishing_angle={self.min_vanishing_angle:.1f}°,\n"
            f"  min_dynamic_stability={self.min_dynamic_stability:.4f} m·rad,\n"
            f"  strict_mode={self.strict_mode}\n"
            f")"
        )


def quick_stability_assessment(
    metrics: StabilityMetrics, curve: Optional[StabilityCurve] = None, strict_mode: bool = False
) -> StabilityAssessment:
    """
    Quick stability assessment with default criteria.

    Convenience function for assessing stability without creating
    a StabilityCriteria instance.

    Args:
        metrics: Stability metrics from analysis
        curve: Optional stability curve
        strict_mode: If True, warnings become failures

    Returns:
        Complete stability assessment

    Example:
        >>> from src.stability import analyze_stability, quick_stability_assessment
        >>> metrics = analyze_stability(curve)
        >>> assessment = quick_stability_assessment(metrics)
        >>> print(assessment.summary)
    """
    criteria = StabilityCriteria(strict_mode=strict_mode)
    return criteria.assess_stability(metrics, curve)
