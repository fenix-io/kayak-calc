"""
Tests for center of gravity calculations.

This test suite validates the center of gravity (CG) calculations by:
1. Testing component-based CG calculations
2. Validating manual CG specification
3. Testing mass component validation
4. Testing CG adjustments for loading changes
5. Testing validation and error handling
"""

import pytest
import numpy as np
from src.hydrostatics import (
    MassComponent,
    CenterOfGravity,
    calculate_cg_from_components,
    create_cg_manual,
    validate_center_of_gravity,
    adjust_cg_for_loading,
    calculate_mass_summary,
)


class TestMassComponent:
    """Test MassComponent dataclass."""

    def test_initialization(self):
        """Test basic initialization."""
        comp = MassComponent(name="Paddler", mass=80.0, x=2.0, y=0.0, z=0.3)

        assert comp.name == "Paddler"
        assert comp.mass == 80.0
        assert comp.x == 2.0
        assert comp.y == 0.0
        assert comp.z == 0.3
        assert comp.description == ""

    def test_initialization_with_description(self):
        """Test initialization with description."""
        comp = MassComponent(
            name="Gear", mass=15.0, x=1.5, y=0.0, z=0.1, description="Camping equipment"
        )

        assert comp.description == "Camping equipment"

    def test_negative_mass_raises_error(self):
        """Test that negative mass raises an error."""
        with pytest.raises(ValueError, match="Mass must be non-negative"):
            MassComponent("Invalid", mass=-10.0, x=0, y=0, z=0)

    def test_non_finite_mass_raises_error(self):
        """Test that non-finite mass raises an error."""
        with pytest.raises(ValueError, match="Mass must be finite"):
            MassComponent("Invalid", mass=np.inf, x=0, y=0, z=0)

    def test_non_finite_position_raises_error(self):
        """Test that non-finite position raises an error."""
        with pytest.raises(ValueError, match="Position coordinates must be finite"):
            MassComponent("Invalid", mass=10.0, x=np.nan, y=0, z=0)

    def test_zero_mass_is_valid(self):
        """Test that zero mass is valid (e.g., for reference points)."""
        comp = MassComponent("Reference", mass=0.0, x=0, y=0, z=0)
        assert comp.mass == 0.0

    def test_repr(self):
        """Test string representation."""
        comp = MassComponent("Test", mass=10.0, x=1.0, y=2.0, z=3.0)
        repr_str = repr(comp)

        assert "MassComponent" in repr_str
        assert "Test" in repr_str
        assert "10.00 kg" in repr_str


class TestCenterOfGravity:
    """Test CenterOfGravity dataclass."""

    def test_initialization(self):
        """Test basic initialization."""
        cg = CenterOfGravity(lcg=2.5, vcg=0.2, tcg=0.0, total_mass=120.0)

        assert cg.lcg == 2.5
        assert cg.vcg == 0.2
        assert cg.tcg == 0.0
        assert cg.total_mass == 120.0
        assert cg.num_components == 0
        assert cg.components is None

    def test_weight_property(self):
        """Test weight calculation."""
        cg = CenterOfGravity(lcg=2.0, vcg=0.1, tcg=0.0, total_mass=100.0)

        # Weight = mass × gravity (9.81 m/s²)
        expected_weight = 100.0 * 9.81
        assert np.isclose(cg.weight, expected_weight)

    def test_to_dict(self):
        """Test conversion to dictionary."""
        cg = CenterOfGravity(lcg=2.5, vcg=0.2, tcg=0.0, total_mass=120.0, num_components=2)

        data = cg.to_dict()

        assert data["lcg"] == 2.5
        assert data["vcg"] == 0.2
        assert data["tcg"] == 0.0
        assert data["total_mass"] == 120.0
        assert data["num_components"] == 2

    def test_to_dict_with_components(self):
        """Test dictionary conversion with components."""
        comp1 = MassComponent("Hull", mass=25.0, x=2.5, y=0.0, z=0.0)
        comp2 = MassComponent("Paddler", mass=80.0, x=2.0, y=0.0, z=0.3)

        cg = CenterOfGravity(
            lcg=2.1, vcg=0.2, tcg=0.0, total_mass=105.0, num_components=2, components=[comp1, comp2]
        )

        data = cg.to_dict()
        assert "components" in data
        assert len(data["components"]) == 2
        assert data["components"][0]["name"] == "Hull"

    def test_repr(self):
        """Test string representation."""
        cg = CenterOfGravity(lcg=2.0, vcg=0.1, tcg=0.0, total_mass=100.0)
        repr_str = repr(cg)

        assert "CenterOfGravity" in repr_str
        assert "LCG=2.000000" in repr_str
        assert "VCG=0.100000" in repr_str


