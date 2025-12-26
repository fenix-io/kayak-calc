"""
Validation test cases with analytical solutions and symmetry checks.

This module contains validation tests that verify the correctness of
calculations using:
1. Analytical solutions for simple geometries (rectangular hulls)
2. Symmetry preservation for symmetric hulls
3. Edge case validation for extreme configurations
"""

import pytest
import numpy as np
from pathlib import Path

from src.geometry import Point3D, Profile, KayakHull
from src.hydrostatics import (
    calculate_volume,
    calculate_displacement,
    calculate_center_of_buoyancy
)
from src.hydrostatics.center_of_gravity import create_cg_manual
from src.stability import StabilityAnalyzer, calculate_gz
from tests.utils.analytical_solutions import (
    box_volume,
    box_centroid,
    wedge_volume
)


class TestRectangularHullValidation:
    """Test calculations against analytical solutions for rectangular hulls."""
    
    def create_rectangular_hull(
        self,
        length: float,
        beam: float,
        height: float,
        num_stations: int = 5
    ) -> KayakHull:
        """
        Create a rectangular box hull.
        
        Args:
            length: Length in x-direction (m)
            beam: Beam (width) in y-direction (m)
            height: Height in z-direction (m, from keel to deck)
            num_stations: Number of transverse profiles
            
        Returns:
            KayakHull object with rectangular cross-sections
            
        Note:
            Hull is positioned with keel at z=-height and deck at z=0.
            Waterline at z=0 gives full immersion.
        """
        hull = KayakHull()
        
        # Create profiles along the length
        # Keel at z=-height, deck at z=0 (so waterline at z=0 gives full immersion)
        for x_pos in np.linspace(0, length, num_stations):
            # Rectangular cross-section
            # Note: y=0 is centerline, z=0 is waterline for full immersion
            points = [
                Point3D(x_pos, -beam/2, 0.0),         # Deck-left (at waterline when fully immersed)
                Point3D(x_pos, -beam/2, -height),     # Keel-left
                Point3D(x_pos, beam/2, -height),      # Keel-right
                Point3D(x_pos, beam/2, 0.0),          # Deck-right
            ]
            profile = Profile(station=x_pos, points=points)
            hull.add_profile(profile)
        
        return hull
    
    def test_rectangular_hull_volume_upright(self):
        """Test volume calculation for upright rectangular hull."""
        # Create a simple box hull
        length = 5.0  # m
        beam = 1.0    # m
        draft = 0.5   # m (depth below waterline)
        
        hull = self.create_rectangular_hull(length, beam, height=draft, num_stations=11)
        
        # Calculate volume with waterline at z=0 (full immersion)
        volume = calculate_volume(hull, waterline_z=0.0, method='simpson')
        
        # Analytical solution
        expected_volume = box_volume(length, beam, draft)
        
        # Should match within 1% (numerical integration error)
        relative_error = abs(volume - expected_volume) / expected_volume
        assert relative_error < 0.01, (
            f"Volume error too large: {relative_error*100:.2f}% "
            f"(calculated={volume:.6f}, expected={expected_volume:.6f})"
        )
    
    def test_rectangular_hull_volume_multiple_waterlines(self):
        """Test volume at multiple waterlines."""
        length = 4.0
        beam = 0.8
        height = 0.6
        
        hull = self.create_rectangular_hull(length, beam, height, num_stations=9)
        
        # Test at different waterlines (negative values, since keel is at -height)
        waterlines = [-0.1, -0.2, -0.3, -0.4, -0.5]
        
        for wl_z in waterlines:
            volume = calculate_volume(hull, waterline_z=wl_z, method='simpson')
            
            # Draft is distance from waterline to keel
            draft = wl_z - (-height)  # keel at z=-height
            expected_volume = box_volume(length, beam, draft)
            
            relative_error = abs(volume - expected_volume) / expected_volume
            assert relative_error < 0.01, (
                f"Volume error at WL={wl_z}: {relative_error*100:.2f}%"
            )
    
    def test_rectangular_hull_center_of_buoyancy_upright(self):
        """Test center of buoyancy for upright rectangular hull."""
        length = 5.0
        beam = 1.0
        draft = 0.5
        
        hull = self.create_rectangular_hull(length, beam, height=draft, num_stations=11)
        
        # Calculate CB with waterline at z=0 (hull extends from -draft to 0)
        cb = calculate_center_of_buoyancy(hull, waterline_z=0.0, method='simpson')
        
        # Analytical solution for centroid
        # Box extends from x=0 to x=length, y=-beam/2 to y=beam/2, z=0 to z=-draft
        expected_lcb = length / 2.0
        expected_vcb = -draft / 2.0  # Half draft below waterline
        expected_tcb = 0.0  # On centerline for symmetric hull
        
        # Check LCB (longitudinal center of buoyancy)
        lcb_error = abs(cb.lcb - expected_lcb)
        assert lcb_error < 0.01 * length, (
            f"LCB error: {lcb_error:.6f} m (calculated={cb.lcb:.6f}, expected={expected_lcb:.6f})"
        )
        
        # Check VCB (vertical center of buoyancy)
        vcb_error = abs(cb.vcb - expected_vcb)
        assert vcb_error < 0.01 * draft, (
            f"VCB error: {vcb_error:.6f} m (calculated={cb.vcb:.6f}, expected={expected_vcb:.6f})"
        )
        
        # Check TCB (transverse center of buoyancy) - should be on centerline
        assert abs(cb.tcb) < 0.001, (
            f"TCB should be near centerline: {cb.tcb:.6f} m"
        )
    
    def test_rectangular_hull_multiple_sizes(self):
        """Test volume calculation with different hull sizes."""
        test_cases = [
            (2.0, 0.5, 0.3),   # Small
            (5.0, 1.0, 0.5),   # Medium  
            (10.0, 2.0, 1.0),  # Large
        ]
        
        for length, beam, draft in test_cases:
            hull = self.create_rectangular_hull(length, beam, height=draft, num_stations=11)
            volume = calculate_volume(hull, waterline_z=0.0, method='simpson')
            expected_volume = box_volume(length, beam, draft)
            
            relative_error = abs(volume - expected_volume) / expected_volume
            assert relative_error < 0.01, (
                f"Volume error for {length}×{beam}×{draft}: {relative_error*100:.2f}%"
            )
    
    def test_rectangular_hull_displacement(self):
        """Test displacement calculation for rectangular hull."""
        length = 5.0
        beam = 1.0
        draft = 0.5
        
        hull = self.create_rectangular_hull(length, beam, height=draft, num_stations=11)
        
        # Calculate displacement
        disp = calculate_displacement(
            hull,
            waterline_z=0.0,
            water_density=1000.0,  # Fresh water
            method='simpson'
        )
        
        # Expected volume and mass
        expected_volume = box_volume(length, beam, draft)
        expected_mass = expected_volume * 1000.0  # kg
        
        # Check volume
        volume_error = abs(disp.volume - expected_volume) / expected_volume
        assert volume_error < 0.01, f"Volume error: {volume_error*100:.2f}%"
        
        # Check mass
        mass_error = abs(disp.mass - expected_mass) / expected_mass
        assert mass_error < 0.01, f"Mass error: {mass_error*100:.2f}%"


