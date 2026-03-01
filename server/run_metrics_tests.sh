#!/bin/bash
#
# Run all metrics tests
#

set -e

echo "🧪 Metrics & Analytics Test Suite"
echo "=================================="
echo ""

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run: python -m venv venv"
    exit 1
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing..."
    pip install pytest pytest-asyncio pytest-cov
fi

echo "📋 Step 1: Unit Tests"
echo "---------------------"
pytest tests/test_metrics.py tests/test_analytics.py -v
UNIT_RESULT=$?

echo ""
echo "⚡ Step 2: Performance Tests"
echo "---------------------------"
pytest tests/test_performance.py -v -s
PERF_RESULT=$?

echo ""
echo "📊 Step 3: Coverage Report"
echo "-------------------------"
if command -v pytest-cov &> /dev/null; then
    pytest tests/test_metrics.py tests/test_analytics.py --cov=metrics --cov-report=term-missing
    COV_RESULT=$?
else
    echo "⚠️  pytest-cov not installed, skipping coverage"
    echo "   Install with: pip install pytest-cov"
    COV_RESULT=0
fi

echo ""
echo "=================================="
if [ $UNIT_RESULT -eq 0 ] && [ $PERF_RESULT -eq 0 ] && [ $COV_RESULT -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi
