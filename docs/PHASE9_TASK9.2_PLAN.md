# Phase 9, Task 9.2: User Guide - Implementation Plan

**Date:** December 26, 2025  
**Status:** Planning  
**Dependencies:** Task 9.1 (Code Documentation - Complete)

---

## Task Overview

Create a comprehensive user guide that enables users to:
1. Understand basic usage and workflows
2. Learn how to prepare and load input data
3. Perform hydrostatic and stability calculations
4. Interpret and export results
5. Use example datasets effectively

---

## Objectives

### Primary Goals
1. **Basic Usage Tutorial** - Step-by-step guide for common workflows
2. **Input Data Format Explanation** - Detailed guide on preparing hull geometry
3. **Result Interpretation Guide** - Understanding outputs and stability metrics
4. **Example Dataset Documentation** - Annotated examples with explanations

### Secondary Goals
1. Update README.md with clear quickstart
2. Create comprehensive USER_GUIDE.md
3. Update getting_started.rst with practical examples
4. Document example datasets in detail
5. Create troubleshooting section

---

## Documentation Structure

### 1. README.md Updates
**Purpose:** Quick overview and installation  
**Content:**
- Clear project description
- Quick installation instructions
- 5-minute quickstart example
- Links to detailed documentation

### 2. USER_GUIDE.md (New)
**Purpose:** Comprehensive usage guide  
**Sections:**
- Introduction and Prerequisites
- Installation and Setup
- Basic Concepts and Terminology
- Loading Hull Geometry
- Performing Calculations
  - Displacement and Volume
  - Center of Buoyancy
  - Center of Gravity
  - Stability Analysis
- Visualization and Plotting
- Exporting Results
- Working with Examples
- Troubleshooting and FAQs
- Best Practices

### 3. DOCUMENTATION_QUICKSTART.md (New)
**Purpose:** Fast reference for experienced users  
**Content:**
- Common code snippets
- API quick reference
- File format templates
- Typical workflows

### 4. docs/getting_started.rst Updates
**Purpose:** Enhanced Sphinx tutorial  
**Content:**
- More detailed workflow examples
- Common use cases
- Integration with API documentation

### 5. data/README.md (New)
**Purpose:** Document sample datasets  
**Content:**
- Description of each sample file
- What each demonstrates
- Expected results
- How to use them

---

## Content Requirements

### Tutorial Content

#### 1. Installation Section
- Prerequisites (Python version, pip)
- Virtual environment setup
- Installation methods (pip, development mode)
- Verification steps

#### 2. Basic Concepts
- Coordinate system explanation
- Hull geometry representation
- Profiles, stations, and points
- Waterline definition
- Center of gravity vs. center of buoyancy
- Stability metrics (GZ, GM, vanishing angle)

#### 3. Input Data Preparation
- How to measure or digitize hull geometry
- Profile spacing recommendations
- Point density guidelines
- JSON format walkthrough
- CSV format walkthrough
- Metadata requirements
- Common pitfalls and validation

#### 4. Calculation Workflows

**Workflow 1: Basic Displacement**
```python
# Load hull
# Set waterline
# Calculate volume and displacement
# View results
```

**Workflow 2: Center of Buoyancy**
```python
# Load hull
# Calculate CB at waterline
# Visualize CB position
```

**Workflow 3: Stability Analysis**
```python
# Load hull
# Define CG
# Generate stability curve
# Extract metrics
# Plot results
```

**Workflow 4: Complete Analysis**
```python
# Load hull
# Define CG and loading
# Calculate all properties
# Generate all visualizations
# Export report
```

#### 5. Visualization Guide
- Profile plotting
- 3D hull visualization
- Stability curves
- Interactive tools
- Exporting plots

#### 6. Result Interpretation
- Understanding displacement values
- Reading stability curves
- Interpreting GM values
- Recognizing good vs. poor stability
- Safety margins and criteria

#### 7. Exporting Results
- CSV export formats
- Report generation
- Plot export options
- Data archiving

### Example Datasets Documentation

