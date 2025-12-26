# Documentation

This directory contains the Sphinx documentation for the Kayak Calculator project.

## Building the Documentation

### Prerequisites

Install Sphinx and related dependencies:

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
```

Or install all project dependencies including documentation tools:

```bash
pip install -r requirements.txt
```

### Build HTML Documentation

From the `docs` directory:

```bash
make html
```

The generated HTML documentation will be in `_build/html/`. Open `_build/html/index.html` in your browser to view it.

### Clean Build

To remove all build artifacts and rebuild from scratch:

```bash
make clean
make html
```

### Other Output Formats

Sphinx supports multiple output formats:

```bash
make latexpdf  # PDF via LaTeX
make epub      # EPUB ebook format
make man       # Unix manual pages
make help      # Show all available formats
```

## Documentation Structure

- `index.rst` - Main documentation page
- `getting_started.rst` - Installation and basic usage guide
- `examples.rst` - Usage examples and code snippets
- `theory.rst` - Mathematical background and theory
- `api/` - API reference documentation
  - `index.rst` - API overview
  - `geometry.rst` - Geometry module docs
  - `hydrostatics.rst` - Hydrostatics module docs
  - `stability.rst` - Stability module docs
  - `visualization.rst` - Visualization module docs
  - `io.rst` - IO module docs
  - `config.rst` - Configuration docs
- `conf.py` - Sphinx configuration file
- `_static/` - Static files (CSS, images, etc.)
- `_templates/` - Custom Sphinx templates
- `_build/` - Generated documentation (gitignored)

## Docstring Format

All docstrings in the source code follow the **Google style** guide:

```python
def function_name(param1: int, param2: str) -> bool:
    """
    Brief description of the function.
    
    Longer description providing more details about what the function
    does, how it works, and any important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of the return value
    
    Raises:
        ValueError: When and why this exception is raised
    
    Example:
        >>> result = function_name(42, "test")
        >>> print(result)
        True
    
    Note:
        Additional notes, implementation details, or caveats.
    """
    pass
```

## Updating Documentation

1. **Update docstrings** in the source code (`src/`)
2. **Update .rst files** in `docs/` for guides and examples
3. **Rebuild** the documentation: `make html`
4. **Review** the generated HTML in `_build/html/`

## Publishing Documentation

The documentation can be published to:

- **GitHub Pages**: Use GitHub Actions to build and deploy
- **Read the Docs**: Connect your repository for automatic builds
- **Custom web server**: Copy `_build/html/` to your server

## Docstring Coverage

Run the docstring audit script to check coverage:

```bash
cd ..
python audit_docstrings.py
```

Current coverage: **100%** ✓

## Troubleshooting

### Import Errors

If you see import errors when building:

1. Ensure the package is installed: `pip install -e .`
2. Check `sys.path` in `conf.py` includes the src directory

### Missing Modules

If Sphinx can't find modules:

```bash
pip install -e .  # Install package in editable mode
```

### Build Warnings

Some warnings about duplicate object descriptions are expected when documenting modules and their classes separately. These can be safely ignored.
