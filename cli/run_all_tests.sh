#!/bin/bash
# Local test runner - run this before committing changes

set -e

echo "🧪 Running CLI Test Suite"
echo "=========================="

# Get script directory and change to cli
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
source ../.venv/bin/activate

# Add current directory to PYTHONPATH
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# 1. Unit tests
echo ""
echo "📋 Step 1: Unit Tests"
echo "---------------------"
pytest tests/ -v --tb=short -x || {
    echo ""
    echo "❌ FAILED: Unit tests failed"
    exit 1
}

# 2. Check coverage
echo ""
echo "📊 Step 2: Coverage Check"
echo "-------------------------"
pytest tests/ --cov=. --cov-report=term-missing --cov-report=html -q
coverage report --fail-under=75 || {
    echo ""
    echo "⚠️  WARNING: Coverage below 75%"
    echo "   View detailed report: htmlcov/index.html"
}

# 3. E2E tests (if server is running)
echo ""
echo "🔗 Step 3: E2E Tests"
echo "--------------------"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    python test_e2e.py || {
        echo ""
        echo "❌ FAILED: E2E tests failed"
        exit 1
    }
else
    echo "⚠️  Server not running on localhost:8000"
    echo "   Start server: cd server && source ../venv/bin/activate && uvicorn main:app --port 8000"
    echo "   Skipping E2E tests..."
fi

# 4. Manual test reminder
echo ""
echo "✅ All automated tests passed!"
echo ""
echo "📝 Manual Testing Checklist:"
echo "   [ ] Run: python terminal_client.py"
echo "   [ ] Verify menu displays"
echo "   [ ] Start a game"
echo "   [ ] Check terrain renders as LINES"
echo "   [ ] Check lander renders and ROTATES"
echo "   [ ] Test controls (arrow keys/WASD)"
echo "   [ ] Verify HUD updates"
echo "   [ ] Test game over"
echo ""
echo "Ready to commit? Run: git add . && git commit"


