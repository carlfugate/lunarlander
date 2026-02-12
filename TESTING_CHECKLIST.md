# Manual Testing Checklist

## Setup
- [x] Server running on port 8000
- [x] nginx running on port 80
- [x] Access game at http://localhost

## Test 1: Difficulty Selection UI
1. Open http://localhost
2. Click "Play Game"
3. **Expected**: Difficulty selection screen appears with 3 buttons
4. **Verify**: 
   - Easy button shows "Gentle terrain, more fuel"
   - Medium button shows "Moderate terrain, standard fuel"
   - Hard button shows "Rough terrain, limited fuel"
   - Back button returns to main menu

## Test 2: Easy Difficulty Game
1. Select "Easy" difficulty
2. Play the game (use arrow keys: Up=thrust, Left/Right=rotate)
3. Try to land successfully
4. **Expected**: 
   - Game starts with gentle terrain
   - Score displayed on game over (if landed)
   - Score range: 1,300 - 1,800 points
   - Crashed = 0 points

## Test 3: Medium Difficulty Game
1. Return to menu (ESC)
2. Select "Medium" difficulty
3. Play and land
4. **Expected**:
   - More challenging terrain
   - Score range: 1,950 - 2,700 points (1.5x multiplier)
   - Higher score than Easy for same performance

## Test 4: Hard Difficulty Game
1. Return to menu (ESC)
2. Select "Hard" difficulty
3. Play and land
4. **Expected**:
   - Difficult terrain
   - Score range: 2,600 - 3,600 points (2.0x multiplier)
   - Highest possible scores

## Test 5: Score Display
1. Land successfully on any difficulty
2. **Verify game over screen shows**:
   - "LANDED!" in green
   - Score prominently displayed
   - Time, fuel, and input stats
   - "Press R to restart | ESC for menu"

## Test 6: Crash Scenario
1. Crash the lander (land too fast or wrong angle)
2. **Verify**:
   - "CRASHED!" in red
   - No score displayed (or score = 0)
   - Stats still shown

## Test 7: Spectator Mode
1. Start a game in one browser tab
2. Open http://localhost in another tab
3. Click "Spectate Live Game"
4. Select the active game
5. **Verify**:
   - Can watch the game in real-time
   - Score shown when game ends
   - Spectator count visible in HUD

## Test 8: Score Calculation Verification
Test these scenarios and verify scores:

### Perfect Landing (Easy)
- Land in ~20 seconds with full fuel
- **Expected**: ~1,800 points

### Perfect Landing (Hard)
- Land in ~20 seconds with full fuel
- **Expected**: ~3,600 points

### Slow Landing (Medium)
- Land in ~60 seconds with half fuel
- **Expected**: ~1,600 points

### Crash
- Any crash scenario
- **Expected**: 0 points

## Test 9: Keyboard Navigation
1. Use Tab key to navigate menu
2. Use Enter to select buttons
3. **Verify**: All buttons accessible via keyboard

## Test 10: Restart Flow
1. Complete a game
2. Press 'R' to restart
3. **Verify**: 
   - Returns to difficulty selection
   - Can select same or different difficulty
   - Score resets

## Automated Tests Status
- [x] 11 unit tests for scoring calculation (all passing)
- [x] Integration tests for difficulty selection (all passing)
- [x] Server health check (passing)

## Known Issues to Watch For
- [ ] Score not displaying on game over
- [ ] Difficulty selection not showing
- [ ] Wrong multiplier applied
- [ ] Negative scores
- [ ] Score shown on crash

## Performance Tests
1. Play 5 games in a row
2. **Verify**:
   - No memory leaks
   - Consistent frame rate
   - Scores calculate correctly each time

## Browser Compatibility
Test in:
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari

## Results
Record your findings here:

Easy difficulty score: _______
Medium difficulty score: _______
Hard difficulty score: _______

Issues found:
-
-
-