class TestSymmetryPreservation:
    """Test that symmetric hulls maintain symmetry in calculations."""
    
    def create_symmetric_hull(self, length: float, beam: float, height: float) -> KayakHull:
        """Create a symmetric hull (box shape with keel at -height, deck at 0)."""
        hull = KayakHull()
        
        for x_pos in np.linspace(0, length, 7):
            points = [
                Point3D(x_pos, -beam/2, 0.0),
                Point3D(x_pos, -beam/2, -height),
                Point3D(x_pos, beam/2, -height),
                Point3D(x_pos, beam/2, 0.0),
            ]
            profile = Profile(station=x_pos, points=points)
            hull.add_profile(profile)
        
        return hull
    
    def test_symmetric_hull_tcb_at_zero_heel(self):
        """Test that TCB is on centerline for symmetric hull at 0° heel."""
        hull = self.create_symmetric_hull(length=4.0, beam=0.8, height=0.5)
        
        # Calculate CB at zero heel
        cb = calculate_center_of_buoyancy(hull, waterline_z=0.0, heel_angle=0.0)
        
        # TCB should be very close to zero (on centerline)
        assert abs(cb.tcb) < 0.001, (
            f"TCB should be on centerline for symmetric hull: {cb.tcb:.6f} m"
        )
    
    def test_symmetric_hull_gz_antisymmetry(self):
        """Test that GZ curve is antisymmetric: GZ(φ) = -GZ(-φ)."""
        hull = self.create_symmetric_hull(length=4.0, beam=0.8, height=0.5)
        
        # Create CG on centerline, below waterline for stability
        cg = create_cg_manual(total_mass=100.0, lcg=2.0, vcg=-0.2, tcg=0.0)
        
        # Test at multiple heel angles
        heel_angles = [10.0, 20.0, 30.0, 40.0, 50.0]
        
        for angle in heel_angles:
            # Calculate GZ at +angle and -angle
            ra_pos = calculate_gz(hull, cg, waterline_z=0.0, heel_angle=angle)
            ra_neg = calculate_gz(hull, cg, waterline_z=0.0, heel_angle=-angle)
            
            # GZ should be antisymmetric: GZ(φ) ≈ -GZ(-φ)
            gz_sum = ra_pos.gz + ra_neg.gz
            
            # Tolerance is small but not zero due to numerical precision
            assert abs(gz_sum) < 0.001, (
                f"GZ antisymmetry violation at {angle}°: "
                f"GZ(+{angle})={ra_pos.gz:.6f}, GZ(-{angle})={ra_neg.gz:.6f}, sum={gz_sum:.6f}"
            )
    
    def test_symmetric_hull_volume_conservation(self):
        """Test that volume is same for port and starboard heel."""
        hull = self.create_symmetric_hull(length=4.0, beam=0.8, height=0.5)
        
        # Test at multiple heel angles
        heel_angles = [15.0, 30.0, 45.0]
        
        for angle in heel_angles:
            # Calculate volume at +angle and -angle
            vol_pos = calculate_volume(hull, waterline_z=0.0, heel_angle=angle)
            vol_neg = calculate_volume(hull, waterline_z=0.0, heel_angle=-angle)
            
            # Volumes should be equal (within numerical tolerance)
            vol_diff = abs(vol_pos - vol_neg)
            relative_diff = vol_diff / vol_pos
            
            assert relative_diff < 0.001, (
                f"Volume asymmetry at ±{angle}°: "
                f"V(+{angle})={vol_pos:.6f}, V(-{angle})={vol_neg:.6f}, "
                f"relative_diff={relative_diff*100:.3f}%"
            )
    
    def test_symmetric_hull_cb_tcb_symmetry(self):
        """Test that TCB has opposite sign for port/starboard heel."""
        hull = self.create_symmetric_hull(length=4.0, beam=0.8, height=0.5)
        
        heel_angles = [20.0, 40.0]
        
        for angle in heel_angles:
            # Calculate CB at +angle and -angle
            cb_pos = calculate_center_of_buoyancy(hull, waterline_z=0.0, heel_angle=angle)
            cb_neg = calculate_center_of_buoyancy(hull, waterline_z=0.0, heel_angle=-angle)
            
            # TCB should be opposite: TCB(+φ) ≈ -TCB(-φ)
            tcb_sum = cb_pos.tcb + cb_neg.tcb
            
            assert abs(tcb_sum) < 0.001, (
                f"TCB symmetry violation at ±{angle}°: "
                f"TCB(+{angle})={cb_pos.tcb:.6f}, TCB(-{angle})={cb_neg.tcb:.6f}, sum={tcb_sum:.6f}"
            )


