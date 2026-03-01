import threading
import time
from typing import List, Set

class InputHandler:
    def __init__(self):
        self.actions: Set[str] = set()
        self.running = False
        self.thread = None
        self.use_keyboard = True
        
        # Try keyboard library first
        try:
            import keyboard
            self.keyboard = keyboard
        except (ImportError, PermissionError):
            self.use_keyboard = False
            try:
                from blessed import Terminal
                self.term = Terminal()
            except ImportError:
                raise ImportError("Neither keyboard nor blessed library available")
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        self.actions.clear()
        
        if self.use_keyboard:
            self._setup_keyboard_hooks()
        else:
            self.thread = threading.Thread(target=self._blessed_loop, daemon=True)
            self.thread.start()
    
    def stop(self):
        self.running = False
        
        if self.use_keyboard:
            try:
                self.keyboard.unhook_all()
            except:
                pass
        
        if self.thread:
            self.thread.join(timeout=0.1)
    
    def get_actions(self) -> List[str]:
        return list(self.actions)
    
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
            
            self.keyboard.on_press_key('esc', lambda _: self._on_key_press('quit'))
            self.keyboard.on_press_key('q', lambda _: self._on_key_press('quit'))
        except PermissionError:
            self.use_keyboard = False
            from blessed import Terminal
            self.term = Terminal()
            self.thread = threading.Thread(target=self._blessed_loop, daemon=True)
            self.thread.start()
    
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
            'KEY_ESCAPE': 'quit', 'q': 'quit'
        }
        
        action = key_map.get(key)
        if action:
            if action == 'quit':
                self._on_key_press('quit')
            else:
                # Simulate press/release for blessed
                self._on_key_press(action)
                time.sleep(0.05)
                self._on_key_release(action)
    
    def _on_key_press(self, action: str):
        if action == 'thrust':
            self.actions.add('thrust_on')
            self.actions.discard('thrust_off')
        else:
            self.actions.add(action)
    
    def _on_key_release(self, action: str):
        if action == 'thrust':
            self.actions.add('thrust_off')
            self.actions.discard('thrust_on')
        else:
            self.actions.discard(action)