#!/usr/bin/env python3
"""
Headless browser test for Lunar Lander
Captures console logs and errors for debugging
"""
import asyncio
from playwright.async_api import async_playwright
import sys

async def test_game(url="http://localhost", action="play"):
    """
    Test the game and capture console logs
    
    Args:
        url: Base URL of the game
        action: 'play' for single-player, 'multiplayer' for multiplayer lobby
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

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "play"
    url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost"
    
    exit_code = asyncio.run(test_game(url, action))
    sys.exit(exit_code)