#### For each sample file:
1. **Description** - What hull type it represents
2. **Key features** - Special characteristics
3. **Use case** - What it's good for demonstrating
4. **Expected results** - Typical values users should see
5. **Loading instructions** - Code examples

### Troubleshooting Section

Common issues:
1. **Import errors** - Missing dependencies
2. **File format errors** - Validation failures
3. **Negative volumes** - Profile ordering
4. **Unrealistic results** - Data quality issues
5. **Plotting failures** - Backend issues

---

## Implementation Steps

### Step 1: Create DOCUMENTATION_QUICKSTART.md
- Quick reference guide
- Code snippets for common tasks
- File format templates

### Step 2: Create Comprehensive USER_GUIDE.md
- Full tutorial from installation to analysis
- Multiple workflow examples
- Detailed explanations
- Links to API documentation

### Step 3: Update README.md
- Clearer quickstart
- Better organization
- Links to new guides

### Step 4: Update docs/getting_started.rst
- Enhanced with more examples
- Better integration with Sphinx docs
- Cross-references to API

### Step 5: Create data/README.md
- Document all sample datasets
- Provide expected results
- Usage examples

### Step 6: Update docs/index.rst
- Add links to new user guides
- Better navigation structure

---

## Code Examples to Include

### Example 1: Simple Displacement Calculation
```python
from src.io import load_hull_from_json
from src.hydrostatics import calculate_volume

hull = load_hull_from_json('data/sample_hull_simple.json')
volume, cb = calculate_volume(hull, waterline_z=-0.1)
displacement_kg = volume * 1025  # seawater density
print(f"Displacement: {displacement_kg:.2f} kg")
```

### Example 2: Stability Analysis
```python
from src.io import load_hull_from_json
from src.hydrostatics import CenterOfGravity
from src.stability import StabilityAnalyzer

hull = load_hull_from_json('data/sample_hull_kayak.json')
cg = CenterOfGravity(x=2.5, y=0.0, z=-0.3, mass=100.0)
analyzer = StabilityAnalyzer(hull, cg)

results = analyzer.calculate_stability_curve(
    waterline_z=-0.1,
    heel_angles=range(0, 91, 5)
)

print(f"Initial GM: {results.initial_gm:.3f} m")
print(f"Max GZ: {results.max_gz:.3f} m at {results.max_gz_angle:.1f}°")
```

### Example 3: Visualization
```python
from src.visualization import plot_stability_curve, plot_hull_3d

analyzer = StabilityAnalyzer(hull, cg)
results = analyzer.calculate_stability_curve(waterline_z=-0.1)

plot_stability_curve(results, save_path='stability.png')
plot_hull_3d(hull, waterline_z=-0.1, heel_angle=30)
```

---

## Success Criteria

1. ✅ User can install and run first example in < 5 minutes
2. ✅ All common workflows have clear examples
3. ✅ Input data formats are clearly explained
4. ✅ Result interpretation guidance is comprehensive
5. ✅ All sample datasets are documented
6. ✅ Troubleshooting covers common issues
7. ✅ Links between guides and API docs work correctly
8. ✅ Examples run without modification

---

## Quality Checks

- [ ] All code examples tested and working
- [ ] All links verified
- [ ] Consistent terminology throughout
- [ ] Clear progression from simple to complex
- [ ] Cross-references between documents
- [ ] Spell check and grammar review
- [ ] Screenshots/diagrams where helpful

---

## Estimated Effort

- DOCUMENTATION_QUICKSTART.md: 1 hour
- USER_GUIDE.md: 3-4 hours
- README.md updates: 30 minutes
- getting_started.rst updates: 1 hour
- data/README.md: 1 hour
- Testing and review: 1 hour

**Total: 7-8 hours**

---

## References

- Existing documentation:
  - INPUT_DATA_FORMATS.md
  - OUTPUT_DATA_FORMATS.md
  - docs/getting_started.rst
  - docs/examples.rst
  - docs/theory.rst
- Example files in examples/
- Sample data in data/
- API documentation (from Task 9.1)
