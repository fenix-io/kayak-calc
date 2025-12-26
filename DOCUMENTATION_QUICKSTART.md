# Quick Start: Using the Documentation

## Viewing the Documentation

### Option 1: Local HTML (Recommended)

The documentation is already built and ready to view:

```bash
# Open in your default browser
xdg-open docs/_build/html/index.html

# Or use a specific browser
firefox docs/_build/html/index.html
chromium docs/_build/html/index.html
```

### Option 2: Local Web Server

Serve the documentation locally:

```bash
cd docs/_build/html
python -m http.server 8000
```

Then open http://localhost:8000 in your browser.

### Option 3: Rebuild First

If you want to rebuild before viewing:

```bash
cd docs
make clean
make html
firefox _build/html/index.html
```

## Navigation Guide

### Main Page (`index.html`)
- Project overview
- Quick start code example
- Links to all documentation sections

### Getting Started (`getting_started.html`)
- Installation instructions
- Coordinate system explanation
- Input data formats
- Basic workflow examples

### Examples (`examples.html`)
- Code snippets for common tasks
- Basic examples (loading, volume, CB, stability)
- Advanced examples (comparisons, interactive)
- Export and reporting

### Theory (`theory.html`)
- Mathematical background
- Coordinate system
- Volume integration methods
- Stability calculations
- References to literature

### API Reference (`api/*.html`)
- Complete API documentation
- **Geometry** - Hull, profiles, points, interpolation, transformations
- **Hydrostatics** - Volume, buoyancy, center of gravity
- **Stability** - Analyzer, righting arm, criteria
- **Visualization** - Plotting functions
- **IO** - Data loading and exporting
- **Config** - Configuration settings

## Search Functionality

Use the search box in the top-left corner to find:
- Function names
- Class names
- Concepts
- Examples

## Links to Source Code

Each documented function/class has a "[source]" link that shows the actual implementation in the codebase.

## Cross-References

- Blue hyperlinks connect related functions and classes
- Click on parameter types to see their documentation
- Click on module names to jump to that module's docs

## Tips

1. **Start with Getting Started** if you're new to the project
2. **Use Examples** for copy-paste ready code
3. **Read Theory** to understand the mathematics
4. **Browse API Reference** when you need detailed function info
5. **Use Search** when looking for something specific

## Publishing Online

### Option A: Read the Docs (Recommended)

1. Sign up at https://readthedocs.org
2. Connect your GitHub repository
3. Enable the project
4. Documentation builds automatically on git push

### Option B: GitHub Pages

1. Build docs: `cd docs && make html`
2. Copy to gh-pages branch: `cp -r _build/html/* ../gh-pages/`
3. Push to GitHub
4. Enable GitHub Pages in repository settings

### Option C: Custom Server

1. Build docs: `cd docs && make html`
2. Copy `_build/html/*` to your web server
3. Configure web server to serve static files

## Maintenance

### Checking Coverage

```bash
python audit_docstrings.py
```

### Rebuilding After Code Changes

```bash
cd docs
make clean
make html
```

### Adding New Documentation

1. Update docstrings in source code
2. Update .rst files in `docs/` if needed
3. Rebuild: `cd docs && make html`

## Verification

Run the verification script to check everything:

```bash
./verify_docs.sh
```

This checks:
- ✓ Docstring coverage is 100%
- ✓ Documentation builds successfully
- ✓ All required files exist
- ✓ Sphinx and dependencies installed

## Need Help?

- Check `docs/README.md` for detailed documentation guide
- See `docs/PHASE9_TASK9.1_SUMMARY.md` for implementation details
- Review `audit_docstrings.py` source for coverage checking
