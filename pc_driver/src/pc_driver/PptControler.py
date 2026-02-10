import keyboard
from .Gesture import Gesture
from .UiMessages import InfoMessage, GestureMessage

def press_key(gesture: Gesture):
    if gesture == Gesture.LEFT:
        keyboard.press('left')
    elif gesture == Gesture.RIGHT:
        keyboard.press('right')

