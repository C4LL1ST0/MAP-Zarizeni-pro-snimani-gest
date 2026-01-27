from pydantic import BaseModel
from typing import List

class SensorData(BaseModel):
    AcX: int
    AcY: int
    AcZ: int
    GyX: int
    GyY: int
    GyZ: int

    def to_array(self) -> List[int]:
        return [self.AcX, self.AcY, self.AcZ, self.GyX, self.GyY, self.GyZ]
    