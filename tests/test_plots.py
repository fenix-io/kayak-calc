"""
Unit tests for visualization plotting functions.

Tests the profile and hull plotting functionality including:
- Single profile plots
- Multiple profile comparisons
- 3D hull visualization
- Annotated property plots
"""

from src.visualization import (
    plot_profile,
    plot_multiple_profiles,
    plot_hull_3d,
    plot_profile_with_properties,
    configure_plot_style,
    save_figure,
    plot_stability_curve,
    plot_multiple_stability_curves,
    plot_stability_curve_with_areas,
    plot_gz_at_angles,
    plot_righting_moment_curve,
    create_stability_report_plot,
    interactive_heel_explorer,
    interactive_stability_curve,
    animate_heel_sequence,
    interactive_cg_adjustment,
    interactive_waterline_explorer,
)
from src.stability import StabilityAnalyzer
from src.hydrostatics import CenterOfGravity
from src.geometry import Point3D, Profile, KayakHull
from pathlib import Path
import matplotlib.pyplot as plt
import unittest
import numpy as np
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for testing


class TestPlotProfile(unittest.TestCase):
    """Test plot_profile() function."""

    def setUp(self):
        """Create test profile."""
        # Simple box-shaped profile
        self.profile = Profile(
            station=2.0,
            points=[
                Point3D(2.0, -0.6, 0.2),  # Top-left
                Point3D(2.0, -0.6, -0.4),  # Bottom-left
                Point3D(2.0, 0.6, -0.4),  # Bottom-right
                Point3D(2.0, 0.6, 0.2),  # Top-right
            ],
        )

    def test_plot_profile_basic(self):
        """Test basic profile plotting."""
        ax = plot_profile(self.profile)

        self.assertIsNotNone(ax)
        self.assertEqual(len(ax.lines), 3)  # Profile line, waterline, centerline

        plt.close("all")

    def test_plot_profile_with_waterline(self):
        """Test profile plotting with waterline."""
        ax = plot_profile(self.profile, waterline_z=-0.2, show_waterline=True)

        self.assertIsNotNone(ax)
        # Should have profile line, waterline, and centerline
        self.assertGreaterEqual(len(ax.lines), 2)

        plt.close("all")

    def test_plot_profile_without_waterline(self):
        """Test profile plotting without waterline."""
        ax = plot_profile(self.profile, show_waterline=False)

        self.assertIsNotNone(ax)
        # Should have profile line and centerline only
        self.assertGreaterEqual(len(ax.lines), 1)

        plt.close("all")

    def test_plot_profile_submerged(self):
        """Test profile with submerged area highlighting."""
        ax = plot_profile(self.profile, waterline_z=0.0, show_submerged=True)

        self.assertIsNotNone(ax)
        # Should have a patch for submerged area
        self.assertGreater(len(ax.patches), 0)

        plt.close("all")

    def test_plot_profile_heeled(self):
        """Test heeled profile plotting."""
        ax = plot_profile(self.profile, waterline_z=-0.2, heel_angle=30.0)

        self.assertIsNotNone(ax)
        self.assertGreaterEqual(len(ax.lines), 2)

        plt.close("all")

    def test_plot_profile_custom_axes(self):
        """Test plotting on provided axes."""
        fig, ax = plt.subplots()
        result_ax = plot_profile(self.profile, ax=ax)

        self.assertIs(result_ax, ax)

        plt.close("all")

    def test_plot_profile_custom_colors(self):
        """Test custom color options."""
        ax = plot_profile(
            self.profile, profile_color="red", waterline_color="green", submerged_color="yellow"
        )

        self.assertIsNotNone(ax)

        plt.close("all")

    def test_plot_profile_custom_title(self):
        """Test custom title."""
        custom_title = "My Custom Profile"
        ax = plot_profile(self.profile, title=custom_title)

        self.assertEqual(ax.get_title(), custom_title)

        plt.close("all")

    def test_plot_profile_no_grid(self):
        """Test plotting without grid."""
        ax = plot_profile(self.profile, grid=False)

        self.assertIsNotNone(ax)
        self.assertFalse(ax.xaxis.get_gridlines()[0].get_visible())

        plt.close("all")


