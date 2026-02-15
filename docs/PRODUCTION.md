# Production Improvements

This document tracks production-ready improvements implemented in the codebase.

## 1. Error Tracking (Sentry)

### Setup

```bash
# Install Sentry
npm install --save-dev @sentry/browser
```

### Configuration

Set environment variable in `.env`:
```
VITE_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### Features

- ✅ Automatic error capture
- ✅ Performance monitoring (10% sample rate)
- ✅ Game state context in errors
- ✅ Breadcrumbs for debugging
- ✅ Only enabled in production
- ✅ User context tracking

### Usage

```javascript
import { captureError, addBreadcrumb, setUser } from './error-tracking.js';

// Manual error capture
try {
    // risky operation
} catch (error) {
    captureError(error, { context: 'additional info' });
}

// Add breadcrumb
addBreadcrumb('User clicked play button', 'user-action');

// Set user context
setUser({ id: 'user-123', username: 'player1' });
```

### Benefits

- Know when errors occur in production
- Full stack traces and context
- Performance monitoring
- User impact tracking

## 2. Centralized State Management

### Implementation

Simple state manager with pub/sub pattern:

```javascript
import { stateManager } from './state.js';

// Get state
const state = stateManager.getState();

// Update state
stateManager.setState({ lander: newLanderData });

// Subscribe to changes
const unsubscribe = stateManager.subscribe((newState, oldState) => {
    console.log('State changed:', newState);
});

// Unsubscribe
unsubscribe();

// Reset state
stateManager.reset();
```

### Benefits

- ✅ Single source of truth
- ✅ Predictable state updates
- ✅ Easy debugging (state history)
- ✅ Reactive updates
- ✅ Available globally for error tracking

## 3. CI/CD Pipeline (GitHub Actions)

### Workflow

Runs on every push and pull request:

1. **Lint CSS** - Check for syntax errors
2. **Unit Tests** - Run all unit tests
3. **E2E Tests** - Run Playwright tests
4. **Upload Results** - Save test artifacts

### Configuration

See `.github/workflows/ci.yml`

### Status Badge

Add to README.md:
```markdown
![CI](https://github.com/carlfugate/lunarlander/workflows/CI/badge.svg)
```

### Benefits

- ✅ Catch bugs before merge
- ✅ Automated quality checks
- ✅ Consistent testing environment
- ✅ Test results archived

## 4. Code Splitting (Future)

### Plan

Split code by route/mode:
- Main menu (always loaded)
- Play mode (lazy loaded)
- Spectate mode (lazy loaded)
- Replay mode (lazy loaded)

### Implementation

```javascript
// Lazy load modules
const { startPlayMode } = await import('./modes/play.js');
const { startSpectateMode } = await import('./modes/spectate.js');
```

### Benefits

- Faster initial load
- Smaller bundle size
- Better caching
- Progressive loading

## Environment Variables

Create `.env` file in `client/`:

```bash
# Sentry (optional)
VITE_SENTRY_DSN=https://your-dsn@sentry.io/project-id

# App version (for release tracking)
VITE_APP_VERSION=1.0.0

# Environment
VITE_ENV=production
```

## Testing Locally

```bash
# Run all checks (same as CI)
cd client
npm run lint:css
npm test -- --run
npm run test:e2e

# Or use validate script
npm run validate
```

## Deployment Checklist

- [ ] Set VITE_SENTRY_DSN environment variable
- [ ] Set VITE_APP_VERSION to current version
- [ ] Run `npm run validate` locally
- [ ] Check CI passes on GitHub
- [ ] Deploy to production
- [ ] Monitor Sentry for errors

## Monitoring

### Sentry Dashboard

- Error rate
- Performance metrics
- User impact
- Release tracking

### Dev Tools Panel

- Press ` to toggle
- Real-time FPS, memory, game state
- Available in development

## Future Improvements

1. **Code Splitting** - Implement lazy loading
2. **Performance Budget** - Set bundle size limits
3. **A/B Testing** - Feature flags
4. **Analytics** - User behavior tracking
5. **Automated Deployments** - Deploy on merge to master