class TestExtremeHeelAngles:
    """Test calculations at extreme heel angles."""
    
    def create_stable_hull(self) -> KayakHull:
        """Create a wide, stable hull for extreme heel testing."""
        hull = KayakHull()
        length = 4.0
        beam = 1.5  # Wide beam for stability
        height = 0.8
        
        for x_pos in np.linspace(0, length, 7):
            points = [
                Point3D(x_pos, -beam/2, 0.0),
                Point3D(x_pos, -beam/2, -height),
                Point3D(x_pos, beam/2, -height),
                Point3D(x_pos, beam/2, 0.0),
            ]
            profile = Profile(station=x_pos, points=points)
            hull.add_profile(profile)
        
        return hull
    
    def test_extreme_heel_angles_no_nan(self):
        """Test that calculations don't produce NaN at extreme heel angles."""
        hull = self.create_stable_hull()
        
        # Test up to 89° (near capsizing)
        extreme_angles = [75.0, 80.0, 85.0, 88.0, 89.0]
        
        for angle in extreme_angles:
            # Calculate volume
            vol = calculate_volume(hull, waterline_z=0.0, heel_angle=angle)
            
            # Should get finite values, not NaN or Inf
            assert np.isfinite(vol), (
                f"Volume is not finite at {angle}°: {vol}"
            )
            assert vol >= 0, (
                f"Volume is negative at {angle}°: {vol}"
            )
    
    def test_extreme_heel_cb_finite(self):
        """Test that CB calculations remain finite at extreme angles."""
        hull = self.create_stable_hull()
        
        extreme_angles = [75.0, 80.0, 85.0, 88.0]
        
        for angle in extreme_angles:
            cb = calculate_center_of_buoyancy(hull, waterline_z=0.0, heel_angle=angle)
            
            # All CB coordinates should be finite
            assert np.isfinite(cb.lcb), f"LCB not finite at {angle}°"
            assert np.isfinite(cb.vcb), f"VCB not finite at {angle}°"
            assert np.isfinite(cb.tcb), f"TCB not finite at {angle}°"
    
    def test_extreme_heel_gz_behavior(self):
        """Test GZ behavior at extreme heel angles."""
        hull = self.create_stable_hull()
        cg = create_cg_manual(total_mass=100.0, lcg=2.0, vcg=-0.3, tcg=0.0)
        
        # Test GZ calculation at extreme angles
        extreme_angles = [70.0, 75.0, 80.0, 85.0]
        
        for angle in extreme_angles:
            ra = calculate_gz(hull, cg, waterline_z=0.0, heel_angle=angle)
            
            # GZ should be finite
            assert np.isfinite(ra.gz), f"GZ not finite at {angle}°: {ra.gz}"
            
            # At extreme angles, GZ is typically negative (capsizing)
            # But we just want to verify it's calculated, not necessarily stable


