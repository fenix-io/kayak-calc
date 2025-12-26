#!/usr/bin/env python3
"""Script to automatically fix linting issues."""

import re
import subprocess
from pathlib import Path

def fix_unused_imports():
    """Remove unused imports using autoflake."""
    subprocess.run([
        "autoflake",
        "--in-place",
        "--remove-all-unused-imports",
        "--remove-unused-variables",
        "--recursive",
        "src/", "tests/", "examples/"
    ], check=False)

def fix_formatting():
    """Fix formatting issues with autopep8."""
    subprocess.run([
        "autopep8",
        "--in-place",
        "--aggressive",
        "--aggressive",
        "--max-line-length=100",
        "--recursive",
        "src/", "tests/", "examples/"
    ], check=False)

if __name__ == "__main__":
    print("Installing autoflake and autopep8...")
    subprocess.run(["pip", "install", "-q", "autoflake", "autopep8"], check=False)
    
    print("\nRemoving unused imports and variables...")
    fix_unused_imports()
    
    print("\nFixing formatting issues...")
    fix_formatting()
    
    print("\nDone!")
