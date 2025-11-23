from pc_driver.Receiver import Receiver
from pc_driver.Gesture import Gesture

receiver = Receiver()
receiver.start_receiving_train_data("nothing.json", Gesture.NOTHING)
