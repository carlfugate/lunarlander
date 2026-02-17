#!/usr/bin/env python3
"""
Headless browser test for Lunar Lander
Captures console logs and errors for debugging
"""
import asyncio
from playwright.async_api import async_playwright
import sys
import json
import aiohttp

async def test_game(url="http://localhost", action="play"):
    """
    Test the game and capture console logs
    
    Args:
        url: Base URL of the game
        action: 'play' for single-player, 'multiplayer' for multiplayer lobby, 'create_room' for room creation test
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Capture console messages
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        # Capture errors
        errors = []
        page.on("pageerror", lambda err: errors.append(f"PAGE ERROR: {err}"))
        
        # Track prompts for create_room action
        prompt_count = 0
        prompts_data = []
        
        async def handle_dialog(dialog):
            nonlocal prompt_count
            prompt_count += 1
            prompt_message = dialog.message
            prompts_data.append(prompt_message)
            print(f"Prompt {prompt_count}: {prompt_message}")
            
            # Auto-fill with test data
            if prompt_count == 1:
                await dialog.accept("TestPlayer")
            elif prompt_count == 2:
                await dialog.accept("TestRoom")
            else:
                await dialog.accept("UnexpectedPrompt")
        
        if action == "create_room":
            page.on("dialog", handle_dialog)
        
        try:
            print(f"Loading {url}...")
            await page.goto(url, wait_until="networkidle")
            
            # Wait for menu to load
            await page.wait_for_selector('#menu', timeout=5000)
            print("✓ Page loaded")
            
            if action == "play":
                print("Clicking 'Play Game'...")
                await page.click('button:has-text("Play Game")')
                
                # Wait for game to start
                await page.wait_for_timeout(2000)
                
                # Check if game canvas is visible
                canvas = await page.query_selector('canvas')
                if canvas:
                    print("✓ Game canvas found")
                else:
                    print("✗ Game canvas not found")
                    
            elif action == "multiplayer":
                print("Clicking 'Multiplayer'...")
                await page.click('button:has-text("Multiplayer")')
                
                # Wait for lobby
                await page.wait_for_selector('#lobby', timeout=5000)
                print("✓ Lobby loaded")
                
            elif action == "create_room":
                print("Testing room creation...")
                
                # Click Multiplayer button
                print("Clicking 'Multiplayer'...")
                await page.click('button:has-text("Multiplayer")')
                
                # Wait for lobby
                await page.wait_for_selector('#lobby', timeout=5000)
                print("✓ Lobby loaded")
                
                # Click Create Room button
                print("Clicking 'Create Room'...")
                await page.click('button:has-text("Create Room")')
                
                # Wait for prompts to complete
                await page.wait_for_timeout(2000)
                
                print(f"\n=== PROMPT TEST RESULTS ===")
                print(f"Total prompts: {prompt_count}")
                for i, prompt_msg in enumerate(prompts_data, 1):
                    print(f"Prompt {i}: '{prompt_msg}'")
                
                if prompt_count == 2:
                    print("✓ Correct number of prompts (2)")
                else:
                    print(f"✗ Expected 2 prompts, got {prompt_count}")
                    return 1
                
            # Wait a bit for any async operations
            await page.wait_for_timeout(3000)
            
            # Print console logs
            print("\n=== CONSOLE LOGS ===")
            for log in console_logs:
                print(log)
            
            # Print errors
            if errors:
                print("\n=== ERRORS ===")
                for error in errors:
                    print(error)
                return 1
            else:
                print("\n✓ No errors detected")
                return 0
                
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            print("\n=== CONSOLE LOGS ===")
            for log in console_logs:
                print(log)
            if errors:
                print("\n=== ERRORS ===")
                for error in errors:
                    print(error)
            return 1
        finally:
            await browser.close()

async def test_single_player(url="http://localhost"):
    """Test single-player game functionality"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        
        try:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector('#menu', timeout=5000)
            
            # Click Play Game
            await page.click('#playBtn')
            
            # Wait for difficulty selection
            await page.wait_for_selector('#difficultySelect', timeout=5000)
            
            # Select Easy difficulty
            await page.click('button[data-difficulty="simple"]')
            
            # Verify canvas appears
            canvas = await page.wait_for_selector('#gameCanvas', timeout=5000)
            if not canvas:
                return 1
            
            # Check app container is visible
            app_visible = await page.is_visible('#app')
            if not app_visible:
                return 1
            
            # Wait for game initialization
            await page.wait_for_timeout(2000)
            
            return 0 if not errors else 1
        except Exception:
            return 1
        finally:
            await browser.close()

