"""
Stability module for stability analysis and GZ curve generation.

This module contains classes and functions for:
- Righting arm (GZ) calculation
- Stability curve generation
- Stability metrics (GM, range of stability, etc.)
- Stability criteria checks and assessment
"""

from .righting_arm import (
    RightingArm,
    StabilityCurve,
    StabilityMetrics,
    calculate_gz,
    calculate_gz_curve,
    analyze_stability,
    calculate_stability_at_multiple_waterlines,
)

from .analyzer import StabilityAnalyzer, quick_stability_analysis

from .criteria import (
    CriteriaResult,
    CriteriaCheck,
    StabilityAssessment,
    StabilityCriteria,
    quick_stability_assessment,
)

__all__ = [
    # Righting arm classes and functions
    "RightingArm",
    "StabilityCurve",
    "StabilityMetrics",
    "calculate_gz",
    "calculate_gz_curve",
    "analyze_stability",
    "calculate_stability_at_multiple_waterlines",
    # Analyzer classes and functions
    "StabilityAnalyzer",
    "quick_stability_analysis",
    # Criteria classes and functions
    "CriteriaResult",
    "CriteriaCheck",
    "StabilityAssessment",
    "StabilityCriteria",
    "quick_stability_assessment",
]
