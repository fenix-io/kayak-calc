"""Diagnose CB calculation by showing volume distribution along the hull."""
import numpy as np
from src.io import load_hull_from_json
from src.hydrostatics import calculate_displacement, calculate_section_properties
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
hull = load_hull_from_json(f'{script_dir}/kyk-01_hull.json')

waterline_z = 0.110
heel_angle = 0.0

# Get detailed volume distribution
print(f"Hull length: {hull.length} m")
print(f"Waterline z: {waterline_z} m")
print(f"\nVolume distribution analysis:")
print("-" * 70)
print(f"{'Station (x)':>12} {'Area (m²)':>12} {'Volume Contrib':>15} {'% of Total':>12}")
print("-" * 70)

# Use many stations for detailed analysis
num_stations = 50
min_station = hull.get_stern_station()
max_station = hull.get_bow_station()
stations = np.linspace(min_station, max_station, num_stations)

areas = []
volumes = []

for i, station in enumerate(stations):
    profile = hull.get_profile(station, interpolate=True)
    props = calculate_section_properties(profile, waterline_z, heel_angle)
    areas.append(props.area)
    
    # Approximate volume contribution using trapezoidal rule
    if i > 0:
        dx = station - stations[i-1]
        vol_contrib = (areas[i-1] + props.area) / 2 * dx
        volumes.append(vol_contrib)

total_volume = sum(volumes)

# Print distribution
vol_idx = 0
for i, station in enumerate(stations):
    if i > 0:
        pct = (volumes[vol_idx] / total_volume * 100) if total_volume > 0 else 0
        print(f"{station:12.3f} {areas[i]:12.6f} {volumes[vol_idx]:15.6f} {pct:11.2f}%")
        vol_idx += 1

print("-" * 70)
print(f"{'TOTAL':>12} {sum(areas):12.6f} {total_volume:15.6f} {100.0:11.2f}%")

# Calculate LCB manually
lcb_sum = sum((stations[i-1] + stations[i])/2 * volumes[i-1] for i in range(1, len(stations)))
lcb = lcb_sum / total_volume if total_volume > 0 else 0

print(f"\nManual LCB calculation: {lcb:.3f} m")
print(f"Expected LCB for symmetric hull: {hull.length/2:.3f} m")
print(f"\n⚠️  LCB is at {(lcb/hull.length)*100:.1f}% of hull length from bow")
print(f"   (should be around 50% for symmetric hull)")

# Check profile positions
print(f"\n\nProfile station distribution:")
print(f"  Bow at: x = {max_station:.3f} m")
for station in hull.get_stations():
    print(f"  Profile at: x = {station:.3f} m ({(station/hull.length)*100:.1f}% from stern)")
print(f"  Stern at: x = {min_station:.3f} m")