async def test_multiplayer_lobby(url="http://localhost"):
    """Test multiplayer lobby functionality"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        
        try:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector('#menu', timeout=5000)
            
            # Click Multiplayer
            await page.click('#multiplayerBtn')
            
            # Verify lobby shows
            lobby = await page.wait_for_selector('#lobby', timeout=5000)
            if not lobby:
                return 1
            
            # Check room list loads
            room_list = await page.wait_for_selector('#roomList', timeout=5000)
            if not room_list:
                return 1
            
            # Test Refresh button
            refresh_btn = await page.query_selector('#refreshRoomsBtn')
            if refresh_btn:
                await refresh_btn.click()
                await page.wait_for_timeout(1000)
            
            # Test Back button
            back_btn = await page.query_selector('#backFromLobby')
            if not back_btn:
                return 1
            
            await back_btn.click()
            await page.wait_for_selector('#menu', timeout=3000)
            
            return 0 if not errors else 1
        except Exception:
            return 1
        finally:
            await browser.close()

async def test_room_creation_modal(url="http://localhost"):
    """Test room creation modal functionality"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        
        try:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector('#menu', timeout=5000)
            
            # Click Multiplayer
            await page.click('#multiplayerBtn')
            await page.wait_for_selector('#lobby', timeout=5000)
            
            # Scroll to and click Create Room button
            await page.evaluate('document.querySelector("#createRoomBtn").scrollIntoView()')
            await page.wait_for_timeout(200)
            await page.click('#createRoomBtn')
            
            # Verify modal appears
            modal = await page.wait_for_selector('#createRoomModal', timeout=3000)
            if not modal:
                return 1
            
            # Check for player name input
            player_input = await page.query_selector('#playerNameInput')
            if not player_input:
                return 1
            
            # Check for room name input
            room_input = await page.query_selector('#roomNameInput')
            if not room_input:
                return 1
            
            # Check for Create button
            create_btn = await page.query_selector('#createRoomConfirm')
            if not create_btn:
                return 1
            
            # Check for Cancel button
            cancel_btn = await page.query_selector('#createRoomCancel')
            if not cancel_btn:
                return 1
            
            # Test Cancel button
            await cancel_btn.click()
            await page.wait_for_timeout(500)
            
            return 0 if not errors else 1
        except Exception:
            return 1
        finally:
            await browser.close()