class TestCalculateCGFromComponents:
    """Test CG calculation from components."""

    def test_single_component(self):
        """Test CG with single component."""
        comp = MassComponent("Hull", mass=25.0, x=2.5, y=0.0, z=-0.1)

        cg = calculate_cg_from_components([comp])

        # CG should be at component position
        assert cg.lcg == 2.5
        assert cg.vcg == -0.1
        assert cg.tcg == 0.0
        assert cg.total_mass == 25.0
        assert cg.num_components == 1

    def test_two_components_equal_mass(self):
        """Test CG with two components of equal mass."""
        comp1 = MassComponent("A", mass=10.0, x=0.0, y=0.0, z=0.0)
        comp2 = MassComponent("B", mass=10.0, x=2.0, y=0.0, z=0.0)

        cg = calculate_cg_from_components([comp1, comp2])

        # CG should be at midpoint
        assert cg.lcg == 1.0
        assert cg.vcg == 0.0
        assert cg.tcg == 0.0
        assert cg.total_mass == 20.0

    def test_two_components_different_mass(self):
        """Test CG with two components of different mass."""
        # Light component at x=0, heavy component at x=3
        comp1 = MassComponent("Light", mass=10.0, x=0.0, y=0.0, z=0.0)
        comp2 = MassComponent("Heavy", mass=30.0, x=3.0, y=0.0, z=0.0)

        cg = calculate_cg_from_components([comp1, comp2])

        # CG = (10*0 + 30*3) / 40 = 90/40 = 2.25
        assert np.isclose(cg.lcg, 2.25)
        assert cg.total_mass == 40.0

    def test_three_components_3d(self):
        """Test CG with three components in 3D."""
        comp1 = MassComponent("Hull", mass=25.0, x=2.5, y=0.0, z=-0.1)
        comp2 = MassComponent("Paddler", mass=80.0, x=2.0, y=0.0, z=0.3)
        comp3 = MassComponent("Gear", mass=15.0, x=1.5, y=0.0, z=0.1)

        cg = calculate_cg_from_components([comp1, comp2, comp3])

        # Calculate expected values
        total_mass = 25.0 + 80.0 + 15.0  # 120 kg
        lcg_expected = (25 * 2.5 + 80 * 2.0 + 15 * 1.5) / total_mass
        vcg_expected = (25 * (-0.1) + 80 * 0.3 + 15 * 0.1) / total_mass
        tcg_expected = 0.0  # All at centerline

        assert np.isclose(cg.lcg, lcg_expected)
        assert np.isclose(cg.vcg, vcg_expected)
        assert np.isclose(cg.tcg, tcg_expected)
        assert cg.total_mass == 120.0
        assert cg.num_components == 3

    def test_off_centerline_loading(self):
        """Test CG with asymmetric loading."""
        comp1 = MassComponent("Hull", mass=25.0, x=2.0, y=0.0, z=0.0)
        comp2 = MassComponent("Paddler", mass=80.0, x=2.0, y=0.05, z=0.3)  # Slightly off-center

        cg = calculate_cg_from_components([comp1, comp2])

        # TCG should be non-zero
        tcg_expected = (25 * 0.0 + 80 * 0.05) / 105.0
        assert np.isclose(cg.tcg, tcg_expected)
        assert cg.tcg > 0  # Positive (starboard side)

    def test_empty_list_raises_error(self):
        """Test that empty component list raises error."""
        with pytest.raises(ValueError, match="Components list cannot be empty"):
            calculate_cg_from_components([])

    def test_zero_total_mass_raises_error(self):
        """Test that zero total mass raises error."""
        comp1 = MassComponent("A", mass=0.0, x=0, y=0, z=0)
        comp2 = MassComponent("B", mass=0.0, x=1, y=0, z=0)

        with pytest.raises(ValueError, match="Total mass must be positive"):
            calculate_cg_from_components([comp1, comp2])

    def test_include_components_true(self):
        """Test that components are stored when include_components=True."""
        comp1 = MassComponent("A", mass=10.0, x=0, y=0, z=0)
        comp2 = MassComponent("B", mass=20.0, x=1, y=0, z=0)

        cg = calculate_cg_from_components([comp1, comp2], include_components=True)

        assert cg.components is not None
        assert len(cg.components) == 2
        assert cg.components[0].name == "A"

    def test_include_components_false(self):
        """Test that components are not stored when include_components=False."""
        comp1 = MassComponent("A", mass=10.0, x=0, y=0, z=0)

        cg = calculate_cg_from_components([comp1], include_components=False)

        assert cg.components is None


