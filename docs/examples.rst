Examples
========

This section provides practical examples for using the Kayak Calculator.

Basic Examples
--------------

Loading Hull Data
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.io import load_hull_from_json
   
   # Load from JSON file
   hull = load_hull_from_json('data/sample_hull_kayak.json')
   
   # Check hull properties
   print(f"Number of profiles: {len(hull.profiles)}")
   print(f"Stations: {hull.get_stations()}")

Volume Calculation
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.hydrostatics import calculate_volume
   
   # Calculate volume at waterline
   volume_props = calculate_volume(
       hull,
       waterline_z=-0.2,
       heel_angle=0.0,
       num_stations=50,
       integration_method='simpson'
   )
   
   print(f"Displaced volume: {volume_props.volume:.3f} m³")
   print(f"Displaced mass: {volume_props.mass:.1f} kg")

Center of Buoyancy
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.hydrostatics import calculate_center_of_buoyancy
   
   # Calculate CB for upright condition
   cb = calculate_center_of_buoyancy(
       hull,
       waterline_z=-0.2,
       heel_angle=0.0
   )
   
   print(f"LCB: {cb.x:.3f} m")
   print(f"VCB: {cb.z:.3f} m")

Stability Analysis
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.stability import StabilityAnalyzer
   from src.hydrostatics import CenterOfGravity
   
   # Define CG
   cg = CenterOfGravity(lcg=2.5, vcg=-0.3, tcg=0.0, total_mass=100.0)
   
   # Create analyzer
   analyzer = StabilityAnalyzer(hull, cg, waterline_z=-0.2)
   
   # Generate stability curve
   curve = analyzer.generate_stability_curve(
       heel_angles=np.arange(0, 91, 5)
   )
   
   print(f"Max GZ: {curve.max_gz:.3f} m at {curve.angle_max_gz:.1f}°")
   print(f"Range: {curve.range_positive:.1f}°")

Advanced Examples
-----------------

Multi-Waterline Analysis
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.stability import calculate_stability_at_multiple_waterlines
   
   # Analyze at multiple waterlines
   waterlines = [-0.1, -0.15, -0.2, -0.25]
   results = calculate_stability_at_multiple_waterlines(
       hull, cg, waterlines
   )
   
   for wl, curve in zip(waterlines, results):
       print(f"WL {wl:.2f}m: Max GZ = {curve.max_gz:.3f} m")

Comparative Analysis
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.stability import compare_configurations
   from src.visualization import plot_stability_curve_comparison
   
   # Compare different CG positions
   cg1 = CenterOfGravity(lcg=2.5, vcg=-0.30, tcg=0.0, total_mass=100.0)
   cg2 = CenterOfGravity(lcg=2.5, vcg=-0.35, tcg=0.0, total_mass=100.0)
   
   analyzer1 = StabilityAnalyzer(hull, cg1, waterline_z=-0.2)
   analyzer2 = StabilityAnalyzer(hull, cg2, waterline_z=-0.2)
   
   curve1 = analyzer1.generate_stability_curve()
   curve2 = analyzer2.generate_stability_curve()
   
   # Plot comparison
   fig = plot_stability_curve_comparison(
       [curve1, curve2],
       labels=['VCG = -0.30m', 'VCG = -0.35m']
   )
   fig.savefig('cg_comparison.png')

Interactive Visualization
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.visualization import interactive_heel_explorer
   
   # Launch interactive heel explorer
   fig = interactive_heel_explorer(
       hull,
       waterline_z=-0.2,
       heel_range=(-45, 45)
   )
   plt.show()

Exporting Results
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.io import (
       export_stability_curve,
       export_hydrostatic_properties,
       generate_stability_report
   )
   
   # Export stability curve to CSV
   export_stability_curve(
       curve,
       'output/stability_curve.csv',
       metadata={'hull': 'Sample Kayak'}
   )
   
   # Export hydrostatic properties
   export_hydrostatic_properties(
       volume_props,
       cb,
       'output/hydrostatics.csv'
   )
   
   # Generate comprehensive report
   report = generate_stability_report(
       hull, cg, waterline_z=-0.2,
       output_path='output/report.txt'
   )

For more examples, see the ``examples/`` directory in the repository.