class TestPlotMultipleProfiles(unittest.TestCase):
    """Test plot_multiple_profiles() function."""

    def setUp(self):
        """Create test profiles."""
        self.profiles = []
        for x_pos in [0.0, 1.0, 2.0, 3.0, 4.0]:
            profile = Profile(
                station=x_pos,
                points=[
                    Point3D(x_pos, -0.5, 0.1),
                    Point3D(x_pos, -0.5, -0.4),
                    Point3D(x_pos, 0.5, -0.4),
                    Point3D(x_pos, 0.5, 0.1),
                ],
            )
            self.profiles.append(profile)

    def test_plot_multiple_profiles_basic(self):
        """Test basic multiple profile plotting."""
        fig, axes = plot_multiple_profiles(self.profiles)

        self.assertIsNotNone(fig)
        self.assertEqual(len(axes), len(self.profiles))

        plt.close("all")

    def test_plot_multiple_profiles_custom_ncols(self):
        """Test custom column layout."""
        fig, axes = plot_multiple_profiles(self.profiles, ncols=2)

        self.assertIsNotNone(fig)
        self.assertEqual(len(axes), len(self.profiles))

        plt.close("all")

    def test_plot_multiple_profiles_with_heel(self):
        """Test multiple profiles with heel angle."""
        fig, axes = plot_multiple_profiles(self.profiles, waterline_z=-0.2, heel_angle=20.0)

        self.assertIsNotNone(fig)
        self.assertEqual(len(axes), len(self.profiles))

        plt.close("all")

    def test_plot_multiple_profiles_custom_stations(self):
        """Test with custom station labels."""
        stations = [f"Station {i}" for i in range(len(self.profiles))]
        fig, axes = plot_multiple_profiles(self.profiles, stations=stations)

        self.assertIsNotNone(fig)

        plt.close("all")

    def test_plot_multiple_profiles_single_profile(self):
        """Test with single profile."""
        fig, axes = plot_multiple_profiles([self.profiles[0]])

        self.assertIsNotNone(fig)
        self.assertEqual(len(axes), 1)

        plt.close("all")

    def test_plot_multiple_profiles_empty_list(self):
        """Test with empty profile list."""
        with self.assertRaises(ValueError):
            plot_multiple_profiles([])

    def test_plot_multiple_profiles_custom_figsize(self):
        """Test with custom figure size."""
        fig, axes = plot_multiple_profiles(self.profiles, figsize=(15, 10))

        self.assertIsNotNone(fig)

        plt.close("all")


class TestPlotHull3D(unittest.TestCase):
    """Test plot_hull_3d() function."""

    def setUp(self):
        """Create test hull."""
        self.hull = KayakHull()

        # Add profiles along length
        for x_pos in np.linspace(0, 4, 7):
            points = [
                Point3D(x_pos, -0.6, 0.1),
                Point3D(x_pos, -0.6, -0.5),
                Point3D(x_pos, 0.6, -0.5),
                Point3D(x_pos, 0.6, 0.1),
            ]
            self.hull.add_profile(Profile(station=x_pos, points=points))

    def test_plot_hull_3d_basic(self):
        """Test basic 3D hull plotting."""
        ax = plot_hull_3d(self.hull)

        self.assertIsNotNone(ax)
        # Should have multiple lines for profiles and longitudinal connections
        self.assertGreater(len(ax.lines), 0)

        plt.close("all")

    def test_plot_hull_3d_wireframe(self):
        """Test wireframe view mode."""
        ax = plot_hull_3d(self.hull, view_mode="wireframe")

        self.assertIsNotNone(ax)

        plt.close("all")

    def test_plot_hull_3d_with_waterline(self):
        """Test with waterline plane."""
        ax = plot_hull_3d(self.hull, waterline_z=-0.2, show_waterline_plane=True)

        self.assertIsNotNone(ax)

        plt.close("all")

    def test_plot_hull_3d_without_waterline(self):
        """Test without waterline plane."""
        ax = plot_hull_3d(self.hull, show_waterline_plane=False)

        self.assertIsNotNone(ax)

        plt.close("all")

    def test_plot_hull_3d_heeled(self):
        """Test heeled hull visualization."""
        ax = plot_hull_3d(self.hull, waterline_z=-0.2, heel_angle=30.0)

        self.assertIsNotNone(ax)

        plt.close("all")

    def test_plot_hull_3d_custom_view_angle(self):
        """Test custom viewing angles."""
        ax = plot_hull_3d(self.hull, elev=30, azim=-45)

        self.assertIsNotNone(ax)

        plt.close("all")

    def test_plot_hull_3d_custom_axes(self):
        """Test plotting on provided 3D axes."""

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        result_ax = plot_hull_3d(self.hull, ax=ax)

        self.assertIs(result_ax, ax)

        plt.close("all")

    def test_plot_hull_3d_empty_hull(self):
        """Test with empty hull."""
        empty_hull = KayakHull()

        with self.assertRaises(ValueError):
            plot_hull_3d(empty_hull)

    def test_plot_hull_3d_invalid_view_mode(self):
        """Test with invalid view mode."""
        with self.assertRaises(ValueError):
            plot_hull_3d(self.hull, view_mode="invalid")


