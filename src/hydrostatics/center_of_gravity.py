"""
Center of Gravity (CG) calculations for kayak systems.

This module provides functionality for specifying and calculating the center
of gravity of a kayak system, including the hull and all payload (paddler,
gear, etc.).

The CG is critical for stability analysis, as the relative positions of CG
and CB (center of buoyancy) determine stability characteristics.

Components:
- CenterOfGravity: Dataclass for CG position
- MassComponent: Individual mass item with position
- calculate_cg_from_components: Aggregate CG from multiple components
- validate_center_of_gravity: Validation and warnings
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np


@dataclass
class MassComponent:
    """
    A component with mass and position contributing to overall CG.
    
    Represents any mass element in the kayak system (hull structure,
    paddler, gear, equipment, etc.).
    
    Attributes:
        name: Descriptive name of the component
        mass: Mass in kilograms
        x: Longitudinal position (m) from origin
        y: Transverse position (m) from centerline (+ starboard)
        z: Vertical position (m) from origin (+ up)
        description: Optional detailed description
    
    Example:
        >>> paddler = MassComponent("Paddler", mass=80.0, x=2.0, y=0.0, z=0.3)
        >>> hull = MassComponent("Hull", mass=25.0, x=2.5, y=0.0, z=-0.1)
    
    Note:
        - Positive y is to starboard (right side)
        - Positive z is upward
        - Positions are relative to hull origin
    """
    
    name: str
    mass: float
    x: float
    y: float
    z: float
    description: str = ""
    
    def __post_init__(self):
        """Validate mass component after initialization."""
        if self.mass < 0:
            raise ValueError(f"Mass must be non-negative, got {self.mass} kg")
        
        if not np.isfinite(self.mass):
            raise ValueError(f"Mass must be finite, got {self.mass}")
        
        if not all(np.isfinite([self.x, self.y, self.z])):
            raise ValueError(f"Position coordinates must be finite: ({self.x}, {self.y}, {self.z})")
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"MassComponent('{self.name}', "
            f"mass={self.mass:.2f} kg, "
            f"pos=({self.x:.3f}, {self.y:.3f}, {self.z:.3f}))"
        )


@dataclass
class CenterOfGravity:
    """
    Center of Gravity (CG) position and total mass.
    
    The center of gravity is the point where the weight force acts.
    It is calculated from all mass components in the system.
    
    Attributes:
        lcg: Longitudinal Center of Gravity (m) - x-coordinate
        vcg: Vertical Center of Gravity (m) - z-coordinate
        tcg: Transverse Center of Gravity (m) - y-coordinate
        total_mass: Total system mass (kg)
        num_components: Number of components included
        components: Optional list of mass components
    
    Note:
        - LCG is measured from the origin along longitudinal axis
        - VCG is measured from the origin along vertical axis
        - TCG is measured from centerline; should be ~0 for balanced loading
        - Total mass includes all components (hull, paddler, gear, etc.)
    """
    
    lcg: float
    vcg: float
    tcg: float
    total_mass: float
    num_components: int = 0
    components: Optional[List[MassComponent]] = None
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CenterOfGravity(\n"
            f"  LCG={self.lcg:.6f} m,\n"
            f"  VCG={self.vcg:.6f} m,\n"
            f"  TCG={self.tcg:.6f} m,\n"
            f"  total_mass={self.total_mass:.2f} kg,\n"
            f"  num_components={self.num_components}\n"
            f")"
        )
    
    @property
    def weight(self) -> float:
        """Calculate weight force in Newtons (mass × gravity)."""
        g = 9.81  # m/s² (standard gravity)
        return self.total_mass * g
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        data = {
            'lcg': float(self.lcg),
            'vcg': float(self.vcg),
            'tcg': float(self.tcg),
            'total_mass': float(self.total_mass),
            'num_components': self.num_components,
        }
        
        if self.components is not None:
            data['components'] = [
                {
                    'name': c.name,
                    'mass': float(c.mass),
                    'x': float(c.x),
                    'y': float(c.y),
                    'z': float(c.z),
                    'description': c.description
                }
                for c in self.components
            ]
        
        return data


def calculate_cg_from_components(
    components: List[MassComponent],
    include_components: bool = True
) -> CenterOfGravity:
    """
    Calculate center of gravity from multiple mass components.
    
    Uses the principle of moments: the CG is the point where the
    sum of moments equals the total weight times the CG position.
    
    Mathematical formulation:
        LCG = Σ(m_i × x_i) / M
        VCG = Σ(m_i × z_i) / M
        TCG = Σ(m_i × y_i) / M
    
    where:
        m_i = mass of component i
        x_i, y_i, z_i = position of component i
        M = Σ(m_i) = total mass
    
    Args:
        components: List of MassComponent objects
        include_components: If True, store components in result
    
    Returns:
        CenterOfGravity object with calculated position
    
    Raises:
        ValueError: If components list is empty or total mass is zero
    
    Example:
        >>> components = [
        ...     MassComponent("Hull", mass=25.0, x=2.5, y=0.0, z=-0.1),
        ...     MassComponent("Paddler", mass=80.0, x=2.0, y=0.0, z=0.3),
        ...     MassComponent("Gear", mass=15.0, x=1.5, y=0.0, z=0.1)
        ... ]
        >>> cg = calculate_cg_from_components(components)
        >>> print(f"CG position: ({cg.lcg:.2f}, {cg.vcg:.2f})")
    
    Note:
        - All components must have non-negative mass
        - Zero-mass components are included but don't affect CG
        - If all components have zero mass, raises ValueError
    """
    if not components:
        raise ValueError("Components list cannot be empty")
    
    # Calculate total mass
    total_mass = sum(c.mass for c in components)
    
    if total_mass <= 0:
        raise ValueError(
            f"Total mass must be positive, got {total_mass:.6f} kg. "
            "Check that at least one component has non-zero mass."
        )
    
    # Calculate moments (mass × position)
    moment_x = sum(c.mass * c.x for c in components)
    moment_y = sum(c.mass * c.y for c in components)
    moment_z = sum(c.mass * c.z for c in components)
    
    # Calculate CG coordinates (moment / total_mass)
    lcg = moment_x / total_mass
    vcg = moment_z / total_mass
    tcg = moment_y / total_mass
    
    return CenterOfGravity(
        lcg=lcg,
        vcg=vcg,
        tcg=tcg,
        total_mass=total_mass,
        num_components=len(components),
        components=components.copy() if include_components else None
    )


def create_cg_manual(
    lcg: float,
    vcg: float,
    tcg: float,
    total_mass: float
) -> CenterOfGravity:
    """
    Create a CenterOfGravity object with manually specified coordinates.
    
    Use this function when you know the CG position directly rather than
    calculating it from components.
    
    Args:
        lcg: Longitudinal CG position (m)
        vcg: Vertical CG position (m)
        tcg: Transverse CG position (m)
        total_mass: Total system mass (kg)
    
    Returns:
        CenterOfGravity object
    
    Raises:
        ValueError: If mass is non-positive or coordinates are non-finite
    
    Example:
        >>> cg = create_cg_manual(lcg=2.3, vcg=0.2, tcg=0.0, total_mass=120.0)
        >>> print(f"Weight: {cg.weight:.1f} N")
    """
    if total_mass <= 0:
        raise ValueError(f"Total mass must be positive, got {total_mass} kg")
    
    if not all(np.isfinite([lcg, vcg, tcg])):
        raise ValueError(f"CG coordinates must be finite: ({lcg}, {vcg}, {tcg})")
    
    return CenterOfGravity(
        lcg=lcg,
        vcg=vcg,
        tcg=tcg,
        total_mass=total_mass,
        num_components=0,
        components=None
    )


def validate_center_of_gravity(
    cg: CenterOfGravity,
    min_mass: float = 1.0,
    max_mass: float = 500.0,
    max_tcg_offset: float = 0.1
) -> Tuple[bool, List[str]]:
    """
    Validate center of gravity for physical reasonableness.
    
    Checks for:
    - Finite CG coordinates
    - Positive total mass
    - Mass within reasonable range for kayak
    - TCG near centerline (for balanced loading)
    
    Args:
        cg: CenterOfGravity object to validate
        min_mass: Minimum reasonable total mass (kg), default 1.0
        max_mass: Maximum reasonable total mass (kg), default 500.0
        max_tcg_offset: Maximum TCG offset from centerline (m), default 0.1
    
    Returns:
        Tuple of (is_valid, list_of_issues)
    
    Example:
        >>> cg = calculate_cg_from_components(components)
        >>> is_valid, issues = validate_center_of_gravity(cg)
        >>> if not is_valid:
        ...     for issue in issues:
        ...         print(f"Warning: {issue}")
    """
    issues = []
    
    # Check for finite values
    if not np.isfinite(cg.lcg):
        issues.append(f"Non-finite LCG: {cg.lcg}")
    
    if not np.isfinite(cg.vcg):
        issues.append(f"Non-finite VCG: {cg.vcg}")
    
    if not np.isfinite(cg.tcg):
        issues.append(f"Non-finite TCG: {cg.tcg}")
    
    # Check mass
    if cg.total_mass <= 0:
        issues.append(f"Total mass must be positive: {cg.total_mass:.2f} kg")
    elif not np.isfinite(cg.total_mass):
        issues.append(f"Non-finite total mass: {cg.total_mass}")
    else:
        # Check mass range (only if mass is valid)
        if cg.total_mass < min_mass:
            issues.append(
                f"Total mass ({cg.total_mass:.2f} kg) is very low. "
                f"Expected at least {min_mass:.0f} kg for a kayak system."
            )
        
        if cg.total_mass > max_mass:
            issues.append(
                f"Total mass ({cg.total_mass:.2f} kg) is very high. "
                f"Expected at most {max_mass:.0f} kg for a kayak system."
            )
    
    # Check TCG (transverse balance)
    if np.isfinite(cg.tcg) and abs(cg.tcg) > max_tcg_offset:
        issues.append(
            f"TCG ({cg.tcg:.3f} m) is significantly off centerline. "
            f"This indicates unbalanced loading (expected < {max_tcg_offset:.2f} m). "
            "The kayak may have poor stability or tend to roll."
        )
    
    is_valid = len(issues) == 0
    return is_valid, issues


def adjust_cg_for_loading(
    base_cg: CenterOfGravity,
    additional_components: List[MassComponent]
) -> CenterOfGravity:
    """
    Calculate new CG after adding components to an existing system.
    
    Useful for analyzing different loading conditions without recalculating
    from scratch.
    
    Args:
        base_cg: Existing CenterOfGravity
        additional_components: List of new components to add
    
    Returns:
        New CenterOfGravity with updated position and mass
    
    Example:
        >>> # Start with empty kayak
        >>> kayak_cg = create_cg_manual(lcg=2.5, vcg=0.0, tcg=0.0, total_mass=25.0)
        >>> 
        >>> # Add paddler and gear
        >>> new_items = [
        ...     MassComponent("Paddler", mass=80.0, x=2.0, y=0.0, z=0.3),
        ...     MassComponent("Gear", mass=15.0, x=1.5, y=0.0, z=0.1)
        ... ]
        >>> loaded_cg = adjust_cg_for_loading(kayak_cg, new_items)
    """
    # Create a pseudo-component for the base CG
    base_component = MassComponent(
        name="Base System",
        mass=base_cg.total_mass,
        x=base_cg.lcg,
        y=base_cg.tcg,
        z=base_cg.vcg
    )
    
    # Combine all components
    all_components = [base_component] + additional_components
    
    # Calculate new CG
    return calculate_cg_from_components(all_components, include_components=True)


def calculate_mass_summary(components: List[MassComponent]) -> dict:
    """
    Generate a summary of mass distribution.
    
    Useful for understanding the mass breakdown and identifying
    heavy components.
    
    Args:
        components: List of MassComponent objects
    
    Returns:
        Dictionary with summary statistics
    
    Example:
        >>> summary = calculate_mass_summary(components)
        >>> print(f"Total: {summary['total_mass']:.1f} kg")
        >>> print(f"Heaviest: {summary['heaviest']['name']} ({summary['heaviest']['mass']:.1f} kg)")
    """
    if not components:
        return {
            'total_mass': 0.0,
            'num_components': 0,
            'heaviest': None,
            'lightest': None,
            'average_mass': 0.0
        }
    
    total_mass = sum(c.mass for c in components)
    masses = [c.mass for c in components]
    
    heaviest = max(components, key=lambda c: c.mass)
    lightest = min(components, key=lambda c: c.mass)
    
    return {
        'total_mass': total_mass,
        'num_components': len(components),
        'heaviest': {'name': heaviest.name, 'mass': heaviest.mass},
        'lightest': {'name': lightest.name, 'mass': lightest.mass},
        'average_mass': total_mass / len(components),
        'mass_distribution': [
            {'name': c.name, 'mass': c.mass, 'percentage': (c.mass / total_mass * 100) if total_mass > 0 else 0}
            for c in sorted(components, key=lambda x: x.mass, reverse=True)
        ]
    }
