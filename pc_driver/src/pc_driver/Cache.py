from typing import List
from textual.app import App
from .UiMessages import InfoMessage
from .SensorData import SensorData
from .TrainObject import TrainObject
from .Gesture import Gesture
from pathlib import Path
import json
from threading import Lock

class Cache:
    def __init__(self, ui) -> None:
        self.ui: App = ui
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

    def get_padded_data(self) -> List[SensorData]:
        with self._lock:
            return self.pad_gesture(self.data)

    def pad_gesture(self, sensor_data) -> List[SensorData]:
        MAX_BLOCKS = 45
        ZERO_BLOCK: SensorData = SensorData(
            AcX=0,
            AcY=0,
            AcZ=0,
            GyX=0,
            GyY=0,
            GyZ=0
        )
        sensor_data = sensor_data[:MAX_BLOCKS]
        while len(sensor_data) < MAX_BLOCKS:
            sensor_data.append(ZERO_BLOCK.copy())
        return sensor_data

    def saveCacheAsTrainDataToFile(self, filename: str, gesture: Gesture) -> None:
        myfile = Path("../data/" + filename)
        print("before file check")
        if(not myfile.is_file()):
            self.ui.post_message(InfoMessage("File: " + filename + " does not exist."))
            with open("../data/" + filename, "x") as f:
                f.write("")
                self.ui.post_message(InfoMessage("File: " + filename + " created."))

        trainFile = open("../data/" + filename, "r")
        trainData: List[TrainObject] = []

        try:
            data = json.load(trainFile)   # -> Python list/dict
            trainData = [TrainObject(**item) for item in data]
        except Exception as e:
            trainData = []
            self.ui.post_message(InfoMessage(f"Failed to read previous data.\n {e}"))
        finally:
            trainFile.close()

        newTrainData = TrainObject(
            sensorData=self.pad_gesture(self.data),
            gesture=gesture
        )
        trainData.append(newTrainData)

        with open("../data/" + filename, "w") as f:
            json_string = json.dumps([obj.model_dump() for obj in trainData], indent=2)
            f.write(json_string)

        self.clear()


    def clear(self):
        with self._lock:
            self.data = []

    def getLength(self) -> int:
        with self._lock:
            return len(self.data)
