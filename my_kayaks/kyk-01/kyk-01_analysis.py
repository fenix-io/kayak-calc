from src.hydrostatics.center_of_gravity import MassComponent, calculate_cg_from_components
from src.io import load_hull_from_json
from src.hydrostatics import CenterOfGravity, calculate_displacement
from src.stability import StabilityAnalyzer
from src.visualization import plot_stability_curve, plot_hull_3d
import matplotlib.pyplot as plt
import os

waterline_z = 0.20
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load your hull data (replace with your file)
hull = load_hull_from_json(f'{script_dir}/kyk-01_hull.json')
#hull = load_hull_from_json('data/sample_hull_simple.json')
# Plot the 3D hull
print("\nPlotting 3D hull visualization...")
fig = plt.figure(figsize=(12, 8))
ax_hull = fig.add_subplot(111, projection='3d')
plot_hull_3d(hull, waterline_z=waterline_z, heel_angle=0.0, ax=ax_hull, view_mode='wireframe')

# Save hull plot
hull_image_path = os.path.join(script_dir, 'hull_3d.png')
plt.savefig(hull_image_path, dpi=300, bbox_inches='tight')
print(f"3D hull plot saved as '{hull_image_path}'")
plt.show()

# Define your kayak's center of gravity
# Define all mass components
components = [
    MassComponent("Hull", mass=10.0, x=2.8, y=0.0, z=0.10),
    # MassComponent("Paddler", mass=100.0, x=3.00, y=0.0, z=0.35),  # Lower CG for more stability
    # MassComponent("Gear", mass=5.0, x=2.0, y=0.0, z=0.10),
    # ... more components
]

# Calculate CG automatically
cg = calculate_cg_from_components(components)

# Create stability analyzer with waterline
analyzer = StabilityAnalyzer(hull, cg, waterline_z=waterline_z)

# Calculate displacement
displacement = calculate_displacement(hull, waterline_z=waterline_z)

# Generate stability curve
curve = analyzer.generate_stability_curve()

# Analyze stability to get metrics
metrics = analyzer.analyze_stability(curve)

# Print key results
print(f"Displacement: {displacement.mass:.2f} kg")
print(f"Initial GM: {metrics.gm_estimate:.3f} m")
print(f"Max GZ: {metrics.max_gz:.3f} m at {metrics.angle_of_max_gz:.0f}°")

# Plot the stability curve
ax = plot_stability_curve(curve, metrics)

# Save in the same directory as this script
image_path = os.path.join(script_dir, 'stability_curve.png')
plt.savefig(image_path, dpi=300, bbox_inches='tight')
print(f"Stability curve saved as '{image_path}'")
plt.show()  # This won't display in non-interactive environments but won't error


