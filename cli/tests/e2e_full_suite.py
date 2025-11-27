#!/usr/bin/env python3
"""
Comprehensive E2E Test Suite for Hopx CLI

Tests ALL commands and arguments to ensure perfect implementation.
Run with: python tests/e2e_full_suite.py
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class TestResult:
    """Result of a single test."""

    name: str
    command: str
    passed: bool
    exit_code: int
    expected_exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    duration: float = 0.0
    error_msg: Optional[str] = None
    group: str = ""


@dataclass
class TestSuite:
    """Collection of test results."""

    name: str
    results: list[TestResult] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    sandbox_id: Optional[str] = None

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


class CLITester:
    """CLI test runner with subprocess execution."""

    def __init__(self):
        self.suite = TestSuite(name="Hopx CLI E2E Full Suite")
        self.sandbox_id: Optional[str] = None
        self.venv_python = str(Path(__file__).parent.parent / ".venv" / "bin" / "python")

    def run_cmd(self, args: list[str], timeout: int = 120) -> tuple[str, str, int]:
        """Run a CLI command and return stdout, stderr, exit_code."""
        cmd = [self.venv_python, "-m", "hopx_cli", *args]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, "NO_COLOR": "1"},
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", 124
        except Exception as e:
            return "", str(e), 1

    def test(
        self,
        name: str,
        args: list[str],
        group: str,
        expected_exit_code: int = 0,
        expect_output: Optional[str] = None,
        expect_json: bool = False,
        timeout: int = 120,
    ) -> TestResult:
        """Run a test and record the result."""
        start = time.time()
        stdout, stderr, exit_code = self.run_cmd(args, timeout)
        duration = time.time() - start

        passed = exit_code == expected_exit_code
        error_msg = None

        # Check for expected output
        if passed and expect_output and expect_output not in stdout:
            passed = False
            error_msg = f"Expected '{expect_output}' in output"

        # Validate JSON if expected
        if passed and expect_json and stdout.strip():
            try:
                json.loads(stdout)
            except json.JSONDecodeError as e:
                passed = False
                error_msg = f"Invalid JSON: {e}"

        result = TestResult(
            name=name,
            command=" ".join(["hopx", *args]),
            passed=passed,
            exit_code=exit_code,
            expected_exit_code=expected_exit_code,
            stdout=stdout[:500] if stdout else "",
            stderr=stderr[:500] if stderr else "",
            duration=duration,
            error_msg=error_msg,
            group=group,
        )

        self.suite.results.append(result)

        # Print progress
        status = "✓" if passed else "✗"
        print(f"  {status} {name} ({duration:.2f}s)")
        if not passed:
            print(f"    Exit: {exit_code} (expected {expected_exit_code})")
            if error_msg:
                print(f"    Error: {error_msg}")
            if stderr:
                print(f"    stderr: {stderr[:200]}")

        return result

    def extract_sandbox_id(self, stdout: str) -> Optional[str]:
        """Extract sandbox ID from create command output."""
        # Try JSON first
        try:
            data = json.loads(stdout)
            if isinstance(data, dict):
                return data.get("sandbox_id") or data.get("id")
        except:
            pass

        # Try plain text
        for line in stdout.split("\n"):
            line = line.strip()
            # Look for lines that look like sandbox IDs (alphanumeric, ~20 chars)
            if len(line) >= 16 and len(line) <= 30 and line.replace("_", "").isalnum():
                return line
            # Also check for "ID: xxx" format
            if "id:" in line.lower():
                parts = line.split(":")
                if len(parts) >= 2:
                    potential_id = parts[-1].strip()
                    if len(potential_id) >= 16:
                        return potential_id

        return None

    def run_group1_no_sandbox(self):
        """Group 1: Commands that don't require a sandbox."""
        print("\n" + "=" * 60)
        print("[Group 1: No Sandbox Required]")
        print("=" * 60)

        # Basic CLI tests
        self.test("hopx --version", ["--version"], "Group 1", expect_output="hopx")
        self.test("hopx --help", ["--help"], "Group 1", expect_output="Hopx CLI")

        # System health
        self.test("hopx system health", ["system", "health"], "Group 1")

        # Template commands
        self.test("hopx template list", ["template", "list"], "Group 1")
        self.test(
            "hopx template list --output json",
            ["template", "list", "--output", "json"],
            "Group 1",
            expect_json=True,
        )
        self.test("hopx tpl list (alias)", ["tpl", "list"], "Group 1")
        self.test("hopx template info python", ["template", "info", "python"], "Group 1")

        # Sandbox list
        self.test("hopx sandbox list", ["sandbox", "list"], "Group 1")
        self.test(
            "hopx sandbox list --output json",
            ["sandbox", "list", "--output", "json"],
            "Group 1",
            expect_json=True,
        )
        self.test("hopx sb list (alias)", ["sb", "list"], "Group 1")
        self.test("hopx sandbox list --limit 5", ["sandbox", "list", "--limit", "5"], "Group 1")

        # Org/Profile/Usage (may require auth)
        self.test("hopx org info", ["org", "info"], "Group 1")
        self.test("hopx profile show", ["profile", "show"], "Group 1")
        self.test("hopx profile whoami", ["profile", "whoami"], "Group 1")
        self.test("hopx usage summary", ["usage", "summary"], "Group 1")
        self.test("hopx usage sandboxes", ["usage", "sandboxes"], "Group 1")

    def run_group2_sandbox_lifecycle(self):
        """Group 2: Sandbox lifecycle commands."""
        print("\n" + "=" * 60)
        print("[Group 2: Sandbox Lifecycle]")
        print("=" * 60)

        # Create sandbox
        result = self.test(
            "hopx sandbox create --template python",
            ["sandbox", "create", "--template", "python", "--output", "json"],
            "Group 2",
            timeout=60,
        )

        if result.passed:
            self.sandbox_id = self.extract_sandbox_id(result.stdout)
            if self.sandbox_id:
                print(f"    Created sandbox: {self.sandbox_id}")
                self.suite.sandbox_id = self.sandbox_id
            else:
                print("    WARNING: Could not extract sandbox ID")
                # Try to get it from sandbox list
                stdout, _, _ = self.run_cmd(["sandbox", "list", "--output", "json", "--limit", "1"])
                try:
                    data = json.loads(stdout)
                    if data and isinstance(data, list) and len(data) > 0:
                        self.sandbox_id = data[0].get("sandbox_id") or data[0].get("id")
                        self.suite.sandbox_id = self.sandbox_id
                        print(f"    Found sandbox from list: {self.sandbox_id}")
                except:
                    pass

        if not self.sandbox_id:
            print("    FATAL: No sandbox ID available, skipping sandbox tests")
            return

        # Sandbox info/status commands
        self.test("hopx sandbox info", ["sandbox", "info", self.sandbox_id], "Group 2")
        self.test(
            "hopx sandbox info --output json",
            ["sandbox", "info", self.sandbox_id, "--output", "json"],
            "Group 2",
            expect_json=True,
        )
        self.test("hopx sandbox health", ["sandbox", "health", self.sandbox_id], "Group 2")
        self.test("hopx sandbox expiry", ["sandbox", "expiry", self.sandbox_id], "Group 2")
        self.test("hopx sandbox url", ["sandbox", "url", self.sandbox_id], "Group 2")
        self.test("hopx sandbox url 8080", ["sandbox", "url", self.sandbox_id, "8080"], "Group 2")
        self.test("hopx sandbox token", ["sandbox", "token", self.sandbox_id], "Group 2")
        self.test(
            "hopx sandbox timeout 3600", ["sandbox", "timeout", self.sandbox_id, "3600"], "Group 2"
        )
        self.test("hopx sb connect (alias)", ["sb", "connect", self.sandbox_id], "Group 2")

    def run_group3_code_execution(self):
        """Group 3: Code execution commands."""
        print("\n" + "=" * 60)
        print("[Group 3: Code Execution]")
        print("=" * 60)

        if not self.sandbox_id:
            print("    SKIPPED: No sandbox available")
            return

        # Run with existing sandbox
        self.test(
            "hopx run with sandbox",
            ["run", "--sandbox", self.sandbox_id, "print('hello from test')"],
            "Group 3",
            expect_output="hello from test",
        )

        self.test(
            "hopx run python",
            ["run", "--sandbox", self.sandbox_id, "--language", "python", "print(1+1)"],
            "Group 3",
            expect_output="2",
        )

        self.test(
            "hopx run bash",
            ["run", "--sandbox", self.sandbox_id, "--language", "bash", "echo 'bash test'"],
            "Group 3",
            expect_output="bash test",
        )

        self.test(
            "hopx run with env",
            [
                "run",
                "--sandbox",
                self.sandbox_id,
                "--env",
                "TEST_VAR=hello123",
                "import os; print(os.environ.get('TEST_VAR', 'NOT_SET'))",
            ],
            "Group 3",
            expect_output="hello123",
        )

        self.test(
            "hopx run with timeout",
            ["run", "--sandbox", self.sandbox_id, "--timeout", "30", "print('quick')"],
            "Group 3",
            expect_output="quick",
        )

        # Run ps
        self.test("hopx run ps", ["run", "ps", "--sandbox", self.sandbox_id], "Group 3")

    def run_group4_files(self):
        """Group 4: File operations."""
        print("\n" + "=" * 60)
        print("[Group 4: File Operations]")
        print("=" * 60)

        if not self.sandbox_id:
            print("    SKIPPED: No sandbox available")
            return

        test_content = "Hello from E2E test!"
        test_path = "/workspace/e2e_test.txt"

        # List files
        self.test("hopx files list", ["files", "list", self.sandbox_id, "/workspace"], "Group 4")

        # Write file
        self.test(
            "hopx files write",
            ["files", "write", self.sandbox_id, test_path, "-d", test_content],
            "Group 4",
        )

        # Read file
        self.test(
            "hopx files read",
            ["files", "read", self.sandbox_id, test_path],
            "Group 4",
            expect_output=test_content,
        )

        # File info
        self.test("hopx files info", ["files", "info", self.sandbox_id, test_path], "Group 4")

        # File alias
        self.test("hopx f list (alias)", ["f", "list", self.sandbox_id, "/workspace"], "Group 4")

        # Upload/download with temp files
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Upload test content")
            local_upload = f.name

        local_download = tempfile.mktemp(suffix=".txt")

        try:
            self.test(
                "hopx files upload",
                ["files", "upload", self.sandbox_id, local_upload, "/workspace/uploaded.txt"],
                "Group 4",
            )

            self.test(
                "hopx files download",
                ["files", "download", self.sandbox_id, test_path, local_download],
                "Group 4",
            )

            # Verify download
            if os.path.exists(local_download):
                with open(local_download) as f:
                    if test_content in f.read():
                        print("    ✓ Download content verified")
        finally:
            if os.path.exists(local_upload):
                os.unlink(local_upload)
            if os.path.exists(local_download):
                os.unlink(local_download)

        # Delete file
        self.test(
            "hopx files delete",
            ["files", "delete", self.sandbox_id, test_path, "--force"],
            "Group 4",
        )

    def run_group5_commands(self):
        """Group 5: Shell commands."""
        print("\n" + "=" * 60)
        print("[Group 5: Shell Commands]")
        print("=" * 60)

        if not self.sandbox_id:
            print("    SKIPPED: No sandbox available")
            return

        self.test("hopx cmd run ls", ["cmd", "run", self.sandbox_id, "ls -la"], "Group 5")

        self.test(
            "hopx cmd run with workdir",
            ["cmd", "run", self.sandbox_id, "pwd", "--workdir", "/tmp"],
            "Group 5",
            expect_output="/tmp",
        )

        self.test(
            "hopx cmd run with env",
            ["cmd", "run", self.sandbox_id, "echo $MY_VAR", "--env", "MY_VAR=test_value"],
            "Group 5",
            expect_output="test_value",
        )

        self.test(
            "hopx cmd run with timeout",
            ["cmd", "run", self.sandbox_id, "echo quick", "--timeout", "30"],
            "Group 5",
            expect_output="quick",
        )

        self.test("hopx cmd exec", ["cmd", "exec", self.sandbox_id, "whoami"], "Group 5")

    def run_group6_env(self):
        """Group 6: Environment variables."""
        print("\n" + "=" * 60)
        print("[Group 6: Environment Variables]")
        print("=" * 60)

        if not self.sandbox_id:
            print("    SKIPPED: No sandbox available")
            return

        # List env vars
        self.test("hopx env list", ["env", "list", self.sandbox_id], "Group 6")

        # Set env var
        self.test(
            "hopx env set",
            ["env", "set", self.sandbox_id, "--env", "E2E_TEST_VAR=e2e_value"],
            "Group 6",
        )

        # Get env var
        self.test(
            "hopx env get",
            ["env", "get", self.sandbox_id, "E2E_TEST_VAR"],
            "Group 6",
            expect_output="e2e_value",
        )

        # Delete env var
        self.test("hopx env delete", ["env", "delete", self.sandbox_id, "E2E_TEST_VAR"], "Group 6")

        # Load from file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("LOADED_VAR=from_file\n")
            env_file = f.name

        try:
            self.test(
                "hopx env load", ["env", "load", self.sandbox_id, "--file", env_file], "Group 6"
            )
        finally:
            if os.path.exists(env_file):
                os.unlink(env_file)

    def run_group7_terminal(self):
        """Group 7: Terminal commands."""
        print("\n" + "=" * 60)
        print("[Group 7: Terminal]")
        print("=" * 60)

        if not self.sandbox_id:
            print("    SKIPPED: No sandbox available")
            return

        self.test("hopx terminal info", ["terminal", "info", self.sandbox_id], "Group 7")

        self.test("hopx terminal url", ["terminal", "url", self.sandbox_id], "Group 7")

        self.test("hopx term info (alias)", ["term", "info", self.sandbox_id], "Group 7")

        self.test(
            "hopx terminal connect with command",
            ["terminal", "connect", self.sandbox_id, "--command", "echo terminal_test"],
            "Group 7",
            timeout=30,
        )

    def run_group8_system(self):
        """Group 8: System commands with sandbox."""
        print("\n" + "=" * 60)
        print("[Group 8: System (with sandbox)]")
        print("=" * 60)

        if not self.sandbox_id:
            print("    SKIPPED: No sandbox available")
            return

        self.test("hopx system metrics", ["system", "metrics", self.sandbox_id], "Group 8")

        self.test("hopx system agent-info", ["system", "agent-info", self.sandbox_id], "Group 8")

        self.test("hopx system processes", ["system", "processes", self.sandbox_id], "Group 8")

        self.test("hopx system jupyter", ["system", "jupyter", self.sandbox_id], "Group 8")

        self.test("hopx system snapshot", ["system", "snapshot", self.sandbox_id], "Group 8")

    def run_group9_output_formats(self):
        """Group 9: Output format testing."""
        print("\n" + "=" * 60)
        print("[Group 9: Output Formats]")
        print("=" * 60)

        # Test with sandbox list (works without sandbox)
        self.test(
            "sandbox list --output table", ["sandbox", "list", "--output", "table"], "Group 9"
        )

        self.test(
            "sandbox list --output json",
            ["sandbox", "list", "--output", "json"],
            "Group 9",
            expect_json=True,
        )

        self.test(
            "sandbox list --output plain", ["sandbox", "list", "--output", "plain"], "Group 9"
        )

        self.test("template list --quiet", ["template", "list", "--quiet"], "Group 9")

        self.test("template list --verbose", ["template", "list", "--verbose"], "Group 9")

        self.test("template list --no-color", ["template", "list", "--no-color"], "Group 9")

    def run_group10_pause_resume(self):
        """Test pause/resume cycle."""
        print("\n" + "=" * 60)
        print("[Group 10: Pause/Resume Cycle]")
        print("=" * 60)

        if not self.sandbox_id:
            print("    SKIPPED: No sandbox available")
            return

        self.test("hopx sandbox pause", ["sandbox", "pause", self.sandbox_id], "Group 10")

        # Brief wait for pause to take effect
        time.sleep(2)

        self.test("hopx sandbox resume", ["sandbox", "resume", self.sandbox_id], "Group 10")

        # Wait for resume
        time.sleep(3)

    def run_group11_errors(self):
        """Group 11: Error handling tests."""
        print("\n" + "=" * 60)
        print("[Group 11: Error Handling]")
        print("=" * 60)

        # Invalid sandbox ID - expect exit code 1 or 4 (not found)
        self.test(
            "Invalid sandbox ID",
            ["sandbox", "info", "invalid_sandbox_id_12345"],
            "Group 11",
            expected_exit_code=1,  # May be 1 or 4 depending on implementation
        )

        # Missing required argument
        self.test(
            "Missing required argument",
            ["sandbox", "info"],
            "Group 11",
            expected_exit_code=2,  # Typer returns 2 for missing args
        )

    def run_group12_cleanup(self):
        """Group 12: Cleanup."""
        print("\n" + "=" * 60)
        print("[Group 12: Cleanup]")
        print("=" * 60)

        if not self.sandbox_id:
            print("    SKIPPED: No sandbox to clean up")
            return

        self.test("hopx sandbox kill", ["sandbox", "kill", self.sandbox_id], "Group 12")

    def print_report(self):
        """Print comprehensive test report."""
        print("\n")
        print("═" * 70)
        print("              HOPX CLI E2E TEST REPORT")
        print("═" * 70)
        print()
        print(f"Test Suite: {self.suite.name}")
        print(f"Started: {self.suite.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {self.suite.duration:.2f} seconds")
        if self.suite.sandbox_id:
            print(f"Test Sandbox: {self.suite.sandbox_id}")
        print()
        print("─" * 70)
        print("RESULTS SUMMARY")
        print("─" * 70)
        print(f"Total:    {self.suite.total} tests")
        print(
            f"Passed:   {self.suite.passed} ({100 * self.suite.passed / max(1, self.suite.total):.1f}%)"
        )
        print(
            f"Failed:   {self.suite.failed} ({100 * self.suite.failed / max(1, self.suite.total):.1f}%)"
        )
        print()

        # Group results
        print("─" * 70)
        print("RESULTS BY GROUP")
        print("─" * 70)

        groups = {}
        for r in self.suite.results:
            if r.group not in groups:
                groups[r.group] = {"passed": 0, "failed": 0}
            if r.passed:
                groups[r.group]["passed"] += 1
            else:
                groups[r.group]["failed"] += 1

        for group, stats in sorted(groups.items()):
            total = stats["passed"] + stats["failed"]
            print(f"  {group}: {stats['passed']}/{total} passed")

        # Failed tests
        failed = [r for r in self.suite.results if not r.passed]
        if failed:
            print()
            print("─" * 70)
            print("FAILED TESTS")
            print("─" * 70)
            for r in failed:
                print(f"\n  ✗ {r.name}")
                print(f"    Command: {r.command}")
                print(f"    Exit code: {r.exit_code} (expected {r.expected_exit_code})")
                if r.error_msg:
                    print(f"    Error: {r.error_msg}")
                if r.stderr:
                    print(f"    stderr: {r.stderr[:300]}")

        print()
        print("═" * 70)

        return self.suite.failed == 0

    def run_all(self):
        """Run all test groups."""
        self.suite.start_time = datetime.now()

        try:
            self.run_group1_no_sandbox()
            self.run_group2_sandbox_lifecycle()
            self.run_group3_code_execution()
            self.run_group4_files()
            self.run_group5_commands()
            self.run_group6_env()
            self.run_group7_terminal()
            self.run_group8_system()
            self.run_group9_output_formats()
            self.run_group10_pause_resume()
            self.run_group11_errors()
            self.run_group12_cleanup()
        finally:
            self.suite.end_time = datetime.now()

        success = self.print_report()
        return 0 if success else 1


def main():
    """Main entry point."""
    # Check for API key
    if not os.environ.get("HOPX_API_KEY"):
        print("ERROR: HOPX_API_KEY environment variable not set")
        print("Please set your API key: export HOPX_API_KEY='hopx_live_...'")
        sys.exit(1)

    tester = CLITester()
    sys.exit(tester.run_all())


if __name__ == "__main__":
    main()
