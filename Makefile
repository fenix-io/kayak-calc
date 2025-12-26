.PHONY: help lint test test-unit test-integration test-validation test-all clean install dev-install docs

# Default target
help:
	@echo "Kayak Calculation Tool - Makefile Commands"
	@echo "==========================================="
	@echo ""
	@echo "Development:"
	@echo "  make install          - Install package and dependencies"
	@echo "  make dev-install      - Install package with development dependencies"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             - Run all linters (flake8, black check, mypy)"
	@echo "  make format           - Auto-format code with black"
	@echo ""
	@echo "Testing:"
	@echo "  make test-unit        - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-validation  - Run validation tests"
	@echo "  make test-all         - Run all tests with coverage"
	@echo "  make test             - Alias for test-all"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs             - Build Sphinx documentation"
	@echo "  make docs-serve       - Build and serve documentation"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Remove build artifacts and cache files"

# Installation targets
install:
	pip install -e .

dev-install:
	pip install -e .[dev]
	pip install -r requirements.txt

# Linting and formatting
lint: lint-flake8 lint-black lint-mypy

lint-flake8:
	@echo "Running flake8..."
	flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	flake8 examples/ --max-line-length=120 --extend-ignore=E203,W503,F541,F841

lint-black:
	@echo "Checking code formatting with black..."
	black --check --line-length=100 src/ tests/ examples/

lint-mypy:
	@echo "Running mypy type checker..."
	mypy src/ --ignore-missing-imports

format:
	@echo "Formatting code with black..."
	black --line-length=100 src/ tests/ examples/

# Testing targets
test: test-all

test-unit:
	@echo "Running unit tests..."
	pytest tests/test_geometry.py \
	       tests/test_interpolation.py \
	       tests/test_transformations.py \
	       tests/test_cross_section.py \
	       tests/test_volume.py \
	       tests/test_center_of_buoyancy.py \
	       tests/test_center_of_gravity.py \
	       tests/test_righting_arm.py \
	       tests/test_hull.py \
	       tests/test_io.py \
	       tests/test_plots.py \
	       tests/test_criteria.py \
	       -v

test-integration:
	@echo "Running integration tests..."
	pytest tests/test_integration.py \
	       tests/test_analyzer.py \
	       -v

test-validation:
	@echo "Running validation tests..."
	pytest tests/test_validation.py \
	       tests/test_validation_cases.py \
	       -v

test-all:
	@echo "Running all tests with coverage..."
	pytest tests/ \
	       -v \
	       --cov=src \
	       --cov-report=term-missing \
	       --cov-report=html

# Documentation
docs:
	@echo "Building Sphinx documentation..."
	cd docs && make html

docs-serve: docs
	@echo "Serving documentation at http://localhost:8000"
	@echo "Press Ctrl+C to stop..."
	cd docs/_build/html && python -m http.server 8000

# Cleanup
clean:
	@echo "Cleaning build artifacts and cache files..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	cd docs && make clean

# Combined targets for convenience
check: lint test-all
	@echo "All checks passed!"

ci: clean lint test-all
	@echo "CI pipeline completed successfully!"
