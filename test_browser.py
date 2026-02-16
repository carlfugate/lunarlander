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
            
            # Click Create Room
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

async def main():
    """Run all tests and report summary"""
    url = "http://localhost"
    
    tests = [
        ("Single Player", test_single_player),
        ("Multiplayer Lobby", test_multiplayer_lobby),
        ("Room Creation Modal", test_room_creation_modal),
        ("Room in List", test_room_in_list)
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
    else:
        exit_code = asyncio.run(test_game(url, action))
    
    sys.exit(exit_code)