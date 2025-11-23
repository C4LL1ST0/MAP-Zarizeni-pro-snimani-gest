from typing import List
from pc_driver.SensorData import SensorData
from pc_driver.Gesture import Gesture
from pydantic import BaseModel

class TrainObject(BaseModel):
    sensorData: List[SensorData]
    gesture: Gesture
