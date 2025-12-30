# Phase 9, Task 9.6 - Input Format Documentation Update

## Task Overview
Update the user documentation to reflect the removal of explicit `bow` and `stern` entries from the JSON hull format, clarify preferred point ordering for profiles, and explain how bow/stern positions are derived from profile data.

## Objectives
1. Remove all references to `bow` and `stern` entries in JSON format examples
2. Document preferred point ordering for profiles (port waterline → keel → starboard waterline)
3. Explain how bow/stern positions are derived from the profile endpoints
4. Update all affected documentation files consistently

## Current State Analysis

### Files to Update
1. **USER_GUIDE.md** - Contains JSON format examples and hull geometry explanations
2. **QUICKREF.md** - Contains quick reference examples for data input
3. **INPUT_DATA_FORMATS.md** - Detailed format specification (if exists)
4. **data/README.md** - Sample data documentation
5. **docs/getting_started.rst** - Getting started guide
6. **README.md** - Project overview (if contains format info)

### Key Changes Needed
1. Remove `bow` and `stern` fields from all JSON examples
2. Add clear documentation on point ordering conventions
3. Add explanation of how bow/stern are determined from profiles
4. Update any diagrams or illustrations if present
5. Ensure consistency across all documentation

## Implementation Plan

### Step 1: Analyze Current Documentation
- [x] Read USER_GUIDE.md to identify all JSON examples
- [x] Read QUICKREF.md to identify format references
- [x] Check INPUT_DATA_FORMATS.md for format specifications
- [x] Review data/README.md for sample data docs
- [x] Check docs/getting_started.rst

### Step 2: Update JSON Format Examples
- [ ] Remove `bow` and `stern` entries from all JSON examples
- [ ] Add comments/notes about profile-based geometry
- [ ] Ensure examples are valid and consistent

### Step 3: Document Point Ordering
- [ ] Add section on preferred point ordering conventions
- [ ] Explain port → keel → starboard traversal
- [ ] Provide visual/textual examples
- [ ] Document why consistent ordering matters

### Step 4: Explain Bow/Stern Derivation
- [ ] Add explanation of how bow/stern are derived from profiles
- [ ] Clarify that first/last profiles define bow/stern
- [ ] Note that explicit fields are no longer needed
- [ ] Explain how the code determines bow/stern positions

### Step 5: Update All Documentation Files
- [ ] USER_GUIDE.md
- [ ] QUICKREF.md
- [ ] INPUT_DATA_FORMATS.md (if exists)
- [ ] data/README.md
- [ ] docs/getting_started.rst
- [ ] README.md (if needed)

### Step 6: Verify Sample Data Files
- [ ] Check data/sample_hull_kayak.json
- [ ] Check data/sample_hull_simple.json
- [ ] Ensure they match the documented format
- [ ] Update if necessary

### Step 7: Quality Assurance
- [ ] Run make lint and make format
- [ ] Verify all examples still work
- [ ] Check for broken links or references
- [ ] Ensure consistency across all docs

## Documentation Sections to Add

### Section 1: Point Ordering Convention
```
### Profile Point Ordering

Each profile should list points in a consistent order for reliable calculations:

**Recommended ordering:**
1. Start at port side waterline (or deck edge)
2. Progress downward along the port side
3. Continue through the keel (lowest point)
4. Progress upward along the starboard side
5. End at starboard waterline (or deck edge)

**Example ordering for a kayak profile:**
- Point 0: Port deck edge (left side, high)
- Point 1: Port chine (if present)
- Point 2: Port bilge
- Point 3: Keel (centerline, lowest)
- Point 4: Starboard bilge
- Point 5: Starboard chine (if present)
- Point 6: Starboard deck edge (right side, high)

**Why consistent ordering matters:**
- Ensures correct area calculations
- Maintains proper waterline intersections
- Enables accurate interpolation
- Prevents reversed normals
```

### Section 2: Bow/Stern Derivation
```
### Bow and Stern Positions

The kayak hull geometry is now defined entirely by the `profiles` array. 
There is no need for explicit `bow` or `stern` entries in the JSON format.

**How bow/stern are determined:**
- The **first profile** (lowest x-coordinate) defines the bow
- The **last profile** (highest x-coordinate) defines the stern
- The bow/stern positions are taken from the profile endpoints

**Example:**
If your profiles are at x = [0.0, 1.0, 2.0, 3.0, 4.0]:
- Bow position: The profile at x = 0.0 defines the bow geometry
- Stern position: The profile at x = 4.0 defines the stern geometry

**Note:** For kayaks that come to a point at bow/stern, the first/last 
profile should contain points that converge toward the centerline, 
defining the tapered shape.
```

## Expected Outcomes

### Documentation Updates
- All JSON examples will show only `profiles` array
- Clear point ordering guidance added
- Bow/stern derivation explained
- Consistent documentation across all files

### User Benefits
- Clearer understanding of data format
- Less confusion about bow/stern fields
- Better guidance on creating valid hull data
- More consistent data structures

### Backward Compatibility
- Existing sample files remain valid (if they don't use bow/stern)
- Code should already handle this (Task 9.5 may have addressed this)
- No breaking changes to working user data

## Success Criteria

1. [ ] All `bow`/`stern` references removed from JSON examples
2. [ ] Point ordering conventions clearly documented
3. [ ] Bow/stern derivation explained in user-facing docs
4. [ ] All documentation files updated consistently
5. [ ] Sample data files match documented format
6. [ ] Documentation builds without errors
7. [ ] All examples still run successfully
8. [ ] make lint and make format pass

## Timeline
- Analysis: 15 minutes
- Implementation: 45 minutes
- Testing and verification: 15 minutes
- **Total estimated time:** 75 minutes

## Notes
- Focus on clarity and user-friendliness
- Use examples to illustrate concepts
- Ensure consistency across all documentation
- This completes the documentation cleanup after hull CG automation
