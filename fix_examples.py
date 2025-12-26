#!/usr/bin/env python3
"""Fix remaining linting issues in examples/."""

import re
from pathlib import Path

def fix_long_lines_in_file(filepath):
    """Break long lines in examples."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix specific long lines
    replacements = {
        # center_of_buoyancy_examples.py:173
        'volume, cb = calculate_volume(hull, waterline_z=waterline_z)  # Calculate at new waterline':
            'volume, cb = calculate_volume(\n                hull, waterline_z=waterline_z\n            )  # Calculate at new waterline',
        
        # center_of_buoyancy_examples.py:202
        'print(f"  CB at waterline z={wl:.2f}: LCB={cb.lcb:.3f}, VCB={cb.vcb:.3f}, TCB={cb.tcb:.3f}")':
            'print(\n                f"  CB at waterline z={wl:.2f}: "\n                f"LCB={cb.lcb:.3f}, VCB={cb.vcb:.3f}, TCB={cb.tcb:.3f}"\n            )',
        
        # center_of_buoyancy_examples.py:263
        'print(f"    VCB at {angle}°: {cb.vcb:.4f} m (change: {vcb_change:+.4f} m from upright)")':
            'print(\n                f"    VCB at {angle}\u00b0: {cb.vcb:.4f} m "\n                f"(change: {vcb_change:+.4f} m from upright)"\n            )',
    }
    
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
    
    with open(filepath, 'w') as f:
        f.write(content)

def fix_unused_vars():
    """Add _ prefix to unused variables."""
    files_to_fix = [
        ('examples/interactive_visualization_examples.py', [94, 118, 181, 210, 238]),
        ('examples/profile_plotting_examples.py', [75, 99, 159, 182, 213]),
    ]
    
    for filepath, line_numbers in files_to_fix:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        for line_num in line_numbers:
            idx = line_num - 1
            if idx < len(lines):
                # Replace fig = or ax = with _ prefix
                lines[idx] = lines[idx].replace('fig = ', '_fig = ')
                lines[idx] = lines[idx].replace('ax = ', '_ax = ')
        
        with open(filepath, 'w') as f:
            f.writelines(lines)

if __name__ == '__main__':
    print("Fixing long lines...")
    fix_long_lines_in_file('examples/center_of_buoyancy_examples.py')
    
    print("Fixing unused variables...")
    fix_unused_vars()
    
    print("Done!")
