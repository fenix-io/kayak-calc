from src.hydrostatics.center_of_gravity import MassComponent, calculate_cg_from_components
from src.io import load_hull_from_json
from src.hydrostatics import calculate_displacement, calculate_hull_cg_mass_component, calculate_center_of_buoyancy
from src.stability import StabilityAnalyzer
from src.visualization import plot_stability_curve, plot_hull_3d
import matplotlib.pyplot as plt
import os

# IMPORTANT: This hull has max displacement of ~42 kg, not typical 80-100 kg for full-size kayak
# This suggests the hull data may be for a scale model or measurements need verification
# Using appropriate masses for this hull capacity

waterline_z = 0.150 
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load your hull data
hull = load_hull_from_json(f'{script_dir}/kyk-01_hull.json')

# Check hull capacity first
from src.hydrostatics import calculate_displacement as calc_disp
max_disp = calc_disp(hull, waterline_z=waterline_z)
print(f"Hull maximum displacement: {max_disp.mass:.2f} kg at WL z={waterline_z} m")

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

# Define mass components
# ADJUSTED FOR THIS HULL'S CAPACITY (~42 kg max)
# For a full-size kayak, you would need 12 kg hull + 75 kg paddler = 87 kg total
# But this hull can only support 42 kg, suggesting:
#   - Scale model data
#   - Incorrect z-coordinates in source data  
#   - Missing hull sections

# Option A: Scaled masses matching hull capacity (CURRENT APPROACH)
components = [
    calculate_hull_cg_mass_component(hull, hull_mass=12.0),
    MassComponent(name="payload", mass=100.0, x=2.6, y=0.0, z=0.30, description="Payload/paddler"),
]

# Calculate CG automatically
cg = calculate_cg_from_components(components)
print(f"\nMass breakdown:")
for comp in components:
    print(f"  {comp.description}: {comp.mass:.1f} kg at z={comp.z:.3f} m")
print(f"Total mass: {sum(c.mass for c in components):.1f} kg")

print(f"\nCalculated Center of Gravity: x={cg.x:.3f} m, y={cg.y:.3f} m, z={cg.z:.3f} m")

# Calculate CB at design waterline
cb = calculate_center_of_buoyancy(hull, waterline_z=waterline_z, heel_angle=0.0)
print(f"Calculated Center of Buoyancy at WL: x={cb.lcb:.3f} m, y={cb.tcb:.3f} m, z={cb.vcb:.3f} m, volume={cb.volume:.3f} m³")

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


