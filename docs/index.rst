.. Kayak Calculator documentation master file

Welcome to Kayak Calculator's documentation!
==============================================

**Kayak Calculator** is a Python application for calculating kayak hydrostatic parameters and stability characteristics using numerical naval architecture methods.

The application calculates:

* **Displacement**: Volume and mass of water displaced by the kayak
* **Stability Curves**: GZ curves showing righting moment vs. heel angle
* **Center of Gravity (CG)**: 3D position of the mass centroid (from components or direct)
* **Center of Buoyancy (CB)**: 3D centroid of the displaced volume (upright and heeled)
* **Stability Metrics**: GM, vanishing angle, dynamic stability, and criteria assessment

Documentation Structure
-----------------------

.. toctree::
   :maxdepth: 2
   :caption: User Guides:

   getting_started

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   api/index

.. toctree::
   :maxdepth: 1
   :caption: Additional Documentation:

   examples
   theory

.. note::
   
   **Complete User Guides Available:**
   
   * `USER_GUIDE.md <../USER_GUIDE.md>`_ - Complete tutorial from installation to advanced usage
   * `QUICKREF.md <../QUICKREF.md>`_ - Quick reference for experienced users
   * `INPUT_DATA_FORMATS.md <../INPUT_DATA_FORMATS.md>`_ - Hull geometry file format specifications
   * `OUTPUT_DATA_FORMATS.md <../OUTPUT_DATA_FORMATS.md>`_ - Export format documentation
   * `data/README.md <../data/README.md>`_ - Sample dataset descriptions

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   git clone <repository-url>
   cd kyk-calc
   pip install -e .

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from src.io import load_hull_from_json
   from src.hydrostatics import CenterOfGravity
   from src.stability import StabilityAnalyzer
   from src.visualization import plot_stability_curve

   # Load hull geometry
   hull = load_hull_from_json('data/sample_hull_kayak.json')

   # Define center of gravity
   cg = CenterOfGravity(x=2.5, y=0.0, z=-0.3, mass=100.0)

   # Analyze stability
   analyzer = StabilityAnalyzer(hull, cg)
   results = analyzer.calculate_stability_curve(waterline_z=-0.1)

   # Print key metrics
   print(f"Initial GM: {results.initial_gm:.3f} m")
   print(f"Max GZ: {results.max_gz:.3f} m at {results.max_gz_angle:.0f}°")
   print(f"Vanishing angle: {results.vanishing_angle:.0f}°")

   # Visualize
   plot_stability_curve(results, save_path='stability.png', show=True)

Features
--------

✨ **Hydrostatic Calculations**

* Displacement and volume integration
* Center of buoyancy (3D)
* Center of gravity from components
* Cross-section properties

⚓ **Stability Analysis**

* GZ curves (0-90° heel)
* Metacentric height (GM)
* Vanishing angle
* Dynamic stability
* Criteria assessment

📊 **Visualization**

* 3D hull plots
* Profile cross-sections
* Stability curves
* Interactive tools
* Animations

💾 **Data I/O**

* JSON and CSV input
* CSV and report export
* Comprehensive validation

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
