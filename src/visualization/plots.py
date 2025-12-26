"""
Visualization functions for plotting hull profiles and 3D geometry.

This module provides functions for:
- Plotting individual transverse profiles (2D cross-sections)
- Plotting multiple profiles for comparison
- 3D hull visualization (wireframe and surface)
- Annotated plots with geometric properties
- Stability curve plotting (GZ curves and metrics)
- Interactive visualization with widgets and animations
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Polygon, Rectangle
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
from scipy import integrate

from ..geometry import Point3D, Profile, KayakHull
from ..geometry.transformations import apply_heel


def plot_profile(
    profile: Profile,
    waterline_z: float = 0.0,
    heel_angle: float = 0.0,
    show_submerged: bool = True,
    show_waterline: bool = True,
    ax: Optional[Axes] = None,
    title: Optional[str] = None,
    **kwargs
) -> Axes:
    """
    Plot a single transverse profile (cross-section).
    
    Args:
        profile: Profile object to plot
        waterline_z: Z-coordinate of waterline (default: 0.0)
        heel_angle: Heel angle in degrees, positive to starboard (default: 0.0)
        show_submerged: Whether to highlight submerged portion (default: True)
        show_waterline: Whether to draw waterline reference line (default: True)
        ax: Optional matplotlib axes (creates new if None)
        title: Optional plot title (default: f"Profile at Station {profile.station}")
        **kwargs: Additional customization options:
            - profile_color: Color for profile line (default: 'black')
            - profile_linewidth: Line width for profile (default: 2)
            - waterline_color: Color for waterline (default: 'blue')
            - waterline_linestyle: Line style for waterline (default: '--')
            - submerged_color: Color for submerged fill (default: 'lightblue')
            - submerged_alpha: Transparency for submerged fill (default: 0.5)
            - grid: Whether to show grid (default: True)
    
    Returns:
        matplotlib Axes object with the plot
        
    Example:
        >>> profile = Profile(station=2.0, points=[...])
        >>> ax = plot_profile(profile, waterline_z=-0.2, heel_angle=30.0)
        >>> plt.show()
    """
    # Create figure and axes if not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    
    # Extract customization options with defaults
    profile_color = kwargs.get('profile_color', 'black')
    profile_linewidth = kwargs.get('profile_linewidth', 2)
    waterline_color = kwargs.get('waterline_color', 'blue')
    waterline_linestyle = kwargs.get('waterline_linestyle', '--')
    submerged_color = kwargs.get('submerged_color', 'lightblue')
    submerged_alpha = kwargs.get('submerged_alpha', 0.5)
    show_grid = kwargs.get('grid', True)
    
    # Apply heel transformation if needed
    if abs(heel_angle) > 1e-6:
        transformed_points = [
            apply_heel(pt, heel_angle) for pt in profile.points
        ]
    else:
        transformed_points = profile.points
    
    # Extract y and z coordinates
    y_coords = np.array([pt.y for pt in transformed_points])
    z_coords = np.array([pt.z for pt in transformed_points])
    
    # Plot the profile outline
    ax.plot(y_coords, z_coords, color=profile_color, linewidth=profile_linewidth,
            label='Profile', marker='o', markersize=4)
    
    # Show waterline if requested
    if show_waterline:
        y_range = [y_coords.min(), y_coords.max()]
        ax.plot(y_range, [waterline_z, waterline_z], 
                color=waterline_color, linestyle=waterline_linestyle,
                linewidth=1.5, label='Waterline')
    
    # Fill submerged portion if requested
    if show_submerged:
        # Find points below waterline and create filled polygon
        submerged_points = []
        
        for i, (y, z) in enumerate(zip(y_coords, z_coords)):
            if z <= waterline_z:
                submerged_points.append((y, z))
            
            # Check for waterline crossing between consecutive points
            if i < len(y_coords) - 1:
                z_next = z_coords[i + 1]
                y_next = y_coords[i + 1]
                
                # If segment crosses waterline, add intersection point
                if (z <= waterline_z < z_next) or (z_next <= waterline_z < z):
                    # Linear interpolation to find crossing point
                    t = (waterline_z - z) / (z_next - z)
                    y_cross = y + t * (y_next - y)
                    submerged_points.append((y_cross, waterline_z))
        
        # Close the polygon at waterline if we have submerged points
        if len(submerged_points) >= 3:
            # Add waterline endpoints to close the polygon
            y_min = min(pt[0] for pt in submerged_points)
            y_max = max(pt[0] for pt in submerged_points)
            
            # Sort points to create proper polygon
            submerged_array = np.array(submerged_points)
            
            # Create filled polygon
            polygon = Polygon(submerged_array, facecolor=submerged_color,
                            alpha=submerged_alpha, edgecolor='none',
                            label='Submerged')
            ax.add_patch(polygon)
    
    # Set labels and title
    ax.set_xlabel('Transverse Position (y) [m]', fontsize=10)
    ax.set_ylabel('Vertical Position (z) [m]', fontsize=10)
    
    if title is None:
        heel_str = f", Heel={heel_angle:.1f}°" if abs(heel_angle) > 1e-6 else ""
        title = f"Profile at Station x={profile.station:.2f} m{heel_str}"
    ax.set_title(title, fontsize=12)
    
    # Set equal aspect ratio for accurate geometry
    ax.set_aspect('equal', adjustable='box')
    
    # Add grid if requested
    if show_grid:
        ax.grid(True, alpha=0.3)
    
    # Add legend
    ax.legend(loc='best', fontsize=9)
    
    # Add centerline reference (y=0)
    ax.axvline(x=0, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    
    return ax


def plot_multiple_profiles(
    profiles: List[Profile],
    stations: Optional[List[float]] = None,
    waterline_z: float = 0.0,
    heel_angle: float = 0.0,
    ncols: int = 3,
    figsize: Optional[Tuple[float, float]] = None,
    **kwargs
) -> Tuple[plt.Figure, List[Axes]]:
    """
    Plot multiple profiles side-by-side for comparison.
    
    Args:
        profiles: List of Profile objects to plot
        stations: Optional list of station labels (uses profile.station if None)
        waterline_z: Z-coordinate of waterline
        heel_angle: Heel angle in degrees (applied to all profiles)
        ncols: Number of columns in subplot grid (default: 3)
        figsize: Figure size as (width, height) tuple (auto-calculated if None)
        **kwargs: Passed to plot_profile() for customization
    
    Returns:
        Tuple of (Figure, list of Axes objects)
        
    Example:
        >>> profiles = [hull.get_profile(x) for x in [0, 1, 2, 3, 4]]
        >>> fig, axes = plot_multiple_profiles(profiles, waterline_z=-0.2)
        >>> plt.tight_layout()
        >>> plt.show()
    """
    n_profiles = len(profiles)
    if n_profiles == 0:
        raise ValueError("Must provide at least one profile to plot")
    
    # Calculate grid dimensions
    nrows = (n_profiles + ncols - 1) // ncols  # Ceiling division
    
    # Auto-calculate figure size if not provided
    if figsize is None:
        fig_width = 5 * ncols
        fig_height = 4 * nrows
        figsize = (fig_width, fig_height)
    
    # Create figure and subplots
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    
    # Ensure axes is always a flat array
    if nrows == 1 and ncols == 1:
        axes = np.array([axes])
    elif nrows == 1 or ncols == 1:
        axes = np.array(axes).flatten()
    else:
        axes = np.array(axes).flatten()
    
    # Determine consistent axis limits across all profiles
    all_y = []
    all_z = []
    for profile in profiles:
        if abs(heel_angle) > 1e-6:
            transformed_points = [
                apply_heel(pt, heel_angle) for pt in profile.points
            ]
        else:
            transformed_points = profile.points
        
        all_y.extend([pt.y for pt in transformed_points])
        all_z.extend([pt.z for pt in transformed_points])
    
    y_min, y_max = min(all_y), max(all_y)
    z_min, z_max = min(all_z), max(all_z)
    
    # Add margins
    y_margin = (y_max - y_min) * 0.1
    z_margin = (z_max - z_min) * 0.1
    y_lim = (y_min - y_margin, y_max + y_margin)
    z_lim = (z_min - z_margin, z_max + z_margin)
    
    # Plot each profile
    for i, profile in enumerate(profiles):
        ax = axes[i]
        
        # Use provided station labels or profile's station
        if stations is not None and i < len(stations):
            station_label = stations[i]
            # Format title based on label type
            if isinstance(station_label, str):
                title = station_label
            else:
                title = f"x = {station_label:.2f} m"
        else:
            station_label = profile.station
            title = f"x = {station_label:.2f} m"
        
        # Plot profile
        plot_profile(
            profile=profile,
            waterline_z=waterline_z,
            heel_angle=heel_angle,
            ax=ax,
            title=title,
            **kwargs
        )
        
        # Set consistent axis limits
        ax.set_xlim(y_lim)
        ax.set_ylim(z_lim)
    
    # Hide empty subplots
    for i in range(n_profiles, len(axes)):
        axes[i].set_visible(False)
    
    # Overall title
    heel_str = f" (Heel={heel_angle:.1f}°)" if abs(heel_angle) > 1e-6 else ""
    fig.suptitle(f"Hull Profiles{heel_str}", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    return fig, list(axes[:n_profiles])


def plot_hull_3d(
    hull: KayakHull,
    waterline_z: float = 0.0,
    heel_angle: float = 0.0,
    show_waterline_plane: bool = True,
    view_mode: str = 'wireframe',
    ax: Optional[Axes3D] = None,
    figsize: Tuple[float, float] = (12, 8),
    **kwargs
) -> Axes3D:
    """
    Plot hull in 3D view (wireframe or surface).
    
    Args:
        hull: KayakHull object to plot
        waterline_z: Z-coordinate of waterline (default: 0.0)
        heel_angle: Heel angle in degrees (default: 0.0)
        show_waterline_plane: Whether to show waterline plane (default: True)
        view_mode: 'wireframe' or 'surface' (default: 'wireframe')
        ax: Optional 3D axes (creates new if None)
        figsize: Figure size as (width, height) tuple
        **kwargs: Additional customization options:
            - hull_color: Color for hull (default: 'blue')
            - hull_alpha: Transparency for hull (default: 0.7)
            - waterline_alpha: Transparency for waterline plane (default: 0.2)
            - elev: Elevation viewing angle (default: 20)
            - azim: Azimuth viewing angle (default: -60)
    
    Returns:
        matplotlib 3D Axes object
        
    Example:
        >>> hull = KayakHull()
        >>> # ... add profiles to hull ...
        >>> ax = plot_hull_3d(hull, waterline_z=-0.2, heel_angle=30.0)
        >>> plt.show()
    """
    # Validate view mode
    if view_mode not in ['wireframe', 'surface']:
        raise ValueError(f"view_mode must be 'wireframe' or 'surface', got '{view_mode}'")
    
    # Create figure and 3D axes if not provided
    if ax is None:
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111, projection='3d')
    
    # Extract customization options
    hull_color = kwargs.get('hull_color', 'blue')
    hull_alpha = kwargs.get('hull_alpha', 0.7)
    waterline_alpha = kwargs.get('waterline_alpha', 0.2)
    elev = kwargs.get('elev', 20)
    azim = kwargs.get('azim', -60)
    
    # Get sorted stations
    stations = hull.get_stations()
    if len(stations) == 0:
        raise ValueError("Hull has no profiles to plot")
    
    # Apply heel transformation if needed
    def transform_points(points):
        """Apply heel transformation to a list of points."""
        if abs(heel_angle) > 1e-6:
            return [apply_heel(pt, heel_angle) for pt in points]
        return points
    
    # Plot profiles as transverse lines
    for station in stations:
        profile = hull.get_profile(station)
        transformed_points = transform_points(profile.points)
        
        x_coords = np.array([pt.x for pt in transformed_points])
        y_coords = np.array([pt.y for pt in transformed_points])
        z_coords = np.array([pt.z for pt in transformed_points])
        
        ax.plot(x_coords, y_coords, z_coords, color=hull_color,
                linewidth=1.5, alpha=hull_alpha)
    
    # Plot longitudinal lines connecting profiles
    # Find maximum number of points across all profiles
    max_points = max(hull.get_profile(s).num_points for s in stations)
    
    # For each point index, connect across profiles
    for point_idx in range(max_points):
        x_line = []
        y_line = []
        z_line = []
        
        for station in stations:
            profile = hull.get_profile(station)
            if point_idx < profile.num_points:
                transformed_points = transform_points(profile.points)
                pt = transformed_points[point_idx]
                x_line.append(pt.x)
                y_line.append(pt.y)
                z_line.append(pt.z)
        
        if len(x_line) > 1:
            ax.plot(x_line, y_line, z_line, color=hull_color,
                    linewidth=1, alpha=hull_alpha * 0.5)
    
    # Show waterline plane if requested
    if show_waterline_plane:
        # Create a mesh grid for the waterline plane
        x_range = [min(stations), max(stations)]
        
        # Determine y range from all profiles
        all_y = []
        for station in stations:
            profile = hull.get_profile(station)
            transformed_points = transform_points(profile.points)
            all_y.extend([pt.y for pt in transformed_points])
        y_range = [min(all_y), max(all_y)]
        
        # Create mesh grid
        x_plane = np.linspace(x_range[0], x_range[1], 10)
        y_plane = np.linspace(y_range[0], y_range[1], 10)
        X_plane, Y_plane = np.meshgrid(x_plane, y_plane)
        Z_plane = np.full_like(X_plane, waterline_z)
        
        # Plot waterline plane
        ax.plot_surface(X_plane, Y_plane, Z_plane,
                       color='cyan', alpha=waterline_alpha,
                       label='Waterline')
    
    # Set labels
    ax.set_xlabel('Longitudinal (x) [m]', fontsize=10)
    ax.set_ylabel('Transverse (y) [m]', fontsize=10)
    ax.set_zlabel('Vertical (z) [m]', fontsize=10)
    
    # Set title
    heel_str = f", Heel={heel_angle:.1f}°" if abs(heel_angle) > 1e-6 else ""
    ax.set_title(f"3D Hull View{heel_str}", fontsize=12, fontweight='bold')
    
    # Set view angle
    ax.view_init(elev=elev, azim=azim)
    
    # Set equal aspect ratio (approximately)
    # Get data ranges
    all_x = []
    all_y = []
    all_z = []
    for station in stations:
        profile = hull.get_profile(station)
        transformed_points = transform_points(profile.points)
        all_x.extend([pt.x for pt in transformed_points])
        all_y.extend([pt.y for pt in transformed_points])
        all_z.extend([pt.z for pt in transformed_points])
    
    x_range = max(all_x) - min(all_x)
    y_range = max(all_y) - min(all_y)
    z_range = max(all_z) - min(all_z)
    
    max_range = max(x_range, y_range, z_range)
    
    # Set aspect ratio
    ax.set_box_aspect([x_range/max_range, y_range/max_range, z_range/max_range])
    
    return ax


def plot_profile_with_properties(
    profile: Profile,
    waterline_z: float = 0.0,
    heel_angle: float = 0.0,
    show_centroid: bool = True,
    show_area: bool = True,
    show_waterline_intersection: bool = True,
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
    """
    Plot profile with geometric properties annotated.
    
    Args:
        profile: Profile object to plot
        waterline_z: Z-coordinate of waterline
        heel_angle: Heel angle in degrees
        show_centroid: Whether to mark centroid of submerged area (default: True)
        show_area: Whether to annotate submerged area value (default: True)
        show_waterline_intersection: Mark waterline intersection points (default: True)
        ax: Optional matplotlib axes
        **kwargs: Passed to plot_profile() for additional customization
    
    Returns:
        matplotlib Axes object with annotated plot
        
    Example:
        >>> profile = Profile(station=2.0, points=[...])
        >>> ax = plot_profile_with_properties(profile, waterline_z=-0.2)
        >>> plt.show()
    """
    # First, plot the basic profile
    ax = plot_profile(
        profile=profile,
        waterline_z=waterline_z,
        heel_angle=heel_angle,
        ax=ax,
        **kwargs
    )
    
    # Create a working profile with heel transformation if needed
    if abs(heel_angle) > 1e-6:
        # Apply heel to create transformed profile
        transformed_profile = Profile(
            station=profile.station,
            points=[apply_heel(pt, heel_angle) for pt in profile.points]
        )
    else:
        transformed_profile = profile
    
    # Calculate submerged area
    try:
        area = transformed_profile.calculate_area_below_waterline(waterline_z)
        
        if show_area and area > 1e-6:
            # Annotate area value
            ax.text(0.02, 0.98, f"Area: {area:.4f} m²",
                   transform=ax.transAxes,
                   verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                   fontsize=10)
    except Exception:
        area = 0.0
    
    # Calculate and mark centroid
    if show_centroid and area > 1e-6:
        try:
            centroid_y, centroid_z = transformed_profile.calculate_centroid_below_waterline(
                waterline_z
            )
            
            ax.plot(centroid_y, centroid_z, 'rx', markersize=12, 
                   markeredgewidth=3, label='Centroid')
            
            # Add legend entry for centroid
            ax.legend(loc='best', fontsize=9)
            
        except Exception:
            pass  # Skip centroid if calculation fails
    
    # Mark waterline intersection points
    if show_waterline_intersection:
        try:
            intersections = transformed_profile.find_waterline_intersection(waterline_z)
            
            if len(intersections) > 0:
                y_int = [pt.y for pt in intersections]
                z_int = [pt.z for pt in intersections]
                ax.plot(y_int, z_int, 'go', markersize=8,
                       label='Waterline Intersections')
                ax.legend(loc='best', fontsize=9)
                
        except Exception:
            pass  # Skip if intersection calculation fails
    
    return ax


def configure_plot_style(
    grid: bool = True,
    style: str = 'seaborn-v0_8-darkgrid'
) -> None:
    """
    Configure consistent plot styling for all visualizations.
    
    Args:
        grid: Whether to show grid by default (default: True)
        style: Matplotlib style name (default: 'seaborn-v0_8-darkgrid')
    
    Example:
        >>> configure_plot_style()
        >>> # Now all subsequent plots will use this style
    """
    try:
        plt.style.use(style)
    except:
        # If style not available, use default settings
        plt.rcParams['axes.grid'] = grid
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = 'white'


def save_figure(
    fig: plt.Figure,
    filepath: Path,
    dpi: int = 300,
    bbox_inches: str = 'tight',
    **kwargs
) -> None:
    """
    Save figure to file with standard options.
    
    Args:
        fig: Matplotlib Figure object to save
        filepath: Path where to save the figure (Path object or string)
        dpi: Resolution in dots per inch (default: 300)
        bbox_inches: Bounding box behavior (default: 'tight')
        **kwargs: Additional arguments passed to fig.savefig()
    
    Example:
        >>> fig, ax = plt.subplots()
        >>> # ... create plot ...
        >>> save_figure(fig, Path("output/my_plot.png"))
    """
    # Convert to Path object if string
    if isinstance(filepath, str):
        filepath = Path(filepath)
    
    # Create parent directory if it doesn't exist
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Save figure
    fig.savefig(filepath, dpi=dpi, bbox_inches=bbox_inches, **kwargs)
    print(f"Figure saved to: {filepath}")


# ============================================================================
# Stability Curve Plotting Functions
# ============================================================================


def plot_stability_curve(
    curve,  # StabilityCurve type
    metrics=None,  # Optional StabilityMetrics type
    mark_key_points: bool = True,
    show_metrics: bool = True,
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
    """
    Plot a GZ stability curve with key points and metrics.
    
    Args:
        curve: StabilityCurve object containing heel angles and GZ values
        metrics: Optional StabilityMetrics object (calculated if None and show_metrics=True)
        mark_key_points: Whether to mark maximum GZ and vanishing stability (default: True)
        show_metrics: Whether to display metrics text box (default: True)
        ax: Optional matplotlib axes (creates new if None)
        **kwargs: Additional customization options:
            - curve_color: Color for GZ curve (default: 'navy')
            - curve_linewidth: Line width for curve (default: 2.5)
            - positive_fill_color: Color for positive stability region (default: 'lightgreen')
            - positive_fill_alpha: Transparency for positive region (default: 0.3)
            - max_gz_color: Color for max GZ marker (default: 'red')
            - vanishing_color: Color for vanishing stability marker (default: 'orange')
            - grid: Whether to show grid (default: True)
            - title: Custom plot title (default: auto-generated)
    
    Returns:
        matplotlib Axes object with the plot
        
    Example:
        >>> analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.2)
        >>> curve = analyzer.generate_stability_curve()
        >>> metrics = analyzer.analyze_stability(curve)
        >>> ax = plot_stability_curve(curve, metrics)
        >>> plt.show()
    """
    # Create figure and axes if not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # Extract customization options
    curve_color = kwargs.get('curve_color', 'navy')
    curve_linewidth = kwargs.get('curve_linewidth', 2.5)
    positive_fill_color = kwargs.get('positive_fill_color', 'lightgreen')
    positive_fill_alpha = kwargs.get('positive_fill_alpha', 0.3)
    max_gz_color = kwargs.get('max_gz_color', 'red')
    vanishing_color = kwargs.get('vanishing_color', 'orange')
    show_grid = kwargs.get('grid', True)
    custom_title = kwargs.get('title', None)
    
    # Plot the GZ curve
    ax.plot(curve.heel_angles, curve.gz_values, 
           color=curve_color, linewidth=curve_linewidth,
           label='GZ Curve', marker='o', markersize=3)
    
    # Fill positive stability region
    positive_mask = curve.gz_values > 0
    if np.any(positive_mask):
        ax.fill_between(
            curve.heel_angles, 0, curve.gz_values,
            where=positive_mask,
            color=positive_fill_color,
            alpha=positive_fill_alpha,
            label='Positive Stability'
        )
    
    # Plot zero line
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.7)
    
    # Mark key points if requested
    if mark_key_points:
        # Maximum GZ
        max_idx = np.argmax(curve.gz_values)
        max_gz = curve.gz_values[max_idx]
        max_angle = curve.heel_angles[max_idx]
        
        ax.plot(max_angle, max_gz, marker='*', markersize=15,
               color=max_gz_color, markeredgecolor='darkred',
               markeredgewidth=1.5, label='Max GZ', zorder=5)
        
        ax.annotate(
            f'Max GZ\n{max_gz:.4f} m\n@ {max_angle:.1f}°',
            xy=(max_angle, max_gz),
            xytext=(10, 10),
            textcoords='offset points',
            fontsize=9,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', lw=1.5)
        )
        
        # Vanishing stability (zero crossing from positive to negative)
        if np.any(positive_mask):
            positive_indices = np.where(positive_mask)[0]
            if len(positive_indices) > 0:
                last_positive_idx = positive_indices[-1]
                
                # Check if there's a crossing to negative
                if last_positive_idx < len(curve.gz_values) - 1:
                    # Linear interpolation to find zero crossing
                    idx1 = last_positive_idx
                    idx2 = last_positive_idx + 1
                    
                    gz1 = curve.gz_values[idx1]
                    gz2 = curve.gz_values[idx2]
                    angle1 = curve.heel_angles[idx1]
                    angle2 = curve.heel_angles[idx2]
                    
                    # Interpolate zero crossing angle
                    vanishing_angle = angle1 + (angle2 - angle1) * (-gz1) / (gz2 - gz1)
                    
                    ax.plot(vanishing_angle, 0, marker='^', markersize=12,
                           color=vanishing_color, markeredgecolor='darkorange',
                           markeredgewidth=1.5, label='Vanishing Stability', zorder=5)
                    
                    ax.annotate(
                        f'Vanishing\n@ {vanishing_angle:.1f}°',
                        xy=(vanishing_angle, 0),
                        xytext=(10, -30),
                        textcoords='offset points',
                        fontsize=9,
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='orange', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', lw=1.5)
                    )
    
    # Show metrics text box if requested
    if show_metrics:
        # Calculate metrics if not provided
        if metrics is None:
            try:
                # Import here to avoid circular dependency
                from ..stability import analyze_stability
                metrics = analyze_stability(curve)
            except:
                metrics = None
        
        if metrics is not None:
            # Create metrics text
            metrics_text = "Stability Metrics:\n" + "─" * 20 + "\n"
            metrics_text += f"Max GZ:    {metrics.max_gz:.4f} m @ {metrics.angle_of_max_gz:.1f}°\n"
            metrics_text += f"GM:        {metrics.gm_estimate:.4f} m\n"
            
            if metrics.angle_of_vanishing_stability is not None:
                metrics_text += f"Vanishing: {metrics.angle_of_vanishing_stability:.1f}°\n"
            
            if metrics.range_of_positive_stability is not None:
                range_start, range_end = metrics.range_of_positive_stability
                metrics_text += f"Range:     {range_start:.1f}° - {range_end:.1f}°\n"
            
            if hasattr(metrics, 'area_under_curve') and metrics.area_under_curve is not None:
                metrics_text += f"Area:      {metrics.area_under_curve:.4f} m⋅rad"
            
            # Add text box
            ax.text(0.02, 0.98, metrics_text,
                   transform=ax.transAxes,
                   verticalalignment='top',
                   fontfamily='monospace',
                   fontsize=9,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Set labels and title
    ax.set_xlabel('Heel Angle (degrees)', fontsize=11)
    ax.set_ylabel('Righting Arm GZ (m)', fontsize=11)
    
    if custom_title:
        title = custom_title
    else:
        title = 'Stability Curve (GZ vs Heel Angle)'
    ax.set_title(title, fontsize=13, fontweight='bold')
    
    # Grid
    if show_grid:
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.5)
        ax.minorticks_on()
    
    # Legend
    ax.legend(loc='best', fontsize=9, framealpha=0.9)
    
    # Set reasonable y-axis limits
    y_max = max(curve.gz_values) * 1.15
    y_min = min(min(curve.gz_values), 0) * 1.15
    ax.set_ylim(y_min, y_max)
    
    return ax


def plot_multiple_stability_curves(
    curves: List,  # List of StabilityCurve objects
    labels: Optional[List[str]] = None,
    mark_key_points: bool = True,
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
    """
    Compare multiple stability curves on the same axes.
    
    Args:
        curves: List of StabilityCurve objects to compare
        labels: Optional labels for each curve (auto-generated if None)
        mark_key_points: Whether to mark key points for each curve (default: True)
        ax: Optional matplotlib axes (creates new if None)
        **kwargs: Additional customization options:
            - colors: List of colors for curves (default: auto-generated)
            - linewidth: Line width for all curves (default: 2.5)
            - grid: Whether to show grid (default: True)
            - title: Custom plot title
    
    Returns:
        matplotlib Axes object with the plot
        
    Example:
        >>> # Compare different loading conditions
        >>> curve1 = analyzer1.generate_stability_curve()
        >>> curve2 = analyzer2.generate_stability_curve()
        >>> ax = plot_multiple_stability_curves(
        ...     [curve1, curve2],
        ...     labels=['Light Load', 'Heavy Load']
        ... )
        >>> plt.show()
    """
    # Create figure and axes if not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=(11, 7))
    
    # Extract customization options
    colors = kwargs.get('colors', None)
    linewidth = kwargs.get('linewidth', 2.5)
    show_grid = kwargs.get('grid', True)
    custom_title = kwargs.get('title', None)
    
    # Generate default colors if not provided
    if colors is None:
        color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
        colors = [color_cycle[i % len(color_cycle)] for i in range(len(curves))]
    
    # Generate default labels if not provided
    if labels is None:
        labels = [f'Curve {i+1}' for i in range(len(curves))]
    
    # Plot each curve
    for i, (curve, label, color) in enumerate(zip(curves, labels, colors)):
        ax.plot(curve.heel_angles, curve.gz_values,
               color=color, linewidth=linewidth,
               label=label, marker='o', markersize=2)
        
        # Mark max GZ if requested
        if mark_key_points:
            max_idx = np.argmax(curve.gz_values)
            max_gz = curve.gz_values[max_idx]
            max_angle = curve.heel_angles[max_idx]
            
            ax.plot(max_angle, max_gz, marker='*', markersize=12,
                   color=color, markeredgecolor='black',
                   markeredgewidth=0.5, zorder=5)
    
    # Plot zero line
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.7)
    
    # Set labels and title
    ax.set_xlabel('Heel Angle (degrees)', fontsize=11)
    ax.set_ylabel('Righting Arm GZ (m)', fontsize=11)
    
    if custom_title:
        title = custom_title
    else:
        title = 'Stability Curve Comparison'
    ax.set_title(title, fontsize=13, fontweight='bold')
    
    # Grid
    if show_grid:
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax.grid(True, which='minor', alpha=0.15, linestyle=':', linewidth=0.5)
        ax.minorticks_on()
    
    # Legend
    ax.legend(loc='best', fontsize=9, framealpha=0.9)
    
    return ax


def plot_stability_curve_with_areas(
    curve,  # StabilityCurve type
    metrics,  # StabilityMetrics type
    show_slope: bool = True,
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
    """
    Plot stability curve with shaded areas representing dynamic stability.
    
    Args:
        curve: StabilityCurve object
        metrics: StabilityMetrics object with calculated values
        show_slope: Whether to show initial slope (GM tangent line) (default: True)
        ax: Optional matplotlib axes (creates new if None)
        **kwargs: Additional customization options
    
    Returns:
        matplotlib Axes object with the plot
        
    Example:
        >>> curve = analyzer.generate_stability_curve()
        >>> metrics = analyzer.analyze_stability(curve)
        >>> ax = plot_stability_curve_with_areas(curve, metrics)
        >>> plt.show()
    """
    # Start with basic stability curve plot
    ax = plot_stability_curve(curve, metrics, ax=ax, show_metrics=False, **kwargs)
    
    # Shade area under curve (dynamic stability)
    positive_mask = curve.gz_values > 0
    if np.any(positive_mask):
        # Calculate area under curve in radians
        angles_rad = np.radians(curve.heel_angles[positive_mask])
        gz_pos = curve.gz_values[positive_mask]
        
        # Use scipy trapezoid for integration
        area = integrate.trapezoid(gz_pos, angles_rad)
        
        # Add annotation for area
        mid_angle = np.mean(curve.heel_angles[positive_mask])
        mid_gz = np.mean(curve.gz_values[positive_mask]) * 0.5
        
        ax.text(mid_angle, mid_gz,
               f'Dynamic Stability\nArea = {area:.4f} m⋅rad',
               ha='center', va='center',
               fontsize=9,
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    # Show initial slope (GM tangent) if requested
    if show_slope and metrics.gm_estimate is not None:
        # GM is approximately the initial slope: GZ ≈ GM * sin(φ)
        # For small angles: GZ ≈ GM * φ (in radians)
        # Tangent line: GZ = GM * φ_rad = GM * (π/180) * φ_deg
        
        # Plot tangent line for first 10-15 degrees
        angle_range = np.linspace(0, min(15, curve.heel_angles[-1]), 50)
        gz_tangent = metrics.gm_estimate * np.radians(angle_range)
        
        ax.plot(angle_range, gz_tangent, '--',
               color='purple', linewidth=2, alpha=0.7,
               label=f'Initial Slope (GM={metrics.gm_estimate:.4f} m)')
        
        ax.legend(loc='best', fontsize=9, framealpha=0.9)
    
    return ax


def plot_gz_at_angles(
    curve,  # StabilityCurve type
    angles: List[float],
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
    """
    Plot GZ values at specific heel angles as a bar chart.
    
    Args:
        curve: StabilityCurve object
        angles: List of heel angles to display (in degrees)
        ax: Optional matplotlib axes (creates new if None)
        **kwargs: Additional customization options:
            - positive_color: Color for positive GZ bars (default: 'green')
            - negative_color: Color for negative GZ bars (default: 'red')
            - title: Custom plot title
    
    Returns:
        matplotlib Axes object with the plot
        
    Example:
        >>> curve = analyzer.generate_stability_curve()
        >>> ax = plot_gz_at_angles(curve, [0, 15, 30, 45, 60, 75, 90])
        >>> plt.show()
    """
    # Create figure and axes if not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # Extract customization options
    positive_color = kwargs.get('positive_color', 'green')
    negative_color = kwargs.get('negative_color', 'red')
    custom_title = kwargs.get('title', None)
    
    # Interpolate GZ values at specified angles
    gz_values = np.interp(angles, curve.heel_angles, curve.gz_values)
    
    # Color bars by sign
    colors = [positive_color if gz > 0 else negative_color for gz in gz_values]
    
    # Create bar chart
    bars = ax.bar(angles, gz_values, width=5, color=colors, edgecolor='black', linewidth=1)
    
    # Add value labels on bars
    for angle, gz, bar in zip(angles, gz_values, bars):
        height = bar.get_height()
        label_y = height + (0.01 if height > 0 else -0.01)
        va = 'bottom' if height > 0 else 'top'
        
        ax.text(bar.get_x() + bar.get_width()/2, label_y,
               f'{gz:.4f}',
               ha='center', va=va, fontsize=8, fontweight='bold')
    
    # Plot zero line
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
    
    # Set labels and title
    ax.set_xlabel('Heel Angle (degrees)', fontsize=11)
    ax.set_ylabel('Righting Arm GZ (m)', fontsize=11)
    
    if custom_title:
        title = custom_title
    else:
        title = 'GZ Values at Specific Heel Angles'
    ax.set_title(title, fontsize=13, fontweight='bold')
    
    # Set x-axis ticks to match angles
    ax.set_xticks(angles)
    
    # Grid
    ax.grid(True, axis='y', alpha=0.3)
    
    return ax


def plot_righting_moment_curve(
    curve,  # StabilityCurve type
    displacement_mass: float,
    g: float = 9.81,
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
    """
    Plot righting moment curve (GZ × Displacement × g).
    
    The righting moment is the actual restoring moment acting on the hull,
    calculated as M = Δ × g × GZ, where Δ is displacement mass.
    
    Args:
        curve: StabilityCurve object
        displacement_mass: Displacement in kg
        g: Gravitational acceleration in m/s² (default: 9.81)
        ax: Optional matplotlib axes (creates new if None)
        **kwargs: Additional customization options
    
    Returns:
        matplotlib Axes object with the plot
        
    Example:
        >>> curve = analyzer.generate_stability_curve()
        >>> ax = plot_righting_moment_curve(curve, displacement_mass=100.0)
        >>> plt.show()
    """
    # Create figure and axes if not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # Calculate righting moment
    moment_values = curve.gz_values * displacement_mass * g
    
    # Extract customization options
    curve_color = kwargs.get('curve_color', 'darkblue')
    curve_linewidth = kwargs.get('curve_linewidth', 2.5)
    show_grid = kwargs.get('grid', True)
    
    # Plot moment curve
    ax.plot(curve.heel_angles, moment_values,
           color=curve_color, linewidth=curve_linewidth,
           label='Righting Moment', marker='o', markersize=3)
    
    # Fill positive region
    positive_mask = moment_values > 0
    if np.any(positive_mask):
        ax.fill_between(
            curve.heel_angles, 0, moment_values,
            where=positive_mask,
            color='lightcyan', alpha=0.4,
            label='Positive Moment'
        )
    
    # Plot zero line
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.7)
    
    # Mark maximum moment
    max_idx = np.argmax(moment_values)
    max_moment = moment_values[max_idx]
    max_angle = curve.heel_angles[max_idx]
    
    ax.plot(max_angle, max_moment, marker='*', markersize=15,
           color='red', markeredgecolor='darkred',
           markeredgewidth=1.5, label='Max Moment', zorder=5)
    
    # Set labels and title
    ax.set_xlabel('Heel Angle (degrees)', fontsize=11)
    ax.set_ylabel('Righting Moment (N⋅m)', fontsize=11)
    ax.set_title(f'Righting Moment Curve (Displacement = {displacement_mass:.1f} kg)',
                fontsize=13, fontweight='bold')
    
    # Grid
    if show_grid:
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        ax.minorticks_on()
    
    # Legend
    ax.legend(loc='best', fontsize=9, framealpha=0.9)
    
    return ax


def create_stability_report_plot(
    curve,  # StabilityCurve type
    metrics,  # StabilityMetrics type
    hull: Optional[KayakHull] = None,
    figsize: Tuple[float, float] = (14, 10),
    **kwargs
) -> Tuple[plt.Figure, Dict[str, Axes]]:
    """
    Create a comprehensive multi-panel stability report.
    
    Args:
        curve: StabilityCurve object
        metrics: StabilityMetrics object
        hull: Optional KayakHull object for profile plot
        figsize: Figure size as (width, height) tuple
        **kwargs: Additional customization options
    
    Returns:
        Tuple of (Figure, dict of Axes) where dict keys are panel names:
            'stability_curve', 'profiles', 'metrics_table'
            
    Example:
        >>> curve = analyzer.generate_stability_curve()
        >>> metrics = analyzer.analyze_stability(curve)
        >>> fig, axes = create_stability_report_plot(curve, metrics, hull)
        >>> plt.tight_layout()
        >>> plt.show()
    """
    # Create figure with subplots
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    axes_dict = {}
    
    # Main stability curve (top, spanning both columns)
    ax_curve = fig.add_subplot(gs[0, :])
    plot_stability_curve(curve, metrics, ax=ax_curve, **kwargs)
    axes_dict['stability_curve'] = ax_curve
    
    # Profile at key angles (bottom left)
    if hull is not None:
        ax_profiles = fig.add_subplot(gs[1, 0])
        
        # Get midship profile
        stations = hull.get_stations()
        mid_station = stations[len(stations)//2]
        profile = hull.get_profile(mid_station)
        
        # Plot profiles at key angles
        key_angles = [0, metrics.angle_of_max_gz]
        if metrics.angle_of_vanishing_stability:
            key_angles.append(min(metrics.angle_of_vanishing_stability * 0.7, 60))
        
        for angle in key_angles[:2]:  # Plot up to 2 angles
            # This is simplified - would need heel transformation
            pass  # Implementation would plot profile at each angle
        
        ax_profiles.set_title('Profile at Key Angles', fontsize=11, fontweight='bold')
        ax_profiles.text(0.5, 0.5, 'Profile plots\n(implementation can be extended)',
                        ha='center', va='center', transform=ax_profiles.transAxes)
        axes_dict['profiles'] = ax_profiles
    
    # Metrics table (bottom right)
    ax_metrics = fig.add_subplot(gs[1, 1])
    ax_metrics.axis('off')
    
    # Create metrics text table
    metrics_data = [
        ['Metric', 'Value'],
        ['─' * 25, '─' * 15],
        ['Max GZ', f'{metrics.max_gz:.4f} m'],
        ['Angle at Max GZ', f'{metrics.angle_of_max_gz:.1f}°'],
        ['GM Estimate', f'{metrics.gm_estimate:.4f} m'],
    ]
    
    if metrics.angle_of_vanishing_stability:
        metrics_data.append(['Vanishing Angle', f'{metrics.angle_of_vanishing_stability:.1f}°'])
    
    if metrics.range_of_positive_stability:
        r_start, r_end = metrics.range_of_positive_stability
        metrics_data.append(['Stability Range', f'{r_start:.1f}° - {r_end:.1f}°'])
    
    if hasattr(metrics, 'area_under_curve') and metrics.area_under_curve:
        metrics_data.append(['Area Under Curve', f'{metrics.area_under_curve:.4f} m⋅rad'])
    
    # Create table
    table = ax_metrics.table(
        cellText=metrics_data,
        cellLoc='left',
        loc='center',
        colWidths=[0.6, 0.4]
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style header row
    for i in range(2):
        cell = table[(0, i)]
        cell.set_facecolor('#4CAF50')
        cell.set_text_props(weight='bold', color='white')
    
    # Style separator row
    for i in range(2):
        cell = table[(1, i)]
        cell.set_facecolor('#E8E8E8')
    
    ax_metrics.set_title('Stability Metrics Summary', fontsize=11, fontweight='bold')
    axes_dict['metrics_table'] = ax_metrics
    
    # Overall title
    fig.suptitle('Comprehensive Stability Report', fontsize=15, fontweight='bold', y=0.98)
    
    return fig, axes_dict


# ============================================================================
# Interactive Visualization Functions
# ============================================================================


def interactive_heel_explorer(
    hull: KayakHull,
    cg: Point3D,
    waterline_z: float = 0.0,
    heel_range: Tuple[float, float] = (0.0, 90.0),
    initial_heel: float = 0.0,
    figsize: Tuple[float, float] = (16, 10)
) -> plt.Figure:
    """
    Create an interactive heel angle explorer with slider control.
    
    This function creates a multi-panel interactive visualization that updates
    in real-time as the user adjusts the heel angle slider. It displays:
    - 3D hull view at the current heel angle
    - Cross-section profile view
    - Real-time stability metrics (GZ, GM, etc.)
    - Center of buoyancy and center of gravity positions
    
    Args:
        hull: KayakHull object containing hull geometry
        cg: Point3D representing the center of gravity
        waterline_z: Z-coordinate of waterline (default: 0.0)
        heel_range: Tuple of (min_heel, max_heel) in degrees (default: (0.0, 90.0))
        initial_heel: Initial heel angle in degrees (default: 0.0)
        figsize: Figure size as (width, height) in inches (default: (16, 10))
    
    Returns:
        matplotlib Figure object with interactive controls
        
    Example:
        >>> hull = KayakHull()
        >>> # ... add profiles to hull ...
        >>> cg = Point3D(2.0, 0.0, -0.2)
        >>> fig = interactive_heel_explorer(hull, cg)
        >>> plt.show()  # Must use interactive backend
        
    Note:
        - Requires an interactive matplotlib backend (e.g., TkAgg, Qt5Agg)
        - Call plt.show() to display the interactive plot
        - Slider updates all views in real-time
    """
    from ..hydrostatics import calculate_volume, calculate_center_of_buoyancy
    from ..stability import calculate_gz, analyze_stability
    
    # Create figure with subplots
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3, 
                          left=0.08, right=0.95, top=0.93, bottom=0.15)
    
    # Create axes
    ax_3d = fig.add_subplot(gs[0:2, 0:2], projection='3d')
    ax_profile = fig.add_subplot(gs[0, 2])
    ax_metrics = fig.add_subplot(gs[1, 2])
    ax_gz = fig.add_subplot(gs[2, :])
    
    # Calculate initial stability curve for reference
    heel_angles = np.linspace(heel_range[0], heel_range[1], 50)
    gz_values = []
    for angle in heel_angles:
        try:
            gz = calculate_gz(hull, cg, waterline_z, angle)
            gz_values.append(gz)
        except:
            gz_values.append(np.nan)
    gz_values = np.array(gz_values)
    
    # Plot stability curve (static)
    ax_gz.plot(heel_angles, gz_values, 'b-', linewidth=2, label='GZ Curve')
    ax_gz.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    ax_gz.grid(True, alpha=0.3)
    ax_gz.set_xlabel('Heel Angle (degrees)', fontsize=10)
    ax_gz.set_ylabel('GZ (m)', fontsize=10)
    ax_gz.set_title('Stability Curve', fontsize=11, fontweight='bold')
    ax_gz.legend()
    
    # Create indicator line for current heel angle
    current_line = ax_gz.axvline(x=initial_heel, color='red', linestyle='--', 
                                  linewidth=2, label='Current Angle')
    ax_gz.legend()
    
    # Storage for plot elements that will be updated
    plot_elements = {
        '3d_lines': [],
        'profile_lines': [],
        'text_objects': []
    }
    
    def update(heel_angle):
        """Update all plots for new heel angle."""
        # Clear previous elements
        ax_3d.clear()
        ax_profile.clear()
        ax_metrics.clear()
        
        # Update 3D hull view
        plot_hull_3d(hull, waterline_z=waterline_z, heel_angle=heel_angle,
                    ax=ax_3d, title=f'Hull at {heel_angle:.1f}° Heel')
        
        # Update profile view
        # Get midship or representative profile
        stations = sorted(hull.profiles.keys())
        mid_station = stations[len(stations) // 2]
        profile = hull.get_profile(mid_station)
        plot_profile(profile, waterline_z=waterline_z, heel_angle=heel_angle,
                    ax=ax_profile, title=f'Profile at Station {mid_station:.2f}')
        
        # Calculate and display metrics
        try:
            gz = calculate_gz(hull, cg, waterline_z, heel_angle)
            cb = calculate_center_of_buoyancy(hull, waterline_z, heel_angle)
            volume = calculate_volume(hull, waterline_z, heel_angle)
            
            if abs(heel_angle) < 5.0:
                try:
                    metrics = analyze_stability(hull, cg, waterline_z)
                    gm_text = f'{metrics.gm_estimate:.4f} m' if metrics.gm_estimate else 'N/A'
                except:
                    gm_text = 'N/A'
            else:
                gm_text = 'N/A (>5°)'
            
            metrics_text = f"""
