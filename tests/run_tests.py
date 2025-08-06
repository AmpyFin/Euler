#!/usr/bin/env python3
"""
Test runner for the Euler market analysis system.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)


def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests."""
    print("Running unit tests...")

    cmd = [sys.executable, "-m", "pytest", "tests/unit_tests/", "-v" if verbose else "-q", "--tb=short"]

    if coverage:
        cmd.extend(
            [
                "--cov=clients",
                "--cov=adapters",
                "--cov=indicators",
                "--cov=registries",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
            ]
        )

    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode == 0


def run_integration_tests(verbose=False):
    """Run integration tests."""
    print("Running integration tests...")

    cmd = [sys.executable, "-m", "pytest", "tests/integration_tests/", "-v" if verbose else "-q", "--tb=short"]

    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode == 0


def run_all_tests(verbose=False, coverage=False):
    """Run all tests."""
    print("Running all tests...")

    cmd = [sys.executable, "-m", "pytest", "tests/", "-v" if verbose else "-q", "--tb=short"]

    if coverage:
        cmd.extend(
            [
                "--cov=clients",
                "--cov=adapters",
                "--cov=indicators",
                "--cov=registries",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
            ]
        )

    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode == 0


def install_test_dependencies():
    """Install test dependencies."""
    print("Installing test dependencies...")

    test_requirements = ["pytest>=7.0.0", "pytest-cov>=4.0.0", "pytest-mock>=3.10.0", "pytest-html>=3.1.0"]

    for req in test_requirements:
        cmd = [sys.executable, "-m", "pip", "install", req]
        result = subprocess.run(cmd, cwd=project_root)
        if result.returncode != 0:
            print(f"Failed to install {req}")
            return False

    return True


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run Euler market analysis tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", "-c", action="store_true", help="Generate coverage report")
    parser.add_argument("--install-deps", action="store_true", help="Install test dependencies")

    args = parser.parse_args()

    # Install dependencies if requested
    if args.install_deps:
        if not install_test_dependencies():
            sys.exit(1)

    success = True

    try:
        if args.unit:
            success = run_unit_tests(args.verbose, args.coverage)
        elif args.integration:
            success = run_integration_tests(args.verbose)
        else:
            success = run_all_tests(args.verbose, args.coverage)
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
