# Debug Logging

The client includes a debug logging system that can be enabled/disabled without code changes.

## Usage

### Enable Debug Logging

**Option 1: URL Parameter**
```
http://localhost:8080?debug=true
```

**Option 2: Browser Console**
```javascript
logger.enable()
// Reload page
```

### Disable Debug Logging

```javascript
logger.disable()
// Reload page
```

### Dev Tools Panel

Press **`** (backtick key) to toggle the dev tools panel showing:
- FPS and frame time
- WebSocket status
- Mobile detection
- Debug mode status
- Game state (position, velocity, rotation, fuel)

### Performance Monitoring

```javascript
logger.perf.memory()  // Show memory usage
logger.storage()      // Show localStorage contents
```

## What Gets Logged

When debug mode is enabled, you'll see:
- WebSocket messages (send/receive)
- WebSocket init messages
- Mobile device detection details
- Mobile control swap events
- Telemetry data (position, velocity, fuel, etc.)

When debug mode is disabled:
- Only info, warnings, and errors are shown
- Production-ready output

## In Code

```javascript
import { logger } from './logger.js';

logger.debug('Only shown in debug mode', data);
logger.info('Always shown');
logger.warn('Always shown');
logger.error('Always shown');
```

## Why This Approach?

- No code changes needed to enable/disable logging
- No redeployment required
- Debug logs stay in code for future troubleshooting
- Clean production output by default
- Easy to enable when investigating issues
- Real-time dev tools panel for monitoring
