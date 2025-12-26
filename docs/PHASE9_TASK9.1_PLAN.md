# Phase 9: Task 9.1 - Code Documentation Plan

## Objective
Add comprehensive docstrings to all classes and functions, and set up automated API documentation generation using Sphinx.

## Subtasks

### 1. Documentation Standard Selection
- Choose docstring format: **Google style** (recommended for readability)
- Alternative: NumPy style, reStructuredText
- Ensure consistency across all modules

### 2. Audit Current Documentation State
- Identify modules/classes/functions lacking docstrings
- Identify incomplete docstrings
- Review existing docstrings for consistency

### 3. Add/Update Docstrings by Module

#### 3.1 Geometry Module (`src/geometry/`)
- `hull.py` - Point3D, Profile, KayakHull classes
- `interpolation.py` - All interpolation functions
- `transformations.py` - Transformation functions

#### 3.2 Hydrostatics Module (`src/hydrostatics/`)
- `cross_section.py` - Cross-section calculation functions
- `volume.py` - Volume integration functions
- `center_of_buoyancy.py` - CB calculation functions
- `center_of_gravity.py` - CG class and functions

#### 3.3 Stability Module (`src/stability/`)
- `righting_arm.py` - GZ calculation functions
- `analyzer.py` - StabilityAnalyzer class
- `criteria.py` - Stability criteria functions

#### 3.4 Visualization Module (`src/visualization/`)
- `plots.py` - All plotting functions (static, interactive, animation)

#### 3.5 IO Module (`src/io/`)
- `defaults.py` - Default configurations
- `formats.py` - Data format specifications
- `validators.py` - Validation functions
- `loaders.py` - Data loading functions
- `exporters.py` - Data export functions (if exists)

#### 3.6 Configuration (`src/`)
- `config.py` - Configuration constants and settings

### 4. Docstring Content Requirements

For each function/method:
- **Brief description** (one line summary)
- **Detailed description** (if needed)
- **Parameters** (type, description)
- **Returns** (type, description)
- **Raises** (exceptions, when they occur)
- **Examples** (code snippets demonstrating usage)
- **Notes** (implementation details, mathematical formulas)
- **References** (citations to papers, books, standards)

For each class:
- **Brief description**
- **Detailed description** (purpose, usage)
- **Attributes** (public attributes with types and descriptions)
- **Examples** (basic usage)
- **Notes** (design decisions, limitations)

### 5. Sphinx Documentation Setup

#### 5.1 Install Sphinx and Extensions
```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
```

#### 5.2 Initialize Sphinx
```bash
cd docs
sphinx-quickstart
```

#### 5.3 Configure Sphinx (`docs/conf.py`)
- Set project name, author, version
- Add extensions: autodoc, napoleon, viewcode
- Set theme: sphinx_rtd_theme
- Configure autodoc to include all members

#### 5.4 Create Documentation Structure
- `docs/index.rst` - Main documentation page
- `docs/api/` - API reference pages
  - `docs/api/geometry.rst`
  - `docs/api/hydrostatics.rst`
  - `docs/api/stability.rst`
  - `docs/api/visualization.rst`
  - `docs/api/io.rst`
- `docs/guides/` - User guides
- `docs/tutorials/` - Tutorials

#### 5.5 Build Documentation
```bash
cd docs
make html
```

### 6. Quality Checks
- Verify all public functions/classes have docstrings
- Check docstring format consistency
- Build Sphinx documentation without errors
- Review generated HTML documentation
- Check cross-references work correctly

## Implementation Order

1. **Setup** (Task 5: Sphinx Setup)
2. **Core Geometry** (Task 3.1: geometry module)
3. **Hydrostatics** (Task 3.2: hydrostatics module)
4. **Stability** (Task 3.3: stability module)
5. **Visualization** (Task 3.4: visualization module)
6. **IO** (Task 3.5: io module)
7. **Config** (Task 3.6: config module)
8. **Quality Assurance** (Task 6: Review and verify)

## Estimated Effort

- Audit: 30 minutes
- Docstring writing: 4-6 hours (depending on current state)
- Sphinx setup: 1-2 hours
- Review and refinement: 1 hour
- **Total: 6-9 hours**

## Success Criteria

- [ ] All public classes have complete docstrings
- [ ] All public functions/methods have complete docstrings
- [ ] Docstrings follow Google style guide consistently
- [ ] Mathematical formulas documented with LaTeX notation
- [ ] Sphinx builds successfully without warnings
- [ ] Generated API documentation is readable and navigable
- [ ] Examples in docstrings are executable
- [ ] Cross-references between modules work correctly

## References

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Napoleon Extension](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)
