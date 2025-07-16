#!/usr/bin/env python3
"""
Code quality checker for TMCloud project
Runs ruff, black, isort, and pytest to ensure code quality
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    print("TMCloud Code Quality Checker")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("Error: requirements.txt not found. Please run from project root.")
        sys.exit(1)
    
    results = {}
    
    # Run ruff linter
    results['ruff'] = run_command("python3 -m ruff check .", "Ruff Linter")
    
    # Run black formatter check
    results['black'] = run_command("python3 -m black --check --diff .", "Black Formatter Check")
    
    # Run isort import sorting check
    results['isort'] = run_command("python3 -m isort --check-only --diff .", "Import Sorting Check")
    
    # Run pytest
    results['pytest'] = run_command("python3 -m pytest -v", "Pytest Test Suite")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    all_passed = True
    for tool, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{tool.upper()}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All code quality checks passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some code quality checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()