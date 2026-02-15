#!/usr/bin/env python3
"""
Create GitHub issue from JUnit XML test results.

This script parses JUnit XML files and creates formatted GitHub issues
for test failures using the existing issue templates.
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def parse_junit_xml(junit_xml_path: str) -> Dict:
    """Parse JUnit XML file and extract test results."""
    try:
        tree = ET.parse(junit_xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing JUnit XML: {e}", file=sys.stderr)
        return {}

    # Handle both JUnit 4 and JUnit 5 formats
    testsuites = root.findall('.//testsuite')
    if not testsuites:
        # Single testsuite
        testsuites = [root] if root.tag == 'testsuite' else []

    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    total_time = 0.0
    failed_tests = []
    error_tests = []
    skipped_tests = []

    for suite in testsuites:
        total_tests += int(suite.get('tests', 0))
        total_failures += int(suite.get('failures', 0))
        total_errors += int(suite.get('errors', 0))
        total_skipped += int(suite.get('skipped', 0))
        total_time += float(suite.get('time', 0.0))

        # Extract test cases
        for testcase in suite.findall('.//testcase'):
            test_name = testcase.get('name', '')
            class_name = testcase.get('classname', '')
            test_time = float(testcase.get('time', 0.0))
            full_name = f"{class_name}::{test_name}" if class_name else test_name

            # Check for failures
            failure = testcase.find('failure')
            if failure is not None:
                failed_tests.append({
                    'name': full_name,
                    'class': class_name,
                    'method': test_name,
                    'time': test_time,
                    'message': failure.get('message', ''),
                    'type': failure.get('type', ''),
                    'text': failure.text or ''
                })

            # Check for errors
            error = testcase.find('error')
            if error is not None:
                error_tests.append({
                    'name': full_name,
                    'class': class_name,
                    'method': test_name,
                    'time': test_time,
                    'message': error.get('message', ''),
                    'type': error.get('type', ''),
                    'text': error.text or ''
                })

            # Check for skipped
            skipped = testcase.find('skipped')
            if skipped is not None:
                skipped_tests.append({
                    'name': full_name,
                    'class': class_name,
                    'method': test_name,
                    'time': test_time,
                    'reason': skipped.get('message', '') or (skipped.text or '')
                })

    total_passed = total_tests - total_failures - total_errors - total_skipped
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    return {
        'total': total_tests,
        'passed': total_passed,
        'failed': total_failures,
        'errors': total_errors,
        'skipped': total_skipped,
        'time': total_time,
        'success_rate': success_rate,
        'failed_tests': failed_tests,
        'error_tests': error_tests,
        'skipped_tests': skipped_tests,
        'name': root.get('name', 'Test Suite')
    }


def generate_issue_body(results: Dict, commit_sha: Optional[str] = None,
                        branch_name: Optional[str] = None,
                        workflow_run_url: Optional[str] = None,
                        report_artifacts: Optional[List[str]] = None) -> str:
    """Generate GitHub issue body from test results."""
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    # Determine overall status
    if results['failed'] > 0 or results['errors'] > 0:
        status = "❌ FAILED"
    elif results['skipped'] > 0:
        status = "⚠️ UNSTABLE"
    else:
        status = "✅ PASSED"

    body = f"""# Test Results Report

- **Date:** {date}
- **Commit:** `{commit_sha or 'N/A'}`
- **Branch:** `{branch_name or 'N/A'}`
- **Environment:** CI (GitHub Actions)
- **Trigger:** Automated test run
- **Test Runner:** pytest

---

## 1. Summary

- **Overall status:** {status}
- **Total tests:** {results['total']}
- **Passed:** {results['passed']} ✅
- **Failed:** {results['failed']} ❌
- **Errors:** {results['errors']} ❌
- **Skipped:** {results['skipped']} ⏭️
- **Duration:** {results['time']:.2f}s
- **Success rate:** {results['success_rate']:.1f}%