class TestExtremeAspectRatios:
    """Test hulls with extreme length/beam ratios."""
    
    def test_very_narrow_hull(self):
        """Test a very narrow hull (high length/beam ratio)."""
        # Narrow kayak-like hull: 10:1 length to beam ratio
        length = 5.0
        beam = 0.5  # Very narrow
        height = 0.4
        
        hull = KayakHull()
        for x_pos in np.linspace(0, length, 11):
            points = [
                Point3D(x_pos, -beam/2, 0.0),
                Point3D(x_pos, -beam/2, -height),
                Point3D(x_pos, beam/2, -height),
                Point3D(x_pos, beam/2, 0.0),
            ]
            profile = Profile(station=x_pos, points=points)
            hull.add_profile(profile)
        
        # Calculate properties
        vol = calculate_volume(hull, waterline_z=0.0)
        cb = calculate_center_of_buoyancy(hull, waterline_z=0.0)
        
        # Should get reasonable results
        assert vol > 0
        assert np.isfinite(cb.lcb)
        assert np.isfinite(cb.vcb)
        assert abs(cb.tcb) < 0.01  # Should be near centerline
    
    def test_very_wide_hull(self):
        """Test a very wide hull (low length/beam ratio)."""
        # Wide barge-like hull: 2:1 length to beam ratio
        length = 3.0
        beam = 1.5  # Very wide
        height = 0.5
        
        hull = KayakHull()
        for x_pos in np.linspace(0, length, 7):
            points = [
                Point3D(x_pos, -beam/2, 0.0),
                Point3D(x_pos, -beam/2, -height),
                Point3D(x_pos, beam/2, -height),
                Point3D(x_pos, beam/2, 0.0),
            ]
            profile = Profile(station=x_pos, points=points)
            hull.add_profile(profile)
        
        # Calculate properties
        vol = calculate_volume(hull, waterline_z=0.0)
        cb = calculate_center_of_buoyancy(hull, waterline_z=0.0)
        
        # Should get reasonable results
        assert vol > 0
        assert np.isfinite(cb.lcb)
        assert np.isfinite(cb.vcb)
        assert abs(cb.tcb) < 0.01
    
    def test_aspect_ratio_stability(self):
        """Test stability characteristics of different aspect ratios."""
        cg = create_cg_manual(total_mass=100.0, lcg=2.0, vcg=-0.2, tcg=0.0)
        
        # Test narrow vs wide hulls
        configs = [
            ("narrow", 4.0, 0.5),  # 8:1 ratio
            ("wide", 3.0, 1.5),    # 2:1 ratio
        ]
        
        for name, length, beam in configs:
            hull = KayakHull()
            for x_pos in np.linspace(0, length, 7):
                points = [
                    Point3D(x_pos, -beam/2, 0.0),
                    Point3D(x_pos, -beam/2, -0.5),
                    Point3D(x_pos, beam/2, -0.5),
                    Point3D(x_pos, beam/2, 0.0),
                ]
                profile = Profile(station=x_pos, points=points)
                hull.add_profile(profile)
            
            # Calculate GZ at 30°
            ra = calculate_gz(hull, cg, waterline_z=0.0, heel_angle=30.0)
            
            # Should get finite result
            assert np.isfinite(ra.gz), f"GZ not finite for {name} hull"


