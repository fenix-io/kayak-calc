"""
Configuration module for kayak calculation tool.

This module provides configuration settings and constants for the application.
"""

# Physical constants
WATER_DENSITY = 1025.0  # kg/m³ (seawater)
FRESHWATER_DENSITY = 1000.0  # kg/m³
GRAVITY = 9.81  # m/s²

# Numerical integration defaults
DEFAULT_INTEGRATION_METHOD = "simpson"  # Options: 'simpson', 'trapezoidal'
DEFAULT_NUM_STATIONS = 20  # Number of stations for integration

# Stability analysis defaults
DEFAULT_HEEL_ANGLES = list(range(0, 91, 5))  # 0 to 90 degrees in 5-degree increments
MAX_HEEL_ANGLE = 90.0  # degrees

# Interpolation settings
DEFAULT_INTERPOLATION_METHOD = "linear"  # Options: 'linear', 'cubic'
MIN_POINTS_PER_PROFILE = 3

# Tolerance settings
ZERO_TOLERANCE = 1e-10  # Tolerance for floating point comparisons
AREA_TOLERANCE = 1e-6  # Minimum cross-sectional area to consider

# Plotting defaults
DEFAULT_FIGURE_SIZE = (10, 6)
DEFAULT_DPI = 100

# Units
LENGTH_UNIT = "m"
MASS_UNIT = "kg"
ANGLE_UNIT = "deg"

# File format defaults
DEFAULT_DATA_FORMAT = "json"  # Options: 'json', 'csv'


class Config:
    """
    Configuration class for application settings.
    
    Can be subclassed or modified for specific use cases.
    """
    
    def __init__(self):
        self.water_density = WATER_DENSITY
        self.gravity = GRAVITY
        self.integration_method = DEFAULT_INTEGRATION_METHOD
        self.num_stations = DEFAULT_NUM_STATIONS
        self.heel_angles = DEFAULT_HEEL_ANGLES
        self.interpolation_method = DEFAULT_INTERPOLATION_METHOD
        
    def use_freshwater(self):
        """Switch to freshwater density."""
        self.water_density = FRESHWATER_DENSITY
        
    def use_seawater(self):
        """Switch to seawater density."""
        self.water_density = WATER_DENSITY
