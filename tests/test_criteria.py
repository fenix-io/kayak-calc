"""
Tests for stability criteria and assessment.

This test suite validates the stability criteria checking functionality.
"""

import pytest

from src.stability import (
    StabilityMetrics,
    StabilityCriteria,
    CriteriaResult,
    StabilityAssessment,
    quick_stability_assessment,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def good_metrics():
    """Metrics that meet all criteria."""
    return StabilityMetrics(
        max_gz=0.25,
        angle_of_max_gz=35.0,
        angle_of_vanishing_stability=85.0,
        range_of_positive_stability=(5.0, 85.0),
        gm_estimate=0.15,
        area_under_curve=0.15,
        waterline_z=-0.3,
        cg_position=(2.0, -0.3, 0.0),
    )


@pytest.fixture
def poor_metrics():
    """Metrics that fail multiple criteria."""
    return StabilityMetrics(
        max_gz=0.08,  # Too low
        angle_of_max_gz=15.0,  # Too low
        angle_of_vanishing_stability=45.0,  # Too low
        range_of_positive_stability=(10.0, 45.0),  # Too narrow
        gm_estimate=0.02,  # Too low
        area_under_curve=0.02,  # Too low
        waterline_z=-0.3,
        cg_position=(2.0, -0.25, 0.0),
    )


@pytest.fixture
def unstable_metrics():
    """Metrics indicating unstable configuration."""
    return StabilityMetrics(
        max_gz=-0.05,  # Negative
        angle_of_max_gz=10.0,
        angle_of_vanishing_stability=30.0,
        range_of_positive_stability=(0.0, 30.0),
        gm_estimate=-0.10,  # Negative GM
        area_under_curve=-0.01,  # Negative
        waterline_z=-0.3,
        cg_position=(2.0, -0.15, 0.0),
    )


@pytest.fixture
def missing_optional_metrics():
    """Metrics with missing optional values."""
    return StabilityMetrics(
        max_gz=0.20,
        angle_of_max_gz=30.0,
        angle_of_vanishing_stability=75.0,
        range_of_positive_stability=(5.0, 75.0),
        gm_estimate=None,  # Not calculated
        area_under_curve=None,  # Not calculated
        waterline_z=-0.3,
        cg_position=(2.0, -0.3, 0.0),
    )


# ============================================================================
# Test Individual Criterion Checks
# ============================================================================


class TestGMCriterion:
    """Tests for GM criterion check."""

    def test_good_gm(self, good_metrics):
        """Test GM that meets criterion."""
        criteria = StabilityCriteria()
        check = criteria.check_gm(good_metrics)

        assert check.result == CriteriaResult.PASS
        assert check.measured_value == good_metrics.gm_estimate
        assert "meets minimum requirement" in check.details.lower()

    def test_low_gm(self, poor_metrics):
        """Test GM below threshold."""
        criteria = StabilityCriteria()
        check = criteria.check_gm(poor_metrics)

        assert check.result == CriteriaResult.WARNING
        assert check.measured_value == poor_metrics.gm_estimate
        assert "below minimum" in check.details.lower()

    def test_negative_gm(self, unstable_metrics):
        """Test negative GM."""
        criteria = StabilityCriteria()
        check = criteria.check_gm(unstable_metrics)

        assert check.result == CriteriaResult.FAIL
        assert check.measured_value == unstable_metrics.gm_estimate
        assert "negative" in check.details.lower()
        assert "unstable" in check.details.lower()

    def test_missing_gm(self, missing_optional_metrics):
        """Test when GM is not available."""
        criteria = StabilityCriteria()
        check = criteria.check_gm(missing_optional_metrics)

        assert check.result == CriteriaResult.NOT_APPLICABLE
        assert check.measured_value is None

    def test_strict_mode(self, poor_metrics):
        """Test that strict mode converts warnings to failures."""
        criteria = StabilityCriteria(strict_mode=True)
        check = criteria.check_gm(poor_metrics)

        assert check.result == CriteriaResult.FAIL


class TestMaxGZCriterion:
    """Tests for maximum GZ criterion check."""

    def test_good_max_gz(self, good_metrics):
        """Test max GZ that meets criterion."""
        criteria = StabilityCriteria()
        check = criteria.check_max_gz(good_metrics)

        assert check.result == CriteriaResult.PASS
        assert check.measured_value == good_metrics.max_gz

    def test_low_max_gz(self, poor_metrics):
        """Test max GZ below threshold."""
        criteria = StabilityCriteria()
        check = criteria.check_max_gz(poor_metrics)

        assert check.result == CriteriaResult.WARNING
        assert "below minimum" in check.details.lower()

    def test_negative_max_gz(self, unstable_metrics):
        """Test negative max GZ."""
        criteria = StabilityCriteria()
        check = criteria.check_max_gz(unstable_metrics)

        assert check.result == CriteriaResult.FAIL
        assert "negative" in check.details.lower()


class TestAngleOfMaxGZCriterion:
    """Tests for angle of max GZ criterion check."""

    def test_good_angle(self, good_metrics):
        """Test angle that meets criterion."""
        criteria = StabilityCriteria()
        check = criteria.check_angle_of_max_gz(good_metrics)

        assert check.result == CriteriaResult.PASS
        assert check.measured_value == good_metrics.angle_of_max_gz

    def test_low_angle(self, poor_metrics):
        """Test angle below threshold."""
        criteria = StabilityCriteria()
        check = criteria.check_angle_of_max_gz(poor_metrics)

        assert check.result == CriteriaResult.WARNING
        assert "below minimum" in check.details.lower()


class TestRangeOfPositiveStability:
    """Tests for range of positive stability criterion."""

    def test_good_range(self, good_metrics):
        """Test range that meets criterion."""
        criteria = StabilityCriteria()
        check = criteria.check_range_of_positive_stability(good_metrics)

        assert check.result == CriteriaResult.PASS
        min_angle, max_angle = good_metrics.range_of_positive_stability
        assert check.measured_value == max_angle - min_angle

    def test_narrow_range(self, poor_metrics):
        """Test range below threshold."""
        criteria = StabilityCriteria()
        check = criteria.check_range_of_positive_stability(poor_metrics)

        assert check.result == CriteriaResult.WARNING
        assert "below minimum" in check.details.lower()


class TestVanishingAngleCriterion:
    """Tests for vanishing angle criterion check."""

    def test_good_angle(self, good_metrics):
        """Test angle that meets criterion."""
        criteria = StabilityCriteria()
        check = criteria.check_vanishing_angle(good_metrics)

        assert check.result == CriteriaResult.PASS
        assert check.measured_value == good_metrics.angle_of_vanishing_stability

    def test_low_angle(self, poor_metrics):
        """Test angle below threshold."""
        criteria = StabilityCriteria()
        check = criteria.check_vanishing_angle(poor_metrics)

        assert check.result == CriteriaResult.WARNING
        assert "below minimum" in check.details.lower()


class TestDynamicStabilityCriterion:
    """Tests for dynamic stability criterion check."""

    def test_good_area(self, good_metrics):
        """Test area that meets criterion."""
        criteria = StabilityCriteria()
        check = criteria.check_dynamic_stability(good_metrics)

        assert check.result == CriteriaResult.PASS
        assert check.measured_value == good_metrics.area_under_curve

    def test_low_area(self, poor_metrics):
        """Test area below threshold."""
        criteria = StabilityCriteria()
        check = criteria.check_dynamic_stability(poor_metrics)

        assert check.result == CriteriaResult.WARNING
        assert "below minimum" in check.details.lower()

    def test_negative_area(self, unstable_metrics):
        """Test negative area."""
        criteria = StabilityCriteria()
        check = criteria.check_dynamic_stability(unstable_metrics)

        assert check.result == CriteriaResult.FAIL
        assert "negative" in check.details.lower()

    def test_missing_area(self, missing_optional_metrics):
        """Test when area is not available."""
        criteria = StabilityCriteria()
        check = criteria.check_dynamic_stability(missing_optional_metrics)

        assert check.result == CriteriaResult.NOT_APPLICABLE


# ============================================================================
# Test Complete Assessment
# ============================================================================


class TestStabilityAssessment:
    """Tests for complete stability assessment."""

    def test_good_metrics_assessment(self, good_metrics):
        """Test assessment with good metrics."""
        criteria = StabilityCriteria()
        assessment = criteria.assess_stability(good_metrics)

        assert assessment.overall_result == CriteriaResult.PASS
        assert len(assessment.get_passed_checks()) >= 5
        assert len(assessment.get_failed_checks()) == 0
        assert "passed all" in assessment.summary.lower()

    def test_poor_metrics_assessment(self, poor_metrics):
        """Test assessment with poor metrics."""
        criteria = StabilityCriteria()
        assessment = criteria.assess_stability(poor_metrics)

        assert assessment.overall_result == CriteriaResult.WARNING
        assert len(assessment.get_warning_checks()) > 0
        assert len(assessment.recommendations) > 0

    def test_unstable_metrics_assessment(self, unstable_metrics):
        """Test assessment with unstable metrics."""
        criteria = StabilityCriteria()
        assessment = criteria.assess_stability(unstable_metrics)

        assert assessment.overall_result == CriteriaResult.FAIL
        assert len(assessment.get_failed_checks()) > 0
        assert "failed" in assessment.summary.lower()

    def test_missing_optional_assessment(self, missing_optional_metrics):
        """Test assessment with missing optional values."""
        criteria = StabilityCriteria()
        assessment = criteria.assess_stability(missing_optional_metrics)

        # Should still be able to assess based on available metrics
        assert assessment.overall_result in [CriteriaResult.PASS, CriteriaResult.WARNING]

        # Check that N/A checks are present
        na_checks = [
            c for c in assessment.criteria_checks if c.result == CriteriaResult.NOT_APPLICABLE
        ]
        assert len(na_checks) > 0

    def test_strict_mode_assessment(self, poor_metrics):
        """Test assessment in strict mode."""
        criteria_normal = StabilityCriteria(strict_mode=False)
        criteria_strict = StabilityCriteria(strict_mode=True)

        assessment_normal = criteria_normal.assess_stability(poor_metrics)
        assessment_strict = criteria_strict.assess_stability(poor_metrics)

        # Strict mode should have more failures
        assert len(assessment_strict.get_failed_checks()) >= len(
            assessment_normal.get_failed_checks()
        )

    def test_recommendations_generation(self, poor_metrics):
        """Test that recommendations are generated."""
        criteria = StabilityCriteria()
        assessment = criteria.assess_stability(poor_metrics)

        assert len(assessment.recommendations) > 0

        # Check that recommendations are meaningful
        for rec in assessment.recommendations:
            assert len(rec) > 20  # Should have substantial content

    def test_critical_recommendations(self, unstable_metrics):
        """Test that critical issues generate appropriate recommendations."""
        criteria = StabilityCriteria()
        assessment = criteria.assess_stability(unstable_metrics)

        # Should have recommendation about negative GM
        has_critical = any(
            "CRITICAL" in rec or "negative GM" in rec.lower() for rec in assessment.recommendations
        )
        assert has_critical


# ============================================================================
# Test Custom Thresholds
# ============================================================================


class TestCustomThresholds:
    """Tests for custom criteria thresholds."""

    def test_custom_min_gm(self, good_metrics):
        """Test with custom GM threshold."""
        # Set very high threshold
        criteria = StabilityCriteria(min_gm=0.50)
        check = criteria.check_gm(good_metrics)

        # Should fail now even though it was passing before
        assert check.result in [CriteriaResult.WARNING, CriteriaResult.FAIL]

    def test_custom_min_max_gz(self, good_metrics):
        """Test with custom max GZ threshold."""
        criteria = StabilityCriteria(min_max_gz=0.50)
        check = criteria.check_max_gz(good_metrics)

        assert check.result in [CriteriaResult.WARNING, CriteriaResult.FAIL]

    def test_custom_all_thresholds(self):
        """Test creating criteria with all custom thresholds."""
        criteria = StabilityCriteria(
            min_gm=0.10,
            min_max_gz=0.20,
            min_angle_of_max_gz=30.0,
            min_range_positive=60.0,
            min_vanishing_angle=80.0,
            min_dynamic_stability=0.10,
        )

        assert criteria.min_gm == 0.10
        assert criteria.min_max_gz == 0.20
        assert criteria.min_angle_of_max_gz == 30.0


# ============================================================================
# Test Helper Methods
# ============================================================================


class TestAssessmentHelpers:
    """Tests for assessment helper methods."""

    def test_get_passed_checks(self, good_metrics):
        """Test getting passed checks."""
        criteria = StabilityCriteria()
        assessment = criteria.assess_stability(good_metrics)

        passed = assessment.get_passed_checks()
        assert len(passed) > 0
        assert all(c.result == CriteriaResult.PASS for c in passed)

    def test_get_failed_checks(self, unstable_metrics):
        """Test getting failed checks."""
        criteria = StabilityCriteria()
        assessment = criteria.assess_stability(unstable_metrics)

        failed = assessment.get_failed_checks()
        assert len(failed) > 0
        assert all(c.result == CriteriaResult.FAIL for c in failed)

    def test_get_warning_checks(self, poor_metrics):
        """Test getting warning checks."""
        criteria = StabilityCriteria()
        assessment = criteria.assess_stability(poor_metrics)

        warnings = assessment.get_warning_checks()
        assert len(warnings) > 0
        assert all(c.result == CriteriaResult.WARNING for c in warnings)


# ============================================================================
# Test Quick Assessment Function
# ============================================================================


class TestQuickAssessment:
    """Tests for quick assessment convenience function."""

    def test_quick_assessment_normal(self, good_metrics):
        """Test quick assessment with normal mode."""
        assessment = quick_stability_assessment(good_metrics)

        assert isinstance(assessment, StabilityAssessment)
        assert assessment.overall_result == CriteriaResult.PASS

    def test_quick_assessment_strict(self, poor_metrics):
        """Test quick assessment with strict mode."""
        assessment = quick_stability_assessment(poor_metrics, strict_mode=True)

        assert isinstance(assessment, StabilityAssessment)
        # Should have more failures in strict mode
        assert len(assessment.get_failed_checks()) > 0

    def test_quick_assessment_equivalence(self, good_metrics):
        """Test that quick assessment equals full process."""
        assessment1 = quick_stability_assessment(good_metrics)

        criteria = StabilityCriteria()
        assessment2 = criteria.assess_stability(good_metrics)

        assert assessment1.overall_result == assessment2.overall_result
        assert len(assessment1.criteria_checks) == len(assessment2.criteria_checks)


# ============================================================================
# Test String Representations
# ============================================================================


class TestStringRepresentations:
    """Tests for string representations."""

    def test_criteria_check_repr(self, good_metrics):
        """Test CriteriaCheck string representation."""
        criteria = StabilityCriteria()
        check = criteria.check_gm(good_metrics)

        repr_str = repr(check)
        assert "CriteriaCheck" in repr_str
        assert "PASS" in repr_str
        assert check.name in repr_str

    def test_stability_assessment_repr(self, good_metrics):
        """Test StabilityAssessment string representation."""
        criteria = StabilityCriteria()
        assessment = criteria.assess_stability(good_metrics)

        repr_str = repr(assessment)
        assert "StabilityAssessment" in repr_str
        assert "PASS" in repr_str

    def test_criteria_repr(self):
        """Test StabilityCriteria string representation."""
        criteria = StabilityCriteria(min_gm=0.10, min_max_gz=0.20, strict_mode=True)

        repr_str = repr(criteria)
        assert "StabilityCriteria" in repr_str
        assert "0.10" in repr_str or "0.1000" in repr_str
        assert "True" in repr_str


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for complete workflow."""

    def test_complete_workflow(self, good_metrics):
        """Test complete assessment workflow."""
        # Create criteria
        criteria = StabilityCriteria()

        # Perform assessment
        assessment = criteria.assess_stability(good_metrics)

        # Verify all components
        assert len(assessment.criteria_checks) > 0
        assert assessment.overall_result is not None
        assert len(assessment.summary) > 0
        assert isinstance(assessment.recommendations, list)

    def test_workflow_with_poor_stability(self, poor_metrics):
        """Test workflow with poor stability metrics."""
        criteria = StabilityCriteria()
        assessment = criteria.assess_stability(poor_metrics)

        # Should have warnings
        assert assessment.overall_result == CriteriaResult.WARNING

        # Should have specific recommendations
        assert len(assessment.recommendations) > 0

        # Check for specific improvement suggestions
        recommendations_text = " ".join(assessment.recommendations).lower()
        assert any(keyword in recommendations_text for keyword in ["lower", "cg", "beam", "hull"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