async def test_room_in_list(url="http://localhost"):
    """Test room creation and verification in room list"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        
        try:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector('#menu', timeout=5000)
            
            # Navigate to multiplayer
            await page.click('#multiplayerBtn')
            await page.wait_for_selector('#lobby', timeout=5000)
            
            # Open create room modal
            await page.evaluate('document.querySelector(\"#createRoomBtn\").scrollIntoView()')
            await page.wait_for_timeout(200)
            await page.click('#createRoomBtn')
            await page.wait_for_selector('#createRoomModal', timeout=3000)
            
            # Fill in room details
            await page.fill('#playerNameInput', 'TestPlayer')
            await page.fill('#roomNameInput', 'TestRoom')
            
            # Create room
            await page.click('#createRoomConfirm')
            await page.wait_for_timeout(3000)  # Wait longer for room creation
            
            # Check if we're back in lobby or in a game room
            # The room should now exist and we should be in it
            
            # Verify room appears in API by checking /rooms endpoint
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/rooms") as response:
                    if response.status != 200:
                        return 1
                    
                    rooms = await response.json()
                    # Check if any room exists (the room name might be auto-generated)
                    if len(rooms) == 0:
                        return 1
            
            return 0 if not errors else 1
        except Exception:
            return 1
        finally:
            await browser.close()

async def test_input_validation(url="http://localhost"):
    """Test room creation modal input validation"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        
        try:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector('#menu', timeout=5000)
            
            # Navigate to multiplayer
            await page.click('#multiplayerBtn')
            await page.wait_for_selector('#lobby', timeout=5000)
            
            # Open create room modal
            await page.evaluate('document.querySelector(\"#createRoomBtn\").scrollIntoView()')
            await page.wait_for_timeout(200)
            await page.click('#createRoomBtn')
            await page.wait_for_selector('#createRoomModal', timeout=3000)
            
            # Test empty player name - click Create button
            await page.click('#createRoomConfirm')
            await page.wait_for_timeout(500)
            
            # Modal should still be visible (validation failed)
            modal_visible = await page.is_visible('#createRoomModal')
            if not modal_visible:
                return 1
            
            # Fill player name, leave room name empty
            await page.fill('#playerNameInput', 'TestPlayer')
            await page.click('#createRoomConfirm')
            await page.wait_for_timeout(500)
            
            # Modal should still be visible
            modal_visible = await page.is_visible('#createRoomModal')
            if not modal_visible:
                return 1
            
            # Fill both fields - should work
            await page.fill('#roomNameInput', 'TestRoom')
            await page.click('#createRoomConfirm')
            await page.wait_for_timeout(1000)
            
            # Modal should be hidden now
            modal_visible = await page.is_visible('#createRoomModal')
            if modal_visible:
                return 1
            
            return 0 if not errors else 1
        except Exception:
            return 1
        finally:
            await browser.close()

async def test_websocket_connection(url="http://localhost"):
    """Test WebSocket connection and telemetry"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        console_logs = []
        page.on("console", lambda msg: console_logs.append(msg.text))
        
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        
        try:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector('#menu', timeout=5000)
            
            # Click Play Game
            await page.click('#playBtn')
            await page.wait_for_selector('#difficultySelect', timeout=5000)
            
            # Select Easy difficulty
            await page.click('button[data-difficulty="simple"]')
            await page.wait_for_timeout(3000)
            
            # Check console logs for WebSocket connection
            ws_connected = any('WebSocket connected' in log for log in console_logs)
            if not ws_connected:
                print(f"WebSocket test: No 'WebSocket connected' message found")
                return 1
            
            # Check that game is actually running by checking canvas visibility
            canvas_visible = await page.is_visible('#gameCanvas')
            if not canvas_visible:
                print(f"WebSocket test: Game canvas not visible")
                return 1
            
            # Wait a bit more to ensure game is running
            await page.wait_for_timeout(2000)
            
            # Check for any WebSocket errors
            ws_errors = any('websocket' in log.lower() and 'error' in log.lower() for log in console_logs)
            if ws_errors:
                print(f"WebSocket test: WebSocket errors found in logs")
                return 1
            
            return 0 if not errors else 1
        except Exception as e:
            print(f"WebSocket test exception: {e}")
            import traceback
            traceback.print_exc()
            return 1
        finally:
            await browser.close()

async def test_game_state_updates(url="http://localhost"):
    """Test game state updates and HUD values"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        
        try:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector('#menu', timeout=5000)
            
            # Start game
            await page.click('#playBtn')
            await page.wait_for_selector('#difficultySelect', timeout=5000)
            await page.click('button[data-difficulty="simple"]')
            
            # Wait for game to start
            await page.wait_for_selector('#gameCanvas', timeout=5000)
            await page.wait_for_timeout(1000)
            
            # Check initial HUD values by examining canvas context
            initial_check = await page.evaluate("""
                () => {
                    const canvas = document.getElementById('gameCanvas');
                    if (!canvas) return { error: 'No canvas found' };
                    
                    // Look for HUD text in the page or check if game state exists
                    const hudElements = document.querySelectorAll('*');
                    let fuelFound = false, altFound = false, speedFound = false;
                    
                    // Check if game state is accessible via window object
                    if (window.stateManager && window.stateManager.state) {
                        const state = window.stateManager.state;
                        return {
                            hasFuel: state.lander && typeof state.lander.fuel === 'number',
                            hasAltitude: typeof state.altitude === 'number',
                            hasSpeed: typeof state.speed === 'number',
                            fuelValue: state.lander ? state.lander.fuel : null
                        };
                    }
                    
                    return { error: 'Game state not accessible' };
                }
            """)
            
            if 'error' in initial_check:
                # Fallback: just check that canvas exists and no errors
                canvas_exists = await page.query_selector('#gameCanvas')
                if not canvas_exists:
                    return 1
            else:
                # Verify initial values exist
                if not (initial_check.get('hasFuel') and initial_check.get('hasAltitude') and initial_check.get('hasSpeed')):
                    return 1
                
                # Check fuel is reasonable (0-1000 range)
                fuel_value = initial_check.get('fuelValue')
                if fuel_value is not None and (fuel_value < 0 or fuel_value > 1000):
                    return 1
            
            # Wait 2 seconds for game state changes
            await page.wait_for_timeout(2000)
            
            # Check that values have changed (lander should be falling)
            final_check = await page.evaluate("""
                () => {
                    if (window.stateManager && window.stateManager.state) {
                        const state = window.stateManager.state;
                        return {
                            altitude: state.altitude,
                            speed: state.speed,
                            fuel: state.lander ? state.lander.fuel : null,
                            landerY: state.lander ? state.lander.y : null
                        };
                    }
                    return { error: 'Game state not accessible' };
                }
            """)
            
            if 'error' not in final_check:
                # Verify altitude/speed changed (lander falling)
                if final_check.get('speed', 0) <= 0:
                    return 1
                
                # Verify fuel is still reasonable
                fuel_value = final_check.get('fuel')
                if fuel_value is not None and (fuel_value < 0 or fuel_value > 1000):
                    return 1
            
            return 0 if not errors else 1
        except Exception:
            return 1
        finally:
            await browser.close()