Heel Angle: {heel_angle:.2f}°

Stability Metrics:
  GZ: {gz:.4f} m
  GM: {gm_text}
  
Center of Buoyancy:
  X: {cb.x:.4f} m
  Y: {cb.y:.4f} m
  Z: {cb.z:.4f} m
  
Center of Gravity:
  X: {cg.x:.4f} m
  Y: {cg.y:.4f} m
  Z: {cg.z:.4f} m
  
Displacement:
  Volume: {volume:.4f} m³
            """
        except Exception as e:
            metrics_text = f"""
Heel Angle: {heel_angle:.2f}°

Error calculating metrics:
{str(e)[:100]}
            """
        
        ax_metrics.text(0.05, 0.95, metrics_text, transform=ax_metrics.transAxes,
                       fontsize=9, verticalalignment='top', family='monospace')
        ax_metrics.axis('off')
        
        # Update current angle line
        current_line.set_xdata([heel_angle, heel_angle])
        
        fig.canvas.draw_idle()
    
    # Create slider
    ax_slider = plt.axes([0.15, 0.05, 0.7, 0.03])
    slider = Slider(ax_slider, 'Heel Angle (°)', heel_range[0], heel_range[1],
                   valinit=initial_heel, valstep=0.5)
    slider.on_changed(update)
    
    # Initial update
    update(initial_heel)
    
    fig.suptitle('Interactive Heel Angle Explorer', fontsize=14, fontweight='bold')
    
    return fig


def interactive_stability_curve(
    hull: KayakHull,
    cg: Point3D,
    waterline_z: float = 0.0,
    heel_angles: Optional[np.ndarray] = None,
    figsize: Tuple[float, float] = (16, 10)
) -> plt.Figure:
    """
    Create an interactive stability curve with clickable point selection.
    
    This function creates a visualization where users can click on points along
    the stability curve to see detailed information about the hull at that heel
    angle, including 3D visualization, cross-section, and numerical values.
    
    Args:
        hull: KayakHull object containing hull geometry
        cg: Point3D representing the center of gravity
        waterline_z: Z-coordinate of waterline (default: 0.0)
        heel_angles: Array of heel angles to calculate. If None, uses 0° to 90°
                    with 1° increments (default: None)
        figsize: Figure size as (width, height) in inches (default: (16, 10))
    
    Returns:
        matplotlib Figure object with interactive controls
        
    Example:
        >>> hull = KayakHull()
        >>> # ... add profiles to hull ...
        >>> cg = Point3D(2.0, 0.0, -0.2)
        >>> fig = interactive_stability_curve(hull, cg)
        >>> plt.show()  # Must use interactive backend
        
    Note:
        - Requires an interactive matplotlib backend
        - Click on any point on the GZ curve to see details
        - Hover over curve to see tooltip with heel angle and GZ value
    """
    from ..hydrostatics import calculate_volume, calculate_center_of_buoyancy
    from ..stability import calculate_gz, analyze_stability
    
    # Default heel angles if not provided
    if heel_angles is None:
        heel_angles = np.arange(0.0, 91.0, 1.0)
    
    # Calculate stability curve
    gz_values = []
    for angle in heel_angles:
        try:
            gz = calculate_gz(hull, cg, waterline_z, angle)
            gz_values.append(gz)
        except:
            gz_values.append(np.nan)
    gz_values = np.array(gz_values)
    
    # Create figure with subplots
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3,
                          left=0.08, right=0.95, top=0.93, bottom=0.08)
    
    # Create axes
    ax_curve = fig.add_subplot(gs[:, 0])
    ax_3d = fig.add_subplot(gs[0, 1:], projection='3d')
    ax_profile = fig.add_subplot(gs[1, 1])
    ax_metrics = fig.add_subplot(gs[1, 2])
    
    # Plot stability curve
    line, = ax_curve.plot(heel_angles, gz_values, 'b-', linewidth=2, 
                          marker='o', markersize=3, label='GZ Curve',
                          picker=5)  # Enable picking within 5 points
    ax_curve.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    ax_curve.grid(True, alpha=0.3)
    ax_curve.set_xlabel('Heel Angle (degrees)', fontsize=11)
    ax_curve.set_ylabel('GZ (m)', fontsize=11)
    ax_curve.set_title('Stability Curve\n(Click on curve to see details)', 
                      fontsize=11, fontweight='bold')
    ax_curve.legend()
    
    # Marker for selected point
    selected_point, = ax_curve.plot([], [], 'ro', markersize=10, 
                                    label='Selected', zorder=5)
    
    # State variable
    state = {'current_heel': 0.0}
    
    def update_details(heel_angle):
        """Update detail views for selected heel angle."""
        ax_3d.clear()
        ax_profile.clear()
        ax_metrics.clear()
        
        # Update marker on curve
        try:
            gz = calculate_gz(hull, cg, waterline_z, heel_angle)
            selected_point.set_data([heel_angle], [gz])
        except:
            selected_point.set_data([], [])
        
        # Update 3D hull view
        plot_hull_3d(hull, waterline_z=waterline_z, heel_angle=heel_angle,
                    ax=ax_3d, title=f'Hull at {heel_angle:.1f}° Heel')
        
        # Update profile view
        stations = sorted(hull.profiles.keys())
        mid_station = stations[len(stations) // 2]
        profile = hull.get_profile(mid_station)
        plot_profile(profile, waterline_z=waterline_z, heel_angle=heel_angle,
                    ax=ax_profile, title=f'Profile at Station {mid_station:.2f}')
        
        # Calculate and display metrics
        try:
            gz = calculate_gz(hull, cg, waterline_z, heel_angle)
            cb = calculate_center_of_buoyancy(hull, waterline_z, heel_angle)
            volume = calculate_volume(hull, waterline_z, heel_angle)
            
            if abs(heel_angle) < 5.0:
                try:
                    metrics = analyze_stability(hull, cg, waterline_z)
                    gm_text = f'{metrics.gm_estimate:.4f} m' if metrics.gm_estimate else 'N/A'
                except:
                    gm_text = 'N/A'
            else:
                gm_text = 'N/A (>5°)'
            
            metrics_text = f"""
