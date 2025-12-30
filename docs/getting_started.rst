Getting Started
===============

This guide will help you get started with the Kayak Calculator application.

Installation
------------

Prerequisites
~~~~~~~~~~~~~

* Python 3.11 or higher
* pip package manager

Install from Source
~~~~~~~~~~~~~~~~~~~

1. Clone the repository:

.. code-block:: bash

   git clone <repository-url>
   cd kyk-calc

2. Install in development mode:

.. code-block:: bash

   pip install -e .

This will install the package along with all dependencies (numpy, scipy, matplotlib).

Understanding the Coordinate System
------------------------------------

The application uses a right-handed coordinate system referenced to the centerline plane:

* **X-axis**: Longitudinal direction (along kayak length)
* **Y-axis**: Transverse direction (port is negative, starboard is positive)
* **Z-axis**: Vertical direction (down is negative, up is positive)

The origin is typically placed at midship on the centerline, but can be at any convenient location.

Input Data Format
-----------------

Hull geometry is defined by transverse profiles at various longitudinal stations. Two formats are supported:

JSON Format
~~~~~~~~~~~

.. code-block:: json

   {
     "metadata": {
       "name": "Sample Kayak",
       "units": "meters",
       "coordinate_system": "centerline"
     },
     "profiles": [
       {
         "station": 0.0,
         "points": [
           {"x": 0.0, "y": -0.3, "z": -0.2},
           {"x": 0.0, "y": 0.3, "z": -0.2}
         ]
       },
       {
         "station": 5.0,
         "points": [
           {"x": 5.0, "y": -0.25, "z": -0.15},
           {"x": 5.0, "y": 0.25, "z": -0.15}
         ]
       }
     ]
   }

.. note::
   The hull geometry is now defined entirely by the ``profiles`` array. 
   Bow and stern positions are automatically derived from the first and last profiles.

CSV Format
~~~~~~~~~~

Simple CSV format with defaults applied:

.. code-block:: text

   x,y,z,station
   0.0,-0.3,-0.2,0.0
   0.0,0.3,-0.2,0.0
   1.0,-0.4,-0.3,1.0
   1.0,0.4,-0.3,1.0

Basic Workflow
--------------

1. **Load Hull Geometry**

.. code-block:: python

   from src.io import load_hull_from_json
   
   hull = load_hull_from_json('data/sample_hull_kayak.json')

2. **Define Center of Gravity**

.. code-block:: python

   from src.hydrostatics import CenterOfGravity
   
   # Simple CG definition
   cg = CenterOfGravity(x=2.5, y=0.0, z=-0.3, mass=100.0)
   
   # Or from component masses
   cg = CenterOfGravity.from_components([
       {'mass': 20.0, 'x': 2.0, 'y': 0.0, 'z': -0.15, 'name': 'hull'},
       {'mass': 80.0, 'x': 2.5, 'y': 0.0, 'z': -0.35, 'name': 'paddler'},
   ])

3. **Calculate Hydrostatics**

.. code-block:: python

   from src.hydrostatics import calculate_volume
   
   volume, cb = calculate_volume(
       hull,
       waterline_z=-0.1,
       num_sections=20
   )
   
   displacement_kg = volume * 1025  # seawater density
   
   print(f"Volume: {volume:.4f} m³")
   print(f"Displacement: {displacement_kg:.1f} kg")
   print(f"Center of Buoyancy: ({cb.x:.2f}, {cb.y:.2f}, {cb.z:.2f})")

4. **Perform Stability Analysis**

.. code-block:: python

   from src.stability import StabilityAnalyzer
   
   analyzer = StabilityAnalyzer(hull, cg)
   
   # Generate full stability curve
   results = analyzer.calculate_stability_curve(
       waterline_z=-0.1,
       heel_angles=range(0, 91, 5)
   )
   
   print(f"Initial GM: {results.initial_gm:.3f} m")
   print(f"Max GZ: {results.max_gz:.3f} m at {results.max_gz_angle:.0f}°")
   print(f"Vanishing angle: {results.vanishing_angle:.0f}°")

5. **Visualize Results**

.. code-block:: python

   from src.visualization import plot_stability_curve, plot_hull_3d
   
   # Plot stability curve
   plot_stability_curve(results, save_path='stability_curve.png', show=True)
   
   # Plot hull in 3D
   plot_hull_3d(hull, waterline_z=-0.1, heel_angle=0, view='isometric')

Complete Example
----------------

Here's a complete working example:

.. code-block:: python

   from src.io import load_hull_from_json
   from src.hydrostatics import CenterOfGravity
   from src.stability import StabilityAnalyzer
   from src.visualization import plot_stability_curve
   
   # 1. Load hull
   hull = load_hull_from_json('data/sample_hull_kayak.json')
   
   # 2. Define CG (paddler + hull)
   cg = CenterOfGravity.from_components([
       {'mass': 22.0, 'x': 2.0, 'y': 0.0, 'z': -0.15, 'name': 'hull'},
       {'mass': 78.0, 'x': 2.5, 'y': 0.0, 'z': -0.35, 'name': 'paddler'},
   ])
   
   # 3. Analyze stability
   analyzer = StabilityAnalyzer(hull, cg)
   results = analyzer.calculate_stability_curve(waterline_z=-0.1)
   
   # 4. Print results
   print(f"Total mass: {cg.mass:.1f} kg")
   print(f"CG at: ({cg.x:.2f}, {cg.y:.2f}, {cg.z:.2f})")
   print(f"Initial GM: {results.initial_gm:.3f} m")
   print(f"Max GZ: {results.max_gz:.3f} m at {results.max_gz_angle:.0f}°")
   print(f"Vanishing angle: {results.vanishing_angle:.0f}°")
   
   # 5. Visualize
   plot_stability_curve(results, save_path='stability.png', show=True)

Interactive Exploration
-----------------------

The tool also provides interactive visualization:

.. code-block:: python

   from src.visualization import interactive_heel_explorer, interactive_cg_adjustment
   
   # Explore heel behavior interactively
   interactive_heel_explorer(hull, cg, waterline_z=-0.1)
   
   # Adjust CG and see stability effects in real-time
   interactive_cg_adjustment(hull, initial_cg=cg, waterline_z=-0.1)

Next Steps
----------

* **For Beginners**: Read the complete `USER_GUIDE.md <../USER_GUIDE.md>`_ for detailed tutorials
* **For Quick Reference**: See `QUICKREF.md <../QUICKREF.md>`_ for code snippets
* **For File Formats**: Check `INPUT_DATA_FORMATS.md <../INPUT_DATA_FORMATS.md>`_
* **For Sample Data**: See `data/README.md <../data/README.md>`_ for dataset descriptions
* Explore the :doc:`api/index` for detailed API documentation
* Check out :doc:`examples` for more usage examples  
* Read about the :doc:`theory` behind the calculations
