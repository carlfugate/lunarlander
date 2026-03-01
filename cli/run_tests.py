#!/usr/bin/env python3
"""Test runner script for CLI client."""

import subprocess
import sys
import os

def run_tests():
    """Run all tests with appropriate options."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Unit tests
    print("Running unit tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", "-v", "-m", "unit or not integration",
        "--cov=.", "--cov-report=term-missing"
    ])
    
    if result.returncode != 0:
        print("Unit tests failed!")
        return result.returncode
    
    # Integration tests
    print("\nRunning integration tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/", "-v", "-m", "integration",
        "--cov=.", "--cov-report=term-missing", "--cov-append"
    ])
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_tests())