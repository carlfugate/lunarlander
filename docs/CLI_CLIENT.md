# CLI Terminal Client

A fully-featured terminal-based client for Lunar Lander with ANSI/VT terminal compatibility.

## Implementation Status

✅ All features implemented and committed  
✅ Ready for testing  
**Branch:** feature/cli-terminal-client  
**Next:** Test and merge

## Features

- ✅ Play single-player games with all three difficulty levels
- ✅ Real-time keyboard controls (↑ thrust, ←→ rotate, ESC quit)
- ✅ Visual rendering with ASCII/Unicode art
- ✅ HUD with fuel, speed, altitude, angle indicators
- ✅ Color-coded safety indicators
- ✅ Thrust flame animation
- ✅ ANSI/VT terminal compatibility with graceful degradation
- ✅ Spectate mode
- ✅ Replay mode

## Installation

```bash
cd cli
pip install -r requirements.txt
```

## Usage

### Interactive Menu

```bash
python terminal_client.py
```

### Direct Play

```bash
# Easy difficulty
python terminal_client.py --difficulty simple --no-menu

# Medium difficulty
python terminal_client.py --difficulty medium --no-menu

# Hard difficulty
python terminal_client.py --difficulty hard --no-menu
```

### ANSI/VT100 Strict Mode

For maximum compatibility with vintage terminals:

```bash
python terminal_client.py --ansi-strict
```

This forces ASCII-only characters and basic colors.

## Controls

- **↑** or **W**: Thrust (main engine)
- **←** or **A**: Rotate left
- **→** or **D**: Rotate right
- **ESC** or **Q**: Quit

## Terminal Compatibility

### Supported Terminals

- ✅ Modern terminals (iTerm2, Terminal.app, Windows Terminal, etc.)
- ✅ xterm, rxvt, urxvt
- ✅ Linux console
- ✅ VT100/VT220 emulators
- ✅ tmux, screen

### Feature Degradation

The client automatically detects terminal capabilities and adapts:

| Feature | Modern | VT100 | Fallback |
|---------|--------|-------|----------|
| Colors | Truecolor/256 | 16 colors | Monochrome |
| Characters | Unicode (▲◄►▼) | ASCII (^<>v) | ASCII |
| Thrust flame | 🔥 | * | * |

### Color Support Detection

- **Truecolor**: 16.7 million colors
- **256 colors**: Extended palette
- **16 colors**: Basic ANSI colors
- **Monochrome**: No colors (text only)

## HUD Indicators

### Fuel
- 🟢 Green: > 300 units (safe)
- 🟡 Yellow: 100-300 units (caution)
- 🔴 Red: < 100 units (danger)

### Speed
- 🟢 Green + ✓: < 5.0 m/s (safe to land)
- 🟡 Yellow: 5-10 m/s (slow down)
- 🔴 Red: > 10 m/s (too fast)

### Angle
- 🟢 Green + ✓: < 17° (safe to land)
- 🟡 Yellow: 17-30° (level out)
- 🔴 Red: > 30° (danger)

## Troubleshooting

### Keyboard Library Permissions

The `keyboard` library may require elevated permissions on some systems:

**Linux/macOS:**
```bash
sudo python terminal_client.py
```

**Alternative:** The client automatically falls back to `blessed` input if `keyboard` is unavailable.

### Terminal Size

Minimum terminal size: 80x24 characters

For best experience: 120x40 or larger

### Flickering

If you experience flickering:
1. Use a modern terminal emulator
2. Enable hardware acceleration in terminal settings
3. Try `--ansi-strict` mode

### Unicode Characters Not Displaying

If you see `?` or boxes instead of arrows:
1. Use `--ansi-strict` flag to force ASCII mode
2. Check your terminal's character encoding (should be UTF-8)
3. Install a font with Unicode support

## Architecture

The CLI client consists of modular components:

- **terminal_client.py**: Main orchestration and async loops
- **game_state.py**: Game state management
- **websocket_client.py**: WebSocket communication
- **renderer.py**: Terminal rendering with rich
- **input_handler.py**: Keyboard input capture
- **terminal_caps.py**: Terminal capability detection

### Async Architecture

Three concurrent loops run simultaneously:

1. **WebSocket Loop** (60Hz): Receives telemetry from server
2. **Render Loop** (30fps): Updates terminal display
3. **Input Loop** (60Hz): Sends keyboard input to server

## Development

### Running from Source

```bash
cd cli
python terminal_client.py
```

### Testing Terminal Compatibility

Test on different terminal types:

```bash
# VT100 emulation
TERM=vt100 python terminal_client.py --ansi-strict

# 16-color mode
TERM=xterm python terminal_client.py

# 256-color mode
TERM=xterm-256color python terminal_client.py
```

## Future Enhancements

**Completed:**
- ✅ Spectate mode implementation
- ✅ Replay mode implementation

**Planned:**
- [ ] Multiplayer support
- [ ] Leaderboard display
- [ ] Sound effects (terminal bell)
- [ ] Particle effects for explosions
- [ ] Configurable key bindings

## Credits

Built with:
- [rich](https://github.com/Textualize/rich) - Terminal UI
- [blessed](https://github.com/jquast/blessed) - Terminal control
- [keyboard](https://github.com/boppreh/keyboard) - Input capture
- [websockets](https://github.com/python-websockets/websockets) - WebSocket client