class TestCreateCGManual:
    """Test manual CG specification."""

    def test_create_cg_manual(self):
        """Test creating CG with manual specification."""
        cg = create_cg_manual(lcg=2.3, vcg=0.2, tcg=0.0, total_mass=120.0)

        assert cg.lcg == 2.3
        assert cg.vcg == 0.2
        assert cg.tcg == 0.0
        assert cg.total_mass == 120.0
        assert cg.num_components == 0
        assert cg.components is None

    def test_negative_mass_raises_error(self):
        """Test that negative mass raises error."""
        with pytest.raises(ValueError, match="Total mass must be positive"):
            create_cg_manual(lcg=2.0, vcg=0.1, tcg=0.0, total_mass=-10.0)

    def test_zero_mass_raises_error(self):
        """Test that zero mass raises error."""
        with pytest.raises(ValueError, match="Total mass must be positive"):
            create_cg_manual(lcg=2.0, vcg=0.1, tcg=0.0, total_mass=0.0)

    def test_non_finite_coordinates_raise_error(self):
        """Test that non-finite coordinates raise error."""
        with pytest.raises(ValueError, match="CG coordinates must be finite"):
            create_cg_manual(lcg=np.nan, vcg=0.1, tcg=0.0, total_mass=100.0)


class TestValidateCenterOfGravity:
    """Test CG validation."""

    def test_validate_valid_cg(self):
        """Test validation of valid CG."""
        cg = create_cg_manual(lcg=2.5, vcg=0.2, tcg=0.0, total_mass=120.0)

        is_valid, issues = validate_center_of_gravity(cg)

        assert is_valid
        assert len(issues) == 0

    def test_validate_non_finite_lcg(self):
        """Test validation detects non-finite LCG."""
        cg = CenterOfGravity(lcg=np.nan, vcg=0.2, tcg=0.0, total_mass=100.0)

        is_valid, issues = validate_center_of_gravity(cg)

        assert not is_valid
        assert any("Non-finite LCG" in issue for issue in issues)

    def test_validate_negative_mass(self):
        """Test validation detects negative mass."""
        cg = CenterOfGravity(lcg=2.0, vcg=0.1, tcg=0.0, total_mass=-10.0)

        is_valid, issues = validate_center_of_gravity(cg)

        assert not is_valid
        assert any("must be positive" in issue for issue in issues)

    def test_validate_low_mass(self):
        """Test validation warns about very low mass."""
        cg = CenterOfGravity(lcg=2.0, vcg=0.1, tcg=0.0, total_mass=0.5)

        is_valid, issues = validate_center_of_gravity(cg, min_mass=1.0)

        assert not is_valid
        assert any("very low" in issue for issue in issues)

    def test_validate_high_mass(self):
        """Test validation warns about very high mass."""
        cg = CenterOfGravity(lcg=2.0, vcg=0.1, tcg=0.0, total_mass=600.0)

        is_valid, issues = validate_center_of_gravity(cg, max_mass=500.0)

        assert not is_valid
        assert any("very high" in issue for issue in issues)

    def test_validate_off_centerline_tcg(self):
        """Test validation warns about TCG off centerline."""
        cg = CenterOfGravity(lcg=2.0, vcg=0.1, tcg=0.5, total_mass=100.0)

        is_valid, issues = validate_center_of_gravity(cg, max_tcg_offset=0.1)

        assert not is_valid
        assert any("off centerline" in issue for issue in issues)

    def test_validate_acceptable_tcg(self):
        """Test that small TCG offset is acceptable."""
        cg = CenterOfGravity(lcg=2.0, vcg=0.1, tcg=0.05, total_mass=100.0)

        is_valid, issues = validate_center_of_gravity(cg, max_tcg_offset=0.1)

        assert is_valid
        assert len(issues) == 0


