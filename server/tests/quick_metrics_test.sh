#!/bin/bash
# Quick test script for metrics

echo "🔄 This will restart the server and run bot tests"
echo "⚠️  Make sure to stop any running server first (Ctrl+C)"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

cd "$(dirname "$0")/.."

# Start server in background
echo "🚀 Starting server..."
uvicorn main:app --port 8000 > /tmp/server.log 2>&1 &
SERVER_PID=$!
echo "   Server PID: $SERVER_PID"

# Wait for server to start
echo "⏳ Waiting for server..."
sleep 3

# Run bot test
echo "🤖 Starting 10 bots for 10 minutes..."
python3 tests/run_bot_test.py 10 10

# Show results
echo ""
echo "📊 Results:"
curl -s http://localhost:8000/api/stats/live | python3 -m json.tool
echo ""
curl -s http://localhost:8000/api/stats/aggregate | python3 -m json.tool

# Cleanup
echo ""
echo "🧹 Stopping server (PID: $SERVER_PID)..."
kill $SERVER_PID

echo "✅ Done!"