class TestPlotProfileWithProperties(unittest.TestCase):
    """Test plot_profile_with_properties() function."""

    def setUp(self):
        """Create test profile."""
        self.profile = Profile(
            station=2.0,
            points=[
                Point3D(2.0, -0.6, 0.2),
                Point3D(2.0, -0.6, -0.4),
                Point3D(2.0, 0.6, -0.4),
                Point3D(2.0, 0.6, 0.2),
            ],
        )

    def test_plot_profile_with_properties_basic(self):
        """Test basic annotated profile plotting."""
        ax = plot_profile_with_properties(self.profile, waterline_z=-0.1)

        self.assertIsNotNone(ax)

        plt.close("all")

    def test_plot_profile_with_centroid(self):
        """Test plotting with centroid marker."""
        ax = plot_profile_with_properties(self.profile, waterline_z=0.0, show_centroid=True)

        self.assertIsNotNone(ax)
        # Should have additional markers for centroid
        self.assertGreater(len(ax.lines), 2)

        plt.close("all")

    def test_plot_profile_with_area(self):
        """Test plotting with area annotation."""
        ax = plot_profile_with_properties(self.profile, waterline_z=0.0, show_area=True)

        self.assertIsNotNone(ax)
        # Should have text annotation for area
        self.assertGreater(len(ax.texts), 0)

        plt.close("all")

    def test_plot_profile_with_intersections(self):
        """Test plotting with waterline intersections marked."""
        ax = plot_profile_with_properties(
            self.profile, waterline_z=0.0, show_waterline_intersection=True
        )

        self.assertIsNotNone(ax)

        plt.close("all")

    def test_plot_profile_with_all_properties(self):
        """Test plotting with all properties shown."""
        ax = plot_profile_with_properties(
            self.profile,
            waterline_z=-0.1,
            show_centroid=True,
            show_area=True,
            show_waterline_intersection=True,
        )

        self.assertIsNotNone(ax)

        plt.close("all")

    def test_plot_profile_with_properties_heeled(self):
        """Test annotated plot with heel angle."""
        ax = plot_profile_with_properties(
            self.profile, waterline_z=-0.1, heel_angle=25.0, show_centroid=True, show_area=True
        )

        self.assertIsNotNone(ax)

        plt.close("all")


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""

    def test_configure_plot_style(self):
        """Test plot style configuration."""
        configure_plot_style(grid=True)

        # Just verify it runs without error
        self.assertTrue(True)

    def test_configure_plot_style_no_grid(self):
        """Test style configuration without grid."""
        configure_plot_style(grid=False)

        self.assertTrue(True)

    def test_save_figure(self):
        """Test figure saving."""
        # Create a simple figure
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])

        # Save to temporary location
        output_path = Path("tests/output/test_figure.png")
        save_figure(fig, output_path, dpi=100)

        # Check file exists
        self.assertTrue(output_path.exists())

        # Clean up
        output_path.unlink()

        plt.close("all")

    def test_save_figure_creates_directory(self):
        """Test that save_figure creates parent directories."""
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])

        # Save to nested path that doesn't exist
        output_path = Path("tests/output/nested/deep/test_figure.png")
        save_figure(fig, output_path, dpi=100)

        # Check file exists
        self.assertTrue(output_path.exists())

        # Clean up
        output_path.unlink()
        output_path.parent.rmdir()
        output_path.parent.parent.rmdir()

        plt.close("all")

    def test_save_figure_string_path(self):
        """Test saving with string path."""
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])

        # Save using string path
        output_path = "tests/output/test_figure_str.png"
        save_figure(fig, output_path)

        # Check file exists
        self.assertTrue(Path(output_path).exists())

        # Clean up
        Path(output_path).unlink()

        plt.close("all")


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple functions."""

    def test_full_workflow(self):
        """Test complete workflow from hull creation to visualization."""
        # Create hull
        hull = KayakHull()
        for x_pos in [0.0, 2.0, 4.0]:
            points = [
                Point3D(x_pos, -0.5, 0.1),
                Point3D(x_pos, -0.5, -0.3),
                Point3D(x_pos, 0.5, -0.3),
                Point3D(x_pos, 0.5, 0.1),
            ]
            hull.add_profile(Profile(station=x_pos, points=points))

        # Plot single profile
        profile = hull.get_profile(2.0)
        ax1 = plot_profile(profile, waterline_z=-0.1)
        self.assertIsNotNone(ax1)

        # Plot multiple profiles
        profiles = [hull.get_profile(x) for x in [0.0, 2.0, 4.0]]
        fig2, axes2 = plot_multiple_profiles(profiles, waterline_z=-0.1)
        self.assertIsNotNone(fig2)
        self.assertEqual(len(axes2), 3)

        # Plot 3D hull
        ax3 = plot_hull_3d(hull, waterline_z=-0.1)
        self.assertIsNotNone(ax3)

        # Plot profile with properties
        ax4 = plot_profile_with_properties(
            profile, waterline_z=-0.1, show_centroid=True, show_area=True
        )
        self.assertIsNotNone(ax4)

        plt.close("all")


class TestStabilityCurvePlotting(unittest.TestCase):
    """Test stability curve plotting functions."""

    def setUp(self):
        """Create test hull and stability data."""
        # Create simple hull
        self.hull = KayakHull()
        for x_pos in np.linspace(0, 4, 7):
            points = [
                Point3D(x_pos, -0.6, 0.1),
                Point3D(x_pos, -0.6, -0.5),
                Point3D(x_pos, 0.6, -0.5),
                Point3D(x_pos, 0.6, 0.1),
            ]
            self.hull.add_profile(Profile(station=x_pos, points=points))

        # Create CG and analyzer
        self.cg = CenterOfGravity(lcg=2.0, vcg=-0.3, tcg=0.0, total_mass=100.0, num_components=1)
        self.analyzer = StabilityAnalyzer(self.hull, self.cg, waterline_z=-0.2)

        # Generate stability curve
        self.curve = self.analyzer.generate_stability_curve(max_angle=60.0, angle_step=5.0)
        self.metrics = self.analyzer.analyze_stability(self.curve)

    def test_plot_stability_curve_basic(self):
        """Test basic stability curve plotting."""
        ax = plot_stability_curve(self.curve)

        self.assertIsNotNone(ax)
        self.assertGreater(len(ax.lines), 0)

        plt.close("all")

    def test_plot_stability_curve_with_metrics(self):
        """Test stability curve with metrics display."""
        ax = plot_stability_curve(self.curve, self.metrics, show_metrics=True)

        self.assertIsNotNone(ax)
        # Should have text annotations
        self.assertGreater(len(ax.texts), 0)

        plt.close("all")

    def test_plot_stability_curve_no_metrics(self):
        """Test stability curve without metrics object."""
        ax = plot_stability_curve(self.curve, show_metrics=False)

        self.assertIsNotNone(ax)

        plt.close("all")

    def test_plot_stability_curve_mark_key_points(self):
        """Test marking key points on stability curve."""
        ax = plot_stability_curve(self.curve, self.metrics, mark_key_points=True)

        self.assertIsNotNone(ax)
        # Should have markers for key points
        self.assertGreater(len(ax.lines), 1)

        plt.close("all")

    def test_plot_stability_curve_custom_axes(self):
        """Test plotting on provided axes."""
        fig, ax = plt.subplots()
        result_ax = plot_stability_curve(self.curve, ax=ax)

        self.assertIs(result_ax, ax)

        plt.close("all")

    def test_plot_stability_curve_custom_colors(self):
        """Test custom color options."""
        ax = plot_stability_curve(
            self.curve, curve_color="red", positive_fill_color="yellow", max_gz_color="blue"
        )

        self.assertIsNotNone(ax)

        plt.close("all")

    def test_plot_multiple_stability_curves(self):
        """Test plotting multiple curves."""
        # Create second curve with different CG
        cg2 = CenterOfGravity(lcg=2.0, vcg=-0.2, tcg=0.0, total_mass=100.0, num_components=1)
        analyzer2 = StabilityAnalyzer(self.hull, cg2, waterline_z=-0.2)
        curve2 = analyzer2.generate_stability_curve(max_angle=60.0, angle_step=5.0)

        ax = plot_multiple_stability_curves([self.curve, curve2], labels=["CG Low", "CG High"])

        self.assertIsNotNone(ax)
        self.assertGreater(len(ax.lines), 2)  # At least 2 curves plus zero line

        plt.close("all")

    def test_plot_multiple_stability_curves_no_labels(self):
        """Test multiple curves without custom labels."""
        curve2 = self.curve  # Use same curve twice for testing

        ax = plot_multiple_stability_curves([self.curve, curve2])

        self.assertIsNotNone(ax)

        plt.close("all")

    def test_plot_stability_curve_with_areas(self):
        """Test stability curve with shaded areas."""
        ax = plot_stability_curve_with_areas(self.curve, self.metrics)

        self.assertIsNotNone(ax)
        # Should have additional annotations for areas
        self.assertGreater(len(ax.texts), 0)

        plt.close("all")

    def test_plot_stability_curve_with_slope(self):
        """Test stability curve with initial slope line."""
        ax = plot_stability_curve_with_areas(self.curve, self.metrics, show_slope=True)

        self.assertIsNotNone(ax)
        # Should have tangent line
        self.assertGreater(len(ax.lines), 1)

        plt.close("all")

    def test_plot_gz_at_angles(self):
        """Test GZ bar chart at specific angles."""
        angles = [0, 15, 30, 45, 60]
        ax = plot_gz_at_angles(self.curve, angles)

        self.assertIsNotNone(ax)
        # Should have bars
        self.assertGreater(len(ax.patches), 0)

        plt.close("all")

    def test_plot_gz_at_angles_custom_colors(self):
        """Test GZ bar chart with custom colors."""
        angles = [0, 15, 30, 45]
        ax = plot_gz_at_angles(self.curve, angles, positive_color="blue", negative_color="orange")

        self.assertIsNotNone(ax)

        plt.close("all")

    def test_plot_righting_moment_curve(self):
        """Test righting moment curve plotting."""
        ax = plot_righting_moment_curve(self.curve, displacement_mass=100.0)

        self.assertIsNotNone(ax)
        self.assertGreater(len(ax.lines), 0)

        plt.close("all")

    def test_plot_righting_moment_curve_custom_g(self):
        """Test righting moment with custom gravity."""
        ax = plot_righting_moment_curve(self.curve, displacement_mass=100.0, g=10.0)

        self.assertIsNotNone(ax)

        plt.close("all")

    def test_create_stability_report_plot(self):
        """Test comprehensive stability report creation."""
        fig, axes_dict = create_stability_report_plot(self.curve, self.metrics, hull=self.hull)

        self.assertIsNotNone(fig)
        self.assertIn("stability_curve", axes_dict)
        self.assertIn("metrics_table", axes_dict)

        plt.close("all")

    def test_create_stability_report_plot_no_hull(self):
        """Test stability report without hull."""
        fig, axes_dict = create_stability_report_plot(self.curve, self.metrics)

        self.assertIsNotNone(fig)
        self.assertIn("stability_curve", axes_dict)

        plt.close("all")


class TestStabilityCurveIntegration(unittest.TestCase):
    """Integration tests for stability curve plotting."""

    def test_full_stability_workflow(self):
        """Test complete workflow from analysis to plotting."""
        # Create hull
        hull = KayakHull()
        for x_pos in [0.0, 2.0, 4.0]:
            points = [
                Point3D(x_pos, -0.5, 0.1),
                Point3D(x_pos, -0.5, -0.3),
                Point3D(x_pos, 0.5, -0.3),
                Point3D(x_pos, 0.5, 0.1),
            ]
            hull.add_profile(Profile(station=x_pos, points=points))

        # Create analyzer and generate curve
        cg = CenterOfGravity(lcg=2.0, vcg=-0.25, tcg=0.0, total_mass=80.0, num_components=1)
        analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.15)
        curve = analyzer.generate_stability_curve(max_angle=50.0, angle_step=5.0)
        metrics = analyzer.analyze_stability(curve)

        # Test all plotting functions
        ax1 = plot_stability_curve(curve, metrics)
        self.assertIsNotNone(ax1)

        ax2 = plot_stability_curve_with_areas(curve, metrics)
        self.assertIsNotNone(ax2)

        ax3 = plot_gz_at_angles(curve, [0, 10, 20, 30, 40, 50])
        self.assertIsNotNone(ax3)

        ax4 = plot_righting_moment_curve(curve, displacement_mass=80.0)
        self.assertIsNotNone(ax4)

        fig, axes = create_stability_report_plot(curve, metrics, hull)
        self.assertIsNotNone(fig)

        plt.close("all")


class TestInteractiveVisualization(unittest.TestCase):
    """Test interactive visualization functions."""

    def setUp(self):
        """Create test hull and CG for interactive tests."""
        # Create a simple test hull
        self.hull = KayakHull()

        # Add profiles
        for x in [0.0, 1.0, 2.0, 3.0, 4.0]:
            width = 0.6 - abs(x - 2.0) * 0.15
            height = 0.5
            profile = Profile(
                station=x,
                points=[
                    Point3D(x, -width, 0.2),
                    Point3D(x, -width, -height),
                    Point3D(x, width, -height),
                    Point3D(x, width, 0.2),
                ],
            )
            self.hull.add_profile(profile)

        self.cg = Point3D(2.0, 0.0, -0.2)
        self.waterline_z = 0.0

    def test_interactive_heel_explorer_creation(self):
        """Test that interactive_heel_explorer creates figure and widgets."""
        fig = interactive_heel_explorer(self.hull, self.cg, figsize=(12, 8))

        self.assertIsNotNone(fig)
        self.assertIsInstance(fig, plt.Figure)

        # Check that figure has multiple axes
        axes = fig.get_axes()
        self.assertGreater(len(axes), 3)  # Should have 3D, profile, metrics, GZ, slider

        plt.close(fig)

    def test_interactive_heel_explorer_with_parameters(self):
        """Test interactive_heel_explorer with custom parameters."""
        fig = interactive_heel_explorer(
            self.hull,
            self.cg,
            waterline_z=-0.1,
            heel_range=(0.0, 60.0),
            initial_heel=15.0,
            figsize=(14, 9),
        )

        self.assertIsNotNone(fig)
        plt.close(fig)

    def test_interactive_heel_explorer_heel_ranges(self):
        """Test interactive_heel_explorer with different heel ranges."""
        # Test small heel range
        fig1 = interactive_heel_explorer(self.hull, self.cg, heel_range=(0.0, 30.0))
        self.assertIsNotNone(fig1)
        plt.close(fig1)

        # Test large heel range
        fig2 = interactive_heel_explorer(self.hull, self.cg, heel_range=(0.0, 180.0))
        self.assertIsNotNone(fig2)
        plt.close(fig2)

    def test_interactive_stability_curve_creation(self):
        """Test that interactive_stability_curve creates figure."""
        fig = interactive_stability_curve(self.hull, self.cg, figsize=(12, 8))

        self.assertIsNotNone(fig)
        self.assertIsInstance(fig, plt.Figure)

        # Check that figure has multiple axes
        axes = fig.get_axes()
        self.assertGreater(len(axes), 3)  # Should have curve, 3D, profile, metrics

        plt.close(fig)

    def test_interactive_stability_curve_with_custom_angles(self):
        """Test interactive_stability_curve with custom heel angles."""
        heel_angles = np.array([0, 10, 20, 30, 45, 60, 75, 90])

        fig = interactive_stability_curve(self.hull, self.cg, heel_angles=heel_angles)

        self.assertIsNotNone(fig)
        plt.close(fig)

    def test_interactive_stability_curve_different_waterlines(self):
        """Test interactive_stability_curve with different waterlines."""
        fig1 = interactive_stability_curve(self.hull, self.cg, waterline_z=0.0)
        self.assertIsNotNone(fig1)
        plt.close(fig1)

        fig2 = interactive_stability_curve(self.hull, self.cg, waterline_z=-0.2)
        self.assertIsNotNone(fig2)
        plt.close(fig2)

    def test_animate_heel_sequence_creation(self):
        """Test that animate_heel_sequence creates figure and animation."""
        fig, anim = animate_heel_sequence(
            self.hull,
            self.cg,
            n_frames=10,  # Use fewer frames for testing
            interval=200,
            figsize=(12, 8),
        )

        self.assertIsNotNone(fig)
        self.assertIsNotNone(anim)
        self.assertIsInstance(fig, plt.Figure)

        plt.close(fig)

    def test_animate_heel_sequence_with_parameters(self):
        """Test animate_heel_sequence with custom parameters."""
        fig, anim = animate_heel_sequence(
            self.hull, self.cg, waterline_z=-0.1, heel_range=(0.0, 45.0), n_frames=15, interval=150
        )

        self.assertIsNotNone(fig)
        self.assertIsNotNone(anim)
        plt.close(fig)

    def test_animate_heel_sequence_heel_ranges(self):
        """Test animate_heel_sequence with different heel ranges."""
        # Small range
        fig1, anim1 = animate_heel_sequence(self.hull, self.cg, heel_range=(0.0, 30.0), n_frames=10)
        self.assertIsNotNone(fig1)
        plt.close(fig1)

        # Larger range
        fig2, anim2 = animate_heel_sequence(self.hull, self.cg, heel_range=(0.0, 90.0), n_frames=10)
        self.assertIsNotNone(fig2)
        plt.close(fig2)

    def test_interactive_cg_adjustment_creation(self):
        """Test that interactive_cg_adjustment creates figure."""
        fig = interactive_cg_adjustment(self.hull, self.cg, figsize=(12, 8))

        self.assertIsNotNone(fig)
        self.assertIsInstance(fig, plt.Figure)

        # Check that figure has multiple axes
        axes = fig.get_axes()
        self.assertGreater(len(axes), 3)  # Should have curve, original, adjusted, sliders

        plt.close(fig)

    def test_interactive_cg_adjustment_with_ranges(self):
        """Test interactive_cg_adjustment with custom CG ranges."""
        fig = interactive_cg_adjustment(
            self.hull, self.cg, vcg_range=(-0.5, 0.0), lcg_range=(1.5, 2.5)
        )

        self.assertIsNotNone(fig)
        plt.close(fig)

    def test_interactive_cg_adjustment_default_ranges(self):
        """Test interactive_cg_adjustment with default ranges."""
        # Default ranges should be auto-calculated from initial CG
        fig = interactive_cg_adjustment(
            self.hull,
            self.cg,
            vcg_range=None,  # Will use default
            lcg_range=None,  # Will use default
        )

        self.assertIsNotNone(fig)
        plt.close(fig)

    def test_interactive_cg_adjustment_different_waterlines(self):
        """Test interactive_cg_adjustment with different waterlines."""
        fig1 = interactive_cg_adjustment(self.hull, self.cg, waterline_z=0.0)
        self.assertIsNotNone(fig1)
        plt.close(fig1)

        fig2 = interactive_cg_adjustment(self.hull, self.cg, waterline_z=-0.15)
        self.assertIsNotNone(fig2)
        plt.close(fig2)

    def test_interactive_waterline_explorer_creation(self):
        """Test that interactive_waterline_explorer creates figure."""
        fig = interactive_waterline_explorer(self.hull, self.cg, figsize=(12, 8))

        self.assertIsNotNone(fig)
        self.assertIsInstance(fig, plt.Figure)

        # Check that figure has multiple axes
        axes = fig.get_axes()
        self.assertGreater(len(axes), 4)  # Should have 3D, profile, metrics, plot, slider

        plt.close(fig)

    def test_interactive_waterline_explorer_with_parameters(self):
        """Test interactive_waterline_explorer with custom parameters."""
        fig = interactive_waterline_explorer(
            self.hull, self.cg, waterline_range=(-0.3, 0.1), initial_waterline=-0.1, heel_angle=15.0
        )

        self.assertIsNotNone(fig)
        plt.close(fig)

    def test_interactive_waterline_explorer_ranges(self):
        """Test interactive_waterline_explorer with different ranges."""
        # Small range
        fig1 = interactive_waterline_explorer(self.hull, self.cg, waterline_range=(-0.2, 0.0))
        self.assertIsNotNone(fig1)
        plt.close(fig1)

        # Large range
        fig2 = interactive_waterline_explorer(self.hull, self.cg, waterline_range=(-0.6, 0.3))
        self.assertIsNotNone(fig2)
        plt.close(fig2)

    def test_interactive_waterline_explorer_heeled(self):
        """Test interactive_waterline_explorer at different heel angles."""
        fig1 = interactive_waterline_explorer(self.hull, self.cg, heel_angle=0.0)
        self.assertIsNotNone(fig1)
        plt.close(fig1)

        fig2 = interactive_waterline_explorer(self.hull, self.cg, heel_angle=30.0)
        self.assertIsNotNone(fig2)
        plt.close(fig2)

    def test_all_interactive_functions_close_properly(self):
        """Test that all interactive functions can be created and closed."""
        # Create all interactive visualizations
        fig1 = interactive_heel_explorer(self.hull, self.cg, figsize=(10, 6))
        fig2 = interactive_stability_curve(self.hull, self.cg, figsize=(10, 6))
        fig3, anim3 = animate_heel_sequence(self.hull, self.cg, n_frames=5, figsize=(10, 6))
        fig4 = interactive_cg_adjustment(self.hull, self.cg, figsize=(10, 6))
        fig5 = interactive_waterline_explorer(self.hull, self.cg, figsize=(10, 6))

        # Verify all created successfully
        self.assertIsNotNone(fig1)
        self.assertIsNotNone(fig2)
        self.assertIsNotNone(fig3)
        self.assertIsNotNone(fig4)
        self.assertIsNotNone(fig5)

        # Close all
        plt.close("all")

        # Verify no lingering figures
        self.assertEqual(len(plt.get_fignums()), 0)

    def test_interactive_functions_with_minimal_hull(self):
        """Test interactive functions with minimal hull (edge case)."""
        # Create minimal hull with just 2 profiles
        minimal_hull = KayakHull()
        minimal_hull.add_profile(
            Profile(
                0.0,
                [
                    Point3D(0.0, -0.3, 0.1),
                    Point3D(0.0, -0.3, -0.3),
                    Point3D(0.0, 0.3, -0.3),
                    Point3D(0.0, 0.3, 0.1),
                ],
            )
        )
        minimal_hull.add_profile(
            Profile(
                2.0,
                [
                    Point3D(2.0, -0.3, 0.1),
                    Point3D(2.0, -0.3, -0.3),
                    Point3D(2.0, 0.3, -0.3),
                    Point3D(2.0, 0.3, 0.1),
                ],
            )
        )

        cg = Point3D(1.0, 0.0, -0.1)

        # Test each function with minimal hull
        fig1 = interactive_heel_explorer(minimal_hull, cg, figsize=(10, 6))
        self.assertIsNotNone(fig1)
        plt.close(fig1)

        fig2 = interactive_stability_curve(minimal_hull, cg, figsize=(10, 6))
        self.assertIsNotNone(fig2)
        plt.close(fig2)

        fig3, anim3 = animate_heel_sequence(minimal_hull, cg, n_frames=5, figsize=(10, 6))
        self.assertIsNotNone(fig3)
        plt.close(fig3)

        fig4 = interactive_cg_adjustment(minimal_hull, cg, figsize=(10, 6))
        self.assertIsNotNone(fig4)
        plt.close(fig4)

        fig5 = interactive_waterline_explorer(minimal_hull, cg, figsize=(10, 6))
        self.assertIsNotNone(fig5)
        plt.close(fig5)


if __name__ == "__main__":
    unittest.main()