Heel Angle: {heel_angle:.2f}°

Stability Metrics:
  GZ: {gz:.4f} m
  GM: {gm_text}
  
Center of Buoyancy:
  X: {cb.x:.4f} m
  Y: {cb.y:.4f} m
  Z: {cb.z:.4f} m
  
Displacement:
  Volume: {volume:.4f} m³
            """
        except Exception as e:
            metrics_text = f"""
Heel Angle: {heel_angle:.2f}°

Error: {str(e)[:80]}
            """
        
        ax_metrics.text(0.05, 0.95, metrics_text, transform=ax_metrics.transAxes,
                       fontsize=9, verticalalignment='top', family='monospace')
        ax_metrics.axis('off')
        
        state['current_heel'] = heel_angle
        fig.canvas.draw_idle()
    
    def on_pick(event):
        """Handle pick event on stability curve."""
        if event.artist == line:
            # Get the index of the picked point
            ind = event.ind[0]
            heel_angle = heel_angles[ind]
            update_details(heel_angle)
    
    # Connect pick event
    fig.canvas.mpl_connect('pick_event', on_pick)
    
    # Initial update with heel angle = 0
    update_details(0.0)
    
    fig.suptitle('Interactive Stability Curve Explorer', fontsize=14, fontweight='bold')
    
    return fig


def animate_heel_sequence(
    hull: KayakHull,
    cg: Point3D,
    waterline_z: float = 0.0,
    heel_range: Tuple[float, float] = (0.0, 90.0),
    n_frames: int = 90,
    interval: int = 100,
    figsize: Tuple[float, float] = (16, 10),
    save_path: Optional[Path] = None
) -> Tuple[plt.Figure, FuncAnimation]:
    """
    Create an animated heel sequence with playback controls.
    
    This function creates a smooth animation showing the hull heeling through
    a range of angles. The animation includes:
    - 3D hull view rotating through heel angles
    - Synchronized GZ curve with moving indicator
    - Profile view animation
    - Real-time stability metrics
    
    Args:
        hull: KayakHull object containing hull geometry
        cg: Point3D representing the center of gravity
        waterline_z: Z-coordinate of waterline (default: 0.0)
        heel_range: Tuple of (start_heel, end_heel) in degrees (default: (0.0, 90.0))
        n_frames: Number of animation frames (default: 90)
        interval: Delay between frames in milliseconds (default: 100)
        figsize: Figure size as (width, height) in inches (default: (16, 10))
        save_path: Optional path to save animation (MP4 or GIF) (default: None)
    
    Returns:
        Tuple of (Figure, FuncAnimation) objects
        
    Example:
        >>> hull = KayakHull()
        >>> # ... add profiles to hull ...
        >>> cg = Point3D(2.0, 0.0, -0.2)
        >>> fig, anim = animate_heel_sequence(hull, cg, save_path=Path('heel.mp4'))
        >>> plt.show()
        
    Note:
        - Requires an interactive matplotlib backend for display
        - Saving to MP4 requires ffmpeg
        - Saving to GIF requires pillow or imagemagick
        - Animation can be CPU-intensive for complex hulls
    """
    from ..hydrostatics import calculate_volume, calculate_center_of_buoyancy
    from ..stability import calculate_gz, analyze_stability
    
    # Create heel angles for animation
    heel_angles = np.linspace(heel_range[0], heel_range[1], n_frames)
    
    # Pre-calculate stability curve for all angles
    gz_values = []
    for angle in heel_angles:
        try:
            gz = calculate_gz(hull, cg, waterline_z, angle)
            gz_values.append(gz)
        except:
            gz_values.append(np.nan)
    gz_values = np.array(gz_values)
    
    # Create figure with subplots
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3,
                          left=0.08, right=0.95, top=0.93, bottom=0.12)
    
    # Create axes
    ax_3d = fig.add_subplot(gs[0:2, 0:2], projection='3d')
    ax_profile = fig.add_subplot(gs[0, 2])
    ax_metrics = fig.add_subplot(gs[1, 2])
    ax_gz = fig.add_subplot(gs[2, :])
    
    # Plot stability curve (static)
    ax_gz.plot(heel_angles, gz_values, 'b-', linewidth=2, alpha=0.5, label='Full Curve')
    ax_gz.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    ax_gz.grid(True, alpha=0.3)
    ax_gz.set_xlabel('Heel Angle (degrees)', fontsize=10)
    ax_gz.set_ylabel('GZ (m)', fontsize=10)
    ax_gz.set_title('Stability Curve Animation', fontsize=11, fontweight='bold')
    
    # Create animated elements
    curve_line, = ax_gz.plot([], [], 'b-', linewidth=3, label='Current')
    current_point, = ax_gz.plot([], [], 'ro', markersize=10, label='Current Angle')
    ax_gz.legend()
    
    # Animation state
    animation_paused = [False]
    
    def init():
        """Initialize animation."""
        curve_line.set_data([], [])
        current_point.set_data([], [])
        return curve_line, current_point
    
    def animate(frame):
        """Update animation for each frame."""
        if animation_paused[0]:
            return curve_line, current_point
        
        heel_angle = heel_angles[frame]
        
        # Clear axes
        ax_3d.clear()
        ax_profile.clear()
        ax_metrics.clear()
        
        # Update 3D hull view
        plot_hull_3d(hull, waterline_z=waterline_z, heel_angle=heel_angle,
                    ax=ax_3d, title=f'Hull at {heel_angle:.1f}° Heel')
        
        # Update profile view
        stations = sorted(hull.profiles.keys())
        mid_station = stations[len(stations) // 2]
        profile = hull.get_profile(mid_station)
        plot_profile(profile, waterline_z=waterline_z, heel_angle=heel_angle,
                    ax=ax_profile, title=f'Profile at Station {mid_station:.2f}')
        
        # Calculate and display metrics
        try:
            gz = calculate_gz(hull, cg, waterline_z, heel_angle)
            cb = calculate_center_of_buoyancy(hull, waterline_z, heel_angle)
            volume = calculate_volume(hull, waterline_z, heel_angle)
            
            metrics_text = f"""
