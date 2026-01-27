import socket
import struct
from typing import Tuple
from .AIService import AIService
from .UiMessages import InfoMessage, SensorDataMessage
from .Cache import Cache
from .SensorData import SensorData
from .Gesture import Gesture
import threading
import time
from textual.app import App


class Receiver:
    def __init__(self, ui: App, ai_service: AIService) -> None:
        self.ui: App = ui
        self.ai_service: AIService = ai_service
        self.ip: str = "0.0.0.0"
        self.port: int = 1234
        self.sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(3)
        self.cache: Cache = Cache(self.ui)
        self.receiving = True
    def capture_data_thread(self, dataFile: str, gesture: Gesture):
        self.ui.post_message(InfoMessage("Training data capturing started.")) #delete later
        def capture_training_data():
            self.ui.post_message(InfoMessage("Training data capturing started. 2")) #delete the '2' later
            try:
                while True:
                    self.start_receiving_train_data(dataFile, gesture)
                    time.sleep(0.1)
                    self.receiving = True
            except KeyboardInterrupt:
                self.ui.post_message(InfoMessage("Receiver stopped by user."))
        threading.Thread(target=capture_training_data, daemon=True).start()
        self.ui.post_message(InfoMessage("thread started."))  #delete later

    def start_receiving_train_data(self, dataFile: str, gesture: Gesture) -> None:
        self.receiving = True
        self.cache.clear()

        while self.receiving:
            packet: bytes
            addr: Tuple[str, int]

            packet = None
            try:
                packet, addr = self.sock.recvfrom(1024)
            except (socket.timeout, TimeoutError):
                if(self.cache.getLength() != 0):
                    self.cache.saveCacheAsTrainDataToFile(dataFile, gesture) # store all previously received data
                    self.ui.post_message(InfoMessage(f"Data saved to file: {dataFile} gesture: {gesture}"))
                    self.end_receiving()
                break

            if packet is not None:
                if len(packet) != 12:
                    self.ui.post_message(InfoMessage("Are you connected to ESP wifi?"))
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
            self.ui.post_message(SensorDataMessage(values))


    def start_receiving(self):
        """Receives sensor data,
        adds to cache,
        sends them for evaluation(if correct legth),
        runs in its own thread"""

        self.receiving = True
        self.cache.clear()

        def loop():
            while self.receiving:
                packet: bytes
                addr: Tuple[str, int]

                packet = None
                try:
                    packet, addr = self.sock.recvfrom(1024)
                except (socket.timeout, TimeoutError):
                   
                    if(self.cache.getLength() < self.ai_service.gesture_length/2):
                        self.cache.clear()
                        self.ui.call_from_thread(
                            self.ui.post_message,
                            InfoMessage("Uncomplete gesture received, data cannot be used./n Please try again.")
                        )
                        continue

                    if(self.cache.getLength() < self.ai_service.gesture_length):
                        # gesto neni cele, ale vice nez polovina
                        # vypadovat do celku, nasledne pouzit
                        self.ui.call_from_thread(
                            self.ui.post_message,
                            InfoMessage("Uncomplete gesture received, padding to compensate.")
                        )
                        x = self.cache.get_padded_data()
                        self.ai_service.eval_gesture(self.cache.get_padded_data())
                        self.ui.call_from_thread(
                            self.ui.post_message,
                            InfoMessage("after eval")
                        )
                        self.cache.clear()
                        continue

                    if(self.cache.getLength() == self.ai_service.gesture_length):
                        self.ai_service.eval_gesture(self.cache.getData())
                        self.cache.clear()
                        continue

                if packet is not None:
                    if len(packet) != 12:
                        self.ui.call_from_thread(
                            self.ui.post_message,
                            InfoMessage("Are you connected to ESP wifi?")
                        )

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
                self.ui.post_message(SensorDataMessage(values))

                if(self.cache.getLength() == self.ai_service.gesture_length):
                    self.ui.call_from_thread(
                            self.ui.post_message,
                            InfoMessage("before eval")
                        )
                    self.ai_service.eval_gesture(self.cache.getData())
                    self.cache.clear()
                    continue

        threading.Thread(target=loop, daemon=True).start()

    def end_receiving(self) -> None:
        self.receiving = False
        self.cache.clear()
        self.ui.post_message(InfoMessage("Receiving stopped."))