class TestAdjustCGForLoading:
    """Test CG adjustment for loading changes."""

    def test_add_single_component(self):
        """Test adding a single component to base CG."""
        # Empty kayak
        base_cg = create_cg_manual(lcg=2.5, vcg=0.0, tcg=0.0, total_mass=25.0)

        # Add paddler
        paddler = MassComponent("Paddler", mass=80.0, x=2.0, y=0.0, z=0.3)

        new_cg = adjust_cg_for_loading(base_cg, [paddler])

        # Calculate expected
        total = 25.0 + 80.0
        lcg_expected = (25 * 2.5 + 80 * 2.0) / total
        vcg_expected = (25 * 0.0 + 80 * 0.3) / total

        assert np.isclose(new_cg.lcg, lcg_expected)
        assert np.isclose(new_cg.vcg, vcg_expected)
        assert new_cg.total_mass == 105.0

    def test_add_multiple_components(self):
        """Test adding multiple components."""
        base_cg = create_cg_manual(lcg=2.5, vcg=0.0, tcg=0.0, total_mass=25.0)

        new_items = [
            MassComponent("Paddler", mass=80.0, x=2.0, y=0.0, z=0.3),
            MassComponent("Gear", mass=15.0, x=1.5, y=0.0, z=0.1),
        ]

        new_cg = adjust_cg_for_loading(base_cg, new_items)

        assert new_cg.total_mass == 120.0
        assert new_cg.num_components == 3  # Base + 2 new

    def test_adjusted_cg_has_components(self):
        """Test that adjusted CG includes component list."""
        base_cg = create_cg_manual(lcg=2.0, vcg=0.0, tcg=0.0, total_mass=25.0)
        new_item = MassComponent("Test", mass=10.0, x=1.0, y=0.0, z=0.0)

        new_cg = adjust_cg_for_loading(base_cg, [new_item])

        assert new_cg.components is not None
        assert len(new_cg.components) == 2


class TestCalculateMassSummary:
    """Test mass summary calculation."""

    def test_summary_single_component(self):
        """Test summary with single component."""
        comp = MassComponent("Hull", mass=25.0, x=2.0, y=0.0, z=0.0)

        summary = calculate_mass_summary([comp])

        assert summary["total_mass"] == 25.0
        assert summary["num_components"] == 1
        assert summary["heaviest"]["name"] == "Hull"
        assert summary["lightest"]["name"] == "Hull"
        assert summary["average_mass"] == 25.0

    def test_summary_multiple_components(self):
        """Test summary with multiple components."""
        components = [
            MassComponent("Hull", mass=25.0, x=2.5, y=0.0, z=0.0),
            MassComponent("Paddler", mass=80.0, x=2.0, y=0.0, z=0.3),
            MassComponent("Gear", mass=15.0, x=1.5, y=0.0, z=0.1),
        ]

        summary = calculate_mass_summary(components)

        assert summary["total_mass"] == 120.0
        assert summary["num_components"] == 3
        assert summary["heaviest"]["name"] == "Paddler"
        assert summary["heaviest"]["mass"] == 80.0
        assert summary["lightest"]["name"] == "Gear"
        assert summary["lightest"]["mass"] == 15.0
        assert np.isclose(summary["average_mass"], 40.0)

    def test_summary_mass_distribution(self):
        """Test mass distribution in summary."""
        components = [
            MassComponent("A", mass=50.0, x=0, y=0, z=0),
            MassComponent("B", mass=30.0, x=0, y=0, z=0),
            MassComponent("C", mass=20.0, x=0, y=0, z=0),
        ]

        summary = calculate_mass_summary(components)

        # Should be sorted by mass (descending)
        dist = summary["mass_distribution"]
        assert dist[0]["name"] == "A"
        assert dist[0]["percentage"] == 50.0
        assert dist[1]["name"] == "B"
        assert dist[1]["percentage"] == 30.0
        assert dist[2]["name"] == "C"
        assert dist[2]["percentage"] == 20.0

    def test_summary_empty_list(self):
        """Test summary with empty list."""
        summary = calculate_mass_summary([])

        assert summary["total_mass"] == 0.0
        assert summary["num_components"] == 0
        assert summary["heaviest"] is None
        assert summary["lightest"] is None
        assert summary["average_mass"] == 0.0


