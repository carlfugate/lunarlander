#!/usr/bin/env python3
"""
Terminal client for Lunar Lander
Main orchestration of WebSocket, rendering, and input loops
"""
import asyncio
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from terminal_caps import TerminalCapabilities
from game_state import GameState
from websocket_client import WebSocketClient
from renderer import TerminalRenderer
from input_handler import InputHandler


class TerminalClient:
    def __init__(self, uri="ws://localhost:8000/ws", difficulty="simple", ansi_strict=False):
        self.uri = uri
        self.difficulty = difficulty
        self.console = Console()
        
        # Initialize components
        self.caps = TerminalCapabilities(force_ascii=ansi_strict)
        self.state = GameState()
        self.ws_client = WebSocketClient()
        self.renderer = TerminalRenderer(self.caps)
        self.input_handler = InputHandler()
        self.running = False
        
    async def run(self):
        """Main entry point - orchestrate all async loops"""
        self.show_banner()
        
        try:
            # Connect and start game
            await self.ws_client.connect(self.uri)
            await self.ws_client.start_game(self.difficulty)
            
            self.running = True
            self.input_handler.start()
            
            # Run concurrent loops
            await asyncio.gather(
                self._websocket_loop(),
                self._render_loop(),
                self._input_loop(),
                return_exceptions=True
            )
        except KeyboardInterrupt:
            pass
        finally:
            await self._cleanup()
    
    async def _websocket_loop(self):
        """Receive and process WebSocket messages"""
        while self.running:
            try:
                msg = await self.ws_client.receive_message()
                if not msg:
                    break
                
                msg_type = msg.get("type")
                if msg_type == "init":
                    self.state.update_from_init(msg)
                elif msg_type == "telemetry":
                    self.state.update_from_telemetry(msg)
                elif msg_type == "game_over":
                    self.state.update_from_game_over(msg)
                    self.running = False
            except Exception as e:
                self.console.print(f"[red]WebSocket error: {e}[/red]")
                self.running = False
                break
    
    async def _render_loop(self):
        """Render at 30fps"""
        while self.running:
            try:
                self.renderer.render_frame(self.state)
                await asyncio.sleep(1/30)  # 30fps
            except Exception as e:
                self.console.print(f"[red]Render error: {e}[/red]")
                break
    
    async def _input_loop(self):
        """Send input actions to server"""
        while self.running:
            try:
                actions = self.input_handler.get_actions()
                
                # Check for quit
                if "quit" in actions:
                    self.running = False
                    break
                
                # Send game actions
                for action in actions:
                    if action != "quit":
                        await self.ws_client.send_input(action)
                
                await asyncio.sleep(1/60)  # Check at 60Hz
            except Exception as e:
                self.console.print(f"[red]Input error: {e}[/red]")
                break
    
    async def _cleanup(self):
        """Graceful shutdown"""
        self.running = False
        self.input_handler.stop()
        await self.ws_client.close()
        self.console.clear()
        
        # Show final results
        if self.state.game_over:
            self.show_game_over()
    
    def show_banner(self):
        """Display startup banner"""
        banner = """
    ╔═══════════════════════════════════════╗
    ║   🚀 LUNAR LANDER - Terminal Client   ║
    ╚═══════════════════════════════════════╝
        """
        self.console.print(Panel(banner, style="bold green"))
        self.console.print(f"Terminal: {self.caps.color_support} colors, "
                          f"{'Unicode' if self.caps.unicode_support else 'ASCII'}")
        self.console.print(f"Difficulty: {self.difficulty}\n")
    
    def show_game_over(self):
        """Display game over screen"""
        if self.state.landed:
            self.console.print(Panel("✓ LANDED!", style="bold green"))
        else:
            self.console.print(Panel("✗ CRASHED!", style="bold red"))
        
        self.console.print(f"Score: {self.state.telemetry.get('score', 0)}")
        self.console.print(f"Time: {self.state.telemetry.get('time', 0):.1f}s")
        self.console.print(f"Fuel: {self.state.lander.get('fuel', 0):.0f}")


def show_menu():
    """Interactive menu for mode and difficulty selection"""
    console = Console()
    
    # ASCII art title
    title = """
    ╔═══════════════════════════════════════╗
    ║   🚀 LUNAR LANDER - Terminal Client   ║
    ╚═══════════════════════════════════════╝
    """
    console.print(title, style="bold cyan")
    
    # Show terminal capabilities
    caps = TerminalCapabilities()
    console.print(f"Terminal: {caps.width}x{caps.height}, "
                 f"{caps.color_support} colors, "
                 f"{'Unicode' if caps.unicode_support else 'ASCII'}\n")
    
    # Mode selection
    table = Table(title="Select Mode")
    table.add_column("Option", style="cyan")
    table.add_column("Description")
    table.add_row("1", "Play")
    table.add_row("2", "Spectate")
    table.add_row("3", "Replay")
    console.print(table)
    
    mode = Prompt.ask("Choose mode", choices=["1", "2", "3"], default="1")
    
    if mode == "1":
        # Difficulty selection
        diff_table = Table(title="Select Difficulty")
        diff_table.add_column("Option", style="cyan")
        diff_table.add_column("Difficulty")
        diff_table.add_row("1", "Easy (simple)")
        diff_table.add_row("2", "Medium")
        diff_table.add_row("3", "Hard")
        console.print(diff_table)
        
        diff = Prompt.ask("Choose difficulty", choices=["1", "2", "3"], default="1")
        difficulty_map = {"1": "simple", "2": "medium", "3": "hard"}
        return "play", difficulty_map[diff]
    elif mode == "2":
        return "spectate", None
    else:
        return "replay", None


async def main():
    parser = argparse.ArgumentParser(description="Lunar Lander Terminal Client")
    parser.add_argument("--uri", default="ws://localhost:8000/ws", help="WebSocket URI")
    parser.add_argument("--difficulty", choices=["simple", "medium", "hard"], help="Game difficulty")
    parser.add_argument("--ansi-strict", action="store_true", help="Force ASCII mode for VT100 compatibility")
    parser.add_argument("--no-menu", action="store_true", help="Skip menu and start directly")
    args = parser.parse_args()
    
    # Show menu if not skipped
    if not args.no_menu and not args.difficulty:
        mode, difficulty = show_menu()
        if mode == "play":
            args.difficulty = difficulty
        else:
            Console().print("[yellow]Spectate and Replay modes coming soon![/yellow]")
            return
    
    # Default difficulty
    if not args.difficulty:
        args.difficulty = "simple"
    
    # Run game
    client = TerminalClient(args.uri, args.difficulty, args.ansi_strict)
    await client.run()


if __name__ == "__main__":
    asyncio.run(main())