Frame: {frame + 1}/{n_frames}
Heel: {heel_angle:.2f}°

GZ: {gz:.4f} m
Volume: {volume:.4f} m³

CB: ({cb.x:.3f}, {cb.y:.3f}, {cb.z:.3f})
            """
        except Exception as e:
            metrics_text = f"""
Frame: {frame + 1}/{n_frames}
Heel: {heel_angle:.2f}°

Error: {str(e)[:60]}
            """
        
        ax_metrics.text(0.05, 0.95, metrics_text, transform=ax_metrics.transAxes,
                       fontsize=9, verticalalignment='top', family='monospace')
        ax_metrics.axis('off')
        
        # Update curve line (up to current frame)
        curve_line.set_data(heel_angles[:frame+1], gz_values[:frame+1])
        current_point.set_data([heel_angle], [gz_values[frame]])
        
        return curve_line, current_point
    
    # Create animation
    anim = FuncAnimation(fig, animate, init_func=init, frames=n_frames,
                        interval=interval, blit=False, repeat=True)
    
    # Add play/pause button
    ax_button = plt.axes([0.45, 0.02, 0.1, 0.04])
    button = Button(ax_button, 'Pause')
    
    def toggle_pause(event):
        """Toggle animation play/pause state."""
        animation_paused[0] = not animation_paused[0]
        button.label.set_text('Play' if animation_paused[0] else 'Pause')
        fig.canvas.draw_idle()
    
    button.on_clicked(toggle_pause)
    
    fig.suptitle('Animated Heel Sequence', fontsize=14, fontweight='bold')
    
    # Save animation if path provided
    if save_path is not None:
        save_path = Path(save_path)
        print(f"Saving animation to {save_path}...")
        if save_path.suffix.lower() == '.gif':
            anim.save(str(save_path), writer='pillow', fps=1000//interval)
        else:
            anim.save(str(save_path), writer='ffmpeg', fps=1000//interval)
        print("Animation saved successfully!")
    
    return fig, anim


def interactive_cg_adjustment(
    hull: KayakHull,
    initial_cg: Point3D,
    waterline_z: float = 0.0,
    vcg_range: Optional[Tuple[float, float]] = None,
    lcg_range: Optional[Tuple[float, float]] = None,
    figsize: Tuple[float, float] = (16, 10)
) -> plt.Figure:
    """
    Create an interactive CG position adjustment tool.
    
    This function allows users to adjust the center of gravity position using
    sliders and see the real-time impact on stability characteristics. It displays
    side-by-side comparison of original vs. adjusted stability curves.
    
    Args:
        hull: KayakHull object containing hull geometry
        initial_cg: Point3D representing the initial center of gravity
        waterline_z: Z-coordinate of waterline (default: 0.0)
        vcg_range: Optional tuple of (min_vcg, max_vcg) for vertical CG slider.
                  If None, uses ±0.5m from initial VCG (default: None)
        lcg_range: Optional tuple of (min_lcg, max_lcg) for longitudinal CG slider.
                  If None, uses ±1.0m from initial LCG (default: None)
        figsize: Figure size as (width, height) in inches (default: (16, 10))
    
    Returns:
        matplotlib Figure object with interactive controls
        
    Example:
        >>> hull = KayakHull()
        >>> # ... add profiles to hull ...
        >>> cg = Point3D(2.0, 0.0, -0.2)
        >>> fig = interactive_cg_adjustment(hull, cg)
        >>> plt.show()
        
    Note:
        - Requires an interactive matplotlib backend
        - Adjust VCG (vertical), LCG (longitudinal) using sliders
        - Original curve shown in blue, adjusted in red
        - Key metrics comparison displayed
    """
    from ..stability import calculate_gz, analyze_stability
    
    # Set default ranges if not provided
    if vcg_range is None:
        vcg_range = (initial_cg.z - 0.5, initial_cg.z + 0.5)
    if lcg_range is None:
        lcg_range = (initial_cg.x - 1.0, initial_cg.x + 1.0)
    
    # Calculate original stability curve
    heel_angles = np.linspace(0.0, 90.0, 50)
    original_gz = []
    for angle in heel_angles:
        try:
            gz = calculate_gz(hull, initial_cg, waterline_z, angle)
            original_gz.append(gz)
        except:
            original_gz.append(np.nan)
    original_gz = np.array(original_gz)
    
    # Calculate original metrics
    try:
        original_metrics = analyze_stability(hull, initial_cg, waterline_z)
        original_gm = original_metrics.gm_estimate if original_metrics.gm_estimate else np.nan
        original_max_gz = (original_metrics.angle_of_max_gz, original_metrics.max_gz)
        original_vanishing = original_metrics.angle_of_vanishing_stability
    except:
        original_gm = np.nan
        original_max_gz = (np.nan, np.nan)
        original_vanishing = np.nan
    
    # Create figure with subplots
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3,
                          left=0.1, right=0.95, top=0.88, bottom=0.2)
    
    # Create axes
    ax_curve = fig.add_subplot(gs[0:2, :])
    ax_original = fig.add_subplot(gs[2, 0])
    ax_adjusted = fig.add_subplot(gs[2, 1])
    
    # Plot original stability curve
    ax_curve.plot(heel_angles, original_gz, 'b-', linewidth=2, 
                 label='Original', alpha=0.7)
    adjusted_line, = ax_curve.plot([], [], 'r-', linewidth=2, 
                                   label='Adjusted', alpha=0.7)
    ax_curve.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    ax_curve.grid(True, alpha=0.3)
    ax_curve.set_xlabel('Heel Angle (degrees)', fontsize=11)
    ax_curve.set_ylabel('GZ (m)', fontsize=11)
    ax_curve.set_title('Stability Curve Comparison', fontsize=12, fontweight='bold')
    ax_curve.legend(fontsize=10)
    
    # Display original metrics
    original_text = f"""
