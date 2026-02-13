#!/bin/bash
# Quick test script for bots

echo "Lunar Lander Bot Test Suite"
echo "============================"
echo ""

# Check if server is running
if ! lsof -i :8000 | grep -q LISTEN; then
    echo "❌ Server not running on port 8000"
    echo "Start with: cd server && uvicorn main:app --port 8000"
    exit 1
fi

echo "✓ Server running"
echo ""

# Test simple bot
echo "Testing Simple Bot (3 runs)..."
for i in {1..3}; do
    echo "  Run $i:"
    python3 bots/simple_bot.py simple 2>&1 | grep -E "(LANDED|CRASHED)" | head -1
done
echo ""

# Check if Ollama is available
if command -v ollama &> /dev/null && curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "✓ Ollama available"
    
    # Check for qwen2.5:7b
    if ollama list | grep -q "qwen2.5:7b"; then
        echo "✓ qwen2.5:7b installed"
        echo ""
        echo "Testing Ollama Bot (1 run - slower)..."
        timeout 60 python3 bots/ollama_bot.py --difficulty simple --rate 5 2>&1 | grep -E "(LANDED|CRASHED|Frame)" | tail -5
    else
        echo "⚠ qwen2.5:7b not installed"
        echo "Install with: ollama pull qwen2.5:7b"
    fi
else
    echo "⚠ Ollama not available"
    echo "Install from: https://ollama.com"
fi

echo ""
echo "Test complete!"
