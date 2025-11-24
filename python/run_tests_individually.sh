#!/bin/bash
#
# Test runner shell script wrapper for running test files individually.
#
# This script provides a convenient way to run each test file separately
# and see which ones pass or fail.
#
# Usage:
#   ./run_tests_individually.sh [options]
#
# Examples:
#   ./run_tests_individually.sh                    # Run all test files individually
#   ./run_tests_individually.sh --category integration  # Run integration tests only
#   ./run_tests_individually.sh --verbose          # Run with verbose output
#   ./run_tests_individually.sh --stop-on-failure  # Stop on first failure

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH"
    exit 1
fi

# Run the Python test script with all passed arguments
python3 run_tests_individually.py "$@"