class TestUnusualProfileShapes:
    """Test hulls with unusual profile shapes."""
    
    def test_triangular_profile(self):
        """Test hull with triangular cross-section."""
        hull = KayakHull()
        length = 4.0
        beam = 1.0
        height = 0.5
        
        for x_pos in np.linspace(0, length, 7):
            # Triangular profile: point at keel, flat at deck
            points = [
                Point3D(x_pos, -beam/2, 0.0),      # Left deck
                Point3D(x_pos, 0.0, -height),      # Keel (point)
                Point3D(x_pos, beam/2, 0.0),       # Right deck
            ]
            profile = Profile(station=x_pos, points=points)
            hull.add_profile(profile)
        
        # Calculate properties
        vol = calculate_volume(hull, waterline_z=0.0)
        cb = calculate_center_of_buoyancy(hull, waterline_z=0.0)
        
        # Should handle triangular profiles
        assert vol > 0
        assert np.isfinite(cb.lcb)
        assert np.isfinite(cb.vcb)
        
        # Should be symmetric
        assert abs(cb.tcb) < 0.01
    
    def test_multi_chine_profile(self):
        """Test hull with multiple chines (hard corners)."""
        hull = KayakHull()
        length = 4.0
        
        for x_pos in np.linspace(0, length, 7):
            # Multi-chine profile with several hard corners
            points = [
                Point3D(x_pos, -0.5, 0.0),       # Deck left
                Point3D(x_pos, -0.4, -0.2),      # Chine 1
                Point3D(x_pos, -0.3, -0.4),      # Chine 2
                Point3D(x_pos, -0.1, -0.5),      # Keel left
                Point3D(x_pos, 0.1, -0.5),       # Keel right
                Point3D(x_pos, 0.3, -0.4),       # Chine 2
                Point3D(x_pos, 0.4, -0.2),       # Chine 1
                Point3D(x_pos, 0.5, 0.0),        # Deck right
            ]
            profile = Profile(station=x_pos, points=points)
            hull.add_profile(profile)
        
        # Calculate properties
        vol = calculate_volume(hull, waterline_z=0.0)
        cb = calculate_center_of_buoyancy(hull, waterline_z=0.0)
        
        # Should handle multi-chine profiles
        assert vol > 0
        assert np.isfinite(cb.lcb)
        assert np.isfinite(cb.vcb)
        assert abs(cb.tcb) < 0.01
    
    def test_asymmetric_profile(self):
        """Test hull with intentionally asymmetric profile."""
        hull = KayakHull()
        length = 4.0
        
        for x_pos in np.linspace(0, length, 7):
            # Asymmetric profile: different on port and starboard
            points = [
                Point3D(x_pos, -0.6, 0.0),       # Wider on port side
                Point3D(x_pos, -0.5, -0.5),
                Point3D(x_pos, 0.3, -0.5),       # Narrower on starboard
                Point3D(x_pos, 0.4, 0.0),
            ]
            profile = Profile(station=x_pos, points=points)
            hull.add_profile(profile)
        
        # Calculate properties
        vol = calculate_volume(hull, waterline_z=0.0)
        cb = calculate_center_of_buoyancy(hull, waterline_z=0.0)
        
        # Should handle asymmetric profiles
        assert vol > 0
        assert np.isfinite(cb.lcb)
        assert np.isfinite(cb.vcb)
        
        # TCB should NOT be on centerline for asymmetric hull
        assert abs(cb.tcb) > 0.01, (
            "Asymmetric hull should have TCB off centerline"
        )