Original CG Position:
  LCG: {initial_cg.x:.3f} m
  VCG: {initial_cg.z:.3f} m

Stability Metrics:
  GM: {original_gm:.4f} m
  Max GZ: {original_max_gz[1]:.4f} m
    at {original_max_gz[0]:.1f}°
  Vanishing: {original_vanishing:.1f}°
    """
    ax_original.text(0.05, 0.95, original_text, transform=ax_original.transAxes,
                    fontsize=9, verticalalignment='top', family='monospace')
    ax_original.set_title('Original', fontsize=10, fontweight='bold')
    ax_original.axis('off')
    
    def update(val=None):
        """Update adjusted stability curve."""
        # Get current slider values
        lcg = slider_lcg.val
        vcg = slider_vcg.val
        
        # Create adjusted CG
        adjusted_cg = Point3D(lcg, initial_cg.y, vcg)
        
        # Calculate adjusted stability curve
        adjusted_gz = []
        for angle in heel_angles:
            try:
                gz = calculate_gz(hull, adjusted_cg, waterline_z, angle)
                adjusted_gz.append(gz)
            except:
                adjusted_gz.append(np.nan)
        adjusted_gz = np.array(adjusted_gz)
        
        # Update plot
        adjusted_line.set_data(heel_angles, adjusted_gz)
        
        # Calculate adjusted metrics
        try:
            adjusted_metrics = analyze_stability(hull, adjusted_cg, waterline_z)
            adjusted_gm = adjusted_metrics.gm_estimate if adjusted_metrics.gm_estimate else np.nan
            adjusted_max_gz = (adjusted_metrics.angle_of_max_gz, adjusted_metrics.max_gz)
            adjusted_vanishing = adjusted_metrics.angle_of_vanishing_stability
        except:
            adjusted_gm = np.nan
            adjusted_max_gz = (np.nan, np.nan)
            adjusted_vanishing = np.nan
        
        # Update adjusted metrics display
        ax_adjusted.clear()
        
        # Calculate changes
        delta_gm = adjusted_gm - original_gm
        delta_max_gz = adjusted_max_gz[1] - original_max_gz[1]
        delta_vanishing = adjusted_vanishing - original_vanishing
        
        adjusted_text = f"""
