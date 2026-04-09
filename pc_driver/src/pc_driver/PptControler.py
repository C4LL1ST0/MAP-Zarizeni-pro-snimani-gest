import keyboard
from .Gesture import Gesture

def press_key(gesture: Gesture):
    if gesture == Gesture.LEFT:
        keyboard.press_and_release('left')
    elif gesture == Gesture.RIGHT:
        keyboard.press_and_release('right')
