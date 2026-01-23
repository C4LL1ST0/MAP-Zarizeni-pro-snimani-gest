from textual.message import Message
from .SensorData import SensorData

class SensorDataMessage(Message):
    def __init__(self, data: SensorData):
        self.data = data
        super().__init__()

class InfoMessage(Message):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__()