Adjusted CG Position:
  LCG: {lcg:.3f} m ({lcg-initial_cg.x:+.3f})
  VCG: {vcg:.3f} m ({vcg-initial_cg.z:+.3f})

Stability Metrics:
  GM: {adjusted_gm:.4f} m ({delta_gm:+.4f})
  Max GZ: {adjusted_max_gz[1]:.4f} m ({delta_max_gz:+.4f})
    at {adjusted_max_gz[0]:.1f}°
  Vanishing: {adjusted_vanishing:.1f}° ({delta_vanishing:+.1f}°)
        """
        ax_adjusted.text(0.05, 0.95, adjusted_text, transform=ax_adjusted.transAxes,
                        fontsize=9, verticalalignment='top', family='monospace')
        ax_adjusted.set_title('Adjusted', fontsize=10, fontweight='bold')
        ax_adjusted.axis('off')
        
        fig.canvas.draw_idle()
    
    # Create sliders
    ax_slider_lcg = plt.axes([0.15, 0.10, 0.7, 0.03])
    slider_lcg = Slider(ax_slider_lcg, 'LCG (m)', lcg_range[0], lcg_range[1],
                       valinit=initial_cg.x, valstep=0.01)
    slider_lcg.on_changed(update)
    
    ax_slider_vcg = plt.axes([0.15, 0.05, 0.7, 0.03])
    slider_vcg = Slider(ax_slider_vcg, 'VCG (m)', vcg_range[0], vcg_range[1],
                       valinit=initial_cg.z, valstep=0.01)
    slider_vcg.on_changed(update)
    
    # Add reset button
    ax_reset = plt.axes([0.88, 0.075, 0.08, 0.04])
    button_reset = Button(ax_reset, 'Reset')
    
    def reset(event):
        """Reset sliders to initial CG position."""
        slider_lcg.reset()
        slider_vcg.reset()
    
    button_reset.on_clicked(reset)
    
    # Initial update
    update()
    
    fig.suptitle('Interactive CG Position Adjustment', fontsize=14, fontweight='bold')
    
    return fig


def interactive_waterline_explorer(
    hull: KayakHull,
    cg: Point3D,
    waterline_range: Tuple[float, float] = (-0.5, 0.2),
    initial_waterline: float = 0.0,
    heel_angle: float = 0.0,
    figsize: Tuple[float, float] = (16, 10)
) -> plt.Figure:
    """
    Create an interactive waterline level explorer.
    
    This function allows users to adjust the waterline Z-coordinate using a slider
    to explore how displacement, center of buoyancy, and stability characteristics
    change with draft (loading condition).
    
    Args:
        hull: KayakHull object containing hull geometry
        cg: Point3D representing the center of gravity
        waterline_range: Tuple of (min_wl_z, max_wl_z) for waterline slider
                        (default: (-0.5, 0.2))
        initial_waterline: Initial waterline Z-coordinate (default: 0.0)
        heel_angle: Heel angle to use for visualization (default: 0.0)
        figsize: Figure size as (width, height) in inches (default: (16, 10))
    
    Returns:
        matplotlib Figure object with interactive controls
        
    Example:
        >>> hull = KayakHull()
        >>> # ... add profiles to hull ...
        >>> cg = Point3D(2.0, 0.0, -0.2)
        >>> fig = interactive_waterline_explorer(hull, cg)
        >>> plt.show()
        
    Note:
        - Requires an interactive matplotlib backend
        - Slider adjusts waterline Z-coordinate (positive = higher waterline)
        - Shows real-time updates of volume, CB position, and stability
    """
    from ..hydrostatics import calculate_volume, calculate_center_of_buoyancy
    from ..stability import calculate_gz, analyze_stability
    
    # Create figure with subplots
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3,
                          left=0.08, right=0.95, top=0.93, bottom=0.15)
    
    # Create axes
    ax_3d = fig.add_subplot(gs[0:2, 0:2], projection='3d')
    ax_profile = fig.add_subplot(gs[0, 2])
    ax_metrics = fig.add_subplot(gs[1, 2])
    ax_plot = fig.add_subplot(gs[2, :])
    
    # Pre-calculate data for plot
    wl_values = np.linspace(waterline_range[0], waterline_range[1], 50)
    volumes = []
    cb_z_values = []
    gz_values = []
    
    for wl_z in wl_values:
        try:
            vol = calculate_volume(hull, wl_z, heel_angle)
            cb = calculate_center_of_buoyancy(hull, wl_z, heel_angle)
            gz = calculate_gz(hull, cg, wl_z, heel_angle)
            volumes.append(vol)
            cb_z_values.append(cb.z)
            gz_values.append(gz)
        except:
            volumes.append(np.nan)
            cb_z_values.append(np.nan)
            gz_values.append(np.nan)
    
    volumes = np.array(volumes)
    cb_z_values = np.array(cb_z_values)
    gz_values = np.array(gz_values)
    
    # Plot displacement vs waterline
    ax_plot.plot(wl_values, volumes, 'b-', linewidth=2, label='Displacement Volume')
    ax_plot_twin = ax_plot.twinx()
    ax_plot_twin.plot(wl_values, gz_values, 'r-', linewidth=2, label='GZ')
    
    ax_plot.set_xlabel('Waterline Z-coordinate (m)', fontsize=10)
    ax_plot.set_ylabel('Volume (m³)', fontsize=10, color='b')
    ax_plot_twin.set_ylabel('GZ (m)', fontsize=10, color='r')
    ax_plot.tick_params(axis='y', labelcolor='b')
    ax_plot_twin.tick_params(axis='y', labelcolor='r')
    ax_plot.grid(True, alpha=0.3)
    ax_plot.set_title('Displacement and Stability vs. Waterline', 
                     fontsize=11, fontweight='bold')
    
    # Add lines for current waterline
    current_line = ax_plot.axvline(x=initial_waterline, color='green', 
                                   linestyle='--', linewidth=2, label='Current')
    
    # Combine legends
    lines1, labels1 = ax_plot.get_legend_handles_labels()
    lines2, labels2 = ax_plot_twin.get_legend_handles_labels()
    ax_plot.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    def update(waterline_z):
        """Update all views for new waterline."""
        ax_3d.clear()
        ax_profile.clear()
        ax_metrics.clear()
        
        # Update 3D hull view
        plot_hull_3d(hull, waterline_z=waterline_z, heel_angle=heel_angle,
                    ax=ax_3d, title=f'Hull at WL Z={waterline_z:.3f}m')
        
        # Update profile view
        stations = sorted(hull.profiles.keys())
        mid_station = stations[len(stations) // 2]
        profile = hull.get_profile(mid_station)
        plot_profile(profile, waterline_z=waterline_z, heel_angle=heel_angle,
                    ax=ax_profile, title=f'Profile at Station {mid_station:.2f}')
        
        # Calculate and display metrics
        try:
            volume = calculate_volume(hull, waterline_z, heel_angle)
            cb = calculate_center_of_buoyancy(hull, waterline_z, heel_angle)
            gz = calculate_gz(hull, cg, waterline_z, heel_angle)
            
            # Calculate displacement mass (assuming fresh water)
            displacement_mass = volume * 1000.0  # kg (water density = 1000 kg/m³)
            
            if abs(heel_angle) < 5.0:
                try:
                    metrics = analyze_stability(hull, cg, waterline_z)
                    gm_text = f'{metrics.gm_estimate:.4f} m' if metrics.gm_estimate else 'N/A'
                except:
                    gm_text = 'N/A'
            else:
                gm_text = 'N/A (>5°)'
            
            metrics_text = f"""
