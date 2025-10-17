#!/usr/bin/env python3
"""Check Python files for missing or improperly formatted docstrings."""

import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple


class DocstringChecker(ast.NodeVisitor):
    """Visits AST nodes to check for docstring issues."""

    def __init__(self, filepath: str):
        """Initialize the checker with a filepath.
        
        Args:
            filepath: Path to the Python file being checked.
        """
        self.filepath = filepath
        self.issues: List[Tuple[int, str, str]] = []  # (line_no, node_type, issue)

    def visit_Module(self, node: ast.Module) -> None:
        """Check module-level docstring.
        
        Args:
            node: The module AST node.
        """
        docstring = ast.get_docstring(node)
        if not docstring:
            self.issues.append((1, "Module", "Missing module-level docstring"))
        else:
            self._validate_docstring(docstring, 1, "Module")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Check class docstring.
        
        Args:
            node: The class definition AST node.
        """
        docstring = ast.get_docstring(node)
        if not docstring:
            self.issues.append((node.lineno, f"Class '{node.name}'", "Missing docstring"))
        else:
            self._validate_docstring(docstring, node.lineno, f"Class '{node.name}'")
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Check function/method docstring.
        
        Args:
            node: The function definition AST node.
        """
        # Skip private methods starting with underscore (convention allows no docstring)
        if node.name.startswith('_') and not node.name.startswith('__'):
            self.generic_visit(node)
            return

        docstring = ast.get_docstring(node)
        node_type = "Method" if self._is_method(node) else "Function"
        
        if not docstring:
            self.issues.append((node.lineno, f"{node_type} '{node.name}'", "Missing docstring"))
        else:
            self._validate_docstring(docstring, node.lineno, f"{node_type} '{node.name}'")
        
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Check async function/method docstring.
        
        Args:
            node: The async function definition AST node.
        """
        # Treat same as regular function
        if node.name.startswith('_') and not node.name.startswith('__'):
            self.generic_visit(node)
            return

        docstring = ast.get_docstring(node)
        node_type = "Async Method" if self._is_method(node) else "Async Function"
        
        if not docstring:
            self.issues.append((node.lineno, f"{node_type} '{node.name}'", "Missing docstring"))
        else:
            self._validate_docstring(docstring, node.lineno, f"{node_type} '{node.name}'")
        
        self.generic_visit(node)

    def _is_method(self, node: ast.FunctionDef) -> bool:
        """Check if a function is a method (inside a class).
        
        Args:
            node: The function definition AST node.
            
        Returns:
            True if the function is a method, False otherwise.
        """
        # This is a simplified check; in practice we'd track context
        return any(isinstance(arg, ast.arg) and arg.arg == 'self' 
                   for arg in node.args.args[:1])

    def _validate_docstring(self, docstring: str, lineno: int, node_desc: str) -> None:
        """Validate docstring format and conventions.
        
        Args:
            docstring: The docstring text.
            lineno: Line number where the node is defined.
            node_desc: Description of the node (e.g., "Class 'MyClass'").
        """
        stripped = docstring.strip()
        
        # Check if empty
        if not stripped:
            self.issues.append((lineno, node_desc, "Empty docstring"))
            return
        
        # Check if first character is capitalized
        first_char = stripped[0]
        if first_char.isalpha() and not first_char.isupper():
            self.issues.append(
                (lineno, node_desc, 
                 f"Docstring should start with capital letter (found: '{first_char}')")
            )
        
        # Check if ends with period (for single-line docstrings)
        if '\n' not in stripped and not stripped.endswith('.'):
            self.issues.append(
                (lineno, node_desc, 
                 "Single-line docstring should end with a period")
            )


def check_file(filepath: Path) -> List[Tuple[int, str, str]]:
    """Check a single Python file for docstring issues.
    
    Args:
        filepath: Path to the Python file.
        
    Returns:
        List of issues found (line_no, node_type, issue_description).
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(filepath))
        checker = DocstringChecker(str(filepath))
        checker.visit(tree)
        return checker.issues
    
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error processing {filepath}: {e}", file=sys.stderr)
        return []


def find_python_files(root_dir: Path) -> List[Path]:
    """Find all Python files in the directory tree.
    
    Args:
        root_dir: Root directory to start search.
        
    Returns:
        List of Python file paths.
    """
    python_files = []
    
    for path in root_dir.rglob('*.py'):
        # Skip common directories that shouldn't be checked
        if any(part in path.parts for part in ['.git', '__pycache__', '.venv', 'venv', '.tox', 'build', 'dist', '.eggs']):
            continue
        python_files.append(path)
    
    return sorted(python_files)


def write_report(issues_by_file: dict, output_file: Path) -> None:
    """Write the docstring issues report to a markdown file.
    
    Args:
        issues_by_file: Dictionary mapping file paths to lists of issues.
        output_file: Path to the output markdown file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Docstring Issues\n\n")
        f.write("This file lists Python files with missing or improperly formatted docstrings.\n\n")
        
        if not issues_by_file:
            f.write("✅ No issues found! All docstrings are present and properly formatted.\n")
            return
        
        f.write(f"**Total files with issues:** {len(issues_by_file)}\n\n")
        f.write("---\n\n")
        
        for filepath, issues in sorted(issues_by_file.items()):
            f.write(f"## `{filepath}`\n\n")
            f.write(f"**Issues found:** {len(issues)}\n\n")
            
            for lineno, node_type, issue in issues:
                f.write(f"- **Line {lineno}** - {node_type}: {issue}\n")
            
            f.write("\n")


def main():
    """Main entry point for the docstring checker."""
    # Get the current directory as root
    root_dir = Path.cwd()
    
    print(f"Scanning Python files in: {root_dir}")
    python_files = find_python_files(root_dir)
    print(f"Found {len(python_files)} Python files\n")
    
    issues_by_file = {}
    
    for filepath in python_files:
        issues = check_file(filepath)
        if issues:
            # Store relative path for cleaner output
            rel_path = filepath.relative_to(root_dir)
            issues_by_file[str(rel_path)] = issues
            print(f"✗ {rel_path}: {len(issues)} issue(s)")
        else:
            print(f"✓ {filepath.relative_to(root_dir)}")
    
    # Write report
    output_file = root_dir / "TODO_DOCSTRINGS.md"
    write_report(issues_by_file, output_file)
    
    print(f"\n{'='*60}")
    print(f"Report written to: {output_file}")
    print(f"Files with issues: {len(issues_by_file)}")
    print(f"Total issues: {sum(len(issues) for issues in issues_by_file.values())}")
    
    # Exit with error code if issues found (useful for CI/CD)
    sys.exit(1 if issues_by_file else 0)


if __name__ == "__main__":
    main()