import json
from typing import List
from pc_driver.SensorData import SensorData

class Cache:
    def __init__(self) -> None:
        self.data:  List[SensorData] = []

    def add(self, sensorData: SensorData) -> None:
        if(len(self.data) >= 100):
            self.data.pop(0)

        self.data.append(sensorData)

    def getData(self) -> List[SensorData]:
        return self.data

    def saveCacheToFile(self, filename: str) -> None:
        jsonList = [record.asdict() for record in self.data]
        with open(filename, x) as f:
            json.dump(jsonList, f)
