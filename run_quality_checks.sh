#!/bin/bash

# TMCloud Code Quality Check Script
# This script runs all the code quality tools available in the project

echo "🔍 TMCloud Code Quality Checks"
echo "================================"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run from project root."
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run a command and check its result
run_check() {
    local tool=$1
    local command=$2
    local description=$3
    
    echo -e "\n${YELLOW}Running $description...${NC}"
    echo "Command: $command"
    echo "----------------------------------------"
    
    if eval $command; then
        echo -e "${GREEN}✅ $tool: PASSED${NC}"
        return 0
    else
        echo -e "${RED}❌ $tool: FAILED${NC}"
        return 1
    fi
}

# Initialize counters
total_checks=0
passed_checks=0

# Check if tools are available
echo "Checking tool availability..."
for tool in ruff black isort pytest; do
    if python3 -m $tool --version >/dev/null 2>&1; then
        echo "✅ $tool is available"
    else
        echo "❌ $tool is not available"
    fi
done

echo -e "\n🚀 Starting code quality checks..."

# Run ruff linter
total_checks=$((total_checks + 1))
if run_check "Ruff" "python3 -m ruff check ." "Ruff linter"; then
    passed_checks=$((passed_checks + 1))
fi

# Run black formatter check
total_checks=$((total_checks + 1))
if run_check "Black" "python3 -m black --check --diff ." "Black formatter check"; then
    passed_checks=$((passed_checks + 1))
fi

# Run isort import sorting check
total_checks=$((total_checks + 1))
if run_check "isort" "python3 -m isort --check-only --diff ." "Import sorting check"; then
    passed_checks=$((passed_checks + 1))
fi

# Run pytest (if tests exist)
if [ -d "tests" ] || ls test_*.py 1> /dev/null 2>&1; then
    total_checks=$((total_checks + 1))
    if run_check "pytest" "python3 -m pytest -v" "Test suite"; then
        passed_checks=$((passed_checks + 1))
    fi
else
    echo -e "${YELLOW}⚠️  No tests found, skipping pytest${NC}"
fi

# Summary
echo -e "\n📊 Summary"
echo "================================"
echo "Total checks: $total_checks"
echo "Passed: $passed_checks"
echo "Failed: $((total_checks - passed_checks))"

if [ $passed_checks -eq $total_checks ]; then
    echo -e "${GREEN}🎉 All code quality checks passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some checks failed. Please review the output above.${NC}"
    exit 1
fi