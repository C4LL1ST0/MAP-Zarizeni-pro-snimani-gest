import keyboard
from .Gesture import Gesture
from .UiMessages import InfoMessage, GestureMessage

def press_key(self, gesture: Gesture):
    if gesture == Gesture.LEFT:
        self.ui.call_from_thread(
            self.ui.post_message,
            InfoMessage("pressing left key")
            )
        keyboard.press_and_release('left')
    elif gesture == Gesture.RIGHT:
        self.ui.call_from_thread(
            self.ui.post_message,
            InfoMessage("pressing right key")
            )
        keyboard.press_and_release('right')
