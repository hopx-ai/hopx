#!/usr/bin/env python3
"""
Map source code changes to test paths.

This script analyzes changed files and determines which tests should be run
based on the source code that was modified. It handles multiple files,
multiple commits, and provides intelligent test path selection.

Used by GitHub Actions workflows for intelligent test selection.
"""

import sys
from pathlib import Path
from typing import List, Set

# Mapping of source files to test paths
SOURCE_TO_TESTS = {
    # Main classes
    "hopx_ai/sandbox.py": [
        "tests/integration/sandbox/",
        "tests/e2e/sandbox/",
    ],
    "hopx_ai/async_sandbox.py": [
        "tests/integration/async_sandbox/",
        "tests/e2e/async_sandbox/",
    ],
    "hopx_ai/desktop.py": [
        "tests/integration/desktop/",
    ],
    # Template directory (matches any file in template/)
    "hopx_ai/template/": [
        "tests/integration/template/",
    ],
    # Resource classes (affect both sync and async)
    "hopx_ai/files.py": [
        "tests/integration/sandbox/resources/files/",
        "tests/integration/async_sandbox/resources/files/",
    ],
    "hopx_ai/commands.py": [
        "tests/integration/sandbox/resources/commands/",
        "tests/integration/async_sandbox/resources/commands/",
    ],
    "hopx_ai/env_vars.py": [
        "tests/integration/sandbox/resources/env_vars/",
        "tests/integration/async_sandbox/resources/env_vars/",
    ],
    "hopx_ai/cache.py": [
        "tests/integration/sandbox/resources/cache/",
        "tests/integration/async_sandbox/resources/cache/",
    ],
    "hopx_ai/terminal.py": [
        "tests/integration/terminal/",
    ],
    # Core infrastructure (run all tests for safety)
    "hopx_ai/_client.py": ["tests/integration/", "tests/e2e/"],
    "hopx_ai/_async_client.py": ["tests/integration/", "tests/e2e/"],
    "hopx_ai/errors.py": ["tests/integration/", "tests/e2e/"],
    "hopx_ai/models.py": ["tests/integration/", "tests/e2e/"],
}

# Patterns for inference when exact match not found
PATTERN_TO_TESTS = {
    "sandbox": ["tests/integration/sandbox/"],
    "async.*sandbox": ["tests/integration/async_sandbox/"],
    "desktop": ["tests/integration/desktop/"],
    "template": ["tests/integration/template/"],
    "terminal": ["tests/integration/terminal/"],
}


def get_tests_for_file(file_path: str) -> List[str]:
    """Get test paths for a given source file."""
    # Remove python/ prefix if present
    if file_path.startswith("python/"):
        file_path = file_path[7:]
    
    # Direct mapping
    if file_path in SOURCE_TO_TESTS:
        return SOURCE_TO_TESTS[file_path]
    
    # Directory-based matching (e.g., template/)
    for source_pattern, test_paths in SOURCE_TO_TESTS.items():
        if file_path.startswith(source_pattern):
            return test_paths
    
    # Pattern-based inference
    file_lower = file_path.lower()
    for pattern, test_paths in PATTERN_TO_TESTS.items():
        import re
        if re.search(pattern, file_lower):
            return test_paths
    
    # Test file changes - run that specific test
    if file_path.startswith("tests/"):
        return [file_path]
    
    # Conftest or shared test utilities - run all tests
    if "conftest.py" in file_path:
        return ["tests/integration/", "tests/e2e/"]
    
    # Default: return empty (will trigger fallback)
    return []


def map_changed_files_to_tests(changed_files: List[str], verbose: bool = False) -> Set[str]:
    """Map multiple changed files to test paths, deduplicating results."""
    test_paths: Set[str] = set()
    
    for file_path in changed_files:
        if not file_path or not file_path.strip():
            continue
        
        file_tests = get_tests_for_file(file_path)
        test_paths.update(file_tests)
        
        if verbose:
            print(f"  {file_path} → {file_tests}", file=sys.stderr)
    
    return test_paths


def main():
    """Main entry point for GitHub Actions."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Map source code changes to test paths")
    parser.add_argument(
        "changed_files",
        nargs="?",
        help="File containing list of changed files (one per line), or read from stdin",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output showing file-to-test mappings",
    )
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Don't fallback to all tests if no mapping found",
    )
    
    args = parser.parse_args()
    
    # Read changed files
    if args.changed_files:
        with open(args.changed_files, 'r') as f:
            changed_files = [line.strip() for line in f if line.strip()]
    else:
        changed_files = [line.strip() for line in sys.stdin if line.strip()]
    
    if not changed_files:
        print("No changed files provided", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"Analyzing {len(changed_files)} changed file(s):", file=sys.stderr)
    
    # Map to test paths
    test_paths = map_changed_files_to_tests(changed_files, verbose=args.verbose)
    
    # Convert to space-separated string
    test_paths_str = " ".join(sorted(test_paths))
    
    # Fallback: if no tests found, run all
    if not test_paths_str and not args.no_fallback:
        test_paths_str = "tests/integration/ tests/e2e/"
        print("No specific mapping found, running all tests", file=sys.stderr)
    elif not test_paths_str:
        print("No test paths found and fallback disabled", file=sys.stderr)
        sys.exit(1)
    
    # Output for GitHub Actions (both formats for compatibility)
    print(f"test_paths={test_paths_str}")
    if "GITHUB_OUTPUT" in sys.environ:
        with open(sys.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"test_paths={test_paths_str}\n")
    
    if args.verbose:
        print(f"\nTest paths to run: {test_paths_str}", file=sys.stderr)


if __name__ == "__main__":
    main()

