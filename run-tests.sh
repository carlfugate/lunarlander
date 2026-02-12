#!/bin/bash

# Test runner script for Lunar Lander

set -e

echo "🧪 Running Lunar Lander Tests"
echo "=============================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Track failures
FAILED=0

# 1. Python Unit Tests
echo ""
echo "📦 Running Python unit tests..."
cd server
source ../venv/bin/activate
if pytest tests/ -v; then
    echo -e "${GREEN}✓ Python tests passed${NC}"
else
    echo -e "${RED}✗ Python tests failed${NC}"
    FAILED=1
fi
cd ..

# 2. JavaScript Unit Tests
echo ""
echo "📦 Running JavaScript unit tests..."
cd client
if npm test -- --run; then
    echo -e "${GREEN}✓ JavaScript tests passed${NC}"
else
    echo -e "${RED}✗ JavaScript tests failed${NC}"
    FAILED=1
fi
cd ..

# 3. E2E Tests (only if servers are running)
echo ""
echo "🌐 Checking if servers are running..."
if curl -s http://localhost:8080 > /dev/null && curl -s http://localhost:8000/health > /dev/null; then
    echo "Servers detected, running E2E tests..."
    cd client
    if npm run test:e2e; then
        echo -e "${GREEN}✓ E2E tests passed${NC}"
    else
        echo -e "${RED}✗ E2E tests failed${NC}"
        FAILED=1
    fi
    cd ..
else
    echo "⚠️  Servers not running, skipping E2E tests"
    echo "   Start servers with: ./start-servers.sh"
fi

# Summary
echo ""
echo "=============================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
