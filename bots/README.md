# Lunar Lander Bots

Test bots for the Lunar Lander game demonstrating different AI approaches.

## Prerequisites

```bash
# Install Python dependencies
pip install websockets requests

# For LLM bot: Install Ollama
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh
# Windows: Download from https://ollama.com
```

## Simple Rule-Based Bot

Fast, deterministic bot using basic physics heuristics.

**Features**:
- 60 Hz update rate
- <1ms decision time
- Rule-based logic:
  1. Keep upright (angle < 5°)
  2. Navigate to landing zone
  3. Control descent speed

**Usage**:
```bash
# Easy difficulty
python3 bots/simple_bot.py simple

# Medium difficulty
python3 bots/simple_bot.py medium

# Hard difficulty
python3 bots/simple_bot.py hard
```

**Performance**: Usually lands successfully on easy/medium, ~50% on hard

## Ollama LLM Bot

Language model-powered bot using local LLMs via Ollama.

**Recommended Models**:
- **qwen2.5:7b** - Best balance of speed and intelligence (recommended)
- **llama3.2:3b** - Faster, good for 10Hz
- **phi3:mini** - Very fast, good for 10Hz
- **llama3.1:8b** - Slower but smarter

**Setup**:
```bash
# Start Ollama service
ollama serve

# Pull a model (in another terminal)
ollama pull qwen2.5:7b

# Or try a smaller/faster model
ollama pull llama3.2:3b
```

**Usage**:
```bash
# Default: qwen2.5:7b at 5 Hz
python3 bots/ollama_bot.py

# Specify model and difficulty
python3 bots/ollama_bot.py --model llama3.2:3b --difficulty medium

# Faster update rate (10 Hz) for small models
python3 bots/ollama_bot.py --model phi3:mini --rate 10

# Slower rate (2 Hz) for large models
python3 bots/ollama_bot.py --model llama3.1:8b --rate 2
```

**How it works**:
1. Receives telemetry every 100-500ms (depending on rate)
2. Creates concise prompt with current state and scoring info
3. Queries Ollama for decision (JSON array of actions)
4. Sends actions to game server
5. Repeats until landed or crashed

**Performance**: Varies by model, typically 20-60% success rate

## Model Comparison

| Model | Size | Speed | Update Rate | Success Rate | Notes |
|-------|------|-------|-------------|--------------|-------|
| qwen2.5:7b | 4.7GB | ~200ms | 5 Hz | ~50% | Best overall |
| llama3.2:3b | 2.0GB | ~150ms | 5-10 Hz | ~40% | Fast, decent |
| phi3:mini | 2.3GB | ~100ms | 10 Hz | ~30% | Very fast |
| llama3.1:8b | 4.7GB | ~300ms | 2-5 Hz | ~60% | Slower, smarter |

*Tested on M1 Mac. Your performance may vary.*

## Troubleshooting

**"Connection refused"**:
- Make sure the game server is running: `cd server && uvicorn main:app --port 8000`

**"Ollama error"**:
- Check Ollama is running: `ollama serve`
- Verify model is installed: `ollama list`
- Pull model if needed: `ollama pull qwen2.5:7b`

**Bot crashes immediately**:
- Check server logs: `tail -f /tmp/lunarlander.log`
- Try easier difficulty: `--difficulty simple`

**LLM too slow**:
- Use smaller model: `--model llama3.2:3b`
- Reduce update rate: `--rate 2`

## Creating Your Own Bot

See the example bots for reference. Key points:

1. **Connect** to `ws://localhost:8000/ws`
2. **Start game** with telemetry mode and update rate:
   ```python
   {
       "type": "start",
       "difficulty": "simple",
       "telemetry_mode": "advanced",  # Get AI optimization data
       "update_rate": 5  # Hz (2-60)
   }
   ```
3. **Receive telemetry** with comprehensive state
4. **Send actions**: `thrust_on`, `thrust_off`, `rotate_left`, `rotate_right`, `rotate_stop`
5. **Handle game_over** message

See `TELEMETRY.md` for full telemetry documentation.

## Tips for Better Performance

**Rule-based bots**:
- Use `time_to_ground` to predict impact
- Use `estimated_score` to optimize fuel usage
- Check `is_safe_speed` and `is_safe_angle` before landing

**LLM bots**:
- Keep prompts concise (faster inference)
- Use lower temperature (0.1-0.3) for consistency
- Request JSON-only responses
- Handle timeouts gracefully
- Consider fine-tuning on game data
