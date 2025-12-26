#!/bin/bash
# Verification script for Phase 9, Task 9.1 - Code Documentation

echo "=========================================="
echo "Phase 9 Task 9.1 Verification"
echo "=========================================="
echo ""

# Check docstring coverage
echo "1. Checking docstring coverage..."
python audit_docstrings.py | grep -E "(Coverage:|Files Checked:|Missing:)"
echo ""

# Check Sphinx documentation built
echo "2. Checking Sphinx documentation..."
if [ -f "docs/_build/html/index.html" ]; then
    echo "✓ HTML documentation generated"
    echo "  Location: docs/_build/html/index.html"
    echo "  Size: $(du -h docs/_build/html/index.html | cut -f1)"
else
    echo "✗ HTML documentation not found"
fi
echo ""

# Count documentation files
echo "3. Documentation files:"
echo "  RST files: $(find docs -name "*.rst" | wc -l)"
echo "  HTML pages: $(find docs/_build/html -name "*.html" 2>/dev/null | wc -l)"
echo "  API modules: $(ls docs/api/*.rst 2>/dev/null | wc -l)"
echo ""

# Check key files exist
echo "4. Key files verification:"
files=(
    "docs/conf.py"
    "docs/Makefile"
    "docs/index.rst"
    "docs/getting_started.rst"
    "docs/examples.rst"
    "docs/theory.rst"
    "docs/api/index.rst"
    "audit_docstrings.py"
    "docs/PHASE9_TASK9.1_SUMMARY.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (missing)"
    fi
done
echo ""

# Check Sphinx dependencies
echo "5. Checking Sphinx installation..."
if python -c "import sphinx" 2>/dev/null; then
    version=$(python -c "import sphinx; print(sphinx.__version__)")
    echo "  ✓ Sphinx installed (version $version)"
else
    echo "  ✗ Sphinx not installed"
fi

if python -c "import sphinx_rtd_theme" 2>/dev/null; then
    echo "  ✓ sphinx_rtd_theme installed"
else
    echo "  ✗ sphinx_rtd_theme not installed"
fi
echo ""

# Test documentation build
echo "6. Testing documentation build..."
cd docs && make clean > /dev/null 2>&1
if make html > /tmp/sphinx_build.log 2>&1; then
    errors=$(grep -i "error" /tmp/sphinx_build.log | wc -l)
    warnings=$(grep -i "warning" /tmp/sphinx_build.log | wc -l)
    echo "  ✓ Build successful"
    echo "    Errors: $errors"
    echo "    Warnings: $warnings"
else
    echo "  ✗ Build failed"
    echo "    See /tmp/sphinx_build.log for details"
fi
cd ..
echo ""

echo "=========================================="
echo "Verification Complete!"
echo "=========================================="
echo ""
echo "To view documentation:"
echo "  firefox docs/_build/html/index.html"
echo ""
echo "To rebuild documentation:"
echo "  cd docs && make html"
echo ""
