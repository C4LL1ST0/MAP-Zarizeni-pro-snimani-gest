import socket
import struct
from typing import List
from pc_driver.Cache import Cache


class Receiver:
    def __init__(self) -> None:
        self.ip: str = "0.0.0.0"
        self.port: int = 1234
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.cache: Cache = Cache()
        self.receiving = True

    def start_receiving(self) -> None:
        while self.receiving:
            packet: bytes
            addr: Tuple[str, int]
            packet, addr = self.sock.recvfrom(1024)

            if len(packet) != 24:
                continue

            values = SensorData(*struct.unpack("6i", packet))
            self.cache.add(values)

    def end_receiving(self) -> None:
        self.receiving = False
