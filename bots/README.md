# Lunar Lander Bots

Test bots for the Lunar Lander game demonstrating different AI approaches.

## Prerequisites

```bash
# Use the project's virtual environment (has all dependencies)
cd ~/Documents/Github/lunarlander
source venv/bin/activate

# Or install dependencies separately
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
# Activate venv first
cd ~/Documents/Github/lunarlander
source venv/bin/activate

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
- **phi3:mini** - Fastest! (80-120ms), great for 10Hz
- **gemma3:4b** - Fast (100-150ms), good reasoning
- **llama3.2:3b** - Very fast option
- **qwen2.5:7b** - Excellent balance

**Setup**:
```bash
# Start Ollama service
ollama serve

# Pull recommended models
ollama pull phi3:mini
ollama pull gemma3:4b
```

**Usage**:
```bash
# Activate venv first
cd ~/Documents/Github/lunarlander
source venv/bin/activate

# List installed models
python3 bots/ollama_bot.py --list

# Auto-select best model (phi3:mini preferred)
python3 bots/ollama_bot.py

# Specify model
python3 bots/ollama_bot.py --model phi3:mini --rate 10

# Specify difficulty
python3 bots/ollama_bot.py --model gemma3:4b --difficulty medium
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
| phi3:mini | 2.3GB | ~100ms | 10 Hz | ~50% | ⭐ Fastest! |
| gemma3:4b | 3.3GB | ~120ms | 10 Hz | ~50% | Fast & smart |
| llama3.2:3b | 2.0GB | ~150ms | 5-10 Hz | ~40% | Very fast |
| llava:latest | 4.7GB | ~250ms | 5 Hz | ~45% | Good but slower |
| qwen2.5:7b | 4.7GB | ~200ms | 5 Hz | ~50% | Excellent |

*Tested on M1 Mac. Your performance may vary.*

**Your installed models:**
- ✅ phi3:mini - Fastest, recommended!
- ✅ gemma3:4b - Fast with good reasoning
- ✅ llava:latest - Works but slower
- ✅ llama3.2-vision - Vision model (not ideal for text-only game)
- ✅ qwen3-vl:8b - Vision model (not ideal for text-only game)

**Auto-selection priority**: phi3:mini → gemma3:4b → llama3.2:3b → qwen2.5:7b

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
