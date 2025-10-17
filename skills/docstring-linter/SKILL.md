---
name: docstring-linter
description: Automated Python docstring linting and fixing tool. Use this skill when working on Python codebases to ensure all modules, classes, functions, and methods have proper docstrings that follow style conventions (capitalization, punctuation, formatting).
license: Complete terms in LICENSE.txt
---

# Python Docstring Linter

To ensure Python codebases maintain high-quality documentation, use this skill to automatically detect and fix missing or improperly formatted docstrings.

## Overview

This skill provides an automated workflow for:
1. Scanning Python files in a codebase
2. Identifying docstring issues (missing or improperly formatted)
3. Fixing the identified issues
4. Recursively re-running the linter until all issues are resolved

## Available Tools

**Helper Script**:
- `scripts/lint-docstrings.py` - Automated docstring checker that generates a report

**Always run the script first** to understand the current state of docstrings in the codebase before attempting fixes.

## Docstring Standards Enforced

The linter checks for:

1. **Presence**: All public modules, classes, functions, and methods must have docstrings
   - Private methods (starting with single underscore `_`) are exempt
   - Dunder methods (starting/ending with `__`) require docstrings

2. **Capitalization**: Docstrings must start with a capital letter (if starting with alphabetic character)

3. **Punctuation**: Single-line docstrings must end with a period

4. **Non-empty**: Docstrings cannot be empty or contain only whitespace

## Workflow

### Phase 1: Initial Scan

To begin the docstring linting process:

1. **Run the linter script** from the repository root:
   ```bash
   python scripts/lint-docstrings.py
   ```

2. **Review the generated report**: The script creates `TODO_DOCSTRINGS.md` in the current directory, containing:
   - List of files with issues
   - Line numbers and specific problems
   - Total count of issues

3. **Analyze the scope**: Read the report to understand:
   - Which files need attention
   - Types of issues (missing vs. formatting)
   - Overall magnitude of work

### Phase 2: Systematic Fixing

To fix the identified issues systematically:

1. **Process files one at a time** from the report:
   - Read the file to understand context
   - Fix each issue identified for that file
   - Use the Edit tool to make precise changes

2. **Apply appropriate fixes** based on issue type:

   **For missing docstrings:**
   - Analyze the code to understand purpose
   - Write clear, concise docstrings that explain:
     - What the module/class/function does
     - Parameters (with types if not obvious)
     - Return values (with types if not obvious)
     - Any important side effects or exceptions
   - Follow Google or NumPy docstring style conventions

   **For formatting issues:**
   - Capitalize first letter if needed
   - Add terminal period for single-line docstrings
   - Ensure docstring is not empty

3. **Maintain existing style**: When adding docstrings to a codebase:
   - Match the existing docstring format (Google, NumPy, or reStructuredText style)
   - Mirror the level of detail used in existing docstrings
   - Follow any project-specific conventions observed

### Phase 3: Iterative Verification

After making fixes, verify the changes:

1. **Re-run the linter**:
   ```bash
   python scripts/lint-docstrings.py
   ```

2. **Check the updated report**: Compare against previous run:
   - Verify fixed files no longer appear
   - Identify any new issues introduced
   - Confirm total issue count decreased

3. **Continue iteration**: If issues remain:
   - Return to Phase 2 to fix remaining problems
   - Repeat until the linter reports: "✅ No issues found!"

### Phase 4: Completion

To finalize the docstring improvements:

1. **Verify clean report**: Confirm the linter exits with success status (exit code 0)

2. **Clean up**: Remove the `TODO_DOCSTRINGS.md` file if desired:
   ```bash
   rm TODO_DOCSTRINGS.md
   ```

3. **Summary**: Report to the user:
   - Total files processed
   - Total issues fixed
   - Confirmation that all docstrings now meet standards

## Example Docstring Formats

### Module-level Docstring
```python
"""Utilities for processing user authentication and authorization."""
```

### Class Docstring
```python
class UserManager:
    """Manages user accounts and authentication state.

    Handles user creation, authentication, and session management
    for the application.
    """
```

### Function/Method Docstring (Simple)
```python
def calculate_total(items: List[Item]) -> float:
    """Calculate the total price of all items including tax."""
```

### Function/Method Docstring (Detailed)
```python
def process_payment(amount: float, currency: str) -> PaymentResult:
    """Process a payment transaction.

    Args:
        amount: Payment amount in the specified currency.
        currency: ISO 4217 currency code (e.g., "USD", "EUR").

    Returns:
        PaymentResult containing transaction ID and status.

    Raises:
        ValueError: If amount is negative or currency is invalid.
        PaymentError: If payment processing fails.
    """
```

## Script Behavior

The `lint-docstrings.py` script:
- Recursively scans all `.py` files in the current directory
- Skips common directories: `.git`, `__pycache__`, `.venv`, `venv`, `.tox`, `build`, `dist`, `.eggs`
- Generates a markdown report with all issues
- Exits with code 1 if issues found, 0 if all checks pass
- Can be integrated into CI/CD pipelines

## Common Issues and Solutions

**Issue: "Missing module-level docstring"**
- Solution: Add a docstring at the very top of the file (line 1) describing the module's purpose

**Issue: "Docstring should start with capital letter"**
- Solution: Capitalize the first alphabetic character in the docstring

**Issue: "Single-line docstring should end with a period"**
- Solution: Add a period at the end of single-line docstrings

**Issue: "Empty docstring"**
- Solution: Replace empty triple-quotes with meaningful documentation