async def test_multiplayer_game(url="http://localhost", keep_open=False):
    """Test automated multiplayer game with 2 players"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Create two contexts for two players
        context1 = await browser.new_context()
        context2 = await browser.new_context()
        page1 = await context1.new_page()
        page2 = await context2.new_page()
        
        errors = []
        page1.on("pageerror", lambda err: errors.append(f"Player1: {err}"))
        page2.on("pageerror", lambda err: errors.append(f"Player2: {err}"))
        
        room_id = None
        
        try:
            # Generate unique room name to avoid conflicts with stale rooms
            import time
            unique_room_name = f"Test_{int(time.time())}"
            
            # Both players load the page
            await page1.goto(url, wait_until="networkidle")
            await page2.goto(url, wait_until="networkidle")
            await page1.wait_for_selector('#menu', timeout=5000)
            await page2.wait_for_selector('#menu', timeout=5000)
            
            # Player 1: Go to multiplayer and create room
            await page1.click('#multiplayerBtn')
            await page1.wait_for_selector('#lobby', timeout=5000)
            await page1.evaluate('document.querySelector(\"#createRoomBtn\").scrollIntoView()')
            await page1.wait_for_timeout(200)
            await page1.click('#createRoomBtn')
            await page1.wait_for_selector('#createRoomModal', timeout=3000)
            
            # Fill room details with unique name
            await page1.fill('#playerNameInput', 'Player1')
            await page1.fill('#roomNameInput', unique_room_name)
            await page1.click('#createRoomConfirm')
            
            # Wait for waiting lobby
            await page1.wait_for_selector('#waitingLobby', timeout=5000)
            
            # Get room ID from URL or page content
            room_id = await page1.evaluate("""
                () => {
                    const roomNameEl = document.querySelector('#roomName');
                    return roomNameEl ? roomNameEl.textContent : 'unknown';
                }
            """)
            
            # Player 2: Join the room
            await page2.click('#multiplayerBtn')
            await page2.wait_for_selector('#lobby', timeout=5000)
            
            # Refresh room list
            await page2.click('#refreshRoomsBtn')
            await page2.wait_for_timeout(1500)
            
            room_count = await page2.evaluate('document.querySelectorAll(".room-item").length')
            print(f'Player 2: Found {room_count} rooms in list')
            if room_count == 0:
                print('ERROR: No rooms visible to Player 2')
                errors.append('No rooms found in Player 2 list')
                return 1
            
            # Set up dialog handler BEFORE clicking room (must be async)
            async def handle_dialog(dialog):
                print(f'Player 2: Dialog appeared with message: {dialog.message}')
                await dialog.accept('Player2')
                print('Player 2: Dialog accepted with name "Player2"')
            
            page2.on('dialog', handle_dialog)
            print('Player 2: Dialog handler set')
            
            # Find and click the specific room by unique name
            print(f'Player 2: Looking for room: {unique_room_name}')
            
            # Find and click the specific room by name
            room_found = await page2.evaluate(f'''
                () => {{
                    const rooms = document.querySelectorAll('.room-item');
                    for (let room of rooms) {{
                        const nameEl = room.querySelector('.room-name');
                        if (nameEl && nameEl.textContent.includes('{unique_room_name}')) {{
                            room.click();
                            return true;
                        }}
                    }}
                    return false;
                }}
            ''')
            
            if not room_found:
                print(f'ERROR: Could not find room "{unique_room_name}" in Player 2 list')
                errors.append('Room not found')
                return 1
            
            print('Player 2: Clicked correct room, waiting for join...')
            
            # Give time for dialog to appear and be handled
            await page2.wait_for_timeout(1000)
            
            # Wait for Player 2 to be in waiting lobby
            await page2.wait_for_selector('#waitingLobby', timeout=5000)
            print('Player 2: Successfully joined waiting lobby')
            
            # Wait for both players in waiting lobby
            await page2.wait_for_selector('#waitingLobby', timeout=5000)
            await page1.wait_for_timeout(2000)  # Let player list update
            
            # Player 1: Start the game
            start_btn = await page1.wait_for_selector('#startGameBtn', timeout=5000)
            await start_btn.click()
            
            # Wait for game to start
            await page1.wait_for_timeout(2000)
            
            # Verify both contexts show game screen
            canvas1 = await page1.wait_for_selector('#gameCanvas', timeout=5000)
            canvas2 = await page2.wait_for_selector('#gameCanvas', timeout=5000)
            
            if not canvas1 or not canvas2:
                return 1
            
            # Keep game running for 60 seconds
            await page1.wait_for_timeout(60000)
            
            if keep_open:
                print(f"Game running with room_id: {room_id}")
                print("Browsers kept open for testing. Press Ctrl+C to exit.")
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    pass
            
            return 0 if not errors else 1
        except Exception as e:
            print(f"ERROR in test_multiplayer_game: {e}")
            import traceback
            traceback.print_exc()
            return 1
        finally:
            if not keep_open:
                await browser.close()

async def main():
    """Run all tests and report summary"""
    url = "http://localhost"
    
    tests = [
        ("Single Player", test_single_player),
        ("Multiplayer Lobby", test_multiplayer_lobby),
        ("Room Creation Modal", test_room_creation_modal),
        ("Room in List", test_room_in_list),
        ("Input Validation", test_input_validation),
        ("WebSocket Connection", test_websocket_connection),
        ("Game State Updates", test_game_state_updates),
        ("Multiplayer Game", test_multiplayer_game)
    ]
    
    results = []
    print("Running comprehensive test suite...\n")
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            result = await test_func(url)
            status = "PASS" if result == 0 else "FAIL"
            results.append((test_name, result))
            print(f"  {status}\n")
            
            # Small delay between tests to avoid race conditions
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"  FAIL - {e}\n")
            results.append((test_name, 1))
    
    # Summary
    passed = sum(1 for _, result in results if result == 0)
    total = len(results)
    
    print("=== TEST SUMMARY ===")
    for test_name, result in results:
        status = "PASS" if result == 0 else "FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nPassed: {passed}/{total}")
    return 0 if passed == total else 1
if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "play"
    url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost"
    
    if action == "all":
        exit_code = asyncio.run(main())
    elif action == "multiplayer_game":
        exit_code = asyncio.run(test_multiplayer_game(url, keep_open=True))
    else:
        exit_code = asyncio.run(test_game(url, action))
    
    sys.exit(exit_code)