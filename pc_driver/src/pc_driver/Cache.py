from typing import List
from pc_driver.SensorData import SensorData
from pc_driver.TrainObject import TrainObject
from pc_driver.Gesture import Gesture
from pathlib import Path


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
            print("File does not exist.")
            with open("../data/" + filename, "x") as f:
                f.write("[]")
            return

        trainFile = open("../data/" + filename, "r")
        trainData: List[TrainObject] = TrainObject.model_validate_json(trainFile.read())
        trainFile.close()

        newTrainData = TrainObject(self.data, gesture)
        trainData.append(newTrainData)

        with open("../data/" + filename, "w") as f:
            f.write(trainData.model_dump_json())

        self.clear()

        print("Received data saved as: " + filename + "gesture: " + gesture)

    def clear(self):
        self.data = []

    def getLength(self) -> int:
        return len(self.data)
