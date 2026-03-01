import threading
import time
from typing import List, Set

class InputHandler:
    def __init__(self):
        self.actions: Set[str] = set()
        self.running = False
        self.thread = None
        self.use_keyboard = False  # Default to blessed on macOS
        
        # Always use blessed - keyboard library doesn't work on macOS without sudo
        from blessed import Terminal
        self.term = Terminal()
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        self.actions.clear()
        
        # Start blessed input thread
        self.thread = threading.Thread(target=self._blessed_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=0.1)
    
    def get_actions(self) -> List[str]:
        actions = list(self.actions)
        # Clear pulse actions after reading
        self.actions.discard('rotate_left')
        self.actions.discard('rotate_right')
        self.actions.discard('thrust')
        return actions
    
    def _setup_keyboard_hooks(self):
        try:
            self.keyboard.on_press_key('up', lambda _: self._on_key_press('thrust'))
            self.keyboard.on_press_key('w', lambda _: self._on_key_press('thrust'))
            self.keyboard.on_release_key('up', lambda _: self._on_key_release('thrust'))
            self.keyboard.on_release_key('w', lambda _: self._on_key_release('thrust'))
            
            self.keyboard.on_press_key('left', lambda _: self._on_key_press('rotate_left'))
            self.keyboard.on_press_key('a', lambda _: self._on_key_press('rotate_left'))
            self.keyboard.on_release_key('left', lambda _: self._on_key_release('rotate_left'))
            self.keyboard.on_release_key('a', lambda _: self._on_key_release('rotate_left'))
            
            self.keyboard.on_press_key('right', lambda _: self._on_key_press('rotate_right'))
            self.keyboard.on_press_key('d', lambda _: self._on_key_press('rotate_right'))
            self.keyboard.on_release_key('right', lambda _: self._on_key_release('rotate_right'))
            self.keyboard.on_release_key('d', lambda _: self._on_key_release('rotate_right'))
            
            self.keyboard.on_press_key('space', lambda _: self._on_key_press(' '))
            self.keyboard.on_press_key('esc', lambda _: self._on_key_press('quit'))
            self.keyboard.on_press_key('q', lambda _: self._on_key_press('quit'))
        except (PermissionError, OSError, ValueError) as e:
            # Fallback to blessed mode
            self.use_keyboard = False
            if not hasattr(self, 'term'):
                from blessed import Terminal
                self.term = Terminal()
    
    def _blessed_loop(self):
        with self.term.cbreak(), self.term.hidden_cursor():
            while self.running:
                key = self.term.inkey(timeout=0.1)
                if key:
                    self._handle_blessed_key(str(key))
    
    def _handle_blessed_key(self, key):
        key_map = {
            'KEY_UP': 'thrust', 'w': 'thrust',
            'KEY_LEFT': 'rotate_left', 'a': 'rotate_left', 
            'KEY_RIGHT': 'rotate_right', 'd': 'rotate_right',
            ' ': ' ',  # Space key
            'KEY_ESCAPE': 'quit', 'q': 'quit'
        }
        
        action = key_map.get(key)
        if action:
            # For rotation and thrust, add single pulse command
            if action in ['rotate_left', 'rotate_right', 'thrust']:
                self.actions.add(action)
            else:
                self.actions.add(action)
    
    def _on_key_press(self, action: str):
        if action == 'thrust':
            self.actions.add('thrust_on')
            self.actions.discard('thrust_off')
        elif action == ' ':
            # Toggle space key state for replay pause
            if ' ' in self.actions:
                self.actions.discard(' ')
            else:
                self.actions.add(' ')
        else:
            self.actions.add(action)
    
    def _on_key_release(self, action: str):
        if action == 'thrust':
            self.actions.add('thrust_off')
            self.actions.discard('thrust_on')
        else:
            self.actions.discard(action)