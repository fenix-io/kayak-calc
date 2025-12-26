# Phase 9, Task 9.3 Plan: Example Scripts

**Status:** Planning
**Date:** December 26, 2025

## Objective

Create comprehensive example calculation scripts demonstrating:
1. Basic displacement calculation workflows
2. Full stability analysis workflows
3. Integration of visualization features
4. End-to-end calculation pipelines

Add extensive comments and explanations to make examples instructional.

## Current Status

### Existing Example Scripts
We currently have 15 example scripts covering individual components:
1. `center_of_buoyancy_examples.py` - CB calculation demos
2. `center_of_gravity_examples.py` - CG definition and manipulation
3. `cross_section_examples.py` - Cross-section property calculations
4. `data_input_examples.py` - Loading hull data from JSON/CSV
5. `data_output_examples.py` - Exporting results and generating reports
6. `interactive_visualization_examples.py` - Interactive plots and animations
7. `interpolation_examples.py` - All interpolation methods
8. `profile_plotting_examples.py` - Profile and hull plotting
9. `righting_arm_examples.py` - GZ calculations
10. `stability_analyzer_examples.py` - StabilityAnalyzer class usage
11. `stability_criteria_examples.py` - Stability criteria assessment
12. `stability_curve_plotting_examples.py` - Stability visualization
13. `transformation_examples.py` - Heel and trim transformations
14. `volume_examples.py` - Displacement volume calculations
15. `README.md` - Documentation of all examples

### What's Missing

While we have excellent component-level examples, we need **end-to-end workflow scripts** that:
1. Start from raw data and go through complete analysis
2. Demonstrate common use cases a user would have
3. Show best practices for combining multiple features
4. Provide templates users can adapt for their needs

## Proposed New Example Scripts

### 1. `basic_displacement_workflow.py`
**Purpose:** Complete workflow for basic displacement calculation

**Workflow:**
1. Load hull from JSON file (use existing sample data)
2. Define waterline level
3. Calculate displacement volume and mass
4. Calculate center of buoyancy (LCB, VCB)
5. Generate visualizations:
   - Hull geometry with waterline
   - Cross-section plots
   - Summary report
6. Export results to CSV and report

**Educational Focus:**
- Most common beginner use case
- Simple, clear workflow
- Demonstrates file I/O
- Shows basic visualization

**Length:** ~200-250 lines with comments

### 2. `complete_stability_analysis.py`
**Purpose:** Full stability analysis from data to report

**Workflow:**
1. Load hull geometry (realistic kayak data)
2. Define center of gravity (multiple components)
3. Calculate hydrostatic properties
4. Perform stability analysis:
   - Generate GZ curve
   - Calculate stability metrics (GM, max GZ, vanishing angle)
   - Check stability criteria
5. Create comprehensive visualizations:
   - Hull geometry
   - Stability curves
   - Criteria assessment report
6. Generate and export complete analysis report

**Educational Focus:**
- Professional-level analysis workflow
- Multiple CG configurations
- Stability assessment
- Report generation

**Length:** ~300-350 lines with comments

### 3. `parametric_study_workflow.py`
**Purpose:** Compare multiple configurations systematically

**Workflow:**
1. Load base hull geometry
2. Define multiple scenarios to compare:
   - Different CG locations (light load, normal, heavy load)
   - Different waterline levels (loading conditions)
3. Calculate and compare:
   - Displacement for each condition
   - Stability curves
   - Stability metrics
4. Create comparison visualizations:
   - Side-by-side GZ curves
   - Metric comparison tables
   - Criteria pass/fail summary
5. Generate comparative report

**Educational Focus:**
- Design exploration
- Configuration comparison
- Decision-making support
- Advanced analysis

**Length:** ~250-300 lines with comments

### 4. `quick_assessment_script.py`
**Purpose:** Template for rapid initial assessment

