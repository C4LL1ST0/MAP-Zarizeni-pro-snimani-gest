import keyboard
from .Gesture import Gesture

def press_key(gesture: Gesture):
    if gesture == Gesture.LEFT:
        keyboard.press('left')
    elif gesture == Gesture.RIGHT:
        keyboard.press('right')

