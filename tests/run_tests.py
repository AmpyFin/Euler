"""
Test runner script that ensures proper environment setup.
"""
import os
import sys
import glob
from typing import List
import subprocess

def setup_environment():
    """Set up the test environment."""
    # Add project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Set PYTHONPATH environment variable
    os.environ['PYTHONPATH'] = project_root

def find_test_files() -> List[str]:
    """Find all test files in the test directories."""
    test_files = []
    test_dirs = ['e2e_tests', 'integration_tests', 'unit_tests']
    
    for test_dir in test_dirs:
        pattern = os.path.join(os.path.dirname(__file__), test_dir, '*.py')
        test_files.extend([f for f in glob.glob(pattern) if not f.endswith('__init__.py')])
    
    return test_files

def run_test(test_file: str) -> bool:
    """Run a single test file."""
    print(f"\nRunning test: {os.path.basename(test_file)}")
    print("="*80)
    
    result = subprocess.run([sys.executable, test_file], 
                          env=dict(os.environ),
                          capture_output=True,
                          text=True)
    
    # Print output
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
        
    return result.returncode == 0

def main():
    """Main test runner."""
    # Set up environment
    setup_environment()
    
    # Find test files
    test_files = find_test_files()
    if not test_files:
        print("No test files found!")
        return 1
        
    # Run tests
    print(f"Found {len(test_files)} test files")
    
    passed = 0
    failed = 0
    
    for test_file in test_files:
        if run_test(test_file):
            passed += 1
        else:
            failed += 1
            
    # Print summary
    print("\nTest Summary")
    print("="*80)
    print(f"Total tests: {len(test_files)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    return 1 if failed > 0 else 0

if __name__ == "__main__":
    sys.exit(main()) 