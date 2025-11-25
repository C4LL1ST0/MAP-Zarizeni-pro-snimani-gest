from typing import List
from pc_driver.SensorData import SensorData
from pc_driver.TrainObject import TrainObject
from pc_driver.Gesture import Gesture
from pathlib import Path
import json

class Cache:
    def __init__(self) -> None:
        self.data: List[SensorData] = []

    def add(self, sensorData: SensorData) -> None:
        if(len(self.data) >= 100):
            self.data.pop(0)

        self.data.append(sensorData)

    def getData(self) -> List[SensorData]:
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

        with open("../data/" + filename, "w") as f:
            json_string = json.dumps([obj.model_dump() for obj in trainData], indent=2)
            f.write(json_string)

        self.clear()

        print("Received data saved as: " + filename + " gesture: " + str(gesture.value))

    def clear(self):
        self.data = []

    def getLength(self) -> int:
        return len(self.data)
