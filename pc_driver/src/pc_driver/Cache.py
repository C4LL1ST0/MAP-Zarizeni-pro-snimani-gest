from typing import List
from pc_driver.SensorData import SensorData
from pc_driver.TrainObject import TrainObject
from pc_driver.Gesture import Gesture
from pathlib import Path
import json
from threading import Lock

class Cache:
    def __init__(self) -> None:
        self.data: List[SensorData] = []
        self._lock = Lock()

    def add(self, sensorData: SensorData) -> None:
        with self._lock:
            if(len(self.data) >= 100):
                self.data.pop(0)
            self.data.append(sensorData)

    def getData(self) -> List[SensorData]:
        with self._lock:
            return self.data

    def saveCacheAsTrainDataToFile(self, filename: str, gesture: Gesture) -> None:
        myfile = Path("../data/" + filename)
        if(not myfile.is_file()):
            print("File: " + filename + " does not exist.")
            with open("../data/" + filename, "x") as f:
                f.write("")
                print("File: " + filename + " created.")

        trainFile = open("../data/" + filename, "r")
        trainData: List[TrainObject] = []

        try:
            data = json.load(trainFile)   # -> Python list/dict
            trainData = [TrainObject(**item) for item in data]
        except Exception as e:
            trainData = []
            print("Failed to read previous data.", e)
        finally:
            trainFile.close()

        newTrainData = TrainObject(sensorData=self.data, gesture=gesture)
        trainData.append(newTrainData)

        def pad_to_5_digits(num): # hell nah
            if num == 0:
                return 0
            sign = -1 if num < 0 else 1
            num_abs = abs(num)

            num_digits = len(str(num_abs))

            while num_digits < 5:
                num_abs *= 10
                num_digits += 1
            return sign * num_abs


        for reading in trainData:
            for sensor_reading in reading.sensorData:
                for key in ['AcX', 'AcY', 'AcZ', 'GyX', 'GyY', 'GyZ']:
                    old_value = getattr(sensor_reading, key)
                    new_value = pad_to_5_digits(old_value)
                    setattr(sensor_reading, key, new_value)


        with open("../data/" + filename, "w") as f:
            json_string = json.dumps([obj.model_dump() for obj in trainData], indent=2)
            f.write(json_string)

        self.clear()

        print("Received data saved as: " + filename + " gesture: " + str(gesture.value))

    def clear(self):
        with self._lock:
            self.data = []

    def getLength(self) -> int:
        with self._lock:
            return len(self.data)