**Workflow:**
1. Minimal setup (quick hull definition or loading)
2. Define CG (simple)
3. Run quick analysis functions:
   - `quick_stability_analysis()`
   - `quick_criteria_check()`
4. Display console summary output
5. Save quick report

**Educational Focus:**
- Speed and efficiency
- Using high-level convenience functions
- Template for copy-paste adaptation
- Minimal visualization

**Length:** ~150-200 lines with comments

### 5. `advanced_visualization_workflow.py`
**Purpose:** Showcase all visualization capabilities

**Workflow:**
1. Load hull and perform basic analysis
2. Create all visualization types:
   - Static plots (profiles, hull 3D, GZ curves)
   - Comparison plots (multiple configurations)
   - Interactive explorers (heel angle, CG adjustment)
   - Animations (heel sequence)
3. Export in multiple formats (PNG, PDF, MP4)
4. Create figure gallery

**Educational Focus:**
- Complete visualization showcase
- Interactive features
- Animation capabilities
- Publication-quality plots

**Length:** ~250-300 lines with comments

## Documentation Requirements

Each script should include:

### Header Documentation
```python
"""
Script title and brief description.

This script demonstrates:
- Key feature 1
- Key feature 2
- Key feature 3

Prerequisites:
- Required data files
- Python packages needed

Expected outputs:
- Output file 1
- Output file 2

Usage:
    python examples/script_name.py

Author: Kayak Calculation Tool
Version: 1.0
"""
```

### Section Comments
- Clear section headers using comment blocks
- Step-by-step explanations
- Reasoning for parameter choices
- Interpretation of results

### Inline Comments
- Explain non-obvious operations
- Note important assumptions
- Reference equations or theory where relevant

### Output Messages
- Print progress messages
- Show calculated values with units
- Indicate where output files are saved

## Update `examples/README.md`

Add comprehensive documentation for each new script:
- What it demonstrates
- How to run it
- Expected outputs
- When to use it as a template

## Testing Requirements

1. All scripts must run successfully with provided sample data
2. Generate expected output files in `examples/output/`
3. Produce clear console output
4. Handle errors gracefully
5. Complete in reasonable time (< 30 seconds each)

## Implementation Steps

1. Create `basic_displacement_workflow.py` (simple case)
2. Create `quick_assessment_script.py` (convenience functions)
3. Create `complete_stability_analysis.py` (full workflow)
4. Create `parametric_study_workflow.py` (comparison)
5. Create `advanced_visualization_workflow.py` (viz showcase)
6. Update `examples/README.md` with new scripts
7. Test all scripts
8. Review for clarity and completeness

## Success Criteria

- [ ] 5 new comprehensive example scripts created
- [ ] All scripts run successfully without errors
- [ ] Extensive comments and explanations throughout
- [ ] Clear console output with progress messages
- [ ] Generate useful output files and visualizations
- [ ] Updated README.md documenting all new scripts
- [ ] Scripts serve as templates users can adapt
- [ ] Cover common use cases from simple to advanced
- [ ] Code is clean, well-structured, and follows project style

## Expected Deliverables

1. **New Python Scripts** (5 files)
   - `examples/basic_displacement_workflow.py`
   - `examples/quick_assessment_script.py`
   - `examples/complete_stability_analysis.py`
   - `examples/parametric_study_workflow.py`
   - `examples/advanced_visualization_workflow.py`

2. **Updated Documentation**
   - `examples/README.md` (enhanced with new scripts)

3. **Summary Document**
   - `docs/PHASE9_TASK9.3_SUMMARY.md`

## Timeline

Estimated time: 4-5 hours
- Script development: 3-4 hours
- Testing and refinement: 30-45 minutes
- Documentation: 30-45 minutes

## Notes

- Use existing sample data files where possible
- Scripts should be self-contained (can run independently)
- Balance between educational clarity and concise code
- Show realistic use cases, not just toy examples
- Make scripts easy to adapt for user's own data
