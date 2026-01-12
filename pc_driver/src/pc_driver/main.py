from pc_driver.Receiver import Receiver
from pc_driver.Gesture import Gesture



print("Starting receiver...")
receiver = Receiver()

dataFile = "right.json"
gesture = Gesture.RIGHT
receiver.capture_training_data(dataFile, gesture)