class TestPhysicalReasonableness:
    """Test that results are physically reasonable."""
    
    def test_volume_increases_with_draft(self):
        """Test that volume increases as draft increases."""
        hull = KayakHull()
        length = 4.0
        beam = 0.8
        
        for x_pos in np.linspace(0, length, 7):
            points = [
                Point3D(x_pos, -beam/2, 0.2),      # Deck above waterline
                Point3D(x_pos, -beam/2, -0.6),     # Keel below
                Point3D(x_pos, beam/2, -0.6),
                Point3D(x_pos, beam/2, 0.2),
            ]
            profile = Profile(station=x_pos, points=points)
            hull.add_profile(profile)
        
        # Test at increasing waterlines (going UP means more draft, more submerged)
        waterlines = [-0.4, -0.3, -0.2, -0.1, 0.0]
        volumes = []
        
        for wl_z in waterlines:
            vol = calculate_volume(hull, waterline_z=wl_z)
            volumes.append(vol)
        
        # Volumes should be increasing as waterline rises
        for i in range(len(volumes) - 1):
            assert volumes[i+1] > volumes[i], (
                f"Volume should increase with draft: "
                f"V({waterlines[i]})={volumes[i]:.6f}, V({waterlines[i+1]})={volumes[i+1]:.6f}"
            )
    
    def test_cb_moves_down_with_draft(self):
        """Test that VCB (vertical CB) moves down as draft increases."""
        hull = KayakHull()
        length = 4.0
        beam = 0.8
        
        for x_pos in np.linspace(0, length, 7):
            points = [
                Point3D(x_pos, -beam/2, 0.0),
                Point3D(x_pos, -beam/2, -0.6),
                Point3D(x_pos, beam/2, -0.6),
                Point3D(x_pos, beam/2, 0.0),
            ]
            profile = Profile(station=x_pos, points=points)
            hull.add_profile(profile)
        
        # Test at increasing draft (decreasing waterline)
        waterlines = [-0.1, -0.2, -0.3, -0.4]
        vcb_values = []
        
        for wl_z in waterlines:
            cb = calculate_center_of_buoyancy(hull, waterline_z=wl_z)
            vcb_values.append(cb.vcb)
        
        # VCB should decrease (move down) as draft increases
        for i in range(len(vcb_values) - 1):
            assert vcb_values[i+1] < vcb_values[i], (
                f"VCB should move down with increasing draft: "
                f"VCB({waterlines[i]})={vcb_values[i]:.6f}, VCB({waterlines[i+1]})={vcb_values[i+1]:.6f}"
            )
