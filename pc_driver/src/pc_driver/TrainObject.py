from typing import List
from pc_driver.SensorData import SensorData
from pc_driver.Gesture import Gesture
from pydantic import BaseModel

class TrainObject(BaseModel):
    sensorData: List[SensorData]
    gesture: Gesture

    def sensor_data_to_2d_list(self) -> List[List[int]]:
        sensor_data_list: List[List[int]] = []
        for sd in self.sensorData:
            values = [sd.AcX, sd.AcY, sd. AcZ, sd.GyX, sd.GyY, sd.GyZ]
            sensor_data_list.append(values)

        return sensor_data_list

    class Config:
        use_enum_values = True
