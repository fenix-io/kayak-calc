#!/usr/bin/env python3
"""
Script to audit docstring coverage in the codebase.

Checks all Python files for docstrings on classes and functions.
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Tuple


class DocstringAuditor(ast.NodeVisitor):
    """Visit AST nodes to check for docstrings."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.missing_docstrings = []
        self.has_docstrings = []
        
    def visit_FunctionDef(self, node):
        """Check function docstrings."""
        docstring = ast.get_docstring(node)
        name = node.name
        line = node.lineno
        
        # Skip private functions (but include __init__ and __special__)
        if name.startswith('_') and not (name.startswith('__') and name.endswith('__')):
            self.generic_visit(node)
            return
            
        if docstring:
            self.has_docstrings.append(('function', name, line, len(docstring)))
        else:
            self.missing_docstrings.append(('function', name, line))
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Check async function docstrings."""
        self.visit_FunctionDef(node)
    
    def visit_ClassDef(self, node):
        """Check class docstrings."""
        docstring = ast.get_docstring(node)
        name = node.name
        line = node.lineno
        
        # Skip private classes
        if name.startswith('_'):
            self.generic_visit(node)
            return
            
        if docstring:
            self.has_docstrings.append(('class', name, line, len(docstring)))
        else:
            self.missing_docstrings.append(('class', name, line))
        
        self.generic_visit(node)


def audit_file(filepath: Path) -> Tuple[List, List]:
    """
    Audit a single Python file for docstrings.
    
    Returns:
        Tuple of (missing, present) docstring lists
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        auditor = DocstringAuditor(str(filepath))
        auditor.visit(tree)
        
        return auditor.missing_docstrings, auditor.has_docstrings
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return [], []


def audit_directory(directory: Path) -> Dict:
    """Audit all Python files in a directory."""
    results = {
        'files': {},
        'totals': {
            'total_items': 0,
            'documented': 0,
            'missing': 0,
            'files_checked': 0
        }
    }
    
    for pyfile in directory.rglob('*.py'):
        # Skip __pycache__ and test files
        if '__pycache__' in str(pyfile) or 'tests' in str(pyfile):
            continue
            
        missing, present = audit_file(pyfile)
        
        if missing or present:
            rel_path = pyfile.relative_to(directory)
            results['files'][str(rel_path)] = {
                'missing': missing,
                'present': present,
                'coverage': len(present) / (len(present) + len(missing)) * 100 if (present or missing) else 100
            }
            
            results['totals']['documented'] += len(present)
            results['totals']['missing'] += len(missing)
            results['totals']['total_items'] += len(present) + len(missing)
            results['totals']['files_checked'] += 1
    
    return results


def print_report(results: Dict):
    """Print a formatted report of the audit."""
    print("\n" + "="*80)
    print("DOCSTRING COVERAGE AUDIT REPORT")
    print("="*80 + "\n")
    
    # Overall statistics
    totals = results['totals']
    overall_coverage = (totals['documented'] / totals['total_items'] * 100) if totals['total_items'] > 0 else 100
    
    print(f"Files Checked: {totals['files_checked']}")
    print(f"Total Items (classes/functions): {totals['total_items']}")
    print(f"Documented: {totals['documented']}")
    print(f"Missing Docstrings: {totals['missing']}")
    print(f"Overall Coverage: {overall_coverage:.1f}%")
    print("\n" + "-"*80 + "\n")
    
    # Per-file breakdown
    files_sorted = sorted(results['files'].items(), key=lambda x: x[1]['coverage'])
    
    for filepath, data in files_sorted:
        coverage = data['coverage']
        status = "✓" if coverage == 100 else "✗"
        
        print(f"{status} {filepath}")
        print(f"   Coverage: {coverage:.1f}% ({len(data['present'])}/{len(data['present']) + len(data['missing'])} items)")
        
        if data['missing']:
            print(f"   Missing docstrings:")
            for item_type, name, line in data['missing']:
                print(f"      Line {line:4d}: {item_type:8s} {name}")
        print()
    
    print("="*80)


if __name__ == '__main__':
    src_dir = Path('/home/fenix/projects/proteum/kyk-calc/src')
    results = audit_directory(src_dir)
    print_report(results)
