import socket
import struct
from typing import Tuple
from pc_driver.Cache import Cache
from pc_driver.SensorData import SensorData
from pc_driver.Gesture import Gesture
import time


class Receiver:
    def __init__(self) -> None:
        self.ip: str = "0.0.0.0"
        self.port: int = 1234
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(3)
        self.cache = Cache()
        self.receiving = True

    def capture_training_data(self, dataFile: str, gesture: Gesture):
        try:
            while True:
                self.start_receiving_train_data(dataFile, gesture)
                print(f"Data saved to {dataFile}. Waiting for next batch...")
                time.sleep(0.1)
                self.receiving = True
        except KeyboardInterrupt:
            print("Receiver stopped by user.")


    def start_receiving_train_data(self, dataFile: str, gesture: Gesture) -> None:
        print("DEBUG: exiting receive loop, receiving =", self.receiving)
        while self.receiving:
            packet: bytes
            addr: Tuple[str, int]

            packet = None
            try:
                packet, addr = self.sock.recvfrom(1024)
            except (socket.timeout, TimeoutError):
                if(self.cache.getLength() != 0):
                    print("before cache")
                    self.cache.saveCacheAsTrainDataToFile(dataFile, gesture)
                    self.end_receiving()
                break

            if packet is not None:
                if len(packet) != 12:
                    print("Are you connected to ESP wifi?")
                    continue

            unpacked = struct.unpack("6h", packet)
            values = SensorData(
                AcX=unpacked[0],
                AcY=unpacked[1],
                AcZ=unpacked[2],
                GyX=unpacked[3],
                GyY=unpacked[4],
                GyZ=unpacked[5]
            )

            self.cache.add(values)


    def start_receiving(self):
        # potom realna ziva data, musi bezet na vlastnim vlakne
        pass

    def end_receiving(self) -> None:
        self.receiving = False
        self.cache.clear()