"""

    # Add failed tests section
    if results['failed_tests'] or results['error_tests']:
        body += "## 2. Failed Tests\n\n"
        
        all_failures = results['failed_tests'] + results['error_tests']
        
        for idx, test in enumerate(all_failures, 1):
            error_type = test.get('type', 'Unknown')
            error_message = test.get('message', '')
            error_text = test.get('text', '')
            
            # Truncate long error messages
            if len(error_text) > 1000:
                error_text = error_text[:1000] + "\n... (truncated)"
            
            body += f"""### {idx}. `{test['name']}`

- **Class:** `{test['class']}`
- **Method:** `{test['method']}`
- **Duration:** {test['time']:.2f}s
- **Error Type:** `{error_type}`

**Error Message:**
```
{error_message[:500] if error_message else 'No error message'}
```

**Traceback:**
```
{error_text[:2000] if error_text else 'No traceback available'}
```

"""
    
    # Add skipped tests section
    if results['skipped_tests']:
        body += "## 3. Skipped Tests\n\n"
        body += "| Test Name | Reason |\n"
        body += "|-----------|--------|\n"
        for test in results['skipped_tests'][:20]:  # Limit to 20
            reason = test.get('reason', 'Unknown')[:100]
            body += f"| `{test['name']}` | {reason} |\n"
        if len(results['skipped_tests']) > 20:
            body += f"\n*... and {len(results['skipped_tests']) - 20} more skipped tests*\n"
        body += "\n"

    # Add artifacts section
    if workflow_run_url or report_artifacts:
        body += "## 4. Artifacts & References\n\n"
        if workflow_run_url:
            body += f"- **CI Workflow Run:** {workflow_run_url}\n"
        if report_artifacts:
            body += "- **Test Reports:**\n"
            for artifact in report_artifacts:
                body += f"  - {artifact}\n"
        body += "\n"

    # Add recommended actions
    if results['failed'] > 0 or results['errors'] > 0:
        body += """## 5. Recommended Actions

1. Review failed tests above
2. Check CI logs for detailed error messages
3. Verify test environment and dependencies
4. Re-run tests to check for flakiness

"""
    
    body += f"\n---\n\n*Report generated automatically from JUnit XML on {date}*"
    
    return body


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Create GitHub issue from JUnit XML test results'
    )
    parser.add_argument(
        'junit_xml',
        type=str,
        help='Path to JUnit XML file'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path for issue body (default: stdout)'
    )
    parser.add_argument(
        '--commit-sha',
        type=str,
        default=os.getenv('GITHUB_SHA'),
        help='Git commit SHA (default: GITHUB_SHA env var)'
    )
    parser.add_argument(
        '--branch',
        type=str,
        default=os.getenv('GITHUB_REF_NAME'),
        help='Branch name (default: GITHUB_REF_NAME env var)'
    )
    parser.add_argument(
        '--workflow-url',
        type=str,
        default=os.getenv('GITHUB_SERVER_URL') and os.getenv('GITHUB_REPOSITORY') and os.getenv('GITHUB_RUN_ID') and 
                f"{os.getenv('GITHUB_SERVER_URL')}/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}",
        help='Workflow run URL'
    )
    parser.add_argument(
        '--artifacts',
        type=str,
        nargs='*',
        help='List of artifact paths/URLs'
    )
    parser.add_argument(
        '--only-if-failed',
        action='store_true',
        help='Only generate issue body if there are failures'
    )

    args = parser.parse_args()

    # Parse JUnit XML
    if not os.path.exists(args.junit_xml):
        print(f"Error: JUnit XML file not found: {args.junit_xml}", file=sys.stderr)
        sys.exit(1)

    results = parse_junit_xml(args.junit_xml)

    if not results:
        print("Error: Failed to parse JUnit XML", file=sys.stderr)
        sys.exit(1)

    # Check if we should generate (only-if-failed flag)
    if args.only_if_failed and results['failed'] == 0 and results['errors'] == 0:
        print("No test failures detected. Skipping issue creation.", file=sys.stderr)
        sys.exit(0)

    # Generate issue body
    issue_body = generate_issue_body(
        results,
        commit_sha=args.commit_sha,
        branch_name=args.branch,
        workflow_run_url=args.workflow_url,
        report_artifacts=args.artifacts
    )

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(issue_body)
        print(f"Issue body written to: {args.output}")
    else:
        print(issue_body)

    # Exit with error code if there are failures
    if results['failed'] > 0 or results['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

