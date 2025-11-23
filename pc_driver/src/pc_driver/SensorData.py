from pydantic import BaseModel

class SensorData(BaseModel):
    AcX: int
    AcY: int
    AcZ: int
    GyX: int
    GyY: int
    GyZ: int
