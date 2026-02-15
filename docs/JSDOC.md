# JSDoc Type Checking

We use JSDoc comments for type checking without TypeScript.

## Benefits

- ✅ Type safety in VS Code
- ✅ Better autocomplete
- ✅ Catch bugs early
- ✅ No build changes
- ✅ Still JavaScript

## How It Works

VS Code reads JSDoc comments and `jsconfig.json` to provide type checking.

## Type Definitions

### Game State Types

```javascript
/**
 * @typedef {Object} Lander
 * @property {number} x - X position
 * @property {number} y - Y position
 * @property {number} vx - X velocity
 * @property {number} vy - Y velocity
 * @property {number} rotation - Rotation in degrees
 * @property {number} fuel - Remaining fuel
 */

/**
 * @typedef {Object} GameState
 * @property {Array<{x: number, y: number}>|null} terrain
 * @property {Lander|null} lander
 * @property {boolean} thrusting
 * @property {number} altitude
 * @property {number} speed
 */
```

### Function Documentation

```javascript
/**
 * Start a new game with specified difficulty
 * @param {string} [difficulty='simple'] - Difficulty level
 * @returns {Promise<void>}
 */
async function startGame(difficulty = 'simple') {
    // VS Code knows difficulty is a string!
}
```

### Variable Types

```javascript
/** @type {GameState} */
let gameState = { terrain: null, lander: null };

/** @type {WebSocketClient|null} */
let wsClient = null;
```

## Adding JSDoc to New Code

### Functions

```javascript
/**
 * Brief description
 * @param {Type} paramName - Description
 * @returns {ReturnType} Description
 */
function myFunction(paramName) {
    // ...
}
```

### Classes

```javascript
/**
 * Class description
 */
export class MyClass {
    /**
     * Constructor description
     * @param {string} url - Parameter description
     */
    constructor(url) {
        this.url = url;
    }
    
    /**
     * Method description
     * @param {Object} data - Data object
     * @returns {void}
     */
    handleData(data) {
        // ...
    }
}
```

### Type Definitions

```javascript
/**
 * @typedef {Object} MyType
 * @property {string} name - Property description
 * @property {number} value - Property description
 */
```

## VS Code Integration

With `jsconfig.json` in place, VS Code will:
- Show type errors as you type
- Provide autocomplete based on types
- Show parameter hints
- Catch type mismatches

## Checking Types

VS Code checks types automatically. You can also run:

```bash
# Check all files (if you have TypeScript installed)
npx tsc --noEmit
```

## Migration Path

This is a stepping stone to TypeScript:
1. Add JSDoc comments (done)
2. Get comfortable with types
3. Optionally migrate to TypeScript later
4. Just rename `.js` → `.ts` and remove JSDoc

## Resources

- [JSDoc Reference](https://jsdoc.app/)
- [TypeScript JSDoc Support](https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html)
- [VS Code JSDoc](https://code.visualstudio.com/docs/languages/javascript#_jsdoc-support)
