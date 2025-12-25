"""
Visualization module for plotting and displaying results.

This module contains functions for:
- Profile plotting
- Hull 3D visualization
- Stability curve plotting
- Hydrostatic report generation
- Interactive visualization and animation
"""

from .plots import (
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
    interactive_waterline_explorer
)

__all__ = [
    'plot_profile',
    'plot_multiple_profiles',
    'plot_hull_3d',
    'plot_profile_with_properties',
    'configure_plot_style',
    'save_figure',
    'plot_stability_curve',
    'plot_multiple_stability_curves',
    'plot_stability_curve_with_areas',
    'plot_gz_at_angles',
    'plot_righting_moment_curve',
    'create_stability_report_plot',
    'interactive_heel_explorer',
    'interactive_stability_curve',
    'animate_heel_sequence',
    'interactive_cg_adjustment',
    'interactive_waterline_explorer'
]
