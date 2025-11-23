import socket
import struct
from typing import Tuple
from pc_driver.Cache import Cache
from pc_driver.SensorData import SensorData
from pc_driver.Gesture import Gesture

class Receiver:
    def __init__(self) -> None:
        self.ip: str = "0.0.0.0"
        self.port: int = 1234
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(3)
        self.cache = Cache()
        self.receiving = True

    def start_receiving_train_data(self, dataFile: str, gesture: Gesture) -> None:
        while self.receiving:
            packet: bytes
            addr: Tuple[str, int]

            try:
                packet, addr = self.sock.recvfrom(1024)
            except socket.timeout:
                if(self.cache.getLength() != 0):
                    self.cache.saveCacheAsTrainDataToFile(dataFile, gesture)
                    self.receiving = False
                #continue

            if len(packet) != 24:
                continue

            unpacked = struct.unpack("6i", packet)
            values = SensorData(
                AcX=unpacked[0],
                AcY=unpacked[1],
                AcZ=unpacked[2],
                GyX=unpacked[3],
                GyY=unpacked[4],
                GyZ=unpacked[5]
            )

            self.cache.add(values)

    def start_receiving(self) -> None:
        while self.receiving:
            packet: bytes
            addr: Tuple[str, int]

            try:
                packet, addr = self.sock.recvfrom(1024)
            except socket.timeout:
                print("No data received")

            if len(packet) != 24:
                continue


            unpacked = struct.unpack("6i", packet)
            values = SensorData(
                AcX=unpacked[0],
                AcY=unpacked[1],
                AcZ=unpacked[2],
                GyX=unpacked[3],
                GyY=unpacked[4],
                GyZ=unpacked[5]
            )
            self.cache.add(values)

    def end_receiving(self) -> None:
        self.receiving = False
        self.cache.clear()
