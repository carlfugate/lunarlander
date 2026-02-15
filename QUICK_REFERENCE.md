# Lunar Lander - Quick Reference

## Production Features Status

| Feature | Status | Action Required |
|---------|--------|-----------------|
| Error Tracking (Sentry) | ✅ Ready | Add DSN to `.env` (optional) |
| State Management | ✅ Complete | None - fully integrated |
| Environment Config | ✅ Complete | None - `.env` created |
| CI/CD Pipeline | ⏳ Ready | Upload to GitHub Actions |
| Documentation | ✅ Complete | None |
| Source Maps | ✅ Complete | None |

## Quick Commands

```bash
# Development
npm run dev              # Start dev server
npm test                 # Run tests (watch mode)
npm test -- --run        # Run tests once
npm run lint:css         # Lint CSS
npm run validate         # Run all checks

# Production
npm run build            # Build for production
npm run preview          # Preview production build

# Testing
npm run test:e2e         # Run E2E tests
```

## File Locations

```
client/
├── js/
│   ├── error-tracking.js    # Sentry integration
│   ├── state.js             # State manager
│   └── main-menu.js         # Main game logic (integrated)
├── .env                     # Local config (gitignored)
└── .env.example             # Config template

docs/
├── PRODUCTION_COMPLETE.md   # Implementation summary
├── PRODUCTION.md            # Production guide
└── PRODUCTION_PLAN.md       # Implementation plan

ci-workflow.yml              # CI/CD workflow (upload to GitHub)
```

## State Manager Usage

```javascript
import { stateManager } from './state.js';

// Update state
stateManager.setState({ lander: newLander, altitude: 100 });

// Subscribe to changes
const unsubscribe = stateManager.subscribe((newState, oldState) => {
    console.log('State changed');
});

// Get state
const state = stateManager.getState();

// Reset state
stateManager.reset();
```

## Enable Sentry (Optional)

1. Sign up: https://sentry.io
2. Create project
3. Edit `client/.env`:
   ```
   VITE_SENTRY_DSN=https://your-key@sentry.io/your-project-id
   ```
4. Build: `npm run build`

## Add CI/CD (5 minutes)

1. Go to: https://github.com/carlfugate/lunarlander
2. Actions → New workflow → set up a workflow yourself
3. Copy content from `ci-workflow.yml`
4. Save as `.github/workflows/ci.yml`
5. Commit to master

## Debug Tools

- Press **`** (backtick) to toggle dev tools panel
- Add `?debug=true` to URL for debug logging
- Source maps enabled for debugging original code

## Tests

All 47 tests passing:
- Logger (2)
- Input (9)
- Mobile Controls (10)
- WebSocket (5)
- Renderer (21)

## Documentation

- `docs/PRODUCTION_COMPLETE.md` - What's done
- `docs/PRODUCTION.md` - How to use features
- `docs/GIT_WORKFLOW.md` - Branching strategy
- `docs/JSDOC.md` - Type annotations

## Next Steps

1. ⏳ Upload CI/CD workflow (5 min)
2. Optional: Configure Sentry (10 min)
3. Optional: Code splitting for faster load

---

**Status:** 95% Complete | **Tests:** 47/47 Passing | **Last Updated:** 2026-02-15
