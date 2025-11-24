#!/usr/bin/env python3
"""
Run each test file individually and generate a report.

This script discovers all test files, runs them one by one, and generates
a comprehensive report showing which test files pass or fail.

Usage:
    python run_tests_individually.py [options]

Examples:
    # Run all test files individually
    python run_tests_individually.py

    # Run only integration test files
    python run_tests_individually.py --category integration

    # Run only e2e test files
    python run_tests_individually.py --category e2e

    # Run with verbose output
    python run_tests_individually.py --verbose

    # Stop on first failure
    python run_tests_individually.py --stop-on-failure
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def check_dependencies():
    """Check for required testing dependencies."""
    missing = []
    
    try:
        import pytest
    except ImportError:
        missing.append("pytest")
    
    try:
        import pytest_asyncio
    except ImportError:
        missing.append("pytest-asyncio")
    
    try:
        import pytest_html
    except ImportError:
        missing.append("pytest-html")
    
    return missing


def print_installation_instructions(missing_deps):
    """Print instructions for installing missing dependencies."""
    print("\n" + "="*80)
    print("Missing Dependencies Detected")
    print("="*80)
    print(f"\nThe following dependencies are missing: {', '.join(missing_deps)}\n")
    print("To install all test dependencies, run:")
    print("  pip install -e '.[dev]'")
    print("\nOr install individually:")
    for dep in missing_deps:
        print(f"  pip install {dep}")
    print("="*80 + "\n")


def discover_test_files(category: str = None) -> List[Path]:
    """
    Discover all test files, excluding __init__.py and conftest.py.
    
    Args:
        category: Filter by category ('integration', 'e2e', or None for all)
    
    Returns:
        List of test file paths
    """
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    if not tests_dir.exists():
        return []
    
    test_files = []
    
    if category == "integration":
        search_dir = tests_dir / "integration"
    elif category == "e2e":
        search_dir = tests_dir / "e2e"
    else:
        search_dir = tests_dir
    
    if not search_dir.exists():
        return []
    
    # Find all Python files, excluding __init__.py and conftest.py
    for py_file in search_dir.rglob("*.py"):
        if py_file.name in ("__init__.py", "conftest.py"):
            continue
        test_files.append(py_file)
    
    return sorted(test_files)


def run_test_file(test_file: Path, verbose: bool = False) -> Tuple[bool, Dict]:
    """
    Run a single test file and return the result.
    
    Args:
        test_file: Path to the test file
        verbose: Whether to show verbose output
    
    Returns:
        Tuple of (success: bool, result_dict: dict)
    """
    project_root = Path(__file__).parent
    cmd = ["python", "-m", "pytest", str(test_file.relative_to(project_root))]
    
    if not verbose:
        cmd.append("-q")
    else:
        cmd.append("-v")
    
    # Add minimal output options
    cmd.extend(["--tb=short"])
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per file
        )
        
        duration = time.time() - start_time
        success = result.returncode == 0
        
        # Parse output to get test counts
        output_lines = result.stdout.split('\n') + result.stderr.split('\n')
        passed = 0
        failed = 0
        skipped = 0
        errors = 0
        
        for line in output_lines:
            if "passed" in line.lower() and "failed" not in line.lower():
                # Try to extract number
                match = re.search(r'(\d+)\s+passed', line)
                if match:
                    passed = int(match.group(1))
            if "failed" in line.lower():
                match = re.search(r'(\d+)\s+failed', line)
                if match:
                    failed = int(match.group(1))
            if "skipped" in line.lower():
                match = re.search(r'(\d+)\s+skipped', line)
                if match:
                    skipped = int(match.group(1))
            if "error" in line.lower() and "failed" not in line.lower():
                match = re.search(r'(\d+)\s+error', line)
                if match:
                    errors = int(match.group(1))
        
        return success, {
            "file": str(test_file.relative_to(project_root)),
            "success": success,
            "returncode": result.returncode,
            "duration": round(duration, 2),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return False, {
            "file": str(test_file.relative_to(project_root)),
            "success": False,
            "returncode": -1,
            "duration": round(duration, 2),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 1,
            "stdout": "",
            "stderr": "Test file timed out after 10 minutes",
        }
    except Exception as e:
        duration = time.time() - start_time
        return False, {
            "file": str(test_file.relative_to(project_root)),
            "success": False,
            "returncode": -1,
            "duration": round(duration, 2),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 1,
            "stdout": "",
            "stderr": str(e),
        }


def generate_report(results: List[Dict], output_dir: Path, timestamp: str):
    """Generate reports from test results."""
    # Calculate statistics
    total_files = len(results)
    passed_files = sum(1 for r in results if r["success"])
    failed_files = total_files - passed_files
    
    total_tests = sum(r["passed"] + r["failed"] + r["skipped"] + r["errors"] for r in results)
    total_passed = sum(r["passed"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    total_skipped = sum(r["skipped"] for r in results)
    total_errors = sum(r["errors"] for r in results)
    total_duration = sum(r["duration"] for r in results)
    
    # Generate JSON report
    json_report = {
        "timestamp": timestamp,
        "summary": {
            "total_files": total_files,
            "passed_files": passed_files,
            "failed_files": failed_files,
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_skipped": total_skipped,
            "total_errors": total_errors,
            "total_duration_seconds": round(total_duration, 2),
        },
        "results": results,
    }
    
    json_file = output_dir / f"individual_tests_{timestamp}.json"
    with open(json_file, "w") as f:
        json.dump(json_report, f, indent=2)
    
    # Generate Markdown report
    md_file = output_dir / f"individual_tests_{timestamp}.md"
    with open(md_file, "w") as f:
        f.write(f"# Individual Test Files Report\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
        
        f.write(f"## Summary\n\n")
        f.write(f"- **Total Test Files:** {total_files}\n")
        f.write(f"- **Passed Files:** {passed_files}\n")
        f.write(f"- **Failed Files:** {failed_files}\n")
        f.write(f"- **Success Rate:** {round(passed_files / total_files * 100, 2) if total_files > 0 else 0}%\n\n")
        
        f.write(f"- **Total Tests:** {total_tests}\n")
        f.write(f"- **Passed Tests:** {total_passed}\n")
        f.write(f"- **Failed Tests:** {total_failed}\n")
        f.write(f"- **Skipped Tests:** {total_skipped}\n")
        f.write(f"- **Errors:** {total_errors}\n")
        f.write(f"- **Total Duration:** {round(total_duration, 2)} seconds\n\n")
        
        # Passed files
        passed_results = [r for r in results if r["success"]]
        if passed_results:
            f.write(f"## ✅ Passed Test Files ({len(passed_results)})\n\n")
            f.write("| File | Tests | Passed | Failed | Skipped | Duration (s) |\n")
            f.write("|------|-------|--------|--------|---------|-------------|\n")
            for r in passed_results:
                total = r["passed"] + r["failed"] + r["skipped"] + r["errors"]
                f.write(f"| `{r['file']}` | {total} | {r['passed']} | {r['failed']} | {r['skipped']} | {r['duration']} |\n")
            f.write("\n")
        
        # Failed files
        failed_results = [r for r in results if not r["success"]]
        if failed_results:
            f.write(f"## ❌ Failed Test Files ({len(failed_results)})\n\n")
            f.write("| File | Tests | Passed | Failed | Skipped | Errors | Duration (s) |\n")
            f.write("|------|-------|--------|--------|---------|--------|-------------|\n")
            for r in failed_results:
                total = r["passed"] + r["failed"] + r["skipped"] + r["errors"]
                f.write(f"| `{r['file']}` | {total} | {r['passed']} | {r['failed']} | {r['skipped']} | {r['errors']} | {r['duration']} |\n")
            f.write("\n")
            
            # Detailed error information
            f.write("### Failed Test Details\n\n")
            for r in failed_results:
                f.write(f"#### {r['file']}\n\n")
                f.write(f"- **Return Code:** {r['returncode']}\n")
                f.write(f"- **Duration:** {r['duration']}s\n")
                if r['stderr']:
                    f.write(f"- **Error:**\n```\n{r['stderr'][:500]}\n```\n\n")
                if r['stdout']:
                    # Extract last few lines of output
                    lines = r['stdout'].split('\n')
                    if len(lines) > 10:
                        f.write(f"- **Output (last 10 lines):**\n```\n{chr(10).join(lines[-10:])}\n```\n\n")
                    else:
                        f.write(f"- **Output:**\n```\n{r['stdout']}\n```\n\n")
        
        f.write(f"\n## Report Files\n\n")
        f.write(f"- **JSON Report:** `individual_tests_{timestamp}.json`\n")
        f.write(f"- **Markdown Report:** `individual_tests_{timestamp}.md`\n")
    
    return json_file, md_file


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run each test file individually and generate a report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    
    parser.add_argument(
        "--category",
        choices=["integration", "e2e"],
        help="Run tests from specific category (integration or e2e)",
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )
    
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="Stop on first test file failure",
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print_installation_instructions(missing)
        sys.exit(1)
    
    # Check for required environment variable
    if not os.getenv("HOPX_API_KEY"):
        print("Warning: HOPX_API_KEY environment variable not set. Some tests may be skipped.")
    
    # Discover test files
    test_files = discover_test_files(category=args.category)
    
    if not test_files:
        print(f"No test files found for category: {args.category or 'all'}")
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print(f"Running {len(test_files)} test files individually")
    print(f"{'='*80}\n")
    
    # Run each test file
    results = []
    project_root = Path(__file__).parent
    reports_dir = project_root / "local" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    start_time = time.time()
    
    for i, test_file in enumerate(test_files, 1):
        print(f"[{i}/{len(test_files)}] Running: {test_file.relative_to(project_root)}")
        
        success, result = run_test_file(test_file, verbose=args.verbose)
        results.append(result)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"         {status} - {result['passed']} passed, {result['failed']} failed, {result['skipped']} skipped ({result['duration']}s)")
        
        if not success and args.stop_on_failure:
            print(f"\nStopping on first failure as requested.")
            break
    
    total_duration = time.time() - start_time
    
    # Generate reports
    print(f"\n{'='*80}")
    print("Generating reports...")
    print(f"{'='*80}\n")
    
    json_file, md_file = generate_report(results, reports_dir, timestamp)
    
    # Print summary
    total_files = len(results)
    passed_files = sum(1 for r in results if r["success"])
    failed_files = total_files - passed_files
    
    print(f"{'='*80}")
    print("Test Execution Summary")
    print(f"{'='*80}")
    print(f"Total Test Files: {total_files}")
    print(f"Passed: {passed_files}")
    print(f"Failed: {failed_files}")
    print(f"Success Rate: {round(passed_files / total_files * 100, 2) if total_files > 0 else 0}%")
    print(f"Total Duration: {round(total_duration, 2)} seconds")
    print(f"\nReports generated in: {reports_dir.relative_to(project_root)}")
    print(f"- JSON Report: {json_file.name}")
    print(f"- Markdown Report: {md_file.name}")
    print(f"{'='*80}\n")
    
    # Exit with error code if any tests failed
    sys.exit(1 if failed_files > 0 else 0)


if __name__ == "__main__":
    main()

