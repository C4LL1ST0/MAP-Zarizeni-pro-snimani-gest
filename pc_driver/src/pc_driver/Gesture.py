from enum import Enum

class Gesture(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

gesture_dict = {
    "left": Gesture.LEFT,
    "right": Gesture.RIGHT,
    "up": Gesture.UP,
    "down": Gesture.DOWN
}
