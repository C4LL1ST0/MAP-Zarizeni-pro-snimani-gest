from pc_driver.Receiver import Receiver
from pc_driver.Gesture import Gesture
import time
print("Starting receiver...")
receiver = Receiver()
receiver.receiving = True

dataFile = "right.json"

try:
    while True:
        print("Waiting for new data from ESP...")
        receiver.start_receiving_train_data(dataFile, Gesture.RIGHT)
        print(f"Data saved to {dataFile}. Waiting for next batch...")
        time.sleep(0.1) 
        receiver.receiving = True
except KeyboardInterrupt:
    print("Receiver stopped by user.")

print("done.")