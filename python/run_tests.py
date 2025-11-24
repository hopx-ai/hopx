#!/usr/bin/env python3
"""
Test runner script for Hopx SDK tests.

This script runs pytest tests and generates comprehensive reports including:
- HTML test reports
- JUnit XML reports
- Coverage reports
- Summary reports

Usage:
    python run_tests.py [options]

Examples:
    # Run all tests
    python run_tests.py

    # Run only integration tests
    python run_tests.py --category integration

    # Run only e2e tests
    python run_tests.py --category e2e

    # Run specific integration folder
    python run_tests.py --integration-folder sandbox
    python run_tests.py --integration-folder async_sandbox
    python run_tests.py --integration-folder desktop

    # Run specific test file
    python run_tests.py --file tests/integration/sandbox/creation/sandbox_creation.py

    # Run with coverage
    python run_tests.py --coverage

    # Run with verbose output
    python run_tests.py --verbose

    # Run specific marker
    python run_tests.py --marker slow
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def check_dependencies(require_coverage=False):
    """
    Check for required testing dependencies and return missing ones.
    
    All testing dependencies (pytest, pytest-asyncio, pytest-html, pytest-cov)
    are part of the dev dependencies and should be installed.
    
    Args:
        require_coverage: Whether coverage reports are required (pytest-cov)
    
    Returns:
        List of missing dependencies
    """
    missing = []
    
    # Required testing dependencies (all part of dev dependencies)
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
    
    if require_coverage:
        try:
            import pytest_cov
        except ImportError:
            missing.append("pytest-cov")
    
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
    print("\nOr install all recommended test dependencies:")
    print("  pip install pytest pytest-asyncio pytest-html pytest-cov")
    print("="*80 + "\n")


def get_integration_folders():
    """Get list of available integration test folders."""
    project_root = Path(__file__).parent
    integration_dir = project_root / "tests" / "integration"
    
    if not integration_dir.exists():
        return []
    
    folders = []
    for item in integration_dir.iterdir():
        if item.is_dir() and not item.name.startswith("_") and item.name != "__pycache__":
            folders.append(item.name)
    
    return sorted(folders)


class TestRunner:
    """Test runner that executes pytest and generates reports."""

    def __init__(self, args):
        self.args = args
        self.project_root = Path(__file__).parent
        self.reports_dir = self.project_root / "local" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = time.time()

    def run_tests(self):
        """Run pytest with configured options."""
        cmd = ["python", "-m", "pytest"]

        # Add test paths
        if self.args.file:
            cmd.append(self.args.file)
        elif self.args.integration_folder:
            # Target specific integration folder
            folder_path = f"tests/integration/{self.args.integration_folder}"
            if not (self.project_root / folder_path).exists():
                available = get_integration_folders()
                print(f"Error: Integration folder '{self.args.integration_folder}' not found.")
                print(f"Available integration folders: {', '.join(available)}")
                sys.exit(1)
            cmd.append(folder_path)
        elif self.args.category:
            if self.args.category == "integration":
                cmd.append("tests/integration")
            elif self.args.category == "e2e":
                cmd.append("tests/e2e")
            elif self.args.category == "all":
                cmd.append("tests")
            else:
                print(f"Unknown category: {self.args.category}")
                sys.exit(1)
        else:
            cmd.append("tests")

        # Add markers
        if self.args.marker:
            cmd.extend(["-m", self.args.marker])

        # Add verbose flag
        if self.args.verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")

        # Add JUnit XML report
        junit_xml = self.reports_dir / f"junit_{self.timestamp}.xml"
        cmd.extend(["--junitxml", str(junit_xml)])

        # Add HTML report (required dependency)
        html_report = self.reports_dir / f"report_{self.timestamp}.html"
        cmd.extend(["--html", str(html_report), "--self-contained-html"])

        # Add coverage if requested (required dependency when --coverage is used)
        if self.args.coverage:
            coverage_html = self.reports_dir / f"coverage_{self.timestamp}.html"
            coverage_xml = self.reports_dir / f"coverage_{self.timestamp}.xml"
            cmd.extend([
                "--cov=hopx_ai",
                "--cov-report=html:" + str(coverage_html),
                "--cov-report=xml:" + str(coverage_xml),
                "--cov-report=term-missing",
            ])

        # Add other pytest options
        if self.args.maxfail:
            cmd.extend(["--maxfail", str(self.args.maxfail)])

        if self.args.tb:
            cmd.extend(["--tb", self.args.tb])

        # Add custom pytest args
        if self.args.pytest_args:
            cmd.extend(self.args.pytest_args)

        # Print command
        print(f"\n{'='*80}")
        print(f"Running tests: {' '.join(cmd)}")
        print(f"{'='*80}\n")

        # Run pytest
        result = subprocess.run(cmd, cwd=self.project_root)

        # Generate summary report
        self.generate_summary_report(junit_xml, html_report if 'html_report' in locals() else None)

        return result.returncode

    def generate_summary_report(self, junit_xml, html_report):
        """Generate a summary report from test results."""
        summary = {
            "timestamp": self.timestamp,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": round(time.time() - self.start_time, 2),
            "junit_xml": str(junit_xml.relative_to(self.project_root)),
        }

        if html_report:
            summary["html_report"] = str(html_report.relative_to(self.project_root))

        # Parse JUnit XML if it exists
        if junit_xml.exists():
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(junit_xml)
                root = tree.getroot()

                # Extract test statistics
                testsuites = root.findall("testsuite")
                total_tests = 0
                total_failures = 0
                total_errors = 0
                total_skipped = 0
                total_time = 0.0

                for testsuite in testsuites:
                    total_tests += int(testsuite.get("tests", 0))
                    total_failures += int(testsuite.get("failures", 0))
                    total_errors += int(testsuite.get("errors", 0))
                    total_skipped += int(testsuite.get("skipped", 0))
                    total_time += float(testsuite.get("time", 0.0))

                summary["statistics"] = {
                    "total_tests": total_tests,
                    "passed": total_tests - total_failures - total_errors - total_skipped,
                    "failed": total_failures,
                    "errors": total_errors,
                    "skipped": total_skipped,
                    "total_time_seconds": round(total_time, 2),
                    "success_rate": round(
                        ((total_tests - total_failures - total_errors - total_skipped) / total_tests * 100)
                        if total_tests > 0 else 0,
                        2
                    ),
                }

                # Extract failed tests
                failed_tests = []
                for testsuite in testsuites:
                    for testcase in testsuite.findall("testcase"):
                        failure = testcase.find("failure")
                        error = testcase.find("error")
                        if failure is not None or error is not None:
                            failed_tests.append({
                                "name": testcase.get("name"),
                                "classname": testcase.get("classname"),
                                "time": testcase.get("time"),
                                "message": (failure or error).get("message", ""),
                                "type": "failure" if failure is not None else "error",
                            })

                summary["failed_tests"] = failed_tests

            except Exception as e:
                summary["parse_error"] = str(e)

        # Write JSON summary
        summary_json = self.reports_dir / f"summary_{self.timestamp}.json"
        with open(summary_json, "w") as f:
            json.dump(summary, f, indent=2)

        # Write Markdown summary
        summary_md = self.reports_dir / f"summary_{self.timestamp}.md"
        with open(summary_md, "w") as f:
            f.write(f"# Test Execution Summary\n\n")
            f.write(f"**Timestamp:** {summary['timestamp']}\n\n")
            f.write(f"**Start Time:** {summary['start_time']}\n\n")
            f.write(f"**End Time:** {summary['end_time']}\n\n")
            f.write(f"**Duration:** {summary['duration_seconds']} seconds\n\n")

            if "statistics" in summary:
                stats = summary["statistics"]
                f.write(f"## Test Statistics\n\n")
                f.write(f"- **Total Tests:** {stats['total_tests']}\n")
                f.write(f"- **Passed:** {stats['passed']}\n")
                f.write(f"- **Failed:** {stats['failed']}\n")
                f.write(f"- **Errors:** {stats['errors']}\n")
                f.write(f"- **Skipped:** {stats['skipped']}\n")
                f.write(f"- **Success Rate:** {stats['success_rate']}%\n")
                f.write(f"- **Total Time:** {stats['total_time_seconds']} seconds\n\n")

            if "failed_tests" in summary and summary["failed_tests"]:
                f.write(f"## Failed Tests\n\n")
                for test in summary["failed_tests"]:
                    f.write(f"### {test['classname']}.{test['name']}\n\n")
                    f.write(f"- **Type:** {test['type']}\n")
                    f.write(f"- **Time:** {test['time']}s\n")
                    f.write(f"- **Message:** {test['message'][:200]}...\n\n")

            f.write(f"## Reports\n\n")
            f.write(f"- **JUnit XML:** `{summary['junit_xml']}`\n")
            if "html_report" in summary:
                f.write(f"- **HTML Report:** `{summary['html_report']}`\n")
            f.write(f"- **JSON Summary:** `summary_{self.timestamp}.json`\n")
            f.write(f"- **Markdown Summary:** `summary_{self.timestamp}.md`\n")

        print(f"\n{'='*80}")
        print(f"Test execution completed!")
        print(f"{'='*80}")
        if "statistics" in summary:
            stats = summary["statistics"]
            print(f"Total Tests: {stats['total_tests']}")
            print(f"Passed: {stats['passed']}")
            print(f"Failed: {stats['failed']}")
            print(f"Errors: {stats['errors']}")
            print(f"Skipped: {stats['skipped']}")
            print(f"Success Rate: {stats['success_rate']}%")
        print(f"\nReports generated in: {self.reports_dir.relative_to(self.project_root)}")
        print(f"- JUnit XML: {junit_xml.name}")
        if html_report:
            print(f"- HTML Report: {html_report.name}")
        print(f"- Summary JSON: summary_{self.timestamp}.json")
        print(f"- Summary Markdown: summary_{self.timestamp}.md")
        print(f"{'='*80}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Hopx SDK tests and generate reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--category",
        choices=["integration", "e2e", "all"],
        help="Run tests from specific category (integration, e2e, or all)",
    )

    integration_folders = get_integration_folders()
    folder_help = f"Run tests from specific integration folder. Available: {', '.join(integration_folders) if integration_folders else 'none'}"
    
    if integration_folders:
        parser.add_argument(
            "--integration-folder",
            "--folder",
            dest="integration_folder",
            choices=integration_folders,
            help=folder_help,
        )
    else:
        parser.add_argument(
            "--integration-folder",
            "--folder",
            dest="integration_folder",
            type=str,
            help=folder_help,
        )

    parser.add_argument(
        "--file",
        type=str,
        help="Run specific test file",
    )

    parser.add_argument(
        "--marker",
        type=str,
        help="Run tests with specific marker (e.g., 'slow', 'integration', 'e2e')",
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    parser.add_argument(
        "--maxfail",
        type=int,
        help="Stop after N failures",
    )

    parser.add_argument(
        "--tb",
        choices=["short", "long", "line", "no"],
        default="short",
        help="Traceback style",
    )

    parser.add_argument(
        "--pytest-args",
        nargs=argparse.REMAINDER,
        help="Additional arguments to pass to pytest",
        metavar="PYTEST_ARGS",
    )

    args = parser.parse_args()

    # Check for required testing dependencies (all part of dev dependencies)
    missing = check_dependencies(require_coverage=args.coverage)
    
    if missing:
        # All testing dependencies are required - fail if any are missing
        print_installation_instructions(missing)
        sys.exit(1)

    # Check for required environment variable
    if not os.getenv("HOPX_API_KEY"):
        print("Warning: HOPX_API_KEY environment variable not set. Some tests may be skipped.")

    runner = TestRunner(args)
    return runner.run_tests()


if __name__ == "__main__":
    sys.exit(main())