Waterline Z: {waterline_z:.3f} m
Heel Angle: {heel_angle:.1f}°

Displacement:
  Volume: {volume:.4f} m³
  Mass: {displacement_mass:.1f} kg
  
Center of Buoyancy:
  X: {cb.x:.4f} m
  Y: {cb.y:.4f} m
  Z: {cb.z:.4f} m
  
Stability:
  GZ: {gz:.4f} m
  GM: {gm_text}
            """
        except Exception as e:
            metrics_text = f"""
Waterline Z: {waterline_z:.3f} m
Heel Angle: {heel_angle:.1f}°

Error calculating metrics:
{str(e)[:100]}
            """
        
        ax_metrics.text(0.05, 0.95, metrics_text, transform=ax_metrics.transAxes,
                       fontsize=9, verticalalignment='top', family='monospace')
        ax_metrics.axis('off')
        
        # Update current waterline line
        current_line.set_xdata([waterline_z, waterline_z])
        
        fig.canvas.draw_idle()
    
    # Create slider
    ax_slider = plt.axes([0.15, 0.05, 0.7, 0.03])
    slider = Slider(ax_slider, 'Waterline Z (m)', waterline_range[0], 
                   waterline_range[1], valinit=initial_waterline, valstep=0.01)
    slider.on_changed(update)
    
    # Initial update
    update(initial_waterline)
    
    fig.suptitle('Interactive Waterline Explorer', fontsize=14, fontweight='bold')
    
    return fig
