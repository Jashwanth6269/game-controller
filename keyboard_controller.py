"""Short keyboard taps and global Ctrl+Alt+G / Escape controls."""

import threading

import pyautogui
from pynput import keyboard


KEY_MAP = {"LEFT": "left", "RIGHT": "right", "UP": "up", "DOWN": "down"}


class KeyboardController:
    def __init__(self):
        self.enabled = False
        self.stopped = threading.Event()
        self._toggle_requested = threading.Event()
        pyautogui.PAUSE = 0
        self.listener = keyboard.GlobalHotKeys({
            "<ctrl>+<alt>+g": self._on_toggle_hotkey,
            "<esc>": self._on_escape,
        })
        self.listener.start()

    def _on_toggle_hotkey(self):
        self._toggle_requested.set()

    def _on_escape(self):
        self.stopped.set()

    def consume_toggle(self):
        if self._toggle_requested.is_set():
            self._toggle_requested.clear()
            self.enabled = not self.enabled
            return True
        return False

    def press_gesture(self, gesture):
        key = KEY_MAP.get(gesture)
        if self.enabled and not self.stopped.is_set() and key:
            pyautogui.press(key)
            return key
        return None

    def close(self):
        self.enabled = False
        self.stopped.set()
        try:
            pyautogui.keyUp("left")
            pyautogui.keyUp("right")
            pyautogui.keyUp("up")
            pyautogui.keyUp("down")
        finally:
            self.listener.stop()
            self.listener.join(timeout=1.0)

