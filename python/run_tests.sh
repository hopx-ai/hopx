#!/bin/bash
#
# Test runner shell script wrapper for Hopx SDK tests.
#
# This script provides a convenient way to run tests with common configurations.
#
# Usage:
#   ./run_tests.sh [options]
#
# Examples:
#   ./run_tests.sh                    # Run all tests
#   ./run_tests.sh --category integration  # Run integration tests only
#   ./run_tests.sh --coverage         # Run with coverage
#   ./run_tests.sh --verbose          # Run with verbose output

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
python3 run_tests.py "$@"

