Theory and Mathematical Background
===================================

This section explains the theoretical foundation and mathematical methods used in the Kayak Calculator.

Coordinate System
-----------------

The application uses a right-handed Cartesian coordinate system:

* **X-axis**: Longitudinal (along kayak length, positive forward)
* **Y-axis**: Transverse (athwartship, positive to starboard)
* **Z-axis**: Vertical (positive upward)

The origin is typically placed on the centerline plane (Y=0) at a convenient longitudinal position (e.g., midship).

Hull Geometry Representation
-----------------------------

The hull is defined by a series of **transverse profiles** (cross-sections) at discrete longitudinal stations. Each profile consists of a set of points defining the hull surface at that station.

Interpolation between profiles allows calculation of properties at arbitrary positions along the length.

Volume Integration
------------------

The displaced volume is calculated by numerical integration of cross-sectional areas along the hull length:

.. math::

   V = \\int_{x_1}^{x_2} A(x) \\, dx

where :math:`A(x)` is the submerged cross-sectional area at longitudinal position :math:`x`.

Simpson's Rule
~~~~~~~~~~~~~~

For regularly spaced stations, Simpson's 1/3 rule is used:

.. math::

   V \\approx \\frac{h}{3} \\left[ A_0 + 4\\sum_{i=1,3,5}^{n-1} A_i + 2\\sum_{i=2,4,6}^{n-2} A_i + A_n \\right]

where :math:`h` is the station spacing and :math:`n` is the number of stations.

Trapezoidal Rule
~~~~~~~~~~~~~~~~

For irregular spacing or as an alternative:

.. math::

   V \\approx \\sum_{i=0}^{n-1} \\frac{A_i + A_{i+1}}{2} (x_{i+1} - x_i)

Center of Buoyancy
------------------

The center of buoyancy (CB) is the centroid of the displaced volume:

.. math::

   \\bar{x}_{CB} = \\frac{1}{V} \\int_{x_1}^{x_2} x \\cdot A(x) \\, dx

   \\bar{z}_{CB} = \\frac{1}{V} \\int_{x_1}^{x_2} \\bar{z}_c(x) \\cdot A(x) \\, dx

where :math:`\\bar{z}_c(x)` is the centroid of the cross-sectional area at position :math:`x`.

The transverse position :math:`\\bar{y}_{CB}` is calculated similarly.

Heel Transformation
-------------------

When the hull is heeled by angle :math:`\\phi` (roll about the X-axis), points are transformed:

.. math::

   \\begin{bmatrix} x' \\\\ y' \\\\ z' \\end{bmatrix} = 
   \\begin{bmatrix} 
   1 & 0 & 0 \\\\
   0 & \\cos\\phi & -\\sin\\phi \\\\
   0 & \\sin\\phi & \\cos\\phi
   \\end{bmatrix}
   \\begin{bmatrix} x \\\\ y \\\\ z \\end{bmatrix}

This rotation is applied to find the new waterline intersection and calculate heeled properties.

Righting Arm (GZ)
-----------------

The righting arm GZ is the horizontal distance between the center of gravity (G) and the center of buoyancy (B) when the hull is heeled:

.. math::

   GZ = (y_{CB} - y_{CG}) \\cos\\phi + (z_{CB} - z_{CG}) \\sin\\phi

where:

* :math:`y_{CB}, z_{CB}` are the CB coordinates in the heeled condition
* :math:`y_{CG}, z_{CG}` are the fixed CG coordinates
* :math:`\\phi` is the heel angle

The righting moment is:

.. math::

   M_r = \\Delta \\cdot GZ

where :math:`\\Delta` is the displacement (mass).

Stability Metrics
-----------------

Metacentric Height (GM)
~~~~~~~~~~~~~~~~~~~~~~~

For small angles, GM is estimated from the initial slope of the GZ curve:

.. math::

   GM \\approx \\frac{dGZ}{d\\phi}\\bigg|_{\\phi=0}

Initial transverse stability requires :math:`GM > 0`.

Range of Positive Stability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The range is the heel angle at which GZ becomes zero (angle of vanishing stability):

.. math::

   \\phi_{\\text{vanish}} : GZ(\\phi_{\\text{vanish}}) = 0

Dynamic Stability
~~~~~~~~~~~~~~~~~

The area under the GZ curve represents the work done to heel the vessel:

.. math::

   W = \\Delta \\int_0^{\\phi} GZ(\\theta) \\, d\\theta

This is a measure of the energy required to capsize the vessel.

Numerical Methods
-----------------

Waterline Intersection
~~~~~~~~~~~~~~~~~~~~~~

Finding the waterline intersection with a heeled profile involves:

1. Transform profile points by heel angle
2. Identify points above/below waterline (Z = 0 in heeled frame)
3. Linear interpolation to find exact intersection points
4. Sort points to form closed contour

Cross-Sectional Area
~~~~~~~~~~~~~~~~~~~~

The submerged area of a profile is calculated using the Shoelace formula:

.. math::

   A = \\frac{1}{2} \\left| \\sum_{i=0}^{n-1} (y_i z_{i+1} - y_{i+1} z_i) \\right|

where points are ordered counterclockwise.

Centroid of Area
~~~~~~~~~~~~~~~~

The centroid coordinates are:

.. math::

   \\bar{y} = \\frac{1}{6A} \\sum_{i=0}^{n-1} (y_i + y_{i+1})(y_i z_{i+1} - y_{i+1} z_i)

   \\bar{z} = \\frac{1}{6A} \\sum_{i=0}^{n-1} (z_i + z_{i+1})(y_i z_{i+1} - y_{i+1} z_i)

References
----------

1. Rawson, K. J., & Tupper, E. C. (2001). *Basic ship theory* (5th ed.). Butterworth-Heinemann.

2. Gillmer, T. C., & Johnson, B. (1982). *Introduction to naval architecture*. Naval Institute Press.

3. Press, W. H., et al. (2007). *Numerical recipes: The art of scientific computing* (3rd ed.). Cambridge University Press.

4. IMO. (2008). *International Code on Intact Stability, 2008*. International Maritime Organization.