class TestEdgeCases:
    """Test edge cases."""

    def test_very_small_masses(self):
        """Test CG with very small masses."""
        comp1 = MassComponent("A", mass=0.001, x=0.0, y=0.0, z=0.0)
        comp2 = MassComponent("B", mass=0.002, x=1.0, y=0.0, z=0.0)

        cg = calculate_cg_from_components([comp1, comp2])

        # LCG = (0.001*0 + 0.002*1) / 0.003 = 0.002/0.003 = 2/3
        assert np.isclose(cg.lcg, 2.0 / 3.0)
        assert np.isclose(cg.total_mass, 0.003)

    def test_very_large_masses(self):
        """Test CG with very large masses."""
        comp1 = MassComponent("A", mass=10000.0, x=0.0, y=0.0, z=0.0)
        comp2 = MassComponent("B", mass=20000.0, x=10.0, y=0.0, z=0.0)

        cg = calculate_cg_from_components([comp1, comp2])

        # LCG = (10000*0 + 20000*10) / 30000 = 200000/30000 = 6.667
        assert np.isclose(cg.lcg, 20.0 / 3.0)
        assert cg.total_mass == 30000.0

    def test_components_with_zero_mass(self):
        """Test that zero-mass components don't affect CG."""
        comp1 = MassComponent("Real", mass=10.0, x=0.0, y=0.0, z=0.0)
        comp2 = MassComponent("Zero", mass=0.0, x=100.0, y=0.0, z=0.0)
        comp3 = MassComponent("Real2", mass=10.0, x=2.0, y=0.0, z=0.0)

        cg = calculate_cg_from_components([comp1, comp2, comp3])

        # Zero mass component shouldn't affect CG
        # LCG = (10*0 + 0*100 + 10*2) / 20 = 1.0
        assert cg.lcg == 1.0
        assert cg.total_mass == 20.0


class TestRealWorldScenarios:
    """Test realistic kayak scenarios."""

    def test_typical_touring_kayak(self):
        """Test typical touring kayak configuration."""
        components = [
            MassComponent("Hull", mass=28.0, x=2.3, y=0.0, z=-0.05),
            MassComponent("Paddler", mass=75.0, x=2.0, y=0.0, z=0.25),
            MassComponent("Paddle", mass=1.0, x=2.0, y=0.3, z=0.4),
            MassComponent("PFD", mass=0.8, x=2.0, y=0.0, z=0.35),
            MassComponent("Water bottle", mass=1.0, x=2.1, y=0.0, z=0.1),
            MassComponent("Dry bag", mass=3.0, x=1.2, y=0.0, z=0.0),
        ]

        cg = calculate_cg_from_components(components)

        # Should have reasonable values
        assert 1.5 < cg.lcg < 2.5  # Somewhere in middle
        assert 0.1 < cg.vcg < 0.4  # Above waterline
        assert abs(cg.tcg) < 0.1  # Near centerline
        assert 100 < cg.total_mass < 120  # Reasonable total

        # Validate
        is_valid, issues = validate_center_of_gravity(cg)
        assert is_valid

    def test_unbalanced_loading(self):
        """Test detection of unbalanced loading."""
        components = [
            MassComponent("Hull", mass=25.0, x=2.0, y=0.0, z=0.0),
            MassComponent("Paddler", mass=80.0, x=2.0, y=0.0, z=0.3),
            MassComponent("Heavy gear", mass=20.0, x=1.0, y=0.3, z=0.1),  # Off to side
        ]

        cg = calculate_cg_from_components(components)

        # TCG should be off centerline: (25*0 + 80*0 + 20*0.3) / 125 = 6/125 = 0.048
        assert abs(cg.tcg) > 0.03

        # Validation should warn if threshold is stricter
        is_valid, issues = validate_center_of_gravity(cg, max_tcg_offset=0.03)
        assert not is_valid
        assert any("off centerline" in issue for issue in issues)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
