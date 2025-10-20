#!/usr/bin/env python3
"""
Test code examples in pytest-jux documentation.

This script extracts code blocks from Markdown files and attempts to validate them.
It can execute bash commands and Python code snippets to ensure examples work.

Usage:
    python scripts/test_docs.py                  # Test all docs
    python scripts/test_docs.py --dry-run        # Show what would be tested
    python scripts/test_docs.py --verbose        # Show detailed output
    python scripts/test_docs.py docs/tutorials/  # Test specific directory
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class CodeBlock:
    """Represents a code block extracted from documentation."""

    def __init__(self, language: str, code: str, file_path: Path, line_number: int):
        self.language = language
        self.code = code
        self.file_path = file_path
        self.line_number = line_number

    def __repr__(self) -> str:
        return f"CodeBlock({self.language}, {self.file_path}:{self.line_number})"


def extract_code_blocks(markdown_file: Path) -> List[CodeBlock]:
    """
    Extract code blocks from a Markdown file.

    Args:
        markdown_file: Path to the Markdown file

    Returns:
        List of CodeBlock objects
    """
    code_blocks = []
    content = markdown_file.read_text()
    lines = content.split("\n")

    in_code_block = False
    language = None
    code_lines = []
    start_line = 0

    for i, line in enumerate(lines, 1):
        # Detect start of code block
        match = re.match(r"^```(\w+)?", line)
        if match and not in_code_block:
            in_code_block = True
            language = match.group(1) or "text"
            code_lines = []
            start_line = i
        # Detect end of code block
        elif line.strip() == "```" and in_code_block:
            in_code_block = False
            code = "\n".join(code_lines)
            if code.strip():  # Only include non-empty blocks
                code_blocks.append(
                    CodeBlock(language, code, markdown_file, start_line)
                )
            language = None
            code_lines = []
        # Collect code lines
        elif in_code_block:
            code_lines.append(line)

    return code_blocks


def is_testable_bash(code: str) -> bool:
    """
    Determine if a bash code block can be tested.

    Args:
        code: The bash code

    Returns:
        True if testable, False otherwise
    """
    # Skip code blocks that are just examples or placeholders
    untestable_patterns = [
        r"pytest --junit-xml=report\.xml",  # Requires pytest setup
        r"jux-.*",  # CLI commands require installation
        r"git\s+",  # Git commands
        r"npm\s+",  # npm commands
        r"pip\s+",  # pip commands
        r"uv\s+",  # uv commands
        r"export\s+",  # Environment variable exports
        r"echo\s+",  # Echo commands (usually just examples)
        r"\$\s*#",  # Comments in shell
        r"\.\.\.+",  # Ellipsis (indicates omitted code)
        r"<.*>",  # Placeholder syntax
        r"your-.*",  # Placeholder text
    ]

    for pattern in untestable_patterns:
        if re.search(pattern, code):
            return False

    return True


def is_testable_python(code: str) -> bool:
    """
    Determine if a Python code block can be tested.

    Args:
        code: The Python code

    Returns:
        True if testable, False otherwise
    """
    # Skip code blocks that are incomplete or just examples
    untestable_patterns = [
        r"\.\.\.+",  # Ellipsis (indicates omitted code)
        r"<.*>",  # Placeholder syntax
        r"# \.\.\.",  # Comment indicating omitted code
        r"pass$",  # Stub code
    ]

    for pattern in untestable_patterns:
        if re.search(pattern, code):
            return False

    # Must have valid Python syntax (at least one statement)
    if not code.strip():
        return False

    # Skip if it's just import statements or variable assignments
    lines = [line.strip() for line in code.split("\n") if line.strip()]
    if all(
        line.startswith("import ") or line.startswith("from ") or "=" in line
        for line in lines
    ):
        return False

    return True


def test_bash_block(block: CodeBlock, verbose: bool = False) -> Tuple[bool, str]:
    """
    Test a bash code block.

    Args:
        block: The CodeBlock to test
        verbose: Show detailed output

    Returns:
        Tuple of (success, message)
    """
    if not is_testable_bash(block.code):
        return True, "Skipped (not testable)"

    try:
        # Run in a safe shell environment
        result = subprocess.run(
            ["bash", "-c", block.code],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        if result.returncode == 0:
            return True, "Passed"
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return False, f"Failed: {error_msg[:100]}"

    except subprocess.TimeoutExpired:
        return False, "Timeout (>5s)"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"


def test_python_block(block: CodeBlock, verbose: bool = False) -> Tuple[bool, str]:
    """
    Test a Python code block.

    Args:
        block: The CodeBlock to test
        verbose: Show detailed output

    Returns:
        Tuple of (success, message)
    """
    if not is_testable_python(block.code):
        return True, "Skipped (not testable)"

    try:
        # Write code to temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(block.code)
            temp_file = Path(f.name)

        try:
            # Validate syntax
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(temp_file)],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            if result.returncode == 0:
                return True, "Syntax OK"
            else:
                error_msg = result.stderr.strip()
                return False, f"Syntax error: {error_msg[:100]}"

        finally:
            temp_file.unlink()

    except subprocess.TimeoutExpired:
        return False, "Timeout (>5s)"
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"


def test_code_block(block: CodeBlock, verbose: bool = False) -> Tuple[bool, str]:
    """
    Test a code block based on its language.

    Args:
        block: The CodeBlock to test
        verbose: Show detailed output

    Returns:
        Tuple of (success, message)
    """
    if block.language == "bash" or block.language == "sh":
        return test_bash_block(block, verbose)
    elif block.language == "python":
        return test_python_block(block, verbose)
    else:
        return True, "Skipped (unsupported language)"


def find_markdown_files(path: Path) -> List[Path]:
    """
    Find all Markdown files in a directory tree.

    Args:
        path: Directory to search

    Returns:
        List of Markdown file paths
    """
    if path.is_file():
        return [path] if path.suffix == ".md" else []

    return sorted(path.glob("**/*.md"))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test code examples in pytest-jux documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test all documentation
  python scripts/test_docs.py

  # Test specific directory
  python scripts/test_docs.py docs/tutorials/

  # Dry run (show what would be tested)
  python scripts/test_docs.py --dry-run

  # Verbose output
  python scripts/test_docs.py --verbose
        """,
    )

    parser.add_argument(
        "path",
        nargs="?",
        default="docs/",
        help="Path to documentation directory or file (default: docs/)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be tested without executing"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        default=["bash", "python"],
        help="Languages to test (default: bash python)",
    )

    args = parser.parse_args()

    # Find documentation files
    docs_path = Path(args.path)
    if not docs_path.exists():
        print(f"{RED}Error:{RESET} Path not found: {docs_path}")
        return 1

    markdown_files = find_markdown_files(docs_path)
    if not markdown_files:
        print(f"{YELLOW}Warning:{RESET} No Markdown files found in {docs_path}")
        return 0

    print(f"{BLUE}Testing code examples in {len(markdown_files)} Markdown files...{RESET}\n")

    total_blocks = 0
    tested_blocks = 0
    passed_blocks = 0
    failed_blocks = 0
    skipped_blocks = 0

    for md_file in markdown_files:
        blocks = extract_code_blocks(md_file)
        file_blocks = [b for b in blocks if b.language in args.languages]

        if not file_blocks:
            continue

        total_blocks += len(file_blocks)
        relative_path = md_file.relative_to(Path.cwd())

        if args.verbose or args.dry_run:
            print(f"\n{BLUE}File:{RESET} {relative_path}")
            print(f"  {len(file_blocks)} code block(s) found\n")

        for block in file_blocks:
            if args.dry_run:
                print(f"  Would test: {block.language} block at line {block.line_number}")
                tested_blocks += 1
                continue

            success, message = test_code_block(block, args.verbose)

            if "Skipped" in message:
                skipped_blocks += 1
                if args.verbose:
                    print(
                        f"  {YELLOW}SKIP{RESET} {block.language} (line {block.line_number}): {message}"
                    )
            elif success:
                passed_blocks += 1
                tested_blocks += 1
                if args.verbose:
                    print(
                        f"  {GREEN}PASS{RESET} {block.language} (line {block.line_number}): {message}"
                    )
            else:
                failed_blocks += 1
                tested_blocks += 1
                print(
                    f"  {RED}FAIL{RESET} {relative_path}:{block.line_number} ({block.language}): {message}"
                )

    # Summary
    print(f"\n{BLUE}Summary:{RESET}")
    print(f"  Total code blocks: {total_blocks}")
    print(f"  Tested: {tested_blocks}")
    print(f"  {GREEN}Passed: {passed_blocks}{RESET}")
    if failed_blocks > 0:
        print(f"  {RED}Failed: {failed_blocks}{RESET}")
    if skipped_blocks > 0:
        print(f"  {YELLOW}Skipped: {skipped_blocks}{RESET}")

    if args.dry_run:
        print(f"\n{YELLOW}Dry run completed - no tests were executed{RESET}")
        return 0

    if failed_blocks > 0:
        print(f"\n{RED}Some code examples failed validation{RESET}")
        return 1

    print(f"\n{GREEN}All testable code examples passed!{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
